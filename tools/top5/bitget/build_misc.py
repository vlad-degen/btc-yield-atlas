"""-> ../liquidity_ladder.csv, ../holders.csv, ../events.csv (values from raw/ files produced by the other scripts; see comments)"""
import json, csv
st=json.load(open('../raw/state_now.json'))
g=st['gtusdc']; mk=st['market']
idle=g['usdc_idle']/1e6; mliq=(mk['totalSupplyAssets']-mk['totalBorrowAssets'])/1e6
debt=mk['totalBorrowAssets']/1e6; gsh=g['balance_aera']/1e18*g['convertToAssets_1e18']/1e6
ext=g['totalAssets()']/1e6-gsh
lad=[
 ('0 same block','gtusdc idle USDC (liquidityAdapter=0x0, so only idle is withdrawable by a plain redeem)',round(idle,2),'USDC','any gtusdc holder','on-chain RPC: USDC.balanceOf(gtusdc)'),
 ('0 same block','Morpho bgBTC/USDC market unborrowed liquidity (supply - borrow); reachable by allocator deallocate or permissionless forceDeallocate (penalty 0.001%)',round(mliq,2),'USDC','gtusdc allocators (Gauntlet Safe 0xae95..., bot 0xa690...) or any holder via forceDeallocate','Morpho.market(id); gtusdc.forceDeallocatePenalty(adapter)=1e13 (0.001%)'),
 ('0 same block','= liquidity available to external (non-vault) gtusdc holders',round(idle+mliq,2),'USDC',f'external holders hold ${ext:,.0f} -> coverage {100*(idle+mliq)/ext:.1f}%','sum of rows above vs gtusdc.totalAssets - vault shares'),
 ('0 same tx (atomic)','Full de-leverage of the Aera vault: withdraw gtusdc -> repay -> deallocate -> repeat (~5 loops of the $9.3M real liquidity) or Morpho flash loan; the vault owns gtusdc shares worth ~= its debt',round(debt,2),'USDC debt repaid','Aera guardian (Gauntlet bot 0x1A57... via Forwarder 0x58c6...) + allocator/forceDeallocate','circular funding: vault gtusdc shares $%.2fM vs debt $%.2fM'%(gsh,debt)),
 ('0 same block','bgBTC sell-side liquidity on Morph: Native RFQ CreditVault (LP = Bitget omnibus, 99.99% of wNLP-BGBTC)',22.39999536,'bgBTC','RFQ takers / liquidators','bgBTC.balanceOf(0x4df7...); wNLP-BGBTC holders'),
 ('~1 hour','Aera async redemption of vault units (requestRedeem -> solved by guardian); observed 40 min on 9 Sep; depositRefundTimeout 3600 s',801.41,'bgBTC NAV','only unit holder: Bitget omnibus EOA 0x9EB5...','ProvisionerV2 events / omnibus txs'),
 ('1 day','CCIP bgBTC Morph -> Ethereum: outbound bucket 65 bgBTC, refill 65 bgBTC/day (Ethereum inbound 70/day); owner EOA 0xdb25... can raise limits with no timelock (did so 29 Jul and 14 Aug)',65,'bgBTC/day','anyone bridging via CCIP (Bitget omnibus in practice)','BurnMintTokenPool 0xf50b... getCurrentOutboundRateLimiterState; LockReleaseTokenPool 0xa1f0... inbound'),
 ('~12-13 days','Full exit of 801.7 bgBTC collateral to Ethereum at current CCIP limits (estimate: 801.7/65)',801.7,'bgBTC','Bitget','estimate'),
 ('~2 days (7 in docs)','Morph canonical bridge withdrawal to Ethereum (USDC/ETH), per L2BEAT finalization; docs walkthrough says 7 days',None,'','any Morph user','raw/web/l2beat_morph.txt; raw/web/morph_docs_bridge.txt'),
 ('instant (Bitget books)','Bitget Earn express redemption BGBTC->BTC 1:1 for 0.1% fee (VIP discounts); backed by Bitget balance sheet / idle BGBTC 382.59 (32.32% not deployed)',382.58881232,'BGBTC idle','Bitget Earn users','Bitget API landingPage/statistics 21 Sep; product FAQ'),
 ('T+4 (3-5 days)','Bitget Earn standard redemption, no fee',1184,'BGBTC supply','Bitget Earn users','Bitget product info redeemDelayTime=4; 30 Jul article'),
 ('off-chain','BTC reserve: single P2PKH address 19pFLWW3CwjZujRWpVEMdguBMZEqPuj5nA (Chainlink PoR 1,419.9997 BTC); burn/release process off-chain',1419.9997,'BTC','Bitget','mempool.space; Chainlink PoR 0xADcc914F...'),
]
with open('../liquidity_ladder.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['horizon','source','amount','unit','who_can_access','evidence']); w.writerows(lad)
# holders
gh=json.load(open('../raw/gtusdc_holders.json')); px=g['convertToAssets_1e18']/1e6
ah=json.load(open('../raw/aera_holders.json'))
bm=json.load(open('../raw/bgbtc_morph_holders.json')); be=json.load(open('../raw/bgbtc_eth_holders.json'))['items']
H=[]
tot_units=sum(int(x['value']) for x in ah)
lab={'0x9eb53a82d9f390dbe94b6b8b15ca32b523195ca4':'Bitget omnibus EOA (inference: gas + 0.1 bgBTC from Bitget hot wallet 0x1AB4...; all bgBTC arrives via CCIP from Ethereum; Bitget API reports 801.41 BTC in this vault)'}
for x in ah:
    a=x['address']['hash'].lower(); v=int(x['value'])
    H.append(('Aera vault units gtOVBG','Morph',a,lab.get(a,'EIP-7702 wallet / EOA (dust)'),v/1e18,v/tot_units))
totg=sum(int(x['value']) for x in gh)
for x in gh[:25]:
    a=x['address']['hash'].lower(); v=int(x['value'])
    l='Aera vault bgBTC Earn (0x85a1...)' if a=='0x85a1d961f1d1bbd9b4a6d96106c5bf9ae91f0510' else 'EIP-7702 wallet delegated to 0x490Aac77... (inference: Bitget Wallet smart account)'
    H.append(('gtusdc (USD value)','Morph',a,l,round(v/1e18*px,2),v/totg))
ex=[int(x['value'])/1e18*px for x in gh if x['address']['hash'].lower()!='0x85a1d961f1d1bbd9b4a6d96106c5bf9ae91f0510']
H.append(('gtusdc summary','Morph','(all non-vault holders)',f'{len(ex)} holders; median ${sorted(ex)[len(ex)//2]:.2f}; >$100k: {sum(1 for e in ex if e>1e5)}; >$10k: {sum(1 for e in ex if e>1e4)}; <$100: {sum(1 for e in ex if e<100)}',round(sum(ex),2),sum(ex)/(totg/1e18*px)))
ts=sum(int(x['value']) for x in bm)
nm={'0xad10d07901dc3195c3cb5e78e061f4ea8d9b4905':'Morpho Blue (vault collateral)','0x4df7557734b382eb542bea6c74786d398df4cc19':'Native CreditVault (LP = Bitget omnibus)','0x1ab4973a48dc892cd9971ece8e01dcc7688f8f23':'Bitget hot wallet (labelled on Ethereum)','0x9eb53a82d9f390dbe94b6b8b15ca32b523195ca4':'Bitget omnibus EOA','0x26209d9f0dc3ac0129c3fb1badabfeb9ee728c66':'EOA (unlabelled)'}
for x in bm[:6]:
    a=x['address']['hash'].lower(); v=int(x['value'])
    H.append(('bgBTC','Morph',a,nm.get(a,x['address'].get('name') or ''),v/1e8,v/ts))
te=sum(int(x['value']) for x in be)
nme={'0xa1f0caf824d5bbf103b33172a711e58c6cab2a04':'CCIP LockReleaseTokenPool (backs Morph supply)','0x1ab4973a48dc892cd9971ece8e01dcc7688f8f23':'Bitget hot wallet (Blockscout/Etherscan label)','0xffa8db7b38579e6a2d14f9b347a9ace4d044cd54':'Bitget 35 (exchange label)'}
for x in be[:4]:
    a=x['address']['hash'].lower(); v=int(x['value'])
    H.append(('bgBTC','Ethereum',a,nme.get(a,''),v/1e8,v/te))
H.append(('BGBTC (Bitget books)','off-chain','Bitget disclosure','supply 1,184 BGBTC; 801.41 in Gauntlet vault (67.68%), 382.59 idle; reserves 1,420.01 BTC (119.93%); no user count disclosed',1184,1.0))
with open('../holders.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['asset','chain','address','label','amount','share'])
    for h in H: w.writerow([h[0],h[1],h[2],h[3],h[4],f'{h[5]*100:.4f}%'])
print('ladder + holders written; ext',round(sum(ex)),'n',len(ex))
