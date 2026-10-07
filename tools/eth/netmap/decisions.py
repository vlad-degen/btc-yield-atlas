"""Classification and netting decisions for the ETH counted-once map, one place, each with its reason.

Read with tools/eth/netmap/03_build.py. Snapshot 2026-10-02. Sources: DefiLlama protocol and adapter code, the
on-chain product research in research/eth/en/, and the issuers' own documentation.
"""

UNCLASSIFIED = []

# ---- rows that are not counted (listed in the site's "listed but not counted" table) --------------------------------
EXCLUDE = {
    'ssv-network': 'Validator infrastructure (distributed validators). The ETH belongs to the staking providers that run on it, counted at their issuers.',
    'obol': 'Validator infrastructure (distributed validators); the ETH is counted at the staking providers.',
    'justlend-v1': 'ETH token on Tron. Ethereum backing and redemption not verified.',
    'nexus-mutual': 'Capital pool of a cover mutual; NXM holders, not ETH depositors, own it.',
    'unslashed': 'Cover capital pool; not an ETH deposit product.',
    'ante-finance': 'Cover capital pool; not an ETH deposit product.',
    'cozy-earn': 'Cover capital pool; not an ETH deposit product.',
    'idex-v1': 'Balances left in a retired exchange contract; earns nothing.',
    'powh3d': 'Game contract, not a yield product.',
    'fomo3d': 'Game contract, not a yield product.',
    'wise-token': 'Reserve behind the WISE token; holders of WISE, not ETH depositors, own it.',
    'derive-v2': 'Margin on an options exchange; traders\' collateral, not a yield product.',
    'dydx-v3': 'Margin on a perp exchange.', 'apex-omni': 'Margin on a perp exchange.', 'extended-perps': 'Margin on a perp exchange.',
    'aevo-perps': 'Margin on a perp exchange.', 'nado-spot': 'Exchange balances.', 'serum': 'Exchange balances.',
    'fulcrom-perps': 'Margin on a perp exchange.', 'mux-perps': 'Margin on a perp exchange.', 'deri-v4': 'Margin on a derivatives exchange.',
    'contango-v2': 'Leveraged positions opened by traders in money markets; the collateral is counted there and at the issuers.',
    'etherfi-borrowing-market': 'ether.fi Cash collateral; mostly Liquid ETH shares, counted in Liquid ETH.',
    'summer.fi-pro': 'Position manager for money-market loans.',
    # curators: their vaults lend inside Morpho and Euler, which the money-market segment counts
    **{s: 'Curator of lending vaults; the ETH sits in Morpho or Euler (money markets).' for s in '''k3-capital gauntlet steakhouse-financial
       kpk clearstar sentora-curator re7-labs mev-capital ultrayield-curator galaxy-curation 9summits block-analitica alphagrowth anthias-labs
       damm-capital yearn-curating api3 avantgarde varlamore-capital mt-pelerin 722-capital gami-labs singularv alphaping b.protocol-curator
       rockawayx apostro hyperithm telos-consilium'''.split()},
    'concrete': ('Concrete Delta weETH (307k ETH) is one principal\'s own position, not a pooled product: a Bitfinex-linked wallet moved its '
                 'Aave position into the vault\'s Safe on 10 Dec 2025 and holds 100% of the shares; it borrows $176M of stablecoins against it '
                 '(research/eth/en/gaps/CONCRETE-DELTA.md). ctwstETH+ (45k ETH) is that Safe\'s own circular holding. Excluded like Avalon in the BTC map; '
                 'the weETH stays counted at ether.fi.'),
    # product-notes review, 7 Oct 2026 (data/eth/netmap/product_notes.csv, flag column)
    'puffer-unifi': 'Same pufETH as the Nucleus row.', 'puffer-vaults': 'Same vaults as the Nucleus row.',
    'swell-earn': 'Same swETH as the Nucleus row.', 'mitosis': 'Same weETH balances as Theo straddle vaults.',
    'moonwell-vaults': 'Lends inside Morpho (money markets).', 'ultrayield-vaults': 'Lends inside money markets.',
    'katana-pre-launch': 'Deposits sit in Yearn vaults counted in the Yearn row.',
    'extra-finance-leverage-farming': 'Borrows from Extra Finance vaults; positions, not deposits.',
    'yield-basis': 'Same WETH pool as YieldBasis WETH, counted on-chain.',
    'pulsex-v1': 'PulseChain copy of WETH, not ETH.', 'aquarius-stellar': 'Custodial ETH tokens on Stellar.',
    'stellar-dex': 'Custodial ETH tokens on Stellar.', 'fermiswap': 'Proprietary market maker\'s inventory.',
    'bisonfi': 'Proprietary market maker\'s inventory.', 'cyclone': 'Mixer, not a yield product.',
    'alchemist': 'A wallet, not a yield product.', 'odyssey-finance': 'Not a product; adapter holds a few wallets.',
    'turtle-club': 'Distribution layer for other vaults counted elsewhere.', 'king-protocol': 'Wrapper of restaking tokens counted at their issuers.',
    'aera-v2': 'Treasury vaults of DAOs, not outside deposits.', 'aera-v3': 'Treasury vaults of DAOs, not outside deposits.',
    'pools:balancer-v2': 'Balancer v2 ETH pools above $1M are the 80BAL/20WETH governance lock, not a yield pool.',
    'yieldfi': 'Counts its own yETH receipt.', 'sushi-bentobox': 'Holds an unidentified GETH token.',
    'infrared-finance': 'BERA staking; its ETH is Dolomite dWETH counted in Dolomite.',
    'meta-pool-eth': 'Adapter frozen at exactly 10,527 ETH for over a year.',
    'hemi-staking': 'egETH balance flat for a year; no issuer row to check against.',
    'ether.fi-liquid': 'Same ether.fi Liquid vaults as the Veda row; counted once there (Liquid ETH on-chain, the rest as Veda).',
    'rocksolid-network': 'Same vault as the Lagoon row (Rocksolid is a Lagoon vault); counted once as Rocksolid rETH.',
    'nonce-capital': 'Curator of ether.fi Liquid ETH; counted once as Liquid ETH.',
    'tulipa-capital': 'Curator of Rocksolid rETH; counted once as Rocksolid.',
    'dialectic': 'Curator of Royco ETH; counted once as Royco.',
    'nemo-trading': 'Curator of NEMO ETH Prime on Upshift; counted in the Upshift row.',
    'tau-labs': 'Curator; its ETH vaults lend in money markets. TAU InfiniFi ETH Carry is counted on-chain.',
    # LP-staking aggregators: they hold DEX pool tokens already counted in the pools
    'convex-finance': 'Stakes Curve pool tokens counted in Curve.', 'aura': 'Stakes Balancer pool tokens counted in Balancer.',
    'stake-dao-yield': 'Stakes Curve pool tokens counted in Curve.', 'badger-dao': 'Holds DEX pool tokens counted in the pools.',
    'pickle': 'Holds DEX pool tokens counted in the pools.',
    # liquidity managers run positions in DEX pools that the pool rows count
    **{s: 'Manages positions in DEX pools counted in the pool rows.' for s in '''arrakis-modular arrakis-v2 steer-protocol gamma ichi
       kodiak-islands xtoken snuggle thedeep baseline-protocol aegis-markets stonkbrokers-smart-lp yieldflow-yield-farming arrowfarm
       skate-fi arcadia-v2'''.split()},
    'sosovalue-indexes': 'Index token backed by exchange custody; size not verifiable on-chain.',
    'stakingverse': 'LUKSO staking (LYX), mislabelled as ETH by the adapter.',
    'opengdp-shared-security': 'Restaking of non-ETH assets.',
    'smardex-usdn': 'Dollar product: wstETH backs a delta-neutral stablecoin (USDN); holders earn in dollars.',
    'river-omni-cdp': 'Borrowing venue; the collateral is counted at its issuers.',
}

# ---- category overrides (DefiLlama category otherwise decides) --------------------------------------------------------
CATEGORY = {
    'ether.fi-stake': 'restaking',        # weETH is a restaking token (EigenLayer); DefiLlama lists it under liquid staking
    'cap': 'credit',                       # restakers' wstETH/weETH cover loans made by Cap's stablecoin to named operators
    'native-credit-pool': 'credit',        # lends to market makers
    'gain': 'farming',                     # Kelp Gain vaults (agETH, hgETH): points and rsETH lending
    'mantle-restaking': 'restaking', 'mellow-restaking': 'restaking', 'eigenpie': 'restaking', 'inceptionlrt-(isolated-restaking)': 'restaking',
    'yieldnest': 'restaking',              # ynETH max: restaking token basket
    'treehouse-protocol': 'loops', 'fluid-lite': 'loops', 'cian-yield-layer': 'loops', 'origami-finance': 'loops', 'juice-finance': 'loops',
    'index-coop': 'loops',                 # icETH: leveraged staked ETH
    'reserve-protocol': 'staking',         # ETH+: basket of staking tokens
    'extra-finance-leverage-farming': 'farming',
    'pendle-v2': 'fixed_yield', 'spectra-v2': 'fixed_yield', 'napier': 'fixed_yield', 'hourglass': 'fixed_yield', 'tranchess-yield': 'fixed_yield',
    'rysk-v12': 'options', 'ribbon': 'options', 'ribbon-earn': 'options', 'opyn-gamma': 'options', 'opyn-convexity': 'options',
    'panoptic-v2': 'options', 'thetanuts-finance': 'options', 'theo-straddle-vaults': 'options',
    'manta-cedefi': 'basis', 'liminal-basis': 'basis', 'desyn-basis-trading': 'basis',
    'spark-savings': 'lending',            # spETH: WETH lent into SparkLend
    'moonwell-vaults': 'lending', 'ultrayield-vaults': 'lending', 'yearn-finance': 'farming', 'harvest-finance': 'farming',
    'fx-protocol': 'cdp', 'frankencoin': 'cdp', 'reflexer': 'cdp', 'abracadabra-spell': 'cdp', 'inverse-finance-firm': 'cdp',
    'qidao': 'cdp', 'lista-cdp': 'cdp', 'alchemix-v3': 'farming',
    'enzyme-finance': 'farming', 'set-protocol': 'farming', 'arbitrove': 'farming', 'fyde-protocol': 'farming',
    'eigencloud': 'restaking', 'symbiotic': 'restaking',
    'across': 'farming', 'jupiter-perpetual-exchange': 'farming', 'gmx-v2-perps': 'farming',
    'stakestone-stone': 'staking', 'stakestone-berachain-vault': 'farming', 'infrared-finance': 'staking',
}

# farming-and-pools kinds (BTC map: points farming, strategy vaults, liquidity pools)
POINTS = '''swell-l2-farm zircuit-staking hemi-staking katana-pre-launch blast-pre-launch-farm terminal-finance-pre-deposits corn-kernels
sophon-farm cytonic-airdrop-campaign turtle-club mitosis blackwing gain stakestone-berachain-vault'''.split()
POOLS = '''curve-dex fluid-dex aerodrome-v1 aerodrome-slipstream velodrome-v2 velodrome-v3 uniswap-v2 sushiswap-v3 pancakeswap-amm balancer-v3
balancer-v1 camelot-v2 camelot-v3 syncswap thorchain-dex ekubo hydration-dex katana-dex merchant-moe-liquidity-book quickswap-dex
quickswap-v3 bancor-v3 bancor-v2.1 shibaswap-v1 bulbaswap-v3 kodiak-v3 angstrom fluxion-network swaap-maker-v2 dodo-amm agni-finance
up-v3 hydrex-integral fermiswap pharaoh-v3 ramses-cl-v2 vvs-standard fables chainflip-amm bisonfi frax-swap biswap-v2 joe-dex
pulsex-v1 aquarius-stellar stellar-dex origin-arm across jupiter-perpetual-exchange gmx-v2-perps'''.split()
KIND = {**{s: 'points' for s in POINTS}, **{s: 'pools' for s in POOLS}}


def kind_default(cat):
    return 'vaults' if cat == 'farming' else None


NAMES = {'veda': 'Veda: other ETH vaults', 'mellow-core': 'Mellow Core vaults (other than Lido Earn)', 'lagoon': 'Lagoon vaults (other)',
         'concrete': 'Concrete: other ETH vaults', 'vesper': 'Vesper pools (other than vaETH)', 'upshift': 'Upshift ETH vaults',
         'ether.fi-liquid': 'ether.fi Liquid (other ETH vaults)', 'eigencloud': 'EigenLayer: direct restaking',
         'symbiotic': 'Symbiotic: direct restaking'}

# DEX projects without a token breakdown: ETH side of each ETH pool over $1M from DefiLlama's yields list
POOL_PROJECTS = {'uniswap-v3': ('Uniswap v3 ETH pools', 'pools'), 'uniswap-v4': ('Uniswap v4 ETH pools', 'pools'),
                 'sushiswap': ('SushiSwap v2 ETH pools', 'pools'), 'balancer-v2': ('Balancer v2 ETH pools', 'pools'),
                 'pancakeswap-amm-v3': ('PancakeSwap v3 ETH pools', 'pools'), 'aerodrome-slipstream-2': ('Aerodrome Slipstream 2 ETH pools', 'pools')}
_PLAIN = {'ETH', 'WETH', 'WETH.E'}


def pool_eth_share(parts):
    """ETH side counted here: plain ETH/WETH legs only, an equal share per leg. The staking-token side of an ETH/LST
    pool stays with its issuer, as in the BTC map (only the part not counted elsewhere is added)."""
    if not parts:
        return 0.0
    return sum(1 for p in parts if p in _PLAIN) / len(parts)


# ---- staking-token issuers -------------------------------------------------------------------------------------------
ISSUER_SLUGS = set('''lido rocket-pool coinbase-wrapped-staked-eth binance-staked-eth ether.fi-stake renzo kelp puffer-stake stakewise-v3
meth-protocol mantle-restaking swell-liquid-staking swell-liquid-restaking frax-ether stader ankr origin-ether bedrock-unieth
liquid-collective dinero-(pxeth)'''.split())
# restaking-token issuers: their ETH sits in EigenLayer (or Symbiotic); they also hold staking tokens of other issuers
LRT_ISSUERS = set('''ether.fi-stake kelp renzo puffer-stake swell-liquid-restaking bedrock-unieth eigenpie inceptionlrt-(isolated-restaking)
yieldnest king-protocol euclid-finance'''.split())
# platform -> rows whose ETH already sits in it ('LRT' = all restaking-token issuers)
RESTAKING_PLATFORMS = {'eigencloud': 'LRT', 'symbiotic': ['mellow-restaking', 'mantle-restaking']}
# Cap's weETH (8,350 at T) is restaked through a Symbiotic vault: count it once, in Cap
SYMBIOTIC_ALSO = {'cap': 8349.99 / 22666.22}

# ---- on-chain carry books (research/eth/en/CARRY-PRODUCTS.md); issuer mix = which staking token the book holds -------
CARRY = {
    'ether.fi Liquid ETH': dict(id='liquid-eth', name='ether.fi Liquid ETH', category='carry', issuer_mix={'ether.fi-stake': 1.0},
                                replaces={'veda': 1.0}),
    'Lido Earn ETH': dict(id='lido-earn', name='Lido Earn ETH', category='carry', issuer_mix={'lido': 1.0}, replaces={'mellow-core': 1.0}),
    'Avant avETH / savETH': dict(id='avant-aveth', name='Avant avETH / savETH', category='carry', issuer_mix={}, replaces={'avant-aveth': 1.0}),
    'YieldBasis WETH': dict(id='yieldbasis-weth', name='YieldBasis WETH', category='carry', issuer_mix={}, replaces={'yield-basis': 1.0}),
    'Rocksolid rETH': dict(id='rocksolid', name='Rocksolid rETH', category='carry', issuer_mix={'rocket-pool': 1.0},
                           replaces={'lagoon': 1.0}),
    'Liquity ETH Carry': dict(id='liquity-carry', name='Liquity ETH Carry', category='carry', issuer_mix={'lido': 1.0}, replaces={'fusion-by-ipor': 1.0}),
    'Makina DETH': dict(id='makina-deth', name='Makina DETH', category='carry', issuer_mix={'ether.fi-stake': 1.0}, replaces={'makina': 1.0}),
    'Vesper vaETH': dict(id='vesper-vaeth', name='Vesper vaETH', category='carry', issuer_mix={}, replaces={'vesper': 1.0}),
    'Royco ETH': dict(id='royco-eth', name='Royco ETH', category='carry', issuer_mix={'lido': 1.0}, replaces={'royco-v2': 1.0}),
    'TAU InfiniFi ETH Carry': dict(id='tau-infinifi', name='TAU InfiniFi ETH Carry', category='carry', issuer_mix={'coinbase-wrapped-staked-eth': 1.0}, replaces={'fusion-by-ipor': 1.0}),
    'Reservoir ETH Yield': dict(id='reservoir-eth', name='Reservoir ETH Yield', category='carry', issuer_mix={}, replaces={'fusion-by-ipor': 1.0}),
    # Upshift vaults reconstructed on 7 Oct (data/eth/gap_rocksolid_upshift.json); book at the snapshot only
    'NEMO ETH Prime': dict(id='nemo-eth-prime', name='NEMO ETH Prime', category='carry', issuer_mix={'lido': 1.0}, replaces={'upshift': 1.0}, snapshot_eth=3037.666),
    'Sentora ETH': dict(id='sentora-eth', name='Sentora ETH', category='carry', issuer_mix={'ether.fi-stake': 1.0}, replaces={'upshift': 1.0}, snapshot_eth=676.67),
    'ZenSats wstETH': dict(id='zensats', name='ZenSats wstETH', category='carry', issuer_mix={'lido': 1.0}),
}


def _rocksolid_liquity(vals, label):
    """Rocksolid holds Liquity ETH Carry shares: 728.48 ETH at the snapshot (research/eth/en/CARRY-PRODUCTS.md)."""
    return 728.48 if label >= '2026-06' else 0.0


# (holder, row that loses the holding, amount function)
OVERLAPS = [
    ('carry:liquity-carry', 'carry:rocksolid', _rocksolid_liquity),
    ('mantle-restaking', 'veda', lambda vals, label: vals.get('mantle-restaking') or 0.0),   # Veda's adapter counts the cmETH vault
    ('upshift', 'gain', lambda vals, label: vals.get('gain') or 0.0),                       # Kelp Gain vaults run on Upshift; count once
]

# rows that report gross collateral, scaled to depositor equity (product-notes review, at the snapshot)
SCALE = {'origami-finance': 9 / 455, 'index-coop': 110 / 309}
