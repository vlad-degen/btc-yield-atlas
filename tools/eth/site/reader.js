// The primary reading route mounts only the eight report chapters.
function readerCarryRows(){
 return R.carryCategory.products.filter(p=>p.classification==='E4').map(p=>{
 const c=PC.products.find(c=>c.name.toLowerCase()===p.product.toLowerCase());
 const x=R.carryExpansion?.products.find(x=>x.address?.toLowerCase()===p.address?.toLowerCase());
 return {...p,chapter:c,...(c?.liveRoute||{}),...(x?{collateral:x.collateral,debt:x.debt,destination:x.destination,status:x.status}:{}),name:p.product};
 }).sort((a,b)=>b.sizeETH-a.sizeETH);
}
const READER_STATUS={'Concrete Delta weETH':'Shared backing unresolved','ether.fi Liquid ETH':'Active hybrid','Rocksolid rETH':'Closing; nested carry','Liquity ETH Carry':'Active Ebisu loan','Royco ETH':'Stale parent marks; loan traced','TAU InfiniFi ETH Carry':'Historical carry; dust debt at T','Reservoir ETH Yield':'Small current position'};
const READER_ROUTES={
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
function readerCarryTable(){const rows=readerCarryRows(),sum=msum(rows,'sizeETH');return stTable(['Product','Whole book at T','Share of seven books','How it earns'],rows.map(p=>{const route=READER_ROUTES[p.name],chapter=p.chapter,href=chapter?'?carryProduct='+chapter.id+'#strict-product-tabs':'library/CARRY-VARIANTS-EXPANSION.html';return [`<a href="${href}" ${chapter?'data-carry-product="'+chapter.id+'"':''}><b>${esc(p.name)}</b></a><div class="sub">${esc(READER_STATUS[p.name])}</div>`,num(p.sizeETH,1)+' ETH<div class="sub">'+money(p.sizeUSD)+'</div>',pct(p.sizeETH/sum,p.sizeETH/sum<.0001?3:2),esc(route[1])];}),'reader-carry-products');}
function readerCarryComposition(){const rows=readerCarryRows(),sum=msum(rows,'sizeETH');$('#reader-carry-bars').innerHTML=horizontalBars(rows.map((p,i)=>({name:p.name,base:p.sizeETH,total:p.sizeETH,color:CARRY_COLORS[i]})),{format:v=>chartShort(v,n=>num(n,0)+' ETH'),label:'Seven measured carry-design books, whole product NAV'});$('#reader-carry-composition').innerHTML=readerCarryTable();$('#reader-carry-scope').textContent='Seven examined products: '+num(sum,0)+' ETH of whole-product book claims. Concrete and Liquid are hybrid parents; Rocksolid includes 728 ETH of Liquity claims. These sizes describe the products, not unique dollars deployed in carry. The market category above counts two protocol parents; their adapter values use a different price convention.';}
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
 const risks={'Concrete Delta weETH':'Shared custody and unassigned assets','ether.fi Liquid ETH':'Funding, credit and withdrawal liquidity','Rocksolid rETH':'Closing state and nested claims','Liquity ETH Carry':'ETH price, ebUSD liquidity and LP unwind','Royco ETH':'Stale marks and asynchronous withdrawal','TAU InfiniFi ETH Carry':'Two loan layers; current debt is dust','Reservoir ETH Yield':'Two dollar loans and savings redemption','Concrete wstETH Plus':'Shared debt does not establish the strategy','Fluid Lite ETH V2':'Staking spread and unwind capacity','Treehouse tETH':'Staking spread and exit costs','CIAN rsETH':'Restaking, leverage and token redemption','Midas mRe7ETH':'Stale mark; portfolio not reconstructed','Midas mHyperETH':'Stale mark; portfolio not reconstructed','Ethena ETH backing leg':'Hedge, custody and dollar redemption'};
 const rows=R.carryCategory.products.filter(p=>p.classification==='E4').map(p=>{
 const chapter=PC.products.find(c=>c.name.toLowerCase()===p.product.toLowerCase()),extra=R.carryExpansion.products.find(x=>x.address?.toLowerCase()===p.address?.toLowerCase()),route=READER_ROUTES[p.product];
 const book=extra?.navT?.eth??p.sizeETH,usd=extra?.navT?.usd??p.sizeUSD;
 const label=p.classification==='E4'?'Dollar carry':p.classification==='E3'?'ETH loop':p.classification==='E9'?'Basis':'Route unverified';
 const status=READER_STATUS[p.product]||(extra?.navT?.oracle_age_days_at_T?'Mark '+num(extra.navT.oracle_age_days_at_T,1)+' days old':label);
 const returnRow=chapter?.charts.returnVsBorrow.windowReturns?.filter(w=>[365,90,30].includes(w.windowDays)).sort((a,b)=>b.windowDays-a.windowDays).find(w=>w.cumulativeReturnPct!=null);
 const loopName={'Fluid Lite ETH V2':'Fluid Lite ETH','Treehouse tETH':'Treehouse tETH','CIAN rsETH':'CIAN rsETH'}[p.product],loopReturn=loopName?R.returns.find(r=>r.product===loopName&&r.days===365):null;
 const measuredReturn=returnRow?num(returnRow.windowDays)+'d: '+num(returnRow.cumulativeReturnPct,2)+'%':loopReturn?.ETH_pps_cumulative_return!=null?'365d: '+pct(loopReturn.ETH_pps_cumulative_return,2):'Not measured';
 const href=chapter?'?carryProduct='+chapter.id+'#strict-product-tabs':p.classification==='E3'?'exhibits.html#products':p.classification==='E9'?'dossiers/ethena-basis.html':'library/CARRY-VARIANTS-EXPANSION.html';
 const mechanism=route?.[1]||(p.classification==='E3'?'Borrow ETH to buy more staking exposure':p.classification==='E9'?'Hold ETH and an offsetting derivatives short':'Managed ETH product; dollar financing unverified');
 return [`<a href="${href}" ${chapter?'data-carry-product="'+chapter.id+'"':''}><b>${esc(p.product)}</b></a>`,esc(label)+'<div class="sub">'+esc(status)+'</div>',esc(mechanism),measuredReturn+'<div class="sub">ETH book change</div>',book==null?'Not measured':num(book,1)+' ETH<div class="sub">'+money(usd)+'</div>',esc(risks[p.product])];
 });
 $('#strict-landscape').innerHTML=stTable(['Product','Type / status','How it earns','Measured return','Whole book at T','Main risk'],rows,'reader-landscape-table');
 $('#strict-census-note').textContent='Returns are whole-product ETH book changes over the stated period. Historical designs and nested books are included; these rows are not additive carry equity.';
 $('#reader-carry-candidates').innerHTML=stTable(['Product','Measured book','Why verification is pending'],R.carryCategory.products.filter(p=>!['E3','E4','E9'].includes(p.classification)).map(p=>[esc(p.product),p.sizeETH==null?'Not measured':num(p.sizeETH,0)+' ETH','Dollar-funded investment route unverified. <a href="library/CARRY-VARIANTS-EXPANSION.html">Position review →</a>']));
}
function readerBorrowingTable(){
 const reserves=R.readerAnalysis.funding.map(r=>['Aave V3 / '+esc(r.chain),'ETH-family eligibility',esc(r.symbol==='USDCn'?'native USDC':r.symbol),pct(r.borrow_apr,2),money(r.cash_USD)]);
 const loans=EC.borrow_markets.filter(r=>r.observed_product_debt_units>=1).map(r=>[a(r.links?.market,r.venue)+' / '+esc(r.chain),esc(r.collateral_symbol),esc(r.loan_symbol),pct(r.borrow_apr,2),r.reserve_cash_units==null?'Not reported':num(r.reserve_cash_units,0)+' '+esc(r.loan_symbol)]);
 $('#strict-borrow-markets').innerHTML=stTable(['Lender / chain','Collateral','Debt token','Borrow APR at T','Reserve cash'],[...reserves,...loans])+'<p class="note">APR is a snapshot, not an average or a committed offer. The Morpho rows are markets used by tracked Liquid accounts. Reserve cash does not guarantee an account can borrow. <a href="library/DOLLAR-FUNDING-ATLAS.html">All currencies, caps and lenders →</a></p>';
 $('#strict-curve-note').innerHTML='Stored rate-model parameters at T, varying utilization. The curve illustrates repricing, rather than a forecast. <a href="library/CARRY-MATH.html">Model and contract verification →</a>';
}

function readerCarryWaves(){
 const books=R.readerAnalysis.books,book=name=>books.find(p=>p.name===name),liquid=book('ether.fi Liquid ETH'),reservoir=book('Reservoir ETH Yield'),tau=book('TAU InfiniFi ETH Carry');
 const waves=[
 ['Oct 2024 to Aug 2025','Liquid establishes the large hybrid book','The measured book starts at '+num(liquid.history[0].eth,0)+' ETH and peaks at '+num(liquid.peak.eth,0)+' ETH in '+liquid.peak.month+'. It combines staking loops and dollar carry. The whole-book history cannot isolate the historical dollar allocation.','?carryProduct=liquid#strict-product-tabs'],
 ['Sep to Dec 2025','New wrappers and nested financing','Rocksolid and Reservoir acquire material balances in September. Reservoir peaks at '+num(reservoir.peak.eth,0)+' ETH in October. Concrete’s '+num(book('Concrete Delta weETH').history.find(r=>r.month==='2025-12').eth,0)+' ETH claim appears in December; its issuance still needs an outside-capital reconciliation.','library/CARRY-VARIANTS-EXPANSION.html'],
 ['Jan to Sep 2026','Routes grow, change and unwind','TAU peaks at '+num(tau.peak.eth,0)+' ETH in January, but has only dust USDC debt at T. Liquity first exceeds 1 ETH in March and reaches '+num(book('Liquity ETH Carry').history.at(-1).eth,0)+' ETH by September. Rocksolid then enters Closing on 29 September. Product names persist while financing and exits change.','library/CARRY-PRODUCTS.html']
 ];return waves.map(w=>'<div><div class="k">'+esc(w[0])+'</div><h4>'+esc(w[1])+'</h4><p>'+esc(w[2])+'</p><a href="'+w[3]+'">Evidence →</a></div>').join('');
}
function readerResearchSynthesis(){
 $('#reader-earned-carry').innerHTML='<p><b>Income can still fall short of the loan.</b> In three traced USDC and PYUSD investments, measured destination income did not cover the allocated funding cost. These are investment-leg results, rather than whole-wallet profit. <a href="library/CARRY-LIFECYCLES.html">Transactions and calculations →</a></p>';
 $('#reader-borrower-use').innerHTML='<p><b>A large loan is not automatically carry.</b> Sampled large-borrower loans also fund transfers, refinancing and currency conversion. <a href="library/BORROWER-USE.html">Identities and use of proceeds →</a></p>';
 readerComparison();readerPlaybook();
}

function readerComparison(){
 const route={concrete:['weETH → shared dollar loans','Published neutral arbitrage; allocation unverified'],liquid:['weETH / wstETH → dollar loans','Cap and Sentora credit vaults'],rocksolid:['Liquity shares → underlying ebUSD loan','Nested Liquity carry and other strategies'],liquity:['wstETH → ebUSD','Curve and Uniswap liquidity'],royco:['wstETH → PYUSD','Senior dollar-credit receipt']};
 const fees={concrete:'0% configured; private fees unknown',liquid:'0.35% management',rocksolid:'1% management / 10% performance',liquity:'0.5% management / 10% performance',royco:'0% management / 10% performance'};
 const operators={concrete:'Concrete / shared custody Safe',liquid:'ether.fi / Veda / Nonce',rocksolid:'Rocksolid / Tulipa',liquity:'Sentinel / Fusion',royco:'Dialectic / Concrete / Makina'};
 const risks={concrete:'Shared assets and outside capital unresolved',liquid:'Thin loop headroom; funding and credit exposure',rocksolid:'Closing; overlaps Liquity’s book',liquity:'ebUSD liquidity and debt repayment',royco:'Stale marks; asynchronous exit'};
 const dimensions=[['Whole book at T',p=>num(p.capitalETH,0)+' ETH<div class="sub">'+money(p.capitalUSD)+'</div>'],['Collateral → borrowing',p=>esc(route[p.id][0])],['Dollar destination',p=>esc(route[p.id][1])],['ETH book gain',p=>(p.charts.returnVsBorrow.windowReturns||[]).filter(r=>[90,365].includes(r.windowDays)).map(r=>r.windowDays+'d: '+num(r.cumulativeReturnPct,2)+'%').join('<br>')||'Not measured'],['Fees at T',p=>esc(fees[p.id])],['Holder addresses',p=>esc(p.keyMetrics.find(r=>r.label.includes('Holder'))?.value)],['Operators / infrastructure',p=>esc(operators[p.id])],['Main concern',p=>esc(risks[p.id])]];
 $('#strict-top5-comparison').innerHTML='<table class="product-matrix"><thead><tr><th>Investor question</th>'+PC.products.map(p=>'<th><button class="market-text-button" data-carry-product="'+p.id+'">#'+p.rank+' '+esc(p.name)+'</button></th>').join('')+'</tr></thead><tbody>'+dimensions.map(([label,fn])=>'<tr><th scope="row">'+label+'</th>'+PC.products.map(p=>'<td>'+fn(p)+'</td>').join('')+'</tr>').join('')+'</tbody></table><p class="note">Whole books can overlap and contain other strategies. Book gains exclude separately paid rewards and withdrawal costs. Carry profit is not independently isolated. Fee settings are dated contract observations; later published terms can differ.</p>';
}

function readerPlaybook(){
 const labels=['Observed RLUSD loan','Ethereum USDC scenario','RLUSD without rewards','RLUSD funding +3 pp'];
 $('#strict-playbook-scenarios').innerHTML=stTable(['Scenario','Borrow / invest, annual','Net ETH income','Without rewards'],EC.playbook.scenarios.map((p,i)=>{const r=stCalcResult(p.inputs);return [labels[i],pct(p.inputs.borrow_rate,2)+' / '+pct(p.inputs.parking_rate,2),pct(r.net,2),pct(r.noRewards,2)];}))+'<p class="note">These use the calculator’s assumptions. Net income includes the staking baseline; the incremental carry contribution can be negative. <a href="library/CARRY-MATH.html">Scenario inputs and calculations →</a></p>';
 const rewards=EC.playbook.reward_payers.filter(r=>r.income_type==='External incentive program');
 $('#strict-reward-payers').innerHTML=stTable(['Campaign','Reported reward APY','Verified sponsor'],rewards.map(r=>[esc(r.venue),pct(r.reward_apy,2)+' · '+esc(r.reward_asset),'Not established']))+'<p class="note">Reward-asset identity does not identify the campaign funder. Confirm the funding wallet, budget and expiry. Ordinary lending income comes from borrowers. <a href="library/CARRY-MATH.html">Payers and source evidence →</a></p>';
 const rules=[
 ['Require a positive base spread','Income after fees must clear loan cost','RLUSD base yield is below its funding cost.'],
 ['Watch each borrowing account','Illustrative HF floor 1.25, plus collateral stress','Liquid’s main ETH loop has HF 1.027; aggregation hides this.'],
 ['Stress rates and rewards together','Remove incentives; add 3 pp funding cost','The RLUSD scenario then has negative total income.'],
 ['Prepare the full exit','Redeem investments, source debt tokens, repay and release','Queues and lender cash constrain different stages.'],
 ['Expose self-credit and nested loans','Separate external income and test every loan layer','Liquid lends back to itself; Reservoir has two loans.'],
 ['Apply each fee once','Separate outer NAV fees and destination fees','Destination share values already recognise their own fees.'],
 ['Stress prices and custody','Test collateral discounts, stablecoins, bridges and marks','Book value does not establish executable proceeds.']
 ];
 $('#strict-product-rules').innerHTML=stTable(['Rule','Operating test','Market evidence'],rules.map(r=>r.map(esc)))+'<p class="note"><a href="library/CARRY-MATH.html">Full rules, assumptions and measured constraints →</a></p>';
 const partners=[['Dollar funding','Stablecoin ecosystems / Sentora','Committed currency, cash, budget and renewal terms'],['Curation','Sentora and comparable curators','Concentration, caps, fee rights and loss allocation'],['Vault infrastructure','Veda','Price, fee and withdrawal permissions; effective delays'],['Strategy operation','Nonce','Repayment automation, incident response and reporting'],['Distribution','ether.fi; exchange and broker channels','Holder rights, exit communication and commercial economics'],['Independent review / liquidity','Contract reviewers and repayment counterparties','Backing reconciliation and an unwind at the intended size']];
 $('#strict-partners').innerHTML=stTable(['Role','Candidate / observed reference','What to verify'],partners.map(r=>r.map(esc)))+'<p class="note">Observed integrations are diligence starting points. Commercial terms and capacity are unconfirmed. <a href="library/CARRY-MATH.html">Selection evidence →</a></p>';
}

function readerCompactProduct(id){
 if(document.body.dataset.edition!=='reader'||id==='closed')return;
 const p=PC.products.find(p=>p.id===id),host=$('#strict-product-content'),c=p.charts;
 const findings={
 concrete:'One address holds the 307,363 ETH book. Its share price stays flat in weETH; ETH growth follows the staking conversion. Verified borrowing sits in a shared Safe, so assets and private arbitrage income cannot be assigned wholly to Delta.',
 liquid:'Liquid combines staking loops and dollar carry. Its two-year ETH book gain is 6.85%, versus 5.49% for stETH. The main Aave ETH loop has HF 1.027 at T; dollar destinations add separate credit and liquidity risks.',
 rocksolid:'Rocksolid holds a 728 ETH claim in Liquity ETH Carry, 7.49% of its book. Direct Aave debt is zero at T. The vault is in Closing and rejects new requests; its historical book still matters.',
 liquity:'The current route pledges 4,585 wstETH to Ebisu and borrows 6.75M ebUSD at a 2.55% annual rate, before extra charges. The dollars enter Curve and Uniswap liquidity. Funded return history begins in March 2026.',
 royco:'Eight addresses hold a 116 ETH book. Fresh reads trace a Morpho wstETH/PYUSD loan and a senior credit receipt, while parent accounting marks are stale. Immediate withdrawal capacity is zero; the documented exit is asynchronous.'
 };
 host.querySelector('.product-finding').innerHTML='<p>'+esc(findings[id])+'</p>';
 const metricNotes=['Whole-product book','Addresses, including contracts','Configured fees at T','Deployment, not public launch','Cumulative book gain','Whole-book income mixes strategies'];
 host.querySelectorAll('.strict-product-metrics small').forEach((el,i)=>el.textContent=metricNotes[i]);
 host.querySelector('[data-product-part="actors"] .tblwrap').innerHTML=stTable(['Actor','Control','Delay'],p.actors.map(r=>[r.url?a(r.url,r.who):esc(r.who),esc(r.role===r.canChange?r.role:r.role+'. '+r.canChange),esc(r.delay)]));
 host.querySelector('[data-product-part="payers"] .tblwrap').innerHTML=stTable(['Income source'],p.incomePayers.map(r=>{const text=r.text||r.income||r.mechanism||'';return [esc(r.payer)+(text&&text!==r.payer?'<div class="sub">'+esc(text)+'</div>':'')];}));
 const income=host.querySelector('[data-closure-product="income"]');if(income)income.innerHTML='<p class="note">Historical carry profit remains unallocated. <a href="exhibits.html#carry-earned-income">Income, debt costs and reward evidence →</a></p>';
 const capital=host.querySelector('[data-product-part="capital"]');
 const windows=Array.from(capital.querySelectorAll('h4')).find(el=>el.textContent==='Matched return windows');
 if(windows){windows.nextElementSibling.innerHTML=stTable(['Window ending at T','ETH book gain'],c.returnVsBorrow.windowReturns.filter(r=>[30,90,365,730].includes(r.windowDays)).map(r=>[r.windowDays+' days',r.cumulativeReturnPct==null?'Not measured':num(r.cumulativeReturnPct,2)+'%']));}
 const chartNotes=capital.querySelectorAll('.strict-exhibit > .note');
 if(chartNotes[0])chartNotes[0].textContent='Whole-product book, converted from its underlying asset into ETH at each date.';
 if(chartNotes[1])chartNotes[1].textContent='Cumulative ETH share-value change. Separately paid rewards and withdrawal costs are excluded.';
 if(chartNotes[2])chartNotes[2].textContent='Borrowing APR per loan principal at month end. Missing funded periods stay absent; these are not monthly average costs.';
 const unsupported=capital.querySelector(':scope > .strict-unverified');if(unsupported)unsupported.textContent='A product-attributed borrowing-cost history is unavailable. See the loan balances below.';
 const holderNote=host.querySelector('[data-product-part="holders"] > .note');if(holderNote)holderNote.textContent='Reconstructed holder addresses at T, including contracts. Cross-chain distributions are separate.';
 const exit=host.querySelector('[data-closure-product="exit"]'),bx=BX.products.find(r=>r.id===id);
 if(exit&&bx)exit.innerHTML='<h4>Investor exit at T</h4><div class="tblwrap">'+stTable(['Demand / book','Request accepted','Immediate payment call'],bx.demandScenarios.map(d=>[d.navPct+'%',d.simulatedRequest?'Queued':id==='rocksolid'?'Rejected in Closing':id==='liquid'?'Aggregate request untested':'Separate request route',d.simulatedImmediatePayout?'Succeeds at T':d.withdrawalCall?.response?.error?'Reverts':'Not established']))+'</div><p class="note">Snapshot calls differ from paid withdrawals. The examined historical route has '+num(bx.historicalExits.receiptVerifiedCount)+' receipt-verified payouts. <a href="exhibits.html?carryProduct='+id+'#strict-product-tabs">Demand amounts, coverage and payout receipts →</a></p>';
 const verdict=host.querySelector('.verdict-box');verdict.innerHTML='<b>Read the complete product evidence</b><p><a href="exhibits.html?carryProduct='+id+'#strict-product-tabs">Full mechanics, balances, permissions, dates and limitations →</a></p>';
}

function readerAdjacentCatalogue(q,category){
 const rows=R.carryCategory.products.filter(p=>['E3','E9'].includes(p.classification)&&(q?[p.product,p.collateral,p.debt,p.destination].join(' ').toLowerCase().includes(q):(category==='loops'?p.classification==='E3':category==='basis'?p.classification==='E9':false)));
 if(!rows.length)return '';
 return '<h4>Product examples in this strategy</h4>'+stTable(['Product','Mechanism','Evidence'],rows.map(p=>[esc(p.product),p.classification==='E3'?'Borrow ETH to increase staking exposure':'Hold ETH with an offsetting derivatives short','<a href="'+(p.classification==='E9'?'dossiers/ethena-basis.html':'exhibits.html#products')+'">Product and return analysis →</a>']))+'<p class="note">These examples identify products, rather than additional capital to add to the parent-protocol totals. Ethena’s backing disclosure is separately dated.</p>';
}
