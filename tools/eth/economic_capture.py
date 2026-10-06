"""Read-only financing captures for the BTC economic-question revision."""
import json, sys
from pathlib import Path
import finalization_capture as c
from carry_borrow_history import monthly_blocks

D=c.DATA; MORPHO='0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb'
AAVE='0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2'
SPARK='0xc13e21b648a5ee794902342038ff3adab66be987'
TOKENS={'USDC':('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',6),'USDT':('0xdac17f958d2ee523a2206206994597c13d831ec7',6),'PYUSD':('0x6c3ea9036406852006290770bedfcaba0e23a0e8',6),'USDS':('0xdc035d45d973e3ec169d2276ddab16f1e407384f',18),'DAI':('0x6b175474e89094c44da98b954eedeac495271d0f',18)}
def read(n):return json.loads((D/(n+'.json')).read_text())
def words(x):return [int(x[i:i+64],16) for i in range(2,len(x),64)] if isinstance(x,str) and len(x)>=66 else []
def address(x):return '0x'+format(x,'040x')
def registry():
 selected=[v for v in read('economic_upshift_eth_registry')['items'] if v['chain']==1 and v['vault_name'] not in ['Test WETH Tokenized Account ','Ethena Growth sUSDe']]
 markets=[m for m in read('carry_economics_chapter')['borrow_markets'] if m.get('chain')=='ethereum' and m.get('market_id') and m['collateral_symbol'] in ['weETH','wstETH','WETH','rETH']]
 rows=[]
 for v in selected:
  a=v['address']; name=v['vault_name']
  for sig in ['asset()','totalAssets()','totalSupply()','convertToAssets(uint256)']:
   rows.append(c.call(name+'|'+sig,a,sig,c.enc_uint(10**18) if 'uint256' in sig else ''))
  for o in [a]+[x['address'] for x in v.get('operators',[])]:
   rows.append(c.call(name+'|'+o+'|AaveAccount',AAVE,'getUserAccountData(address)',c.enc_addr(o)))
   rows.append(c.call(name+'|'+o+'|SparkAccount',SPARK,'getUserAccountData(address)',c.enc_addr(o)))
   for m in markets:rows.append(c.call(name+'|'+o+'|'+m['market_id'],MORPHO,'position(bytes32,address)',m['market_id'][2:]+c.enc_addr(o)))
 c.rpc('economic_upshift_positions_T',rows,batch_size=20,delay=.3)
 c.interfaces({'sentora_eth':next(v['address'] for v in selected if v['vault_name']=='Sentora ETH'),'sentora_account':'0x9AA69b81BA8b762c4dcE28bE4fEB12990550fa33'},'economic_upshift_interfaces')

def stage1():
 pc=read('reader_product_chapters')['products']; legs=[]
 for p in pc:
  if p['id']=='concrete':continue
  for l in p['charts']['loanLegs']['rows']:
   if l['debtAsset'] in TOKENS and l.get('debtUSD',0)>1 and l['collateralAsset']!='PRIME' and ('Aave' in l['protocol'] or 'Spark' in l['protocol']):
    legs.append({'id':p['id'],'name':p['name'],'account':l['account'].lower(),'venue':'Spark' if 'Spark' in l['protocol'] else 'Aave','symbol':l['debtAsset']})
 legs.append({'id':'reservoir-eth','name':'Reservoir ETH Yield','account':'0xf6cd9e8415162c8fb3c52676c7ca68812a34f76e','venue':'Aave','symbol':'USDC'})
 months=monthly_blocks()+[{'month':'snapshot','timestamp':c.T,'block':c.BLOCK}]
 reserves=sorted(set((l['venue'],l['symbol']) for l in legs));rows=[]
 for m in months:
  for venue,sym in reserves:
   rows.append(c.call(m['month']+'|'+venue+'|'+sym+'|reserve',AAVE if venue=='Aave' else SPARK,'getReserveData(address)',c.enc_addr(TOKENS[sym][0]),m['block']))
 (D/'economic_aave_legs.json').write_text(json.dumps({'legs':legs,'months':months},indent=2)+'\n')
 c.rpc('economic_reserves_history',rows,batch_size=20,delay=.3)

def stage2():
 x=read('economic_aave_legs');rr=read('economic_reserves_history')['records']; by={r['label']:r for r in rr};rows=[]
 for m in x['months']:
  for l in x['legs']:
   r=by[m['month']+'|'+l['venue']+'|'+l['symbol']+'|reserve']; w=words(r['response'].get('result'))
   if len(w)>10 and w[10]:rows.append(c.call('|'.join([m['month'],l['id'],l['account'],l['venue'],l['symbol']]),address(w[10]),'balanceOf(address)',c.enc_addr(l['account']),m['block']))
 c.rpc('economic_aave_debt_history',rows,batch_size=20,delay=.3)

def morpho():
 ec=read('carry_economics_chapter'); mid=lambda cs,ls:next(m['market_id'] for m in ec['borrow_markets'] if m.get('chain')=='ethereum' and m.get('market_id') and m['collateral_symbol']==cs and m['loan_symbol']==ls)
 legs=[{'id':'liquid','account':a,'market':mid(cs,ls),'outer':True} for a,cs,ls in [('0xf0bb20865277abd641a307ece5ee04e79073416c','weETH','RLUSD'),('0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3','weETH','RLUSD'),('0xf0bb20865277abd641a307ece5ee04e79073416c','weETH','USDC'),('0xf0bb20865277abd641a307ece5ee04e79073416c','weETH','PYUSD')]]
 for p in read('carry_variants_expansion')['products'][:2]:
  for l in p['positionsT']:
   if l['protocol']=='Morpho Blue':legs.append({'id':p['id'],'account':l['account'],'market':l['market_id'],'outer':l['collateral_symbol'] in ['wstETH','WETH']})
 legs += [{'id':'makina-deth','account':'0xD1A2d9DF5db842DA2Ee81075Fa441602B2352915','market':mid('wstETH','USDT'),'outer':True}]
 # Royco's exact market is fixed by the existing public loan evidence.
 roy=next(p for p in read('reader_product_chapters')['products'] if p['id']=='royco')['charts']['loanLegs']['rows'][0]
 royid=next(u.split('/market/')[1] for u in roy['sourceURLs'] if '/market/' in u)
 legs.append({'id':'royco','account':roy['account'],'market':royid,'outer':True})
 # Registry bindings are discovery evidence; ownership is tested separately.
 registry=read('economic_upshift_eth_registry')['items']; positions=read('economic_upshift_positions_T')['records']
 for r in positions:
  w=words(r['response'].get('result'))
  if r['label'].count('|')==2 and len(w)==3 and w[1]>0:
   name,account,market=r['label'].split('|')
   if market.startswith('0x'):
    legs.append({'id':'upshift-'+name.lower().replace(' ','-'),'name':name,'account':account,'market':market,'outer':True})
 months=monthly_blocks()+[{'month':'snapshot','timestamp':c.T,'block':c.BLOCK}]; rows=[]
 for m in months:
  for market in sorted(set(l['market'] for l in legs)):
   for sig,suffix in [('idToMarketParams(bytes32)','params'),('market(bytes32)','market')]:rows.append(c.call(m['month']+'|'+market+'|'+suffix,MORPHO,sig,market[2:],m['block']))
  for l in legs:rows.append(c.call('|'.join([m['month'],l['id'],l['account'].lower(),l['market'],'position']),MORPHO,'position(bytes32,address)',l['market'][2:]+c.enc_addr(l['account']),m['block']))
  rows.append(c.call(m['month']+'|yieldbasis|get_state','0x5f8d24f33cc5a1d5d1bf012261e6a2214c92233c','get_state()',block=m['block']))
  rows.append(c.call(m['month']+'|yieldbasis|rate','0x5f8d24f33cc5a1d5d1bf012261e6a2214c92233c','rate()',block=m['block']))
  trove=read('economic_trove_source')['record']
  rows.append(c.call(m['month']+'|liquity|trove',trove['address'],trove['signature'],trove['argument'],m['block']))
 (D/'economic_morpho_legs.json').write_text(json.dumps({'legs':legs,'months':months},indent=2)+'\n')
 c.rpc('economic_morpho_history',rows,batch_size=8,delay=.65)

def follow():
 x=read('economic_morpho_legs');rr={r['label']:r for r in read('economic_morpho_history')['records']};rows=[]
 for m in x['months']:
  for market in sorted(set(l['market'] for l in x['legs'])):
   ps=words(rr[m['month']+'|'+market+'|params']['response'].get('result'));mk=words(rr[m['month']+'|'+market+'|market']['response'].get('result'))
   if ps and mk and any(ps) and mk[4]:
    rows.append(c.call(m['month']+'|'+market+'|rate',address(ps[3]),'borrowRateView((address,address,address,address,uint256),(uint128,uint128,uint128,uint128,uint128,uint128))',''.join(c.enc_uint(v) for v in ps+mk),m['block']))
    rows.append(c.call(m['month']+'|'+market+'|oracle',address(ps[2]),'price()',block=m['block']))
 c.rpc('economic_morpho_rates',rows,batch_size=8,delay=.65)

def upshift_binding():
 selected=[v for v in read('economic_upshift_eth_registry')['items'] if v['chain']==1 and v['vault_name'] not in ['Test WETH Tokenized Account ','Ethena Growth sUSDe']]; rows=[]
 loanaccounts=['0xfB9776DE51A24Eb75E11110fAE659e54B346658f','0x90882e7C28dDf0ac1177033A310aeeD8eFf25E90']
 for v in selected:
  for sig in ['getTotalAssets()','getSharePrice()','lpTokenAddress()','assetsUpdatedOn()','externalAssets()','owner()','operatorAddress()','managementFeePercent()','performanceFeeRate()','withdrawalFee()','lagDuration()']:
   rows.append(c.call(v['vault_name']+'|'+sig,v['address'],sig))
  for a in loanaccounts:rows.append(c.call(v['vault_name']+'|whitelist|'+a.lower(),v['address'],'whitelistedSubAccounts(address)',c.enc_addr(a)))
 c.rpc('economic_upshift_binding_T',rows,batch_size=8,delay=.65)

if __name__=='__main__':{'registry':registry,'reserves':stage1,'debt':stage2,'morpho':morpho,'follow':follow,'binding':upshift_binding}[sys.argv[1]]()
