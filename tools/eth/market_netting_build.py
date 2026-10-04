"""Build a bounded capital reconciliation from immutable historical evidence.

Physical custody, issuer accounting and adapter exposure are separate ledgers.
No global net figure is manufactured by subtracting unlike observations.
"""
import csv
import datetime as dt
import hashlib
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'data/eth'
RAW=ROOT/'raw/eth/research-closure-2026-10-04/market'
T=1790985599
BLOCK=26108081
UNIT=Decimal(10)**18
WETH='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
STETH='0xae7ab96520de3a18e5e111b5eaab095312d7fe84'
QUEUE='0x889edc2edab5f40e902b864ad4d7ade8e412f9b1'

def read(name):return json.loads((D/(name+'.json')).read_text())
def units(result):return Decimal(int(result,16))/UNIT
def values(result):
    s=result[2:]
    return [int(s[i:i+64],16) for i in range(0,len(s),64)]
def utc(timestamp):return dt.datetime.fromtimestamp(timestamp,dt.timezone.utc).isoformat().replace('+00:00','Z')
def proof(path):
    p=ROOT/path
    return {'path':path,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def write(name,value):(D/(name+'.json')).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def csv_file(name,rows):
    if not rows:return
    with (D/(name+'.csv')).open('w',newline='') as out:
        w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def build():
    issuer=read('market_netting_issuer_calls_T')
    custody=read('market_netting_custody_T')
    lending=read('weth_lending_markets_T')
    receipt=read('market_netting_lending_edges_T')
    lp=read('market_netting_lp_cash_T')
    curve=read('market_netting_curve_cash_T')
    hist=read('market_netting_lp_history_rpc')
    restake=read('market_netting_restaking_edges_T')
    kelp=read('market_netting_kelp_nesting_T')
    checks=read('market_netting_final_checks_T')
    snapshot=read('snapshot_manifest')
    ethereum_snapshot=next(x for x in snapshot['chains'] if x['chain']=='ethereum')
    assert int(checks['responses'][3]['result'],16)==1
    fresh_block=checks['responses'][4]['result']
    assert fresh_block['hash']==ethereum_snapshot['block_hash']
    assert int(fresh_block['number'],16)==BLOCK
    assert int(fresh_block['timestamp'],16)==T
    market=read('research_market_chapter')
    roots={}
    def root(address,asset,amount,label,group,source,raw_wei=None,excluded=False):
        key=(address,asset)
        assert key not in roots, ('duplicate physical custody node',key)
        roots[key]={'id':address+':'+asset,'address':address,'chain_id':1,'asset':asset,'amount_ETH':float(amount),
                    'raw_wei':str(raw_wei) if raw_wei is not None else None,'label':label,'group':group,
                    'source':source,'physical_root':'canonical_WETH_escrow' if asset=='WETH' else 'native_ETH_at_address',
                    'included_in_primary_custody_floor':not excluded,
                    'scope':'Physical custody in an examined yield venue. May include idle reserves, fees or pending capital; not proof every unit is earning.'}
    # Fixed block calls, canonical WETH total supply and native escrow match.
    issuer_by_sig={l.get('signature',l.get('name')):r for l,r in zip(issuer['labels'],issuer['responses'])}
    lido_book=units(issuer_by_sig['getTotalPooledEther()']['result'])
    lido_buffer=units(issuer_by_sig['getBufferedEther()']['result'])
    stat=values(issuer_by_sig['getBalanceStats()']['result'])
    external=units(issuer_by_sig['getExternalEther()']['result'])
    components={'active_CL_at_last_report_ETH':float(Decimal(stat[0])/UNIT),'pending_CL_at_last_report_ETH':float(Decimal(stat[1])/UNIT),
                'deposited_since_last_report_ETH':float(Decimal(stat[2])/UNIT),'buffered_ETH':float(lido_buffer),'external_stVault_backing_ETH':float(external)}
    accounting_sum=Decimal(stat[0]+stat[1]+stat[2])/UNIT+lido_buffer+external
    assert accounting_sum==lido_book
    weth_supply=units(issuer['responses'][7]['result'])
    weth_escrow=units(issuer['responses'][8]['result'])
    assert weth_supply==weth_escrow
    root(STETH,'native_ETH',lido_buffer,'Lido buffer','issuer_cash','data/eth/market_netting_issuer_calls_T.json',int(issuer_by_sig['getBufferedEther()']['result'],16))
    ref_slot=None
    for l,r in zip(custody['labels'],custody['responses']):
        if l.get('signature')=='getLastProcessingRefSlot()':ref_slot=int(r['result'],16)
        if l['kind']!='native_balance' or l['address']==QUEUE:continue
        if l['name'] not in ['Lido withdrawalVault()','Lido elRewardsVault()']:continue
        root(l['address'],'native_ETH',units(r['result']),l['name'].replace('()',''),'issuer_cash','data/eth/market_netting_custody_T.json',int(r['result'],16))
    queue_amount=units(issuer['responses'][10]['result'])
    queue_locked=units(checks['responses'][0]['result'])
    assert queue_locked==queue_amount
    root(QUEUE,'native_ETH',queue_amount,'Lido finalized withdrawal queue','withdrawal_claim_cash','data/eth/market_netting_issuer_calls_T.json',int(issuer['responses'][10]['result'],16),excluded=True)
    raw_lending={}
    for bundle in lending['raw_calls']:
        if bundle['chain']!='ethereum':continue
        for request,response in zip(bundle.get('requests') or [],bundle.get('responses') or []):
            if request[0]!='eth_call' or not response.get('result'):continue
            params=request[1][0];raw_lending[(params['to'].lower(),params['data'].lower())]=response['result']
    lending_rows=[]
    for item in lending['markets']:
        if item['chain']!='ethereum':continue
        a=item['aToken'].lower();debt=item['variableDebtToken'].lower()
        cash_result=raw_lending[(WETH,'0x70a08231'+a[2:].rjust(64,'0'))]
        claim_result=raw_lending[(a,'0x18160ddd')]
        debt_result=raw_lending[(debt,'0x18160ddd')]
        cash=units(cash_result);claim=units(claim_result);borrowing=units(debt_result)
        root(a,'WETH',cash,item['protocol'].title()+' WETH reserve cash','lending_cash','data/eth/weth_lending_markets_T.json',int(cash_result,16))
        lending_rows.append({'protocol':item['protocol'],'lender_claim_ETH':float(claim),'debt_ETH':float(borrowing),'cash_ETH':float(cash),
                             'claims_minus_cash_ETH':float(claim-cash),'claims_minus_cash_and_debt_ETH':float(claim-cash-borrowing),
                             'reported_reserve_deficit_ETH':item['extra_getters'].get('getReserveDeficit(address)'),
                             'scope':'Claims and debt are not additional WETH escrow. Reconciliation remainder is retained, not reclassified as principal.'})
    for l,r in zip(lp['labels'],lp['responses']):
        if l['kind']!='WETH_cash':continue
        root(l['address'],'WETH',units(r['result']),'Uniswap V3 '+l['counterasset']+'/WETH '+str(l['fee']),'LP_cash','data/eth/market_netting_lp_cash_T.json',int(r['result'],16))
    curve_identity={}
    for l,r in zip(curve['labels'],curve['responses']):
        if l['kind']=='coin':curve_identity[l['address']]='0x'+r['result'][-40:]
    for l,r in zip(curve['labels'],curve['responses']):
        if l['kind']!='cash':continue
        assert curve_identity[l['address']]==l['asset']
        asset='native_ETH' if l['root_asset']=='native_ETH' else 'WETH'
        root(l['address'],asset,units(r['result']),l['name'],'LP_cash','data/eth/market_netting_curve_cash_T.json',int(r['result'],16))
    floor=sum(Decimal(n['raw_wei'])/UNIT for n in roots.values() if n['included_in_primary_custody_floor'])
    weth_floor=sum(Decimal(n['raw_wei'])/UNIT for n in roots.values() if n['included_in_primary_custody_floor'] and n['asset']=='WETH')
    native_floor=floor-weth_floor
    assert weth_floor<=weth_supply
    # The ceiling includes every canonical WETH unit, even balances outside the
    # examined venues. It bounds this stated liquid custody scope, never CL ETH.
    scoped_ceiling=weth_supply+native_floor
    unassigned_weth=weth_supply-weth_floor
    grouped=defaultdict(Decimal)
    for n in roots.values():
        if n['included_in_primary_custody_floor']:grouped[n['group']]+=Decimal(n['raw_wei'])/UNIT
    rates={l['symbol']:units(r['result']) for l,r in zip(receipt['labels'],receipt['responses']) if l['kind']=='exchange_rate'}
    reserve_rows={}
    edges=[]
    for l,r in zip(receipt['labels'],receipt['responses']):
        if l['kind']=='exchange_rate':continue
        key=(l['protocol'],l['symbol'])
        row=reserve_rows.setdefault(key,{'protocol':l['protocol'],'asset':l['symbol'],'aToken':l['aToken'],'exchange_rate_ETH_per_receipt':float(rates[l['symbol']])})
        amount=units(r['result']);row[l['kind']+'_units']=float(amount);row[l['kind']+'_ETH_equivalent']=float(amount*rates[l['symbol']])
        if l['kind']=='lender_claim':
            edges.append({'id':l['protocol']+'_'+l['symbol'],'parent':'lido' if l['symbol']=='wstETH' else 'etherfi_stake' if l['symbol']=='weETH' else 'rocket_pool',
                          'child':l['protocol'],'asset':l['symbol'],'claim_units':float(amount),'ETH_equivalent':float(amount*rates[l['symbol']]),
                          'measurement':'Lender receipt total supply at T, converted at the T issuer accounting rate. Includes loaned receipts.',
                          'independent_root_addition_ETH':0,'reason':'Lending claims reuse issuer backing; debt remains a separate liability.',
                          'source':'data/eth/market_netting_lending_edges_T.json','additive_with_other_edges':False})
    steth_eigen=units(restake['strategy_underlying']['response']['result'])
    steth_eigen_cash=units(restake['responses'][3]['result'])
    eigen_share_to_custody_difference=steth_eigen-steth_eigen_cash
    assert abs(eigen_share_to_custody_difference)<Decimal('0.000000001')
    assert '0x'+restake['responses'][0]['result'][-40:]==STETH
    kelp_accounting=units(restake['responses'][5]['result'])
    kelp_nodes=[];kelp_eigen=Decimal(0);kelp_direct=Decimal(0)
    for item in kelp.get('converted_node_shares',[]):
        amount=units(item['response']['result']);kelp_eigen+=amount
        kelp_nodes.append({'node':item['node'],'eigen_strategy_share_units':float(Decimal(item['shares'])/UNIT),'stETH_underlying':float(amount)})
    for l,r in zip(kelp['labels'],kelp['responses']):
        if l['kind']=='direct_stETH' and r.get('result'):kelp_direct+=units(r['result'])
    kelp_pool_direct=units(checks['responses'][2]['result'])
    assert kelp_eigen<=steth_eigen
    edges.extend([
        {'id':'lido_eigen_stETH','parent':'lido','child':'eigenlayer_stETH_strategy','asset':'stETH','claim_units':float(steth_eigen),'ETH_equivalent':float(steth_eigen),'measurement':'Official strategy underlying token, current deposit permission, totalShares converted to underlying and physical stETH token custody all checked at T.','independent_root_addition_ETH':0,'reason':'The stETH already represents Lido backing.','source':'data/eth/market_netting_restaking_edges_T.json','additive_with_other_edges':False},
        {'id':'eigen_kelp_stETH','parent':'eigenlayer_stETH_strategy','child':'kelp_seven_node_delegators','asset':'stETH','claim_units':float(kelp_eigen),'ETH_equivalent':float(kelp_eigen),'measurement':'Each node deposit share converted with the T strategy sharesToUnderlying rate.','independent_root_addition_ETH':0,'reason':'Kelp node claims are a subset of the same Eigen strategy, then the same Lido stake.','source':'data/eth/market_netting_kelp_nesting_T.json','additive_with_other_edges':False},
    ])
    wst_lender_claim=sum(Decimal(str(row['lender_claim_ETH_equivalent'])) for row in reserve_rows.values() if row['asset']=='wstETH')
    # Daily adapter exposure is kept in its own time and valuation ledger.
    panel_edges=[]
    for product in market['products']:
        c=product['current']
        if c['status']!='observed':continue
        for asset,usd in c.get('selected_tokens_usd',{}).items():
            if asset.upper() not in ['STETH','WSTETH']:continue
            panel_edges.append({'protocol':product['id'],'category':product['category'],'asset':asset,'reported_value_USD':usd,
                                'reported_ETH_reference':usd/c['reference_ETH_USD'],'source_timestamp':c['source_timestamp'],
                                'source_age_seconds':c['source_age_seconds'],'default_category_enabled':product['category'] not in ['lending','cdp'],
                                'source_url':product['source_url'],'token_source_sha256':c['token_source_sha256']})
    default_reuse=sum(x['reported_value_USD'] for x in panel_edges if x['default_category_enabled'])
    full_reuse=sum(x['reported_value_USD'] for x in panel_edges)
    monthly=defaultdict(list);history_rows=[]
    for l,r in zip(hist['labels'],hist['responses']):
        if l['kind']!='cash':continue
        amount=float(units(r['result'])) if r.get('result') else None
        row={'month':l['month'],'target_timestamp':l['target_timestamp'],'block':l['block'],'block_hash':l['block_hash'],'block_timestamp':l['block_timestamp'],
             'pool':l['address'],'asset':l['asset'],'label':l['label'],'root_custody_ETH':amount,'status':'observed' if amount is not None else 'missing'}
        history_rows.append(row);monthly[l['month']].append(row)
    history_summary=[]
    for month,rows in sorted(monthly.items()):
        count=sum(x['root_custody_ETH'] is not None for x in rows)
        history_summary.append({'month':month,'target_timestamp':rows[0]['target_timestamp'],'observed_pools':count,'expected_pools':len(rows),
                                'root_custody_ETH':sum(x['root_custody_ETH'] for x in rows) if count==len(rows) else None,
                                'known_custody_subset_ETH':sum(x['root_custody_ETH'] or 0 for x in rows),
                                'missing_pools':len(rows)-count,'scope':'Same bounded current address census; not market-wide LP capital or investor yield.'})
    nft=read('etherfi_uniswap_positions')
    nft_weth=sum(x['amount0'] for x in nft if x['token0']==WETH)
    nft_receipt=sum(x['backing_equivalent_eth']-x['amount0'] for x in nft if x['token0']==WETH)
    manifest=[json.loads(line) for line in (RAW/'requests.jsonl').read_text().splitlines()]
    latest={}
    for record in manifest:latest[(record['key'],record['path'])]=record
    successful=[x for x in latest.values() if x['http_status']==200]
    unresolved=[{'id':'consensus_actual_T','quantity_ETH':None,'reason':'Canonical finalized header is captured, but full historical actual/effective validator balances and active/pending status sets remain unavailable from tried public sources.','scope':'Native solo, custodial and issuer validators; actual current balances, not validators times 32.'},
                {'id':'unexamined_liquid_custody','quantity_ETH':None,'reason':'Other ETH custody contracts and pools are not enumerated.','scope':'Additional LP factories, Balancer shared custody, Fluid, managed products, issuers, bridges and other chains.'},
                {'id':'canonical_weth_unassigned','quantity_ETH':float(unassigned_weth),'reason':'Measured WETH supply outside the examined address nodes. Its earning status is not classified.','scope':'A measured maximum remaining amount inside the stated canonical WETH universe.'},
                {'id':'issuer_physical_backing','quantity_ETH':None,'reason':'Oracle accounting does not establish each issuer validator balance at T or cross-issuer use of deposited receipts.','scope':'Lido CL report timing is measured; physical T CL census is not closed.'}]
    out={'schema_version':1,'financial_as_of_timestamp':T,'financial_as_of_UTC':utc(T),'block':BLOCK,'block_hash':fresh_block['hash'],'block_reverified_against_original_manifest':True,'financial_data_refreshed':False,
         'purpose':'A rooted reconciliation of an examined subset. Physical custody, issuer accounting and reported exposure have different scopes and clocks.',
         'global_unique_ETH':None,'global_unique_ETH_upper_bound':None,'global_net_market_NAV':None,'market_share_denominator':None,
         'headline':{'physical_custody_floor_ETH':float(floor),'physical_custody_floor_label':'Native ETH and canonical WETH custody floor in examined yield venues',
                     'extended_floor_including_withdrawal_queue_ETH':float(floor+queue_amount),'withdrawal_queue_ETH':float(queue_amount),
                     'canonical_WETH_scoped_ceiling_ETH':float(scoped_ceiling),'canonical_WETH_scoped_ceiling_label':'All canonical WETH plus the examined native ETH custody; excludes consensus and other native custody',
                     'unbounded_unknown':True,'unbounded_unknown_meaning':'The unexamined market has no numeric upper bound established by this evidence. This is not a claim that ETH supply is infinite.',
                     'earning_capital_floor_ETH':None,'coverage_percentage':None,'lido_wstETH_lending_repeat_ETH':float(wst_lender_claim)},
         'bounds':[{'id':'physical_custody_examined','label':'Measured physical custody in examined yield venues','lower_ETH':float(floor),'upper_ETH':float(floor),
                    'scope':'Exact sum at one Ethereum block of distinct native ETH holdings and canonical WETH claims, anchored to matching WETH native escrow. Some cash can be idle.','excluded':['Finalized withdrawal queue','Issuer consensus oracle balances','Non-ETH loan destinations','Other venue custody','All L2 native/WETH custody']},
                   {'id':'canonical_WETH_and_examined_native_scope','label':'Bounded liquid custody universe','lower_ETH':float(floor),'upper_ETH':float(scoped_ceiling),
                    'scope':'Canonical WETH held anywhere plus the named native ETH venues. Unknown WETH allocation can range from no additional earning custody to the entire unassigned supply.','excluded':['Actual consensus ETH','Other native ETH venue balances','Other wrapped/synthetic claims without root verification','Other chains']},
                   {'id':'global_market','label':'Global unique ETH capital','lower_ETH':None,'upper_ETH':None,
                    'scope':'Not measured. The custody subset is proof of underlying assets, not a complete market census or measure of assets currently earning.','excluded':[]}],
         'root_nodes':list(roots.values()),'root_groups_ETH':{k:float(v) for k,v in grouped.items()},
         'canonical_WETH':{'address':WETH,'native_escrow_ETH':float(weth_escrow),'total_supply_WETH':float(weth_supply),'reconciliation_difference_ETH':float(weth_escrow-weth_supply),
                           'assigned_to_examined_custody_ETH':float(weth_floor),'unassigned_to_examined_custody_ETH':float(unassigned_weth),
                           'rule':'Count named WETH holders once through the single native escrow. Never add the full escrow on top of those assigned holder balances.'},
         'duplicate_edges':edges,'duplicate_edges_are_additive':False,
         'dedup_examples':[
             {'id':'weth_escrow_and_holders','label':'Canonical WETH escrow and the examined holders','naive_sum_ETH':float(weth_supply+weth_floor),'duplicate_adjustment_ETH':float(weth_floor),'count_once_ETH':float(weth_supply),
              'scope':'The full canonical WETH physical universe, including unclassified wallet balances. This is not a total for assets earning yield.'},
             {'id':'lido_and_lender_claims','label':'Lido accounting plus Aave and Spark wstETH lender claims','naive_sum_ETH':float(lido_book+wst_lender_claim),'duplicate_adjustment_ETH':float(wst_lender_claim),'count_once_ETH':float(lido_book),
              'scope':'Issuer-accounting example at T. The issuer root is oracle accounting, not independently measured T consensus custody. Lending has created claims on existing stETH backing.'},
             {'id':'eigen_and_kelp_nodes','label':'Eigen stETH custody plus Kelp node claims on that strategy','naive_sum_ETH':float(steth_eigen_cash+kelp_eigen),'duplicate_adjustment_ETH':float(kelp_eigen),'count_once_ETH':float(steth_eigen_cash),
              'scope':'Underlying stETH receipt custody. Its physical consensus ETH is not added to the native/WETH floor.'}],
         'issuer_accounting':{'lido_book_ETH':float(lido_book),'components':components,'component_sum_ETH':float(accounting_sum),'component_reconciliation_difference_ETH':float(accounting_sum-lido_book),
                              'last_oracle_reference_slot':ref_slot,'last_oracle_reference_timestamp':1606824023+12*ref_slot,'last_oracle_reference_UTC':utc(1606824023+12*ref_slot),'oracle_reference_age_seconds_at_T':T-(1606824023+12*ref_slot),
                              'deposited_for_current_report_ETH':float(Decimal(stat[3])/UNIT),'deprecated_getBeaconStat_validator_counter':values(issuer_by_sig['getBeaconStat()']['result'])[:2],
                              'sum_counter_times_32_not_used':True,'is_actual_consensus_balance_at_T':False,
                              'scope':'Pool accounting read at T. Active and pending CL fields refer to the last oracle reference slot. External backing is accounted stVault backing, not the total value of all stVaults.',
                              'physical_root_addition_from_oracle_ETH':0},
         'lending_reconciliation':{'WETH_markets':lending_rows,'WETH_lender_claims_ETH':sum(x['lender_claim_ETH'] for x in lending_rows),
                                   'WETH_debt_ETH':sum(x['debt_ETH'] for x in lending_rows),'WETH_cash_ETH':sum(x['cash_ETH'] for x in lending_rows),
                                   'lender_claims_minus_cash_ETH':sum(x['claims_minus_cash_ETH'] for x in lending_rows),'receipt_markets':list(reserve_rows.values()),
                                   'scope':'Aave V3 and Spark Ethereum reserves only. Loan debt is not automatically subtracted from every market row: it changes investor equity, while spent or re-lent underlying must be traced.'},
         'restaking':{'eigen_stETH_strategy':'0x93c4b944d05dfe6df7645a86cd2206016c51564d','eigen_stETH_custody':float(steth_eigen_cash),'eigen_strategy_total_shares_underlying_stETH':float(steth_eigen),'eigen_share_to_custody_difference_stETH':float(eigen_share_to_custody_difference),'kelp_stETH_accounting':float(kelp_accounting),
                      'kelp_nodes_eigen_stETH':float(kelp_eigen),'kelp_nodes_direct_stETH':float(kelp_direct),'kelp_accounting_minus_measured_nodes_stETH':float(kelp_accounting-kelp_eigen-kelp_direct),
                      'kelp_deposit_pool_direct_stETH':float(kelp_pool_direct),'kelp_accounting_minus_measured_nodes_and_pool_stETH':float(kelp_accounting-kelp_eigen-kelp_direct-kelp_pool_direct),
                      'kelp_nodes':kelp_nodes,'kelp_share_of_eigen_stETH_strategy':float(kelp_eigen/steth_eigen),
                      'nested_graph_rule':'Kelp node shares are inside Eigen stETH custody, which is inside Lido backing. These amounts add no physical ETH on top of the issuer root.',
                      'native_restaking_exact_T_ETH':None,'adapter_native_freshness_note':'The captured current Eigen adapter uses a three-day native-validator data offset, a cached external query and timetravel=false. The frozen aggregate API date alone cannot establish the actual date of its native component; source version at T is not independently reproduced.'},
         'lp':{'pool_count':len(hist['pools']),'uniswap_tested_pair_fee_combinations':len(read('market_netting_lp_discovery_T')['labels']),'uniswap_existing_pools_at_T':len(lp['discovered_pools']),
               'curve_main_registry_pools_in_current_directory':curve['directory_pool_count'],'curve_examined_root_pools':len(curve['selected_root_pools']),
               'current_root_custody_ETH':float(grouped['LP_cash']),'monthly_history':history_summary,'monthly_history_source':'data/eth/market_netting_lp_history.csv',
               'historical_cash_observations':len(history_rows),'historical_cash_observations_successful':sum(x['status']=='observed' for x in history_rows),
               'historical_scope':'The 28 current verified addresses, observed at month-end. Current discovery causes survivorship limits. Cash is physical venue backing, not concentrated-liquidity investor principal, LP NAV, deposits or yield.',
               'etherfi_NFT_principal_WETH':nft_weth,'etherfi_NFT_principal_receipt_ETH_equivalent':nft_receipt,'etherfi_NFT_principal_total_ETH_equivalent':nft_weth+nft_receipt,
               'etherfi_NFT_rule':'The two active NFT WETH principal amounts sit inside the two pool cash nodes already counted. The weETH side is a claim on ether.fi staking backing. Neither is added again to the physical custody floor.'},
         'observed_panel_overlap':{'scope':'Repeated Lido stETH/wstETH receipt exposure inside the frozen daily adapter panel; separate from exact-T block measurements.',
                                  'default_selection_repeated_receipt_USD':default_reuse,'all_categories_repeated_receipt_USD':full_reuse,
                                  'default_selection_repeated_receipt_ETH_reference':sum(x['reported_ETH_reference'] for x in panel_edges if x['default_category_enabled']),
                                  'all_categories_repeated_receipt_ETH_reference':sum(x['reported_ETH_reference'] for x in panel_edges),'protocols_with_receipt_exposure':len({x['protocol'] for x in panel_edges}),
                                  'edges':panel_edges,'netting_applied_to_canonical_panel':False,
                                  'rule':'Observed receipt reuse is quantified but not mechanically subtracted to claim a global physical total. Issuer marks, source times, nested intermediate claims, receipt rate coverage and signed accounting differ.'},
         'unknowns':unresolved,'consensus':{'target_slot':15346798,'state_root':'0x14a3c4ae7fcd440993b15b81da8e0cc491d93d866ccc1b4d858add1d30441282',
                                          'actual_active_balance_ETH':None,'actual_all_validator_balance_ETH':None,'effective_active_balance_ETH':None,
                                          'header_finalized_and_canonical':True,'ETHSTORE_scope_note':'Daily ETH.STORE aggregates select validators active throughout the reward day and report effective/start/end balances. They are not an automatic match for all validators at the final T slot. Correct epoch-selector requests return 401 without an API key.',
                                          'actual_vs_effective_note':'Actual balance is the ETH held by a validator. Effective balance is consensus weight, rounded and capped by credentials and protocol rules. EIP-7251 allows compounding validator effective balances up to 2,048 ETH. Validator count times 32 is not used.'},
         'withdrawal_queue':{'native_ETH':float(queue_amount),'locked_for_finalized_claims_ETH':float(queue_locked),'native_minus_locked_ETH':float(queue_amount-queue_locked),'unfinalized_stETH_claims':float(units(checks['responses'][1]['result'])),
                             'rule':'Finalized queue ETH is held at a distinct native address and is separated from the active custody floor. Unfinalized stETH remains an issuer claim and is not added as new ETH.',
                             'added_to_lido_accounting_book':False},
         'sources':[proof('data/eth/'+name+'.json') for name in ['snapshot_manifest','weth_lending_markets_T','etherfi_uniswap_positions','market_netting_issuer_calls_T','market_netting_locator_T','market_netting_custody_T','market_netting_reserve_identity_T','market_netting_lending_edges_T','market_netting_lp_discovery_T','market_netting_lp_cash_T','market_netting_curve_cash_T','market_netting_lp_history_rpc','market_netting_restaking_edges_T','market_netting_kelp_nesting_T','market_netting_final_checks_T','research_market_chapter']]+[proof('raw/eth/2026-10-02/beacon_header_T-d792521a8e67ce74.json')],
         'raw_sources':successful,'raw_capture_manifest':'raw/eth/research-closure-2026-10-04/market/requests.jsonl',
         'limitations':['No percentage of global coverage can be calculated against the overlapping adapter total.',
                        'A custody floor proves physical ETH at identified yield venues, including idle cash. It does not prove that all units are currently earning or are immediately redeemable.',
                        'The scoped ceiling is valid only for the stated canonical WETH and named native-address universe. It cannot cap the global ETH yield market.',
                        'Oracle issuer balances and actual consensus T balances are not interchangeable.',
                        'All observations use the existing frozen T or previously verified historical blocks. New documentation captures are dated independently.',
                        'Debt and parent NAV are not universally additive or universally subtractable. A complete root census needs validator ownership, all liquid custody and all claim links.',
                        'Missing external custody, native consensus and other-chain bridge roots remain unbounded by the available measurements.']}
    write('market_netting_closure',out)
    csv_file('market_netting_roots',[{k:n[k] for k in ['id','address','chain_id','asset','amount_ETH','raw_wei','label','group','physical_root','included_in_primary_custody_floor','source']} for n in roots.values()])
    csv_file('market_netting_lp_history',history_rows)
    csv_file('market_netting_lp_monthly',history_summary)
    print(json.dumps(out['headline'],indent=2));print('Root groups',out['root_groups_ETH']);print('Restaking',out['restaking']['kelp_nodes_eigen_stETH'],out['restaking']['kelp_accounting_minus_measured_nodes_stETH'])
    print('History',len(history_rows),len(history_summary))

if __name__=='__main__':build()
