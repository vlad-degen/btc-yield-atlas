// Counted-once ETH market and the answer, in the BTC atlas's style. Loaded last in the reader:
// the function declarations below replace market.js's text-producing functions (hoisting), and the
// assignments at the bottom replace the hero writers of the earlier layers.
try{if(localStorage.getItem('eth-atlas-v2')!=='1'){localStorage.removeItem('eth-research-eight-categories');localStorage.setItem('eth-atlas-v2','1');}}catch{}

// Concrete Delta is one principal's own position, not a pooled product (research/eth/en/gaps/CONCRETE-DELTA.md):
// out of the carry history chart, shown under Other carry.
if(R.readerAnalysis?.books)R.readerAnalysis.books=R.readerAnalysis.books.filter(b=>b.name!=='Concrete Delta weETH');
const ATK=v=>v==null?'n/a':Math.abs(v)>=1e6?num(v/1e6,2)+'M':Math.abs(v)>=1e4?num(v/1e3,0)+'k':num(v,0);
const ATUSD=v=>v==null?'n/a':'$'+(Math.abs(v)>=1e9?num(v/1e9,1)+'B':Math.abs(v)>=1e7?num(v/1e6,0)+'M':Math.abs(v)>=1e6?num(v/1e6,1)+'M':Math.abs(v)>=1e4?num(v/1e3,0)+'k':num(v,0));
const ATPCT=(v,d=1)=>v==null?'n/a':num(v*100,d)+'%';
const ATMON=p=>{const [y,m]=String(p).split('-');return ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][+m-1]+' '+y;};
const ATKINDS={farming:[['pools','Liquidity pools','DEX, perp and bridge pools. Only the plain ETH side is counted; the staking-token side of an ETH/LST pool stays with its issuer.'],['vaults','Strategy vaults','Managed vaults that lend, loop or provide liquidity on the depositor’s behalf.'],['points','Points farming','ETH parked for points or a future token: pre-deposits for new chains and lock-ups.']]};
const atRows=cat=>MP.products.filter(p=>p.category===cat&&p.current?.status==='observed'&&(p.current.eth_ref||0)>=0.5).sort((a,b)=>b.current.eth_ref-a.current.eth_ref);
const atCatSize=cat=>msum(atRows(cat).map(p=>p.current),'eth_ref');
const atHist=cat=>MP.months.map(m=>m.by_category[cat]?.eth_ref||0);

function stMarketMechanism(p){return p.how_earns||'';}
function stMarketOperator(p){return p.operator||'';}

function atTable(rows,base,{limit=8,id='',showCat=false}={}){
 const body=rows.map((p,i)=>{const r=p.current;return `<tr${i>=limit?' class="more-row" hidden':''}><td><b>${p.official_url?a(p.official_url,p.name):esc(p.name)}</b></td>${showCat?`<td>${esc(mcat(p.category).label)}</td>`:''}<td class="n">${num(r.eth_ref,0)}<div class="sub">${ATUSD(r.usd)}</div></td><td class="n">${base?ATPCT(r.eth_ref/base):''}</td><td>${esc(p.how_earns||'')}</td><td>${esc(p.yield||'')}</td><td>${esc(p.operator||'')}</td></tr>`;}).join('');
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
 $('#m-donut').innerHTML=marketDonut(MP.products.filter(p=>(p.current.eth_ref||0)>=0.5),total).replace('layered exposure','counted once').replace(money(total.usd),ATUSD(total.usd));
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
 marketCatalogue();marketFindings();marketPersist();if(document.body.dataset.edition==='reader')readerAnswer();else if(typeof renderStrictHeadline==='function')renderStrictHeadline();if(document.body.dataset.edition!=='reader'){$('#m-hero-total').textContent=ATK(total.eth_ref);atLabel('#m-hero-total','ETH earns a yield, each product counted once');const st=atCatSize('staking')+atCatSize('restaking');if($('#m-hero-staking'))$('#m-hero-staking').textContent=total.eth_ref?ATPCT(st/total.eth_ref,0):'';const n=$('#m-hero-total').closest('section')?.querySelector('.hero-note,.tiles+p');if(n)n.textContent='The market counts each product once, as in the BTC study: staking tokens held by other products leave their issuer\u2019s row. Method in Data.';}
}

function atMapFindings(total){
 const st=atCatSize('staking'),rs=atCatSize('restaking'),cy=atCatSize('carry'),lido=MP.products.find(p=>p.id==='lido')?.current.eth_ref||0,bn=MP.products.find(p=>p.id==='binance-staked-eth')?.current.eth_ref||0;
 const mm=atCatSize('lending'),cdp=atCatSize('cdp'),rs0=MP.months[0].by_category.restaking.eth_ref;
 const items=[];
 if(MS.selected.has('staking')&&total.eth_ref)items.push(`<b>Staking is ${ATPCT(st/total.eth_ref,0)} of it.</b> Lido holds ${ATPCT(lido/st,0)} of the staking row and Binance’s wBETH ${ATPCT(bn/st,0)}; the other ${atRows('staking').length-2} issuers share the rest.`);
 if(MS.selected.has('restaking')&&total.eth_ref)items.push(`<b>Restaking is ${ATPCT(rs/total.eth_ref,0)}</b> (${ATK(rs)} ETH), down from ${ATK(rs0)} two years ago; ether.fi\u2019s weETH is ${ATPCT((MP.products.find(p=>p.id==='ether.fi-stake')?.current.eth_ref||0)/rs,0)} of it.`);
 if(MS.selected.has('carry')&&total.eth_ref)items.push(`<b>Carry is ${ATPCT(cy/total.eth_ref,1)}</b>: ${ATK(cy)} ETH in ${atRows('carry').length} products that owe dollars against ETH, none two years ago. In BTC it is 9.8%.`);
 if(!MS.selected.has('lending'))items.push(`<b>Money markets hold another ${ATK(mm)} ETH</b> of idle WETH and CDPs ${ATK(cdp)} ETH of plain collateral; both are off by default (staking tokens posted as collateral are already counted at their issuer).`);
 return '<ol class="steps">'+items.map(t=>'<li>'+t+'</li>').join('')+'</ol>';
}

function atMovers(cat,from,dir=-1,n=3){
 const i0=MP.months.findIndex(m=>m.period===from);
 return MP.products.filter(p=>p.category===cat&&!['eigencloud','symbiotic'].includes(p.id)).map(p=>({p,d:(p.current.eth_ref||0)-(p.history[i0]?.eth_ref||0)})).filter(x=>dir<0?x.d<0:x.d>0).sort((x,y)=>dir<0?x.d-y.d:y.d-x.d).slice(0,n);
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
 $('#strict-carry-size').textContent=cy!=null?ATK(cy)+' ETH in '+cr.length+' products that owe dollars against ETH ($'+num(EQ.attributedDollarDebtUSD/1e6,0)+'M; most of their books are ETH loops). Two years ago: '+ATK(MP.months[0].by_category.carry.eth_ref)+' ETH.':'Carry is switched off.';
 const top2=cr.slice(0,2),t2=msum(top2.map(p=>p.current),'eth_ref');
 $('#strict-carry-concentration').textContent=cy?ATPCT(t2/cy,0):'n/a';
 $('#strict-carry-concentration-note').textContent=top2.map(p=>p.name+' '+ATK(p.current.eth_ref)).join(' and ')+' ETH.';
 $('#strict-organic-return').textContent='+0.66 pp';
 $('#strict-organic-return-note').textContent='Liquid ETH 3.37% a year vs stETH 2.71% over two years. The ETH loop added +0.02 pp and the dollar leg \u22120.13 pp; the rest our model cannot assign.';
}

readerAnswer=function(){atHero();atMeaning();const T=marketTotals();atLabel('#m-hero-total','ETH earns a yield ('+ATUSD(T.usd)+')');atLabel('#strict-carry-share','is carry');atLabel('#strict-carry-concentration','of carry is in two products');atLabel('#strict-organic-return','largest carry product over stETH, a year');};
function atMeaning(){
 const ol=$('.market-conclusions ol');if(!ol)return;
 ol.innerHTML=[
  '<b>ETH carry has to beat staking; BTC carry only has to beat zero.</b> Staked ETH earns 2.2 to 2.7%, so the dollar leg must add on top. Liquid ETH beat stETH by 0.66 pp a year over two years, but neither its ETH loop (+0.02 pp) nor its dollar leg (\u22120.13 pp) explains it. All of the lead came in year two (2.86% vs 2.93% for stETH to October 2025, then 3.86% vs 2.47%), and the fee cut from 1.10 to 0.26 pp of NAV a year is most of that turn. YieldBasis and Vesper trailed stETH in September.',
  '<b>Rewards are a small part of ETH carry, except at YieldBasis and Liquity.</b> Without rewards Liquid ETH still earns 3.39% a year against 3.87% (rewards are 34% of its lead over stETH); Lido Earn has none in its price and Avant 7%. Liquity\u2019s lead over stETH is 99% rewards, and a YieldBasis gauge staker earns +1.69% only because of YB emissions (\u22122.96% unstaked). Live programmes at the snapshot: $2.7M a year to Liquid from the RLUSD and PYUSD side, $0.5M of YB.',
  '<b>The same dollar vaults fund BTC and ETH carry.</b> Liquid ETH parks $55M in Sentora’s RLUSD vault, where 53% of the money is lent to Kraken’s kBTC loop, and $50M in the PYUSD vault that is 95% PRIME home-equity credit. A loss there hits both markets at once.',
  '<b>Private mandates borrow as much as all ETH carry products together.</b> Concrete Delta (one Bitfinex-linked wallet, $176M of stablecoin debt) and three whitelist-only rSHARE vaults run by one operator ($76M against ETH) owe $252M; the 12 carry products owe $261M. The demand for large ETH-backed dollar loans comes from single principals, not from depositors.',
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
function atlasFinal(){readerAnswer();atTop5Text();readerLandscape();const h=$('#market .shead');if(h)h.innerHTML='<div class="k">03 \u00b7 Other carry</div><h2>Every other product that borrows against ETH</h2><p class="lede">Live, small, reopened, and two private mandates that borrow as much as all the products together.</p>';}
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
 liquid:'<b>The dollar side loses about $6.8M a year at 2 October rates.</b> Interest is about $14.1M a year, $9.0M of it on the $64.6M Aave USDC loan at 13.93% (Aave USDC has cost 12.6 to 14.1% at every month-end since June). The parked dollars earn about $7.3M: $4.7M of base yield and $2.6M of Merkl rewards. A quarter of the debt ($46M) has no dollar asset behind it that we could find.',
 yieldbasis:'<b>Fees cover the loan.</b> The pool pays a fixed 10% on its crvUSD, and Curve fee growth was 9.19% a year on twice the debt. There is no liquidation: debt stays at 49.8 to 50.2% of collateral against a 56.25% critical level.',
 'lido-earn':'<b>The rsETH loop that froze the vault is still open.</b> 113,216 rsETH against 112,310 WETH on Aave at health factor 1.035, about 12% of the book. rsETH is frozen on Aave; the position stands only through rsETH e-mode, so a 3.4% fall in rsETH, or losing that e-mode, liquidates it. <b>Small positive spread.</b> The USDT loans cost 4.33% and earnUSD paid 4.80% over 30 days. Lido Earn owns 48.5% of earnUSD, so its exit is the queue of a vault it mostly is. Earlier USDC debt (Nov 2025 to Mar 2026) on another account was a USDe loop, not ETH-backed carry.',
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
 ${rw?`<h4>Who pays the rewards</h4><div class="tblwrap"><table><thead><tr><th>Vault</th><th>Token</th><th class="n">Budget</th><th class="n">APR, 2 Oct</th><th class="n">Liquid, $ a year</th><th>Campaign creator</th></tr></thead><tbody>${rw}</tbody></table></div><p class="note">Sentora creates the Merkl campaigns but does not fund them: the RLUSD and PYUSD trace back through unlabelled wallets to addresses that receive the tokens straight from mint, on the issuers’ side. No rewards on stcUSD, earnUSD, savUSD or the YieldBasis pool.</p>`:''}
 </section>`;
 const anchor=[...host.querySelectorAll('h3,h4')].find(h=>/Capital and investor outcomes/i.test(h.textContent));
 if(anchor)(anchor.closest('section,.panel,div')||anchor).insertAdjacentHTML('beforebegin',html);else host.insertAdjacentHTML('beforeend',html);
}
const _atRenderProduct=stRenderProduct;stRenderProduct=function(id,u){_atRenderProduct(id,u);atRiskPanel(id);$$('#strict-product-content details.more>summary').forEach(x=>{if(/Repaid Morpho positions and residual debt/.test(x.textContent))x.parentElement.remove();});const k=$('#strict-product-content .k, #strict-product-content .kicker');if(k&&/attributed/.test(k.textContent))k.textContent=k.textContent.replace(/#(\d) by attributed dollar financing.*/,'#$1 by dollars borrowed against ETH');};

// Carry waves (replaces reader.js): three phases, numbers from the books and the corrected debt history.
function readerCarryWaves(){
 const books=R.readerAnalysis.books,book=n=>books.find(p=>p.name===n),liq=book('ether.fi Liquid ETH'),res=book('Reservoir ETH Yield');
 const debt=m=>(EQ.history.find(h=>h.month===m)||{}).debtUSD||0,dT=EQ.attributedDollarDebtUSD,pdebt=(id,m)=>((EQ.products.find(p=>p.id===id)||{history:[]}).history.find(h=>h.month===m)||{}).debtUSD||0;
 const waves=[
  ['Oct 2024 to Aug 2025','One product',`Liquid ETH was the only sizable book (${ATK(liq.history[0].eth)} ETH, peak ${ATK(liq.peak.eth)} in ${ATMON(liq.peak.month)}), and it looped ETH rather than borrowing dollars until its first Aave USDC loan in August 2025 (${ATUSD(pdebt('liquid','2025-08'))} at month-end).`,'?carryProduct=liquid#strict-product-tabs'],
  ['Sep 2025 to Feb 2026','Small wrappers come and go',`Avant, Rocksolid, Reservoir and Makina launched; Reservoir peaked at ${ATK(res.peak.eth)} ETH in ${ATMON(res.peak.month)} and emptied. Liquid repaid its dollar loans in October. Lido Earn borrowed ${ATUSD(pdebt('lido-earn','2025-12'))} of USDT and USDC against wstETH by December.`,'library/CARRY-VARIANTS-EXPANSION.html'],
  ['Mar to Sep 2026','Dollar debt \u00d7'+num(dT/debt('2026-05'),0)+' in five months',`From ${ATUSD(debt('2026-05'))} in May to ${ATUSD(dT)} on 2 October: Liquid’s Morpho RLUSD, USDC and PYUSD loans from June, YieldBasis WETH from May, Liquity from March. Rocksolid closed on 29 September and reopened on 7 October.`,'library/CARRY-PRODUCTS.html']
 ];
 return waves.map(w=>'<div><div class="k">'+esc(w[0])+'</div><h4>'+esc(w[1])+'</h4><p>'+esc(w[2])+'</p><a href="'+w[3]+'">Evidence →</a></div>').join('');
}

// Other carry: every product that borrows dollars against ETH, outside the top five (replaces economic.js/reader.js).
const ATLAND=[
 ['Concrete Delta weETH','One wallet’s own position','307,363 ETH in weETH/wstETH on Aave and Morpho; $176M of USDT/USDC borrowed (21% LTV) into Theo thBILL, ctDefiUSDT and s0xUSD','A Bitfinex-linked wallet moved its own Aave position into the vault’s Safe on 10 Dec 2025 and holds 100% of the shares; the 5-signer Safe still includes it. No outside depositors, no deposits or withdrawals since. Not counted in the map.','concrete'],
 ['Rocksolid rETH','Closed 29 Sep, reopened 7 Oct','rETH vault run from a Fordefi MPC wallet: ETH loops on Monad and Ethereum, Steakhouse Prime ETH, 728 ETH of Liquity carry shares, and a second wallet borrowing $2.7M USDC against rETH into Gami and Hyperithm vaults','Book reconciles to within 0.04%, but across three chains and two wallets; the closing on 29 Sep was reversed by a contract upgrade on 7 Oct.','rocksolid'],
 ['NEMO ETH Prime','Active','Upshift WETH vault; $5.6M USDC borrowed against wstETH, all of it in NEMO\u2019s own USDC vault, which trades on Derive','30-day redemption; upgrades and fund moves have no delay.','upshift-nemo-eth-prime'],
 ['Sentora ETH','Active','Upshift WETH vault; $256k RLUSD on Morpho into Sentora RLUSD and $907k Aave USDC at 13.93% into Huma PayFi tokens with no on-chain price','Book last updated 22 Sep; one of its two loans costs 13.93%.','upshift-sentora-eth'],
 ['Makina DETH','Active','weETH loop on Aave (15,065 WETH debt) plus a Morpho wstETH/USDT route ($385k) into Sentora PYUSD','Book mark was 14.5 hours stale at the snapshot.','makina-deth'],
 ['Vesper vaETH','Active','One of 8 strategies posts 57 WETH, borrows 69k DAI into vDAI','Over 30 days vDAI earned 13.50 DAI against 452.50 DAI of interest.','vesper'],
 ['Royco ETH','Active, exit closed','Morpho wstETH/PYUSD (91k PYUSD at 30%) into a senior Royco credit receipt','Accounting call reverts and maxWithdraw is 0; 30-day epochs, KYC.','royco'],
 ['Reservoir ETH Yield','Small','Aave WETH/USDC (13.93%) into srUSD, which borrows again on Morpho','Outer loan costs 8.95 pp more than srUSD pays; peaked at 4,137 ETH in Oct 2025.','reservoir-eth'],
 ['TAU InfiniFi ETH Carry','Wound down','wstETH collateral, USDC into InfiniFi siUSD (inner loop of 2.53M USDC in Jan 2026)','Debt is 0.02 USDC at the snapshot; the book is a remnant.','tau-infinifi'],
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

// Product stories, one finding each (replaces strict.js and reader_product_chapters wording).
Object.assign(ST_STORIES,{
 liquid:{title:'Beats stETH by 0.66 pp a year, and neither the loop nor the carry explains why',text:'Liquid ETH loops weETH and wstETH on Aave and Spark ($1.18B of collateral, health factor 1.027) and borrows $181M of dollars on the side. Over two years the loop added about +68 ETH over holding the same ETH unlevered (+0.02 pp a year), and the dollar leg cost about 0.13 pp a year; two rate spikes (July 2025, April 2026) wiped out the loop\u2019s carry. The 0.66 pp lead over stETH sits in income our model cannot assign (other strategies and timing, +1.5 pp a year before fees), and the share price did not show the loop\u2019s April loss when it happened.',lesson:'Ask a manager to explain the return by leg; here neither leg does.'},
 yieldbasis:{title:'The only top-five product whose fees pay for its debt',text:'YieldBasis pairs 10,426 ETH of depositors’ WETH with an equal 27.8M crvUSD loan in a 2x Curve LP. Curve fees grew 9.19% a year on twice the debt against a fixed 10% rate. Unstaked LP holders still trailed stETH by 1.27 pp over 94 days: gauge rewards in YB go to stakers, and the token fell 87%.',lesson:'Trading fees can carry the loan; the depositor’s ETH return depends on who gets the rewards.'},
 'lido-earn':{title:'Mostly a staking loop with a small USDT sleeve that pays',text:'Earn ETH (83,309 ETH) holds stRATEGY, which owes 355k WETH across Aave and Spark at health factor 1.035 and $25.6M of USDT parked in earnUSD. The USDT sleeve earned 4.80% against 4.33% of interest; a 5M USDT loan made on 29 September cleared +1,401 USDT in four days. The April rsETH incident froze the vault for 27 days and cost the DAO 144.8 ETH.',lesson:'A positive dollar spread is easiest when the parking vault is your own and you are half of it.'},
 avant:{title:'Positive spread, all of it Avant’s own credit',text:'Avant borrows $10.0M of USDC, USDS and PYUSD against ETH on Aave and Spark at 6.30% and parks 98% of it in savUSD, Avant’s own dollar product, which paid 7.54%. Repaying the debt means a 24-hour cooldown, a bridge from Avalanche and up to seven days of redemption.',lesson:'Parking in the issuer’s own product turns the spread into one credit bet with a week-long exit.'},
 liquity:{title:'Cheap loan, but the parked dollars earn even less',text:'The vault borrows 6.75M ebUSD on Ebisu against 4,585 wstETH at a 2.55% rate it sets itself (LTV 44%, liquidation at 83%) and provides ebUSD/USDC liquidity on Curve and Uniswap v4, which earned 0.45% in fees. The debt is easy to repay: 97.5% can be bought back on Curve in one block.',lesson:'A self-set borrow rate is only cheap until the stablecoin’s peg needs defending.'},
 rocksolid:{title:'Three chains, two wallets, one rETH share',text:'Rocksolid (9,728 ETH) runs ETH loops on Monad and Ethereum through an MPC wallet, bridging wstETH out and borrowed WETH back; a second wallet borrows $2.7M USDC against rETH. The book reconciles to within 0.04%. Dollar carry is 10.5% of it. The owner closed the vault on 29 September and reopened it with a contract upgrade on 7 October.',lesson:'A vault that can be closed and reopened by upgrade has no fixed exit terms.'},
 royco:{title:'A 30% loan inside a 116 ETH vault',text:'Royco ETH borrows 91k PYUSD against wstETH on Morpho at 30.24% and holds a senior Royco credit receipt. The parent’s accounting call reverts and immediate withdrawal capacity is zero; withdrawals run in 30-day epochs with KYC.',lesson:'Show the mark’s age and the exit state next to the share price.'},
 concrete:{title:'307k ETH, one owner',text:'Concrete Delta’s whole supply was minted to one address on 16 December 2025, six days after a Bitfinex-linked wallet moved its own Aave position (246,740 wstETH) into the vault’s Safe. The Safe holds 99.96% of the book and borrows $176M of stablecoins against it at 21% LTV. No deposits or withdrawals since.',lesson:'Not a product: a single principal’s mandate. Left out of the map and the top five.'}
});

// Risks: one table (replaces strict.js stRisks).
function stRisks(){const rows=[
 ['Funding cost','Aave USDC cost 13.93% on 2 October and 12.6 to 14.1% at every month-end since June; Aave USDT cost 4.38%. Liquid’s dollar leg loses about $6.8M a year at those rates.','Borrow the cheapest hub currency; cut any leg whose base yield stays below its loan rate.'],
 ['Rewards','Merkl rewards are $2.6M of Liquid’s $7.3M dollar income; they trace to the RLUSD and PYUSD issuers’ side, campaign by campaign, a week at a time.','Price the product without them; show who pays and until when.'],
 ['Liquidation','Liquid’s main Aave ETH loop runs at health factor 1.027; its dollar legs at 1.27 to 1.87 (a 21% ETH fall to the first liquidation). Lido Earn’s loops sit at 1.035.','Keep dollar legs far from liquidation; a loop can be thin, a dollar leg cannot.'],
 ['Exit','A quarter of Liquid’s dollar debt has no dollar asset behind it; Avant needs a week to bring savUSD back from Avalanche; Rocksolid closed its vault for eight days; Royco can pay out nothing today.','Match every loan with a same-day source of the same currency.'],
 ['Restaking tokens','The April 2026 rsETH exploit froze Lido Earn for 27 days and cost its DAO 144.8 ETH; Aave was left with bad debt.','Treat a restaking token as credit, not as ETH, when sizing collateral.'],
 ['Own and nested credit','Avant parks 98% in its own savUSD; Lido Earn is 48.5% of earnUSD; Liquid borrows from the Sentora vaults it deposits into.','Disclose self-credit and look through to the final borrower.'],
 ['Keys and fees','Liquid’s 24-hour timelock does not cover the role that can change its fee; Liquity’s and Rocksolid’s managers act with no delay.','Put every fee and strategy change behind a delay longer than the exit.'],
 ['Borrow market fills up','Aave USDC on Ethereum ran at 12.6 to 14.1% at every month-end since June; Liquid owes $64.6M there. One large borrower can move a rate for everyone.','Size each loan to what the market can absorb without the rate jumping.'],
 ['Slow exit','Liquid\u2019s queue paid in 12.6 hours at the median but 12 days at worst; Avant needs a week to bring dollars back from Avalanche.','Promise only the exit the slowest leg allows.'],
 ['Who is the investor','Concrete Delta’s 307k ETH is one wallet’s own position, which DefiLlama lists as a $941M product (with a circular second vault); three private rSHARE vaults hold 83k WETH for what looks like one principal.','Check holders before calling a vault a product.']
 ];$('#strict-risk-table').innerHTML=stTable(['Risk','What we saw','Rule for a product'],rows.map(r=>r.map(esc)),'strict-risks');const h=$('#reader-risk-details summary');if(h)h.textContent='Risks: what broke or nearly broke ETH carry';const lede=$('#reader-risk-details .shead .lede');if(lede)lede.textContent='In 2025 and 2026 the losses came from a restaking token (rsETH) and from expensive dollar loans, not from the ETH price.';}

// Data: method of the counted-once map (replaces the protocol-ledger method text of strict.js stData).
const _atPrevData=typeof stData==='function'?stData:null;
function atMethod(){
 const el=$('#strict-method');if(!el)return;
 el.innerHTML=`<p><b>What is counted.</b> Products that pay a yield on ETH, each counted once: ${MP.products_count_default} products and ${ATK(MP.default_current.eth_ref)} ETH on 2 October 2026 (DefiLlama point stamped 3 October 00:00 UTC), and every month-end from October 2024. The ETH part of each protocol’s token breakdown, at the ETH price of the same point.</p>
 <p><b>Counted once.</b> A staking or restaking token held by another product leaves its issuer’s row and is counted in the product that holds it. Products report what their depositors own: a looped vault counts its equity, and the ETH it borrowed stays with the staking issuer it was staked through. Restaking platforms count only what no restaking token on the map already counts (an estimate). Money markets and CDPs count only plain ETH and WETH, not staking tokens posted as collateral, and are off by default: lent ETH is staked again by its borrowers.</p>
 <p><b>On-chain books.</b> The carry products are measured at block 26,108,081 and replace their DefiLlama rows; twelve also at each month-end, NEMO and Sentora at the snapshot only. DEX projects without a token breakdown (Uniswap v3 and v4, SushiSwap v2) are their ETH pools above $1M, plain-ETH side only.</p>
 <p><b>What was cut.</b> Infrastructure (SSV, Obol), curators whose vaults sit in Morpho and Euler, LP-staking aggregators, duplicate listings, synthetic ETH (msETH, alETH), frozen adapters and non-products; each with its reason in “Listed, but not counted”. Every netting step is in the ledger below.</p>
 <p><b>Judgement calls.</b> Concrete Delta and three rSHARE vaults are left out as single-principal mandates (the BTC map left out Avalon the same way). ether.fi\u2019s weETH counts as restaking. A carry product counts as carry only in months it owed dollars; Liquid ETH sits in leveraged staking from October 2024 to July 2025. EigenLayer and Symbiotic count only what no restaking token already counts. Balances unchanged for three months or more count as leftovers (zero).</p><p><b>Not verified.</b> The restaking-platform remainder is an estimate. DEX pool history covers only pools above $1M today. NEMO and Sentora have the snapshot only. Off-chain staking is sized from beacon-chain entity tags dated 7 October. Returns over 30 days are annualised and noisy.</p><div class="section-actions"><a class="btn" href="data/netmap/market_map_current.csv" download>Map, 2 October</a><a class="btn" href="data/netmap/market_map_history_monthly.csv" download>Month-ends by product</a><a class="btn" href="data/netmap/category_history_monthly.csv" download>Month-ends by category</a><a class="btn" href="data/netmap/netting_ledger.csv" download>Netting ledger</a><a class="btn" href="data/netmap/product_notes.csv" download>Product notes</a></div>`;
}
const _atPrevAnswer2=readerAnswer;readerAnswer=function(){_atPrevAnswer2();atMethod();if(typeof stRisks==='function')stRisks();};

// Data: the DefiLlama cross-check and the re-check of the snapshot (data/eth/netmap/crosscheck.json).
function atCheck(){
 const C=R.netmapCheck;if(!C)return;const d=$('#strict-discovery'),r=$('#strict-recheck');
 const tv=C.tvl_by_status||{},all=Object.values(tv).reduce((s,v)=>s+v,0);
 if(d)d.innerHTML=`<p>DefiLlama lists ${num(C.pools_checked,0)} ETH pools above $1M on its yields page. ${ATPCT((tv.map||0)/all,1)} of their TVL belongs to products on the map and ${ATPCT((tv.excluded||0)/all,1)} to rows left out for a stated reason. The rest (${ATUSD(all-(tv.map||0)-(tv.excluded||0))}) is below:</p>`+'<div class="tblwrap">'+stTable(['Project','Pools','Pool TVL','Why it is not on the map'],C.not_in_map.map(x=>[esc(x.project),num(x.pools,0),ATUSD(x.tvlUsd),esc(x.status)+'<div class="sub">'+esc(x.symbols.join(', '))+'</div>']))+'</div>'+`<p class="note">${esc(C.note)}</p>`;
 if(r)r.innerHTML=`<p>The largest rows read again at DefiLlama’s latest point (${esc(C.recheck?.[0]?.later_date||'')}): the median moved ${(()=>{const v=(C.recheck||[]).map(x=>Math.abs(x.change||0)).sort((a,b)=>a-b);return v.length?ATPCT(v[Math.floor(v.length/2)],2):'n/a'})()}.</p>`+'<div class="tblwrap">'+stTable(['Product','2 October, ETH','Later, ETH','Change'],(C.recheck||[]).map(x=>[esc(x.product),num(x.snapshot_gross_eth,0),num(x.later_gross_eth,0),(x.change>=0?'+':'')+ATPCT(x.change,2)]))+'</div><p class="note">Gross ETH part of each protocol before netting.</p>';
}
const _atPrevAnswer3=readerAnswer;readerAnswer=function(){_atPrevAnswer3();atCheck();};

// Product chapters read their story from PC too: keep both in step.
PC.products.forEach(p=>{if(ST_STORIES[p.id])p.story=ST_STORIES[p.id];});
// The old market-overlap disclosure is superseded by the counted-once map.
function atHideOld(){['#market-net-capital','#m-overlap-example'].forEach(s=>{const e=$(s);if(e)e.hidden=true;});$$('details.more>summary').forEach(x=>{if(/Why reported ETH exposure is larger than unique capital/.test(x.textContent))x.parentElement.hidden=true;});}

// Top 5 comparison matrix (replaces the investor-question table).
function atComparison(){
 const el=$('#strict-top5-comparison');if(!el)return;
 const ids=EQ.topFive,R30=Object.fromEntries((R.reportContract.matched30dReturns||[]).map(r=>[r.id,r]));
 const C={liquid:{to:'Sentora RLUSD and PRIME vaults, Cap stcUSD',park:'2.8 to 5.6% + 1.4% rewards',spread:'−$6.8M a year',exit:'49% same block; 26% unmatched',key:'24h timelock; a fee role has none',risk:'13.93% USDC loan; ETH loop at HF 1.03'},
  yieldbasis:{to:'Its own 2x WETH/crvUSD Curve pool',park:'9.19% fees on 2x debt',spread:'fees cover the 10%',exit:'99.6% same block',key:'veYB vote (7 days, can run early); a 5-of-9 Safe can kill',risk:'Rewards go to stakers; LP exit value'},
  'lido-earn':{to:'earnUSD (Lido Earn USD)',park:'4.80%',spread:'+0.47 pp',exit:'earnUSD queue, next daily report',key:'5-of-8 Safe, no timelock; upgrades instantly',risk:'rsETH loop at HF 1.035 (12% of the book): a 3.4% rsETH fall liquidates it; 48.5% of earnUSD'},
  avant:{to:'savUSD, Avant’s own dollar product',park:'7.54%',spread:'+1.24 pp',exit:'2.4% same block; savUSD cooldown + bridge + 7 days',key:'One plain address, no delay on anything',risk:'Own credit; Avalanche exit'},
  liquity:{to:'ebUSD/USDC on Curve and Uniswap v4',park:'0.45% fees',spread:'−2.1 pp',exit:'97.5% same block via Curve',key:'One 2-of-3 Safe, no delay',risk:'ebUSD peg; self-set rate'}};
 const p=id=>PC.products.find(x=>x.id===id),f=id=>EQ.products.find(x=>x.id===id),risk=id=>R.atlasTop5Risk?.products?.[id];
 const worst=id=>({liquid:'1.27 (Morpho weETH/RLUSD); 21% ETH fall to liquidation',yieldbasis:'no liquidation; debt 50% vs 56.25% critical','lido-earn':'2.12; 53% fall',avant:'1.37; 27% fall',liquity:'1.88; 47% fall'})[id]||'';
 const row=(label,fn)=>`<tr><th>${label}</th>${ids.map(id=>`<td>${fn(id)}</td>`).join('')}</tr>`;
 el.innerHTML=`<table class="at-compare"><thead><tr><th></th>${ids.map((id,i)=>`<th>#${i+1} ${esc(p(id)?.name||id)}</th>`).join('')}</tr></thead><tbody>`+
  row('Book, ETH',id=>num(p(id)?.capitalETH,0))+
  row('Dollars borrowed',id=>ATUSD(f(id)?.current.debtUSD))+
  row('Loan rate',id=>pct(f(id)?.current.apr,2))+
  row('Where the dollars go',id=>esc(C[id].to))+
  row('Parked dollars earn',id=>esc(C[id].park))+
  row('Dollar spread at 2 October',id=>esc(C[id].spread))+
  row('Without rewards (90 days, a year)',id=>({liquid:'2.94%<div class="sub">actual 3.32%</div>',yieldbasis:'\u22122.96%<div class="sub">staked +1.69% with YB</div>','lido-earn':'3.14%<div class="sub">no rewards</div>',avant:'4.55%<div class="sub">actual 4.74%</div>',liquity:'2.26%<div class="sub">actual 3.84%</div>'})[id]||'')+
  row('Rewards share of the lead over stETH',id=>({liquid:'35%',yieldbasis:'all of it (staked)','lido-earn':'0%',avant:'7%, points unpriced',liquity:'99%'})[id]||'')+
  row('Paid in ETH, a year (2 Sep to 2 Oct)',id=>R30[id]?(R30[id].bookReturnPct*365/30).toFixed(2)+'%<div class="sub">'+(R30[id].excessPercentagePoints>=0?'+':'')+(R30[id].excessPercentagePoints*365/30).toFixed(2)+' pp vs stETH</div>':'')+
  row('Lowest health factor of a dollar loan',id=>worst(id))+
  row('Debt repayable',id=>esc(C[id].exit))+
  row('Who can change it',id=>esc(C[id].key))+
  row('Main risk',id=>esc(C[id].risk))+'</tbody></table>';
 const sub=el.closest('.panel')?.querySelector('.sub');if(sub)sub.textContent='2 October 2026; returns over 2 September to 2 October, annualised. Dollar spread is what the parked dollars earn less the loan rate.';
 const h=el.closest('.panel')?.querySelector('h3');if(h)h.textContent='The five, side by side';
}
const _atPrevFinal=atlasFinal;atlasFinal=function(){_atPrevFinal();atHideOld();atComparison();};

// Borrower table: identities resolved after the snapshot research (Concrete Delta).
(function(){const B=R.borrowersChapter;if(!B)return;const walk=v=>{if(Array.isArray(v))v.forEach(walk);else if(v&&typeof v==='object'){if(v.who==='Concrete shared Safe'){v.who='Concrete Delta Safe (Bitfinex-linked principal)';v.evidence='The wallet that funded the Safe moved its own Aave position into it on 10 Dec 2025 and holds 100% of Concrete Delta; it remains one of five signers. Not a pooled product.';}Object.values(v).forEach(walk);}};walk(B);})();

// Data: coverage by category (replaces the earlier mechanism matrix).
function atCoverage(){
 const el=$('#reader-coverage-matrix');if(!el)return;
 const n=id=>atRows(id).length,v=id=>ATK(atCatSize(id));
 const rows=[
  ['Staking',v('staking'),n('staking'),'Issuer backing from DefiLlama, net of tokens held by other products; native consensus state (43.81M ETH active) as the ceiling','Every month-end; 14.4M ETH of off-chain stake listed, not counted'],
  ['Restaking',v('restaking'),n('restaking'),'Restaking-token issuers; EigenLayer and Symbiotic only for what no restaking token counts (estimate)','Every month-end'],
  ['Carry',v('carry'),n('carry'),'On-chain books, loans and destinations at block 26,108,081; Concrete Delta excluded as one wallet’s position','Twelve products every month-end; NEMO and Sentora at the snapshot'],
  ['Leveraged staking',v('loops'),n('loops'),'Depositor equity (gross collateral scaled down where the adapter reports it)','Every month-end'],
  ['Farming and pools',v('farming'),n('farming'),'DEX pools: plain ETH side only; Uniswap v3/v4 from pools above $1M','Pools without a token breakdown only for pools that still exist'],
  ['Fixed yield, basis, options, credit',ATK(atCatSize('fixed_yield')+atCatSize('basis')+atCatSize('options')+atCatSize('credit')),n('fixed_yield')+n('basis')+n('options')+n('credit'),'DefiLlama breakdowns, checked against the products’ own pages','Every month-end; most are residuals of 2024 products'],
  ['Money markets, CDPs (off)',ATK(atCatSize('lending')+atCatSize('cdp')),n('lending')+n('cdp'),'Idle plain WETH and ETH collateral only','Every month-end']];
 el.innerHTML='<div class="tblwrap">'+stTable(['Category','ETH','Products','How it is measured','History'],rows.map(r=>r.map(x=>esc(String(x)))))+'</div>';
}
const _atPrevAnswer4=readerAnswer;readerAnswer=function(){_atPrevAnswer4();atCoverage();};

// Borrower table: names from the 7 Oct identification (data/eth/gap_borrowers.csv via atlas_build.py).
(function(){const ID=R.atlasTop5Risk?.borrowers;const B=R.borrowersChapter;if(!ID||!B)return;const walk=v=>{if(Array.isArray(v))v.forEach(walk);else if(v&&typeof v==='object'){const k=String(v.address||'').toLowerCase();if(k&&ID[k]&&'who' in v){v.who=ID[k].who;v.evidence=(ID[k].pooled_product==='yes'?'Pooled product. ':ID[k].pooled_product==='no'?'Not a pooled product. ':'Private vault. ')+(ID[k].destination_of_dollars?'Dollars went to: '+ID[k].destination_of_dollars+'. ':'')+'Full trace in Borrower identities.';}Object.values(v).forEach(walk);}};walk(B);})();
ATLAND.splice(1,0,['Private rSHARE vaults (three managers)','Private; not counted','Three whitelist-only WETH receipt vaults (about 83k WETH) whose managers borrow $87.1M of dollars, 10.6M EURCV and 75k WETH against it, into RockawayX, Sentora, Hastra, Wintermute and Pendle vaults','Same operator (managers created the same day, gas from the same exchange); depositors look like one principal; shares cannot move and the owner sets NAV off-chain, never posted. Like Concrete, a mandate, not a product.','']);

// Reader pruning to the BTC page's scope (parity audit 7 Oct, research/eth/review/parity-audit-2026-10-07).
function atPrune(){
 // older layers still say "at T" and "Hover"; plain wording for the reader
 const tw=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while((n=tw.nextNode())){const v=n.nodeValue;if(/\bat T\b|Hover /.test(v))n.nodeValue=v.replace(/\bat T\b/g,'on 2 October').replace(/Hover a month, or focus the chart and use the arrow keys/g,'Point at a month').replace(/Hover /g,'Point at ');}
 if(document.body.dataset.edition!=='reader')return;
 const drop=(sel)=>$$(sel).forEach(e=>e.remove());
 const dropDetails=re=>$$('details.more>summary').forEach(s=>{if(re.test(s.textContent))s.parentElement.remove();});
 dropDetails(/Products awaiting dollar-carry verification|Share prices and measured ETH returns|^By chain$|Coverage by mechanism|Why reported ETH exposure/);
 drop('.chapter-transition');
 $$('.section-actions').forEach(e=>{if(!e.closest('#data'))e.remove();});
 $$('#market .note').forEach(n=>{if(/Borrowing against ETH establishes financing/.test(n.textContent))n.remove();});
 $$('#market-history [data-market-flags]').forEach(e=>e.remove());   // switches only at the top of Market
 const pr=$('#print');if(pr)pr.remove();$$('#data a.btn').forEach(a=>{if(/Original BTC Research/.test(a.textContent))a.remove();});
 const lib=$('#data .library-grid');if(lib)lib.outerHTML='<p>Research behind the page: '+[['library/BRIEFING.html','briefing'],['library/SELECTION.html','how the five were chosen'],['library/CONCRETE-DELTA.html','Concrete Delta'],['library/TOP5-RISK-LIQUIDITY.html','top-five risk and repayment'],['library/REWARDS-SPLIT.html','organic yield against rewards'],['library/LIQUID-LOOP.html','Liquid ETH loop'],['library/TOP5-KEYS-HOLDERS-TERMS.html','keys, holders and terms'],['library/CLOSED-CASES.html','closed and stressed cases'],['library/RESTAKING-AND-LOOPS.html','restaking and loops'],['library/BORROWER-IDENTITIES.html','who borrows against ETH'],['library/OUTSIDE-AND-SMALL.html','off-chain staking and small categories'],['library/index.html','all articles']].map(([u,t])=>`<a href="${u}">${t}</a>`).join(' · ')+'</p>';
 atBorrowers();
}
// Borrowers: wallets over $20M of dollar debt against ETH, one line each (BTC format)
function atBorrowers(){
 const ID=R.atlasTop5Risk?.borrowers||{};const host=$('#borrowers');if(!host)return;
 const sum=host.closest('details')?.querySelector('summary');if(sum)sum.textContent='Who borrows dollars against ETH: every wallet over $20M';
 const rows=Object.entries(ID).map(([a,r])=>({a,...r,d:+r.dollar_debt_usd_T||0})).filter(r=>r.d>=20e6).sort((x,y)=>y.d-x.d);
 host.innerHTML=`<p>Every Ethereum wallet with more than $20M of dollar debt against ETH collateral at the snapshot (Morpho, Aave, Spark), traced to who it is. Pooled products with outside depositors are marked; the rest are funds, mandates and individuals.</p><div class="tblwrap"><table><thead><tr><th>Wallet</th><th>Who</th><th class="n">Dollar debt</th><th>Pooled product?</th><th>Where the dollars went</th></tr></thead><tbody>${rows.map(r=>`<tr><td><a href="https://etherscan.io/address/${r.a}" target="_blank" rel="noopener" class="mono">${short(r.a)}</a></td><td>${esc(r.who)}</td><td class="n">${ATUSD(r.d)}</td><td>${esc(r.pooled_product==='yes'?'yes':r.pooled_product==='no'?'no':'private vault')}</td><td>${esc(String(r.destination_of_dollars||'').slice(0,160))}</td></tr>`).join('')}</tbody></table></div><p class="note">Full trace of 23 wallets: <a href="library/BORROWER-IDENTITIES.html">who borrows against ETH</a>.</p>`;
}
const _atPrevFinal2=atlasFinal;atlasFinal=function(){_atPrevFinal2();atPrune();};

// Category insights with numbers (Market, "Who is in each category"); research/eth/en/RESTAKING-AND-LOOPS.md.
const ATINSIGHT={
 staking:'<b>Staking pays less every year.</b> Lido’s oracle reports show consensus rewards falling from 2.78% to 2.38% gross and priority fees plus MEV from 0.55% to 0.09% between October 2024 and September 2026. Issuers keep 5 to 15% (Lido 10%, Renzo 15%, Kelp and Puffer 5%).',
 restaking:'<b>Restaking paid in its own token, and less each year.</b> EigenLayer distributed $137M in its first year and $36M in its second, 99.6% of it EIGEN issued by Eigen itself; services paid $0.75M in two years. ETH and LST restakers got 0.78% and then 0.18% a year, and nothing programmatic since 30 July 2026. weETH trailed stETH by 0.19 pp over two years. The 13 real slashes (32.4k ETH equivalent) all came from one operator’s redistributable sets.',
 loops:'<b>The loop spread is thin and sometimes negative.</b> stETH minus the Aave WETH borrow rate averaged +0.15 pp in the first year and +0.10 pp in the second, and was negative in 6 of 24 months; in April 2026, at 99.2% utilization, it was −1.04 pp. A 10x loop averaged 3.81% against 2.68% for plain stETH. WETH debt on Aave and Spark peaked at 3.27M ETH in January 2026 and is 2.27M now.'};
function atLoopChart(){const L=R.atlasTop5Risk?.loopRegime||[];if(!L.length)return '';const t=m=>{const [y,mm]=m.split('-').map(Number);return Date.UTC(y,mm,0)/1000;};
 const s=k=>L.filter(r=>/^\d{4}-\d{2}$/.test(r.month)&&r[k]!==''&&r[k]!=null).map(r=>[t(r.month),+r[k]*100]);
 return '<div class="chart-scroll" style="margin-top:10px">'+lineChart([{name:'stETH yield',color:'#3fae9a',points:s('steth_holder_apr_month')},{name:'Aave WETH borrow rate',color:'var(--danger, #d9534f)',points:s('aave_core_weth_borrow_apr_month_avg')}],{yLabel:'Monthly average, % a year',format:v=>num(v,1)+'%'})+'</div>';}
const _atPrevCat=marketCatalogue;
function atCatInsight(){const id=MS.category,x=ATINSIGHT[id],b=$('#m-category-body .cx');if(!x||!b||b.querySelector('.at-insight'))return;const kd=b.querySelector('.cx-facts');(kd||b.firstElementChild).insertAdjacentHTML('afterend','<p class="kd at-insight">'+x+'</p>'+(id==='loops'?atLoopChart():''));}
document.addEventListener('click',e=>{if(e.target.closest('[data-market-pick]'))setTimeout(atCatInsight,0);});
const _atPrevFinal3=atlasFinal;atlasFinal=function(){_atPrevFinal3();atCatInsight();};
