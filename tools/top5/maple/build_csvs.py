#!/usr/bin/env python3
"""Assemble size_history.csv, yield_history.csv, events.csv from disclosed sources + on-chain reconstruction."""
import csv, datetime, collections
R = '../raw'; O = '..'
px = {r['date']: (float(r['core_usd']), float(r['btc_usd'])) for r in csv.DictReader(open(f'{R}/prices_daily.csv')) if r['core_usd']}
def btcp(d): return px.get(d, (None, None))[1]
cl = {r['date']: (float(r['cluster_btc']), float(r['network_btc_from_events'])) for r in csv.DictReader(open(f'{R}/core/maple_cluster_daily.csv'))}
ONCH = "BTC STAKED ON CORE - ON-CHAIN RECONSTRUCTION (estimate/attribution): BTC in active CLTV stakes on Core for 5 CORE reward addresses linked by shared BTC owner scripts (scripts/cluster_link.py, maple_cluster_series.py); Core BitcoinStake 0x...1014 events via rpc.coredao.org"
size = []
# disclosed points
def add(d, btc, usd, src):
    if usd is None and btc is not None and btcp(d): usd = round(btc * btcp(d))
    size.append([d, btc if btc is not None else '', usd if usd is not None else '', src])
add('2025-04-30', 1600, None, 'DISCLOSED: Maple X post 2025-04-30 "1600+ of Maple BTC staked to @Coredao_Org" https://x.com/maplefinance/status/1917628219223859367 (USD = BTC x Bybit close; derived)')
add('2025-05-02', 1600, None, 'DISCLOSED: Core blog 2025-05-02 "surpassed 1,600 BTC in deposits" https://coredao.org/blog/maple-core-bitcoin-yield-product (USD derived)')
size.append(['2025-06-23', round(140e6 / btcp('2025-06-23')), 140000000, 'DISCLOSED USD: OAK Research 2025-06-23 "$140M in assets under management" https://oakresearch.io/en/analyses/fundamentals/maple-bitcoin-yield-presentation-comparison-outlook (BTC derived)'])
size.append(['2025-06-30', round(180e6 / btcp('2025-06-30')), 180000000, 'DISCLOSED USD: Maple Q2 2025 market update "reaching over $180M in AUM" (published 2025-07-24) https://maple.finance/insights/q2-2025-maple-market-update (BTC derived)'])
size.append(['2025-07-07', 1500, 140000000, 'DISCLOSED: bitcoin.com 2025-07-07 "over 1,500 BTC allocated through H1 2025", AUM $140M https://news.bitcoin.com/maple-finance-delivers-5-13-native-bitcoin-yield-with-institutional-grade-security/'])
size.append(['2025 (undated)', 1500, 180000000, 'DISCLOSED: Maple page btc-yield-now-live (search snippet; page now 404) "More than 1,500 BTC has been deposited, totalling $180M" https://maple.finance/insights/btc-yield-now-live'])
size.append(['2025-11-19', '', 150000000, 'CLAIMED (counterparty): Core Foundation statement "Maple brought over $150m of Bitcoin" (cumulative, not point-in-time) https://x.com/Coredao_Org/status/1991171121534636264'])
for d in sorted(cl):
    dd = datetime.date.fromisoformat(d)
    if (dd.day in (1, 15) and '2025-02-01' <= d <= '2025-12-01') or d in ('2025-05-14', '2025-10-14', '2025-10-15', '2025-11-18', '2025-11-19'):
        b = cl[d][0]; add(d, round(b, 2), None, ONCH + f"; Maple share of Core BTC staked (events-based) = {b/cl[d][1]*100:.1f}%" if cl[d][1] else ONCH)
add('2025-10-15', 1341.03, None, 'PROGRAM BTC (on-chain, Bitcoin+Core): 756.98 BTC still staked + 463.06 BTC in matured-but-unspent CLTV outputs (not re-staked) + 120.99 BTC withdrawn to bc1q0vued... on 10-15; scripts/btc_outspends.py')
add('2025-11-19', 1333.78, None, 'ON-CHAIN (Bitcoin): all remaining CLTV outputs swept on 2025-11-19 into hub bc1pm9v0y2...c0pc4 (963.72+165.40+204.64 BTC); scripts/btc_outspends.py, btc_hub_trace.py via mempool.space')
add('2025-11-30', round(1333.78 - 1050.47, 2), None, 'ON-CHAIN (Bitcoin): 1,050.47 BTC paid out of hub in Nov-2025 (incl. 200.09 BTC holdback moved to separate wallet) -> remaining in hub; scripts/btc_hub_trace.py')
add('2025-12-31', 200.09, None, 'ON-CHAIN (Bitcoin): 1,133.69 BTC (85.0%) paid to 66 addresses Nov-2025..Aug-2026; 200.09 BTC (15.0%) held in bc1pdcj7.../bc1pyed82... (matches Maple 2025-11-21 statement: return 85%, retain 15%)')
add('2026-06-05', 0, 0, 'ON-CHAIN (Bitcoin): 200.0 BTC holdback sent 2026-06-05 (14 days after the 2026-05-22 settlement) via bc1q9tfmg8... to bc1q5zly2... (owner not public); hub emptied 2026-08-10')
add('2026-09-21', 0, 0, 'CURRENT: 0 BTC staked on Core by attributed addresses (rpc.coredao.org / stake.coredao.org candidate API); Maple API poolMeta 67e542004191822941f9e703 state="Hidden"; product page 404; no syrupBTC token or pool found')
size.sort(key=lambda r: r[0])
with open(f'{O}/size_history.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['date', 'btc', 'usd', 'source']); w.writerows(size)
# yield history
ym = {r['month']: r for r in csv.DictReader(open(f'{R}/core/maple_yield_model.csv'))}
def mavg(m):
    xs = [v[0] for d, v in px.items() if d.startswith(m)]; return round(sum(xs) / len(xs), 4) if xs else ''
tiers = {'2025-02': 'Satoshi tier 8,000->16,000 CORE/BTC (2025-02-27), 400%', '2025-03': '16,000 CORE/BTC; multiplier 625%->230%', '2025-04': '24,000 CORE/BTC (2025-04-03); 230%->400% (04-08)', '2025-05': '24,000 CORE/BTC; 400%', '2025-06': '24,000->29,000 CORE/BTC (06-13); 250%/600%/450%/325%', '2025-07': '34,000 CORE/BTC (07-15); 500%', '2025-08': '34,000; 500%', '2025-09': '34,000; 500%', '2025-10': '34,000; 500%', '2025-11': '68,000 CORE/BTC (11-11); 500%'}
ONY = 'ON-CHAIN ESTIMATE: CORE rewards claimed by attributed addresses (BitcoinAgent/CoreAgent claim events) x CORE/USD on claim date / (BTC staked x BTC/USD), annualised; claims are lumpy; excludes put payoffs, CORE inventory P&L, USDC borrow cost, fees (scripts/maple_yield_model.py)'
yrows = [
 ['2025-02 (launch)', 'target 5%+ (90-day lock)', ym.get('2025-02', {}).get('implied_gross_apr_pct_btc_terms', ''), mavg('2025-02'), 'Product live Feb-2025; first on-chain stake 2025-02-06; ' + tiers['2025-02'], 'CoinDesk 2025-02-17 https://www.coindesk.com/business/2025/02/17/bitcoin-staking-platform-core-joins-crypto-lender-maple-and-custodians-bitgo-copper-hex-trust ; ' + ONY],
 ['2025-03', 'target 4-6% (pool card)', ym['2025-03']['implied_gross_apr_pct_btc_terms'], mavg('2025-03'), 'Pool metadata created 2025-03-27: Target APY 4-6%, benchmarkApy 5, bimonthly maturity; ' + tiers['2025-03'], 'Maple GraphQL poolMeta(67e542004191822941f9e703) https://api.maple.finance/v2/graphql ; ' + ONY],
 ['2025-04', '5.6% net (April)', ym['2025-04']['implied_gross_apr_pct_btc_terms'], mavg('2025-04'), '"April was a record month ... 5.6% net APY, returned in BTC"; ' + tiers['2025-04'], 'https://x.com/maplefinance/status/1917628219223859367 ; ' + ONY],
 ['2025-05', '5.6% since launch', ym['2025-05']['implied_gross_apr_pct_btc_terms'], mavg('2025-05'), 'Core blog: "5.6% APY in native Bitcoin since launch"; ' + tiers['2025-05'], 'https://coredao.org/blog/maple-core-bitcoin-yield-product ; ' + ONY],
 ['2025-06', '5.1-5.6% range; 5.3% since launch; Q2 5.2% net', ym['2025-06']['implied_gross_apr_pct_btc_terms'], mavg('2025-06'), 'OAK 2025-06-23 (target 3-5%); Maple Q2 2025 update 5.2% net APY; ' + tiers['2025-06'], 'https://oakresearch.io/en/analyses/fundamentals/maple-bitcoin-yield-presentation-comparison-outlook ; https://maple.finance/insights/q2-2025-maple-market-update ; ' + ONY],
 ['2025-H1 (to 2025-07-07)', '5.13%', '', round(sum(v[0] for d,v in px.items() if '2025-01-01'<=d<='2025-06-30')/len([d for d in px if '2025-01-01'<=d<='2025-06-30']),4), 'bitcoin.com: 5.13% APY paid in BTC', 'https://news.bitcoin.com/maple-finance-delivers-5-13-native-bitcoin-yield-with-institutional-grade-security/'],
 ['2025-07', 'not disclosed', ym['2025-07']['implied_gross_apr_pct_btc_terms'], mavg('2025-07'), tiers['2025-07'] + '; CORE leg raised to 50.5M CORE (=1,485 BTC x 34,000)', ONY],
 ['2025-08', 'not disclosed', ym['2025-08']['implied_gross_apr_pct_btc_terms'], mavg('2025-08'), tiers['2025-08'] + '; one identifiable lender address received 0.3077 BTC from the hub (implied principal ~25.1 BTC; accrual period unknown)', ONY + '; mempool.space hub tx history'],
 ['2025-09', 'not disclosed', ym['2025-09']['implied_gross_apr_pct_btc_terms'], mavg('2025-09'), tiers['2025-09'] + '; same lender received 0.0662 BTC; 2025-09-26 ex parte injunction freezes CORE dealings; puts due 2025-09-30 not paid by Core', ONY + '; [2025] CIGC (FSD) 105 and FSD 2025-0268 judgment of 10 Oct 2025 (judicial.ky)'],
 ['2025-10', 'not disclosed', ym['2025-10']['implied_gross_apr_pct_btc_terms'], mavg('2025-10'), tiers['2025-10'] + '; same lender received 0.045 BTC; 584.047 BTC matured 10-15 but only 120.99 BTC withdrawn', ONY],
 ['2025-11', 'NEGATIVE: lenders repaid 85% of BTC principal; 15% withheld', ym['2025-11']['implied_gross_apr_pct_btc_terms'], mavg('2025-11'), tiers['2025-11'] + '; Maple 2025-11-21: "return 85% of BTC principal ... remaining 15% retained"; on-chain: 1,133.69 BTC paid to 66 addresses, 200.09 BTC held', 'https://x.com/maplefinance/status/1991886803092091268 ; scripts/btc_hub_trace.py'],
 ['2025-02..2025-11 (whole program)', '5.1-5.6% disclosed through Jul-2025 (nothing disclosed after); final lender outcome after 15% holdback NOT PUBLIC', '1.90 (range 1.9-2.7)', '0.5273 (BTC-weighted avg)', 'Total CORE rewards 4.66M CORE (BTC leg 3.05M, CORE leg 1.61M) on 848 BTC-years; gap to 5%+ implies ~3-4 pp/yr came from outside staking (put payoffs by Core Foundation / other) - estimate', ONY],
 ['2026-09-21 (current Core rates)', 'product closed', 'validator btcStakeApr 0.39-0.56%; CORE apr 2.4-4.8%', 0.0222, 'Satoshi tier now 68,000 CORE/BTC (500%); lstBTC system token supply 0; btc_lst_apr 0', 'https://stake.coredao.org/api/staking/search_candidate_page ; /api/staking/btc_lst_apr ; BitcoinAgent.getGrades() on rpc.coredao.org'],
]
with open(f'{O}/yield_history.csv', 'w', newline='') as f:
    # core_staking_apr = on-chain implied GROSS dual-staking yield, % p.a. in BTC terms (see source column)
    w = csv.writer(f); w.writerow(['period', 'realized_apy', 'core_staking_apr', 'core_price', 'notes', 'source']); w.writerows(yrows)
print('ok', len(size), len(yrows))
