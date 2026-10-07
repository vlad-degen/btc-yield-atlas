"""Candidate protocols from DefiLlama /protocols and their /protocol/{slug} histories.

Writes raw/eth/netmap-2026-10-07/candidates.json and proto/{slug}.json.gz (only the fields the map uses).
Re-runs skip files already present. Usage: python3 tools/eth/netmap/01_fetch.py [--workers 12]
"""
import concurrent.futures as cf, gzip, json, os, sys, time, urllib.request
from lib import RAW

YIELD_CATS = {'Liquid Staking', 'Liquid Restaking', 'Restaking', 'Staking Pool', 'Yield', 'Yield Aggregator',
              'Onchain Capital Allocator', 'Leveraged Farming', 'Basis Trading', 'Risk Curators', 'Options Vault',
              'Options', 'CeDeFi', 'Uncollateralized Lending', 'Farm', 'Liquidity Manager', 'Governance Incentives',
              'Dual-Token Stablecoin', 'Indexes', 'Insurance', 'Treasury Manager', 'Liquidity Automation'}
MIN = {'Dexs': 5e6, 'Lending': 2e6, 'CDP': 2e6, 'Derivatives': 10e6}
MANUAL = '''lido ether.fi-stake ether.fi-liquid eigencloud eigenlayer symbiotic karak kelp renzo puffer-stake swell-liquid-staking
swell-liquid-restaking stakewise-v3 rocket-pool coinbase-wrapped-staked-eth binance-staked-eth mantle-staked-eth meth-protocol frax-ether
stader ankr origin-ether bedrock-unieth liquid-collective dinero-pxeth concrete yield-basis fluid-lite treehouse-protocol cian-yield-layer
mellow-lrt mellow-core pendle spectra-v2 ethena-usde lagoon upshift veda yo-protocol avant-protocol liquity-v2 royco makina vesper
reservoir-protocol infinifi rocksolid lido-earn mev-capital gauntlet steakhouse-financial re7-labs sentora-curator nemo
uniswap-v3 uniswap-v4 uniswap-v2 curve-dex balancer-v2 balancer-v3 fluid-dex aerodrome-slipstream aerodrome-v1 velodrome-v2 velodrome-v3
gmx-v2-perps across ribbon thetanuts-finance derive stryke rysk hegic wildcat-protocol maple clearpool truefi
alchemix-v3 midas-rwa morpho-blue aave-v3 aave-v4 sparklend compound-v3 euler-v2 fluid-lending sky-lending liquity-v1 crvusd'''.split()


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'eth-netmap/1'}), timeout=120) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001 - retry any transport error
            if i == tries - 1:
                raise
            time.sleep(2 + 3 * i)


def strip(d):
    keep_chain = {}
    for ch, v in (d.get('chainTvls') or {}).items():
        keep_chain[ch] = {k: v.get(k) for k in ('tvl', 'tokensInUsd', 'tokens') if v.get(k)}
    return {k: d.get(k) for k in ('id', 'name', 'slug', 'category', 'url', 'description', 'chains', 'parentProtocol',
                                   'misrepresentedTokens', 'doublecounted', 'liquidstaking', 'methodology', 'twitter',
                                   'otherProtocols', 'tvl', 'tokensInUsd', 'tokens')} | {'chainTvls': keep_chain}


def fetch(slug):
    p = os.path.join(RAW, 'proto', slug + '.json.gz')
    if os.path.exists(p):
        return slug, 'cached'
    d = get(f'https://api.llama.fi/protocol/{slug}')
    with gzip.open(p + '.part', 'wt') as f:
        json.dump(strip(d), f)
    os.replace(p + '.part', p)
    return slug, 'ok'


def main():
    workers = int(sys.argv[sys.argv.index('--workers') + 1]) if '--workers' in sys.argv else 12
    P = json.load(open(os.path.join(RAW, 'protocols.json')))
    by = {p['slug']: p for p in P}
    cand = {}
    for p in P:
        cat, tvl = p.get('category'), p.get('tvl') or 0
        if (cat in YIELD_CATS and tvl >= 1e5) or (cat in MIN and tvl >= MIN[cat]):
            cand[p['slug']] = dict(name=p['name'], category=cat, tvl_now=tvl, why='category')
    for s in MANUAL:
        if s in by:
            cand.setdefault(s, dict(name=by[s]['name'], category=by[s].get('category'), tvl_now=by[s].get('tvl') or 0, why='manual'))
    json.dump(cand, open(os.path.join(RAW, 'candidates.json'), 'w'), indent=1)
    missing = [s for s in MANUAL if s not in by]
    print(len(cand), 'candidates; manual slugs not on DefiLlama:', ' '.join(missing))
    errs = []
    with cf.ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(fetch, s): s for s in cand}
        for i, f in enumerate(cf.as_completed(futs)):
            try:
                f.result()
            except Exception as e:  # noqa: BLE001
                errs.append((futs[f], str(e)[:120]))
            if i % 200 == 0:
                print(i, 'done', flush=True)
    json.dump(errs, open(os.path.join(RAW, 'fetch_errors.json'), 'w'), indent=1)
    print('errors', len(errs))


if __name__ == '__main__':
    main()
