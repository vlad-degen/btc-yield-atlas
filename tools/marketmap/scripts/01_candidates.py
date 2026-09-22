"""Build the candidate slug list from DefiLlama /protocols (raw/protocols.json).
Categories per task + manual list. Output: raw/candidates.json"""
import json, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(os.path.join(D, 'raw', 'protocols.json')))
CATS = ['Restaked BTC','Anchor BTC','Basis Trading','Leveraged Farming','Onchain Capital Allocator','Yield',
        'Staking Pool','Restaking','CDP','Yield Aggregator','Governance Incentives','Risk Curators']
# 'Lending' handled via whitelist (plain money markets are C0 context, computed from yields pools)
EXTRA_CATS_MIN = {'Farm':1e6,'Options Vault':1e6,'Options':1e6,'CeDeFi':1e6,'Uncollateralized Lending':1e5,
                  'Collateral Management':1e6,'Liquid Restaking':1e6,'Dual-Token Stablecoin':1e6}
MANUAL = '''babylon-protocol lombard-lbtc lombard-vaults solvbtc-lsts solv-basis-trading solv-strategies bedrock-unibtc gtbtc b14g
starknet-btc-staking exsat-staking-btc stacks-sbtc stacks-staking stackingdao yield-basis bitfi-basis bitfi-btc vishwa bitlayer-ybtc-family
avalon-cedefi avalon-superearn hermetica-hbtc hermetica-usdh mezo-earn mezo-vaults mezo-borrow zest-v2 zest-v1 acre ether.fi-liquid veda buzz-farming
concrete pumpbtc lorenzo-stbtc lorenzo-enzobtc satlayer symbiotic bouncebit-prime bouncebit bouncebit-staking maple river-omni-cdp accountable
midas-rwa hyperithm re7-labs upshift hyperbeat-earn hyperbeat-credit kraken-bitcoin-vault obeliskbtc merlins-seal solv-others solv-rwa
templar-protocol granite surge-credit liquidium chainflip-lending chainflip-amm 40-acres echo-lending vesu endur troves native-credit-pool
syntetika pareto-credit fusion-by-ipor tesseract yo-protocol avant-avbtc superform badger-dao proxy btcd multipli lagoon sentora-curator
kernel pell-network sovryn-zero bima-cdp bracket-vaults bracket-lst yala threshold-thusd rysk-v12 hegic hemi-staking zeus-btcsol
aera-v2 aera-v3 mellow-core gauntlet steakhouse-financial k3-capital re7-labs unit felix-vaults felix-cdp kelp
zerobase-cedefi manta-cedefi bitway-earn liminal-basis kraken-bitcoin bitget-bgbtc'''.split()
slugs = {}
for p in P:
    cat = p.get('category'); tvl = p.get('tvl') or 0
    if (cat in CATS and tvl >= 1e6) or (cat in EXTRA_CATS_MIN and tvl >= EXTRA_CATS_MIN[cat]):
        slugs[p['slug']] = dict(name=p['name'], category=cat, tvl_now=tvl, why='category')
byslug = {p['slug']: p for p in P}
for s in MANUAL:
    if s in byslug:
        p = byslug[s]
        slugs.setdefault(s, dict(name=p['name'], category=p.get('category'), tvl_now=p.get('tvl') or 0, why='manual'))
    else:
        print('manual slug not in /protocols:', s)
json.dump(slugs, open(os.path.join(D, 'raw', 'candidates.json'), 'w'), indent=1)
print(len(slugs), 'candidates')
