// The primary reading route mounts only the eight report chapters.
function readerCarryRows(){
 return R.carryCategory.products.filter(p=>p.classification==='E4').map(p=>{
 const c=PC.products.find(c=>c.name.toLowerCase()===p.product.toLowerCase());
 const x=R.carryExpansion?.products.find(x=>x.address?.toLowerCase()===p.address?.toLowerCase());
 return {...p,chapter:c,...(c?.liveRoute||{}),...(x?{collateral:x.collateral,debt:x.debt,destination:x.destination,status:x.status}:{}),name:p.product};
 }).sort((a,b)=>b.sizeETH-a.sizeETH);
}
const READER_STATUS={'YieldBasis WETH':'Active dollar-financed LP','Concrete Delta weETH':'Shared backing unresolved','ether.fi Liquid ETH':'Active hybrid','Rocksolid rETH':'Closing; nested carry','Liquity ETH Carry':'Active Ebisu loan','Royco ETH':'Stale parent marks; loan traced','TAU InfiniFi ETH Carry':'Historical carry; dust debt at T','Reservoir ETH Yield':'Small current position'};
const READER_ROUTES={
 'YieldBasis WETH':['YieldBasis / Curve','Borrow crvUSD to maintain WETH/crvUSD liquidity','YieldBasis / pool admin'],
 'Concrete Delta weETH':['Aave / Spark, shared Safe','Dollar-neutral arbitrage mandate; product allocation unresolved','Concrete / shared 3-of-5 Safe'],
 'ether.fi Liquid ETH':['Aave / Spark / Morpho','Cap cUSD; Sentora RLUSD and PRIME credit','ether.fi / Veda / Nonce'],
 'Rocksolid rETH':['Ebisu, through Liquity shares','Nested Liquity carry; other portfolio strategies','Rocksolid / Fusion'],
 'Liquity ETH Carry':['Ebisu','ebUSD liquidity on Curve and Uniswap V4','Sentinel / Fusion'],
 'Royco ETH':['Morpho, through Makina','Senior dollar-credit receipt','Royco / Concrete / Makina'],
 'TAU InfiniFi ETH Carry':['Morpho','InfiniFi savings; historical nested loan','TAU / Fusion'],
 'Reservoir ETH Yield':['Aave / Morpho','srUSD savings and a second dollar loan','Reservoir / Fusion']
};
function readerCategoryInsight(id){
 const insights={
 staking:['The receipt is a layer over the income source','Custodied receipts such as WBETH and listed staking products still earn validator income. Their charges, custody and access differ. mETH also allocates 8.49% of its controlled book to a lending buffer; restaking adds separate service and reward claims. Count the backing and its wrappers separately.','STRATEGY-UNIVERSE-EXPANSION'],
 loops:['A lending allocator can contain a staking loop','Yearn WETH-1 has a measured Spark wstETH/WETH loop: 7.98× collateral leverage, HF 1.0633 and 14.18% of the parent book. It is absent from the default withdrawal queue. Classify the actual debt currency and look through each allocation.','PRODUCT-FINANCIAL-HISTORY'],
 carry:['The route can change while the product name stays','Reservoir has both an outer ETH-collateral loan and an inner dollar-savings loan. Each must earn enough to cover its own funding and exit. TAU had about 3.04M USDC stored debt in January 2026, but only 0.022132 USDC accrued debt at T. Historical carry is not automatically current carry.','CARRY-VARIANTS-EXPANSION'],
 basis:['A dollar return is different from an ETH-long return','A spot ETH position with an offsetting short earns funding or basis while hedging ETH price exposure. Hedge execution, custody and redemption determine the outcome. The separately dated Ethena disclosure does not fill an unmeasured slice of the frozen market.','STRATEGY-UNIVERSE-EXPANSION'],
 fixed_yield:['Maturity and payoff units matter','The official Ethereum Pendle registry preserves 117 ETH-tagged markets; only four are active and unexpired at the later discovery. The examined PT-stETH claim pays in stETH, despite a wstETH underlying feed label. PT-buy and LP feed rows can refer to the same market liquidity. Neither labels nor duplicated rows establish extra capital.','STRATEGY-UNIVERSE-EXPANSION'],
 farming:['Fees are only part of the trading payoff','GMX LP value includes trader P&L and inventory exposure. An ETH index does not establish ETH collateral: ETH/USDC, ETH/ETH and dollar-collateral markets differ. Covered-call products earn premiums by selling upside. Historical option capacity and a deployed contract do not establish current funded ETH capacity. Retired and recovery products need separate cash-rights analysis.','STRATEGY-UNIVERSE-EXPANSION'],
 lending:['A loan book needs borrowers, income and cash','The measured hgETH rsETH pool has a $13.52M book reconciled to loans, physical assets and reserved adapter positions. Its 173 historical registry entries do not mean 173 active loans. Borrower identity, repayment and dollar-carry use remain separate questions.','HGETH-LOAN-BOOK'],
 cdp:['Dollar debt alone does not establish yield','Seven sampled large-borrower cash loans lead to owner transfers, Maker refinancing or USDC/USDT conversion. A carry position needs an evidenced reinvestment leg. Retaining staking income on collateral does not turn every dollar loan into a carry product.','BORROWER-USE']
 };const item=insights[id];return item?'<div class="category-insight"><h4>'+esc(item[0])+'</h4><p>'+esc(item[1])+' <a href="library/'+item[2]+'.html">Position and source review →</a></p></div>':'';
}
function readerCarryTable(){const rows=readerCarryRows(),sum=msum(rows,'sizeETH');return stTable(['Product','Whole book at T','Share of eight books','How it earns'],rows.map(p=>{const route=READER_ROUTES[p.name],chapter=p.chapter,href=chapter?'?carryProduct='+chapter.id+'#strict-product-tabs':'library/CARRY-VARIANTS-EXPANSION.html';return [`<a href="${href}" ${chapter?'data-carry-product="'+chapter.id+'"':''}><b>${esc(p.name)}</b></a><div class="sub">${esc(READER_STATUS[p.name])}</div>`,num(p.sizeETH,1)+' ETH<div class="sub">'+money(p.sizeUSD)+'</div>',pct(p.sizeETH/sum,p.sizeETH/sum<.0001?3:2),esc(route[1])];}),'reader-carry-products');}
function readerCarryComposition(){const rows=readerCarryRows(),sum=msum(rows,'sizeETH');$('#reader-carry-bars').innerHTML=horizontalBars(rows.map((p,i)=>({name:p.name,base:p.sizeETH,total:p.sizeETH,color:CARRY_COLORS[i]})),{format:v=>chartShort(v,n=>num(n,0)+' ETH'),label:'Eight measured carry-design books, whole product NAV'});$('#reader-carry-composition').innerHTML=readerCarryTable();$('#reader-carry-scope').textContent='Eight examined products: '+num(sum,0)+' ETH of whole-product book claims. Concrete and Liquid are hybrid parents; Rocksolid includes 728 ETH of Liquity claims. These sizes describe the products, not unique dollars deployed in carry. The market category above counts three protocol parents; their adapter values use a different price convention.';}
function readerRouteTable(){const rows=[
 ['Dollar lending','Liquid → Sentora / Cap','Borrower interest, plus disclosed rewards','Loan APR; borrower default; redemption liquidity'],
 ['Savings with a second loan','Reservoir → srUSD; TAU → InfiniFi','Savings return on a leveraged dollar position','Outer and inner loan costs; two liquidation tests'],
 ['Senior credit','Royco → senior dollar receipt','Income assigned to the senior tranche','Senior funding, junior protection and mark freshness'],
 ['Minted-dollar LP','Liquity → Ebisu → stable pools','Swap fees and separately realised incentives','Minting costs, pool losses and ebUSD sourcing'],
 ['External arbitrage','Concrete Delta published mandate','Arbitrage spread under manager execution','Private positions, shared custody and payout rights'],
 ['Fixed maturity / cross-chain credit','Additional route screens','Maturity discount or destination borrower income','Bridge, maturity and repayment timing']
 ];$('#reader-carry-route-table').innerHTML=stTable(['Route','Example / evidence','Who pays','Costs and exit to verify'],rows.map(r=>r.map(esc)));}
function initReader(){
 initTheme();
 wealth();returns(730);$('#wealth-controls').onclick=e=>{const b=e.target.closest('[data-series]');if(b){hiddenSeries.has(b.dataset.series)?hiddenSeries.delete(b.dataset.series):hiddenSeries.add(b.dataset.series);wealth();}};
 $('#return-window').onclick=e=>{const b=e.target.closest('[data-days]');if(b)returns(+b.dataset.days);};
 R.protocols.filter(r=>MP.products.some(p=>p.id===r.protocol)).slice().sort((a,b)=>(b.eth_family_reported_usd||0)-(a.eth_family_reported_usd||0)).forEach(r=>{const opt=document.createElement('option');opt.value=r.protocol;opt.textContent=r.name;$('#history-protocol').appendChild(opt);});$('#history-protocol').onchange=protocolHistory;protocolHistory();
 document.addEventListener('click',e=>{const b=e.target.closest('[data-display-group]');if(b)displayView(b.dataset.displayGroup,b.dataset.display);});
 renderResearchAdditions();initMarket();initStrictResearch();readerCarryComposition();readerRouteTable();readerLandscape();readerBorrowingTable();readerResearchSynthesis();
 const observer=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting)$$('nav.sec a').forEach(a=>a.setAttribute('aria-current',String(a.hash==='#'+e.target.id)));}),{rootMargin:'-10% 0px -75% 0px'});$$('main>section').forEach(s=>observer.observe(s));
 window.addEventListener('hashchange',openHash);openHash(true);document.documentElement.dataset.loaded='true';
}
function readerLandscape(){
 const census=R.reportContract.census;
 const rows=census.map(p=>{
  const chapter=PC.products.find(c=>c.name===p.name),route=READER_ROUTES[p.name];
  const href=chapter?'?carryProduct='+chapter.id+'#strict-product-tabs':'library/CARRY-VARIANTS-EXPANSION.html';
  return ['<a href="'+href+'" '+(chapter?'data-carry-product="'+chapter.id+'"':'')+'><b>'+esc(p.name)+'</b></a>',esc(p.statusLabel),num(p.bookETH,1)+' ETH<div class="sub">'+money(p.bookUSD)+'</div>',esc(route[1]),esc(p.allocationEvidence)];
 });
 R.carryCoverage.documentedRoutes.forEach((p,i)=>rows.push([a(p.source,p.product),i?'Documented legacy; withdraw-only':'Documented active route','Unmeasured at T',i?'Aave USDT → crvUSD → pmUSD/crvUSD LP → StakeDAO':'LlamaLend crvUSD → Curve crvUSD/USDT → StakeDAO','Documentation establishes the design; capital and live allocation at T are unmeasured.']));
 $('#strict-landscape').innerHTML=stTable(['Product','Status at T','Whole book','Financed route / mandate','Attribution boundary'],rows,'reader-landscape-table');
 $('#strict-census-note').innerHTML='Eight examined books; five current traced routes, one Closing, one historical and one declared mandate with shared custody unresolved. Books overlap. Concrete and Liquid hold '+pct(R.reportContract.sampleTopTwoShare,2)+' of this sample’s gross book claims; this is not carry-market concentration. <a href="data/carry-status-and-capital.csv" download>Status and capital CSV →</a>';
 $('#reader-carry-candidates').innerHTML=stTable(['Candidate','Measured book','Why it is separate'],R.carryCategory.products.filter(p=>!['E3','E4','E9'].includes(p.classification)).map(p=>[esc(p.product),p.sizeETH==null?'Not measured':num(p.sizeETH,0)+' ETH','Dollar-funded investment route unverified. <a href="library/CARRY-VARIANTS-EXPANSION.html">Position review →</a>']));
}

function readerBorrowingTable(){
 const reserves=R.readerAnalysis.funding.map(r=>['Aave V3 / '+esc(r.chain),'ETH-family eligibility',esc(r.symbol==='USDCn'?'native USDC':r.symbol),pct(r.borrow_apr,2),money(r.cash_USD)]);
 const loans=EC.borrow_markets.filter(r=>r.observed_product_debt_units>=1).map(r=>[a(r.links?.market,r.venue)+' / '+esc(r.chain),esc(r.collateral_symbol),esc(r.loan_symbol),pct(r.borrow_apr,2),r.reserve_cash_units==null?'Not reported':num(r.reserve_cash_units,0)+' '+esc(r.loan_symbol)]);
 $('#strict-borrow-markets').innerHTML=stTable(['Lender / chain','Collateral','Debt token','Borrow APR at T','Reserve cash'],[...reserves,...loans])+'<p class="note">Snapshot APR; cash does not guarantee borrowing capacity. Morpho rows show tracked Liquid loan markets. <a href="library/DOLLAR-FUNDING-ATLAS.html">All currencies, caps and lenders →</a></p>';
 $('#strict-curve-note').innerHTML='Fixed-block model, varying utilization. This illustrates repricing. <a href="library/CARRY-MATH.html">Model and contract verification →</a>';
}

function readerCarryWaves(){
 const books=R.readerAnalysis.books,book=name=>books.find(p=>p.name===name),liquid=book('ether.fi Liquid ETH'),reservoir=book('Reservoir ETH Yield'),tau=book('TAU InfiniFi ETH Carry');
 const waves=[
 ['Oct 2024 to Aug 2025','Liquid establishes the large hybrid book','The measured book starts at '+num(liquid.history[0].eth,0)+' ETH and peaks at '+num(liquid.peak.eth,0)+' ETH in '+liquid.peak.month+'. It combines staking loops and dollar carry. The whole-book history cannot isolate the historical dollar allocation.','?carryProduct=liquid#strict-product-tabs'],
 ['Sep to Dec 2025','New wrappers and nested financing','Rocksolid and Reservoir acquire material balances in September. Reservoir peaks at '+num(reservoir.peak.eth,0)+' ETH in October. Concrete’s '+num(book('Concrete Delta weETH').history.find(r=>r.month==='2025-12').eth,0)+' ETH claim appears in December; its issuance still needs an outside-capital reconciliation.','library/CARRY-VARIANTS-EXPANSION.html'],
 ['Jan to Sep 2026','Routes grow, change and unwind','Liquity becomes funded in March; YieldBasis WETH is funded by May and reaches '+num(book('YieldBasis WETH').history.at(-1).eth,0)+' ETH in September. TAU reduces its USDC debt to dust. Rocksolid enters Closing on 29 September. Book size and the active route can move in different directions.','library/CARRY-PRODUCTS.html']
 ];return waves.map(w=>'<div><div class="k">'+esc(w[0])+'</div><h4>'+esc(w[1])+'</h4><p>'+esc(w[2])+'</p><a href="'+w[3]+'">Evidence →</a></div>').join('');
}
function readerResearchSynthesis(){
 $('#reader-carry-candidates').insertAdjacentHTML('beforeend',stTable(['Additional product / family','Classification decision'],R.carryCoverage.reviewedCases.filter(r=>!r.counted&&!r.product.startsWith('ZenSats')).map(r=>[a(r.source,r.product),esc(r.decision)+'<div class="sub">'+esc(r.evidence)+'</div>']))+'<p class="note"><a href="library/CARRY-COVERAGE-AUDIT.html">Material pool screen, source decisions and eight route families →</a></p>');
 $('#strict-discovery').insertAdjacentHTML('afterbegin','<p><b>Fresh coverage review, 5 October.</b> '+num(R.carryCoverage.totalPools)+' DefiLlama pools; '+num(R.carryCoverage.keywordCandidates)+' ETH-name candidates; '+num(R.carryCoverage.materialKeywordPools)+' pools above $5M from '+R.carryCoverage.materialProjects+' projects. Every material row has a disposition. Of these, '+R.reportContract.discovery.parentDispositions+' dispositions join an already-covered parent. They do not independently reconstruct each pool’s strategy. Keyword matches and full pool TVL are discovery inputs, not verified ETH capital. <a href="library/CARRY-COVERAGE-AUDIT.html">Decisions, omissions corrected and CSV →</a></p>');

 $('#reader-earned-carry').innerHTML='<h3>Observed financed investment results</h3><p>Three traced lots match investment income with funding on the same borrowed principal through the measured exit or repayment date. They illustrate the mechanism; they are not a market average.</p><div class="tblwrap">'+stTable(['Borrowed lot','Investment income','Funding cost','Result before gas'],R.reportContract.financedLots.map(r=>[a(r.receipt,num(r.borrowed,0)+' '+r.currency+' · '+stHumanDate(r.start.slice(0,10))),num(r.income,2)+' '+r.currency,num(r.fundingCost,2)+' '+r.currency,num(r.resultBeforeGas,2)+' '+r.currency]))+'</div><p class="note">USDC income is allocated proportionally from the common redemption. The PYUSD result includes residual debt. Gas, collateral income and whole-wallet profit are separate. <a href="library/CARRY-LIFECYCLES.html">Dates, receipts and allocation rules →</a></p>';
 $('#reader-borrower-use').innerHTML='<p><b>A large loan is not automatically carry.</b> Sampled large-borrower loans also fund transfers, refinancing and currency conversion. <a href="library/BORROWER-USE.html">Identities and use of proceeds →</a></p>';
 readerComparison();readerPlaybook();readerCoverage();readerAnswer();
}

function readerComparison(){
 const route={yieldbasis:['WETH/crvUSD liquidity → crvUSD','Leveraged Curve liquidity'],concrete:['weETH → shared dollar loans','Published neutral arbitrage; allocation unverified'],liquid:['weETH / wstETH → dollar loans','Cap and Sentora credit vaults'],rocksolid:['Liquity shares → underlying ebUSD loan','Nested Liquity carry and other strategies'],liquity:['wstETH → ebUSD','Curve and Uniswap liquidity'],royco:['wstETH → PYUSD','Senior dollar-credit receipt']};
 const fees={yieldbasis:'10% minimum admin parameter; variable allocation',concrete:'0% configured; private fees unknown',liquid:'0.35% management',rocksolid:'1% management / 10% performance',liquity:'0.5% management / 10% performance',royco:'0% management / 10% performance'};
 const operators={yieldbasis:'YieldBasis / pool admin',concrete:'Concrete / shared custody Safe',liquid:'ether.fi / Veda / Nonce',rocksolid:'Rocksolid / Tulipa',liquity:'Sentinel / Fusion',royco:'Dialectic / Concrete / Makina'};
 const risks={yieldbasis:'Debt repricing; gauge income differs from LT mark',concrete:'Shared assets and outside capital unresolved',liquid:'Thin loop headroom; funding and credit exposure',rocksolid:'Closing; overlaps Liquity’s book',liquity:'ebUSD liquidity and debt repayment',royco:'Stale marks; asynchronous exit'};
 const dimensions=[['Whole book at T',p=>num(p.capitalETH,0)+' ETH<div class="sub">'+money(p.capitalUSD)+'</div>'],['Collateral → borrowing',p=>esc(route[p.id][0])],['Dollar destination',p=>esc(route[p.id][1])],['30-day ETH book return',p=>num(R.reportContract.matched30dReturns.find(r=>r.id===p.id).bookReturnPct,4)+'%'],['Excess vs stETH, same 30 days',p=>num(R.reportContract.matched30dReturns.find(r=>r.id===p.id).excessPercentagePoints,4)+' pp'],['Fees at T',p=>esc(fees[p.id])],['Holder addresses',p=>esc(p.keyMetrics.find(r=>r.label.includes('Holder'))?.value)],['Operators / infrastructure',p=>esc(operators[p.id])],['Main concern',p=>esc(risks[p.id])]];
 $('#strict-top5-comparison').innerHTML='<table class="product-matrix"><thead><tr><th>Investor question</th>'+PC.products.filter(p=>p.rank<=5).map(p=>'<th><button class="market-text-button" data-carry-product="'+p.id+'">#'+p.rank+' '+esc(p.name)+'</button></th>').join('')+'</tr></thead><tbody>'+dimensions.map(([label,fn])=>'<tr><th scope="row">'+label+'</th>'+PC.products.filter(p=>p.rank<=5).map(p=>'<td>'+fn(p)+'</td>').join('')+'</tr>').join('')+'</tbody></table><p class="note">Whole books overlap and mix strategies. All return cells use 2 September to 2 October 2026; stETH gained '+num(R.reportContract.matched30dReturns[0].benchmarkReturnPct,4)+'%. Book marks exclude external payouts and exit costs. Configured fees are not deducted twice. <a href="data/carry-common-30d.csv" download>Matched return CSV →</a></p>';
}

function readerPlaybook(){
 const rules=[
 ['Earn a positive base spread','Investment income after destination fees must clear the debt cost. Rewards need a separate budget.','The RLUSD scenario is negative before rewards on the dollar leg.'],
 ['Monitor each loan','Set account-specific buffers and test collateral discounts, funding jumps and nested loans.','Liquid’s main ETH loop has HF 1.027; Reservoir adds an inner dollar loan.'],
 ['Prepare the complete exit','Redeem the investment, source the debt token, repay, release collateral and fulfil the queue.','Rocksolid is Closing; tested withdrawals differ from historical paid exits.'],
 ['Reconcile ownership and income','Assign backing, own-credit flows, fees and reward periods before stating carry equity or profit.','Concrete’s shared custody cannot be assigned wholly to Delta.'],
 ['Beat a staking benchmark in cash','Use identical dates and include fees, queues and executable proceeds.','Liquid’s 730-day book excess is 1.36 pp; it is not a carry-only return.']
 ];
 $('#strict-product-rules').innerHTML=stTable(['Design requirement','Test','Observed reason'],rules.map(r=>r.map(esc)));
 const partners=[['Funding counterparty','Debt currency, committed capacity, repricing terms and renewal'],['Curator and strategy operator','Position limits, own-credit policy, repayment automation and incident duties'],['Vault infrastructure','Valuation rights, fee permissions, effective delays and redemption process'],['Distributor','Investor rights, suitability, communication and evidenced acquisition economics'],['Independent reconciliation / liquidity','Assignable backing and an unwind at the intended investor size']];
 $('#strict-partners').innerHTML=stTable(['Responsibility','Evidence required before launch'],partners.map(r=>r.map(esc)))+'<p class="note"><a href="library/CARRY-MATH.html">Observed integrations and detailed selection evidence →</a></p>';
}

function readerCompactProduct(id){
 if(document.body.dataset.edition!=='reader'||id==='closed')return;
 const p=PC.products.find(p=>p.id===id),host=$('#strict-product-content'),c=p.charts;
 const findings={
 yieldbasis:'The WETH pool owes 27.81M crvUSD against 10,426 ETH of net book equity. The unstaked LT mark fell 0.69% over 94 days, versus a 0.57% stETH gain. Staked gauge receipts have separate fee and reward rights.',
 concrete:'A single holder owns the 307,363 ETH claim. Its flat weETH share price tracks staking growth in ETH. Dollar loans sit in shared custody, so Delta’s assets and arbitrage income remain unassigned.',
 liquid:'Liquid combines staking loops and dollar carry. Its two-year ETH book gain is 6.85%, versus 5.49% for stETH. The main Aave ETH loop has HF 1.027 at T; dollar destinations add separate credit and liquidity risks.',
 rocksolid:'Rocksolid holds a 728 ETH claim in Liquity ETH Carry, 7.49% of its book. Direct Aave debt is zero at T. The vault is in Closing and rejects new requests; its historical book still matters.',
 liquity:'The current route pledges 4,585 wstETH to Ebisu and borrows 6.75M ebUSD at a 2.55% annual rate, before extra charges. The dollars enter Curve and Uniswap liquidity. Funded return history begins in March 2026.',
 royco:'Eight addresses hold a 116 ETH book. Fresh reads trace a Morpho wstETH/PYUSD loan and a senior credit receipt, while parent accounting marks are stale. Immediate withdrawal capacity is zero; the documented exit is asynchronous.'
 };
 host.querySelector('.product-title .k').textContent='#'+p.rank+' by sample book size · '+R.reportContract.census.find(r=>r.name===p.name).statusLabel;
 host.querySelector('.product-finding').innerHTML='<p>'+esc(findings[id])+'</p>';
 const matched=R.reportContract.matched30dReturns.find(r=>r.id===id);
 const lastMetric=host.querySelector('.strict-product-metrics > div:last-child');
 lastMetric.querySelector('span').textContent='30-day excess vs stETH';lastMetric.querySelector('b').textContent=num(matched.excessPercentagePoints,4)+' pp';
 const metricNotes=id==='yieldbasis'?['Net fair-value pool book','Direct LT addresses; gauge included','Variable allocation, not a flat fee','Month-end observations, not launch date','Unstaked ETH mark; rewards excluded','Same dates; unstaked mark, not carry profit']:['Whole-product book','Addresses, including contracts','Configured fees at T','Deployment, not public launch','Cumulative ETH book change','Same dates; whole book, not carry profit'];
 host.querySelectorAll('.strict-product-metrics small').forEach((el,i)=>el.textContent=metricNotes[i]);
 host.querySelector('[data-product-part="actors"] .tblwrap').innerHTML=stTable(['Actor','Control','Delay'],p.actors.map(r=>[r.url?a(r.url,r.who):esc(r.who),esc(r.role===r.canChange?r.role:r.role+'. '+r.canChange),esc(r.delay)]));
 host.querySelector('[data-product-part="payers"] .tblwrap').innerHTML=stTable(['Income source'],p.incomePayers.map(r=>{const text=r.text||r.income||r.mechanism||'';return [esc(r.payer)+(text&&text!==r.payer?'<div class="sub">'+esc(text)+'</div>':'')];}));
 const income=host.querySelector('[data-closure-product="income"]');if(income)income.remove();
 const loans=host.querySelector('[data-product-part="loans"] .tblwrap');
 if(loans)loans.innerHTML=stTable(['Loan / chain','Collateral','Debt at T','HF / rate'],c.loanLegs.rows.map(r=>[r.account?a(explorer((r.chain||'Ethereum').toLowerCase(),r.account),r.protocol):esc(r.protocol),esc(r.collateralAsset),money(r.debtUSD)+' '+esc(r.debtAsset),(r.healthFactor==null?'HF not established':num(r.healthFactor,3)+' HF')+'<div class="sub">'+(r.borrowAPR_pct==null?'Rate series unavailable':num(r.borrowAPR_pct,2)+'% APR')+'</div>']));
 if(loans&&id==='yieldbasis')loans.innerHTML=stTable(['Loan / chain','Collateral','Actual debt at T','Debt / net equity'],c.loanLegs.rows.map(r=>[a(r.sourceURLs[0],r.protocol)+'<div class="sub">Ethereum</div>',esc(r.collateralAsset),money(r.debtUSD)+' crvUSD','99.996%<div class="sub">Not collateral LTV; no Aave-style HF</div>']));
 const capital=host.querySelector('[data-product-part="capital"]');
 const debtPanel=host.querySelector('[data-product-part="loans"]');capital.before(debtPanel);

 const windows=Array.from(capital.querySelectorAll('h4')).find(el=>el.textContent==='Matched return windows');
 if(windows){windows.nextElementSibling.innerHTML=stTable(['Window ending at T','ETH book gain'],c.returnVsBorrow.windowReturns.filter(r=>[30,90,94,365,730].includes(r.windowDays)).map(r=>[r.windowDays+' days',r.cumulativeReturnPct==null?'Not measured':num(r.cumulativeReturnPct,2)+'%']));}
 const chartNotes=capital.querySelectorAll('.strict-exhibit > .note');
 if(chartNotes[0])chartNotes[0].textContent=id==='yieldbasis'?'Net fair-value pool book: updated effective LT supply × fair ETH value per share.':'Whole-product book, converted from its underlying asset into ETH at each date.';
 if(chartNotes[1])chartNotes[1].textContent='Cumulative ETH share-value change. Separately paid rewards and withdrawal costs are excluded.';
 if(chartNotes[2])chartNotes[2].textContent='Borrowing APR per loan principal at month end. Missing funded periods stay absent; these are not monthly average costs.';
 const unsupported=capital.querySelector(':scope > .strict-unverified');if(unsupported)unsupported.textContent='A product-attributed borrowing-cost history is unavailable. Current loan balances are shown above.';
 if(id==='yieldbasis')host.querySelector('[data-product-part="timeline"]').remove();
 if(id==='concrete'){const holderPanel=host.querySelector('[data-product-part="holders"]');holderPanel.innerHTML='<h3>Share ownership</h3><p>One positive-balance address owns 100% of the issued shares. This concentration does not establish outside investor capital.</p><details class="more"><summary>Holder address and source ledger</summary><div class="body"><a href="exhibits.html?carryProduct=concrete#strict-product-tabs">Verified balance, distribution data and supply reconciliation →</a></div></details>'; }
 const holderNote=host.querySelector('[data-product-part="holders"] > .note');if(holderNote)holderNote.textContent=c.walletDistribution.scope;
 const exit=host.querySelector('[data-closure-product="exit"]'),bx=BX.products.find(r=>r.id===id);
 if(exit&&bx)exit.innerHTML='<h4>Investor exit at T</h4><div class="tblwrap">'+stTable(['Demand / book','Request accepted','Immediate payment call'],bx.demandScenarios.map(d=>[d.navPct+'%',d.simulatedRequest?'Queued':id==='rocksolid'?'Rejected in Closing':id==='liquid'?'Aggregate request untested':'Separate request route',d.simulatedImmediatePayout?'Succeeds at T':d.withdrawalCall?.response?.error?'Reverts':'Not established']))+'</div><p class="note">Snapshot calls differ from paid withdrawals. The examined historical route has '+num(bx.historicalExits.receiptVerifiedCount)+' receipt-verified payouts. <a href="exhibits.html?carryProduct='+id+'#strict-product-tabs">Demand amounts, coverage and payout receipts →</a></p>';
 const verdict=host.querySelector('.verdict-box');verdict.innerHTML='<b>Read the complete product evidence</b><p><a href="exhibits.html?carryProduct='+id+'#strict-product-tabs">Full mechanics, balances, permissions, dates and limitations →</a></p>';
}

function readerAdjacentCatalogue(q,category){
 const rows=R.carryCategory.products.filter(p=>['E3','E9'].includes(p.classification)&&(q?[p.product,p.collateral,p.debt,p.destination].join(' ').toLowerCase().includes(q):(category==='loops'?p.classification==='E3':category==='basis'?p.classification==='E9':false)));
 if(!rows.length)return '';
 return '<h4>Product examples in this strategy</h4>'+stTable(['Product','Mechanism','Evidence'],rows.map(p=>[esc(p.product),p.classification==='E3'?'Borrow ETH to increase staking exposure':'Hold ETH with an offsetting derivatives short','<a href="'+(p.classification==='E9'?'dossiers/ethena-basis.html':'exhibits.html#products')+'">Product and return analysis →</a>']))+'<p class="note">These examples identify products, rather than additional capital to add to the parent-protocol totals. Ethena’s backing disclosure is separately dated.</p>';
}


function readerAnswer(){
 const c=R.reportContract,h=c.headline;
 $('#strict-count-label').textContent=mactive().length+' of '+MP.categories.length+' groups';
 $('#m-hero-total').textContent=num(h.receiptClaimsETH/1e6,2)+'M';
 $('#m-hero-detail').textContent=money(h.receiptClaimsUSD)+' of reported issuer / security-layer exposure. Overlapping claims; native validator total is separate.';
 $('#strict-carry-share').textContent=String(h.examinedBooks);
 $('#strict-carry-size').textContent=h.currentRoutes+' current traced routes; one Closing, one historical, one unresolved mandate. Capital sizes use whole books.';
 $('#strict-carry-concentration').textContent='+'+num(h.liquid730dExcessPP,2)+' pp';
 $('#strict-carry-concentration-note').textContent='Liquid 6.85% vs stETH 5.49%, 2 Oct 2024 to 2 Oct 2026. Whole-product book return; carry is not isolated.';
 $('#strict-organic-return').textContent=num(h.scenarioCarryWithoutRewardsPP,2)+' pp';
 $('#strict-organic-return-note').textContent='Annual illustration per ETH of equity, before the outer fee. Observed RLUSD loan terms plus a later investment quote; not market performance.';
 $('#m-headline-one').innerHTML='<b>Staking income is reused across the market.</b> Staking receipts become restaking collateral, lending assets and vault holdings. Reported balances grow through these layers; adding them does not reveal unique yield capital.';
}
function readerCoverage(){
 $('#reader-coverage-matrix').innerHTML='<p>Mechanism coverage and financial measurement are separate. Native staking, LPs and mixed allocators cannot be sized by summing receipt claims. The table makes the remaining measurement boundaries explicit.</p><div class="tblwrap">'+stTable(['Yield mechanism','Income source','Capital measured','History','Return evidence'],R.reportContract.coverage.map(r=>['<a href="'+(r.report==='staking-restaking'||r.report==='ethena-basis'||r.report==='pendle-pt'?'dossiers/':'library/')+r.report+'.html">'+esc(r.family)+'</a>',esc(r.income),esc(r.capital),esc(r.history),esc(r.returns)]))+'</div><p class="note"><a href="library/MARKET-COVERAGE.html">Coverage decisions and unmeasured boundaries →</a> · <a href="data/report_contract.json" download>Canonical answers and sources →</a></p>';
}
