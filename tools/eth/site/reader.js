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
function readerCarryTable(){const rows=readerCarryRows(),sum=msum(rows,'sizeETH');return stTable(['Product','Whole book at T','Share of seven books','Borrowing venue','Dollar destination','Operators / infrastructure'],rows.map(p=>{const route=READER_ROUTES[p.name],chapter=p.chapter,href=chapter?'?carryProduct='+chapter.id+'#strict-product-tabs':'library/CARRY-VARIANTS-EXPANSION.html';return [`<a href="${href}" ${chapter?'data-carry-product="'+chapter.id+'"':''}><b>${esc(p.name)}</b></a><div class="sub">${esc(READER_STATUS[p.name])}</div>`,num(p.sizeETH,1)+' ETH<div class="sub">'+money(p.sizeUSD)+'</div>',pct(p.sizeETH/sum,p.sizeETH/sum<.0001?3:2),esc(route[0]),esc(route[1]),esc(route[2])];}),'reader-carry-products');}
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
 renderResearchAdditions();initMarket();initStrictResearch();readerCarryComposition();readerRouteTable();readerLandscape();readerBorrowingTable();
 const observer=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting)$$('nav.sec a').forEach(a=>a.setAttribute('aria-current',String(a.hash==='#'+e.target.id)));}),{rootMargin:'-10% 0px -75% 0px'});$$('main>section').forEach(s=>observer.observe(s));
 window.addEventListener('hashchange',openHash);openHash(true);document.documentElement.dataset.loaded='true';
}
function readerLandscape(){
 const risks={'Concrete Delta weETH':'Shared custody and unassigned assets','ether.fi Liquid ETH':'Funding, credit and withdrawal liquidity','Rocksolid rETH':'Closing state and nested claims','Liquity ETH Carry':'ETH price, ebUSD liquidity and LP unwind','Royco ETH':'Stale marks and asynchronous withdrawal','TAU InfiniFi ETH Carry':'Two loan layers; current debt is dust','Reservoir ETH Yield':'Two dollar loans and savings redemption','Concrete wstETH Plus':'Shared debt does not establish the strategy','Fluid Lite ETH V2':'Staking spread and unwind capacity','Treehouse tETH':'Staking spread and exit costs','CIAN rsETH':'Restaking, leverage and token redemption','Midas mRe7ETH':'Stale mark; portfolio not reconstructed','Midas mHyperETH':'Stale mark; portfolio not reconstructed','Ethena ETH backing leg':'Hedge, custody and dollar redemption'};
 const rows=R.carryCategory.products.map(p=>{
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
 $('#strict-census-note').textContent='Returns are accumulated ETH book changes over the stated window. Whole books can overlap and can contain other strategies. The census includes historical carry and unverified designs; it is not a sum of current carry equity.';
}
function readerBorrowingTable(){
 const host=$('#strict-borrow-markets'),full=host.innerHTML,table=host.querySelector('table').cloneNode(true),observed=EC.borrow_markets.map((m,i)=>m.observed_product_debt_units!=null?i:-1).filter(i=>i>=0);
 [...table.tBodies[0].rows].forEach((row,i)=>{if(!observed.includes(i))row.remove();else{const m=EC.borrow_markets[i];row.cells[7].innerHTML='Liquid ETH tracked accounts<div class="sub">'+num(m.observed_product_debt_units,m.observed_product_debt_units<1?6:0)+' '+esc(m.loan_symbol)+'</div>'+(m.health_factor==null?'':'<div class="sub">Account HF '+num(m.health_factor,3)+'</div>');}});
 host.replaceChildren(table);host.insertAdjacentHTML('beforeend','<p class="note">These three rows have a tracked Liquid ETH dollar loan in this dataset. Product chapters also trace Ebisu carry, nested savings loans and Royco’s separate senior-credit route.</p><details class="more"><summary>All 22 financing markets, reserve cash and borrowing terms</summary><div class="body">'+full+'</div></details>');
}
