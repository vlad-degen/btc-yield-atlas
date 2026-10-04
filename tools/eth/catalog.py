"""Evidence-aware catalog and segment screens, without inventing an additive market total."""
import collections,datetime as dt,json
from collect import ROOT,RAW,T,read_latest
from discover import FAMILY

def abi_string(value):
 if not value or value=='0x':return None
 raw=bytes.fromhex(value[2:])
 if len(raw)>=64:
  off=int.from_bytes(raw[:32],'big');length=int.from_bytes(raw[off:off+32],'big');return raw[off+32:off+32+length].decode(errors='replace')
 return raw.rstrip(b'\0').decode(errors='replace')

def run():
 dest=ROOT/'data/eth';assets={};vaults=json.loads((dest/'vault_registry_rpc_T.json').read_text());responses={x['id']:x for x in vaults['responses']};meta=json.loads((dest/'vault_assets_T.json').read_text())
 for r in meta['responses']:
  l=meta['labels'][r['id']-1];a=assets.setdefault(l['asset'],{'chain':'ethereum','address':l['asset'],'identity_source':'fixed-block ERC20 metadata','asset_kind':'unclassified','underlying_verified':False});v=r.get('result')
  if l['signature']=='decimals()' and v and v!='0x':a['decimals']=int(v,16)
  elif l['signature'] in ['symbol()','name()']:a[l['signature'][:-2]]=abi_string(v)
 for a in assets.values():
  s=(a.get('symbol') or '').upper();a['asset_kind']='accounting_unit' if s.startswith('IAU_') else 'native_ETH_wrapper' if s=='WETH' else 'ETH_family_receipt_candidate' if s in FAMILY else 'outside_ETH_core';a['redemption_accounting_verified']=s in ['WETH','STETH','WSTETH','WEETH','RSETH'];a['underlying_verified']=False;a['underlying_verification_scope']='Independent physical reserve reconciliation not performed; redemption/conversion identity is a separate field.'
  if s=='IAU_WSTETH' and (dest/'treehouse_denomination_history.json').exists():a['redemption_accounting_verified']=json.loads((dest/'treehouse_denomination_history.json').read_text())['historical_wstETH_denomination_verified']
 products=[]
 for p in vaults['products']:
  rec={**p,'identity_status':'public adapter candidate with fixed-block view calls','target_timestamp':T,'target_block':vaults['block'],'source':'vault_registry_rpc_T.json'};vals={}
  for i,l in enumerate(vaults['labels'],1):
   if l['product']==p['address']:vals[l['signature']]=responses[i].get('result')
  asset=vals.get('asset()');asset='0x'+asset[-40:] if asset and asset!='0x' else None;rec['asset']=asset;rec['asset_symbol']=assets.get(asset,{}).get('symbol');rec['is_ETH_core_candidate']=(rec['asset_symbol'] or '').upper() in FAMILY or (rec['asset_symbol'] or '').startswith('IAU_');rec['book_assets_raw']=str(int(vals['totalAssets()'],16)) if vals.get('totalAssets()') and vals['totalAssets()']!='0x' else None;rec['share_supply_raw']=str(int(vals['totalSupply()'],16)) if vals.get('totalSupply()') and vals['totalSupply()']!='0x' else None;rec['external_deposits_verified']=False;rec['independent_NAV_reconciled']=False
  products.append(rec)
 products.insert(0,{'name_hint':'ether.fi Liquid ETH','address':'0xf0bb20865277abd641a307ece5ee04e79073416c','chains':['ethereum','optimism'],'canonical_identity':'one logical burn/mint share product','asset_symbol':'ETH accounting','is_ETH_core_candidate':True,'book_nav_eth':json.loads((dest/'etherfi_verified_metrics.json').read_text())['published_book_nav_eth'],'strategy_class':'EH hybrid','independent_NAV_reconciled':False,'source':'etherfi_verified_metrics.json'})
 if (dest/'mono_accountant_T.json').exists():
  products.append({'name_hint':'Liquid Monad ETH nested sleeve','address':'0xa024063b630d554078bbf985718b22f3c6870ee0','chains':['ethereum','monad'],'asset_symbol':'WETH accounting','is_ETH_core_candidate':True,'target_timestamp':T,'source':'mono_identity_T.json; mono_accountant_T.json; mono_remote_T.json','held_by_Liquid_ETH_entire_Ethereum_supply':True,'same_rate_across_chains_verified':False,'external_deposits_verified':False,'independent_NAV_reconciled':False,'not_additive_with_parent':True})
 pendle=[];coverage=[]
 for c in [1,42161,8453,10]:
  first=read_latest('pendle_markets_'+str(c));rows=first['results'][:]
  for skip in range(100,first['total'],100):rows.extend(read_latest('pendle_markets_'+str(c)+'_'+str(skip))['results'])
  ids={x['id'] for x in rows};assert len(ids)==first['total'],'Pendle pagination coverage'
  coverage.append({'chain_id':c,'listed_markets':first['total'],'collected_unique_markets':len(ids)})
  for r in rows:
   sym=(r.get('accountingAsset') or {}).get('symbol','').upper()
   if sym not in FAMILY:continue
   expiry=int(dt.datetime.fromisoformat(r['expiry'].replace('Z','+00:00')).timestamp())
   pendle.append({'chain_id':c,'address':r['address'],'pt':r['pt']['address'],'sy':r['sy']['address'],'underlying':r['underlyingAsset']['address'],'name':r['pt']['symbol'],'accounting_asset':r['accountingAsset']['symbol'],'accounting_asset_address':r['accountingAsset']['address'],'underlying_symbol':r['underlyingAsset']['symbol'],'expiry':r['expiry'],'expired_at_T':expiry<=T,'active_at_collection':r['isActive'],'implied_apy':r.get('impliedApy'),'underlying_apy':r.get('underlyingApy'),'pool_liquidity_usd':r.get('liquidity',{}).get('usd'),'data_updated_at':r.get('dataUpdatedAt'),'target_snapshot_verified':False,'non_additive_with_SY_backing':True,'source':'https://api-v2.pendle.finance/core/v1/'+str(c)+'/markets'})
 pools=json.loads((dest/'yield_pool_candidates.json').read_text());screen=[]
 for p in pools:
  if p['tvlUsd']<5e6:continue
  cat=p.get('category_hint');hint='E5 lending' if cat in ['Lending','Risk Curators'] else 'E7 liquidity' if cat in ['Dexs','Liquidity manager'] else 'E6 fixed yield' if p['project']=='pendle-v2' else 'unverified'
  screen.append({'id':p['pool'],'project':p['project'],'chain':p['normalized_chain'],'symbol':p['symbol'],'reported_full_pool_tvl_usd':p['tvlUsd'],'display_apy':p.get('apy'),'apy_base':p.get('apyBase'),'apy_rewards':p.get('apyReward'),'mechanism_hint':hint,'asset_components':p['matched_components'],'underlying_addresses':p.get('underlyingTokens'),'fixed_block_verified':False,'not_additive':True})
 for name,data in [('asset_registry',list(assets.values())),('product_registry',products),('material_pool_screen',screen),('pendle_eth_market_screen',pendle),('pendle_source_coverage',coverage)]:
  (dest/(name+'.json')).write_text(json.dumps(data,indent=2,ensure_ascii=False))
 print('Vault products',len(products),'ETH core vault candidates',sum(x.get('is_ETH_core_candidate',False) for x in products),'material pools',len(screen),'Pendle',coverage,'ETH accounting markets',len(pendle),'unexpired',sum(not x['expired_at_T'] for x in pendle))

if __name__=='__main__':run()
