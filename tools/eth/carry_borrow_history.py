"""Capture and rebuild monthly loan-principal rates at existing archive blocks.

Run --capture for read-only RPC calls, then run without arguments to rebuild
offline. Prior research captures and canonical reports are never changed.
"""
from __future__ import annotations

import concurrent.futures
import datetime as dt
import hashlib
import json
import math
import sys
from pathlib import Path

import carry_economics_collect as client
from carry_economics_collect import call, enc_addr, enc_uint, words

ROOT = client.ROOT
DATA = ROOT / 'data/eth'
RAW = ROOT / 'raw/eth/carry-borrow-history-2026-10-04'
client.RAW = RAW
MARKET = '0xea4bfb18df0ee6bffb7b3f0270899a8adb92ab6b684709634c8276128813cfd4'
MORPHO = client.MORPHO
MAIN = client.V
LOAN = client.LOAN
WETH = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
RLUSD = '0x8292bb45bf1ee4d140127049757c2e0ff06317ed'
AAVE = '0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2'
YEAR = 365 * 86400


def read(name):
    return json.loads((DATA / (name + '.json')).read_text())


def addr(value):
    return '0x' + format(value, '040x')


def monthly_blocks():
    observed = {}
    for row in read('carry_category_candidates')['history_rpc_records']:
        stamp = row['timestamp']
        if stamp in observed:
            assert observed[stamp]['block'] == row['block']
        observed[stamp] = {k: row[k] for k in ['month', 'timestamp', 'block']}
    rows = sorted(observed.values(), key=lambda r: r['timestamp'])
    assert len(rows) == 24
    return rows


def capture_month(month):
    tag = hex(month['block'])
    labels = ['block', 'next_block', 'main_code', 'loan_manager_code', 'params', 'market', 'main_position', 'loan_manager_position', 'aave_reserve']
    calls = [('eth_getBlockByNumber', [tag, False]), ('eth_getBlockByNumber', [hex(month['block'] + 1), False]), ('eth_getCode', [MAIN, tag]), ('eth_getCode', [LOAN, tag]), call(MORPHO, 'idToMarketParams(bytes32)', MARKET[2:], tag), call(MORPHO, 'market(bytes32)', MARKET[2:], tag), call(MORPHO, 'position(bytes32,address)', MARKET[2:] + enc_addr(MAIN), tag), call(MORPHO, 'position(bytes32,address)', MARKET[2:] + enc_addr(LOAN), tag), call(AAVE, 'getReserveData(address)', enc_addr(WETH), tag)]
    responses = client.rpc('ethereum', calls, 'monthly_' + month['month'])
    byid = {r['id']: r for r in responses}
    first = {name: byid.get(i + 1, {}) for i, name in enumerate(labels)}
    follow_calls, follow_labels = [], []
    params, market = words(first['params'].get('result')), words(first['market'].get('result'))
    if params and market and any(params) and market[4]:
        irm = addr(params[3])
        encoded = ''.join(enc_uint(x) for x in params + market)
        follow_calls += [call(irm, 'borrowRateView((address,address,address,address,uint256),(uint128,uint128,uint128,uint128,uint128,uint128))', encoded, tag), call(irm, 'rateAtTarget(bytes32)', MARKET[2:], tag), call(irm, 'MORPHO()', '', tag), ('eth_getCode', [irm, tag])]
        follow_labels += ['morpho_borrow_rate_view', 'morpho_rate_at_target', 'morpho_model_core', 'morpho_model_code']
    reserve = words(first['aave_reserve'].get('result'))
    if reserve and len(reserve) >= 12 and reserve[10]:
        variable_debt = addr(reserve[10])
        follow_calls += [call(variable_debt, 'balanceOf(address)', enc_addr(MAIN), tag)]
        follow_labels += ['aave_main_variable_debt']
    if follow_calls:
        follow_responses = client.rpc('ethereum', follow_calls, 'monthly_follow_' + month['month'])
        byid = {r['id']: r for r in follow_responses}
        first.update({name: byid.get(i + 1, {}) for i, name in enumerate(follow_labels)})
    return {**month, 'responses': first}


def capture():
    months = monthly_blocks()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(capture_month, months))
    out = {'captured_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'financial_as_of_timestamp': client.T, 'raw_manifest': str((RAW / 'requests.jsonl').relative_to(ROOT)), 'records': records}
    (DATA / 'carry_borrow_history_rpc.json').write_text(json.dumps(out, indent=2))
    print(json.dumps({'months': len(records), 'raw_manifest': out['raw_manifest']}))


def source_proof(name):
    path = DATA / (name + '.json')
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def crosscheck():
    record = next(r for r in read('carry_borrow_history_rpc')['records'] if r['month'] == '2026-09')
    tag, raw = hex(record['block']), record['responses']
    params, market = words(raw['params']['result']), words(raw['market']['result'])
    encoded = ''.join(enc_uint(x) for x in params + market)
    calls = [call(MORPHO, 'idToMarketParams(bytes32)', MARKET[2:], tag), call(MORPHO, 'market(bytes32)', MARKET[2:], tag), call(MORPHO, 'position(bytes32,address)', MARKET[2:] + enc_addr(MAIN), tag), call(addr(params[3]), 'borrowRateView((address,address,address,address,uint256),(uint128,uint128,uint128,uint128,uint128,uint128))', encoded, tag)]
    payload = [{'jsonrpc': '2.0', 'id': i + 1, 'method': method, 'params': args} for i, (method, args) in enumerate(calls)]
    response = client.capture('independent_provider_September_2026_Tenderly', 'https://gateway.tenderly.co/public/mainnet', payload)
    byid = {r['id']: r for r in response} if isinstance(response, list) else {}
    labels = ['params', 'market', 'main_position', 'morpho_borrow_rate_view']
    matches = bool(byid) and all(byid.get(i + 1, {}).get('result') == raw[name].get('result') for i, name in enumerate(labels))
    (DATA / 'carry_borrow_history_crosscheck.json').write_text(json.dumps({'month': record['month'], 'block': record['block'], 'labels': labels, 'responses': response, 'all_primary_results_match': matches}, indent=2))
    print('Independent September primary results match:', matches)


def build():
    rpc = read('carry_borrow_history_rpc')
    rows, verifications = [], []
    sources = [json.loads(line) for line in (ROOT / rpc['raw_manifest']).read_text().splitlines()]
    model = next(r for r in read('carry_economics_chapter')['borrow_markets'] if r['market_id'] == MARKET)['rate_model']
    known_runtime = json.loads((ROOT / model['source_path']).read_text())['deployed_bytecode'].lower()
    for record in rpc['records']:
        raw = record['responses']
        stamp, month, block = record['timestamp'], record['month'], record['block']
        block_response, next_response = raw['block'].get('result'), raw['next_block'].get('result')
        verified = bool(block_response and next_response and int(block_response['number'], 16) == block and int(block_response['timestamp'], 16) <= stamp < int(next_response['timestamp'], 16))
        verifications.append({'timestamp': stamp, 'date': month, 'block': block, 'block_hash': block_response.get('hash') if block_response else None, 'block_timestamp': int(block_response['timestamp'], 16) if block_response else None, 'next_block_timestamp': int(next_response['timestamp'], 16) if next_response else None, 'last_block_at_or_before_timestamp_verified': verified})
        params, market = words(raw['params'].get('result')), words(raw['market'].get('result'))
        main, loan = words(raw['main_position'].get('result')), words(raw['loan_manager_position'].get('result'))
        main_exists = raw['main_code'].get('result') not in [None, '0x', '0x0']
        loan_exists = raw['loan_manager_code'].get('result') not in [None, '0x', '0x0']
        main_funded = bool(main_exists and main and main[1] > 0 and main[2] > 0)
        loan_funded = bool(loan_exists and loan and loan[1] > 0 and loan[2] > 0)
        market_exists = bool(params and any(params) and market and market[4] > 0)
        quoted = words(raw.get('morpho_borrow_rate_view', {}).get('result'))
        model_core = words(raw.get('morpho_model_core', {}).get('result'))
        correct_bindings = bool(market_exists and addr(params[0]) == RLUSD and addr(params[1]) == '0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee' and addr(params[3]) == model['address'] and model_core and addr(model_core[0]) == MORPHO and raw.get('morpho_model_code', {}).get('result', '').lower() == known_runtime)
        verified_quote_apr = quoted[0] * YEAR / 10 ** 18 if verified and quoted and correct_bindings else None
        status, apr = 'rpc_unavailable', None
        if verified and params is not None and market is not None:
            if not market_exists:
                status = 'market_not_created'
            elif not main_exists:
                status = 'main_account_predeployment'
            elif not main_funded:
                status = 'main_account_not_borrowing'
            else:
                if verified_quote_apr is not None:
                    apr, status = verified_quote_apr, 'observed_funded_main_account'
                else:
                    status = 'rate_or_model_verification_unavailable'
        common = {'timestamp': stamp, 'date': month, 'block': block, 'account': MAIN, 'block_verified': verified}
        rows.append({**common, 'series_id': 'liquid-main-weeth-rlusd', 'protocol': 'Morpho Blue', 'market_id': MARKET, 'loan_asset': RLUSD, 'loan_symbol': 'RLUSD', 'borrow_apr': apr, 'status': status, 'sourceURL': 'https://app.morpho.org/ethereum/market/' + MARKET, 'market_exists': market_exists, 'account_exists': main_exists, 'main_account_funded': main_funded, 'loan_manager_exists': loan_exists, 'loan_manager_funded': loan_funded, 'main_borrow_shares': str(main[1]) if main else None, 'main_collateral_raw': str(main[2]) if main else None, 'market_last_update_timestamp': market[4] if market_exists else None, 'pending_accrual_seconds': int(block_response['timestamp'], 16) - market[4] if market_exists and block_response else None, 'rate_model': addr(params[3]) if market_exists else None, 'rate_basis': 'Historical fixed-block borrowRateView average over the pending accrual interval; APR = per-second WAD rate × 365 days. Loan-principal rate, not product income.'})
        rows[-1].update(market_quote_borrow_apr=verified_quote_apr, market_utilization=market[2] / market[0] if market_exists and market[0] else None, loan_manager_observed_borrow_apr=verified_quote_apr if loan_funded else None, rate_model_binding_and_runtime_verified=correct_bindings)
        reserve = words(raw['aave_reserve'].get('result'))
        debt = words(raw.get('aave_main_variable_debt', {}).get('result'))
        aave_apr, aave_status = None, 'rpc_unavailable'
        if verified and reserve and len(reserve) >= 12:
            if not reserve[10]:
                aave_status = 'reserve_not_initialized'
            elif not main_exists:
                aave_status = 'main_account_predeployment'
            elif debt is None:
                aave_status = 'account_debt_unavailable'
            elif debt[0] == 0:
                aave_status = 'main_account_not_borrowing'
            else:
                aave_apr, aave_status = reserve[4] / 10 ** 27, 'observed_funded_main_account'
        rows.append({**common, 'series_id': 'liquid-main-aave-weth', 'protocol': 'Aave V3', 'market_id': AAVE, 'loan_asset': WETH, 'loan_symbol': 'WETH', 'borrow_apr': aave_apr, 'status': aave_status, 'sourceURL': 'https://app.aave.com/reserve-overview/?underlyingAsset=' + WETH + '&marketName=proto_mainnet_v3', 'account_exists': main_exists, 'main_account_variable_debt_WETH': debt[0] / 10 ** 18 if debt else None, 'variable_debt_token': addr(reserve[10]) if reserve and len(reserve) >= 12 else None, 'rate_model': addr(reserve[11]) if reserve and len(reserve) >= 12 else None, 'rate_basis': 'Historical stored reserve variable borrow APR in ray, verified with nonzero variable WETH debt in the main account. E3 loan-principal benchmark, not whole-product income.'})
    series = []
    for ident, title, classification in [('liquid-main-weeth-rlusd', 'Liquid ETH main weETH/RLUSD loan', 'E4 stablecoin borrowing'), ('liquid-main-aave-weth', 'Liquid ETH main Aave WETH borrowing', 'E3 ETH-debt loop benchmark')]:
        observed = [r for r in rows if r['series_id'] == ident and r['borrow_apr'] is not None]
        series.append({'id': ident, 'label': title, 'classification': classification, 'observed_months': len(observed), 'first_observed_date': observed[0]['date'] if observed else None, 'last_observed_date': observed[-1]['date'] if observed else None, 'min_observed_APR': min((r['borrow_apr'] for r in observed), default=None), 'max_observed_APR': max((r['borrow_apr'] for r in observed), default=None)})
    out = {'schema_version': 1, 'financial_as_of_timestamp': client.T, 'captured_at': rpc['captured_at'], 'months': len(rpc['records']), 'scope': 'Completed-month point samples at the exact category history blocks. Loan-principal borrowing APRs for named accounts, not time-weighted funding costs, whole-product return or historic carry allocation.', 'rate_units': 'Fractions per year, not percentages; APR is not compounded annual yield.', 'null_policy': 'Rates are null before market creation, before account deployment, when the named main account does not have verified nonzero borrowing, or when a primary verification fails. No interpolation or flat-rate backfill.', 'series': series, 'rows': rows, 'block_verifications': verifications, 'sources': [source_proof('carry_borrow_history_rpc'), source_proof('carry_category_candidates'), {'path': model['source_path'], 'sha256': model['source_sha256']}], 'raw_manifest': rpc['raw_manifest'], 'raw_capture_records': [{k: r[k] for k in ['key', 'url', 'path', 'sha256', 'retrieved_at'] if k in r} for r in sources if r.get('path')], 'limitations': ['A month-end sample is not the average or maximum borrowing cost paid during that month.', 'Morpho borrowRateView is the model average over the pending accrual interval, rather than an instantaneous prospective rate.', 'The historical main-account position is tested independently of the controlled LoanManager. LoanManager funding is retained as metadata, but it does not backfill an unfunded main-account rate.', 'Aave WETH borrowing is an ETH-debt strategy benchmark, not E4 stablecoin carry.', 'No historical allocation weights, parked debt, destination reward rates or product yield attribution are reconstructed by these funding-cost series.']}
    crosscheck_path = DATA / 'carry_borrow_history_crosscheck.json'
    if crosscheck_path.exists():
        independent = json.loads(crosscheck_path.read_text())
        out['independent_September_provider_match'] = independent['all_primary_results_match']
        out['sources'].append(source_proof('carry_borrow_history_crosscheck'))
    json.dumps(out, allow_nan=False)
    (DATA / 'carry_borrow_rate_history.json').write_text(json.dumps(out, indent=2))
    print(json.dumps({'rows': len(rows), 'series': series, 'verified_blocks': sum(r['last_block_at_or_before_timestamp_verified'] for r in verifications)}, indent=2))


def verify():
    out, rpc = read('carry_borrow_rate_history'), read('carry_borrow_history_rpc')
    assertions = 0
    def test(condition, label):
        nonlocal assertions
        assertions += 1
        assert condition, label
    def near(actual, expected, label):
        test(math.isclose(actual, expected, rel_tol=1e-13, abs_tol=1e-15), label)
    records = {r['timestamp']: r for r in rpc['records']}
    expected_blocks = {r['timestamp']: r['block'] for r in monthly_blocks()}
    for source in out['sources'] + out['raw_capture_records']:
        test(hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest() == source['sha256'], 'preserved source hash')
    test(len(out['rows']) == 48 and len(records) == 24, '24 months / 48 distinct series rows')
    test(out['independent_September_provider_match'] is True, 'independent September RPC match')
    independent = read('carry_borrow_history_crosscheck')
    september = next(r for r in rpc['records'] if r['month'] == '2026-09')
    byid = {r['id']: r for r in independent['responses']}
    for i, label in enumerate(independent['labels']):
        test(byid[i + 1]['result'] == september['responses'][label]['result'], 'independent exact result ' + label)
    for block in out['block_verifications']:
        test(block['block'] == expected_blocks[block['timestamp']], 'exact existing monthly block')
        test(block['last_block_at_or_before_timestamp_verified'], 'archive block verified')
        test(block['block_timestamp'] <= block['timestamp'] < block['next_block_timestamp'], 'last block before month end')
    for row in out['rows']:
        test({'timestamp', 'date', 'protocol', 'market_id', 'loan_asset', 'borrow_apr', 'status', 'sourceURL'} <= row.keys(), 'requested row fields')
        test(row['block'] == expected_blocks[row['timestamp']], 'row monthly block')
        test(row['block_verified'], 'row verified block')
        raw = records[row['timestamp']]['responses']
        if row['series_id'] == 'liquid-main-weeth-rlusd':
            market = words(raw['market']['result'])
            pos = words(raw['main_position']['result'])
            quote = words(raw.get('morpho_borrow_rate_view', {}).get('result'))
            if row['borrow_apr'] is not None:
                test(pos[1] > 0 and pos[2] > 0 and market[4] > 0, 'observed main collateral and borrowing')
                test(row['rate_model_binding_and_runtime_verified'], 'historical exact model binding/code')
                near(row['borrow_apr'], quote[0] / 10 ** 18 * YEAR, 'independent Morpho APR')
                test(row['status'] == 'observed_funded_main_account', 'rate status')
            else:
                test(row['status'] in ['market_not_created', 'main_account_not_borrowing'], 'null explained by state')
                test(not market[4] or pos[1] == 0, 'no main debt backfilled')
            if row['market_quote_borrow_apr'] is not None:
                near(row['market_quote_borrow_apr'], quote[0] / 10 ** 18 * YEAR, 'separate market quote')
                near(row['market_utilization'], market[2] / market[0], 'market utilization')
            if row['loan_manager_observed_borrow_apr'] is not None:
                loan = words(raw['loan_manager_position']['result'])
                test(loan[1] > 0 and loan[2] > 0, 'separate LoanManager funded')
                near(row['loan_manager_observed_borrow_apr'], quote[0] / 10 ** 18 * YEAR, 'separate LoanManager APR')
        else:
            reserve = words(raw['aave_reserve']['result'])
            debt = words(raw['aave_main_variable_debt']['result'])[0]
            test(debt > 0 and row['borrow_apr'] is not None, 'observed Aave account debt')
            near(row['borrow_apr'], reserve[4] / 10 ** 27, 'independent Aave APR')
            near(row['main_account_variable_debt_WETH'], debt / 10 ** 18, 'Aave WETH amount')
            test(row['variable_debt_token'] == addr(reserve[10]), 'Aave debt token binding')
    json.dumps(out, allow_nan=False)
    review = {'passed_checks': assertions, 'months': 24, 'rows': 48, 'dataset_sha256': hashlib.sha256((DATA / 'carry_borrow_rate_history.json').read_bytes()).hexdigest(), 'independent_September_RPC_provider_match': True, 'scope': 'Offline source/state verification, point quote conversion and account funding; no monthly-average cost or yield attribution.'}
    (DATA / 'carry_borrow_history_review.json').write_text(json.dumps(review, indent=2))
    print(json.dumps(review, indent=2))


if __name__ == '__main__':
    capture() if '--capture' in sys.argv else crosscheck() if '--crosscheck' in sys.argv else verify() if '--verify' in sys.argv else build()
