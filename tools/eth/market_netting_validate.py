"""Validate the bounded reconciliation without asserting global completeness."""
import csv
import hashlib
import json
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'data/eth'
v=json.loads((D/'market_netting_closure.json').read_text())
checks=[]
def check(name,condition,detail=None):
    checks.append({'name':name,'passed':bool(condition),'detail':detail})
    assert condition,name
check('global quantities remain unmeasured',all(v[k] is None for k in ['global_unique_ETH','global_unique_ETH_upper_bound','global_net_market_NAV','market_share_denominator']))
check('earning status and global coverage not inferred',v['headline']['earning_capital_floor_ETH'] is None and v['headline']['coverage_percentage'] is None)
check('frozen T and block unchanged',v['financial_as_of_timestamp']==1790985599 and v['block']==26108081 and not v['financial_data_refreshed'])
check('original canonical hash reverified',v['block_hash']=='0x9f430d0cc4301a9f8ea0315223c2ed6e66373f6454baac771cac7449d725ba37' and v['block_reverified_against_original_manifest'])
nodes=v['root_nodes'];keys=[(n['chain_id'],n['address'],n['asset']) for n in nodes]
check('physical addresses and asset claims not duplicated',len(keys)==len(set(keys)))
physical=sum(Decimal(n['raw_wei'])/Decimal(10**18) for n in nodes if n['included_in_primary_custody_floor'])
check('physical custody sums from exact raw wei',abs(float(physical)-v['headline']['physical_custody_floor_ETH'])<1e-8)
queue=[n for n in nodes if n['group']=='withdrawal_claim_cash']
check('one separately excluded finalized queue',len(queue)==1 and not queue[0]['included_in_primary_custody_floor'])
check('queue native balance matches locked claim funds',v['withdrawal_queue']['native_minus_locked_ETH']==0 and not v['withdrawal_queue']['added_to_lido_accounting_book'])
check('WETH has a single physical root',v['canonical_WETH']['reconciliation_difference_ETH']==0 and all(n['physical_root']=='canonical_WETH_escrow' for n in nodes if n['asset']=='WETH'))
check('assigned WETH plus unassigned supply reconciles',abs(v['canonical_WETH']['assigned_to_examined_custody_ETH']+v['canonical_WETH']['unassigned_to_examined_custody_ETH']-v['canonical_WETH']['total_supply_WETH'])<1e-8)
check('scope ceiling contains custody floor',v['headline']['canonical_WETH_scoped_ceiling_ETH']>=v['headline']['physical_custody_floor_ETH'])
check('Lido book exact component reconciliation',v['issuer_accounting']['component_reconciliation_difference_ETH']==0)
check('CL oracle not promoted to actual T physical root',not v['issuer_accounting']['is_actual_consensus_balance_at_T'] and v['issuer_accounting']['physical_root_addition_from_oracle_ETH']==0 and v['issuer_accounting']['last_oracle_reference_timestamp']<v['financial_as_of_timestamp'])
check('no validator count times 32 estimate',v['issuer_accounting']['sum_counter_times_32_not_used'] and v['consensus']['actual_active_balance_ETH'] is None and v['consensus']['effective_active_balance_ETH'] is None)
check('duplicate edges add no roots',all(e['independent_root_addition_ETH']==0 and not e['additive_with_other_edges'] for e in v['duplicate_edges']))
r=v['restaking']
check('Kelp node claim is inside Eigen custody',r['kelp_nodes_eigen_stETH']<=r['eigen_stETH_custody'] and abs(sum(n['stETH_underlying'] for n in r['kelp_nodes'])-r['kelp_nodes_eigen_stETH'])<1e-8)
check('Kelp remainder retained',abs(r['kelp_nodes_eigen_stETH']+r['kelp_nodes_direct_stETH']+r['kelp_deposit_pool_direct_stETH']+r['kelp_accounting_minus_measured_nodes_and_pool_stETH']-r['kelp_stETH_accounting'])<1e-8)
with (D/'market_netting_lp_history.csv').open() as f:rows=list(csv.DictReader(f))
check('LP cash history complete for bounded census',len(rows)==700 and all(row['status']=='observed' and row['root_custody_ETH']!='' for row in rows) and len(v['lp']['monthly_history'])==25)
check('month summaries contain exactly 28 distinct pools',all(len({r['pool'] for r in rows if r['month']==m['month']})==28 and m['observed_pools']==m['expected_pools']==28 and m['missing_pools']==0 for m in v['lp']['monthly_history']))
check('historical blocks and timestamps remain before snapshot',all(int(row['block_timestamp'])<=int(row['target_timestamp'])<v['financial_as_of_timestamp'] for row in rows))
check('daily adapter panel not mechanically netted',not v['observed_panel_overlap']['netting_applied_to_canonical_panel'])
for source in v['sources']:
    p=ROOT/source['path'];check('source hash '+source['path'],hashlib.sha256(p.read_bytes()).hexdigest()==source['sha256'])
for source in v['raw_sources']:
    p=ROOT/source['path'];check('raw hash '+source['path'],hashlib.sha256(p.read_bytes()).hexdigest()==source['sha256'])
article=ROOT/'research/eth/review/MARKET-NETTING-CLOSURE.md'
check('no long dashes in article','\u2014' not in article.read_text() and '\u2013' not in article.read_text())
check('BTC original unchanged',hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest()=='ee05709e085406a6b0da19717e974834c6ae48cea54f34840c830fbc9eaf1222')
out={'passed':all(x['passed'] for x in checks),'checks':checks,'scope':'Validates calculations, provenance and declared boundaries in the bounded closure. Passing does not establish a complete global market, a consensus balance or earning status.'}
(D/'market_netting_validation.json').write_text(json.dumps(out,indent=2)+'\n')
print('Bounded reconciliation and evidence hashes valid. Global native and earning-capital measurements remain open.')
