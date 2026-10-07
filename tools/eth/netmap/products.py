"""Categories, token issuers and classification decisions for the ETH counted-once map.

Rule (as in the BTC map): every product is counted once. A staking token held inside another counted product is taken
out of its issuer's row and counted in the product that holds it. Money markets and CDPs count only plain ETH/WETH that
no product on the map counts; staking tokens posted there as collateral stay with their issuer.
"""

CATEGORIES = [
    dict(id='staking', label='Staking', color='#5b8def', default=True,
         how='ETH staked with validators through a liquid staking token or a staking pool.',
         payer='The Ethereum protocol (issuance), plus priority fees and MEV.'),
    dict(id='restaking', label='Restaking', color='#8a6fe0', default=True,
         how='Staked ETH also secures other services (EigenLayer, Symbiotic) through a liquid restaking token or a direct deposit.',
         payer='Staking income plus service fees and token incentives from the restaking platform, its services and the issuer.'),
    dict(id='loops', label='Leveraged staking', color='#3fae9a', default=True,
         how='Borrow ETH against staked ETH and stake it again, several times over.',
         payer='The gap between the staking yield and the ETH borrow rate, paid by staking; ETH lenders take the borrow rate.'),
    dict(id='carry', label='Carry', color='#e07c49', default=True,
         how='Post ETH as collateral, borrow dollars and put the dollars to work.',
         payer='Dollar borrowers and stablecoin issuers on the parked dollars, minus the dollar borrow rate; often token rewards.'),
    dict(id='fixed_yield', label='Fixed yield', color='#d4a23c', default=True,
         how='A staked-ETH token split into principal and yield (Pendle, Spectra); the principal side locks in a rate.',
         payer='Buyers of the yield side, who pay up front for the future staking yield and points.'),
    dict(id='basis', label='Basis', color='#4fa3c7', default=True,
         how='Hold ETH and short ETH perpetuals or futures, paid in ETH.',
         payer='Traders who pay funding to be long.'),
    dict(id='options', label='Options', color='#c75a8a', default=True,
         how='Sell call or put options on ETH and collect the premium.',
         payer='Option buyers.'),
    dict(id='credit', label='Credit', color='#9c6b4e', default=True,
         how='Lend ETH to named borrowers (market makers, funds) or cover their credit risk.',
         payer='The borrowers.'),
    dict(id='farming', label='Farming and pools', color='#6aa84f', default=True,
         how='DEX, perp and bridge pools, managed strategy vaults and points programmes.',
         payer='Traders (fees), borrowers in the venues the vault lends to, and token incentives.'),
    dict(id='lending', label='Money markets', color='#7f8c9a', default=False,
         how='Plain ETH or WETH supplied to a lending market that no product on the map counts.',
         payer='Borrowers of ETH, mostly leveraged stakers. The same ETH is staked again by them, so it is off by default.'),
    dict(id='cdp', label='CDP collateral', color='#a0a8b3', default=False,
         how='ETH posted to mint a stablecoin (Sky, Liquity, crvUSD).',
         payer='Nobody: the collateral itself earns nothing.'),
]

# staking-token symbol -> issuer slug (DefiLlama)
ISSUERS = {
    'STETH': 'lido', 'WSTETH': 'lido', 'WSTETH.E': 'lido',
    'RETH': 'rocket-pool', 'CBETH': 'coinbase-wrapped-staked-eth', 'WBETH': 'binance-staked-eth', 'BETH': 'binance-staked-eth',
    'WEETH': 'ether.fi-stake', 'EETH': 'ether.fi-stake', 'WEETH.E': 'ether.fi-stake',
    'EZETH': 'renzo', 'PZETH': 'renzo', 'RSETH': 'kelp', 'WRSETH': 'kelp', 'RSETH.E': 'kelp', 'WRSETH.E': 'kelp',
    'PUFETH': 'puffer-stake', 'OSETH': 'stakewise-v3', 'METH': 'meth-protocol', 'CMETH': 'mantle-restaking',
    'SWETH': 'swell-liquid-staking', 'RSWETH': 'swell-liquid-restaking', 'SFRXETH': 'frax-ether', 'FRXETH': 'frax-ether',
    'ETHX': 'stader', 'ANKRETH': 'ankr', 'OETH': 'origin-ether', 'WOETH': 'origin-ether', 'SUPEROETHB': 'origin-ether',
    'UNIETH': 'bedrock-unieth', 'STONE': 'stakestone-stone', 'TETH': 'treehouse-protocol', 'LSETH': 'liquid-collective', 'PXETH': 'dinero-(pxeth)', 'APXETH': 'dinero-(pxeth)',
}

# DefiLlama category -> map category (default rule; overridden per slug below)
BY_DL_CATEGORY = {
    'Liquid Staking': 'staking', 'Staking Pool': 'staking',
    'Liquid Restaking': 'restaking', 'Restaking': 'restaking',
    'Leveraged Farming': 'loops',
    'Options Vault': 'options', 'Options': 'options',
    'Uncollateralized Lending': 'credit', 'Basis Trading': 'basis', 'Insurance': None, 'Collateral Management': 'restaking',
    'DOR': 'loops', 'Dual-Token Stablecoin': 'cdp', 'CeDeFi': 'farming',
    'Yield': 'farming', 'Yield Aggregator': 'farming', 'Onchain Capital Allocator': 'farming', 'Farm': 'farming',
    'Liquidity Manager': 'farming', 'Dexs': 'farming', 'Derivatives': 'farming', 'Indexes': 'farming',
    'Risk Curators': 'lending', 'Lending': 'lending', 'CDP': 'cdp',
}
