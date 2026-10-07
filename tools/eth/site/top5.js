// Top-5 product chapters in the BTC atlas template (reader edition): facts, a numbered money-flow diagram with contract
// links, who can change what, who pays the yield, book and yield charts, holders, events, the risk and exit panel, lesson.
// Hand-written content is dated 2 October 2026 (block 26,108,081) and sourced in research/eth/en/*.md; series come from
// the payload (reader_product_chapters, atlas_top5_risk, top5 CSVs when present).

const ATES='https://etherscan.io/address/',ATMO='https://app.morpho.org/ethereum/';
function atFlowSVG(id,F){const K=['eth','usd','rwa','rew'],e1=t=>esc(t);
 let g=`<svg class="fd" viewBox="0 0 ${F.w} ${F.h}" role="img" aria-label="${e1(F.label)}"><defs>${K.map(k=>`<marker id="${id}-${k}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse"><path class="mk ${k}" d="M0 0L10 5 0 10z"/></marker>`).join('')}</defs>`;
 (F.loops||[]).forEach(l=>{g+=(l.d?`<path class="loop" d="${l.d}"/>`:'')+(l.t?`<text class="lt" x="${l.x}" y="${l.y}" text-anchor="${l.a||'middle'}">${e1(l.t)}</text>`:'');});
 F.edges.forEach(e=>{g+=`<path class="e ${e.k}" d="${e.d}" marker-end="url(#${id}-${e.k})"/>`;});
 F.nodes.forEach(n=>{const L=[];let y=n.y+22;L.push(`<text class="nt" x="${n.x+12}" y="${y}">${e1(n.t)}</text>`);
  (n.s||[]).forEach(t=>{y+=16;L.push(`<text class="${/^[\d$~≈<>−+]/.test(t)?'nv':'ns'}" x="${n.x+12}" y="${y}">${e1(t)}</text>`);});
  if(n.a){y+=15;L.push(`<a href="${n.a[0]}" target="_blank" rel="noopener"><text class="na" x="${n.x+12}" y="${y}">${e1(n.a[1])}</text></a>`);}
  g+=`<rect class="nb${n.hl?' hl':''}" x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" rx="9"/>`+L.join('');});
 F.edges.forEach(e=>{if(e.n)g+=`<g class="bd"><circle cx="${e.bx}" cy="${e.by}" r="10"/><text x="${e.bx}" y="${e.by+3.6}" text-anchor="middle">${e.n}</text></g>`;});
 return g+'</svg>';}
const atL=(u,t)=>`<a href="${u}" target="_blank" rel="noopener">${t}</a>`;
const fdTop=(x,t,s,a,hl)=>({x,y:70,w:170,h:84,t,s,a,hl});
const fdBot=(x,t,s,a)=>({x,y:270,w:170,h:84,t,s,a});

const ATP={
 liquid:{
  facts:[['Depositors own','177,171 ETH','$473M, Ethereum and Optimism'],['Live since','June 2024','Veda vault, run by Nonce for ether.fi'],['Paid, a year','3.37%','2 years; stETH 2.71%; Sep 3.2%'],['Without rewards','3.39%','last year; actual 3.87%; rewards 34% of the lead over stETH'],['Holders','9,304','7,793 Ethereum, 1,511 Optimism'],['Health factor','1.03 / 1.27','ETH loop / weakest dollar loan']],
  sub:'Out along the top, back along the bottom. A fifth of the book is an ETH loop on Aave and Spark (36,821 ETH of equity); the dollar loans are a side sleeve whose largest lender is the same Sentora vault Liquid parks in.',
  flow:{w:1000,h:370,label:'Liquid ETH: deposits become weETH and wstETH, looped against WETH on Aave and Spark; a side account borrows dollars and parks them in Sentora and Cap vaults; staking, interest and rewards raise the share price',
   nodes:[fdTop(10,'You',['ETH, weETH or eETH']),fdTop(210,'Liquid ETH vault',['177,171 ETH','Veda; Nonce runs it'],[ATES+'0xf0bb20865277aBd641a307eCe5Ee04E79073416C','0xf0bb…416C'],1),
    fdTop(410,'ETH loop',['$1.18B weETH/wstETH;','410k WETH borrowed'],['https://app.aave.com/','Aave and Spark']),
    {x:610,y:40,w:170,h:84,t:'Dollar loans',s:['$181M: Aave USDC 13.93%,','Morpho RLUSD, USDC, PYUSD'],a:[ATES+'0x0a42b2f3a0d54157dbd7cc346335a4f1909fc02c','Drone 0x0a42…c02c']},
    {x:810,y:20,w:180,h:56,t:'Sentora RLUSD V2',s:['$55M']},{x:810,y:86,w:180,h:56,t:'Sentora PRIME PYUSD',s:['$50M; 95% home loans']},{x:810,y:152,w:180,h:56,t:'Cap stcUSD',s:['$25M']},
    fdBot(610,'Interest + rewards',['$7.3M a year vs','$14.1M of interest']),fdBot(410,'Staking yield',['weETH and wstETH','on $1.18B']),fdBot(210,'Share price',['0.35% fee; Accountant'],[ATES+'0x0d05d94a5f1e76c18fbeb7a13d17c8a314088198','Accountant']),fdBot(10,'You withdraw',['queue; median 12.6 h,','p90 56 h'])],
   loops:[{d:'M500 70 C500 28 560 28 560 70',t:'loop: borrow WETH, stake, repeat',x:560,y:22,a:'middle'}],
   edges:[{k:'eth',d:'M180 112 H208',n:1,bx:194,by:94},{k:'eth',d:'M380 112 H408',n:2,bx:394,by:94},{k:'usd',d:'M580 100 H608',n:3,bx:594,by:84},
    {k:'usd',d:'M780 82 H795 V48 H808'},{k:'usd',d:'M780 82 H795 V114 H808'},{k:'usd',d:'M780 82 H795 V180 H808',n:4,bx:796,by:200},
    {k:'rew',d:'M900 208 V312 H782',n:5,bx:900,by:250},{k:'rew',d:'M495 154 V268',n:6,bx:495,by:215},{k:'rew',d:'M610 312 H582'},{k:'rew',d:'M410 312 H382',n:7,bx:396,by:294},{k:'eth',d:'M210 312 H182',n:8,bx:196,by:294}]},
  steps:[`You deposit ETH, eETH or weETH into ${atL(ATES+'0xf0bb20865277aBd641a307eCe5Ee04E79073416C','the vault')}, a Veda BoringVault on Ethereum with shares also on Optimism (ether.fi Cash). 177,171 ETH on 2 October.`,
   `The vault holds weETH and wstETH and loops them on ${atL('https://app.aave.com/','Aave')} and ${atL('https://app.spark.fi/','Spark')}: $1.18B of collateral, 410,134 WETH borrowed on Aave and 31,042 on Spark, health factor 1.027. This is 23% of all WETH debt on Aave Ethereum.`,
   `A side account (${atL(ATES+'0x0a42b2f3a0d54157dbd7cc346335a4f1909fc02c','Drone')}), the vault itself and a ${atL(ATES+'0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3','loan manager')} borrow $181M of dollars: $64.6M USDC on Aave at 13.93%, $12.0M USDT, $70.2M RLUSD and $30.7M USDC on ${atL(ATMO+'market/0xea4bfb18df0ee6bffb7b3f0270899a8adb92ab6b684709634','Morpho weETH markets')}, $3.6M PYUSD on Spark.`,
   `The dollars go to Sentora ${atL(ATMO+'vault/0x6dC58a0FdfC8D694e571DC59B9A52EEEa780E6bf','RLUSD Main V2')} ($55M; it lends back into the weETH/RLUSD market Liquid borrows from, and 53% of it is Kraken's kBTC loans), Sentora PRIME PYUSD ($50M; 95% PRIME home-equity credit) and Cap stcUSD ($25M).`,
   `Interest and Merkl rewards come back: about $7.3M a year against $14.1M of interest at 2 October rates. The rewards trace to wallets fed straight from the RLUSD and PYUSD mints.`,
   `The ETH loop earns staking yield on $1.18B of weETH and wstETH against the WETH borrow rate. Over two years it netted +2,499 ETH, only +68 ETH more than the same ETH unlevered: the spread was negative in 33 of 104 weeks.`,
   `The share price rises: 6.85% over two years (3.37% a year) against 5.49% for stETH. Fee 0.35% a year; it has changed 12 times.`,
   `You withdraw through the queue: 2,822 paid requests, median 12.6 hours, longest 12 days.`],
  pays:[['ETH loop','+2,499 ETH over two years, +68 ETH more than unlevered (+0.02 pp a year); two rate spikes erased it'],['Dollar legs','About −$6.8M a year at 2 October rates: $14.1M of interest, $4.7M of base yield, $2.6M of rewards'],['Rewards','Merkl RLUSD and PYUSD: $2.73M a year on 2 October (0.58% of the book), from the issuers’ side; 34% of the lead over stETH last year'],['Fees','0.35% a year on 2 October; 2,130.6 ETH paid to the platform in 19 claims'],['Unexplained','+1.5 pp a year our model cannot assign: other strategies and timing'],['Depositors got','3.37% a year over two years; stETH 2.71%']],
  events:[['Jun 2024','Vault starts; first WETH loop on Aave','Share issuance from 11 June'],['Aug 2025','First dollar loan: $47M USDC on Aave','Repaid in October'],['Jun 2026','Morpho RLUSD loans via a loan manager','Main vault adds RLUSD and USDC in July'],['Aug 2026','Sentora RLUSD V2 deposits begin','Book +51k ETH in August'],['25 Sep 2026','$18M PYUSD loan against PRIME into a PRIME vault','Negative after funding under every withdrawal rule']],
  lesson:'Neither leg explains the return: ask for a P&L by leg, and never borrow USDC at 14% to park at 3%.'},
 yieldbasis:{
  facts:[['Depositors own','10,426 ETH','$28M, Ethereum'],['Live since','May 2026','current pool; an earlier one ran from January'],['Paid, unstaked','−2.96%','90 days, a year; staked in the gauge +1.69%'],['Admin fee','40.5%','rises with the staked share; none taken since 20 Jul'],['Owners','407','332 addresses; top owner 21.8%'],['Loan','1:1','27.8M crvUSD at 10%; no liquidation']],
  sub:'All on Ethereum. The borrowed crvUSD never leaves the pool; trading fees pay the loan.',
  flow:{w:1000,h:370,label:'YieldBasis WETH: your WETH and an equal crvUSD loan from Curve go into one WETH/crvUSD pool at 2x; traders pay fees; gains less costs raise the shares',
   nodes:[fdTop(10,'You',['WETH']),fdTop(210,'YieldBasis WETH',['10,426 ETH; LT shares'],[ATES+'0x2b9c9f3bdceb5d8e36a4704f08a78fca53343cea','LT 0x2b9c…3cea'],1),{x:430,y:40,w:190,h:100,hl:1,t:'Curve WETH/crvUSD',s:['your WETH + equal crvUSD,','2x; re-levered by the AMM'],a:[ATES+'0x5f8d24f33cc5a1d5d1bf012261e6a2214c92233c','AMM 0x5f8d…233c']},
    {x:680,y:40,w:180,h:84,t:'Curve credit line',s:['27.8M crvUSD at a','fixed 10%']},{x:680,y:176,w:180,h:64,t:'Traders',s:['fees: 9.19% a year','on twice the debt']},
    fdBot(430,'Pool gains',['fees less re-levering','costs and 10% admin']),fdBot(210,'Your shares',['unstaked: fee value;','staked: YB emissions']),fdBot(10,'You exit',['at pool value;','1% preview: 104 WETH'])],
   edges:[{k:'eth',d:'M180 112 H208',n:1,bx:194,by:94},{k:'eth',d:'M380 100 H428',n:2,bx:404,by:84},{k:'usd',d:'M680 82 H622',n:3,bx:651,by:64},{k:'rew',d:'M680 208 H560 V142',n:4,bx:620,by:208},{k:'rew',d:'M500 140 V268',n:5,bx:500,by:205},{k:'rew',d:'M430 312 H382',n:6,bx:406,by:294},{k:'eth',d:'M210 312 H182',n:7,bx:196,by:294}]},
  steps:[`You deposit WETH into ${atL(ATES+'0x2b9c9f3bdceb5d8e36a4704f08a78fca53343cea','the WETH market')} and get LT shares; 10,426 ETH on 2 October.`,`The market borrows an equal amount of crvUSD from Curve's credit line (27.8M at a fixed 10%) and puts both into ${atL(ATES+'0x5f8d24f33cc5a1d5d1bf012261e6a2214c92233c','one Curve pool')} at 2x.`,`The loan never leaves the pool; its interest is paid into it.`,`Traders pay fees: 9.19% a year on twice the debt, enough to cover the 10% loan.`,`Gains, less the cost of re-levering as ETH moves and a 10% admin fee, accrue to the pool.`,`Unstaked shares get the fee value; shares staked in the gauge give that up for YB emissions.`,`You exit at the pool's value: a 1% exit would have got 104 WETH on 2 October.`],
  pays:[['Traders','Swap fees: 9.19% a year on the pool, against 10% on the crvUSD loan'],['YB token','$504k a year of emissions to staked shares: the whole return of a gauge staker (+1.69% vs −2.96% unstaked, 90 days)'],['Fees','Admin fee 40.5% of gains on 2 October, rising with the staked share; none taken since 20 July because the staked side is below its high-water mark'],['Depositors got','Unstaked −0.69% over 94 days against +0.57% for stETH']],
  events:[['Jan 2026','An earlier WETH pool runs','Different contract; history not merged'],['May 2026','Current pool funded','641 ETH at month-end'],['Aug 2026','Peak 12,512 ETH','Debt $30.5M'],['Sep 2026','10,616 ETH','Unstaked share trails stETH']],
  lesson:'Trading fees can carry a dollar loan; whether the depositor beats stETH depends on who gets the rewards.'},
 'lido-earn':{
  facts:[['Depositors own','83,309 ETH','$222M; Earn ETH holds stRATEGY'],['Live since','Nov 2025','stRATEGY; Earn ETH later'],['Paid, a year','3.06%','Sep, annualised; stETH 2.25%'],['Without rewards','3.14%','90 days: no rewards in the price'],['Holders','2,500','Ethereum'],['Health factor','1.035 / 2.12','ETH loops / USDT account']],
  sub:'Mostly a wstETH loop. A separate account borrows USDT and parks it in Lido’s own dollar vault, of which it is half.',
  flow:{w:1000,h:370,label:'Lido Earn ETH: deposits go into stRATEGY, which loops wstETH against WETH on Aave and Spark and runs a USDT account parked in earnUSD; staking and interest raise the share price',
   nodes:[fdTop(10,'You',['ETH, stETH or wstETH']),fdTop(210,'Earn ETH',['83,309 ETH;','Mellow Core vault'],[ATES+'0xBBFC8683C8fE8cF73777feDE7ab9574935fea0A4','0xBBFC…a0A4'],1),fdTop(410,'stRATEGY',['84,664 ETH; three','loop accounts']),
    {x:610,y:30,w:180,h:84,t:'wstETH loops',s:['355k WETH borrowed on','Aave and Spark; HF 1.035']},{x:610,y:130,w:180,h:70,t:'USDT account',s:['$25.6M at 4.33%'],a:[ATES+'0x181cb55f872450d16ae858d532b4e35e50eaa76d','0x181c…a76d']},
    {x:820,y:130,w:170,h:70,t:'earnUSD',s:['4.80%; Lido Earn','owns 48.5% of it']},
    fdBot(610,'Staking + interest',['wstETH yield; earnUSD','pays 0.47 pp over cost']),fdBot(410,'Fees',['15% performance','+ 0.20% a year']),fdBot(210,'Share price',['3.06% a year in Sep']),fdBot(10,'You withdraw',['queue; paused 27 days','in April 2026'])],
   edges:[{k:'eth',d:'M180 112 H208',n:1,bx:194,by:94},{k:'eth',d:'M380 112 H408',n:2,bx:394,by:94},{k:'eth',d:'M580 90 H608',n:3,bx:594,by:74},{k:'usd',d:'M580 140 H595 V165 H608',n:4,bx:592,by:182},{k:'usd',d:'M790 165 H818',n:5,bx:804,by:148},
    {k:'rew',d:'M905 200 V312 H782',n:6,bx:905,by:250},{k:'rew',d:'M610 312 H582'},{k:'rew',d:'M410 312 H382',n:7,bx:396,by:294},{k:'eth',d:'M210 312 H182',n:8,bx:196,by:294}]},
  steps:[`You deposit into ${atL(ATES+'0xBBFC8683C8fE8cF73777feDE7ab9574935fea0A4','Earn ETH')}, a Mellow Core vault: 83,309 ETH on 2 October.`,`Earn ETH holds stRATEGY (84,664 ETH), Lido's November 2025 strategy vault. Count it once.`,`Three stRATEGY accounts loop wstETH against WETH on Aave and Spark: 355,217 WETH borrowed, health factors 1.035 to 1.039.`,`A fourth (${atL(ATES+'0x181cb55f872450d16ae858d532b4e35e50eaa76d','0x181c…a76d')}) borrows $25.6M USDT on Aave and Spark at 4.33%.`,`The USDT goes into earnUSD, Lido's own dollar vault, which paid 4.80%. Lido Earn owns 48.5% of earnUSD.`,`Staking yield on the loops and the earnUSD spread come back.`,`Fees: 15% of performance plus 0.20% a year.`,`You withdraw through a queue. In April 2026 it was paused for 27 days after the rsETH exploit; the DAO burned 144.8 ETH of its own shares to cover the loss.`],
  pays:[['ETH loops','wstETH staking yield less the WETH borrow rate on 355k WETH'],['USDT sleeve','earnUSD 4.80% against 4.33% of interest: +0.47 pp on $25.6M; a 5M USDT loan on 29 Sep cleared +1,401 USDT in four days'],['First-loss','Lido DAO set aside $3M of wstETH for Earn ETH (Feb 2026) and burned 144.8 ETH in May'],['Control','No timelock on any key: a 5-of-8 Safe can upgrade every core contract at once; fees went from 0 to 10% + 1% to 0 to 15% + 0.2% between July and September'],['Fees','15% performance + 0.20% a year'],['Depositors got','3.06% a year in September against 2.25% for stETH']],
  events:[['6 Nov 2025','stRATEGY launches','Aave, Ethena and Uniswap routes'],['19 Feb 2026','DAO proposes a $5M first-loss reserve','$3M wstETH for Earn ETH'],['18 Apr 2026','rsETH exploit freezes the vault','27-day pause'],['15 May 2026','DAO burns 144.8 ETH of shares','Covers the loss; withdrawals resume'],['29 Sep 2026','5M USDT borrowed into earnUSD','+1,401 USDT by 2 Oct']],
  lesson:'A positive dollar spread is easiest when the parking vault is your own; a first-loss reserve is what kept depositors whole in April.'},
 avant:{
  facts:[['Depositors own','12,583 ETH','avETH face; returns go to savETH'],['Live since','Sep 2025','Avant'],['Paid, a year','4.12%','Sep, savETH; stETH 2.25%'],['Without rewards','4.55%','90 days; actual 4.74%; points not priced'],['Holders','83 / 37','savETH / avETH'],['Health factor','1.37','27% ETH fall to liquidation']],
  sub:'Ethereum and Avalanche. The borrowed dollars go into Avant’s own dollar product.',
  flow:{w:1000,h:370,label:'Avant avETH: ETH is posted on Aave and Spark, dollars are borrowed and parked in Avant’s own savUSD on Avalanche; income goes to the senior savETH',
   nodes:[fdTop(10,'You',['ETH']),fdTop(210,'avETH / savETH',['12,583 ETH;','savETH is senior'],[ATES+'0x9469470C9878bf3d6d0604831d9A3A366156f7EE','avETH 0x9469…f7EE'],1),fdTop(410,'Strategy wallet',['ETH, wstETH, weETH','on Aave and Spark'],[ATES+'0x6CC60A0b57bc882A0471980D0e2D4aD7DDf3C4bD','0x6CC6…C4bD']),
    fdTop(610,'Dollar loans',['$10.0M at 6.30%:','USDC, USDS, PYUSD']),{x:810,y:70,w:180,h:84,t:'savUSD',s:['Avant’s own; 7.54%','98% on Avalanche']},
    fdBot(610,'Income',['savUSD yield less','6.30%; staking']),fdBot(410,'savETH price',['4.12% a year (Sep)']),fdBot(10,'You withdraw',['1-day cooldown; the debt','needs savUSD back: up to a week'])],
   edges:[{k:'eth',d:'M180 112 H208',n:1,bx:194,by:94},{k:'eth',d:'M380 112 H408',n:2,bx:394,by:94},{k:'usd',d:'M580 112 H608',n:3,bx:594,by:94},{k:'usd',d:'M780 112 H808',n:4,bx:794,by:94},{k:'rew',d:'M900 154 V312 H782',n:5,bx:900,by:230},{k:'rew',d:'M610 312 H582'},{k:'rew',d:'M410 312 H182',n:6,bx:300,by:294}]},
  steps:[`You deposit ETH for avETH; the senior tranche, savETH, receives the yield. 12,583 ETH of avETH on 2 October.`,`A ${atL(ATES+'0x6CC60A0b57bc882A0471980D0e2D4aD7DDf3C4bD','strategy wallet')} posts ETH, wstETH and weETH on Aave and Spark.`,`It borrows $10.0M: 2.2M USDC on Aave, 7.3M USDS and 0.5M PYUSD on Spark, at 6.30% on average; health factor 1.37.`,`98% of the dollars go into savUSD, Avant's own dollar product, on Avalanche, which paid 7.54%.`,`The spread and staking yield go to savETH: 4.12% a year in September.`,`You withdraw after a 1-day cooldown. Repaying the debt needs the savUSD back: a cooldown, a bridge and up to 7 days of redemption.`],
  pays:[['savUSD','Avant’s own dollar product: 7.54% against 6.30% of interest, +1.24 pp on $10M'],['Staking','Yield on the posted ETH'],['Depositors got','4.12% a year in September (savETH) against 2.25% for stETH']],
  events:[['Sep 2025','avETH funded; first dollar loans','$2.0M'],['Apr–May 2026','Debt near zero','Loans repaid'],['Aug 2026','Peak $11.3M of debt','12,573 ETH'],['29 Sep 2026','Portfolio disclosure: $72.65M assets, $39.47M liabilities','$32.53M in savUSD']],
  lesson:'Parking in the issuer’s own product turns the spread into one credit bet with a week-long exit.'},
 liquity:{
  facts:[['Depositors own','6,014 ETH','$16M; an IPOR Fusion vault'],['Live since','Mar 2026','first deposit 5 March'],['Paid, a year','5.59%','Sep, annualised; stETH 2.25%'],['Without rewards','2.26%','90 days; actual 3.84%; rewards 99% of the lead'],['Holders','130','largest 36.9%'],['Health factor','1.88','47% ETH fall to liquidation']],
  sub:'All on Ethereum. The name says Liquity; the live loan is an Ebisu trove (a Liquity v2 fork) and the dollars sit in ebUSD pools.',
  flow:{w:1000,h:370,label:'Liquity ETH Carry: WETH becomes wstETH in an Ebisu trove that mints ebUSD; the ebUSD goes into Curve and Uniswap v4 pools; fees and staking raise the share price',
   nodes:[fdTop(10,'You',['WETH']),fdTop(210,'Liquity ETH Carry',['6,014 ETH;','IPOR Fusion vault'],[ATES+'0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c','0xb9e8…663c'],1),fdTop(410,'Ebisu trove',['4,585 wstETH;','LTV 44%, liq. 83%']),
    fdTop(610,'ebUSD minted',['6.75M at 2.55%,','set by the vault']),{x:810,y:70,w:180,h:84,t:'ebUSD/USDC pools',s:['Curve and Uniswap v4;','0.45% fees']},
    fdBot(610,'Fees + staking',['pool fees and','wstETH yield']),fdBot(410,'Share price',['0.5% + 10% of gains']),fdBot(10,'You withdraw',['1% at once; 10% and','30% requests revert'])],
   edges:[{k:'eth',d:'M180 112 H208',n:1,bx:194,by:94},{k:'eth',d:'M380 112 H408',n:2,bx:394,by:94},{k:'usd',d:'M580 112 H608',n:3,bx:594,by:94},{k:'usd',d:'M780 112 H808',n:4,bx:794,by:94},{k:'rew',d:'M900 154 V312 H782',n:5,bx:900,by:230},{k:'rew',d:'M610 312 H582'},{k:'rew',d:'M410 312 H182',n:6,bx:300,by:294}]},
  steps:[`You deposit WETH into ${atL(ATES+'0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c','an IPOR Fusion vault')}; 6,014 ETH on 2 October from 130 holders.`,`The vault turns it into wstETH in an Ebisu trove (a Liquity v2 fork): 4,585 wstETH, LTV 44% against an 83% liquidation line.`,`The trove mints 6.75M ebUSD at 2.55%, a rate the vault sets itself.`,`The ebUSD goes into ebUSD/USDC pools on Curve and Uniswap v4, which earned 0.45% in fees.`,`Staking yield on the wstETH and the pool fees come back; fees 0.5% a year and 10% of gains.`,`You withdraw: a 1% request goes through, 10% and 30% revert. 97.5% of the debt can be bought back on Curve in one block.`],
  pays:[['Staking','wstETH yield on 4,585 wstETH: most of the return'],['Pools','0.45% in fees on the ebUSD against 2.55% on the loan: −2.1 pp'],['Rewards','Small BOLD reward on Uniswap v4, about $15k a year'],['Depositors got','5.59% a year in September, +3.34 pp over stETH, on a 6,000 ETH book']],
  events:[['30 Jan 2026','Vault deployed','Empty until March'],['5 Mar 2026','First deposit and trove','Nine trove opens and closes since'],['6 Jun 2026','Current trove opens','Rocksolid buys 748 shares'],['Sep 2026','Debt $6.75M','Book 6,017 ETH']],
  lesson:'A self-set borrow rate is cheap until the stablecoin’s peg needs defending; the exit is only as wide as the pool.'}
};

function atFacts(f){return `<div class="facts">${f.map(([a,b,c])=>`<div>${esc(a)}<b>${esc(b)}</b><small>${esc(c)}</small></div>`).join('')}</div>`;}
function atKeys(p){
 const k=R.atlasTop5Risk?.keys?.[p.id];
 const sa=a=>/^0x[0-9a-f]{40}$/i.test(a)?`<a href="https://etherscan.io/address/${a}" target="_blank" rel="noopener" class="mono">${short(a)}</a>`:esc(a);
 const rows=k&&k.length?k.map(r=>[sa(r.holder)+'<div class="sub">'+esc(r.holder_type||'')+'</div>',esc(r.layer)+'<div class="sub">'+esc(r.power||'')+'</div>',esc(r.can_change||''),esc(String(r.delay_at_T||'').replace(/^none.*$/i,'none'))]):(p.actors||[]).slice(0,8).map(r=>[r.url?atL(r.url,esc(r.who)):esc(r.who),esc(r.role||''),esc((r.canChange&&r.canChange!==r.role)?r.canChange:''),esc(String(r.delay||''))]);
 return `<div class="panel"><h3>Who is in the chain, and what each can change</h3><div class="sub">Read on-chain at block 26,108,081.</div><div class="tblwrap"><table><thead><tr><th>Who</th><th>Where</th><th>Can change</th><th class="n">Delay</th></tr></thead><tbody>${rows.map(r=>`<tr>${r.map((c,i)=>`<td${i===3?' class="n"':''}>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div></div>`;}
function atBook(p,color){const rows=p.charts.capitalHistory.rows.filter(r=>r.sizeETH!=null);
 const chart=columnChart([{name:p.name,color,points:rows.map(r=>[r.timestamp,r.sizeETH])}],{small:true,height:230,label:p.name+' book, ETH, month-end',format:v=>ATK(v)+' ETH'});
 const pk=rows.reduce((a,r)=>r.sizeETH>(a?.sizeETH||0)?r:a,null);
 return `<div class="panel"><h3>ETH in the product, month-end</h3><div class="sub">${pk?'Peak '+ATK(pk.sizeETH)+' ETH in '+ATMON(pk.month)+'; '+ATK(rows.at(-1)?.sizeETH)+' at the end of September.':''}</div><div class="chart-scroll">${chart}</div></div>`;}
function atHolders(p){
 const B=(R.atlasTop5Risk?.buckets?.[p.id]||[]).filter(r=>r.row_type==='bucket');const view=B[0]?.view;const rows=B.filter(r=>r.view===view);
 const HM=(R.atlasTop5Risk?.holdersMonthly?.[p.id]||[]);const hm=HM.filter(r=>r.token===HM.at(-1)?.token);
 if(!rows.length)return '';
 const bars=horizontalBars(rows.map(r=>({name:r.label+' ('+num(+r.holders,0)+')',base:+r.eth_pct/100,total:+r.eth_pct/100,color:'var(--pc)'})),{format:v=>pct(v,0),label:'Share of the book by holding size'});
 const n=rows.reduce((a,r)=>a+(+r.holders),0),small=rows.filter(r=>/<1|1-10/.test(r.label)),last=hm.at(-1);
 return `<div class="panel"><h3>Share of ETH by holding size</h3><div class="sub">${num(n,0)} addresses (${esc(view||'')}); ${pct(small.reduce((a,r)=>a+(+r.holders),0)/n,0)} hold under 10 ETH and ${num(small.reduce((a,r)=>a+(+r.eth_pct),0),1)}% of the money.${last?' Top 10 hold '+num(+last.top10_pct,0)+'%.':''}</div><div class="chart-scroll">${bars}</div>${ATHOLD[p.id]?'<p class="note">'+esc(ATHOLD[p.id])+'</p>':''}</div>`;}
const ATHOLD={yieldbasis:'Look-through of the gauge and 81 personal vaults gives 407 owners; the largest holds 21.8%, the top 10 hold 70.7%.',avant:'One investor holds 37.8% of the product, directly, through a Gearbox account and as Morpho collateral; 16.3% of savETH is bridged to other chains.',liquity:'One Safe holds 36.9% of the vault; Rocksolid holds 12.1%.',liquid:'82% of the 7,793 Ethereum addresses hold under 1 ETH (0.26% of the money); 11 addresses hold 70.3%. Optimism adds 1,511 holders.'};
function atEvents(c,id){const E=(R.atlasTop5Risk?.events?.[id]||[]).filter(r=>r.effect_on_deposits_or_yield).slice(-6);const rows=E.length>=3?E.map(r=>[r.date,r.event,r.effect_on_deposits_or_yield]):c.events;return `<div class="panel"><h3>What moved it</h3><div class="tl">${rows.map(([d,t,x])=>`<div class="e"><div class="d">${esc(d)}</div><div><div class="t">${esc(t)}</div><div class="x">${esc(x)}</div></div></div>`).join('')}</div></div>`;}

function atProduct(id){
 const p=PC.products.find(x=>x.id===id),c=ATP[id],host=$('#strict-product-content');if(!p||!c||!host)return false;
 const color=ST_COLORS[(p.rank-1)%ST_COLORS.length],s=ST_STORIES[id]||{};host.style.setProperty('--pc',color);
 const rank=EQ.topFive.indexOf(id)+1;
 host.innerHTML=`<article class="atp" style="--pc:${color}"><div class="k">${rank} · by dollars borrowed against ETH</div><h2 class="ptitle">${esc(p.name)}</h2><p class="pfinding"><b>${esc(s.title||'')}.</b> ${esc(s.text||'')}</p>
  ${atFacts(c.facts)}
  <div class="panel fdp"><h3>How the money moves</h3><div class="sub">${esc(c.sub)} Boxes and steps link to the contracts.</div>
   <div class="fdkey"><span><i class="eth"></i>ETH and staked ETH</span><span><i class="usd"></i>Dollars</span><span><i class="rew"></i>Income and rewards</span></div>
   <div class="fdw">${atFlowSVG('fd-'+id,c.flow)}</div><ol class="fsteps">${c.steps.map(t=>`<li>${t}</li>`).join('')}</ol></div>
  ${atKeys(p)}
  <div class="cols"><div class="panel"><h3>Who pays the yield</h3><dl class="kv">${c.pays.map(([a,b])=>`<dt>${esc(a)}</dt><dd>${esc(b)}</dd>`).join('')}</dl></div>${atBook(p,color)}</div>
  <div class="cols">${atHolders(p)}${atEvents(c,id)}</div>${id==='liquid'?atLiquidLoop():''}
  <div id="atp-risk"></div>
  <p class="lesson"><b>Lesson.</b> ${esc(c.lesson)}</p></article>`;
 atRiskPanel(id);const rp=$('#atlas-risk-'+id);if(rp)$('#atp-risk').replaceWith(rp);
 return true;}

// reader edition: the BTC template replaces the earlier chapter for the five; Closed keeps its own renderer
const _atPrevRender2=stRenderProduct;
stRenderProduct=function(id,u){if(document.body.dataset.edition==='reader'&&ATP[id]){stProduct=id;stProductTabs(id);if(u!==false){const url=new URL(location.href);url.searchParams.set('carryProduct',id);history.replaceState(null,'',url);}atProduct(id);return;}_atPrevRender2(id,u);};
// tab labels as in BTC: name, size, what it paid
const _atPrevTabs=stProductTabs;
stProductTabs=function(active){_atPrevTabs(active);if(document.body.dataset.edition!=='reader')return;const R30=Object.fromEntries((R.reportContract.matched30dReturns||[]).map(r=>[r.id,r]));
 $$('#strict-product-tabs [role=tab]').forEach(b=>{const id=b.dataset.carryProduct;const p=PC.products.find(x=>x.id===id);const sm=b.querySelector('small');if(!sm)return;if(p&&ATP[id]){const r=R30[id];sm.textContent=ATK(p.capitalETH)+' ETH'+(r?' \u00b7 '+(r.bookReturnPct*365/30).toFixed(1)+'% a year':'');}if(id==='closed'){sm.textContent='Lido Earn freeze, Kelp, Reservoir, TAU';const nm=b.querySelector('.nm');if(nm)nm.lastChild.textContent='Closed and stressed';}});};

// Closed and stressed cases (BTC: Maple, Hermetica, Acre). research/eth/en/CLOSED-CASES.md
const ATCLOSED=[
 ['Lido Earn ETH','Frozen 27 days, April to May 2026','The Kelp rsETH exploit on 18 April froze withdrawals until 15 May. The WETH borrow cost during the freeze was 143.98 ETH (0.13% of the book); the DAO burned 144.77 ETH of its own shares to cover it, so depositors lost nothing. Deposits left anyway: 111k ETH fell to 58k.','A first-loss reserve keeps depositors whole; it does not keep them in the vault.'],
 ['The Kelp rsETH exploit','18 April 2026: 112k unbacked rsETH','About 107k came back through Aave and Compound liquidations; a group of DAOs and firms covered the rest and rsETH was fully backed again by 25 May. Aave is still short 52,964 WETH on Ethereum and 29,835 on Arbitrum. CIAN rsETH fell 2.6% and recovered; Kelp Gain (hgETH) was frozen 19 April to 5 June and wrote down 500 rsETH (−4.09% in June).','A restaking token is credit, not ETH: price it as such when it is collateral.'],
 ['Reservoir ETH Yield','Peaked at 4,137 ETH (Oct 2025); now 24 ETH','Two loan layers: WETH collateral on Aave against USDC into srUSD, which borrows again on Morpho. Holders since launch earned +0.29% over 13 months against +2.72% for stETH. No liquidation or incident; depositors simply left.','Two layers of loans paid less than plain staking.'],
 ['TAU InfiniFi ETH Carry','Book down 99% from January to April 2026','wstETH collateral, USDC into InfiniFi siUSD with a second loop inside (2.53M USDC in January). Holders are −0.33% in wstETH terms; debt is 0.02 USDC at the snapshot. No public reason for the unwind.','A carry vault can empty quietly; check the debt, not the name.'],
 ['Rocksolid rETH','Closed 29 Sep, reopened 7 Oct 2026','The owner called initiateClosing; new withdrawal requests reverted for eight days. On 7 October a contract upgrade added cancelClosing and the vault reopened, with no loss. No public reason.','If the owner can close and reopen by upgrade, the exit terms are whatever the owner says.'],
 ['Restaking-token outflows','Eigenpie, Puffer, Mellow, Renzo: −90 to −99.6%','The points and airdrop programmes ended, slashing went live and the Kelp exploit hit. No loss event drove the exits.','Restaking capital was points capital.']];
function atClosed(){const host=$('#strict-product-content');if(!host)return;
 host.innerHTML=`<article class="atp"><h2 class="ptitle">Closed and stressed</h2><p class="pfinding">What went wrong in ETH yield products in 2025 and 2026, and who paid.</p>${ATCLOSED.map(([n,s,t,l])=>`<div class="panel"><h3>${esc(n)}</h3><div class="sub">${esc(s)}</div><p>${esc(t)}</p><p class="lesson"><b>Lesson.</b> ${esc(l)}</p></div>`).join('')}<p class="note">Sources and dates: <a href="library/CLOSED-CASES.html">closed and stressed cases</a>.</p></article>`;}
const _atPrevRender3=stRenderProduct;
stRenderProduct=function(id,u){if(document.body.dataset.edition==='reader'&&id==='closed'){stProduct='closed';stProductTabs('closed');atClosed();return;}_atPrevRender3(id,u);};

// Liquid ETH: the loop's health factor by week, with large repayments (BTC: Kraken's June fall). research/eth/en/LIQUID-LOOP.md
function atLiquidLoop(){const W=(R.atlasTop5Risk?.liquidLoop||[]).filter(r=>/Aave/.test(r.pool));if(!W.length)return '';
 const t=d=>Date.parse(d+'T23:59:59Z')/1000;
 const hf=W.map(r=>[t(r.week_end),+r.health_factor]),line=hf.map(([x])=>[x,1.0]);
 const chart=lineChart([{name:'Aave health factor (weekly)',color:'var(--pc)',points:hf},{name:'Liquidation',color:'var(--danger, #d9534f)',points:line}],{yLabel:'Health factor',format:v=>num(v,3)});
 const rate=lineChart([{name:'Aave WETH borrow rate',color:'var(--danger, #d9534f)',points:W.map(r=>[t(r.week_end),+r.weth_borrow_apr_instant*100])},{name:'weETH staking yield',color:'#3fae9a',points:W.filter(r=>r.staking_apr_week!=='').map(r=>[t(r.week_end),+r.staking_apr_week*100])}],{yLabel:'% a year',format:v=>num(v,1)+'%'});
 return `<div class="panel"><h3>The loop: thin, and the dips are self-made</h3><div class="sub">Of 19 drops below health factor 1.03 on Aave, 18 began when the vault moved collateral into ether.fi or Lido redemption queues; none came from prices. The median wait to the next repayment was 13.5 hours, the longest 126. In the April 2026 rsETH stress the WETH rate spiked and the first repayment came 93.6 hours later; Aave debt then fell by half by June. At 2 October the loop sat below 1.03 for 357 hours. Only about 7,200 WETH can be raised in one block from weETH sales at under 0.5% slippage; lifting the health factor to 1.05 needs 94,000. A 2.64% cut in weETH’s exchange rate would liquidate it.</div><div class="cols" style="margin-top:6px"><div class="chart-scroll">${chart}</div><div class="chart-scroll">${rate}</div></div></div>`;}
