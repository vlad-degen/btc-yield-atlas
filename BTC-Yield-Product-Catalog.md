# Каталог BTC-yield продуктов и волтов
### Полный реестр: похожие продукты, BTC-волты, CeFi/банки/фонды/ETF, стейкинг, опционы, кредиторы

**Дата снимка:** 20 сентября 2026 · BTC $80 681
**Дополняет:** [BTC-Yield-Market-Research.md](BTC-Yield-Market-Research.md) (аналитика, юнит-экономика, выводы)
**Источники размеров:** DefiLlama (protocols/yields), Morpho API, публичная отчётность. Доходности — на дату, переменные, если не сказано «fixed».
**Обозначения:** ★ = прямой аналог вашего архетипа (BTC-залог → заём стейбла → размещение → доходность в BTC); ◐ = частично (залог BTC / кэрри как один из компонентов); TVL — в USD; «BTC-ном.» = доходность выплачивается в BTC.

---

## A. Прямые аналоги ★ — «залог BTC → заём стейбла → доходность» с управлением позиции

| # | Продукт | Стек / механика | Доходность (BTC-ном.) | Размер | Доступ · кастоди | Комментарий |
|---|---|---|---|---|---|---|
| A1 | ★ **Kraken Bitcoin Vault** | Kraken → kBTC → Ink → Veda BoringVault → **Sentora** → Morpho (kBTC/RLUSD 3.07%, kBTC/PYUSD 3.55%) + Aave/Euler/Curve. LTV 63.5%, LLTV 86%, без рекурсии | **0.88%** (лендинг) / 1.4% / 1.8% (30d) | kBTC $762M; Morpho kBTC $510M залог / $324M долг; BTC-волт $320M+ | Розница, мин. 0.00006 BTC; non-custodial kBTC; вывод 3–5 дн.; нет UK/UAE/AU | 25% perf fee. $0 ликвидаций у Sentora за 3+ года |
| A2 | ★ **Kraken «Advanced Strategies BTC»** (DeFi Earn) | Тот же стек Sentora/Veda; «simple lending, leveraged looping, LP» на Ethereum + Ink | 1.8% net 30d | $320M+ (июль 2026) | Розница | Часть $611M / 80k депозиторов по 4 волтам |
| A3 | ★ **Bitget bgBTC Onchain Earn** | Bitget → bgBTC → Morpho на Morph, куратор **Gauntlet** | **3%** | bgBTC $114M | Розница, 125M юзеров биржи | USDC-волт там же — до 18% (стимулы Morph) |
| A4 | ★ **Hermetica hBTC** (Stacks) | BTC → sBTC → залог на Zest (3.5% dual stacking) → заём USDCx → USDh (synthetic $) → стейк под funding → обратно в sBTC | **5.60%** 7d avg; таргет до 8% | ~50 BTC / $3.8M | Self-custodial; редемпция в native BTC | Апр-2026: добавлен доход от STRC (Strategy) |
| A5 | ★ **Mezo Prime / Mezo Earn** | Native BTC в изолированном Enclave (Anchorage) → заём MUSD под **1% fixed** до 90% LTV → волты | BTC-волт 2–5%; Mezo Earn BTC 2.96% (2.93 rewards) | Mezo TVL $72.4M; Mezo Earn $65M; lifetime $487M | Институты (Prime) + розница; без rehypothecation | Bullish — ранний участник. Дешёвый долг = главный рычаг |
| A6 | ★ **Avalon Labs (USDa / sUSDa / Superearn)** | BTC + BTC-LST залог в CeDeFi CDP → USDa (fixed rate) → sUSDa доходность; Superearn — доходные волты | н/д (USDa fixed borrow) | Avalon CeDeFi $103M + Superearn $115M | Розница; CeDeFi-кастоди | Заявлено $2B кредитных линий; «крупнейший BTC-CDP» |
| A7 | ★ **Acre acreBTC** (Threshold, куратор **Re7**/Midas) | BTC → tBTC → macreBTC1 (Re7) → mRe7BTC/mRe7YIELD | заявлялось ~14%; **реализовано −1.24%** (share 1.0002 → 0.9876) | закрыт: депозиты остановлены, редемпции открыты | 51/100 multisig; вывод до 72 ч | markdowns 11.05 и 11.06.2026; см. Deep Dive §4.5 |
| A8 | ★ **ether.fi Liquid BTC / eBTC** | Veda-волт: rate-арбитраж между BTC-активами на Aave/Morpho + стейбл-доходности + points (Babylon/Lombard/Veda) | LIQUIDBTC 1.55%; eBTC stake 0.15% | ether.fi Liquid $433M всего; LIQUIDBTC пул $11M; eBTC $22M | Розница; Veda | Принимает eBTC/WBTC/LBTC/cbBTC |
| A9 | ★ **Lombard Bitcoin Earn (Lombard Vaults)** | Мульти-стратегия поверх LBTC: лендинг, LP, structured, cross-chain (Curve/Uniswap) | **>2%** | $161M заявлено; DefiLlama $74M | Розница | LBTCv (Veda) $72M отдельно |
| A10 | ★ **Hyperbeat Ultra UBTC** (HyperEVM) | Автоматизированный волт UBTC + Morphobeat lending + points (Felix, Silhouette, Upshift) | переменная + points | HBBTC (Upshift) $0.86M; UBTC-рынки Morpho ~$4.4M | Розница | Экосистема Hyperliquid |
| A11 | ★ **Midas mHyperBTC** (оператор Hyperithm) | LYT: BTC-ном. market-neutral стратегии onchain; NAV-price token | Pendle PT 2.28% implied | Morpho mHyperBTC $5.8M залог; Pendle $5.2M | Permissionless ERC-20 | Есть рынок mHyperBTC/USDC @9.84% borrow |
| A12 | ★ **Midas mRe7BTC** (оператор Re7) | Native BTC staking + options premia + тактический DeFi | н/д | малый; торги на CG остановлены | Ethereum, Starknet | Ring-fenced структура |
| A13 | ★ **Midas mBTC** | Токен, трекающий BTC lending rates | ~1.36% (DefiLlama midas-rwa BTC) | $23–29M | Permissionless | «4% в BTC» — исторический таргет |
| A14 | ★ **BIMA USBD + Bracket** | BTC-backed стейбл USBD → real-yield волты (Bracket) | н/д | BIMA CDP $10M | Розница | Binance Labs-backed |
| A15 | ★ **Upshift BTC-стратегии** | Кураторские волты: Lombard LBTC (ETH/Base), Upshift BTC, Hyperbeat uBTC | переменная | Upshift $410M всего | Розница | Пример loop: sUSDe→Aave→sUSDe ×3–4 |
| A16 | ◐ **Zest Bitcoin Collateral Vaults** (Stacks → Bitcoin L1) | BTC остаётся на L1 (BitVM), заём стейблов на destination chain; sBTC-лендинг с dual stacking | sBTC 4.13% avg (Q1); до 12.5% boosted | 800+ BTC; Zest V2 $69M | Self-custodial | **1 500+ ликвидаций без bad debt** |
| A17 | ◐ **Concrete BTC vaults** | Инфраструктура волтов; ctWBTC Berachain/Ethereum | ~0% base + PoL | $38M BTC-пулы; Concrete $1.23B | Розница | |
| A18 | ◐ **Lagoon evcbBTC** | Кураторский cbBTC-волт (Euler) | 7.93% | $1.2M | Розница | Lagoon $151M всего |
| A19 | ◐ **Fusion by IPOR WBTC** | Автоматизированный WBTC-волт | 3.93% | $4.6M | Розница | |
| A20 | ◐ **Native Credit Pool WBTC** | WBTC credit pool | 2.91% | $4.5M | | |
| A21 | ◐ **Superform superWBTC** | Мета-волт WBTC | 1.54% (rewards) | $0.9M | | Superform $4.7M raise, SuperVaults v2 |
| A22 | ◐ **YO Protocol cbBTC** (Base) | Yield optimizer cbBTC | 0% | $8.7M | | |
| A23 | ◐ **Avant avBTC / savBTC** (Avalanche) | Кураторский BTC-волт | 2.23% | $8.2M | | Silo savBTC рынок $1.8M |
| A24 | ◐ **Accountable YieldApp cbBTC** (Monad/Citrea) | Uncollateralized lending с верификацией данных | **14.03%** (13.35 base) | $47M | | Кредитный риск заёмщиков |
| A25 | ◐ **btcd sBTCD** | BTC-dollar/структурированный волт | 7.57% | $1.2M | | |
| A26 | ◐ **multipli.fi xWBTC** | Yield-bearing WBTC | 1.28% | $3.8M | | |
| A27 | ◐ **Sentora Curator WBTC** (Morpho) | Кураторский WBTC-волт | 0.05% | $3.8M | | Показательно: чистый BTC-лендинг ≈ 0 |
| A28 | ◐ **Solv Strategies** | Автоматизированные BTC-стратегии (LP, farming) | переменная | $69M | Розница | |
| A29 | ◐ **Solv BTC+** | Мульти-стратегия: DeFi + CEX + оффчейн | таргет 5–8% | (внутри Solv) | Розница | |
| A30 | ◐ **Badger DAO** | Legacy BTC-агрегатор | н/д | $13M | | Исторический лидер 2021 |
| A31 | ◐ **Proxy Finance (PRXY)** | «Bitcoin Yield Strategies», (3,3)-механика | н/д | $21M | | Высокий риск токеномики |
| A32 | ◐ **Two Prime «C Vault» / Axiom** | Кредитование институтов (см. E) | 1.5–2% | $12M first-loss | non-US, мин. 5 WBTC | Не кэрри, но конкурент за депозит |

---

## B. Ончейн-примитивы, из которых собирается архетип (где взять заём, куда деть стейбл)

### B1. Рынки займа под BTC-залог (топ по занятому объёму)

| Площадка | Залог / заём | Залог | Занято | Ставка займа | LLTV |
|---|---|---|---|---|---|
| Morpho Base | cbBTC / USDC | $3 042M | $1 429M | 4.81% | 86% |
| Morpho Ethereum | cbBTC / USDC | $712M | $306M | 4.56% | 86% |
| Morpho Ethereum | kBTC / RLUSD | $288M | $185M | **3.07%** | 86% |
| Morpho Ethereum | WBTC / USDC | $244M | $112M | 4.57% | 86% |
| Morpho Ethereum | kBTC / PYUSD | $222M | $139M | **3.55%** | 86% |
| Morpho Ethereum | WBTC / USDT | $153M | $75M | 2.94% | 86% |
| Morpho Ethereum | cbBTC / USDT | $62M | $30M | 2.98% | 86% |
| Morpho Ethereum | cbBTC / RLUSD | $40M | $11M | 4.01% | 86% |
| Morpho Ethereum | cbBTC / EURCV | $21M | $13M | 2.00% | 86% |
| Morpho Circle chain | cirBTC / USDC | $18M | $11M | 0.03% | 86% |
| Morpho Katana | vbWBTC / vbUSDC | $12M | $7M | 2.66% | 86% |
| Morpho Hyperliquid | UBTC / USD₮0 | $2.2M | $1.0M | 7.26% | 77% |
| Morpho Hyperliquid | UBTC / USDe | $0.6M | $0.25M | 8.31% | 77% |
| **Aave v3** (все сети) | WBTC/cbBTC/LBTC/tBTC/FBTC/BTC.b/BTCB | **$5.27B** | н/д (общий пул) | USDC ~3.6–4% | 70–80% |
| **SparkLend** | cbBTC $462M · LBTC $221M · WBTC $171M | $855M | н/д | — | |
| **Compound v3** | WBTC/cbBTC | $605M | н/д | — | |
| **Venus (BSC)** | BTCB $366M · SolvBTC $206M · xSolvBTC $63M | $635M | н/д | — | |
| **JustLend (Tron)** | BTC | $532M | н/д | — | |
| **Fluid** | WBTC | $62M | н/д | — | smart collateral |
| **Tydro (Ink, Aave-based)** | kBTC | $92M | н/д | — | Kraken L2 |
| **Kamino (Solana)** | cbBTC $58M · xBTC $17M · zBTC | $86M | н/д | — | |
| **Jupiter Lend (Solana)** | cbBTC | $10M | | | |
| **NAVI (Sui)** | enzoBTC $35M · mBTC $24M · LBTC | $68M | | | |
| **Takara (Sei)** | enzoBTC $22M · UBTC $18M | $44M | | | |
| **Townsquare (Monad)** | enzoBTC | $76M | | | |
| **Dolomite** | stBTC $20M (Berachain) · WBTC | $23M | | WBTC 1.97% supply | |
| **Euler v2** | cbBTC/WBTC | $1.3–1.9M | | cbBTC 2.06% | |
| **crvUSD / LlamaLend** | WBTC $49M · cbBTC $15M · tBTC | $75M | | | |
| **Sky (Maker)** | WBTC | $27M | | | |
| **HyperLend** | UBTC | $9.7M | | 0.33% | |
| **Vesu / Endur / Troves (Starknet)** | WBTC | $7.5M / $2.5M / $3.3M | | 2.1–3.3% | |
| **Benqi (Avalanche)** | BTC.b | $6M | | 1.35% | |
| **Moonwell (Base)** | cbBTC | $4.9M | | 3.46% | |
| **Felix CDP (Hyperliquid)** | feUBTC → feUSD | $1.9M | | | |
| **Frankencoin** | cbBTC | $28M | | | |
| **Inverse FiRM / Gearbox / Vesper / Kava** | WBTC | <$1M каждый | | | |

### B2. CDP / BTC-обеспеченные стейблкоины (собственное «дешёвое фондирование»)

| Протокол | Стейбл | Механика | Размер | Заметка |
|---|---|---|---|---|
| **Mezo** | MUSD | 1% APR fixed, до 90% LTV | Mezo Borrow $2.9M (ончейн) + Prime | см. A5 |
| **Avalon** | USDa | fixed rate, CeDeFi | $103M+ | см. A6 |
| **Sovryn Zero** (Rootstock) | ZUSD/DLLR | 0% interest, one-time fee | $20M | Старейший BTC-CDP |
| **Money on Chain** (Rootstock) | DoC | Dual-token | $22M | |
| **BIMA** | USBD | | $10M | |
| **Threshold thUSD** | thUSD | tBTC/ETH залог | $2.2M | |
| **Yala** | YU | BTC → cross-chain стейбл | $2.3M | |
| **BTCFi CDP** (Bifrost) | | native BTC → стейбл | $7.4M | |
| **Hermetica USDh** | USDh | synthetic $ (funding) на Stacks | $2.0M | Используется в hBTC |
| **Felix** (Hyperliquid) | feUSD | CDP | $35M | |
| **Lista CDP** (BSC) | lisUSD | BTCB залог | $1.9M BTCB | |
| **Bitsmiley / Satoshi Protocol** | bitUSD / satUSD | BTC L2 CDP | малые | |
| **VETRO** | VUSD / vetBTC | yield-bearing collateral | $0.6M | |
| **Saturn** | USDat / sUSDat | **не** BTC-CDP: USDat backed T-bills, sUSDat = STRC-доходность 11%+ | $141M | см. раздел H |

### B3. Куда размещать занятые стейблы (TVL > $100M)

| Венчур | APY | 30d | TVL | Тип риска |
|---|---|---|---|---|
| Maple USDC | 5.07% | 4.96% | $2.85B | Обеспеч. институц. кредит |
| Sky sUSDS | 3.60% | 3.57% | $4.40B | RWA/T-bills |
| Ethena sUSDe | 4.67% | 4.67% | $1.33B | Базис (депег-риск!) |
| Ondo USDY | 3.58% | 3.56% | $1.18B | T-bills |
| BlackRock BUIDL | 3.75% | 3.57% | $993M | T-bills |
| Maple USDT | 4.72% | 4.63% | $688M | |
| Sentora RLUSD v2 (Morpho) | 6.11% (2.62+3.50 rw) | 6.16% | $369M | Стимулы Ripple |
| Sentora PYUSD Main (Morpho) | 5.22% (2.44+2.78 rw) | 5.72% | $436M | Стимулы PayPal |
| Sirloin USDC (Base) | 5.56% | 5.67% | $426M | |
| Steakhouse USDC (Base) | 4.35% | 4.32% | $428M | |
| Gauntlet USDC Prime (Base) | 4.35% | 4.32% | $420M | |
| Spark USDC | 3.90% | 3.88% | $273M | |
| Jupiter Lend USDC (Solana) | 4.91% | 4.86% | $470M | |
| USD.AI sUSDAI | 6.94% | 7.19% | $494M | GPU-кредит |
| Re reUSD | 6.82% | 6.55% | $265M | Перестрахование |
| Pareto Credit USDC | 7.82% | 7.89% | $155M | Частный кредит |
| Fluid USDC / USDT | 4.06% / 5.02% | | $147M / $126M | |
| Aave USDC / USDT | 3.62% / 3.89% | | $173M / $198M | |
| sGHO | 4.50% | | $163M | |
| Usual BUSD0 | 4.46% (rw) | | $505M | Стимулы |
| Curve 3pool | ~0% | | $160M | |

### B4. LP / AMM как источник BTC-дохода (без займа)

| Пул | Проект | APY | TVL |
|---|---|---|---|
| **Yield Basis** YB-cbBTC / YB-WBTC / YB-tBTC | 2x-lev LP без IL | **7.24% / 4.79% / 3.60%** (100% rewards) | $21M / $30M / $14M; протокол $132M |
| WBTC-WETH | Uniswap v3 ETH / Arb | 1.4–10% | $45M / $37M |
| WBTC-USDT | Uniswap v3 | 4.2–10.3% | $29M + $26M |
| WBTC-USDC | Uniswap v3 | 2.4% | $21M |
| crvUSD-WBTC / crvUSD-cbBTC / crvUSD-tBTC | Curve | 0–1.2% | $68M / $56M+$21M / $37M |
| GHO-cbBTC-WETH | Curve / Convex / StakeDAO | 4.75% / 9.35% / 7.61% (rw) | $31M |
| USDT-WBTC-WETH (tricrypto) | Curve / Convex / Yearn | 1.4–4.9% | $14M |
| WETH-cbBTC | Aerodrome Slipstream (Base) | 2.8% (base 0.8) | $16M |
| WBTC.B-USDC GM | GMX v2 (Arb/Avax) | 3.75–19% | $61M+ |
| SOL-WBTC / WBTC-USDC | Orca / Raydium (Solana) | 7.6–38% | $22M |
| XBTC-WBTC | Bluefin (Sui) | 12.6% (rw) | $7.9M |
| WHYPE-UBTC | HyperSwap / Project-X / Ramses | 11–46% | $3–8M |
| XUSD-RBTC | Sovryn DEX (Rootstock) | 6.6% (rw) | $3.7M |
| BTC pool | Chainflip AMM (native BTC) | 4.37% | $5.2M |
| WBTC-cbBTC / WBTC-kBTC | Fluid DEX / Uniswap | 0.02–0.26% | $17M / $37M |
| sBTC pools | Bitflow (Stacks) | н/д | — |

---

## C. Стейкинг / рестейкинг / L2-native доходность (BTC-in, BTC-out)

| # | Продукт | Механика | Доходность | Размер | Заметка |
|---|---|---|---|---|---|
| C1 | **Babylon** | Native BTC на L1 → security для PoS-сетей; награды в BABY | **0.24–0.4%** | **$3.32B** (пик $6.66B сен-2025) | Self-custodial, timelock. Доминирует BTCFi по TVL, но доходность околонулевая |
| C2 | **Lombard LBTC** | Babylon LST; с 2026 — **covered-call стратегия под управлением Bitwise** | база 0.38%; таргет **2.5% net** | **$690M** (пик $1.65B) + BTC.b $172M | 8% fee на yield. Доступ через **Ledger Wallet** (Figment) |
| C3 | **Solv xSolvBTC / SolvBTC.CORE / BTC+** | LST-агрегатор: Babylon + Core + basis + RWA | xSolvBTC **~4%**; BTC+ 5–8% таргет | SolvBTC $517M; LSTs $78M; Basis $199M | 12 сетей; Venus xSolvBTC $63M |
| C4 | **Bedrock uniBTC** | Babylon LRT + Symbiotic | Symbiotic uniBTC 0.42%; Pendle YT ист. 22% | **$374M** (18 сетей) | |
| C5 | **Lorenzo stBTC / enzoBTC / OTF** | stBTC = Babylon LST; enzoBTC = wrapper; OTF = токенизированные фонды | н/д | enzoBTC $485M; stBTC $0.03M | Пивот в asset management (sUSD1+ $80M) |
| C6 | **PumpBTC** | Babylon LRT | н/д | $28M | |
| C7 | **Core lstBTC** (Maple + BitGo/Copper/Hex Trust) | Dual staking Core: BTC в кастодиане + CORE → награды CORE, выплата в BTC | **5%+** таргет (90d lock); lstBTC ниже | (внутри Maple $2.98B) | Институты; BTC не покидает кастодиана |
| C8 | **b14g** (Core/Babylon Genesis) | Модульный dual-staking слой | 0.12% | $189–260M | |
| C9 | **Stacks Dual Stacking / sBTC** | sBTC + STX → PoX-награды | база 0.36%; boosted 3.56%; «~3%» таргет | sBTC $199M | Self-custodial на L1 (Stacks BTC Staking — не запущен полностью) |
| C10 | **Starknet BTC Staking** | WBTC/LBTC/tBTC/SolvBTC → security → STRK | **3.80%** (в STRK) | $47M | Эмиссионный |
| C11 | **Botanix stBTC** (Spiderchain) | 50% gas-fees сети в BTC → стейкерам | **34% APR** headline (накопленное); ожидается 5–6% | н/д | Займы <1% APR; 16 операторов (Galaxy, Fireblocks, Alchemy) |
| C12 | **GTBTC (Gate)** | Биржевой BTC-LST | внутренний earn | **$279M** | |
| C13 | **Bitget bgBTC** | Биржевой wrapper + Morpho/Gauntlet | 3% | $114M | см. A3 |
| C14 | **OKX xBTC** | Биржевой wrapper | н/д | $66M | Kamino xBTC $17M, Sui |
| C15 | **exSat Staking BTC** | Docking layer; стейкинг | н/д | $170M | |
| C16 | **B² Buzz Farming** | Farming с Babylon/Lombard/Bedrock на BSquared | н/д | **$259M** | |
| C17 | **Merlin Chain (M-BTC)** | BTC L2 стейкинг | 16.2% заявлено (coming soon по трекеру) | $8.6M трекер; L2 TVL ист. $1.7B | |
| C18 | **Bitlayer YBTC** | BTC L2 wrapper | н/д | $32M | |
| C19 | **Hemi hemiBTC** | BTC L2 wrapper | н/д | $0.6M wrapper; L2 ист. $1.2B | |
| C20 | **BOB Stake / Gateway** | 1-click BTC → LST (Solv, Bedrock, PumpBTC, Chakra, Pell) | зависит от LST | BOB Bridge $3M | Intents-мост |
| C21 | **Pell Network** | Omnichain BTC restaking | н/д | малый | |
| C22 | **SatLayer** | BVS-рестейкинг | н/д | $0.2M | $8M pre-seed |
| C23 | **Symbiotic BTC vaults** | uniBTC $82M @0.42%; LBTC $47M @1.38% | 0.4–1.4% (rw) | $135M | |
| C24 | **Kernel (BNB)** | BTC restaking на BSC | н/д | $1.4M | |
| C25 | **Chakra / pSTAKE BTC / alloBTC / LISA** | Babylon LST | н/д | ≈0 | Мёртвые/дремлющие |
| C26 | **Nomic nBTC / stBTC** | Cosmos-сайдчейн, Babylon LST | н/д | малый | |
| C27 | **Zeus zBTC / btcSOL / APOLLO** (Solana) | zBTC — permissionless wrapper с 16+ yield-источниками; btcSOL — стейк SOL → выплаты в zBTC | н/д | Zeus $3.8M; btcSOL $0.6M; 21.8 zBTC minted | |
| C28 | **zenBTC** (Solana) | Yield-bearing wrapper | н/д | малый | Kamino/Orca/Meteora |
| C29 | **Chain Fusion ckBTC** (ICP) | Децентр. wrapper | н/д | $25M | Liquidium lending $4M |
| C30 | **Echo aBTC** (Aptos) | Bridge + restake + earn на Move | н/д | Echo Bridge $96M; Lending $5.6M | |
| C31 | **Volo / Current / SpringSui** (Sui) | xBTC/LBTC-стратегии | Current xBTC 3.39% | $16M | |
| C32 | **Lightning: Amboss Magma / Rails** | Лизинг каналов + routing fees в native BTC | **1–4% APY** (крупные каналы ~2.6%) | LN $300M | Единственная «true native» доходность без контрагента; ~break-even после хостинга |
| C33 | **Vishwa** | Agent-native banking, BTC anchor | н/д | $70M | |
| C34 | **BitFi BTC** | CeDeFi staking + synthetic | н/д | $82M + Basis $227M | |
| C35 | **ObeliskBTC** | Restaking + стратегии | н/д | $26M | |
| C36 | **Bitcoin Standard Hashrate (BTCST)** | Токенизированный хэшрейт | н/д | $1M | Не yield на BTC, а майнинг |

---

## D. Базис / delta-neutral / market-neutral (в т.ч. фонды)

| # | Продукт | Механика | Доходность (BTC-ном.) | Размер | Доступ · кастоди |
|---|---|---|---|---|---|
| D1 | **Coinbase Bitcoin Yield Fund (CBYF)** | Cash-and-carry спот vs перпы/CME; без лендинга и call-selling | **4–8%** таргет net | ёмкость $1B; AUM не раскрыт | Non-US институты; Coinbase Custody; токенизированный класс на Base (Apex) |
| D2 | **Coinbase US Bitcoin Yield (USCBYF)** | То же | 4–8% | н/д | US accredited; в 2026 — в пенсионных счетах |
| D3 | **Sygnum × Starboard «BTC Alpha Fund»** | Market-neutral | **8.9%** annualized net (Q1) | 750+ BTC / $65M | Институты; Sygnum (FINMA) |
| D4 | **Syntetika hBTC** (Hilbert Group, Base) | «BTC Basis+»: регулируемый фонд, NAV-аттестация, PoR | **11.61%**; 2025: **+20.18% net** | $14.2M | cbBTC → hBTC; независимая кастоди |
| D5 | **Laser Digital (Nomura) Bitcoin Diversified Yield Fund** | Long BTC + market-neutral арбитраж + лендинг + опционы; токенизирован через KAIO | **~5%** таргет | н/д | Cayman; $250k мин.; accredited |
| D6 | **BounceBit CeDeFi** | Basis + продажа путов через CEFFU + collateral yield | пример: 4.7% basis + 15% puts + 4.25% = 24% брутто | **$289M** AUM | Розница; CEFFU |
| D7 | **Solv Basis Trading** | Basis на CEX | н/д | $199M (BTCB $238M / WBTC $201M / BOB $46M пулы) | |
| D8 | **BitFi Basis** | Basis | н/д | $227M | |
| D9 | **Bitway Earn** (BSC) | Basis | н/д | $84M | |
| D10 | **Liminal Basis xBTC** (Hyperliquid) | Basis на HL | 9.74% | $1.2M | |
| D11 | **Ethena USDe** | BTC/ETH-backed basis, но доходность в USD | sUSDe 4.67% | $4.84B | Не BTC-ном.; депег до $0.65 на Binance в окт-2025 |
| D12 | **Falcon Finance** | Basis, USD-ном. | — | $1.21B | |
| D13 | **XBTO Market Neutral Fund** | Алго-стратегии | н/д | н/д | Институты; Bermuda |
| D14 | **Two Prime** (фонды) | Кредит + структурные | — | 3 000+ BTC выдано | см. E |
| D15 | **GlobalStake Bitcoin Yield Gateway** | Агрегатор сторонних стратегий под единым compliance | н/д | таргет $500M за 3 мес. | Институты (фев-2026) |

**Категория Basis Trading на DefiLlama: 43 протокола, $7.58B.**

---

## E. Кредитование BTC институтам (доходность = кредитный спред)

| # | Продукт | Механика | Доходность | Размер | Условия |
|---|---|---|---|---|---|
| E1 | **Maple BTC Yield** | BTC в Copper/BitGo → залог → USDC → CORE + хедж → dual staking Core | **5.13%** native BTC | (Maple $2.98B всего) | 0.40% mgmt + 20% perf > 5%; CTLV на L1; без rehypothecation |
| E2 | **Two Prime Axiom WBTC Vault** (Pareto) | Лендинг публичным компаниям и рейтингованным институтам | **1.5–2%** таргет | $12M first-loss; Pareto $227M кредитов | Мин. 5 WBTC (~$400k); non-US; ICE кастоди, Copper |
| E3 | **Xapo Byzantine BTC Credit Fund** (с Hilbert) | Структурный кредит институтам, без левериджа | **3.5–5%** net | $100M на первом этапе | Accredited; Xapo Bank (Gibraltar) |
| E4 | **Ledn BTC Growth Account** | Фондирование overcollateralized BTC-кредитной книги | **7–9%** заявлено | (розничный BTC-lending ~$3B рынок) | PoR, open-book; ставки для BTC де-факто ниже стейблов |
| E5 | **Nexo BTC Earn** | Omnibus, ставка зависит от холда NEXO | **6.5%** | $2.04B loan book | Контрагентский риск |
| E6 | **YouHodler** | Flexible Yield Account | **7%** | н/д | LTV до 90% на займах |
| E7 | **Bitfinex Lending Pro (BTC)** | P2P margin funding | **1.98%** до 15% fee | н/д | Единственная прозрачная ставка «спроса на заём BTC» |
| E8 | **Cantor Fitzgerald Bitcoin Financing** | Институциональный BTC-кредит | — | $2B программа | Anchorage + Copper |
| E9 | **Galaxy** | CeFi lending | — | $1.8B loan book | |
| E10 | **Tether** | Secured loans | — | **$14.6B** (59.9% CeFi) | Крупнейший кредитор |
| E11 | **Anchorage / Mezo Prime** | см. A5 | | | |
| E12 | **Sygnum MultiSYG** (с Debifi) | BTC-backed loans в 3-of-5 multisig | — | запуск H1 2026 | Институты/HNWI; без rehypothecation |
| E13 | **Firefish** (Прага) | P2P: инвесторы фондируют BTC-backed займы | инвестор **до 12%** (в EUR/стейблах) | н/д | Не BTC-ном. |
| E14 | **Debifi / Hodl Hodl Lend** | P2P multisig | — | | Non-custodial |
| E15 | **Lava** | DLC-займы на L1 | заёмщик 5–6.5% APR | | Non-KYC, 1–3 мес. |

---

## F. Продажа волатильности / опционные и структурные продукты

### F1. DeFi

| Продукт | Механика | Доходность | Размер |
|---|---|---|---|
| **Lombard LBTC (Bitwise)** | Off-chain covered call | 2.5% net таргет | $690M |
| **Midas mRe7BTC** | Options premia + staking | н/д | малый |
| **Rysk V12** (HyperEVM) | On-chain covered calls / cash-secured puts; Opyn-based | «high sustainable» | **$57M**; $240M+ notional |
| **Hyperion DeFi vault** (на Rysk) | Институц. vol-income (HYPE LST + стейблы) | — | balance sheet |
| **Hegic** | Peer-to-pool опционы WBTC | — | $9.9M |
| **Thetanuts** | Structured vaults, аукционы QCP/Paradigm | — | малый |
| **StakeDAO / Cega / Struct / Derive** | DOV / knock-in-out | — | малые |
| **PsyOptions** (Solana) | BTC/ETH опционы | — | $0.6M |
| **fx Protocol** | Leverage/stable на WBTC | — | $126M |

### F2. CeFi структурные

| Продукт | Механика | Доходность | Заметка |
|---|---|---|---|
| **Binance Dual Investment** | Sell-high (call) / Buy-low (put), короткий тенор | **15%+ APR**; промо 20–35%; Yield Arena до 29% | Non-principal-guaranteed; BitcoinYield трекает «Binance Earn options» 8.29% / $45.5M |
| **OKX Dual Investment** | То же; early redemption | ~10–30% APR по тенорам | |
| **Bybit Dual Asset** | То же | | |
| **Matrixport Dual Currency / Daily Dual-Ccy** | Daily observation | «выше Fixed Income» | Первый daily-DCI |
| **Matrixport BTC-U Range Sniper** | Range-accrual | до **40%** | Base yield во всех сценариях |
| **Matrixport Fixed Income (BTC)** | Фикс. тенор | до **15%** | |
| **Matrixport Flexi Saving** | Гибкий | до 6% | |
| **XBTO «Diamond Hands»** (Arab Bank Switzerland) | Options-based accumulation | **~5%** | Bermuda; HNWI |
| **Deribit / Amber / SignalPlus** | Структурные ноты | индивидуально | |
| **JPMorgan Bitcoin structured notes** | Autocall/participation | условная | TradFi |

### F3. ETF / биржевые фонды (доходность в USD, экспозиция BTC)

| Тикер | Эмитент | Механика | Дистрибуция | AUM / TER |
|---|---|---|---|---|
| **BTCI** | NEOS Bitcoin High Income | Опционный overlay на BTC ETP | **33% trailing** | **$1.3B** |
| **XBCI** | NEOS Boosted Bitcoin High Income | Levered overlay | — | новый (2026) |
| **BTCC** → «Bitcoin High Income» (с 17.09.2026) | Grayscale | Covered call на GBTC | 47.6% distr.; **100% ROC** по 19a-1; SEC yield 2.03% | |
| **BPI** | Grayscale Bitcoin Premium Income | Covered call на GBTC/BTC mini | 18.9% | TER 0.66% |
| **YBTC** | Roundhill | Первый US covered-call BTC ETF; недельные | — | TER 0.96% |
| **YBIT** | YieldMax | Call spreads на IBIT | — | $41.85M; TER 1.02% |
| **MAXI** | Simplify Bitcoin Strategy PLUS Income | Фьючерсы + опционный overlay | — | TER 6.10% |
| **BAGY** | Amplify Bitcoin Max Income Covered Call | Weekly calls, цель 30–60% премии | — | |
| **BTCY** | Purpose (Канада) | Covered call на 10–50% портфеля, до 25% левериджа | месячно | TER 1.74% |
| **HBIX / HBTE** | Harvest (Канада) | Covered call на BTC ETF / майнеров | месячно | |
| **BTCX** | CI Galaxy (Канада) | Спот, без yield | — | |
| **Calamos CBOJ и др.** | Protected BTC | Defined outcome, не yield | — | |

**Замечание:** ETF-«доходность» 18–47% — это распределение опционных премий в USD с капом апсайда; экономически часто return of capital (см. BTCC). Не сопоставимо с BTC-ном. 1–5%.

---

## G. Централизованные площадки: биржи, необанки, банки

### G1. Биржевые Earn на BTC (flexible, если не указано)

| Платформа | BTC APY | Условия | Заметка |
|---|---|---|---|
| **Kraken Auto Earn** | **0.02%** | weekly | Отдельно: Bitcoin Vault 0.88–1.8% (A1), BTC Staking via Babylon |
| **Krak** (Kraken app) | 0.1% | weekly | |
| **Coinbase** | — | | Не платит на BTC; loans через Morpho (см. I) |
| **Binance Simple Earn** | 0.9–2.7% (ист. конец 2024); текущая — на дашборде | flexible/locked 30–120d | Промо на стейблах до 8–20%; Dual Investment 15%+ |
| **Bitget Earn** | 1–3%; bgBTC Onchain **3%** | flexible | |
| **KuCoin Earn** | до 3% | | |
| **OKX Simple Earn / On-chain Earn** | н/д (BTC низкая) | | Dual Investment |
| **Bybit Easy Earn / Wealth Mgmt** | н/д | | Dual Asset, Advanced Earn |
| **Crypto.com Earn** | **0.2%** (Tier 1 до $3k; далее ×0.5, ×0.3) | weekly | |
| **Gate GTBTC** | внутренний earn | | $279M |
| **Bitfinex Lending Pro** | **1.98%** (до 15% fee) | P2P funding | |
| **Coinmetro** | 1.8% | end of term | |
| **Phemex** | 1% | | |
| **EXMO** | 0.2% | | |
| **Bitvavo** | 0.02% | flex | EU |
| **Backpack** | 0.02% | dynamic | |
| **Bitpanda** | н/д для BTC | | |
| **MEXC / HTX / BingX** | промо-ставки | | BingX Dual Investment |
| **ether.fi Cash** | 0.65% | | |
| **Axal** | 2% | non-custodial роутер | |
| **Tuyo** | 1.6% | | |
| **Nebeus / CoinDepo / EarnPark / Lune / Clapp** | 5–21.5% | daily | **Высокий контрагентский риск**; не подтверждённые модели |
| **CoinRabbit** | 0.3% | no-KYC | |

*(Средняя по агрегатору CoinInterestRate по 20 площадкам: 4.19%; медиана — около 1%.)*

### G2. Необанки / CeFi-лендеры / банки

| Платформа | BTC-продукт | Ставка | Заметка |
|---|---|---|---|
| **Xapo Bank** (Гибралтар, UK passport) | BTC Savings | **0.25%** | USD Savings 3.35% выплачивается в BTC; Byzantine BTC Credit Fund 3.5–5% |
| **Nexo** | BTC Earn | 6.5% | зависит от NEXO-холда |
| **Ledn** | BTC Growth | 7–9% заявлено | |
| **YouHodler** | Flexible Yield | 7% | |
| **Wirex X-Accounts** | Earn | н/д | |
| **SwissBorg** | Earn | н/д для BTC | |
| **Sygnum Bank** | Staking 4–10% (не BTC); MultiSYG BTC-loans; BTC Alpha Fund | см. D3/E12 | FINMA; AuM CHF 4.5B |
| **AMINA Bank** | Кастоди/стейкинг | н/д для BTC | AuM CHF 3.5B |
| **Bitcoin Suisse** | Vault + staking (ETH/SOL) | нет BTC-yield | |
| **Arab Bank Switzerland** | BTC yield (XBTO Diamond Hands) | ~5% | HNWI |
| **Laser Digital (Nomura)** | Tokenized BTC yield fund | ~5% | см. D5 |
| **Anchorage Digital** | Mezo Prime кастоди; credit | — | |
| **Ledger Wallet «BTC Yield»** | → LBTC (Lombard/Figment) | 2.5%+ | Self-custody UX |
| **Xverse / Leather** | Stacks: dual stacking, Zest | 0.4–4% | Self-custody |
| **Strike** | BTC loans (не earn) | 9.5% APR заёмщику | |
| **Unchained** | Business loans | 11.49%+ APR | Consumer закрыт с 01/2024 |
| **Arch** | Loans | 7.25–8.49% APR | |
| **SALT** | Loans 1/3/5 лет | 8.95–14.45% APR, LTV 20–70% | |
| **Figure** | Loans | LTV 75% | |
| **Milo** | BTC-mortgage | — | |
| **CoinLoan / Hodlnaut / Vauld / Celsius / BlockFi / Voyager / Gemini Earn** | — | — | **Мёртвые (2022–23)** — исторический бенчмарк контрагентского риска |

---

## H. Смежное: BTC-обеспеченный USD-кредит (доход в USD, обеспечение BTC)

| Продукт | Механика | Доходность (USD) | Размер |
|---|---|---|---|
| **Strategy STRC («Stretch»)** | Perpetual preferred, дивиденд semi-monthly, ставка пересматривается ежемесячно | **12%** (11.5–13% eff.) | Digital Credit outstanding **$13.5B** (STRF/STRK/STRC/STRD) |
| **Strategy STRF / STRK / STRD** | Senior → junior preferred | 10% / 8% conv. / 10% | |
| **Saturn sUSDat** | USDat (T-bills) → sUSDat держит STRC через кастодиан | **11%+** | $141M; 3–7d exit queue |
| **Strategy «BTC Yield» KPI** | Не продукт: прирост BTC на акцию | 13.3% YTD (май-2026) | 843 738 BTC |
| **Hermetica hBTC (STRC-leg)** | Часть дохода hBTC — из STRC | | см. A4 |

**Почему это важно:** STRC/Saturn — прямой конкурент за «доходность, обеспеченную биткоином» в глазах TradFi-аллокатора: 11–12% в USD против 1–5% в BTC.

---

## I. Обратная сторона рынка: где берут кредит под BTC (ваши контрагенты)

| Платформа | Объём | Ставка заёмщику | LTV | Заметка |
|---|---|---|---|---|
| **Coinbase Loans (Morpho/Base)** | >$1.2B originated; >$800M активных; $3.04B cbBTC залога | 4.81% | до 86% LLTV; лимит $5M | Кураторы Steakhouse/Gauntlet |
| **Morpho прочие BTC-рынки** | $2.38B занято всего | 2–5% | 77–86% | |
| **Aave v3** | $5.27B BTC заведено | 3.6–4% USDC | 70–80% | |
| **Tether** | $14.6B secured loans | н/д | | |
| **Nexo** | $2.04B | | | |
| **Galaxy** | $1.8B | | | |
| **Ledn** | (рынок ~$3B) | 9–12% | 50% | |
| **Strike** | | 9.5% | | |
| **Arch / SALT / Figure / Unchained** | | 7.25–14.45% | 40–75% | |
| **Mezo MUSD** | $487M lifetime | **1% fixed** | 90% | |
| **Sygnum MultiSYG** | H1 2026 | bank-grade | | |
| **Templar** ($30M) | Native BTC → USDT на ETH/NEAR, MPC, без KYC | | | $100M lending commitments |
| **Surge Credit** | Native BTC Taproot vault → USDC на Base | | | $1.3M |
| **Chainflip Lending** | Cross-chain native BTC | | | $4.5M |
| **Liquidium** (ICP) | Native BTC lending | | | $4M |
| **Granite** (Stacks) | sBTC → стейбл-займы | | | $7M |
| **Zest / Sovryn / Money on Chain** | см. выше | | | |
| **Lava / Debifi / Hodl Hodl / Firefish** | P2P | 5–12% | | |

---

## J. Сводка по числам

| Метрика | Значение |
|---|---|
| Всего продуктов в каталоге | **~230** позиций (A–I) |
| Прямых аналогов архетипа (★) | **15**, из них с TVL > $50M — 4 (Kraken, Bitget, Mezo, Avalon) |
| BTC в обёртках on-chain | $20.3B (46 эмитентов) |
| BTC в денежных рынках | $13.55B |
| Занято под BTC-залог (Morpho) | $2.38B из $4.93B |
| Стейкинг/рестейкинг BTC | ~$5.5B (Babylon $3.32B + LST/LRT) — **сжимается** |
| Basis-протоколы | $7.58B (43) |
| BTC income ETF (US) | BTCI $1.3B — крупнейший; сегмент synthetic income $225B+ всего |
| Digital Credit (Strategy) | $13.5B |
| CeFi loan books | $73.6B (Tether 59.9%) |
| Медианная BTC-ном. доходность «безопасных» продуктов | **~1–2.5%** |
| Диапазон «5%+» | только базис (D), институц. кредит (E1/E3–E6), эмиссия (C10/C11/C17) и опционы (F) |
