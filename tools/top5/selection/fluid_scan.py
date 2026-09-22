# Fluid vaults with BTC collateral (Ethereum/Base/Arbitrum): all positions via VaultPositionsResolver.getAllVaultPositions; keep debt >= $2M
import json
from addrinfo import ecall
import addrinfo
addrinfo.RPC[1]='https://gateway.tenderly.co/public/mainnet'
R='0xaA21a86030EAa16546A759d2d10fd3bF9D053Bc7'; SEL='0x%s'
out=[]
for ch in (1,8453,42161):
    vs=json.load(open('../raw/fluid_vaults_%d.json'%ch))
    for v in vs:
        s0=v['supplyToken']['token0']; s1=v['supplyToken']['token1']; b0=v['borrowToken']['token0']; b1=v['borrowToken']['token1']
        ss=s0.get('symbol','')+('+'+s1['symbol'] if s1.get('symbol') else ''); bs=b0.get('symbol','')+('+'+b1['symbol'] if b1.get('symbol') else '')
        if 'BTC' not in ss.upper() or 'BTC' in bs.upper() or 'ETH' in bs.upper(): continue
        r=ecall(ch,R,SEL%'f752d757'+v['address'][2:].lower().rjust(64,'0'))
        if not r: print('fail',ch,v['address']); continue
        h=r[2:]; n=int(h[64:128],16); pos=[]
        for i in range(n):
            w=h[128+i*256:128+(i+1)*256]
            nft=int(w[0:64],16); owner='0x'+w[88:128]; sup=int(w[128:192],16); bor=int(w[192:256],16)
            pos.append((nft,owner,sup,bor))
        # T1: supply in collateral token decimals? Fluid resolver returns token amounts (not shares) for T1 in token decimals (1e12 extra for <18 dec? check)
        tot_s=sum(p[2] for p in pos); tot_b=sum(p[3] for p in pos)
        ts=int(v['totalSupply']); tb=int(v['totalBorrow'])
        print(ch,v['id'],v['type'],ss,'->',bs,'positions',n,'sum_supply/api_total',round(tot_s/ts,3) if ts else None,'sum_borrow/api_total',round(tot_b/tb,3) if tb else None,flush=True)
        bp=float(b0.get('price') or 1); bd=b0['decimals']; sp=float(s0.get('price') or 0); sd=s0['decimals']
        for nft,owner,sup,bor in sorted(pos,key=lambda p:-p[3])[:5]:
            debt_usd=bor/10**bd*bp if v['type'] in ('1','2') else None
            coll=sup/10**sd if v['type'] in ('1','3') else None
            print('   nft',nft,owner,'coll',coll,'debt$',round(debt_usd/1e6,2) if debt_usd else ('raw',bor),flush=True)
            if (debt_usd or 0)>=2e6 or (v['type'] in ('3','4') and tb and bor/tb>0.2):
                out.append(dict(chain=ch,vault=v['address'],vault_id=v['id'],type=v['type'],pair=ss+'->'+bs,nft=nft,owner=owner,coll_btc=coll,debt_usd=debt_usd,borrow_raw=bor,vault_total_borrow_raw=tb))
json.dump(out,open('../raw/fluid_btc_borrowers.json','w'),indent=1)
