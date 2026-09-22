"""Product universe: classification + data spec. Edit here, then re-run 10_build.py.

Fields
  id, product, slug, cat (code or {month_from: code} for time-varying), sub, src:
    'dl'      DefiLlama /protocol/{slug}: BTC-symbol part of tokensInUsd (optionally chain filter / incl. '-borrowed')
    'dltotal' DefiLlama total TVL (BTC-only protocol without usable token breakdown)
    'pools'   DefiLlama yields pools (pool ids resolved in 07_fetch_yield_pools.py by product name)
    'fixed'   value supplied from on-chain work / disclosures (current only)
    'core'    Core staking API (current only)
  chains, borrowed, only, excl: DefiLlama filters. hist: 'dl' | 'pools' | 'pending' | 'none'
  net: default include_net (1/0). offchain: 1 for disclosed-AUM rows. memo: 1 = duplicate of another row, excluded from gross/net.
"""
C = 'C'
P = []
def add(**k):
    k.setdefault('src', 'dl'); k.setdefault('hist', 'dl' if k['src'] in ('dl', 'dltotal', 'pools') else 'none')
    k.setdefault('net', 1); k.setdefault('offchain', 0); k.setdefault('memo', 0); k.setdefault('flag', '')
    P.append(k)

# ---------------- C1: BTC collateral + USD loan -> strategy -----------------
add(id='kraken-vault', product='Kraken Bitcoin Vault (Advanced Strategies BTC)', slug='kraken-bitcoin-vault', cat='C1', sub='Curated carry vault (Veda/Sentora)',
    src='fixed', btc=6492.7, hist='pending', source='on-chain (parallel agent; Ink BoringVault) 2026-09-20; DefiLlama slug shows 0 (ignored)',
    just='kBTC collateral on Morpho/Aave -> RLUSD/PYUSD/USDT debt -> Sentora V2 + Hastra PRIME: dollar loan against BTC.')
add(id='yield-basis', product='Yield Basis', slug='yield-basis', cat='C1', sub='Leveraged BTC/crvUSD LP (hybrid)',
    src='fixed', btc=1326.2, hist='pending', source='on-chain depositor equity (LT pricePerShare x supply, all BTC markets v1-v3) 2026-09-20 12:00; history = month-end book value (yieldbasis/tvl_monthly.csv). DefiLlama BTC-token TVL counts the gross LP (incl. borrowed crvUSD side) and is not used',
    just='User BTC + protocol-borrowed crvUSD -> 2x BTC/crvUSD Curve LP; dollar debt under BTC => C1 (hybrid LP, per plan rule).')
add(id='maple-btc-yield', product='Maple BTC Yield', slug='maple', cat='C1', sub='Custodial collateral -> USDC -> Core dual staking',
    src='fixed', btc=0.0, hist='pending', flag='wound down 11-2025: 85% of BTC principal returned, 15% held back until the May-2026 settlement',
    source='on-chain reconstruction (Core CLTV stakes of the Maple cluster + Bitcoin hub payouts); history = max(staked on 1st of next month, mid-month) to smooth maturity rolls; 0 from 2025-11',
    just='BTC at Copper/BitGo as collateral -> USDC -> CORE + hedge -> Core dual staking: dollar loan against BTC. Size unmeasured (blank).')
add(id='bitget-bgbtc-earn', product='Bitget bgBTC Onchain Earn', slug='aera-v3', cat='C1', sub='Curated carry vault (Gauntlet Aera, Morpho on Morph)',
    src='fixed', btc=801.7, hist='pending', source='on-chain (parallel agent): 801.7 bgBTC in Morpho on Morph; = DefiLlama aera-v3 BGBTC 801.6 units',
    just='bgBTC -> USDC loan on Morpho (Morph) -> Gauntlet USDC Prime: dollar loan against BTC.')
add(id='etherfi-liquid-btc', product='ether.fi Liquid BTC', slug='ether.fi-liquid', cat={'2024-09': 'C1', '2025-06': 'C6', '2025-08': 'C1'}, sub='Curated carry vault (Veda, Nonce)',
    src='fixed', btc=231.56, hist='pending', flag='C6 in 2025-06..07: no stablecoin debt, points-only book (Corn, Berachain)',
    source='on-chain: 223.90 shares (Ethereum 133.61 + Optimism 90.28) x accountant rate 1.03425 at 2026-09-20; history = month-end NAV rebuilt from positions (etherfi/tvl_monthly.csv)',
    just='WBTC/cbBTC on Spark -> PYUSD/USDC -> Cap stcUSD + Sentora: dollar loan against BTC. Only the BTC vault of ether.fi Liquid is counted.')
add(id='hermetica-hbtc', product='Hermetica hBTC', slug='hermetica-hbtc', cat='C1', sub='sBTC collateral -> USDh (wound down)',
    src='dltotal', flag='strategy wound down 18.06.2026; deposits closed 24.08.2026',
    just='BTC -> sBTC -> Zest collateral -> USDh -> sUSDh: dollar (USDh) loan against BTC. Historical C1; now ~1% and closing.')
add(id='tesseract', product='Tesseract TESS wBTC debt-loop vaults (IPOR Fusion)', slug='fusion-by-ipor', cat='C1', sub='Institutional carry vaults',
    src='pools', just='WBTC -> USDC loan on Morpho/Aave -> sUSDe/PYUSD/wsrUSD loops: dollar loan against BTC.')
add(id='btcd-carry', product='BTCD Labs / TAU BTC dollar-carry vaults (IPOR Fusion)', slug='fusion-by-ipor', cat='C1', sub='Carry vaults (small)',
    src='pools', just='WBTC collateral -> stablecoin debt -> yield (\"wBTC Dollar Carry\", \"TAU InfiniFi BTC Carry\").')
add(id='acre', product='Acre acreBTC', slug='acre', cat='C1', sub='tBTC -> Midas mRe7 (closed)',
    flag='closed; realized -1.24%', just='BTC -> tBTC -> macreBTC1 / borrow -> mRe7YIELD: historical dollar-carry case (per plan list).')
add(id='avalon-cedefi', product='Avalon CeDeFi (lfBTC pool)', slug='avalon-cedefi', cat='C0', sub='CeDeFi BTC-collateral pool (not a depositor product)', net=0,
    flag='static position since 11-2024; 4 institutional Safes; USDT sent to Binance deposit addresses; DefiLlama notes 100% team-deposited',
    just='Lending pool for four institutional Safes, not a yield product with outside BTC depositors (top-5 check) => C0 context, out of gross/net.')

# ---------------- C2: staking & restaking -----------------
add(id='babylon', product='Babylon (BTC staking)', slug='babylon-protocol', cat='C2', sub='Native BTC staking (self-custodial)',
    just='Timelocked native BTC secures PoS chains; rewards in BABY. ~80% of active stake is Kraken exchange staking (FP data).')
add(id='lombard-lbtc', product='Lombard LBTC', slug='lombard-lbtc', cat={'2024-09': 'C2', '2026-08': 'C4'}, sub='LST -> covered call (Bitwise) from 13.08.2026',
    flag='category switches C2->C4 at 2026-08 (Babylon LST until Aug-2026, then off-chain covered call)',
    just='Babylon LST until Aug-2026; since 13.08.2026 yield = Bitwise off-chain covered-call program => C4 from 2026-08.')
add(id='gtbtc', product='Gate GTBTC', slug='gtbtc', cat='C2', sub='Exchange BTC LST (Babylon)',
    just='Gate stakes the BTC in Babylon (Gate Earn FP 3,455 BTC ~ GTBTC 3,468 BTC).')
add(id='bedrock-unibtc', product='Bedrock uniBTC', slug='bedrock-unibtc', cat='C2', sub='BTC LRT (Babylon, Symbiotic)',
    just='Liquid restaking BTC (Babylon + Symbiotic points/rewards).')
add(id='solvbtc-lsts', product='SolvBTC LSTs (SolvBTC.BBN etc.)', slug='solvbtc-lsts', cat='C2', sub='BTC LST (Babylon/Core)',
    just='SolvBTC staked via Babylon/Core LST wrappers.')
add(id='solv-others', product='Solv Others (M-BTC)', slug='solv-others', cat='C2', sub='BTC LST (small)', just='Solv LST backing on Merlin (small).')
add(id='pumpbtc', product='PumpBTC', slug='pumpbtc', cat='C2', sub='Babylon LRT', just='Babylon liquid restaking token.')
add(id='lorenzo-stbtc', product='Lorenzo stBTC', slug='lorenzo-stbtc', cat='C2', sub='Babylon LST', src='dltotal', just='Babylon LST (now ~0).')
add(id='chakra', product='Chakra', slug='chakra', cat='C2', sub='Babylon LST', src='dltotal', just='Babylon LST (dead).')
add(id='allobtc', product='alloBTC', slug='allobtc', cat='C2', sub='Babylon LST', src='dltotal', just='Babylon LST (dead).')
add(id='pstake-btc', product='pSTAKE BTC', slug='pstake-btc', cat='C2', sub='Babylon LST', src='dltotal', just='Babylon LST (dead).')
add(id='lisa-btc-lst', product='LISA BTC LST', slug='lisa-btc-lst', cat='C2', sub='Babylon LST', src='dltotal', just='Babylon LST (dead).')
add(id='b14g', product='b14g', slug='b14g', cat='C2', sub='Dual staking (Core / Babylon Genesis)', just='Native BTC timelocked for Core/Babylon dual staking; rewards in partner tokens.')
add(id='core-staking', product='Core BTC staking (Satoshi Plus)', slug='-', cat='C2', sub='Native BTC timelock staking',
    src='core', btc=2210.26930986, hist='none', source='Core staking API /staking/summary/overall stakedBTCAmount (read 2026-09-21)',
    flag='current only; may overlap b14g and Maple BTC Yield (unmeasured)', just='Non-custodial timelocked BTC delegated to Core validators; rewards in CORE.')
add(id='starknet-btc-staking', product='Starknet BTC Staking', slug='starknet-btc-staking', cat='C2', sub='BTC staking on L2', just='WBTC/SolvBTC/tBTC staked for Starknet consensus; rewards in STRK.')
add(id='endur', product='Endur (Starknet BTC LSTs)', slug='endur', cat='C2', sub='LST on Starknet BTC staking', net=0,
    just='BTC LSTs that delegate into Starknet BTC staking: presumed nested in the Starknet BTC Staking row.')
add(id='exsat-staking-btc', product='exSat Staking BTC', slug='exsat-staking-btc', cat='C2', sub='BTC staking (docking layer)', just='BTC staked to exSat (XSAT rewards); XBTC-style receipt.')
add(id='symbiotic', product='Symbiotic (BTC vaults)', slug='symbiotic', cat='C2', sub='Restaking collateral', just='BTC collateral (uniBTC, LBTC, SolvBTC) restaked in Symbiotic vaults.')
add(id='mellow-restaking', product='Mellow restaking (uniBTC)', slug='mellow-restaking', cat='C2', sub='Restaking vault', just='uniBTC restaking vault.')
add(id='eigencloud', product='EigenLayer / EigenCloud (BTC part)', slug='eigencloud', cat='C2', sub='Restaking', just='tBTC/WBTC/LBTC restaked.')
add(id='pell-network', product='Pell Network', slug='pell-network', cat='C2', sub='BTC restaking', just='Omnichain BTC restaking.')
add(id='kernel', product='Kernel (BTC part)', slug='kernel', cat='C2', sub='BTC restaking (BNB)', just='BTC restaking on BSC.')
add(id='satlayer', product='SatLayer', slug='satlayer', cat='C2', sub='BTC restaking (BVS)', just='BTC restaking for Bitcoin Validated Services.')
add(id='cian-yield-layer', product='CIAN Yield Layer (BTC vaults)', slug='cian-yield-layer', cat='C2', sub='BTC LST yield layer',
    just='Locked FBTC / pumpBTC vaults deploying into BTC staking/restaking yield.')
add(id='etherfi-ebtc', product='ether.fi eBTC', slug='ether.fi-stake', cat='C2', sub='BTC restaking vault', src='pools', net=0,
    flag='gross only: eBTC is a Veda BoringVault, presumed inside the Veda (other BTC vaults) balance; yields-pool history starts 2026-01',
    just='eBTC (Veda vault) restakes LBTC/WBTC/cbBTC (Karak/Symbiotic/EigenLayer).')
add(id='fragmetric', product='Fragmetric (zBTC)', slug='fragmetric', cat='C2', sub='Restaking (Solana)', just='fragBTC restaking.')
add(id='obeliskbtc', product='ObeliskBTC', slug='obeliskbtc', cat='C2', sub='BTC restaking/asset mgmt', flag='mechanism not verified',
    just='\"Bitcoin asset management through restaking\" (DefiLlama description).')
add(id='vishwa', product='Vishwa', slug='vishwa', cat='C2', sub='Anchor BTC (mechanism undisclosed)', flag='yield mechanism not verified; placed in C2 by DefiLlama Anchor-BTC grouping',
    just='DefiLlama Anchor BTC; native BTC on Bitcoin; yield source not disclosed.')

# ---------------- C3: basis & delta-neutral -----------------
add(id='solv-basis-trading', product='Solv Basis Trading (SolvBTC.TRADING)', slug='solv-basis-trading', cat='C3', sub='CEX basis fund', just='SolvBTC deployed into CEX basis trading.')
add(id='bitfi-basis', product='BitFi bfBTC (EVM chains)', slug='bitfi-basis', cat='C3', sub='CeDeFi basis', flag='bfBTC mechanism = BitFi CeDeFi (basis/staking), not verified',
    just='bfBTC supply on BSC/Ethereum/Base/Pharos; BitFi CeDeFi strategies (basis).')
add(id='bitfi-btc', product='BitFi bfBTC (AILayer)', slug='bitfi-btc', cat='C3', sub='CeDeFi basis', flag='same token as BitFi Basis, different chain',
    just='bfBTC on AILayer; same BitFi CeDeFi product.')
add(id='syntetika', product='Syntetika hBTC (Hilbert BTC Basis+)', slug='syntetika', cat='C3', sub='Basis+ fund token (on-chain, Base)',
    just='cbBTC -> hBTC: basis + curve arb + short options, NAV fund (Hilbert Capital).')
add(id='midas-mhyperbtc', product='Midas mHyperBTC (Hyperithm)', slug='midas-rwa', cat='C1', sub='NAV token: cbBTC collateral -> USDT/USDS loan -> Hyperithm USD strategies',
    src='fixed', btc=354.12, hist='pending', source='Midas oracle NAV 1.02606813 x supply 345.12 (Ethereum 284.07, Monad 57.07, Rootstock 3.98), 2026-09-21; history = month-end supply x NAV (mhyperbtc/tvl_monthly.csv)',
    just='Strategy wallet posts cbBTC on Morpho/Spark, borrows USDT/USDS and deploys the dollars (Midas transparency API) => C1 (was C3).')
add(id='midas-mre7btc', product='Midas mRe7BTC (Re7)', slug='midas-rwa', cat='C3', sub='Market-neutral NAV token', src='pools',
    just='BTC-denominated market-neutral strategies (Re7).')
add(id='midas-mbtc', product='Midas mBTC', slug='midas-rwa', cat='C3', sub='NAV token (dormant)', src='pools', just='NAV token, dormant since 10-2025.')
add(id='liminal-basis', product='Liminal Basis (BTC)', slug='liminal-basis', cat='C3', sub='Basis on Hyperliquid', just='Delta-neutral basis on Hyperliquid.')
add(id='manta-cedefi', product='Manta CeDeFi (BTC)', slug='manta-cedefi', cat='C3', sub='CeDeFi basis', just='CeDeFi delta-neutral.')
add(id='hope-collateral', product='Hope (BTC basis collateral)', slug='hope-collateral', cat='C3', sub='Basis', just='DefiLlama Basis Trading; BTC collateral.')
add(id='desyn-basis-trading', product='DeSyn Basis Trading (BTC)', slug='desyn-basis-trading', cat='C3', sub='Basis', just='Basis trading fund, WBTC part.')
add(id='bouncebit', product='BounceBit (BTC part)', slug='bouncebit', cat='C3', sub='CeDeFi basis (BBTC)', just='BTC restaked on BounceBit chain + CeFi basis via CEFFU.')

# ---------------- C4: options -----------------
add(id='rysk-v12', product='Rysk V12 (BTC part)', slug='rysk-v12', cat='C4', sub='On-chain covered calls / CSPs', just='WBTC/UBTC underwrite covered calls.')
add(id='hegic', product='Hegic (WBTC pool)', slug='hegic', cat='C4', sub='Option writing pool', just='Peer-to-pool option writing with WBTC.')
add(id='ribbon', product='Ribbon (WBTC theta vault)', slug='ribbon', cat='C4', sub='DOV (legacy)', just='WBTC covered-call theta vault.')
add(id='d2-finance', product='D2 Finance (UBTC)', slug='d2-finance', cat='C4', sub='Derivatives strategy vault', flag='strategy mix not verified', just='Options/derivatives yield vault.')

# ---------------- C5: credit -----------------
add(id='lombard-vaults', product='Lombard Vaults (LBTCv / BTCe)', slug='lombard-vaults', cat={'2024-09': 'C6', '2026-07': 'C5'}, sub='Sentora-managed vault; BTCe credit leg (Cap/Symbiotic) from 07-2026',
    flag='C6 (DeFi money-market/points vault) until 2026-06; C5 from 2026-07 (first-loss cover for Flow Traders loan on Cap)',
    just='BTCe credit leg: LBTC delegated via Symbiotic as slashable cover for an institutional loan => C5 (plan). Earlier LBTCv = DeFi/points vault.')
add(id='accountable', product='Accountable YieldApp (cbBTC/wcBTC)', slug='accountable', cat='C5', sub='Uncollateralized credit vaults', borrowed=True,
    just='cbBTC lent to verified borrowers (Monad/Citrea); DefiLlama books it as borrowed, so borrowed + idle are counted.')
add(id='native-credit-pool', product='Native Credit Pool (BTC part)', slug='native-credit-pool', cat='C5', sub='Credit to market makers', just='BTC lent to Native PMM market makers.')
add(id='solv-rwa', product='Solv RWA (SolvBTC)', slug='solv-rwa', cat='C5', sub='RWA/credit', flag='constant value in DefiLlama; mechanism not verified', just='SolvBTC allocated to RWA/credit strategies.')
add(id='two-prime-axiom', product='Two Prime Axiom WBTC Vault (Pareto)', slug='pareto-credit', cat='C5', sub='Institutional BTC lending', src='fixed', btc=150.0, offchain=1,
    source='dossier: 150 WBTC first-loss (vault TVL $12.1M), live since 16.09.2026; on-chain Pareto vault not tracked by DefiLlama',
    just='WBTC lent to institutions; sole borrower on Pareto is Two Prime itself.')
add(id='xapo-byzantine', product='Hilbert Xapo Byzantine BTC Credit Fund', slug='-', cat='C5', sub='Off-chain BTC credit fund', src='fixed', btc=round(100e6 / 81178.0, 1), offchain=1,
    flag='ESTIMATE: $100M phase-1 allocation used (=1,231.9 BTC); range up to 3,000 BTC (2024 seed)',
    source='disclosed: $100M phase-1 allocations; 3,000 BTC seed (2024); fund page (launch 15.09.2024, net 2.94%) gives no AUM',
    just='Short BTC loans to tier-1 institutions, no leverage, no DeFi.')

# ---------------- C6: LP, emissions, farming, DeFi vaults -----------------
add(id='mezo-earn', product='Mezo Earn (veBTC)', slug='mezo-earn', cat='C6', sub='Vote-escrow BTC (emissions/fees)', just='BTC locked as veBTC; MUSD-denominated voting APR.')
add(id='buzz-farming', product='B2 Buzz Farming', slug='buzz-farming', cat='C6', sub='L2 points/emissions farm', just='BTC on B2 farming B2 points/partner rewards.')
add(id='ailayer-farm', product='AILayer farm (AINN)', slug='ailayer-farm', cat='C6', sub='L2 points farm', net=0,
    flag='presumed same BTC as BitFi bfBTC on AILayer (84.6 vs 82.6 $M, co-moving)', just='BTC staked to AINN L2 for points.')
add(id='zest-v2', product='Zest v2 (sBTC supply)', slug='zest-v2', cat='C6', sub='Incentivised supply (Stacks)', only={'SBTC'}, borrowed=True,
    flag='STBTC ($10.9M) excluded: yields API lists it as stSTXbtc (STX LST), DefiLlama prices it as BTC',
    just='sBTC supply earning mostly incentive-driven APY (plan: Zest supply in C6). Supplied = idle + borrowed.')
add(id='solv-strategies', product='Solv Strategies', slug='solv-strategies', cat='C6', sub='DeFi strategy vaults', just='SolvBTC in LP/farming strategies.')
add(id='concrete', product='Concrete (BTC vaults)', slug='concrete', cat='C6', sub='DeFi strategy vaults',
    flag='yields API also lists Berachain BTC vaults ($38M, APY 0) that are not in the protocol TVL (not counted)', just='WBTC vaults (points/PoL).')
add(id='veda-other', product='Veda (other BTC vaults, excl. Kraken)', slug='veda', cat='C6', sub='DeFi strategy vaults (unidentified)', excl_chain_sym={('Ink', 'KBTC')},
    minus_ids=['etherfi-liquid-btc'],
    flag='vaults not identified (mostly Ethereum WBTC, 1,449 BTC); ether.fi Liquid BTC (a Veda vault, counted in C1) subtracted each month: DefiLlama Veda Optimism WBTC 93.3 = liquidBTC Optimism shares', just='Veda BoringVault BTC balances outside the Kraken vault.')
add(id='upshift', product='Upshift (BTC vaults)', slug='upshift', cat='C6', sub='DeFi strategy vaults', just='BTC vaults (August/Sentora/Hyperbeat).')
add(id='hyperbeat-earn', product='Hyperbeat Earn (hbBTC)', slug='hyperbeat-earn', cat='C6', sub='DeFi strategy vault', net=0, just='hbBTC UBTC vault; same balance as Upshift UBTC (nested).')
add(id='proxy', product='Proxy (PRXY BTC strategies)', slug='proxy', cat='C6', sub='Token-incentive (3,3)', just='WBTC in \"Bitcoin Yield Strategies\" with PRXY emissions.')
for s, n in [('convex-finance', 'Convex (BTC LPs)'), ('beefy', 'Beefy (BTC vaults)'), ('yearn-finance', 'Yearn (BTC vaults)'), ('badger-dao', 'Badger DAO (BTC vaults)'),
             ('stake-dao-yield', 'Stake DAO (BTC LPs)'), ('yield-yak-aggregator', 'Yield Yak (BTC)'), ('yo-protocol', 'YO Protocol (yoBTC)'), ('superform', 'Superform (BTC)'),
             ('harvest-finance', 'Harvest (BTC)'), ('autofarm', 'Autofarm (BTC)'), ('t3tris-finance', 't3tris (WBTC)'), ('omniyield', 'OmniYield (WBTC)'),
             ('belt-finance', 'Belt (BTCB)'), ('tranchess-yield', 'Tranchess (BTCB)'), ('radpie', 'Radpie (BTC)'), ('aura', 'Aura (BTC)'), ('lagoon', 'Lagoon (BTC vaults)'),
             ('mellow-core', 'Mellow Core (BTC vaults)'), ('ember-protocol', 'Ember (BTC vaults)'), ('avant-avbtc', 'Avant avBTC'), ('moonwell-vaults', 'Moonwell vaults (cbBTC)'),
             ('ultrayield-vaults', 'UltraYield vaults (cbBTC)'), ('volo-vault', 'Volo vault (xBTC)'), ('katana-pre-launch', 'Katana pre-launch (WBTC)'), ('troves', 'Troves (BTC)'),
             ('yieldfi', 'YieldFi (yBTC)'), ('rujira-amm-strategies', 'Rujira strategies (BTC)'), ('reaper-farm', 'Reaper (WBTC)'), ('vesper', 'Vesper (WBTC)'),
             ('kine-finance', 'Kine (BTC)'), ('deltaprime', 'DeltaPrime (BTC)'), ('extra-finance-leverage-farming', 'Extra Finance (cbBTC)')]:
    add(id=s, product=n, slug=s, cat='C6', sub='Yield aggregator / DeFi vault', just='BTC deposits in aggregator/strategy vaults (LP fees, emissions, lending).')
add(id='fusion-by-ipor-other', product='IPOR Fusion (other BTC vaults)', slug='fusion-by-ipor', cat='C6', sub='Yield aggregator / DeFi vault', minus_pools=['tesseract', 'btcd-carry'],
    just='IPOR Fusion BTC vaults other than the Tesseract/BTCD carry vaults.')

# ---------------- C0 context (not in gross/net) -----------------
for s, n in [('gauntlet', 'Gauntlet'), ('sentora-curator', 'Sentora (WBTC vault)'), ('k3-capital', 'K3 Capital'), ('tulipa-capital', 'Tulipa Capital'), ('9summits', '9Summits'),
             ('telos-consilium', 'Telos Consilium'), ('yearn-curating', 'Yearn curating'), ('gami-labs', 'Gami Labs'), ('anthias-labs', 'Anthias'), ('block-analitica', 'Block Analitica'),
             ('alphagrowth', 'AlphaGrowth'), ('clearstar', 'Clearstar'), ('ultrayield-curator', 'UltraYield curator'), ('damm-capital', 'DAMM'), ('odyssey-digital-am', 'Odyssey'),
             ('hyperithm', 'Hyperithm (curated cbBTC vaults)'), ('steakhouse-financial', 'Steakhouse'), ('re7-labs', 'Re7 Labs'), ('mev-capital', 'MEV Capital')]:
    add(id='cur-' + s, product=f'Curator BTC vaults: {n}', slug=s, cat='C0', sub='Curated BTC lending vaults (~0%)', net=0,
        excl=({'KBTC'} if s == 'sentora-curator' else set()) | ({'MHYPERBTC'} if s == 'hyperithm' else set()),
        just='BTC-denominated lending vaults (Morpho/Euler): ~0% base; plan puts them in C0 context.')
for s, n in [('crvusd', 'crvUSD / LlamaLend'), ('fx-protocol', 'f(x) Protocol'), ('frankencoin', 'Frankencoin'), ('sky-lending', 'Sky (Maker)'), ('moneyonchain', 'Money on Chain'),
             ('sovryn-zero', 'Sovryn Zero'), ('bima-cdp', 'BIMA CDP'), ('btcfi-cdp', 'BTCFi CDP'), ('kava-mint', 'Kava Mint'), ('bucket-cdp', 'Bucket'), ('mezo-borrow', 'Mezo Borrow'),
             ('hylo-protocol', 'Hylo'), ('yala', 'Yala'), ('threshold-thusd', 'Threshold thUSD'), ('lista-cdp', 'Lista CDP'), ('felix-cdp', 'Felix CDP'), ('abracadabra-spell', 'Abracadabra'),
             ('river-omni-cdp', 'River Omni-CDP (satUSD)')]:
    add(id='cdp-' + s, product=f'CDP collateral: {n}', slug=s, cat='C0', sub='BTC collateral for stablecoin debt', net=0,
        just=('Borrowing venue: bfBTC/uniBTC/UBTC collateral mints satUSD; the BTC holder earns no BTC yield from River (only the LST\'s own), '
              'so it is collateral context; counting it would double count bfBTC/uniBTC.') if s == 'river-omni-cdp' else 'BTC is collateral for a stablecoin/leverage loan: earns ~0% (C0).')
for s, n in [('templar-protocol', 'Templar'), ('granite', 'Granite'), ('surge-credit', 'Surge Credit'), ('liquidium', 'Liquidium'), ('chainflip-lending', 'Chainflip Lending'),
             ('vesu', 'Vesu'), ('echo-lending', 'Echo Lending'), ('zest-v1', 'Zest v1')]:
    add(id='mm-' + s, product=f'Lending venue: {n}', slug=s, cat='C0', sub='BTC-collateral lending venue', net=0, just='BTC used as collateral in a lending venue (C0).')

# ---------------- excluded (listed for transparency; not in gross/net) -----------------
for s, n, why in [('kraken-bitcoin', 'Kraken kBTC', 'bare wrapper'), ('unit', 'Unit UBTC', 'bare wrapper/bridge'), ('lorenzo-enzobtc', 'Lorenzo enzoBTC', 'bare wrapper'),
                  ('bitget-bgbtc', 'Bitget bgBTC', 'bare wrapper (Earn counted separately)'), ('stacks-sbtc', 'Stacks sBTC', 'bare wrapper; Dual Stacking enrollment not measurable'),
                  ('merlins-seal', "Merlin's Seal (M-BTC)", 'Merlin chain bridge custody; MERL points campaign ended 2024'),
                  ('bitlayer-ybtc-family', 'Bitlayer YBTC', 'bridge (\"Bridge between Bitcoin and Bitlayer\")'), ('vault-bridge', 'Katana Vault Bridge (WBTC)', 'bridge'),
                  ('pendle-v2', 'Pendle (BTC PT/YT)', 'yield-tokenization venue: BTC is the underlying LSTs already counted'),
                  ('chainflip-amm', 'Chainflip AMM (native BTC)', 'DEX LP (Dexs are out of scope)'), ('stackingdao', 'StackingDAO (sBTC)', 'STX liquid staking; sBTC is reward inventory'),
                  ('btcst', 'BTCST', 'hashrate token, not BTC yield'), ('ybtc.b', 'YBTC.B', 'bridge'), ('ethena-usde', 'Ethena USDe', 'USD-denominated yield (BTC is collateral for a dollar product)'),
                  ('falcon-finance', 'Falcon Finance', 'USD-denominated yield')]:
    add(id='x-' + s, product=n, slug=s, cat='EXCL', sub=why, net=0, just='Excluded: ' + why)

# ---------------- historical / now-dead products found by the history screen (raw/history_screen.json) -----------------
HIST_FLAG = 'historical: ~0 today'
for s, n, c, sub, just in [
    ('desyn-liquid-strategy', 'DeSyn Liquid Strategy (BTC)', 'C6', 'BTCFi points/liquidity pools', 'BTC pools on BTC L2s earning points/emissions; abrupt drop to 0 in 2025-11 (DefiLlama delisting/methodology).'),
    ('desyn-safe', 'DeSyn Safe (BTC)', 'C6', 'Points farm', 'BTC/bfBTC farm (points).'),
    ('corn-kernels', 'Corn Kernels pre-deposit', 'C6', 'L2 points farm', 'BTC/LST pre-deposits for Corn airdrop points.'),
    ('hemi-staking', 'Hemi staking', 'C6', 'L2 points farm', 'BTC assets staked for Hemi points/rewards.'),
    ('zircuit-staking', 'Zircuit staking (BTC)', 'C6', 'L2 points farm', 'BTC staked for Zircuit points.'),
    ('pencils-protocol', 'Pencils Protocol (SolvBTC)', 'C6', 'Points farm', 'SolvBTC farm on Scroll (points).'),
    ('turtle-club', 'Turtle Club (BTC campaigns)', 'C6', 'Liquidity campaigns', 'cbBTC/FBTC liquidity-distribution campaigns.'),
    ('swell-earn', 'Swell Earn (BTC vaults)', 'C6', 'DeFi strategy vaults', 'BTC vaults (UBTC, stBTC).'),
    ('coinwind', 'CoinWind (BTC)', 'C6', 'CeDeFi mining', 'BTCB/WBTC single-asset mining.'),
    ('flamincome', 'Flamincome (WBTC)', 'C6', 'Yield aggregator', 'WBTC aggregator vault.'),
    ('trevee-earn', 'Trevee / Rings earn (BTC)', 'C6', 'DeFi strategy vaults', 'eBTC/LBTC vaults on Sonic.'),
    ('canopy', 'Canopy (BTC)', 'C6', 'Yield aggregator', 'SolvBTC/LBTC deployment on Movement.'),
    ('cian-curating', 'CIAN curated BTC vaults', 'C6', 'DeFi strategy vaults', 'LST/bfBTC strategy vaults (not plain lending).'),
    ('hourglass', 'Hourglass (eBTC/LBTCv)', 'C6', 'Points time-boost', 'Restaking points boosting of eBTC/LBTCv.'),
    ('echo-strategy', 'Echo strategies (aBTC)', 'C6', 'DeFi strategy vaults', 'aBTC strategies on Aptos.'),
    ('aera-v2', 'Aera v2 (BTC)', 'C6', 'DeFi strategy vaults', 'BTC vaults.'),
    ('seamless-vaults', 'Seamless vaults (cbBTC)', 'C6', 'DeFi strategy vaults', 'cbBTC vaults.'),
    ('amber-finance', 'Amber Finance (BTC)', 'C6', 'Points farm', 'BTC farm.'),
    ('terminal-finance-pre-deposits', 'Terminal pre-deposits (BTC)', 'C6', 'Pre-deposit campaign', 'BTC pre-deposits (points).'),
    ('stakestone-berachain-vault', 'StakeStone Berachain vault (BTC)', 'C6', 'Pre-deposit campaign', 'BTC Boyco-style vault.'),
    ('mitosis', 'Mitosis (BTC)', 'C6', 'Pre-deposit campaign', 'BTC deposits for points.'),
    ('goldilocks', 'Goldilocks (BTC)', 'C6', 'DeFi vault', 'BTC vault.'),
    ('umami-finance', 'Umami (BTC)', 'C6', 'DeFi vault', 'GM BTC vault.'),
    ('bucket-farm', 'Bucket farm (BTC)', 'C6', 'Farm', 'BTC farm.'),
    ('capy-finance', 'Capy (BTC)', 'C6', 'Farm', 'BTC farm.'),
    ('sommelier', 'Sommelier (BTC)', 'C6', 'DeFi vault', 'BTC vault.'),
    ('factor-leverage-vault', 'Factor leverage vault (BTC)', 'C6', 'DeFi vault', 'BTC leverage vault.'),
    ('omega', 'Omega (BTC)', 'C6', 'DeFi vault', 'BTC vault.'),
    ('opengdp-shared-security', 'OpenGDP shared security (LBTC)', 'C2', 'Restaking', 'LBTC/BTC restaking.'),
    ('ibtc-finance', 'iBTC Finance', 'C2', 'BTC LST', 'Liquid staked BTC.'),
    ('swell-btc-lrt', 'Swell swBTC', 'C2', 'BTC LRT', 'BTC liquid restaking token.'),
    ('stonebtc', 'StakeStone STONEBTC', 'C2', 'BTC LST', 'Yield-bearing BTC (LBTC based).'),
    ('shardingdao', 'ShardingDAO (BTC)', 'C2', 'Staking pool', 'BTC staking pool.'),
    ('stream-finance', 'Stream Finance (BTC)', 'C3', 'Delta-neutral (collapsed 11-2025)', 'Market-making / delta-neutral strategies.'),
    ('aster-asbtc', 'Aster asBTC', 'C3', 'CeDeFi trading yield', 'asBTC accrues from exchange trading strategies.'),
    ('thetanuts-finance', 'Thetanuts (BTC)', 'C4', 'Options vaults', 'BTC option-selling vaults.'),
    ('wildcat-protocol', 'Wildcat (BTC)', 'C5', 'Uncollateralized credit', 'BTC lent to named borrowers.')]:
    add(id=s, product=n, slug=s, cat=c, sub=sub, just=just, flag=HIST_FLAG)
for s, n in [('avalon-usda', 'Avalon USDa CDP'), ('beraborrow', 'Beraborrow'), ('bitzap-yusd', 'Bitzap yUSD'), ('bitsmiley', 'bitSmiley'), ('bitu-protocol', 'BitU'),
             ('nerite', 'Nerite'), ('bucket-protocol-v2', 'Bucket v2'), ('inverse-finance-firm', 'Inverse FiRM'), ('angle', 'Angle')]:
    add(id='cdp-' + s, product=f'CDP collateral: {n}', slug=s, cat='C0', sub='BTC collateral for stablecoin debt', net=0, just='BTC is collateral for a stablecoin loan: earns ~0% (C0).')
for s, n in [('euler-dao', 'Euler DAO'), ('b.protocol-curator', 'B.Protocol'), ('apostro', 'Apostro'), ('tau-labs', 'Tau Labs')]:
    add(id='cur-' + s, product=f'Curator BTC vaults: {n}', slug=s, cat='C0', sub='Curated BTC lending vaults (~0%)', net=0, just='BTC lending vaults (C0).')
for s, n, why in [('spectra-v2', 'Spectra (BTC PT/YT)', 'yield-tokenization venue'), ('ratex-dex', 'RateX', 'yield-trading venue'), ('nemo-vault', 'Nemo', 'yield-tokenization venue'),
                  ('wbtc', 'WBTC', 'bare wrapper'), ('coinbase-bridge', 'cbBTC', 'bare wrapper'), ('binance-bitcoin', 'BTCB', 'bare wrapper'), ('solvbtc', 'SolvBTC (base)', 'bare wrapper'),
                  ('function-fbtc', 'FBTC', 'bare wrapper'), ('tbtc', 'tBTC', 'bare wrapper'), ('lombard-btc.b', 'BTC.b', 'bare wrapper'), ('nexus-btc', 'Nexus BTC', 'bare wrapper'),
                  ('okx-xbtc', 'OKX xBTC', 'bare wrapper'), ('circle-bitcoin', 'Circle cirBTC', 'bare wrapper'), ('core-bitcoin-bridge', 'Core BTC bridge', 'bridge'),
                  ('echo-bridge', 'Echo bridge', 'bridge'), ('mezo-bridge', 'Mezo bridge', 'bridge'), ('exsat-bridge', 'exSat bridge', 'bridge'), ('bob-bridge', 'BOB bridge', 'bridge')]:
    add(id='x-' + s, product=n, slug=s, cat='EXCL', sub=why, net=0, just='Excluded: ' + why)

# nested / campaign wrappers kept in gross only
add(id='yieldnest', product='YieldNest ynBTCk', slug='yieldnest', cat='C2', sub='BTC restaking (Kernel)', net=0, flag=HIST_FLAG,
    just='BTCB restaked on Kernel via ynBTCk: nested in the Kernel row (net counts Kernel).')
add(id='royco-v1', product='Royco v1 IAM (incl. Boyco pre-deposits)', slug='royco-v1', cat='C6', sub='Incentivised pre-deposit markets', net=0,
    flag=HIST_FLAG + '; excluded from net: campaign wrapper whose deposits are routed into destination vaults (e.g. Concrete/Veda Boyco vaults); DefiLlama zeroed it 2025-05-08',
    just='BTC/LST deposits into incentive campaigns (points/tokens).')
