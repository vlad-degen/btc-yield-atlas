"""Categories, token issuers and classification decisions for the ETH counted-once map.

Rule (as in the BTC map): every product is counted once. A staking token held inside another counted product, or posted in a
lending market, is taken out of its issuer's row and counted where it is used. Lending markets split into leveraged staking
(staking tokens and ETH against borrowed ETH), the carry products' own positions and money markets (everything else, off by
default); lent-out WETH is not added. CDPs count only plain ETH; staking tokens posted there stay with their issuer.
"""

CATEGORIES = [
    dict(id='staking', label='Staking', color='#5b8def', default=True,
         how='ETH that is staked and held, and nothing else.',
         payer='Ethereum itself: new issuance, plus fees and MEV.'),
    dict(id='restaking', label='Restaking', color='#8a6fe0', default=True,
         how='Staked ETH that also secures other services through EigenLayer or Symbiotic, and is held.',
         payer='Staking, plus fees and token rewards from the services and the issuer.'),
    dict(id='loops', label='Leveraged staking', color='#3fae9a', default=True,
         how='Stake ETH, borrow ETH against it, stake again. Private wallets and vaults on Aave, Spark and Morpho.',
         payer='Staking yield above the ETH borrow rate; ETH lenders get the borrow rate.'),
    dict(id='carry', label='Carry', color='#e07c49', default=True,
         how='Open products that borrow dollars against ETH and put them to work; only the ETH behind the loans.',
         payer='Whoever pays on the parked dollars, minus the loan rate; often stablecoin rewards.'),
    dict(id='fixed_yield', label='Fixed yield', color='#d4a23c', default=True,
         how='Staked ETH split into principal and yield (Pendle, Spectra); the principal locks in a rate.',
         payer='Buyers of the yield side, betting on future staking yield and points.'),
    dict(id='basis', label='Basis', color='#4fa3c7', default=True,
         how='Hold ETH and short ETH futures for the funding. Ethena is not here: its depositors hold dollars, not ETH, and its ETH leg is small (all crypto basis about $39M in July).',
         payer='Traders who pay funding to be long.'),
    dict(id='options', label='Options', color='#c75a8a', default=True,
         how='Sell call or put options on ETH and collect the premium.',
         payer='Option buyers.'),
    dict(id='credit', label='Credit', color='#9c6b4e', default=True,
         how='Lend ETH to named market makers and funds, or cover their loans (Cap).',
         payer='The borrowers.'),
    dict(id='farming', label='Farming and pools', color='#6aa84f', default=True,
         how='DEX and bridge pools, strategy vaults and points programmes.',
         payer='Trading fees, borrowers and token incentives.'),
    dict(id='lending', label='Money markets', color='#7f8c9a', default=False,
         how='All other ETH and staking tokens in lending markets, mostly collateral for dollar loans. Off by default, as in BTC.',
         payer='Staking yield on staked collateral; plain WETH earns nothing. Who holds it and what the loans fund is unknown.'),
    dict(id='cdp', label='CDP collateral', color='#a0a8b3', default=False,
         how='ETH posted to mint a stablecoin (Sky, Liquity, crvUSD).',
         payer='Nobody for plain ETH; staking tokens keep their staking yield.'),
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
