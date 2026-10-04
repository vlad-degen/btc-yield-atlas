"""Verified book/share metrics, risk and historical returns. No portfolio netting shortcuts."""
from decimal import Decimal, getcontext
import bisect, datetime as dt, json, math
from collect import ROOT, RAW, T, read_latest
getcontext().prec=80

def words(s): return [int(s[i:i+64],16) for i in range(2,len(s),64)]
def rpc_named(filename):
 d=json.loads((ROOT/'data'/'eth'/filename).read_text())
 return {d['labels'][r['id']-1]['label']:words(r['result']) for r in d['responses'] if r.get('result') and r['result']!='0x'}
def chain_data(chain):
 d=json.loads((ROOT/'data'/'eth'/('pilot_'+chain+'_rpc.json')).read_text());result={d['labels'][str(r['id'])]:r.get('result') for r in d['responses']}
 return result
def annualize(r,seconds):return float((Decimal(str(r))**(Decimal(365*86400)/Decimal(seconds)))-1)

def build():
 eth=chain_data('ethereum');op=chain_data('optimism');details=rpc_named('pilot_details_T.json');more=rpc_named('pilot_more_T.json')
 shares_eth=Decimal(int(eth['totalSupply'],16))/Decimal(10**18);shares_op=Decimal(int(op['totalSupply'],16))/Decimal(10**18);rate=Decimal(int(eth['getRate'],16))/Decimal(10**18)
 price=Decimal(str(read_latest('prices_T')['coins']['coingecko:ethereum']['price']))
 metrics={'target_timestamp':T,'ethereum_shares':float(shares_eth),'optimism_shares':float(shares_op),'rate_eth_per_share':float(rate),'published_book_nav_eth':float((shares_eth+shares_op)*rate),'published_book_nav_usd_nearest_quote':float((shares_eth+shares_op)*rate*price),'book_is_not_independent_asset_nav':True,'bridge_type':'burn/mint verified Teller additional source; in-flight messages remain an audit item','fee_bps':details['accountant_accountantState()'][9],'last_rate_update':details['accountant_accountantState()'][6],'rate_age_seconds':T-details['accountant_accountantState()'][6],'fee_owed_eth':details['accountant_accountantState()'][1]/1e18}
 accounts=[]
 for label,data in [('main_aave',words(eth['aave_account'])),('main_spark',words(eth['spark_account'])),('drone_aave',details['drone_aave']),('drone_spark',details['drone_spark'])]:
  coll=data[0]/1e8;debt=data[1]/1e8;hf=data[5]/1e18
  accounts.append({'position':label,'collateral_oracle_usd':coll,'debt_oracle_usd':debt,'equity_oracle_usd':coll-debt,'gross_leverage':coll/(coll-debt) if coll>debt else None,'health_factor':hf,'weighted_liquidation_threshold':data[3]/10000,'ltv_limit':data[4]/10000,'isolated_collateral_markdown_to_hf1':1-1/hf,'shock_qualification':'assumes debt and LT unchanged; not ETH/USD liquidation price for ETH debt'})
 metrics['aave_spark_accounts']=accounts
 ui=json.loads((RAW/'etherfi_ui_observation.json').read_text());metrics['ui_weighted_estimated_apy_percent']=sum(x['allocation_percent']*x['estimated_apy_percent']/100 for x in ui['positions']);metrics['ui_carry_percent']=sum(x['allocation_percent'] for x in ui['positions'] if 'Carry' in x['name']);metrics['ui_loop_percent']=sum(x['allocation_percent'] for x in ui['positions'] if 'Loop' in x['name']);metrics['ui_observation_not_fixed_block']=True
 logs=json.loads((ROOT/'data'/'eth'/'accountant_logs.json').read_text());rates=[];events=[]
 for row in logs['items']:
  decoded=row.get('decoded') or {};name=(decoded.get('method_call') or '').split('(')[0]
  if not row.get('block_timestamp'):continue
  ts=int(dt.datetime.fromisoformat(row['block_timestamp'].replace('Z','+00:00')).timestamp())
  if ts>T:continue
  if name=='ExchangeRateUpdated':
   w=words(row['data']);rates.append({'timestamp':ts,'block':row['block_number'],'old_rate':w[0]/1e18,'new_rate':w[1]/1e18,'declared_timestamp':w[2],'transaction_hash':row['transaction_hash']})
  else:events.append({'timestamp':ts,'block':row['block_number'],'event':name,'decoded':decoded,'transaction_hash':row['transaction_hash']})
 rates.sort(key=lambda x:(x['timestamp'],x['block']));times=[x['timestamp'] for x in rates]
 def at(t):
  i=bisect.bisect_right(times,t)-1
  return rates[i] if i>=0 else None
 windows=[]
 for days in [7,14,30,90,180,365,730]:
  start=at(T-days*86400);end=at(T)
  if start and end:
   ratio=end['new_rate']/start['new_rate'];windows.append({'days':days,'start_timestamp':T-days*86400,'start_rate_timestamp':start['timestamp'],'end_rate_timestamp':end['timestamp'],'cumulative_return':ratio-1,'annualized_apy':annualize(ratio,days*86400),'method':'published Accountant PPS; rewards outside NAV excluded'})
 monthly=[]
 from normalize import month_ends
 for month,t in month_ends():
  this=at(t);startdt=dt.datetime.fromtimestamp(t,dt.timezone.utc).replace(day=1,hour=0,minute=0,second=0);previous=at(int(startdt.timestamp())-1)
  if this and previous:
   ratio=this['new_rate']/previous['new_rate'];seconds=t-(int(startdt.timestamp())-1)
   monthly.append({'month':month,'end_rate':this['new_rate'],'end_rate_timestamp':this['timestamp'],'start_rate':previous['new_rate'],'monthly_return':ratio-1,'annualized_apy':annualize(ratio,seconds)})
 nftvalues=[]
 weeth_rate=Decimal(details['weETH_rate'][0])/Decimal(10**18)
 pools={500:'0x7a415b19932c0105c82fdb6b720bb01b0cc2cae3',100:'0x202a6012894ae5c288ea824cbc8a9bfb26a49b93'}
 for label,w in more.items():
  if not label.startswith('uni_position_'):continue
  lower=w[5]-(2**256 if w[5]>=2**255 else 0);upper=w[6]-(2**256 if w[6]>=2**255 else 0)
  lo=Decimal('1.0001')**(Decimal(lower)/2);hi=Decimal('1.0001')**(Decimal(upper)/2);s=Decimal(more['uni_slot0_'+pools[w[4]]][0])/Decimal(2**96);liquidity=Decimal(w[7]);clamped=min(hi,max(lo,s))
  amount0=liquidity*(hi-clamped)/(clamped*hi)/Decimal(10**18);amount1=liquidity*(clamped-lo)/Decimal(10**18)
  token0='0x'+format(w[2],'040x');token1='0x'+format(w[3],'040x')
  conversions={'0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2':Decimal(1),'0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee':weeth_rate}
  assert token0 in conversions and token1 in conversions, 'LP token must have a verified conversion'
  ethvalue=amount0*conversions[token0]+amount1*conversions[token1]
  nftvalues.append({'nft_id':int(label.split('_')[-1]),'pool':pools[w[4]],'tick_lower':lower,'tick_upper':upper,'liquidity':str(w[7]),'token0':token0,'token1':token1,'amount0':float(amount0),'amount1':float(amount1),'backing_equivalent_eth':float(ethvalue),'usd_nearest_quote':float(ethvalue*price),'tokens_owed0':w[10],'tokens_owed1':w[11],'uncollected_fee_growth_not_yet_valued':True})
 metrics['uniswap_principal_usd']=sum(x['usd_nearest_quote'] for x in nftvalues);metrics['uniswap_principal_eth']=sum(x['backing_equivalent_eth'] for x in nftvalues)
 dest=ROOT/'data'/'eth'
 for name,data in [('etherfi_verified_metrics',metrics),('etherfi_rate_events',rates),('etherfi_parameter_events',events),('etherfi_published_returns',windows),('etherfi_pps_history_monthly',monthly),('etherfi_uniswap_positions',nftvalues)]:
  (dest/(name+'.json')).write_text(json.dumps(data,indent=2,ensure_ascii=False))
 print(json.dumps(metrics,indent=2));print('Rates',len(rates),'parameter events',len(events),'monthly',len(monthly));print('Returns',windows)

if __name__=='__main__':build()
