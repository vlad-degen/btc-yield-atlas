# Каталог BTC-yield продуктов и волтов
### Полный реестр: похожие продукты, BTC-волты, CeFi/банки/фонды/ETF, стейкинг, опционы, кредиторы

**Дата снимка:** 20 сентября 2026 · BTC $81 178 (закрытие Binance) · **ревизия 21.09.2026** — строки со звёздочкой ★ и отмеченные «(испр.)» перепроверены ончейн и по первоисточникам; подробности в [BTC-Carry-Vaults-Dossiers.md](BTC-Carry-Vaults-Dossiers.md) и [AUDIT.md](AUDIT.md)
**Дополняет:** [BTC-Yield-Market-Research.md](BTC-Yield-Market-Research.md) (аналитика, юнит-экономика, выводы)
> **Обновление v3 (22.09.2026).** Каталог — срез 20–21.09 до ончейн-разборов v3. Актуальная карта рынка (95 825 BTC, $7,78 млрд без двойного счёта; кэрри — 9 278 BTC, 9,7%) и топ-5 кэрри-продуктов — в [REPORT.md](REPORT.md) и [research/top5/](research/top5/). Изменилось: Yield Basis — кэрри-гибрид №2 (1 326 BTC); mHyperBTC — кэрри (C1), ~3,2% в год; Avalon CeDeFi — контекст C0; Maple BTC Yield свёрнут 19.11.2025; Bitget — 2,34% с запуска, один омнибус-депозитор, стимулы из горячего кошелька Bitget; ether.fi — комиссия 0% ончейн с 24.08.2026.
**Источники размеров:** DefiLlama (protocols/yields), Morpho API, публичная отчётность. Доходности — на дату, переменные, если не сказано «fixed».
**Обозначения:** ★ = прямой аналог вашего архетипа (BTC-залог → заём стейбла → размещение → доходность в BTC); ◐ = частично (залог BTC / кэрри как один из компонентов); TVL — в USD; «BTC-ном.» = доходность выплачивается в BTC.

---

## A. Прямые аналоги ★ — «залог BTC → заём стейбла → доходность» с управлением позиции

| # | Продукт | Стек / механика | Доходность (BTC-ном.) | Размер | Доступ · кастоди | Комментарий |
|---|---|---|---|---|---|---|
| A1 | ★ **Kraken Bitcoin Vault** («Advanced Strategies BTC», sentoraBTC) | Kraken → kBTC (1 EOA Kraken) → Ink → Veda BoringVault → **Sentora** → Morpho kBTC/RLUSD и kBTC/PYUSD (5 395 kBTC, долг $278M, LTV 64%) + Aave и Morpho WBTC/USDT (437 WBTC, 20M USDT) + LP Uniswap WBTC/kBTC. 68% kBTC-долга → Sentora Vault V2 (кредиторы тех же рынков), 32% → Hastra PRIME. Без рекурсии на BTC | **1.41%** с запуска, **1.03%** за 30 дней (реклама до 2.5%; лендинг 0.97%) | ~6 575 BTC ≈ $565M (21.09); долг $298M | Розница, мин. 0.00006 BTC; кошелёк на Ink; вывод 3 дня; нет UK/UAE/AU; США — да | 25% валового (ончейн 2500 → 3333 bps 24.08). ~82% кэрри с запуска (~90% при текущих ставках) — субсидии Merkl. Лимиты займа заполнены (испр.) |
| A2 | ★ **Kraken DeFi Earn — Advanced Strategies USDC и др.** | Три USDC-волта на тех же рельсах Veda и Sentora; BTC-волт «Advanced Strategies BTC» = A1 (не отдельный продукт) | — | $611M по 4 волтам (июль 2026, Sentora) | Розница (48 штатов США, Канада, ЕЭЗ) | Запуск 26.01.2026; вначале Balanced и Boosted курировал Chaos Labs (испр.) |
| A3 | ★ **Bitget bgBTC Onchain Earn** | Bitget → bgBTC → Morph → Gauntlet Aera → Morpho bgBTC/USDC (LLTV 77%): 801.7 bgBTC → $43M USDC (LTV 61,9–64,1%) → Gauntlet USDC (gtusdc, 82% шэров) → **обратно в тот же рынок** | до 3% (реклама); реализовано 2,34% с запуска, пользователю — 1,70% | ~$65M в волте; резервы bgBTC $121.8M | Один омнибус-кошелёк Bitget (99,9999% долей); пользователи Bitget — по квотам | Петля, как у Kraken; все стимулы — из горячего кошелька Bitget; комиссии 0/0/0 ончейн; выход T+4 бесплатно или мгновенно за 0,1% (v3) |
| A4 | ★ **Hermetica hBTC** (Stacks) | BTC → sBTC → Zest (цель LTV 50%) → заём **USDh** → sUSDh. **Стратегия свёрнута 18.06.2026**, депозиты выключены с 24.08; USDh теперь обеспечен STRCx | было 5.60% (7d, апрель–май); сейчас **~1%** | 46.9 BTC / $4.0M; 2 адреса держат 86% | Hermetica Labs (Панама); выход 72 ч + ~80 мин | Perf 10% по документации, ончейн 0 (испр.) |
| A5 | ★ **Mezo Prime / Mezo Earn** | BTC (Enclave у Anchorage → triparty-минт) → MUSD под **1% фикс** (MCR 110%) → волты. Свой L1 (21 PoA-валидатор) | veBTC 2.77% (APR голосования в MUSD, не MEZO) | Earn $69.7M (92% — Bullish); MUSD 30.4M (49% бутстрап, 48% Bullish, 3% розница) | Институты + розница | Safe 5-of-9 без таймлока; лок Bullish на 500 BTC до 08.10.2026 (испр.) |
| A6 | ◐ **Avalon Labs** (USDa / sUSDa / Superearn) | FBTC → lfBTC (обёртка Avalon) → **USDT**-долг $47.6M (LTV ~43%, статичная позиция); USDa 7–8% фикс; Superearn → горячий кошелёк Binance | не наблюдается | CeDeFi $110M; Superearn $115M; USDa $146M | TBT Global Ltd (BVI) | **DefiLlama обнулил TVL USDa 23.07.2026** («USDa is dead»); не «крупнейший BTC-CDP» (испр.); в карте рынка v3 — контекст C0: пул четырёх институциональных Safe, не продукт с внешними депозиторами |
| A7 | ★ **Acre acreBTC** (Thesis-спинофф; Re7 на Midas) | BTC → tBTC → macreBTC1 → mRe7BTC / заём → mRe7YIELD | заявлялось ~14%; **реализовано −1.24%** | закрыт; остаток 3.63 tBTC | Hectare Tech Ltd (BVI); вывод 14 дней (Midas) + до 72 ч (мост) | Уценки 11.05 и 11.06.2026; комиссия за выход 0.25% до 15.05 (испр.) |
| A8 | ★ **ether.fi Liquid BTC** | Veda-волт, стратегия Nonce: WBTC + cbBTC на Spark → PYUSD + USDC (LTV 57–62%) → Cap stcUSD + Sentora Paypal USD Main | **1.96%** за год (1,84% в год с запуска); 1.37% за 30 дней | 231,6 BTC ≈ $18,8M (ether.fi Liquid всего $433M) | Розница (не US/CA/UK) | 1% платформы по fact sheet; ончейн 0% с 24.08.2026 (8 смен); 0% за успех; админ — Safe 4-of-6 без таймлока (v3) |
| A9 | ◐ **Lombard Bitcoin Earn (BTCe) и LBTCv** | BTCe — обёртка над LBTCv (Veda, менеджер Sentora). 582 LBTC — слэшируемое покрытие займа Flow Traders на Cap (Symbiotic) — **first-loss, не кэрри** | LBTCv **0.98%** за год; BTCe ~1.5% на кредитной ноге | LBTCv 874 (~$72M); BTCe 445 (~$38M); «$1B / 38.5k» — кумулятивно | Розница | Вывод до 14 дней; комиссии BTCe не раскрыты (испр.) |
| A10 | ★ **Hyperbeat Ultra UBTC (hbBTC)** | UBTC (Unit, MPC 2-of-3) → August/Upshift → UltraYield (Edge Capital) | ~2.1% в год за 508 дней; **0% с июля** | $0.77M (пик $21.8M); UBTC-рынки Morpho $5.05M | **Только вывод**, скрыт | 15% + 1.5%; очки без Felix (испр.) |
| A11 | ★ **Midas mHyperBTC** (Hyperithm) | NAV-токен; кэрри: cbBTC в залог на Morpho и Spark → USDT/USDS → USD-волты (~68% NAV), плюс CEX-базис и LP; в карте рынка v3 — C1, №4 | ~3,2% в год с первого минта 24.11.2025; 90 дней — 1,65%; 30 дней — 1,90% | 354,1 BTC-экв. (~$29M); залог в Morpho (USDC под 9.8%) | KYC, эмитент Midas Software GmbH | Требования субординированы; Hyperithm — акционер Midas (испр.) |
| A12 | ★ **Midas mRe7BTC** (Re7) | BTC-деноминированные рыночно-нейтральные стратегии | **−0.59%** с запуска | $0.8M | Ethereum, Starknet (Vesu) | **Не ring-fenced** (эмитент Midas Software GmbH; требования субординированы) (испр.) |
| A13 | ◐ **Midas mBTC** | NAV-токен | NAV без изменений с 10.2025 | $28k | — | Фактически спит; колонка «mBTC» в старой истории APY была mHyperBTC (испр.) |
| A14 | ◐ **BIMA** (USBD) / **Bracket** | USBD → пивот в collar-займы (FalconX, 50% LTV, волты Accountable) | — | BIMA CDP $10.8M; USBD $7.5M; Bracket $0.5M | — | Seed BIMA — лид Portal Ventures; «Binance Labs» — это про Bracket (испр.) |
| A15 | ◐ **Upshift BTC / upLBTC** | upLBTC (куратор Tulipa Capital), Upshift BTC (August + MEV Capital) | upLBTC −0.5% в год на масштабе; Upshift BTC ~3% в год | **Upshift BTC закрыт; upLBTC скрыт** ($11k) | — | Пример петли sUSDe в документации не найден (испр.) |
| A15a | ◐ **Tesseract TESS wBTC** (IPOR Fusion) | WBTC → USDC на Morpho/Aave (LTV ~59%) → **рекурсивные** петли sUSDe/PYUSD, wsrUSD | таргет 2–4% gross; сейчас кэрри отрицательный (3.34% против 4.96%) | $0.04–2M на волт; ~$13.9M во всех 58 волтах | Институты; Tesseract Investment Oy (MiCA CASP) | Все роли — один EOA (EIP-7702); 1% + 30% HWM. «wBTC Dollar Carry» — это BTCD Labs, не Tesseract |
| A16 | ◐ **Zest** (Stacks) + Bitcoin Collateral Vaults | Площадка займа под sBTC (v2: партиционированный риск, частичные ликвидации); BCV — фаза 1 на предподписанных транзакциях с guardian council, BitVM — в фазе 2 (статус в mainnet не найден) | sBTC supply сейчас 0.1–1.2%; 4.13% — среднее Q1; 12.5% — стимулирующая кампания | Zest v2 $73M (занято $15M) + v1 $2.7M | Self-custodial | «1 500+ ликвидаций без bad debt» — самоотчёт; все 59 предложений DAO прошли как `urgent` в обход таймлока (испр.) |
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
| A32 | ◐ **Two Prime Axiom WBTC** (Pareto) | Кредит институтам; **заёмщик — сама Two Prime** | 1.5–2% таргет; 1.61% (эпоха 1) | first-loss 150 WBTC (=«$10–12M») | Мин. 5 WBTC; KYC Keyring; ICE Digital Trust + Copper | «Только не-US» и «через Morpho» не подтверждены (испр.) |

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
| Morpho Arc (Circle) | cirBTC / USDC | $18M | $11M | 0.03% | 86% |
| Morpho Katana | vbWBTC / vbUSDC | $12M | $7M | 2.66% | 86% |
| Morpho Hyperliquid | UBTC / USD₮0 | $2.2M | $1.0M | 7.26% | 77% |
| Morpho Hyperliquid | UBTC / USDe | $0.6M | $0.25M | 8.31% | 77% |
| **Aave v3** (все сети) | WBTC/cbBTC/LBTC/tBTC/FBTC/BTC.b/BTCB | **$5.32B** | н/д (общий пул) | USDC ~3.6–4% | 70–80% |
| **SparkLend** | cbBTC $462M · LBTC $221M · WBTC $171M | $855M | н/д | — | |
| **Compound v3** | WBTC/cbBTC | $605M | н/д | — | |
| **Venus (BSC)** | BTCB $366M · SolvBTC $206M · xSolvBTC $63M | $635M | н/д | — | |
| **JustLend (Tron)** | BTC | $532M | н/д | — | |
| **Fluid** | WBTC | $62M | н/д | — | smart collateral |
| **Tydro (Ink, white-label Aave V3; управляет Ink Foundation)** | kBTC (LTV 85%, LT 87%, занимать можно только USDC) | $93M | ~$67M всего по Tydro | USDC 6.3% | 87%; 85% kBTC — один сторонний EOA; **волта Kraken там нет**; оракул BTC/USD (испр.) |
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
| **Mezo** | MUSD | 1% фикс, MCR 110% (≈90.9% LTV), выпуск 0.1% | **MUSD 30.4M**: 49% бутстрап, 48% Enclaves (Bullish), 3% розница (0.92M); «$2.9M» — залог розничных троувов (испр.) | см. A5 |
| **Avalon** | USDa | 7–8% фикс, CeDeFi, ликвидация на CEX | USDa $145.6M; TVL CDP по DefiLlama ≈ 0 с 23.07.2026 | см. A6 (испр.) |
| **Sovryn Zero** (Rootstock) | ZUSD/DLLR | 0% ставка, разовая комиссия | TVL $21.4M, но ZUSD всего $1.96M (30 троувов) | Старейший BTC-CDP, активность низкая (испр.) |
| **Money on Chain** (Rootstock) | DoC | Dual-token | $22M | |
| **BIMA** | USBD | Пивот в collar-займы | $10.8M TVL; USBD $7.5M | (испр.) |
| **Threshold thUSD** | thUSD | tBTC/ETH залог | $2.2M | |
| **Yala** | YU | BTC → кроссчейн-стейбл | $2.5M | **Взлом $7.64M (14.09.2025), устойчивый депег с 11.2025**, пивот (испр.) |
| **BTCFi CDP** (Bifrost) | | native BTC → стейбл | $7.4M | |
| **Hermetica USDh** | USDh | было: синтетический доллар (funding); сейчас обеспечен STRCx (префы Strategy) | $2.0M | Используется в hBTC (испр.) |
| **Felix** (Hyperliquid) | feUSD | CDP | CDP $35.7M + Vaults $47.5M; feUSD $9.8M; BTC ~5.5% залога | (испр.) |
| **Lista CDP** (BSC) | lisUSD | BTCB залог | $1.9M BTCB | |
| **Bitsmiley / Satoshi Protocol → River** | bitUSD / satUSD | BTC-CDP | River Omni-CDP $107M; satUSD $154.5M (больше USDa) | Satoshi переименован в River; $12M от TRON DAO (01.2026) (испр.) |
| **VETRO** | VUSD / vetBTC | yield-bearing collateral | $0.6M | |
| **Saturn** | USDat / sUSDat | **не** BTC-CDP: USDat backed T-bills, sUSDat = STRC-доходность 11%+ | $141M | см. раздел H |

### B3. Куда размещать занятые стейблы (TVL > $100M)

| Венчур | APY | 30d | TVL | Тип риска |
|---|---|---|---|---|
| Maple USDC | 5.07% | 4.96% | $2.85B | Обеспеч. институц. кредит |
| Sky sUSDS | 3.60% | 3.57% | $4.40B | RWA/T-bills |
| Ethena sUSDe | 4.67% | 4.71% | $1.33B | Базис (депег-риск!) |
| Ondo USDY (Ethereum) | 3.58% | 3.56% | $1.18B | T-bills |
| BlackRock BUIDL (класс Solana) | 3.75% | 3.57% | $993M | T-bills |
| Maple USDT | 4.72% | 4.63% | $688M | |
| Sentora RLUSD v2 (Morpho) | 6.11% (2.62+3.50 rw) | 6.16% | $369M | Стимулы Ripple |
| Sentora Paypal USD Main (Morpho) | 5.07% (2.26 + 2.82 наград) | 5.68% | $431M | Стимулы Merkl от Safe Sentora (спонсор не раскрыт) (испр.) |
| Sirloin USDC (Base) | 5.56% | 5.67% | $426M | |
| Steakhouse USDC (Base) | 4.35% | 4.32% | $428M | |
| Gauntlet USDC Prime (Base) | 4.35% | 4.32% | $420M | |
| Spark USDC (Morpho SPARKUSDC, Base) | 3.90% | 3.88% | $273M | |
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
| **Yield Basis** YB-cbBTC / YB-WBTC / YB-tBTC | 2x LP на кредитной линии crvUSD (в карте рынка v3 — кэрри-гибрид C1, №2; «без IL» — заявление, выход был до −19,5% к книге) | **7.24% / 4.79% / 3.60%** — только застейканные (эмиссия YB, токен −87%); незастейканные за v3 — от −3,0% до +0,6% по цене выхода | $21M / $30M / $14M; протокол $134M с WETH (пик $247M, 15.01.2026); доля депозиторов в BTC-рынках — 1 326 BTC (~$108M) (испр.) |
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
| C2 | **Lombard LBTC** | С 13.08.2026 — **covered call Bitwise** (50–60% обеспечения активно, пассивная часть ничего не зарабатывает) | таргет **2.5% net** | **$690–738M** (пик $2.107B, 12.05.2025; −58% в BTC, −65% в USD) + BTC.b $172M | **20% прибыли стратегии с HWM** (8% — эпоха Babylon). Доступ через Ledger (Figment). Вывод до 10 дней (испр.) |
| C3 | **Solv xSolvBTC / SolvBTC.CORE / BTC+** | LST-агрегатор: Babylon + Core + basis + RWA | xSolvBTC **~4%**; BTC+ 5–8% таргет | SolvBTC $517M; LSTs $78M; Basis $199M | 12 сетей; Venus xSolvBTC $63M |
| C4 | **Bedrock uniBTC** | Babylon LRT + Symbiotic | Symbiotic uniBTC 0.42%; Pendle YT ист. 22% | **$374M** (18 сетей) | |
| C5 | **Lorenzo stBTC / enzoBTC / OTF** | stBTC = Babylon LST; enzoBTC = wrapper; OTF = токенизированные фонды | н/д | enzoBTC $485M; stBTC $0.03M | Пивот в asset management (sUSD1+ $80M) |
| C6 | **PumpBTC** | Babylon LRT | н/д | $28M | |
| C7 | **Core lstBTC** (Maple + BitGo/Copper/Hex Trust) | Dual staking Core: BTC в кастодиане + CORE → награды CORE, выплата в BTC | 5%+ таргет; ончейн стейкинг давал ~1,9% брутто, остальное — путы Core Foundation | Maple BTC Yield свёрнут 19.11.2025 (0 BTC; пик 1 757,85 BTC); lstBTC так и не запущен (supply 0) | Спор Core и Maple урегулирован 22.05.2026; см. E1 и [research/top5/06-maple.md](research/top5/06-maple.md) |
| C8 | **b14g** (Core/Babylon Genesis) | Модульный dual-staking слой | 0.12% | $189–260M | |
| C9 | **Stacks Dual Stacking / sBTC** | sBTC + STX → PoX-награды | база 0.36%; boosted 3.56%; «~3%» таргет | sBTC $199M | Self-custodial на L1 (Stacks BTC Staking — не запущен полностью) |
| C10 | **Starknet BTC Staking** | WBTC/LBTC/tBTC/SolvBTC → security → STRK | **3.80%** (в STRK) | $47M | Эмиссионный |
| C11 | **Botanix stBTC** (Spiderchain) | 50% gas-fees сети в BTC → стейкерам | **34% APR** headline (накопленное); ожидается 5–6% | н/д | Займы <1% APR; 16 операторов (Galaxy, Fireblocks, Alchemy) |
| C12 | **GTBTC (Gate)** | Биржевой BTC-LST | внутренний earn | **$279M** | |
| C13 | **Bitget bgBTC** | Биржевой wrapper + Morpho/Gauntlet | 3% (реклама); реализовано 2,34% с запуска | $114M (резервы) | см. A3 |
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
| D1 | **Coinbase Bitcoin Yield Fund (CBYF)** | Cash-and-carry (спот против деривативов; CME в первоисточниках не назван) | **4–8%** таргет net | ёмкость $1B; AUM, комиссии и результат не раскрыты | Не-US; запуск 01.05.2025; seed Aspen Digital; ежемесячно, уведомление 5 дней; токен-класс на Base (Apex, 19.03.2026) (испр.) |
| D2 | **Coinbase US Bitcoin Yield (USCBYF)** | **Кредит (BTC private credit) + базис** | 4–8% | н/д | US accredited; IRA через iTrustCapital (заявлено) (испр.) |
| D3 | **Starboard Sygnum BTC Alpha Fund** | Направленный BTC + рыночно-нейтральный оверлей (перпы, фьючерсы, опционы) | **8.9%** net за **Q4 2025** (первый полный квартал); таргет 8–10% | 750+ BTC | Кайманы; мин. $100k; ежемесячно; кастоди CopperClearloop и Sygnum; аудитор KPMG (испр.) |
| D4 | **Syntetika hBTC** (Hilbert Capital, Base) | «BTC Basis+»: базис + кривая + короткие опционы + доходный стейбл-залог; NAV Consulting, PoR | **10.25%** (PPS искажён притоками); 2025: **+20.18% net** | $16.1M | cbBTC → hBTC; куратор Tulipa; выход 1–3 недели; комиссии 1.5% + 15% + 10%. Не путать с Hermetica hBTC (испр.) |
| D5 | **Laser Digital (Nomura) Bitcoin Diversified Yield Fund** | Long BTC + market-neutral арбитраж + лендинг + опционы; токенизирован через KAIO | **~5%** таргет | н/д | Cayman; $250k мин.; accredited |
| D6 | **BounceBit CeDeFi** | Базис + продажа путов через CEFFU | пример: 24% брутто (маркетинг) | **$289M — не подтверждено** (DefiLlama: BounceBit Prime $11.4M) | Розница; CEFFU (испр.) |
| D7 | **Solv Basis Trading** | Базис на CEX | н/д | **$201M** (протокол; $488M — сумма пулов) | (испр.) |
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
| E1 | **Maple BTC Yield** | BTC у Copper/BitGo (CLTV) → залог → USDC → CORE + путы → dual staking Core | **5.13%** (H1 2025, заявлено; ончейн стейкинг ~1,9% брутто, остальное — путы Core Foundation) | пик 1 757,85 BTC (14.05.2025); **свёрнут 19.11.2025, 0 BTC**: 85% BTC вернули 66 адресам, 15% удержали до урегулирования | 0.40% + 20% выше 5%; лок 90 дней при запуске, затем раз в два месяца; **спор с Core урегулирован 22.05.2026** (испр.) |
| E2 | **Two Prime Axiom WBTC Vault** (Pareto) | Займы институтам; **заёмщик на Pareto — сама Two Prime** | 1.5–2% таргет; 1.61% факт | first-loss 150 WBTC; Pareto $247M кредитов | Мин. 5 WBTC (~$400k); KYC Keyring; ICE Digital Trust + Copper; SEC RIA (испр.) |
| E3 | **Xapo Byzantine BTC Credit Fund** (менеджер Hilbert Capital) | Короткие займы BTC институтам первого уровня, без плеча и DeFi | **3.5–5%** таргет; **2.94%** текущая | $100M в первой фазе (≈1 232 BTC, оценка карты рынка v3); seed 3 000 BTC (2024) позже не подтверждён — верхняя граница | ~$120k или 2 BTC; Кайманы; ежемесячно, уведомление 30 дней (испр.) |
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
| **BTCI** | NEOS Bitcoin High Income | Опционный overlay на BTC ETP | **36.51% trailing** (SEC yield 1.35%) | **$1.33B** |
| **XBCI** | NEOS Boosted Bitcoin High Income | Levered overlay | — | новый (2026) |
| **BTCC** → «Bitcoin High Income» (с 17.09.2026) | Grayscale | Covered call на GBTC | 40.12% distr.; **100% ROC** по последнему 19a-1; SEC yield 2.14% | AUM **$16.8M**; TER 0.66% |
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
| **Kraken Auto Earn** | **0.02%** | weekly | Отдельно: Bitcoin Vault — реализовано 1.03% за 30 дней, 1.41% с запуска (A1) |
| **Krak** (Kraken app) | 0.1% | weekly | |
| **Coinbase** | — | | Не платит на BTC; loans через Morpho (см. I) |
| **Binance Simple Earn** | 0.9–2.7% (ист. конец 2024); текущая — на дашборде | flexible/locked 30–120d | Промо на стейблах до 8–20%; Dual Investment 15%+ |
| **Bitget Earn** | 1–3%; bgBTC Onchain **3%** (реклама; реализовано 2,34%, пользователю — 1,70%) | flexible | |
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
| **Xapo Bank** (Гибралтар, GFSC) | BTC Savings | **0.25%** (до 2 BTC) | USD Savings 3.35% выплачивается в BTC; Byzantine BTC Credit Fund — таргет 3.5–5%, текущая 2.94% (испр.) |
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
| **Strategy «BTC Yield» KPI** | Не продукт: прирост BTC на акцию | 13.3% YTD (май 2026) — **не перепроверено** | 843 738 BTC — **не перепроверено** |
| **Hermetica hBTC (STRC-leg)** | Часть дохода hBTC — из STRC | | см. A4 |

**Почему это важно:** STRC/Saturn — прямой конкурент за «доходность, обеспеченную биткоином» в глазах TradFi-аллокатора: 11–12% в USD против 1–5% в BTC.

---

## I. Обратная сторона рынка: где берут кредит под BTC (ваши контрагенты)

| Платформа | Объём | Ставка заёмщику | LTV | Заметка |
|---|---|---|---|---|
| **Coinbase Loans (Morpho/Base)** | **$3B+ выдано; $1.3–1.4B активно; 90K+ пользователей**; $3.07B cbBTC-залога на Base | ~4.8% («от 5.1%» на сайте) | до 75% LTV, ликвидация 86%; лимит $5M | Запуск 16.01.2025; $1B — ~01.10.2025; ~97% долга рынка — смарт-кошельки Coinbase; кредиторы — Gauntlet, Steakhouse Prime, Spark (испр.) |
| **Morpho прочие BTC-рынки** | $2.38B занято всего | 2–5% | 77–86% | |
| **Aave v3** | $5.27B BTC заведено | 3.6–4% USDC | 70–80% | |
| **Tether** | $14.6B secured loans | н/д | | |
| **Nexo** | $2.04B | | | |
| **Galaxy** | $1.8B | | | |
| **Ledn** | (рынок ~$3B) | 9–12% | 50% | |
| **Strike** | | 9.5% | | |
| **Arch / SALT / Figure / Unchained** | | 7.25–14.45% | 40–75% | |
| **Mezo MUSD** | MUSD 30.4M (органики ~$0.9M) | **1% фикс** | ≈90.9% | 92% Earn — Bullish (испр.) |
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
| Весь рынок BTC-доходности (нетто, карта рынка v3) | **95 825 BTC ($7,78B)**; кэрри (C1) — 9 278 BTC (9,7%) |
| Прямых аналогов архетипа (★) | **10 строк, 9 уникальных BTC-продуктов** (A2 — USDC-волты Kraken; BTC-волт — это A1). Avalon, Lombard BTCe, BIMA, Upshift понижены до ◐. На масштабе работает **1** (Kraken, ~$565M); > $50M — ещё Yield Basis (~$108M, 1 326 BTC; в каталоге — B4) и Bitget (~$65M). Закрыты или заморожены: Acre, Hermetica, Hyperbeat, Upshift BTC |
| BTC в обёртках on-chain | **~$28.7B** с cbBTC ($8.0B); без cbBTC — $20.7B |
| BTC в денежных рынках | **$13.86B** (DefiLlama yields); без Zest v2 и Accountable — $13,75B (169 406 BTC, контекст C0 карты рынка) |
| Занято под BTC-залог (Morpho) | $2.38B из $4.93B |
| Стейкинг/рестейкинг BTC | нетто $4,77B (58 759 BTC, 61,3% рынка; карта рынка v3); ~$5.5B — gross с двойным счётом Babylon/LST — **сжимается** |
| Basis-протоколы | $7.58B (43) |
| BTC income ETF (US) | BTCI $1.3B — крупнейший; сегмент synthetic income $225B+ всего |
| Digital Credit (Strategy) | $13.5B |
| Кредитование под крипту | $73.6B всего (Galaxy, Q3 2025); CeFi — $24.4B (Tether 59.9% от CeFi) |
| Медианная BTC-ном. доходность «безопасных» продуктов | **~1–2.5%** |
| Диапазон «5%+» | только базис (D), институц. кредит (E1/E3–E6), эмиссия (C10/C11/C17) и опционы (F) |
