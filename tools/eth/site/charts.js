// Capital is sampled by month: equal-width columns, as in the BTC reference.
// Missing values have no segment. Signed liabilities remain below the baseline.
function chartNice(v){if(!(v>0))return 1;const scale=10**Math.floor(Math.log10(v));return [1,1.5,2,2.5,3,4,5,6,8,10].find(n=>n*scale>=v)*scale;}
function chartShort(v,format){const label=format(v);if(Math.abs(v)<1000)return label;if(label.includes('ETH'))return num(v/(Math.abs(v)>=1e6?1e6:1e3),Math.abs(v)>=1e6?1:0)+(Math.abs(v)>=1e6?'M':'k')+' ETH';return label;}
function chartMonth(t){return new Date(t*1000).toLocaleDateString('en-GB',{month:'short',year:'2-digit',timeZone:'UTC'});}
function columnChart(series,{share=false,label='',format=v=>num(v,0),height=300,legend=true,small=false,grouped=false}={}){
 const times=[...new Set(series.flatMap(s=>s.points.map(p=>p[0])))].sort((a,b)=>a-b);
 const points=series.map(s=>({...s,values:times.map(t=>s.points.find(p=>p[0]===t)?.[1]??null)}));
 if(!points.some(s=>s.values.some(Number.isFinite)))return '<div class="empty">No dated observations available.</div>';
 const totals=times.map((t,i)=>points.reduce((n,s)=>n+(Number.isFinite(s.values[i])?s.values[i]:0),0));
 const values=points.map(s=>s.values.map((v,i)=>v==null?null:share?(totals[i]?v/totals[i]:null):v));
 const pos=times.map((t,i)=>grouped?Math.max(0,...values.map(s=>s[i]??0)):values.reduce((n,s)=>n+Math.max(0,s[i]??0),0)),neg=times.map((t,i)=>grouped?Math.min(0,...values.map(s=>s[i]??0)):values.reduce((n,s)=>n+Math.min(0,s[i]??0),0));
 const top=share?1:chartNice(Math.max(...pos)),bottom=Math.min(...neg)<0?-chartNice(-Math.min(...neg)):0;
 const mobile=innerWidth<560,W=mobile?420:small?520:720,H=height,P={l:74,r:14,t:16,b:34},band=(W-P.l-P.r)/times.length,bw=Math.max(3,Math.min(26,band-4));
 const y=v=>P.t+(top-v)/(top-bottom)*(H-P.t-P.b),x=i=>P.l+band*(i+.5),vf=v=>share?pct(v,0):chartShort(v,format);
 let svg=`<svg class="line-chart column-chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(label)}"><title>${esc(label)}</title>`;
 for(let i=0;i<=5;i++){const v=bottom+(top-bottom)*i/5;svg+=`<line x1="${P.l}" x2="${W-P.r}" y1="${y(v)}" y2="${y(v)}" stroke="var(--grid)"/><text x="${P.l-10}" y="${y(v)+4}" text-anchor="end" fill="var(--muted)" font-family="var(--mono)" font-size="11">${esc(vf(v))}</text>`;}
 const step=Math.max(1,Math.ceil(times.length/(mobile||small?4:8)));times.forEach((t,i)=>{if(i%step===0||i===times.length-1)svg+=`<text x="${x(i)}" y="${H-11}" text-anchor="middle" fill="var(--muted)" font-family="var(--mono)" font-size="11">${chartMonth(t)}</text>`;});
 times.forEach((t,i)=>{let positive=0,negative=0;const last=values.findLastIndex(s=>s[i]>0);values.forEach((s,j)=>{const v=s[i];if(v==null||v===0)return;const base=grouped?0:v>0?positive:negative,end=base+v,yy=Math.min(y(base),y(end)),hh=Math.abs(y(base)-y(end));svg+=`<rect class="capital-column" data-series="${esc(points[j].name)}" data-date="${date(t)}" data-value="${points[j].values[i]}" x="${grouped?x(i)-bw/2+j*bw/values.length:x(i)-bw/2}" y="${yy+.6}" width="${grouped?Math.max(.8,bw/values.length-1):bw}" height="${Math.max(.6,hh-1.2)}" rx="${j===last?2:0}" fill="${points[j].color}"/>`;if(v>0)positive=end;else negative=end;});
 const observed=points.some(s=>s.values[i]!=null),title=date(t)+' · '+(observed?grouped?'Separate series':format(totals[i]):'No observation');
 const rows=points.slice().reverse().map(s=>({name:s.name,color:s.color,value:s.values[i]==null?'No observation':format(s.values[i]),share:!grouped&&points.length>1&&totals[i]>0&&s.values[i]!=null?pct(s.values[i]/totals[i],s.values[i]/totals[i]<.01?2:1):null}));
 const note=title+'\n'+rows.map(r=>r.name+': '+r.value+(r.share?' · '+r.share:'')).join('\n');
 svg+=`<rect class="chart-month-hit" tabindex="${i===0?0:-1}" data-chart-tip="${esc(note)}" data-chart-title="${esc(title)}" data-chart-rows="${esc(JSON.stringify(rows))}" aria-label="${esc(note.replaceAll('\n',' · '))}" x="${P.l+band*i}" y="${P.t}" width="${band}" height="${H-P.t-P.b}" fill="transparent"/>`;
 });svg+=`<line x1="${P.l}" x2="${W-P.r}" y1="${y(0)}" y2="${y(0)}" stroke="var(--hair-2)"/></svg>`;
 return `<div class="research-chart">${svg}<div class="chart-float" role="status" hidden></div>${legend&&series.length>1?'<div class="legend">'+series.map(s=>`<span><i class="rect" style="background:${s.color}"></i>${esc(s.name)}</span>`).join('')+'</div>':''}</div>`;
}
function horizontalBars(rows,{format=v=>pct(v,2),max=null,label='Annual rate',fixed=false,measure=null}={}){
 const top=max??chartNice(Math.max(0,...rows.map(r=>r.total??0))),axis=[0,.25,.5,.75,1].map(n=>`<span style="left:${n*100}%">${esc(format(top*n))}</span>`).join('');
 return `<div class="horizontal-bars" aria-label="${esc(label)}"><div class="horizontal-axis"><span></span><div>${axis}</div><span></span></div>${rows.map(r=>{const base=r.base??null,reward=r.reward??null,note=r.name+'\n'+(r.basis||'')+(measure?'\n'+measure+': '+(r.total==null?'Not observed':format(r.total)):'\nBase: '+(base==null?'Not observed':format(base))+'\nRewards: '+(reward==null?'Not independently reported':format(reward))+'\nTotal: '+(r.total==null?'Not observed':format(r.total)));return `<div class="horizontal-row" tabindex="0" data-chart-tip="${esc(note)}"><span class="horizontal-label">${esc(r.name)}${r.basis?'<small>'+esc(r.basis)+'</small>':''}</span><div class="horizontal-track" style="--bar-grid:${fixed?'25%':'25%'}">${base!=null?`<i style="width:${Math.max(0,base/top*100)}%;background:${r.color||'var(--s2)'}"></i>`:''}${reward!=null?`<i class="reward-segment" style="width:${Math.max(0,reward/top*100)}%;background:${r.rewardColor||r.color||'var(--s2)'}"></i>`:''}</div><b>${r.total==null?'n/a':esc(format(r.total))}</b></div>`}).join('')}<div class="chart-float" role="status" hidden></div></div>`;
}
function initChartInspection(){
 const off=el=>{if(!el)return;const host=el.closest('.research-chart,.horizontal-bars,.strict-exhibit,.chart-scroll')||el.parentElement;host.querySelector('.chart-float')?.setAttribute('hidden','');host.querySelectorAll('.chart-month-hit').forEach(n=>n.classList.remove('inspected'));};
 const show=(el,event)=>{
  if(!el)return;
  const host=el.closest('.research-chart,.horizontal-bars,.strict-exhibit,.chart-scroll')||el.parentElement;
  let tip=host.querySelector('.chart-float');if(!tip){tip=document.createElement('div');tip.className='chart-float';tip.setAttribute('role','status');host.appendChild(tip);}tip.replaceChildren();
  if(el.dataset.chartRows){
   const title=document.createElement('b');title.textContent=el.dataset.chartTitle;tip.appendChild(title);
   JSON.parse(el.dataset.chartRows).forEach(r=>{const row=document.createElement('div');row.className='chart-tip-row';const label=document.createElement('span'),color=document.createElement('i'),value=document.createElement('strong');color.style.background=r.color;label.append(color,document.createTextNode(r.name));value.textContent=r.value+(r.share?' · '+r.share:'');row.append(label,value);tip.appendChild(row);});
  }else (el.dataset.chartTip||el.dataset.point||'').split('\n').forEach((s,i)=>{const row=document.createElement(i?'div':'b');row.textContent=s;tip.appendChild(row);});
  tip.hidden=false;host.querySelectorAll('.chart-month-hit').forEach(n=>n.classList.toggle('inspected',n===el));
  const box=host.getBoundingClientRect(),target=el.getBoundingClientRect(),px=event?.clientX!=null?event.clientX-box.left:target.left-box.left+target.width/2;
  const left=px>box.width*.55?px-tip.offsetWidth-12:px+12;
  tip.style.left=Math.max(0,Math.min(left,box.width-tip.offsetWidth))+'px';tip.style.top=el.classList.contains('chart-month-hit')?'8px':Math.max(4,target.top-box.top-8)+'px';
  const live=host.closest('.strict-exhibit,.panel')?.querySelector('.chart-tooltip')||host.parentElement.querySelector('.chart-tooltip');if(live)live.textContent=(el.dataset.chartTip||el.dataset.point||'').replaceAll('\n',' · ');
 };
 document.addEventListener('pointerover',e=>show(e.target.closest('[data-chart-tip],[data-point]'),e));
 document.addEventListener('pointermove',e=>show(e.target.closest('[data-chart-tip],[data-point]'),e));
 document.addEventListener('pointerout',e=>{const el=e.target.closest('[data-chart-tip],[data-point]');if(el&&!el.contains(e.relatedTarget))off(el);});
 document.addEventListener('focusin',e=>show(e.target.closest('[data-chart-tip],[data-point]')));
 document.addEventListener('focusout',e=>off(e.target.closest('[data-chart-tip],[data-point]')));
 document.addEventListener('keydown',e=>{const el=e.target.closest('.chart-month-hit');if(!el||!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;e.preventDefault();const nodes=[...el.closest('svg').querySelectorAll('.chart-month-hit')],i=nodes.indexOf(el),next=e.key==='Home'?0:e.key==='End'?nodes.length-1:Math.max(0,Math.min(nodes.length-1,i+(e.key==='ArrowRight'?1:-1)));nodes.forEach((n,j)=>n.setAttribute('tabindex',j===next?'0':'-1'));nodes[next].focus();});
}

// Rebuild the SVG label scale only when the small-screen breakpoint changes.
let chartWasMobile=innerWidth<560,chartResizeTimer;
window.addEventListener('resize',()=>{clearTimeout(chartResizeTimer);chartResizeTimer=setTimeout(()=>{const mobile=innerWidth<560;if(mobile===chartWasMobile)return;chartWasMobile=mobile;marketRender();carryCategoryRender();stRenderProduct(stProduct,false);stRenderCurve(stCurve);wealth();if($('#etherfi-chart'))etherfiHistory();protocolHistory();},120);});
