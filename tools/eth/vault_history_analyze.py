"""Keep asset-denominated returns distinct from ETH-denominated returns."""
import json
from collect import ROOT,T

def run():
 d=json.loads((ROOT/'data/eth/vault_history_rpc.json').read_text());points={}
 for r in d['responses']:
  l=d['labels'][r['id']-1];p=points.setdefault(l['name'],{}).setdefault(l['timestamp'],{'timestamp':l['timestamp']});val=r.get('result');p[l['signature']]=val if val and val!='0x' else None
 rse=json.loads((ROOT/'data/eth/rseth_benchmark_rpc.json').read_text());rse_rates={rse['labels'][x['id']-1]['target_timestamp']:int(x['result'],16)/1e18 for x in rse['responses'] if x.get('result') and x['result']!='0x'}
 tree_identity=json.loads((ROOT/'data/eth/treehouse_denomination_history.json').read_text())['historical_wstETH_denomination_verified']
 benchmark=json.loads((ROOT/'data/eth/etherfi_history_points.json').read_text());wst_rates={x['target_timestamp']:x['ethereum_wstETH_rate'] for x in benchmark}
 out=[]
 for name,pp in points.items():
  for days in [7,14,30,90,180,365,730]:
   a=pp[T-days*86400];b=pp[T];key='convertToAssets(uint256)';valid=a[key] and b[key] and a['asset()']==b['asset()']
   ratio=int(b[key],16)/int(a[key],16) if valid else None
   eth_ratio=ratio if name=='Fluid Lite ETH' else ratio*rse_rates[T]/rse_rates[T-days*86400] if name=='CIAN rsETH' and ratio and rse['historical_oracle_identity_verified'] else ratio*wst_rates[T]/wst_rates[T-days*86400] if name=='Treehouse tETH' and ratio and tree_identity else None
   out.append({'product':name,'days':days,'asset_address':'0x'+b['asset()'][-40:] if b['asset()'] else None,'asset_pps_cumulative_return':ratio-1 if ratio else None,'asset_pps_annualized_apy':ratio**(365/days)-1 if ratio else None,'ETH_return_confirmed':eth_ratio is not None,'ETH_pps_cumulative_return':eth_ratio-1 if eth_ratio else None,'ETH_pps_annualized_apy':eth_ratio**(365/days)-1 if eth_ratio else None,'reason':None if valid else 'rate unavailable or underlying changed; no zero assigned','note':'Fluid Lite asset is stETH, rebasing units already reflected in assets/share. CIAN ETH conversion uses the historically verified rsETH oracle, without market depeg or external rewards. Treehouse IAU is historically verified as wstETH-denominated; its book unit is converted via wstETH rate, without asserting independent backing. Concrete external payouts and private terms are not reflected by flat PPS alone.'})
 (ROOT/'data/eth/vault_history_comparison.json').write_text(json.dumps(out,indent=2));print([x for x in out if x['days'] in [365,730]])

if __name__=='__main__':run()
