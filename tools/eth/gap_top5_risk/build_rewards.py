"""Rewards at T for the top-5 dollar legs -> data/eth/gap_top5_rewards.json"""
import json, collections
from glib import *
MC = json.load(open(RAW / 'merkl_campaigns.json')); UB = json.load(open(RAW / 'merkl_user_breakdowns.json')); L = json.load(open(RAW / 'ladder_T_raw.json'))
H = L['holders']['0xf0bb20865277abd641a307ece5ee04e79073416c']
YEAR = 365 * 86400
active = [c_ for c_ in MC['campaigns'] if c_['start'] <= T <= c_['end']]
vault_ta = {'2433802672589613459': L['v2']['senRLUSDv2']['totalAssets'], '16103329905303288034': L['v2']['senPYUSDPRIMEv2']['totalAssets'], '18030207387280065324': json.load(open(RAW / 'extra_raw.json'))['paypalUsdMainV2']['totalAssets']}
liq_claim = {'2433802672589613459': H['senRLUSDv2']['assets'], '16103329905303288034': H['senPYUSDPRIMEv2']['assets'], '18030207387280065324': 0.0}
claimed = collections.defaultdict(float)
for k, sym, amt, cid, oid, price in UB:
    claimed[(k, sym, oid)] += amt
out = {'snapshot': {'timestamp': T, 'block': TB}, 'method': ['Campaign data: Merkl v4 /campaigns?opportunityId= (creatorAddress, amount, start/end); raw raw/eth/gap-2026-10-07/top5-risk/merkl_campaigns.json',
       'Reward APR at T = campaign amount/duration annualized / destination vault totalAssets at T (archive read); applies pro rata to every unblacklisted holder (whitelist and blacklist empty for active campaigns).',
       'Product $/yr = APR x the product\'s destination claim at T. Token sources traced with Blockscout ERC-20 transfer history (raw http/bs_*.json).'], 'liquid': {}, 'destinationsWithoutMerkl': {}, 'otherProducts': {}}
rows = []
for c_ in active:
    oid = c_['opportunityId']
    if oid not in vault_ta: continue
    ann = c_['amount'] / (c_['end'] - c_['start']) * YEAR
    apr = ann / vault_ta[oid]
    rows.append({'opportunity': c_['opportunity'], 'opportunityId': oid, 'campaignId': c_['campaignId'], 'token': c_['token'], 'tokenAddress': c_['tokenAddress'], 'amount': c_['amount'],
                 'startUTC': c_['start'], 'endUTC': c_['end'], 'creator': c_['creator'], 'creatorMerklTags': c_['creatorTags'], 'whitelist': c_['whitelist'], 'blacklist': c_['blacklist'],
                 'annualizedRewardUSD': ann, 'vaultTotalAssetsAtT': vault_ta[oid], 'rewardAPRatT': apr, 'liquidClaimAtT': liq_claim[oid], 'liquidRewardUSDperYearAtT': apr * liq_claim[oid],
                 'merklOpportunityAPRnow_pct': MC['opportunities'][oid]['apr']})
out['liquid']['activeCampaignsAtT'] = rows
out['liquid']['totalRewardUSDperYearAtT'] = sum(r['liquidRewardUSDperYearAtT'] for r in rows)
claims_total = sum(liq_claim.values()) + H['stcUSD']['assets']
out['liquid']['rewardAPRonAllDollarDestinations'] = out['liquid']['totalRewardUSDperYearAtT'] / claims_total
out['liquid']['rewardAPRonEthCollateralDollarDebt'] = out['liquid']['totalRewardUSDperYearAtT'] / 181082907.45
out['liquid']['claimedViaMerklToDate_mainVault'] = {f'{sym} ({MC["opportunities"].get(oid, {}).get("name") or oid})': round(v, 2) for (k, sym, oid), v in claimed.items() if k == 'liquid_main'}
out['liquid']['distributor'] = '0x3ef3d8ba38ebe18db133cec108f4d14ce00dd9ae (Merkl Distributor proxy); recipient 0xf0bb20865277abd641a307ece5ee04e79073416c (Liquid main vault); LoanManager and drone have no Merkl rewards'
out['liquid']['fundingChains'] = {
    'RLUSD': {'campaignCreator': '0xCc6deDe79bc96dbBEe98E29DB51C0b7619ceE000 (Safe; Merkl creator tag "sentora"; deployed by SafeProxyFactory 0x4e1DCf7A...)',
              'chain': ['RLUSD mint (from 0x0) -> 0xFbcA8B5f5794456B59aD4177E5b212d0Db600BB6 (contract "MultiSign"; received 208.5M RLUSD straight from mint in Sep-Oct 2026)',
                        '-> 0xe146C01102e02344d4B1E59fD74b5054979D13A5 (EOA; 145M from the MultiSign)', '-> 0x69ae073586994371A772EFD96d65804c25F990A2 (EOA; 78.3M)',
                        '-> 0xE36B0bAe3E9985D70096ed1b37d4DcF91Edf4Dce (EOA; 68M)', '-> 0xB70e0fAd7D0CF4c187365A84E728802AB24Ca78b (EOA; 12M; also pays a Curve LiquidityGaugeV6 1.52M and ALMProxy 0x1601843c 1.84M)',
                        '-> creator Safe 0xCc6d...e000 (15.14M RLUSD in since Aug 2025) -> Merkl 0x3Ef3D8bA (14.85M out)'],
              'reading': 'Every hop is unlabelled, but the chain starts at the address that receives RLUSD directly from mint, i.e. issuer-side treasury. Sentora only creates the campaigns; the RLUSD is not paid out of Sentora vault fees.'},
    'PYUSD': {'campaignCreator': '0x43076BcfAe3D19d8A839dFa10597EC3012151609 (Safe; Merkl creator tag "sentora-pyusd"; same SafeProxyFactory deployer)',
              'chain': ['PYUSD mint (from 0x0) -> 0x264bd8291fAE1D75DB2c5F573b07faA6715997B5 (EOA receiving 10.0M PYUSD directly from mint in one day; 57.3M historically to 0x1da0d480)',
                        '-> 0x1da0d480dF75D7F2d91B14BdEa217Cb39C000C0a / 0x4CFB4a4B2A0E0153859953F2C6773255A853332A / 0xfc0539d019482D311C161AE3B756cDCcDEc45e87 / 0x1E30F9c2C688F85c82111d1d262bfD127E687282 (EOAs)',
                        '-> creator Safe 0x4307...1609 (9.64M PYUSD in since Apr 2026: 5.29M from 0xfc0539d0, 4.36M from 0x1E30F9c2) -> Merkl (9.67M out)',
                        '0x1E30F9c2 also funds Merkl creator Safe 0xdef1FA4C (tag "aave") with 0.96M PYUSD and received 0.21M PYUSD straight from mint'],
              'reading': 'Issuer-side PYUSD wallets fund the Sentora PYUSD campaigns (consistent with a PYUSD issuer incentive budget). Identity of the EOAs is not labelled on-chain.'}}
out['liquid']['historicalNonDollar'] = 'ETHFI (Aave weETH-lending campaigns by Safe 0xdef1FA4C tagged "aave", Oct 2025-Jan 2026) and rEUL (Euler Prime WETH, creators tagged "euler", 2024-2025) accrued to the E3 staking-loop legs, not the dollar legs; none active at T.'
out['destinationsWithoutMerkl'] = {
    'stcUSD (Cap, 0x88887be4)': 'No Merkl opportunity for the stcUSD identifier; yield arrives through the share price (Cap agents pay USDC borrow interest; 55.3M of 61.4M USDC reserve lent at T).',
    'earnUSD (Lido Earn USD, 0x4ce1ac8f)': 'No Merkl opportunity for the earnUSD identifier; yield is share price only in this read.',
    'savUSD (Avant)': 'Yield through the savUSD/avUSD exchange rate (Chainlink feed 0x9fbb7d07 on Ethereum); no Merkl campaign paying the Avant strategy wallet on its savUSD.',
    'Curve WETH/crvUSD LP (YieldBasis)': 'LP fees accrue to the AMM; gauge (YB token) emissions go to LT stakers, not to the debt leg.'}
liq = L['liquity']
bold = [c_ for c_ in active if c_['opportunityId'] == '13207567167701080626']
v4_tvl = MC['opportunities']['13207567167701080626']['tvl']
if bold:
    ann = sum(c_['amount'] / (c_['end'] - c_['start']) * YEAR for c_ in bold)
    out['otherProducts']['liquity'] = {'campaign': 'Uniswap V4 BOLD-USDC 0.05% (Merkl opp 13207567167701080626), creator 0xB4244885... tag "liquity"', 'annualizedBOLD': ann,
                                       'aprUsingMerklTVLnow': ann / v4_tvl, 'vaultV4BookUSD': 159364.4, 'estUSDperYear': ann / v4_tvl * 159364.4,
                                       'claimedToDate_BOLD': round(sum(v for (k, s, o), v in claimed.items() if k == 'liquity_vault'), 2),
                                       'note': 'TVL from Merkl API today (not T); the vault position is the stored V4 market book. Tiny relative to 6.75M debt.'}
out['otherProducts']['avant'] = {'claimedToDate': {f'{s} ({MC["opportunities"].get(o, {}).get("name") or o})': round(v, 2) for (k, s, o), v in claimed.items() if k == 'avant_wallet'},
                                 'note': 'Small Merkl claims (USDS from sky.money USDS Flagship V2 vault supply, MORPHO for WETH supply, USDC, WFRAX); not tied to the Aave/Spark dollar debt.'}
out['otherProducts']['lido-earn'] = 'No Merkl rewards on the carry account 0x181cb55f.'
out['otherProducts']['yieldbasis'] = 'No Merkl rewards on the LT; YB gauge emissions go to stakers.'
json.dump(out, open(ROOT / 'data/eth/gap_top5_rewards.json', 'w'), indent=1)
for r in rows: print(r['opportunity'], r['token'], round(r['amount']), f"APR {r['rewardAPRatT']*100:.2f}%", f"Liquid ${r['liquidRewardUSDperYearAtT']/1e6:.3f}M/yr")
print('total', out['liquid']['totalRewardUSDperYearAtT'], out['liquid']['rewardAPRonAllDollarDestinations'], out['liquid']['rewardAPRonEthCollateralDollarDebt'])
print(out['liquid']['claimedViaMerklToDate_mainVault']); print(out['otherProducts'].get('liquity'))
