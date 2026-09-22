# USD value of reward tokens received (ETHFI, MORPHO, CRV, FXN) at receipt time via DefiLlama historical prices
import lib,time
blocks={'ETHFI':[(21675016,47100),(21718047,43000),(21777273,30000)],'MORPHO':[(21945659,6658.11),(22137090,12308.99),(22365523,7403.32),(22431811,137.54),(22494507,14.44)],'CRV':[(22230313,805.4),(22280649,502.9),(22338631,667.6),(22365523,256.1),(22431690,495.9),(22494524,481.1)],'FXN':[(22230313,339.3),(22280649,214.4),(22338631,294.0),(22365523,113.9),(22431690,237.6),(22494524,232.1)]}
gid={'ETHFI':'coingecko:ether-fi','MORPHO':'coingecko:morpho','CRV':'coingecko:curve-dao-token','FXN':'coingecko:fxn-token'}
rows=[];tot={}
for s,lst in blocks.items():
    for b,amt in lst:
        ts=int(lib.rpc('eth_getBlockByNumber',[hex(b),False])['timestamp'],16)
        p=lib.get(f'https://coins.llama.fi/prices/historical/{ts}/{gid[s]}')['coins'].get(gid[s],{}).get('price')
        rows.append((s,lib.dt(ts),amt,p,amt*p if p else None)); tot[s]=tot.get(s,0)+(amt*p if p else 0); time.sleep(0.3)
lib.save('reward_token_values.json',{'rows':rows,'tot':tot})
