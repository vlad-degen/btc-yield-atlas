"""Independently check the isolated carry dataset against preserved primary responses."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data/eth'
WAD = 10 ** 18
YEAR = 365 * 86400
checks = 0


def read(name):
    return json.loads((DATA / (name + '.json')).read_text())


def ok(value, message):
    global checks
    checks += 1
    assert value, message


def close(a, b, message):
    ok(math.isclose(a, b, rel_tol=2e-12, abs_tol=2e-12), message)


def words(result):
    return [int(result[i:i + 64], 16) for i in range(2, len(result), 64)]


def address(number):
    return '0x' + format(number, '040x')


def truncdiv(a, b):
    return abs(a) // abs(b) * (-1 if (a < 0) != (b < 0) else 1)


def debt_up(shares, borrow_assets, borrow_shares):
    return (shares * (borrow_assets + 1) + borrow_shares + 10 ** 6 - 1) // (borrow_shares + 10 ** 6)


def verify():
    chapter = read('carry_economics_chapter')
    primary = read('carry_economics_primary_T')
    curves = read('carry_economics_curves_T')
    aave = read('carry_economics_aave_T')
    proof = read('carry_economics_model_proof_T')
    manifests = [json.loads(x) for x in (ROOT / chapter['raw_manifest']).read_text().splitlines()]
    sources = {r['key']: r for r in manifests if r.get('path')}
    snapshots = {r['chain']: r for r in read('snapshot_manifest')['chains']}
    target = chapter['target_timestamp']
    rows = {r['id']: r for r in chapter['borrow_markets']}
    ok(len(rows) == 22, '22 distinct markets')
    ok(len(primary['markets']) == 18 and len(aave['markets']) == 4, '18 Morpho / 4 Aave')
    for source in chapter['sources'] + chapter['primary_document_sources']:
        ok(hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest() == source['sha256'], 'chapter source hash ' + source['path'])
    raw_hashed = 0
    for record in manifests:
        if record.get('path'):
            ok(hashlib.sha256((ROOT / record['path']).read_bytes()).hexdigest() == record['sha256'], 'raw hash ' + record['key'])
            raw_hashed += 1
    exact_debt = {}
    for market in primary['markets']:
        raw = market['raw']
        r = rows[market['id']]
        params = words(raw['params']['result'])
        balances = words(raw['market']['result'])
        loan_decimals = words(raw['loan_asset_decimals()']['result'])[0]
        coll_decimals = words(raw['collateral_asset_decimals()']['result'])[0]
        s = snapshots[market['chain']]
        ok((market['block'], market['block_hash'], market['block_timestamp']) == (s['block'], s['block_hash'], s['block_timestamp']), 'fixed Morpho block')
        ok(s['block_timestamp'] <= target < s['next_timestamp'], 'last block before T')
        ok(address(params[0]) == market['discovery']['loanAsset']['address'].lower() == r['loan_asset'], 'loan token binding')
        ok(address(params[1]) == market['discovery']['collateralAsset']['address'].lower() == r['collateral_asset'], 'collateral token binding')
        ok(loan_decimals == market['discovery']['loanAsset']['decimals'], 'loan decimals')
        ok(coll_decimals == market['discovery']['collateralAsset']['decimals'], 'collateral decimals')
        ok(address(words(raw['irm_morpho']['result'])[0]) == market['morpho'], 'model core binding')
        close(r['liquidation_threshold'], params[4] / WAD, 'Morpho LLTV')
        rate = words(raw['borrow_rate_view']['result'])[0]
        close(r['borrow_apr'], rate * YEAR / WAD, 'Morpho APR')
        close(r['borrow_apy'], math.exp(rate * YEAR / WAD) - 1, 'Morpho annual cost')
        dt = market['block_timestamp'] - balances[4]
        x = rate * dt
        x2 = x * x // (2 * WAD)
        x3 = x2 * x // (3 * WAD)
        interest = balances[2] * (x + x2 + x3) // WAD
        close(r['estimated_accrued_market_debt_units'], (balances[2] + interest) / 10 ** loan_decimals, 'projected market debt')
        oracle = words(raw['oracle_price']['result'])[0]
        observed_positions = []
        for label in ['main_position', 'loan_manager_position']:
            pos = words(raw[label]['result'])
            if not any(pos):
                continue
            observed = r['positions'][len(observed_positions)]
            assets = debt_up(pos[1], balances[2] + interest, balances[3])
            exact_debt[(market['id'], label)] = assets
            close(observed['stored_debt_units'], debt_up(pos[1], balances[2], balances[3]) / 10 ** loan_decimals, 'stored account debt')
            close(observed['estimated_accrued_debt_units'], assets / 10 ** loan_decimals, 'accrued account debt')
            collateral = pos[2] * oracle / 10 ** 36 / 10 ** loan_decimals
            close(observed['collateral_value_loan_units'], collateral, 'oracle collateral units')
            close(observed['collateral_units'], pos[2] / 10 ** coll_decimals, 'collateral amount')
            if assets:
                close(observed['ltv'], assets / 10 ** loan_decimals / collateral, 'account LTV')
                close(observed['health_factor'], collateral * params[4] / WAD / (assets / 10 ** loan_decimals), 'account HF')
            observed_positions.append(observed)
        if observed_positions:
            close(r['observed_product_debt_units'], math.fsum(x['estimated_accrued_debt_units'] for x in observed_positions), 'combined debt')
            close(r['health_factor'], min(x['health_factor'] for x in observed_positions if x['health_factor'] is not None), 'separate account minimum HF')
        close(r['liquidation']['bonus_fraction'], min(1.15, 1 / (1 - .3 * (1 - params[4] / WAD))) - 1, 'Morpho bonus')
    details = read('pilot_details_T')
    old_getters = {label['label']: response for label, response in zip(details['labels'], details['responses'])}
    observed_rlusd = chapter['worked_example']['measured_leg']
    exact_rlusd_debt = exact_debt[(observed_rlusd['borrow_market_id'], 'loan_manager_position')]
    ok(exact_rlusd_debt == int(old_getters['loan_getBorrow()']['result'], 16), 'EXACT original LoanManager accrued debt getter')
    close(observed_rlusd['individual_accounts'][1]['health_factor'], int(old_getters['loan_getHealthFactor()']['result'], 16) / WAD, 'original LoanManager HF getter')
    for label, response in zip(curves['labels'], curves['responses']):
        r = rows[label['market_id']]
        target_per_sec = round(r['rate_model']['stored_rate_at_target_apr'] * WAD / YEAR)
        m = label['market_input']
        ok(m[4] == target, 'frozen adaptation interval')
        utilization = m[2] * WAD // m[0] if m[0] else 0
        error = truncdiv((utilization - 9 * 10 ** 17) * WAD, 9 * 10 ** 17 if utilization < 9 * 10 ** 17 else 10 ** 17)
        coeff = 3 * WAD // 4 if error < 0 else 3 * WAD
        expected = truncdiv((truncdiv(coeff * error, WAD) + WAD) * target_per_sec, WAD)
        ok(expected == int(response['result'], 16), 'EXACT frozen Morpho curve integer result')
        plotted = next(p for p in r['rate_model']['points'] if p['utilization'] == label['utilization'])
        close(plotted['borrow_apr'], expected * YEAR / WAD, 'plotted Morpho APR')
        close(plotted['borrow_apy'], math.exp(expected * YEAR / WAD) - 1, 'plotted Morpho annual equivalent')
    for market in aave['markets']:
        r = rows['aave-usdc-' + market['chain']]
        loan = words(market['loan_reserve']['result'])
        collateral = words(market['collateral_reserve']['result'])
        extras = {label: words(response['result']) for label, response in zip(market['extra_labels'], market['extra_responses'])}
        s = snapshots[market['chain']]
        ok(market['block'] == s, 'fixed Aave block metadata')
        ok(address(loan[11]) == market['irm'] == r['rate_model']['address'], 'Aave reserve model binding')
        close(r['borrow_apr'], loan[4] / 10 ** 27, 'Aave APR')
        close(r['borrow_apy'], math.exp(loan[4] / 10 ** 27) - 1, 'Aave annual cost equivalent')
        close(r['market_debt_units'], extras['variable_debt'][0] / 10 ** 6, 'Aave variable debt')
        close(r['reserve_cash_units'], extras['cash'][0] / 10 ** 6, 'Aave physical cash')
        close(r['ltv_limit'], (collateral[0] & 65535) / 10000, 'Aave base LTV')
        close(r['liquidation_threshold'], ((collateral[0] >> 16) & 65535) / 10000, 'Aave base CF')
        close(r['liquidation']['bonus_fraction'], ((collateral[0] >> 32) & 65535) / 10000 - 1, 'Aave base bonus')
        optimal, base, slope1, slope2 = [x / 10 ** 27 for x in extras['interest_rate_data']]
        for name, value in zip(['target_utilization', 'base_borrow_apr', 'slope1_apr', 'slope2_apr'], [optimal, base, slope1, slope2]):
            close(r['rate_model'][name], value, 'Aave actual curve parameter')
        ok(extras['base_rate'][0] == extras['interest_rate_data'][1], 'Aave base getter crosscheck')
        ok(extras['slope1'][0] == extras['interest_rate_data'][2], 'Aave slope1 getter crosscheck')
        ok(extras['slope2'][0] == extras['interest_rate_data'][3], 'Aave slope2 getter crosscheck')
        for point in r['rate_model']['points']:
            u = point['utilization']
            formula = base + slope1 * min(u / optimal, 1) + (slope2 * (u - optimal) / (1 - optimal) if u > optimal else 0)
            close(point['borrow_apr'], formula, 'Aave curve APR')
            close(point['borrow_apy'], math.exp(formula) - 1, 'Aave curve equivalent')
        ok('proto_ethereum_v3' not in r['links']['market'], 'Ethereum Aave market URL')
    bytecode_models = []
    for chain in proof['bytecodes']:
        for addr, response in zip(chain['model_addresses'], chain['responses']):
            matches = [x for x in rows.values() if x['chain'] == chain['chain'] and x['rate_model']['address'] == addr]
            source = json.loads((ROOT / matches[0]['rate_model']['source_path']).read_text())
            ok(source['is_verified'], 'model source verified')
            ok(response['result'].lower() == source['deployed_bytecode'].lower(), 'T bytecode matches verified source exactly')
            codehash = hashlib.sha256(bytes.fromhex(response['result'][2:])).hexdigest()
            for row in matches:
                ok(row['rate_model']['runtime_sha256'] == codehash and row['rate_model']['T_runtime_matches_verified_source'], 'published runtime hash')
            bytecode_models.append({'chain': chain['chain'], 'address': addr, 'name': source['name'], 'runtime_sha256': codehash})
        virtual_cash = int(chain['responses'][-1]['result'], 16) / 10 ** 6
        r = rows['aave-usdc-' + chain['chain']]
        close(r['virtual_reserve_cash_units'], virtual_cash, 'virtual reserve cash')
        close(r['virtual_balance_utilization'], r['market_debt_units'] / (r['market_debt_units'] + virtual_cash), 'virtual utilization diagnostic')
    pools = json.loads((ROOT / chapter['sources'][7]['path']).read_text())['data']
    fees = read('carry_vaults_T')
    dest_fees = {(l['vault'], l['signature']): int(r['result'], 16) / WAD for l, r in zip(fees['labels'], fees['responses']) if l['signature'] in ['performanceFee()', 'managementFee()']}
    for dest in chapter['destinations']:
        close(dest['gross_apy'], dest['organic_apy'] + (dest['reward_apy'] or 0), 'observed component decomposition')
        feed = next((x for x in pools if x['pool'] == dest['feed_pool_id']), None)
        if dest['id'].startswith('aave-usdc-'):
            r = rows[dest['id']]
            close(dest['organic_apy'], math.exp(r['supply_apr']) - 1, 'T Aave supply equivalent')
            if feed:
                close(dest['reward_apy'], (feed.get('apyReward') or 0) / 100, 'dated Aave reward component')
            else:
                ok(dest['reward_apy'] is None and 'unknown' in dest['gross_definition'], 'missing reward coverage preserved')
            ok('proto_ethereum_v3' not in dest['links']['destination'], 'Ethereum Aave destination URL')
        else:
            close(dest['gross_apy'], feed['apy'] / 100, 'dated headline APY')
            close(dest['organic_apy'], feed['apyBase'] / 100, 'dated base APY')
            close(dest['reward_apy'], feed['apyReward'] / 100, 'dated reward APY')
            close(dest['destination_performance_fee'], dest_fees[(dest['address'], 'performanceFee()')], 'primary destination fee')
            ok(dest_fees[(dest['address'], 'managementFee()')] == 0, 'primary destination management fee zero')
    baseline = chapter['calculator']['staking_baseline']['annual_rate']
    staking = next(x for x in read('etherfi_staking_comparison') if x['days'] == 30)
    close(baseline, (1 + staking['stETH_cumulative_return']) ** (365 / 30) - 1, 'historical annual staking baseline')
    for preset in chapter['calculator']['presets']:
        i, r = preset['inputs'], preset['result']
        ok(set(i) == {'ltv', 'collateral_share', 'cf', 'borrow_rate', 'parking_rate', 'reward_share', 'operator_fee'}, 'seven calculator inputs')
        debt = i['ltv'] * i['collateral_share']
        uplift = debt * (i['parking_rate'] - i['borrow_rate'])
        organic = debt * (i['parking_rate'] * (1 - i['reward_share']) - i['borrow_rate'])
        for name, expected in {'debt_as_share_of_deposit': debt, 'gross_ETH_income': baseline + uplift, 'net_ETH_income': baseline + uplift - i['operator_fee'], 'no_reward_ETH_income': baseline + organic - i['operator_fee'], 'carry_uplift_before_outer_fee': uplift, 'no_reward_carry_uplift_before_outer_fee': organic, 'health_factor': i['cf'] / i['ltv'], 'collateral_price_drop_to_liquidation': 1 - i['ltv'] / i['cf']}.items():
            close(r[name], expected, 'preset ' + preset['id'] + '/' + name)
    ok([len(chapter['playbook'][k]) for k in ['scenarios', 'reward_payers', 'rules', 'partners']] == [4, 6, 7, 6], 'four populated Playbook tables')
    ok(all(x['verified_campaign_funder'] is None for x in chapter['playbook']['reward_payers']), 'no unverified campaign attribution')
    ok(chapter['worked_example']['measured_leg']['whole_product_carry_return'] is None, 'no whole-vault income attribution')
    encoded = json.dumps(chapter, allow_nan=False)
    ok(bool(encoded), 'finite JSON values')
    review = {'passed_checks': checks, 'raw_manifest_hash_checks': raw_hashed, 'fixed_target_timestamp': target, 'market_counts': {'morpho': 18, 'aave': 4}, 'verified_rate_models': bytecode_models, 'exact_LoanManager_debt_smallest_units': str(exact_rlusd_debt), 'dataset_sha256': hashlib.sha256((DATA / 'carry_economics_chapter.json').read_bytes()).hexdigest(), 'scope': 'Independent offline calculations and source/hash checks; no executable exit, reward funding or whole-product solvency verified.'}
    (DATA / 'carry_economics_review.json').write_text(json.dumps(review, indent=2))
    print(json.dumps(review, indent=2))


if __name__ == '__main__':
    verify()
