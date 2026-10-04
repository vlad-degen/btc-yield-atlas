"""Build dollar funding evidence and a reader report from immutable captures."""
from __future__ import annotations
import csv, hashlib, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data/eth'

def read(name):return json.loads((DATA/(name+'.json')).read_text())
def write(name,data):(DATA/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')

def run():
    snap=read('funding_atlas_snapshot');hist=read('funding_atlas_history');holders=read('funding_atlas_borrowers')
    venues={v['id']:v for v in snap['venues']};reserves=[];collateral=[]
    for venue in snap['venues']:
        for asset in venue['assets']:
            if asset['status']!='measured at T':continue
            row={k:v for k,v in asset.items() if k!='raw'}
            explorer={'ethereum':'https://etherscan.io/address/','base':'https://basescan.org/address/','arbitrum':'https://arbiscan.io/address/','optimism':'https://optimistic.etherscan.io/address/'}.get(venue['chain'])
            row.update(venue_id=venue['id'],venue=venue['name'].strip(),chain=venue['chain'],block=venue['block'],pool=venue['pool'],oracle=venue['oracle'],source_url=explorer+venue['pool'] if explorer else venue.get('identity_source_url','https://github.com/bgd-labs/aave-address-book'))
            if asset['role']=='dollar':
                c=asset['configuration'];cap=c['borrow_cap_tokens'];debt=asset['debt_units']
                row['nominal_variable_debt_cap_headroom']=max(0,cap-debt) if cap and debt is not None else None
                row['base_rules_allow_new_borrow']=c['active'] and not c['frozen'] and not c['paused'] and c['borrowing_enabled'] and (not cap or (debt is not None and cap>debt))
                row['headroom_scope']='Borrow cap less observed variable debt. Legacy stable debt, facilitator limits, eMode, isolation, oracle, account and transaction checks can tighten it.'
                row['rate_scope']='Instantaneous stored variable APR; not a fixed rate or a promised effective borrower rate.'
                reserves.append(row)
            else:collateral.append(row)
    grouped={}
    for record in holders['position_calls']:
        label=record['label'];key=(label['venue'],label['borrower']);row=grouped.setdefault(key,{'venue_id':key[0],'address':key[1],'ETH_collateral':[],'dollar_debt':[],'ETH_collateral_USD':0.,'dollar_debt_USD':0.,'queried_calls':0,'successful_calls':0})
        row['queried_calls']+=1
        value=record['response'].get('result')
        if not value or value=='0x':continue
        row['successful_calls']+=1
        n=int(value,16)
        if label['field']=='configuration':row['user_configuration']=n
        elif label['field']=='emode':row['emode']=n
        elif label['field']=='account':
            fields=[int(value[i:i+64],16) for i in range(2,len(value),64)]
            if len(fields)==6:row['account']={'all_collateral_USD':fields[0]/1e8,'all_debt_USD':fields[1]/1e8,'available_borrow_USD':fields[2]/1e8,'weighted_liquidation_threshold':fields[3]/10000,'weighted_ltv':fields[4]/10000,'health_factor':fields[5]/1e18}
        else:
            asset=next(a for a in venues[key[0]]['assets'] if a['address']==label['asset_address'])
            units=n/10**asset['configuration']['decimals'];usd=units*asset['oracle_price_USD'] if asset['oracle_price_USD'] is not None else None
            if units>0:
                leg={'asset':asset['symbol'],'address':asset['address'],'units':units,'raw_units':str(n),'oracle_USD':usd,'reserve_id':asset['reserve_id'],'source_response':record['response']}
                row['ETH_collateral' if label['field']=='collateral' else 'dollar_debt'].append(leg)
    borrowers=[]
    for (venue_id,address),row in grouped.items():
        row['complete_queried_T_state']=row['queried_calls']==row['successful_calls']
        bitmap=row.get('user_configuration')
        for leg in row['ETH_collateral']:
            leg['enabled_as_collateral']=bool(bitmap&(1<<(2*leg['reserve_id']+1))) if bitmap is not None else None
            if leg['enabled_as_collateral'] and leg['oracle_USD'] is not None:row['ETH_collateral_USD']+=leg['oracle_USD']
        row['dollar_debt_USD']=sum(x['oracle_USD'] or 0 for x in row['dollar_debt'])
        row['has_enabled_ETH_collateral_and_dollar_debt']=row['ETH_collateral_USD']>0 and row['dollar_debt_USD']>0
        row.update(venue=venues[venue_id]['name'],chain=venues[venue_id]['chain'],block=venues[venue_id]['block'],carry_use_verified=False,who='Unidentified account',proceeds_scope='Not traced by this debt-token holder screen. ETH collateral plus dollar debt does not establish reinvestment.',amount_scope='Complete selected ETH-family collateral and dollar-token debt views.' if row['complete_queried_T_state'] else 'Partial returned views; measured amounts are lower bounds within the queried asset set.')
        if row['has_enabled_ETH_collateral_and_dollar_debt'] and row['dollar_debt_USD']>=1e6:borrowers.append(row)
    borrowers.sort(key=lambda r:r['dollar_debt_USD'],reverse=True)
    aave_usdc=next(r for r in reserves if r['venue_id']=='aave-ethereum' and r['symbol']=='USDC')
    aave_usdt=next(r for r in reserves if r['venue_id']=='aave-ethereum' and r['symbol']=='USDT')
    delta=aave_usdc['borrow_apr']-aave_usdt['borrow_apr']
    summary={'dollar_reserves':len(reserves),'ETH_family_reserves':len(collateral),'pool_instances':len(venues),'measured_pool_instances':sum(any(a['status']=='measured at T' for a in v['assets']) for v in venues.values()),'chains':sorted(set(v['chain'] for v in venues.values())),'measured_chains':sorted(set(v['chain'] for v in venues.values() if any(a['status']=='measured at T' for a in v['assets']))),'material_dollar_reserves_at_least_1M_variable_debt':sum((r['debt_USD'] or 0)>=1e6 for r in reserves),'base_rules_allow_new_borrow':sum(r['base_rules_allow_new_borrow'] for r in reserves),'monthly_rate_observations':len(hist['rows']),'monthly_rates_measured':sum(r['status']=='measured' for r in hist['rows']),'fixed_T_ETH_collateral_dollar_borrower_accounts_above_1M':len(borrowers),'complete_T_views_in_that_cohort':sum(r['complete_queried_T_state'] for r in borrowers),'holder_discovered_accounts':len(grouped),'successful_borrower_calls':sum(r['successful_calls'] for r in grouped.values()),'requested_borrower_calls':len(holders['position_calls']),'global_carry_capital_USD':None,'global_ETH_only_dollar_debt_USD':None,'aave_ethereum_USDC_minus_USDT_borrow_pp':delta*100}
    findings=[{'title':'Debt currency matters within the same chain','text':f"At T, Aave Ethereum USDC costs {100*aave_usdc['borrow_apr']:.2f}% APR while USDT costs {100*aave_usdt['borrow_apr']:.2f}%. The {100*delta:.2f} percentage-point funding difference is larger than the measured USDC differences among several chains. The tokens have different credit, liquidity and conversion dependencies.",'basis':'Fixed-block stored reserve rates, not an executable recommendation.'},
      {'title':'A low displayed rate can belong to a closed route','text':'Frozen reserves, disabled borrowing and caps below existing debt remain in the atlas. They describe debt already outstanding, rather than a new financing opportunity. Bridged and native versions of the same dollar token remain separate.'},
      {'title':'Liquidity and rates constrain the same trade','text':f"Ethereum Aave USDC holds about ${aave_usdc['cash_USD']/1e6:.2f}M physical underlying at its reserve while USDT holds ${aave_usdt['cash_USD']/1e6:.2f}M. These balances do not guarantee a permitted loan, flash loan or simultaneous investor exit."},
      {'title':'Reserve debt is not ETH carry','text':'Dollar reserve debt spans all collateral types. The borrower screen separately verifies enabled ETH-family collateral and dollar debt at T, then leaves use of loan proceeds unclassified until traced.'}]
    inputs=[]
    for name in ['funding_atlas_snapshot','funding_atlas_history','funding_atlas_borrowers']:
        p=DATA/(name+'.json');inputs.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    out={'schema_version':1,'target_timestamp':1790985599,'financial_snapshot_refreshed':False,'summary':summary,'findings':findings,'reserves':reserves,'collateral':collateral,'history':hist['rows'],'borrowers':borrowers,'borrower_discovery':holders['discovery'],'inputs':inputs,'raw_manifest':snap['raw_manifest'],'limitations':['The official address-book asset set is a dated discovery universe, not a full historical delisting registry. Pools and asset views are verified at T.','History is a sample of instantaneous reserve APR, not time-weighted or realized financing.','Current indexed holder discovery can miss an account that exited after T. A four-page limit remains explicit.','The base collateral configuration does not replace eMode, isolation or user configuration. Dollar debt cannot be attributed proportionally to ETH without tracing account funding.','Oracle marks can differ from stablecoin spot prices. No dollar token is assumed exactly one USD.','Physical reserve cash and nominal cap headroom are necessary diagnostics, not verified executable capacity.']}
    write('funding_atlas_chapter',out)
    fields=['venue','chain','symbol','block','address','borrow_apr','supply_apr','debt_units','debt_USD','cash_units','cash_USD','base_rules_allow_new_borrow','nominal_variable_debt_cap_headroom']
    with (DATA/'funding_atlas_reserves.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(reserves)
    with (DATA/'funding_atlas_history.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,['venue','asset','month','timestamp','block','borrow_apr','supply_apr','status'],extrasaction='ignore');w.writeheader();w.writerows(hist['rows'])
    lines=['# Dollar funding across chains','', 'Dollar carry starts with a financing choice. The same ETH collateral can support different dollar currencies and venues, with different interest, caps, oracles and repayment requirements. This atlas expands the selected Aave and Morpho analysis to additional dollar reserves and Spark. Every balance and stored rate below is read at the existing 2 October 2026, 23:59:59 UTC snapshot. Later holder discovery is labelled separately.','', '## What the expanded funding evidence shows','']
    for finding in findings:lines += ['### '+finding['title'],'',finding['text'],'']
    lines += ['## Dollar reserves at the snapshot','',f"The atlas measures {summary['dollar_reserves']} dollar reserves and {summary['ETH_family_reserves']} ETH-family reserves across {summary['measured_pool_instances']} measured pool instances on {len(summary['measured_chains'])} chains. {summary['material_dollar_reserves_at_least_1M_variable_debt']} dollar reserves each have at least $1 million of observed variable debt across all collateral types. These are financing venues, not a sum of ETH carry capital.",'','| Pool | Chain | Dollar token | Borrow APR | Physical cash USD | Base rules |','|---|---|---|---:|---:|---|']
    for row in reserves:
        cash=f"${row['cash_USD']/1e6:.3f}M" if row['cash_USD'] is not None else 'Unavailable'
        lines.append(f"| {row['venue']} | {row['chain']} | {row['symbol']} | {row['borrow_apr']*100:.3f}% | {cash} | {'Allow a new loan subject to account checks' if row['base_rules_allow_new_borrow'] else 'Restricted by the observed base rules'} |")
    lines += ['', 'Base rules combine active, frozen, paused and borrowing flags with nominal variable-debt cap headroom. They are not an execution test. Some issuer-funded currencies need separate facilitator rules; discounts or borrower-specific arrangements can change effective cost.','', '## Financing history','',f"The historical sample contains {summary['monthly_rate_observations']} market and date observations, including {summary['monthly_rates_measured']} successful stored-rate reads. Each bar represents the quoted annual rate at one dated block. The sample does not measure how long that rate prevailed or the cost paid by a borrower over the month.",'','## Look through the borrowers','',f"Current debt-token holder pages lead to {len(borrowers)} examined accounts with at least $1 million of dollar debt and enabled ETH-family collateral at T. Account health factors and collateral-use flags are read independently. Other collateral and debt can coexist in the account. The dollars may be invested, spent, idle or used to buy more ETH; this screen alone does not establish carry.",'','## Read the limits with the numbers','']
    lines += [x for limit in out['limitations'] for x in [limit,'']]
    lines += ['## Data and primary references','', '[Reserve measurements](../../../data/eth/funding_atlas_chapter.json), [reserve CSV](../../../data/eth/funding_atlas_reserves.csv), [monthly rate CSV](../../../data/eth/funding_atlas_history.csv).','', '[Aave pool configuration](https://aave.com/docs/aave-v3/smart-contracts/pool), [Aave reserve mechanics](https://www.aave.com/docs/aave-v3/concepts/reserve), [official Aave address book](https://github.com/bgd-labs/aave-address-book), [Spark contract documentation](https://docs.spark.fi/dev/deployments/mainnet).']
    (ROOT/'research/eth/en/DOLLAR-FUNDING-ATLAS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(summary))

if __name__=='__main__':run()
