// Counted-once ETH market and the answer, in the BTC atlas's style. Loaded last in the reader:
// the function declarations below replace market.js's text-producing functions (hoisting), and the
// assignments at the bottom replace the hero writers of the earlier layers.
try{if(localStorage.getItem('eth-atlas-v2')!=='1'){localStorage.removeItem('eth-research-eight-categories');localStorage.setItem('eth-atlas-v2','1');}}catch{}

// Concrete Delta is one principal's own position, not a pooled product (research/eth/en/gaps/CONCRETE-DELTA.md):
// out of the carry history chart, shown under Other carry.
if(R.readerAnalysis?.books)R.readerAnalysis.books=R.readerAnalysis.books.filter(b=>b.name!=='Concrete Delta weETH');
const ATK=v=>v==null?'n/a':Math.abs(v)>=1e6?num(v/1e6,2)+'M':Math.abs(v)>=1e4?num(v/1e3,0)+'k':num(v,0);
const ATUSD=v=>v==null?'n/a':'$'+(Math.abs(v)>=1e9?num(v/1e9,1)+'B':Math.abs(v)>=1e6?num(v/1e6,0)+'M':num(v,0));
const ATPCT=(v,d=1)=>v==null?'n/a':num(v*100,d)+'%';
const ATMON=p=>{const [y,m]=String(p).split('-');return ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][+m-1]+' '+y;};
const ATKINDS={farming:[['pools','Liquidity pools','DEX, perp and bridge pools. Only the plain ETH side is counted; the staking-token side of an ETH/LST pool stays with its issuer.'],['vaults','Strategy vaults','Managed vaults that lend, loop or provide liquidity on the depositor’s behalf.'],['points','Points farming','ETH parked for points or a future token: pre-deposits for new chains and lock-ups.']]};
const atRows=cat=>MP.products.filter(p=>p.category===cat&&p.current?.status==='observed'&&(p.current.eth_ref||0)>=0.5).sort((a,b)=>b.current.eth_ref-a.current.eth_ref);
const atCatSize=cat=>msum(atRows(cat).map(p=>p.current),'eth_ref');
const atHist=cat=>MP.months.map(m=>m.by_category[cat]?.eth_ref||0);

function stMarketMechanism(p){return p.how_earns||'';}
function stMarketOperator(p){return p.operator||'';}

function atTable(rows,base,{limit=8,id='',showCat=false}={}){
 const body=rows.map((p,i)=>{const r=p.current;return `<tr${i>=limit?' class="more-row" hidden':''}><td><b>${p.official_url?a(p.official_url,p.name):esc(p.name)}</b>${p.flag?`<div class="sub">${esc(p.flag)}</div>`:''}</td>${showCat?`<td>${esc(mcat(p.category).label)}</td>`:''}<td class="n">${num(r.eth_ref,0)}<div class="sub">${ATUSD(r.usd)}</div></td><td class="n">${base?ATPCT(r.eth_ref/base):''}</td><td>${esc(p.how_earns||'')}</td><td>${esc(p.yield||'')}</td><td>${esc(p.operator||'')}</td></tr>`;}).join('');
 return `<div class="tblwrap"><table class="at-table" ${id?`id="${id}"`:''}><thead><tr><th>Product</th>${showCat?'<th>Category</th>':''}<th class="n">ETH</th><th class="n">Share</th><th>What it does</th><th>What it pays, %</th><th>Run by</th></tr></thead><tbody>${body||'<tr><td colspan="7" class="empty">Nothing here.</td></tr>'}</tbody></table></div>`+(rows.length>limit?`<button class="btn" data-at-more>Show all ${rows.length}</button>`:'');
}

function atEnded(cat,kind){
 // products whose month-end balance passed 1,000 ETH and that hold under 5% of that peak now
 const rows=MP.products.filter(p=>p.category===cat&&(!kind||p.subtype===kind)).map(p=>{const pk=p.peak?.eth_ref;return pk&&pk.value>=1000&&(p.current.eth_ref||0)<pk.value*0.05?{p,pk}:null}).filter(Boolean).sort((x,y)=>y.pk.value-x.pk.value);
 if(!rows.length)return '';
 return `<p class="note cx-ended"><b>Emptied since 2024:</b> ${rows.slice(0,8).map(({p,pk})=>`${esc(p.name)} (${ATK(pk.value)} ETH in ${ATMON(pk.period)}, ${ATK(p.current.eth_ref||0)} now)`).join('; ')}${rows.length>8?`; ${rows.length-8} more`:''}.</p>`;
}

function marketCatalogue(){
 const q=$('#m-product-search').value.toLowerCase().trim(),total=marketTotals();
 $('#m-category-tabs').innerHTML=MP.categories.map(c=>{const v=atCatSize(c.id),on=MS.selected.has(c.id);return `<button role="tab" id="m-tab-${c.id}" aria-controls="m-category-body" aria-selected="${MS.category===c.id&&!q}" tabindex="${MS.category===c.id?0:-1}" data-market-pick="${c.id}" style="--col:${c.color}"><i></i>${esc(c.label)}<small>${ATK(v)} ETH · ${on&&total.eth_ref?ATPCT(v/total.eth_ref):'not counted'}</small></button>`}).join('');
 const body=$('#m-category-body');
 if(q){const rows=MP.products.filter(p=>(p.current.eth_ref||0)>=0.5&&[p.name,p.id,p.how_earns,p.operator,p.yield,mcat(p.category).label].join(' ').toLowerCase().includes(q)).sort((a,b)=>b.current.eth_ref-a.current.eth_ref);body.removeAttribute('aria-labelledby');body.innerHTML=`<div class="cx"><p class="note">${rows.length?rows.length+' product'+(rows.length===1?'':'s')+' match':'Nothing matches'} “${esc(q)}”.</p>${rows.length?atTable(rows,total.eth_ref,{limit:40,showCat:true}):''}</div>`;return;}
 const c=mcat(MS.category),rows=atRows(c.id),size=atCatSize(c.id),on=MS.selected.has(c.id),hv=atHist(c.id),pk=hv.indexOf(Math.max(...hv));
 body.setAttribute('aria-labelledby','m-tab-'+c.id);
 let h=`<div class="cx${on?'':' off'}"><div class="cx-h"><h4 class="h4"><i style="background:${c.color}"></i>${esc(c.label)} <span class="offtag">not counted</span></h4><div class="kval"><b>${num(size,0)} ETH</b><small>${on&&total.eth_ref?ATPCT(size/total.eth_ref)+' of the map · ':''}${rows.length} product${rows.length===1?'':'s'}</small></div></div><p class="kd">${esc(c.how)}</p><div class="cx-facts"><span>Paid by <b>${esc(c.payer)}</b></span>${hv[pk]>0?`<span>Month-end peak <b>${ATK(hv[pk])} ETH</b> in ${ATMON(MP.months[pk].period)}</span><span>Two years ago <b>${ATK(hv[0])} ETH</b></span>`:''}</div>`;
 const kinds=ATKINDS[c.id];
 if(kinds)kinds.forEach(([k,name,what])=>{const rk=rows.filter(p=>p.subtype===k);if(!rk.length)return;const bk=msum(rk.map(p=>p.current),'eth_ref');h+=`<div class="cx-kind"><div class="cx-h"><h4 class="h4">${esc(name)}</h4><div class="kval"><b>${num(bk,0)} ETH</b><small>${size?Math.round(bk/size*100)+'% of the category · ':''}${rk.length} products</small></div></div><p class="kd">${esc(what)}</p>${atTable(rk,size,{limit:5})}${atEnded(c.id,k)}</div>`;});
 else h+=atTable(rows,size)+atEnded(c.id);
 body.innerHTML=h+'</div>';
}
document.addEventListener('click',e=>{const b=e.target.closest('[data-at-more]');if(!b)return;const t=b.previousElementSibling;t.querySelectorAll('tr.more-row').forEach(r=>r.hidden=!r.hidden);const open=!t.querySelector('tr.more-row[hidden]');b.textContent=open?'Show fewer':'Show all '+t.querySelectorAll('tbody tr').length;});

function atShareOf(cat,period){const m=period==null?MP.current:MP.months.find(x=>x.period===period);const tot=mactive().reduce((s,c)=>s+(m.by_category[c.id]?.eth_ref||0),0);return tot?(m.by_category[cat]?.eth_ref||0)/tot:null;}

function marketRender(){
 marketSwitches();$$('#m-cohort-controls button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.marketCohort===MS.cohort)));
 const active=mactive(),total=marketTotals(),cats=active.map(c=>({...c,eth_ref:atCatSize(c.id),usd:msum(atRows(c.id).map(p=>p.current),'usd')})).sort((a,b)=>b.eth_ref-a.eth_ref);
 $('#strict-count-label').textContent=active.length===MP.categories.filter(c=>c.default).length&&active.every(c=>c.default)?'all yield categories':active.length+' of '+MP.categories.length+' categories';
 $('#m-selection').innerHTML=active.length===MP.categories.length?'Every category, money markets and CDPs included.':`Counting: ${active.map(c=>esc(c.label)).join(', ')||'nothing'}.`;
 $('#m-donut').innerHTML=marketDonut(MP.products.filter(p=>(p.current.eth_ref||0)>=0.5),total).replace('layered exposure','counted once');
 $('#m-category-summary tbody').innerHTML=cats.map(c=>`<tr><td><button class="market-text-button" data-market-pick="${c.id}"><i class="pdot" style="background:${c.color}"></i>${esc(c.label)}</button></td><td class="n">${num(c.eth_ref,0)}</td><td class="n">${ATUSD(c.usd)}</td><td class="n">${total.eth_ref?ATPCT(c.eth_ref/total.eth_ref):''}</td></tr>`).join('');
 $('#m-map-findings').innerHTML=atMapFindings(total);
 const series=marketSeries();
 $('#m-history-chart').innerHTML=series.some(s=>s.points.some(p=>p[1]!=null))?marketHistoryChart(series,{share:MS.mode==='share',label:'ETH earning a yield by category, month-end',format:v=>mfmt(v)}):'<div class="empty">Select a category.</div>';
 $('#m-history-scope').textContent=MS.cohort==='constant'?'Same products: only the '+MP.constant_cohort_count+' products that held ETH at every month-end.':'All products, as they existed each month. DEX pools without a token breakdown have history only for pools still above $1M today.';
 $('#m-history-tooltip').textContent='Hover a month to see its split.';
 $('#m-history-table thead').innerHTML='<tr><th>Month</th>'+series.map(s=>`<th class="n">${esc(s.name)}</th>`).join('')+'<th class="n">Total</th></tr>';
 $('#m-history-table tbody').innerHTML=MP.months.map((m,i)=>{const t=msum(series.map(s=>({v:s.points[i][1]})),'v');return `<tr><td>${m.period}</td>${series.map(s=>`<td class="n">${s.points[i][1]==null?'':MS.mode==='share'?ATPCT(t?s.points[i][1]/t:0):mfmt(s.points[i][1])}</td>`).join('')}<td class="n">${mfmt(t)}</td></tr>`}).join('');
 const first=marketTotals(MP.months[0].period),last=marketTotals(MP.months.at(-1).period);
 const per=active.map(c=>{let x=MP.months[0].by_category[c.id],y=MP.months.at(-1).by_category[c.id];if(MS.cohort==='constant'){x=x.constant_cohort;y=y.constant_cohort;}return {c,a:x,b:y,delta:(y?.eth_ref||0)-(x?.eth_ref||0)}}).sort((x,y)=>y.delta-x.delta);
 $('#m-category-changes tbody').innerHTML=per.map(({c,a:x,b:y})=>`<tr><td><i class="pdot" style="background:${c.color}"></i>${esc(c.label)}</td><td class="n">${num(x?.eth_ref,0)}</td><td class="n">${num(y?.eth_ref,0)}</td><td class="n">${pct(mchange(x?.eth_ref,y?.eth_ref),1)}</td><td class="n">${pct(mchange(x?.usd,y?.usd),1)}</td><td class="n">${x?.eth_ref!=null&&y?.eth_ref!=null&&first.eth_ref&&last.eth_ref?num(100*((y?.eth_ref||0)/last.eth_ref-(x?.eth_ref||0)/first.eth_ref),1)+' pp':''}</td></tr>`).join('');
 $('#m-coverage').innerHTML='';
 const chains=MP.chains.map(c=>({...c,eth_ref:msum(active.map(x=>c.by_category[x.id]),'eth_ref'),usd:msum(active.map(x=>c.by_category[x.id]),'usd')})).filter(c=>c.eth_ref>0).sort((x,y)=>y.eth_ref-x.eth_ref);
 $('#m-chain-bars').innerHTML=horizontalBars(chains.slice(0,10).map(c=>({name:c.chain,base:c.eth_ref,total:c.eth_ref,color:'var(--accent)'})),{format:v=>chartShort(v,n=>num(n,0)+' ETH'),label:'ETH earning a yield by chain'});
 $('#m-chain-table tbody').innerHTML=chains.map(c=>{const lead=active.slice().sort((x,y)=>(c.by_category[y.id]?.eth_ref||0)-(c.by_category[x.id]?.eth_ref||0))[0];return `<tr><td>${esc(c.chain)}</td><td class="n">${num(c.eth_ref,0)}</td><td class="n">${ATUSD(c.usd)}</td><td class="n">${c.protocol_count}</td><td>${esc(lead?.label)}</td></tr>`}).join('');
 $('#m-chain-note').textContent='Where the product’s balance sits by DefiLlama’s chain split, scaled to what the map counts. Staking tokens bridged to L2s are counted where their issuer holds the ETH.';
 $('#m-method-note').textContent='';
 marketCatalogue();marketFindings();marketPersist();if(document.body.dataset.edition==='reader')readerAnswer();
}

function atMapFindings(total){
 const st=atCatSize('staking'),rs=atCatSize('restaking'),cy=atCatSize('carry'),lido=MP.products.find(p=>p.id==='lido')?.current.eth_ref||0,bn=MP.products.find(p=>p.id==='binance-staked-eth')?.current.eth_ref||0;
 const mm=atCatSize('lending'),cdp=atCatSize('cdp'),rs0=MP.months[0].by_category.restaking.eth_ref;
 const items=[];
 if(MS.selected.has('staking')&&total.eth_ref)items.push(`<b>Staking is ${ATPCT(st/total.eth_ref,0)} of it.</b> Lido holds ${ATPCT(lido/st,0)} of the staking row and Binance’s wBETH ${ATPCT(bn/st,0)}; the other ${atRows('staking').length-2} issuers share the rest.`);
 if(MS.selected.has('restaking')&&total.eth_ref)items.push(`<b>Restaking is ${ATPCT(rs/total.eth_ref,0)}</b> (${ATK(rs)} ETH), down from ${ATK(rs0)} two years ago; ether.fi\u2019s weETH is ${ATPCT((MP.products.find(p=>p.id==='ether.fi-stake')?.current.eth_ref||0)/rs,0)} of it.`);
 if(MS.selected.has('carry')&&total.eth_ref)items.push(`<b>Carry is ${ATPCT(cy/total.eth_ref,1)}</b>: ${ATK(cy)} ETH in ${atRows('carry').length} products that borrow dollars against ETH. In BTC it is 9.9%.`);
 if(!MS.selected.has('lending'))items.push(`<b>Money markets hold another ${ATK(mm)} ETH</b> of idle WETH and CDPs ${ATK(cdp)} ETH of plain collateral; both are off by default (staking tokens posted as collateral are already counted at their issuer).`);
 return '<ol class="steps">'+items.map(t=>'<li>'+t+'</li>').join('')+'</ol>';
}

function atMovers(cat,from,dir=-1,n=3){
 const i0=MP.months.findIndex(m=>m.period===from);
 return MP.products.filter(p=>p.category===cat).map(p=>({p,d:(p.current.eth_ref||0)-(p.history[i0]?.eth_ref||0)})).filter(x=>dir<0?x.d<0:x.d>0).sort((x,y)=>dir<0?x.d-y.d:y.d-x.d).slice(0,n);
}
function marketFindings(){
 const months=MP.months,tot=months.map(m=>mactive().reduce((s,c)=>s+(m.by_category[c.id]?.eth_ref||0),0)),pk=tot.indexOf(Math.max(...tot)),last=marketTotals().eth_ref;
 const cat=id=>months.map(m=>m.by_category[id]?.eth_ref||0),now=id=>atCatSize(id);
 const fm=cat('farming'),fpk=fm.indexOf(Math.max(...fm)),rs=cat('restaking'),rpk=rs.indexOf(Math.max(...rs));
 const names=L=>L.map(x=>x.p.name.replace(/ \(.*\)$/,'')+' '+ATK(-x.d)).join(', ');
 const up=atMovers('staking',months[0].period,1,1)[0];
 const cards=[
  {big:ATPCT(mchange(tot[pk],last),0),lab:'from the peak',h:'Flat in ETH for two years',t:`${ATK(tot[pk])} ETH at the ${ATMON(months[pk].period)} peak, ${ATK(last)} now. Growth in one category was paid for by another.`},
  MS.selected.has('staking')&&up?{big:'+'+ATK(up.d),lab:up.p.name,h:'Binance became the second-largest staker',t:`wBETH grew from ${ATK(up.p.history[0].eth_ref)} to ${ATK(up.p.current.eth_ref)} ETH, the largest change on the map; Lido added ${ATK((MP.products.find(p=>p.id==='lido')?.current.eth_ref||0)-(MP.products.find(p=>p.id==='lido')?.history[0].eth_ref||0))}.`}:null,
  MS.selected.has('restaking')?{big:ATPCT(mchange(rs[rpk],now('restaking')),0),lab:'restaking',h:'Restaking tokens were redeemed',t:`${ATK(rs[rpk])} ETH in ${ATMON(months[rpk].period)}, ${ATK(now('restaking'))} now. Largest outflows: ${names(atMovers('restaking',months[rpk].period,-1,4))} ETH.`}:null,
  MS.selected.has('farming')?{big:ATPCT(mchange(fm[fpk],now('farming')),0),lab:'farming and pools',h:'Points money left',t:`${ATK(fm[fpk])} ETH in ${ATMON(months[fpk].period)}, ${ATK(now('farming'))} now: ${names(atMovers('farming',months[fpk].period,-1,4))} ETH.`}:null,
 ].filter(Boolean).slice(0,4);
 $('#m-history-findings').innerHTML=cards.map(c=>`<div class="f"><div class="big">${esc(c.big)}</div><span class="lab">${esc(c.lab)}</span><h3>${esc(c.h)}</h3><p>${esc(c.t)}</p></div>`).join('');
 $('#m-history-findings').className='findings f4 market-findings';
}

function atLabel(id,text){const t=$(id)?.closest('.tile')?.querySelector('.l');if(t)t.textContent=text;}
function atHero(){
 if(document.body.dataset.edition!=='reader')return;
 const total=marketTotals(),cy=MS.selected.has('carry')?atCatSize('carry'):null,cr=atRows('carry'),n=MP.products.filter(p=>MS.selected.has(p.category)&&(p.current.eth_ref||0)>=0.5).length;
 const st=MS.selected.has('staking')?atCatSize('staking'):0;
 $('#m-hero-total').textContent=num(total.eth_ref,0);
 $('#m-hero-detail').textContent='Across '+n+' products, each counted once'+(st&&total.eth_ref?'; '+ATPCT(st/total.eth_ref,0)+' is staking.':'.');
 $('#strict-carry-share').textContent=cy!=null&&total.eth_ref?ATPCT(cy/total.eth_ref,1):'off';
 $('#strict-carry-size').textContent=cy!=null?ATK(cy)+' ETH in '+cr.length+' products post ETH against dollar loans ($'+num(EQ.attributedDollarDebtUSD/1e6,0)+'M of debt). Two years ago: '+ATK(MP.months[0].by_category.carry.eth_ref)+' ETH.':'Carry is switched off.';
 const top2=cr.slice(0,2),t2=msum(top2.map(p=>p.current),'eth_ref');
 $('#strict-carry-concentration').textContent=cy?ATPCT(t2/cy,0):'n/a';
 $('#strict-carry-concentration-note').textContent=top2.map(p=>p.name+' '+ATK(p.current.eth_ref)).join(' and ')+' ETH.';
 $('#strict-organic-return').textContent='+0.7 pp';
 $('#strict-organic-return-note').textContent='Liquid ETH 3.37% a year vs stETH 2.71% over two years, rewards included. Without rewards its RLUSD leg loses 0.84 pp.';
}

readerAnswer=function(){atHero();atMeaning();const T=marketTotals();atLabel('#m-hero-total','ETH earns a yield ('+ATUSD(T.usd)+')');atLabel('#strict-carry-share','is carry');atLabel('#strict-carry-concentration','of carry is in two products');atLabel('#strict-organic-return','what carry adds over staking, a year');};
function atMeaning(){
 const ol=$('.market-conclusions ol');if(!ol)return;
 ol.innerHTML=[
  '<b>ETH carry has to beat staking; BTC carry only has to beat zero.</b> ETH collateral already earns about 2.7% staked, so the dollar leg must add on top. Liquid ETH beat stETH by 0.66 pp a year over two years; YieldBasis and Vesper trailed it in September.',
  '<b>The same dollar vaults fund BTC and ETH carry.</b> Liquid ETH parks $55M in Sentora’s RLUSD vault, where 53% of the money is lent to Kraken’s kBTC loop, and $50M in the PYUSD vault that is 95% PRIME home-equity credit. A loss there hits both markets at once.',
  '<b>The loan currency decides the spread.</b> On 2 October Aave charged 13.93% for USDC and 4.38% for USDT; Morpho USDT cost 3.2%. Liquid’s 7.79% average comes from its $65M Aave USDC leg. Pick the cheapest hub currency, not the venue.'
 ].map(t=>'<li>'+t+'</li>').join('');
}

// Data: products that pay a yield on ETH but are not counted, and DefiLlama rows the map leaves out.
function atOutside(){
 const el=$('#strict-exclusions');if(!el)return;
 const out=(MP.outside_totals||[]).filter(r=>r.product);
 const rows=out.map(r=>`<tr><td>${esc(r.kind)}</td><td><b>${r.url?a(r.url,r.product):esc(r.product)}</b></td><td class="n">${r.size_eth?num(+r.size_eth,0):'not disclosed'}<div class="sub">${esc(r.size_date||'')}</div></td><td>${esc(r.yield_eth||'')}</td><td>${esc(r.why_not_counted||'')}${r.overlap_note?`<div class="sub">${esc(r.overlap_note)}</div>`:''}</td></tr>`).join('');
 const ex=(MP.excluded_protocols||[]).filter(r=>(r.eth||0)>=100).map(r=>`<tr><td><b>${esc(r.name)}</b></td><td class="n">${num(r.eth,0)}</td><td>${esc(r.reason)}</td></tr>`).join('');
 const sum=out.reduce((s,r)=>s+(+r.size_eth||0),0);
 el.innerHTML=`<p><b>About 14.4M ETH more is staked off-chain</b>, a third of all stake: exchanges 4.6M (Kraken 1.7M, Coinbase 1.1M beyond cbETH, Upbit, OKX), institutional providers 4.7M (Figment, Blockdaemon, Kiln, Everstake) and BitMine’s treasury 5.1M. Staking ETFs (1.7M) and other treasuries stake through those providers, so they are listed but not added again. Sizes are beacon-chain entity tags and filings, dated in the table.</p><div class="tblwrap"><table><thead><tr><th>Kind</th><th>Product</th><th class="n">ETH</th><th>Pays, %</th><th>Why not counted</th></tr></thead><tbody>${rows}</tbody></table></div><h4>DefiLlama rows the map leaves out</h4><div class="tblwrap"><table><thead><tr><th>Row</th><th class="n">ETH (DefiLlama)</th><th>Why</th></tr></thead><tbody>${ex}</tbody></table></div>`;
}
const _atPrevAnswer=readerAnswer;readerAnswer=function(){_atPrevAnswer();atOutside();};

// runs after every earlier layer has initialised
function atlasFinal(){readerAnswer();atTop5Text();readerLandscape();const h=$('#market .shead');if(h)h.innerHTML='<div class="k">03 \u00b7 Other carry</div><h2>Every other product that borrows against ETH</h2><p class="lede">Live, small, closing and one that is not a product at all, with what each paid.</p>';}
function atTop5Text(){
 const set=(sel,html)=>{const e=$(sel);if(e)e.innerHTML=html;};
 set('#top5 .shead h2','The five largest carry products');
 set('#top5 .shead .lede','Ranked by dollars borrowed against ETH on 2 October. Each product from deposit to exit: where the borrowed dollars go, who holds the keys, who pays the yield, how fast the debt can be repaid.');
 set('#carry-history > h3','Two years of carry, by product');
 set('#carry-history > .sub','Month-end book of the twelve products that borrow dollars against ETH, in ETH. Mixed vaults are shown whole: Liquid and Lido Earn also run ETH loops.');
 set('#c-history-options','Concrete Delta (307k ETH) is left out: it is one wallet\u2019s own position, not a pooled product. See Other carry.');
}

// Top 5: risk and exit panel per product (health factor history, borrow rate vs what the dollars earn, repayment ladder,
// who pays the rewards). Data: R.atlasTop5Risk (tools/eth/atlas_build.py).
const ATR=R.atlasTop5Risk?.products||{};
const ATRISK_TEXT={
 liquid:'<b>The dollar side loses about $6.8M a year at 2 October rates.</b> Interest is about $14.1M a year, $9.0M of it on the $64.5M Aave USDC loan at 13.93% (Aave USDC has cost 12.6 to 14.1% at every month-end since June). The parked dollars earn about $7.3M: $4.7M of base yield and $2.6M of Merkl rewards. A quarter of the debt ($46M) has no dollar asset behind it that we could find.',
 yieldbasis:'<b>Fees cover the loan.</b> The pool pays a fixed 10% on its crvUSD, and Curve fee growth was 9.19% a year on twice the debt. There is no liquidation: debt stays at 49.8 to 50.2% of collateral against a 56.25% critical level.',
 'lido-earn':'<b>Small positive spread.</b> The USDT loans cost 4.33% and earnUSD paid 4.80% over 30 days. Lido Earn owns 48.5% of earnUSD, so its exit is the queue of a vault it mostly is. Earlier USDC debt (Nov 2025 to Mar 2026) on another account was a USDe loop, not ETH-backed carry.',
 avant:'<b>Positive spread, own credit.</b> Loans cost 6.30%; savUSD, Avant’s own dollar product, paid 7.54%. 98% of the parked dollars sit in savUSD on Avalanche: a 24-hour cooldown, a bridge and up to 7 days of redemption before the debt can be repaid.',
 liquity:'<b>The dollar side does not pay for itself.</b> The trove borrows ebUSD at a 2.55% rate the product sets itself, and the Curve ebUSD/USDC position earned 0.45% in fees. Repayment is easy: 97.5% of the debt can be bought back on Curve in one block.'
};
function atRiskPanel(id){
 const p=ATR[id],host=$('#strict-product-content');if(!p||!host||$('#atlas-risk-'+id))return;
 const pts=s=>(s||[]).map(([t,v])=>[t,v]);
 const isYB=id==='yieldbasis';
 const hf=isYB?lineChart([{name:'Debt / collateral',color:'var(--pc)',points:pts(p.ltv).map(([t,v])=>[t,v*100])},{name:'Critical level',color:'var(--danger, #d9534f)',points:pts(p.ltv).map(([t])=>[t,56.25])}],{yLabel:'Debt as % of collateral',format:v=>num(v,1)+'%'})
  :lineChart([{name:'Health factor (worst account)',color:'var(--pc)',points:pts(p.health_factor)},{name:'Liquidation',color:'var(--danger, #d9534f)',points:pts(p.health_factor).map(([t])=>[t,1])}],{yLabel:'Health factor',format:v=>num(v,2)});
 const park=Object.entries(p.parking||{}).map(([d,s],i)=>({name:d+' yield',color:['#3fae9a','#d4a23c','#8a6fe0'][i%3],points:pts(s).map(([t,v])=>[t,v*100])}));
 const rate=lineChart([{name:'Borrow rate (debt-weighted)',color:'var(--danger, #d9534f)',points:pts(p.borrow_rate_debt_weighted).map(([t,v])=>[t,v*100])},...park],{yLabel:'Annual rate, %',format:v=>num(v,1)+'%'});
 const lad=(p.ladder||[]).length?horizontalBars(p.ladder.map(t=>({name:t.tier.replace(/^T\d[a-z]?\s*/,''),base:t.pct,total:t.pct,color:'var(--pc)'})),{format:v=>pct(v,0),label:'Share of the dollar debt that can be repaid'}):'';
 const ladRows=(p.ladder||[]).map(t=>`<tr><td>${esc(t.tier.replace(/^T\d[a-z]?\s*/,''))}</td><td class="n">${ATUSD(t.usd)}</td><td class="n">${pct(t.pct,0)}</td><td class="n">${t.ethReleased!=null?num(t.ethReleased,0):''}</td><td>${esc(t.detail)}</td></tr>`).join('');
 const rw=(p.rewards||[]).map(c=>`<tr><td>${esc(c.opportunity)}</td><td>${esc(c.token)}</td><td class="n">${num(c.amount,0)} a week</td><td class="n">${c.rewardAPRatT!=null?pct(c.rewardAPRatT,2):''}</td><td class="n">${c.liquidRewardUSDperYearAtT!=null?ATUSD(c.liquidRewardUSDperYearAtT):''}</td><td><code>${esc(short(c.creator||''))}</code> ${esc((c.creatorMerklTags||[]).join(', '))}</td></tr>`).join('');
 const html=`<section class="panel atlas-risk" id="atlas-risk-${id}"><h3>Risk and exit</h3><p>${ATRISK_TEXT[id]||''}</p>
 <div class="reader-example-pair"><div><h4>${isYB?'Debt against collateral, month-end':'Health factor, month-end'}</h4><div class="chart-scroll">${hf}</div></div><div><h4>Loan rate against what the dollars earn</h4><div class="chart-scroll">${rate}</div></div></div>
 ${lad?`<h4>How much of the dollar debt can be repaid, and how fast (2 October)</h4><div class="chart-scroll">${lad}</div><details class="more"><summary>Repayment ladder: sources and ETH released</summary><div class="body tblwrap"><table><thead><tr><th>When</th><th class="n">USD</th><th class="n">Share</th><th class="n">ETH released</th><th>From where</th></tr></thead><tbody>${ladRows}</tbody></table><p class="note">What the manager can repay from the destinations, assuming no other depositor withdraws in the same block and stablecoins at $1.</p></div></details>`:''}
 ${rw?`<h4>Who pays the rewards</h4><div class="tblwrap"><table><thead><tr><th>Vault</th><th>Token</th><th class="n">Budget</th><th class="n">APR at T</th><th class="n">Liquid, $ a year</th><th>Campaign creator</th></tr></thead><tbody>${rw}</tbody></table></div><p class="note">Sentora creates the Merkl campaigns but does not fund them: the RLUSD and PYUSD trace back through unlabelled wallets to addresses that receive the tokens straight from mint, on the issuers’ side. No rewards on stcUSD, earnUSD, savUSD or the YieldBasis pool.</p>`:''}
 </section>`;
 const anchor=[...host.querySelectorAll('h3,h4')].find(h=>/Capital and investor outcomes/i.test(h.textContent));
 if(anchor)(anchor.closest('section,.panel,div')||anchor).insertAdjacentHTML('beforebegin',html);else host.insertAdjacentHTML('beforeend',html);
}
const _atRenderProduct=stRenderProduct;stRenderProduct=function(id,u){_atRenderProduct(id,u);atRiskPanel(id);};

// Carry waves (replaces reader.js): three phases, numbers from the books and the corrected debt history.
function readerCarryWaves(){
 const books=R.readerAnalysis.books,book=n=>books.find(p=>p.name===n),liq=book('ether.fi Liquid ETH'),res=book('Reservoir ETH Yield');
 const debt=m=>(EQ.history.find(h=>h.month===m)||{}).debtUSD||0,dT=EQ.attributedDollarDebtUSD,pdebt=(id,m)=>((EQ.products.find(p=>p.id===id)||{history:[]}).history.find(h=>h.month===m)||{}).debtUSD||0;
 const waves=[
  ['Oct 2024 to Aug 2025','One product',`Liquid ETH was the only sizable book (${ATK(liq.history[0].eth)} ETH, peak ${ATK(liq.peak.eth)} in ${ATMON(liq.peak.month)}), and it looped ETH rather than borrowing dollars until its first Aave USDC loan in August 2025 (${ATUSD(pdebt('liquid','2025-08'))} at month-end).`,'?carryProduct=liquid#strict-product-tabs'],
  ['Sep 2025 to Feb 2026','Small wrappers come and go',`Avant, Rocksolid, Reservoir and Makina launched; Reservoir peaked at ${ATK(res.peak.eth)} ETH in ${ATMON(res.peak.month)} and emptied. Liquid repaid its dollar loans in October. Lido Earn borrowed ${ATUSD(pdebt('lido-earn','2025-12'))} of USDT and USDC against wstETH by December.`,'library/CARRY-VARIANTS-EXPANSION.html'],
  ['Mar to Sep 2026','Dollar debt \u00d7'+num(dT/debt('2026-05'),0)+' in five months',`From ${ATUSD(debt('2026-05'))} in May to ${ATUSD(dT)} on 2 October: Liquid’s Morpho RLUSD, USDC and PYUSD loans from June, YieldBasis WETH from May, Liquity from March. Rocksolid entered Closing on 29 September.`,'library/CARRY-PRODUCTS.html']
 ];
 return waves.map(w=>'<div><div class="k">'+esc(w[0])+'</div><h4>'+esc(w[1])+'</h4><p>'+esc(w[2])+'</p><a href="'+w[3]+'">Evidence →</a></div>').join('');
}

// Other carry: every product that borrows dollars against ETH, outside the top five (replaces economic.js/reader.js).
const ATLAND=[
 ['Concrete Delta weETH','One wallet’s own position','307,363 ETH in weETH/wstETH on Aave and Morpho; $176M of USDT/USDC borrowed (21% LTV) into Theo thBILL, ctDefiUSDT and s0xUSD','A Bitfinex-linked wallet moved its own Aave position into the vault’s Safe on 10 Dec 2025 and holds 100% of the shares; the 5-signer Safe still includes it. No outside depositors, no deposits or withdrawals since. Not counted in the map.','concrete'],
 ['Rocksolid rETH','Closing since 29 Sep','rETH vault on Lagoon; 728 ETH of it in Liquity ETH Carry, $6.3M debt on Spark','76% of the book was not traced to a position; new withdrawal requests revert since Closing.','rocksolid'],
 ['Makina DETH','Active','weETH loop on Aave (15,065 WETH debt) plus a Morpho wstETH/USDT route ($385k) into Sentora PYUSD','Book mark was 14.5 hours stale at the snapshot.','makina-deth'],
 ['Vesper vaETH','Active','One of 8 strategies posts 57 WETH, borrows 69k DAI into vDAI','Over 30 days vDAI earned 13.50 DAI against 452.50 DAI of interest.','vesper'],
 ['Royco ETH','Active, exit closed','Morpho wstETH/PYUSD (91k PYUSD at 30%) into a senior Royco credit receipt','Accounting call reverts and maxWithdraw is 0; 30-day epochs, KYC.','royco'],
 ['Reservoir ETH Yield','Small','Aave WETH/USDC (13.93%) into srUSD, which borrows again on Morpho','Outer loan costs 8.95 pp more than srUSD pays; peaked at 4,137 ETH in Oct 2025.','reservoir-eth'],
 ['TAU InfiniFi ETH Carry','Wound down','cbETH collateral, USDC into InfiniFi siUSD (inner loop of 2.53M USDC in Jan 2026)','Debt is 0.02 USDC at the snapshot; the book is a remnant.','tau-infinifi'],
 ['ZenSats wstETH','Micro','LlamaLend wstETH/crvUSD into Curve crvUSD/USDT via StakeDAO','Under 1 ETH; the earlier Aave/RAAC vault is empty.','zensats'],
];
readerLandscape=function(){
 const R30=Object.fromEntries((R.reportContract.matched30dReturns||[]).map(r=>[r.name,r]));
 const rows=ATLAND.map(([name,status,how,risk,id])=>{const c=(R.reportContract.census||[]).find(p=>p.name===name)||{},f=EQ.products.find(p=>p.id===id),r=R30[name];
  return `<tr><td><b>${esc(name)}</b></td><td>${esc(status)}</td><td>${esc(how)}</td><td class="n">${r?(r.bookReturnPct*365/30).toFixed(2)+'%<div class="sub">'+(r.excessPercentagePoints>=0?'+':'')+(r.excessPercentagePoints*365/30).toFixed(2)+' pp vs stETH</div>':''}</td><td class="n">${c.bookETH!=null?ATK(c.bookETH)+' ETH':''}<div class="sub">${f&&f.current.debtUSD?ATUSD(f.current.debtUSD)+' debt':''}</div></td><td>${esc(risk)}</td></tr>`;}).join('');
 $('#strict-landscape').innerHTML=`<table id="reader-landscape-table"><thead><tr><th>Product</th><th>Status</th><th>What it does</th><th class="n">Paid, a year (30 days)</th><th class="n">Size</th><th>What to take from it</th></tr></thead><tbody>${rows}</tbody></table>`;
 $('#strict-census-note').innerHTML='Returns are the book share value over 2 September to 2 October, annualised, against stETH over the same dates. Rocksolid’s Liquity shares are counted once, in Liquity. <a href="data/carry-status-and-capital.csv" download>Status and size CSV</a>';
};

// History CSV for the current switches, built in the browser (one file per mix of 11 switches would be 4,096 files).
function marketPersist(){
 try{localStorage.setItem('eth-research-eight-categories',JSON.stringify([...MS.selected]))}catch{}
 const u=new URL(location.href);if(MP.categories.every(c=>MS.selected.has(c.id)===c.default))u.searchParams.delete('categories');else u.searchParams.set('categories',[...MS.selected].join(','));
 if(MS.cohort==='constant')u.searchParams.set('historyCohort','constant');else u.searchParams.delete('historyCohort');history.replaceState(null,'',u);
 const link=$('#m-history-export');if(!link)return;const act=mactive();
 const rows=[['month',...act.flatMap(c=>[c.id+'_ETH',c.id+'_USD']),'total_ETH','total_USD'],...MP.months.map(m=>{const v=act.map(c=>{const b=m.by_category[c.id];const r=MS.cohort==='constant'?b.constant_cohort:b;return [r?.eth_ref??'',r?.usd??''];});return [m.period,...v.flat(),v.reduce((s,x)=>s+(+x[0]||0),0),v.reduce((s,x)=>s+(+x[1]||0),0)];})];
 link.href=URL.createObjectURL(new Blob([rows.map(r=>r.join(',')).join('\n')],{type:'text/csv'}));link.download='eth-market-history-'+MS.cohort+'.csv';
}
