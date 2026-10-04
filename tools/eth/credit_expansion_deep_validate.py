"""Verify the deep credit evidence and financial reconciliation offline.

This verifies provenance, receipt cash flows, deployed historical code and
liability accounting. It does not claim a complete wallet or market census.
"""
import datetime as dt
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / 'data/eth'
T = 1790985599
ETH_BLOCK = 26108081
ZERO = '0x' + '0' * 40
checks = []


def load(name):
    return json.loads((D / ('credit_expansion_deep' + name + '.json')).read_text())


def check(name, condition, detail=None):
    checks.append({'name': name, 'passed': bool(condition), 'detail': detail})


def w(value):
    if not value or value == '0x':
        return []
    return [int(value[i:i + 64], 16) for i in range(2, len(value), 64)]


def ceil_fraction(value):
    return -(-value.numerator // value.denominator)


def liability(shares, market):
    return ceil_fraction(Fraction(shares * (market[2] + 1), market[3] + 10**6))


def near(actual, expected, tolerance=1e-8):
    return abs(actual - expected) < tolerance


def main():
    out = load('')
    cap = load('_capture')
    states = load('_state')
    funding = load('_funding')
    wrapper = load('_wrapper')
    bytecode = load('_bytecode')
    timeline = out['chronology']
    A = out['cases'][0]['wallet']
    B = out['cases'][2]['wallet']
    failed_hashes = []
    for source in out['sources'] + out['inputs']:
        p = ROOT / source['path']
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != source['sha256']:
            failed_hashes.append(source['path'])
    check('Raw capture and calculation input hashes match', not failed_hashes,
          {'records': len(out['sources']), 'inputs': len(out['inputs']), 'failures': failed_hashes})
    check('Frozen financial timestamp is preserved', out['summary']['financial_snapshot_timestamp'] == T)
    check('All lifecycle transactions precede T', all(x['timestamp'] <= T for x in timeline))
    check('Chronology has unique receipts', len({x['transaction'] for x in timeline}) == len(timeline), len(timeline))
    check('Chronology is sorted', timeline == sorted(timeline, key=lambda x: (x['block'], x['transaction'])))
    receipts = {x['transaction']: x['response']['result'] for x in cap['transactions']}
    check('All receipts succeeded and were submitted by the stated wallet',
          all(int(receipts[x['transaction']]['status'], 16) == 1 and
              receipts[x['transaction']]['from'].lower() == x['wallet'] for x in timeline))
    check('Receipt headers establish exact timestamps', all(
        int(cap['blocks'][str(x['block'])]['result']['timestamp'], 16) == x['timestamp'] and
        int(receipts[x['transaction']]['blockNumber'], 16) == x['block'] for x in timeline))
    check('All terminal state calls use frozen Ethereum block',
          all(x['block'] == ETH_BLOCK for x in funding['labels'] if x['label'] == 'T'))
    index = {(x.get('label'), x.get('when'), x['signature'], x.get('market_id')):
             w(x['response'].get('result')) for x in states['labels']}
    for wallet in [A, B]:
        txs = [x for x in timeline if x['wallet'] == wallet]
        deposits = [e for x in txs for e in x['vault_events'] if e['event'] == 'Deposit']
        exits = [e for x in txs for e in x['vault_events'] if e['event'] == 'Withdraw']
        check(wallet[:8] + ' full share redemption reconciles',
              sum(int(e['shares_raw']) for e in deposits) == sum(int(e['shares_raw']) for e in exits))
        terminal = next(x for x in out['terminal_states'] if x['wallet'] == wallet)
        check(wallet[:8] + ' direct destination shares are zero at T', terminal['destination_direct_share_balance_raw'] == '0')
        for x in txs:
            for e in x['vault_events']:
                token = ('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48' if wallet == A else
                         '0x6c3ea9036406852006290770bedfcaba0e23a0e8')
                vault = out['cases'][0 if wallet == A else 2]['destination']
                # These deposits use an intermediary, identified by Deposit.caller.
                # The receipt proves both wallet -> caller and caller -> vault.
                edges = [(vault, wallet)] if e['event'] == 'Withdraw' else [(wallet, e['caller']), (e['caller'], vault)]
                check(x['label'] + ' underlying cash transfer reconciles', all(any(
                    f['token'] == token and f['from'] == sender and f['to'] == receiver and
                    f['amount_raw'] == e['assets_raw'] for f in x['public_ERC20_transfers'])
                    for sender, receiver in edges), {'public_cash_path': edges})
    # Match the verified runtime, including immutables, to the historical code.
    for code in bytecode['labels']:
        address = code['address']
        key = ('zama_implementation_verified_source' if address.startswith('0x2abad')
               else 'yield_vault_verified_' + address)
        source = next(x for x in reversed(out['sources']) if x['key'] == key and x['http_status'] == 200)
        verified = json.loads((ROOT / source['path']).read_text())
        check(address[:10] + ' historical runtime matches verified source',
              code['block'] == ETH_BLOCK and verified['is_verified'] is True and
              code['response']['result'].lower() == verified['deployed_bytecode'].lower())
    # USDC income is an exact cash total. Lot allocation is expressly analytical.
    Atxs = [x for x in timeline if x['wallet'] == A]
    deposits = [e for x in Atxs for e in x['vault_events'] if e['event'] == 'Deposit']
    redeemed = next(e for x in Atxs for e in x['vault_events'] if e['event'] == 'Withdraw')
    deposited_raw = sum(int(e['assets_raw']) for e in deposits)
    check('USDC full vault cash income reconciles', near(out['summary']['A_full_vault_cash_income_USDC'],
          (int(redeemed['assets_raw']) - deposited_raw) / 10**6))
    all_shares = sum(int(e['shares_raw']) for e in deposits)
    model = next(x for x in funding['labels'] if x['label'] == 'A_redeem')
    market = model['stored_market'][:]
    exit_tx = next(x for x in Atxs if x['label'] == 'A_redeem')
    elapsed = exit_tx['timestamp'] - market[4]
    rate = int(model['response']['result'], 16)
    first = rate * elapsed
    second = first**2 // (2 * 10**18)
    third = second * first // (3 * 10**18)
    pending = market[2] * (first + second + third) // 10**18
    market[2] += pending
    for case in out['cases'][:2]:
        borrow_tx = next(x for x in timeline if x['transaction'] == case['borrow_transaction'])
        borrow = next(e for e in borrow_tx['Morpho_events'] if e['event'] == 'Borrow')
        principal = int(borrow['assets_raw'])
        allocated = Fraction(int(redeemed['assets_raw']) * int(case['minted_shares_raw']), all_shares)
        deposit = next(x for x in timeline if x['transaction'] == case['deposit_transaction'])['vault_events'][0]
        income = float((allocated - int(deposit['assets_raw'])) / 10**6)
        cost = (liability(int(borrow['shares_raw']), market) - principal) / 10**6
        check(case['id'] + ' allocation and exact debt valuation reconcile',
              near(case['allocated_vault_income_units'], income) and
              near(case['funding_cost_through_redemption_units'], cost) and
              near(case['allocated_funded_result_before_gas_units'], income - cost))
        check(case['id'] + ' allocation is not labelled a repayment',
              case['debt_repaid_in_observed_exit'] is False and 'analytical' in case['allocation_rule'])
    check('USDC wrapper amount and receiver match the full redemption',
          out['confidential_wrapper']['wrap_receiver'] == A and
          near(out['confidential_wrapper']['wrapped_USDC_units'], int(redeemed['assets_raw']) / 10**6))
    cash_tx = next(x for x in Atxs if x['label'] == 'A_cash_out')
    check('USDC public wrap transfer matches', any(
        f['from'] == A and f['to'] == out['confidential_wrapper']['contract'] and
        f['amount_raw'] == redeemed['assets_raw'] for f in cash_tx['public_ERC20_transfers']))
    # The repayment does not erase the PYUSD liability.
    case = out['cases'][2]
    repay_tx = next(x for x in timeline if x['label'] == 'B_repay')
    repaid = next(e for e in repay_tx['Morpho_events'] if e['event'] == 'Repay')
    mid = repaid['market_id']
    position = index[('B_repay', 'after', 'position(bytes32,address)', mid)]
    m = index[('B_repay', 'after', 'market(bytes32)', mid)]
    residual = liability(position[1], m)
    check('PYUSD repayment-block debt is fully accrued to block time', m[4] == repay_tx['timestamp'])
    check('PYUSD residual debt is positive and exact', position[1] > 0 and
          near(case['residual_debt_units_at_repayment'], residual / 10**6))
    check('PYUSD funded result includes the residual liability', near(
        case['funded_result_before_gas_units'],
        (round(case['redemption_units'] * 10**6) - int(repaid['assets_raw']) - residual) / 10**6))
    Btxs = [x for x in timeline if x['wallet'] == B]
    gas_raw = sum(int(receipts[x['transaction']]['gasUsed'], 16) *
                  int(receipts[x['transaction']]['effectiveGasPrice'], 16) for x in Btxs)
    check('PYUSD gas is exact native gas across the four transactions',
          near(case['gas_ETH'], gas_raw / 10**18, 1e-18), {'gas_wei': str(gas_raw), 'USD_conversion': None})
    check('PYUSD debt and collateral persist at T', any(
        x['wallet'] == B and x['borrow_shares_raw'] == str(position[1]) and
        x['collateral_raw'] == str(position[2]) for x in out['terminal_states']))
    check('Fee-aware exit previews match measured cash', all(
        x['actual_equals_post_exit_preview'] and x['actual_redemption_assets_raw'] ==
        x['snapshots'][1]['preview_redeem_assets_raw'] for x in out['fee_observations']))
    for case in out['cases']:
        deposit = next(x for x in timeline if x['transaction'] == case['deposit_transaction'])
        route = case['destination_lending_route']
        supply = next(e for e in deposit['Morpho_events'] if e['event'] == 'Supply')
        check(case['id'] + ' destination is a measured loan-supplier route',
              route['market_id'] == supply['market_id'] and route['adapter'] == supply['on_behalf'] and
              near(route['supplied_units_in_deposit_receipt'], int(supply['assets_raw']) / 10**6))
    arb_path = D / 'credit_expansion_deep_silo_arb_retry.json'
    if arb_path.exists():
        arb = json.loads(arb_path.read_text())
        meta = {x['asset']: w(x['response'].get('result'))[0] for x in arb['current_factory_token_metadata']
                if x['signature'] == 'decimals()'}
        check('Silo Arbitrum canonical asset decimals are verified',
              meta['0x82af49447d8a07e3bd95bd0d56f35241523fbab1'] == 18 and
              meta['0xaf88d065e77c8cc2239327c5edb3a432268e5831'] == 6)
        observations = out['registry_observations'][0]
        nonzero = sum(x['response'].get('result') not in [None, '0x'] and
                      int(x['response']['result'], 16) > 0 for x in arb['factory_configs'])
        check('Silo current-generation registration and pair coverage reconcile',
              observations['nonzero_configs'] == nonzero == len(observations['pairs']) and
              len(arb['factory_configs']) == arb['next_silo_id'] - 3000 and
              observations['enumeration_complete'])
        for route in observations['canonical_ETH_USD_credit_routes']:
            x = next(x for x in arb['current_factory_credit_states'] if x['id'] == route['config_id'] and
                     x['asset'] == route['debt_asset'] and x['signature'] == 'getDebtAssets()')
            check('Silo config ' + str(route['config_id']) + ' USDC accrued debt reconciles',
                  near(route['debt_units_with_interest'], w(x['response']['result'])[0] / 10**6))
        check('Silo selected USD debt is kept in token units',
              observations['canonical_ETH_USD_debt_USDC_units'] == sum(
                  x['debt_units_with_interest'] for x in observations['canonical_ETH_USD_credit_routes']))
    retry_path = D / 'credit_expansion_deep_compound_retry.json'
    if retry_path.exists():
        retry = json.loads(retry_path.read_text())
        check('Compound repair preserves previously good chains', retry['original_good_chains_preserved'])
        check('Compound repaired addresses are deployed at the frozen Arbitrum block',
              retry['block'] == 511139919 and all(x['response'].get('result') not in [None, '0x'] for x in retry['codes']))
    boundary = out.get('post_wrap_public_boundary')
    if boundary:
        check('Post-wrap census has successful complete responses for its stated queries',
              boundary['complete_for_stated_queries'] and all(x['complete'] for x in boundary['query_counts']))
        check('Post-wrap census remains within the frozen window',
              boundary['to_block'] == ETH_BLOCK and all(
                  x['timestamp'] <= T and boundary['from_block'] <= x['block'] <= ETH_BLOCK
                  for x in boundary['public_wraps'] + boundary['encrypted_transfer_events'] + boundary['batch_events']))
        check('Post-wrap encrypted handles are never treated as plaintext quantities',
              all(x['amount_units'] is None for x in boundary['encrypted_transfer_events'] + boundary['batch_events']))
        check('Post-wrap counterparty roles match historical verified runtime',
              all(x['historical_bytecode_matches_verified'] for x in boundary['counterparties']))
        check('Post-wrap original redemption wrap amount reconciles',
              any(x['transaction'] == cash_tx['transaction'] and
                  int(x['USDC_raw']) == int(redeemed['assets_raw']) for x in boundary['public_wraps']))
        raw = load('_public_boundary')
        check('Additional post-wrap receipts succeeded and remain separate from lot-profit gas',
              len(raw['receipts']) == boundary['receipt_transactions_added'] and
              all(int(x['result']['status'], 16) == 1 for x in raw['receipts'].values()) and
              all(tx not in {x['transaction'] for x in timeline} for tx in raw['receipts']))
    check('No wallet ownership or whole-wallet profit is invented',
          all(x['beneficial_owner'] is None and x['whole_wallet_profit'] is None for x in out['cases']) and
          out['summary']['A_current_carry_allocation'] is None)
    prose = json.dumps({'findings': out['findings'], 'missing': out['missing_public_inputs']}, ensure_ascii=False)
    check('Reader prose has no long dashes', '\u2014' not in prose and '\u2013' not in prose)
    result = {'schema_version': 1, 'financial_snapshot_timestamp': T,
              'verified_at_UTC': dt.datetime.now(dt.timezone.utc).isoformat(),
              'dataset': 'data/eth/credit_expansion_deep.json',
              'dataset_sha256': hashlib.sha256((D / 'credit_expansion_deep.json').read_bytes()).hexdigest(),
              'passed': all(x['passed'] for x in checks), 'checks': checks,
              'reader_report': {'path': 'research/eth/review/CREDIT-EXPANSION-DEEP.md',
                                'sha256': hashlib.sha256((ROOT / 'research/eth/review/CREDIT-EXPANSION-DEEP.md').read_bytes()).hexdigest()},
              'scope': 'Evidence integrity, receipt cash flows, historical code, lot allocation and debt reconciliation. Does not establish whole-wallet profit, beneficial ownership, confidential balances or a complete market census.'}
    (D / 'credit_expansion_deep_validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'passed': result['passed'], 'checks': len(checks),
                      'failed': [x for x in checks if not x['passed']]}, indent=2))
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
