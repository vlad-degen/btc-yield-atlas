"""Dated API token observations and history, preserving source-age and scope limits."""
import calendar, collections, datetime as dt, json
from collect import ROOT, RAW, T
from discover import FAMILY, ALIASES

def month_ends():
    out=[]
    for year in [2024,2025,2026]:
        for month in range(1,13):
            if (year,month)<(2024,10) or (year,month)>(2026,9):continue
            x=dt.datetime(year,month,calendar.monthrange(year,month)[1],23,59,59,tzinfo=dt.timezone.utc)
            out.append((x.strftime('%Y-%m'),int(x.timestamp())))
    return out

def previous(points,t):
    ps=[p for p in points if p['date']<=t]
    return max(ps,key=lambda x:x['date']) if ps else None

def build():
    requests=[json.loads(x) for x in (RAW/'requests.jsonl').read_text().splitlines()]
    registry=json.loads((ROOT/'data'/'eth'/'protocol_candidates.json').read_text())
    current=[];history=[];coverage=[]
    for pr in registry:
        key='protocol_'+pr['slug'].replace('.','_')
        row=next((r for r in reversed(requests) if r['key']==key and 'path' in r),None)
        if not row:coverage.append({'slug':pr['slug'],'status':'source_missing'});continue
        d=json.loads((ROOT/row['path']).read_text())
        chains=d.get('chainTvls',{})
        has_tokens=bool(d.get('tokensInUsd'))
        tvl=d.get('tvl') or []
        coverage.append({'slug':pr['slug'],'has_aggregate_token_history':has_tokens,'chains':len(chains),'first_tvl_date':tvl[0].get('date') if tvl else None,'source_sha256':row['sha256'],'misrepresented_tokens':d.get('misrepresentedTokens')})
        for period,t in [('snapshot',T)]+month_ends():
            point=previous(d.get('tokensInUsd',[]),t)
            units=previous(d.get('tokens',[]),t)
            if not point:
                if period!='snapshot':history.append({'protocol':pr['slug'],'period':period,'target_timestamp':t,'status':'token_observation_missing','eth_family_reported_usd':None})
                continue
            selected={a:v for a,v in point['tokens'].items() if a.upper() in FAMILY or (a.upper().startswith(('AETH','VARIABLEDEBT','SPWSTETH')) and 'ETH' in a.upper())}
            rec={'protocol':pr['slug'],'name':pr['name'],'category_current_hint':pr['category'],'period':period,'target_timestamp':t,'source_timestamp':point['date'],'source_age_seconds':t-point['date'],'eth_family_reported_usd':sum(selected.values()),'eth_family_positive_usd':sum(v for v in selected.values() if v>0),'eth_family_negative_usd':sum(v for v in selected.values() if v<0),'tokens_usd':selected,'tokens_units':{k:units['tokens'].get(k) for k in selected} if units and units['date']==point['date'] else None,'source_url':row['url'],'source_sha256':row['sha256'],'status':'dated_aggregator_observation_not_net_market','misrepresented_tokens':d.get('misrepresentedTokens')}
            if period=='snapshot':current.append(rec)
            else:history.append(rec)
        for chain,values in chains.items():
            # Borrowed/staking/pool2 lines are separate views, never additive chains.
            point=previous(values.get('tokensInUsd',[]),T)
            if point:
                selected={a:v for a,v in point['tokens'].items() if a.upper() in FAMILY}
                if selected: current.append({'protocol':pr['slug'],'name':pr['name'],'category_current_hint':pr['category'],'period':'snapshot_chain','chain':ALIASES.get(chain,chain),'source_timestamp':point['date'],'source_age_seconds':T-point['date'],'eth_family_reported_usd':sum(selected.values()),'tokens_usd':selected,'source_url':row['url'],'status':'chain_observation_separate_view_not_additive'})
    dest=ROOT/'data'/'eth'
    for name,data in [('protocol_eth_observations',current),('protocol_eth_history_monthly',history),('protocol_source_coverage',coverage)]:
        (dest/(name+'.json')).write_text(json.dumps(data,indent=2,ensure_ascii=False))
    agg=sorted([r for r in current if r['period']=='snapshot'],key=lambda r:r['eth_family_reported_usd'],reverse=True)
    print('Protocols with source',len(coverage),'snapshot observations',len(agg),'historical rows',len(history))
    print('Largest dated observations, NOT additive market:',[(r['protocol'],round(r['eth_family_reported_usd']/1e6,2),r['source_age_seconds']) for r in agg[:20]])

if __name__=='__main__':build()
