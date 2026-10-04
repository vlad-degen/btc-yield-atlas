// Presentation and exports use captured values; no live data or remote requests.
function comparison(){
  const strategies={etherfi:'ETH loops + dollar carry + LP',fluid:'Leveraged staking / LP',treehouse:'wstETH market-efficiency yield',concrete:'ETH collateral / private dollar strategies',cian:'Recursive rsETH restaking'};
  const units={etherfi:num(R.etherfi.published_book_nav_eth,0)+' ETH',fluid:'77,364 stETH',treehouse:'19,860 IAU_wstETH',concrete:'278,171 weETH + 36,440 wstETH',cian:'1,417 rsETH'};
  const exit={etherfi:'Share sale / weETH queue / portfolio unwind',fluid:'5 bp checked withdrawal fee',treehouse:'~7d standard; 5 bp / 0.5% fast',concrete:'Investor agreement; captured UI said 7d',cian:'0.02% policy; contract override unverified'};
  const boundary={etherfi:'Book; 2.634% unresolved residual',fluid:'Parity valuation; 4.692 stETH gap',treehouse:'IAU conversion verified; backing open',concrete:'Shared Safe; external equity unknown',cian:'Oracle conversion; rewards/recovery excluded'};
  function ret(id,days){if(id==='concrete')return null;if(id==='etherfi')return R.etherfiReturns.find(r=>r.days===days).liquidETH_cumulative_return;return R.returns.find(r=>r.days===days&&r.product===productList.find(p=>p[0]===id)[1])?.ETH_pps_cumulative_return}
  $('#product-comparison tbody').innerHTML=productList.map(([id,name])=>`<tr><td><a href="?product=${id}#product-content" data-compare-product="${id}"><b>${name}</b></a></td><td>${strategies[id]}</td><td>${units[id]}</td><td class="n">${pct(ret(id,365),4)}</td><td class="n">${pct(ret(id,730),4)}</td><td>${exit[id]}</td><td>${boundary[id]}</td></tr>`).join('');
  $('#product-comparison').onclick=e=>{const link=e.target.closest('[data-compare-product]');if(!link)return;e.preventDefault();product(link.dataset.compareProduct);$('#product-content').scrollIntoView({behavior:'smooth'})};
}
function csvContent(headers,rows){
  const cell=v=>'"'+String(v??'').replaceAll('"','""')+'"';
  return headers.map(cell).join(',')+'\r\n'+rows.map(r=>r.map(cell).join(',')).join('\r\n');
}
function filteredCSV(){return csvContent(['chain','project','symbol','full_pool_TVL_USD','display_APY_percent','base_APY_percent','reward_APY_percent','pool_ID'],filteredPools.map(r=>[r.chain,r.project,r.symbol,r.tvlUsd,r.apy,r.apyBase,r.apyReward,r.pool]));}
function updateExport(kind){
  const link=$(`[data-export="${kind}"]`);if(!link)return;
  if(kind==='wealth'){const mask=Object.keys(R.wealth.series).reduce((m,n,i)=>m+(!hiddenSeries.has(n)?2**i:0),0);link.href=`data/wealth-series-${mask}.csv`;link.download='ETH-book-wealth.csv'}
  if(kind==='etherfi'){link.href='data/Liquid-ETH-monthly-history.csv';link.download='Liquid-ETH-monthly-history.csv'}
  if(kind==='protocol'){link.href='data/protocol-'+$('#history-protocol').value+'-history.csv';link.download=$('#history-protocol').value+'-history.csv'}
  if(kind==='pools'&&$('#filtered-csv-text')){$('#filtered-csv-text').value=filteredCSV();$('#csv-status').textContent=`${num(filteredPools.length)} filtered rows · null values remain blank.`}
}
function wealthRows(){
  const names=Object.keys(R.wealth.series).filter(n=>!hiddenSeries.has(n));
  const timestamps=[...new Set(names.flatMap(n=>R.wealth.series[n].map(r=>r.timestamp)))].sort((a,b)=>a-b);
  const maps=Object.fromEntries(names.map(n=>[n,new Map(R.wealth.series[n].map(r=>[r.timestamp,r.normalized_ETH_book_wealth]))]));
  return {names,rows:timestamps.map(t=>[date(t),...names.map(n=>maps[n].get(t)??null)])};
}
function wealthTable(){const {names,rows}=wealthRows();$('#wealth-table').innerHTML='<thead><tr><th>Date UTC</th>'+names.map(n=>'<th class="n">'+esc(n)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr><td>'+r[0]+'</td>'+r.slice(1).map(v=>'<td class="n">'+num(v,6)+'</td>').join('')+'</tr>').join('')+'</tbody>';updateExport('wealth');}
function displayControls(group){return `<div class="view-switch" role="group" aria-label="${group} display"><button class="btn" data-display-group="${group}" data-display="chart" aria-pressed="true">Chart</button><button class="btn" data-display-group="${group}" data-display="table" aria-pressed="false">Table</button></div>`}
function displayView(group,view){const chart=$('#'+group+'-chart'),table=$('#'+group+'-table-view');if(!chart||!table)return;chart.hidden=view!=='chart';table.hidden=view!=='table';$$(`[data-display-group="${group}"]`).forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.display===view)));}
let etherfiMetric='nav',etherfiDisplay='chart';
function productHistoryPanel(){return `<div class="panel" id="etherfi-history"><h3>Liquid ETH: capital and returns over 24 months</h3><p class="sub">October 2024 to September 2026. Capital includes changes in the number of shares. Monthly returns measure the share value, adjusted for its underlying asset. Growth in capital is different from investor return.</p><div class="chart-toolbar"><div class="seg" role="group" aria-label="Liquid ETH history metric"><button class="btn" data-etherfi-metric="nav" aria-pressed="true">Published capital · ETH</button><button class="btn" data-etherfi-metric="returns" aria-pressed="false">Monthly returns</button></div>${displayControls('etherfi')}</div><div class="chart-scroll" id="etherfi-chart"></div><div class="tblwrap" id="etherfi-table-view" hidden><table id="etherfi-table"><thead><tr><th>Month</th><th class="n">Book NAV ETH</th><th class="n">Liquid ETH return</th><th class="n">stETH return</th><th class="n">weETH return</th><th class="n">Excess vs stETH, pp</th></tr></thead><tbody></tbody></table></div><a class="btn" data-export="etherfi" download>Download 24-month CSV</a><p class="note" style="margin-top:12px">Published accounting values. Separately paid rewards and the amount realised on exit are outside this series. The contract snapshot follows the last completed monthly point.</p></div>`}
function etherfiHistory(){
  const rows=R.etherfiHistory;
  const series=etherfiMetric==='nav'?[{name:'Liquid ETH book NAV',color:colors['Liquid ETH'],points:rows.map(r=>[r.end_timestamp,r.book_nav_eth])}]:[['Liquid ETH','liquidETH_monthly_return'],['stETH','stETH_monthly_return'],['weETH','weETH_monthly_return']].map(([name,key])=>({name,color:colors[name],points:rows.map(r=>[r.end_timestamp,r[key]*100])}));
  $('#etherfi-chart').innerHTML=(etherfiMetric==='nav'?columnChart:lineChart)(series,{label:'Liquid ETH monthly capital',yLabel:etherfiMetric==='nav'?'Liquid ETH book NAV · ETH':'Monthly book returns · percent',format:etherfiMetric==='nav'?v=>num(v,0)+' ETH':v=>num(v,3)+'%'});
  $('#etherfi-table tbody').innerHTML=rows.map(r=>`<tr><td>${r.month}</td><td class="n">${num(r.book_nav_eth,3)}</td><td class="n">${pct(r.liquidETH_monthly_return,4)}</td><td class="n">${pct(r.stETH_monthly_return,4)}</td><td class="n">${pct(r.weETH_monthly_return,4)}</td><td class="n">${num((r.liquidETH_monthly_return-r.stETH_monthly_return)*100,4)}</td></tr>`).join('');
  $$('[data-etherfi-metric]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.etherfiMetric===etherfiMetric)));
  displayView('etherfi',etherfiDisplay);updateExport('etherfi');
}
function initPresentation(){
  comparison();wealthTable();
  document.addEventListener('click',e=>{
    const display=e.target.closest('[data-display-group]');if(display){if(display.dataset.displayGroup==='etherfi')etherfiDisplay=display.dataset.display;displayView(display.dataset.displayGroup,display.dataset.display)}
    const metric=e.target.closest('[data-etherfi-metric]');if(metric){etherfiMetric=metric.dataset.etherfiMetric;etherfiHistory()}
    const exportButton=e.target.closest('[data-export="pools"]');if(exportButton){const panel=$('#filtered-csv-preview');panel.hidden=!panel.hidden;exportButton.setAttribute('aria-expanded',String(!panel.hidden));updateExport('pools')}
    const copy=e.target.closest('#copy-filtered-csv');if(copy){navigator.clipboard.writeText($('#filtered-csv-text').value).then(()=>{$('#csv-status').textContent=`Copied ${num(filteredPools.length)} filtered rows.`}).catch(()=>{$('#filtered-csv-text').focus();$('#filtered-csv-text').select();$('#csv-status').textContent='Select and copy the CSV below.'})}

  });
}
