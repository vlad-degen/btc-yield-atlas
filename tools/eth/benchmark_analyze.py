"""Compare published vault returns with archive LST conversion rates."""
import bisect,json
from collect import ROOT,T
from normalize import month_ends

def run():
 out=ROOT/'data/eth';points={}
 for chain in ['ethereum','optimism']:
  d=json.loads((out/('benchmark_history_'+chain+'_rpc.json')).read_text())
  for r in d['responses']:
   lab=d['labels'][r['id']-1];t=lab['target_timestamp'];p=points.setdefault(t,{'target_timestamp':t})
   if 'error' in r:raise ValueError(r['error'])
   value=r.get('result')
   if lab['metric']=='block':
    p[chain+'_block_timestamp']=int(value['timestamp'],16)
    assert p[chain+'_block_timestamp']<=t,'future block'
   else:
    p[chain+'_'+lab['metric']]=int(value,16)/1e18 if value and value!='0x' else None
 rates=json.loads((out/'etherfi_rate_events.json').read_text());ts=[x['timestamp'] for x in rates]
 op=json.loads((out/'op_history_rates_rpc.json').read_text());op_rates={op['labels'][x['id']-1]['target_timestamp']:int(x['result'],16)/1e18 for x in op['responses'] if x.get('result') and x['result']!='0x'}
 for t,p in points.items():
  i=bisect.bisect_right(ts,t)-1;rate=rates[i]['new_rate'] if i>=0 else None
  p['liquidETH_rate']=rate;p['liquidETH_rate_timestamp']=rates[i]['timestamp'] if i>=0 else None
  supplies=[p.get(c+'_liquidETH_supply') for c in ['ethereum','optimism']]
  p['optimism_accountant_rate']=op_rates.get(t)
  p['published_book_nav_eth']=supplies[0]*rate+supplies[1]*op_rates[t] if rate is not None and None not in supplies and t in op_rates else None
 windows=[]
 for days in [7,14,30,90,180,365,730]:
  a=points[T-days*86400];b=points[T];r={'days':days,'end_timestamp':T,'start_timestamp':T-days*86400}
  for name,key in [('liquidETH','liquidETH_rate'),('stETH','ethereum_wstETH_rate'),('weETH','ethereum_weETH_rate')]:
   ratio=b[key]/a[key];r[name+'_cumulative_return']=ratio-1;r[name+'_annualized_apy']=ratio**(365/days)-1
  r['liquidETH_minus_stETH_cumulative_pp']=100*(r['liquidETH_cumulative_return']-r['stETH_cumulative_return'])
  r['liquidETH_minus_weETH_cumulative_pp']=100*(r['liquidETH_cumulative_return']-r['weETH_cumulative_return'])
  windows.append(r)
 monthly=[]
 for month,t in month_ends():
  p=points[t];prev=max(k for k in points if k<t and k in {u for _,u in month_ends()}|{1727740799})
  a=points[prev];row={'month':month,'end_timestamp':t,'book_nav_eth':p['published_book_nav_eth']}
  for name,key in [('liquidETH','liquidETH_rate'),('stETH','ethereum_wstETH_rate'),('weETH','ethereum_weETH_rate')]:row[name+'_monthly_return']=p[key]/a[key]-1
  monthly.append(row)
 for name,data in [('etherfi_staking_comparison',windows),('etherfi_history_points',sorted(points.values(),key=lambda x:x['target_timestamp'])),('etherfi_history_monthly',monthly)]:
  (out/(name+'.json')).write_text(json.dumps(data,indent=2))
 print(json.dumps(windows,indent=2))

if __name__=='__main__':run()
