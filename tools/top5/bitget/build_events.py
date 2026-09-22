"""-> ../events.csv (dated timeline; 'onchain' rows come from raw/*.json produced by the other scripts)"""
import csv
W='raw/web/'
E=[
('2025-03-01','First BGBTC mint on Ethereum (0x0520930F...); supply reaches 1,089 by Apr 2025, then burned down','onchain','raw/bgbtc_eth_supply_events.json'),
('2025-08-13','Chainlink Proof of Reserve for BGBTC goes live on Ethereum (feed 0xADcc914F...)','infra','https://www.bitget.com/blog/articles/bitget-chainlink-proof-of-reserve-bgbtc-2025'),
('2025-09-02','Bitget gives 440M BGB to Morph Foundation (220M burned); BGB becomes Morph gas/governance token','ecosystem','https://www.bitget.com/support/articles/12560603836781'),
('2026-04-29','CCIP BurnMintTokenPool for bgBTC deployed on Morph (0xf50b...); rate limits 190/200 bgBTC','onchain','raw/morph_ccip_pool_logs.json'),
('2026-06-30','Morpho market bgBTC/USDC created (id 0x37d156e9..., LLTV 77%, RedStone BTC/USD oracle, AdaptiveCurveIRM); gtusdc VaultV2 deployed, 0% fees, 7-day timelocks on caps/adapters','onchain','raw/morpho_logs_market.json; raw/gtusdc_logs.json'),
('2026-07-09','Aera vault gtOVBG (0x85a1...) registered in PriceAndFeeCalculatorV2 (0/0 fees); test borrower liquidated in the market (4.84 USDC)','onchain','raw/pfc_logs_vault.json; raw/morpho_market_decoded.json'),
('2026-07-14','CCIP pool ownership (Morph) moves to EOA 0xdb25... (also owner of bgBTC on both chains, Aera vault and CCIP pools)','onchain','raw/morph_ccip_pool_logs.json'),
('2026-07-15','Bitget ops EOA 0xbd5b... seeds Native wNLP-USDC with $1M from Bitget hot wallet','onchain','raw/tt_0xbd5bbf1ef0d6eec9010df20ba0d325df97d5957b.json'),
('2026-07-16','Omnibus EOA 0x9EB5... bridges 25 bgBTC via CCIP and seeds Native wNLP-BGBTC (25 bgBTC)','onchain','raw/omnibus_token_transfers.json'),
('2026-07-21','gtusdc liquidityAdapter removed (deposits stay idle until allocated); owner -> Safe 0xc2ae (2-of-2 incl. EOA 0xdb25...)','onchain','raw/gtusdc_logs.json'),
('2026-07-22','Reward distributor 0x53d2... starts test campaigns (USDC, BGB); omnibus test deposit 0.1 bgBTC','onchain','raw/campaigns.json'),
('2026-07-27','Vault price thresholds tightened to +-1%/h; distributor ownership -> Safe 0x72c5 (4-of-6)','onchain','raw/pfc_logs_vault.json; raw/distributor_logs.json'),
('2026-07-29','CCIP limits lifted to 500 bgBTC for one bridge of 500 bgBTC, then cut to 65/80 per day; first $39,724 weekly USDC campaign funded from Bitget hot wallet','onchain','raw/morph_ccip_pool_logs.json; raw/campaigns.json'),
('2026-07-30','Bitget: "BGBTC is now upgraded", reference APR up to 2%, T+3-5 standard redemption; omnibus deposits 60 bgBTC','product','https://www.bitget.com/support/articles/12560603889792'),
('2026-07-31','Launch: Morph / RedStone / Gauntlet announcements (~3% BTC, ~18% USDC); omnibus deposits 440 bgBTC; PoR 820 BTC','launch','https://blog.morph.network/morph-partners-with-gauntlet-and-morpho-to-bring-institutional-grade-defi-yield-to-bitget-and-bitget-wallet-users/'),
('2026-08-03','USDC option live in Bitget Wallet (gtusdc on Morph)','product','https://bitpinas.com/cryptocurrency/morph-bitget-gauntlet-morpho'),
('2026-08-04','Vault first claims USDC rewards and swaps them to bgBTC via Native RFQ; leverage ramp from ~20% to ~38% LTV (4-7 Aug)','onchain','raw/aera_swaps_claims.json; raw/ltv_path.json'),
('2026-08-07','Blockhead: "$55M TVL in a week" ($32.1M BTC + $23.2M USDC vault; double-counts ~$12.1M looped USDC)','press','https://www.blockhead.co/2026/08/07/bitgets-yield-vaults-on-morph-cross-55m-in-tvl-one-week-after-launch/'),
('2026-08-14','Bitget BGBTC quota campaign; 200 BGBTC minted on Ethereum; CCIP limits lifted again; 300 bgBTC bridged; PoR 1,120 BTC','campaign','https://www.bitget.com/support/articles/12560603891580'),
('2026-08-17','Omnibus deposits 300 bgBTC; vault LTV raised to ~62% (target band since)','onchain','raw/omnibus_token_transfers.json; raw/ltv_path.json'),
('2026-08-18','PoolX: lock BGBTC for 9,200 UNI airdrop (to 23 Aug)','campaign','https://www.bitget.com/support/articles/12560603892311'),
('2026-08-20','BTC +13% intraday; vault bot cycles ~148 bgBTC collateral out and back, re-levers to ~62%','onchain','raw/morpho_market_decoded.json'),
('2026-08-21','Morph blog: Bitget Wallet USDC vault "earns 6% APY" (was ~18% at launch)','press','https://blog.morph.network/how-to-earn-on-your-usdc-with-morph/'),
('2026-08-25','Bitget: +2% Simple Earn APR and BGBTC quota 1:1 to net BTC deposits (subscription 2-3 Sep)','campaign','https://www.bitget.com/support/articles/12560603893165'),
('2026-08-28','Bitget suspends BGBTC-Morph deposits/withdrawals ("wallet maintenance"); no resumption notice found','incident','https://www.bitget.com/support/articles/12560603893675'),
('2026-09-01','PoR 1,420 BTC; 200 BGBTC minted 1-2 Sep; extra supply stays idle (vault near $50M market cap)','onchain','raw/por_rounds.json; raw/bgbtc_eth_supply_events.json'),
('2026-09-09','Omnibus redeems 1 vault unit (1.00255 bgBTC, 40 min) and sends 1 bgBTC to a Bitget deposit address','onchain','raw/omnibus_token_transfers.json'),
('2026-09-15','Bitget VIP campaign: +1% APR on BTC net deposits; BGBTC quota 1 per 4 BTC (subscription 22-24 Sep)','campaign','https://www.bitget.com/support/articles/12560603895080'),
('2026-09-21','Snapshot: vault 801.7 bgBTC collateral, $43.03M debt, LTV 62.0%, unit price 1.00337; gtusdc $52.35M (82.1% owned by the vault); Bitget annualRate 1.70%','onchain','raw/state_now.json; raw/web/bitget_api_bgbtc_landing_statistics.json'),
]
with open('events.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['date','event','type','source']); w.writerows(E)
print(len(E))
