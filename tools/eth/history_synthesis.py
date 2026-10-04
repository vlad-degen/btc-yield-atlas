"""Comparable ETH book wealth and dated, non-additive protocol trends."""
import collections,datetime as dt,json
from collect import ROOT,T,read_latest

def run():
 dest=ROOT/'data/eth';read=lambda n:json.loads((dest/(n+'.json')).read_text())
 points=read('etherfi_history_points');start=T-730*86400
 base={x['target_timestamp']:x for x in points if x['target_timestamp']>=start}
 vh=read('vault_history_rpc');rates=collections.defaultdict(dict)
 for r in vh['responses']:
  l=vh['labels'][r['id']-1]
  if l['signature']=='convertToAssets(uint256)' and r.get('result') and r['result']!='0x':rates[l['name']][l['timestamp']]=int(r['result'],16)/1e18
 rr=read('rseth_benchmark_rpc');rs={rr['labels'][r['id']-1]['target_timestamp']:int(r['result'],16)/1e18 for r in rr['responses'] if r.get('result') and r['result']!='0x'}
 assert read('treehouse_denomination_history')['historical_wstETH_denomination_verified']
 assert rr['historical_oracle_identity_verified']
 series={}
 for name in ['Liquid ETH','stETH','weETH','Fluid Lite ETH','Treehouse tETH','CIAN rsETH']:
  data=[]
  for t,p in sorted(base.items()):
   v=p['liquidETH_rate'] if name=='Liquid ETH' else p['ethereum_wstETH_rate'] if name=='stETH' else p['ethereum_weETH_rate'] if name=='weETH' else rates[name].get(t)
   if v is None:continue
   if name=='Treehouse tETH':v*=p['ethereum_wstETH_rate']
   if name=='CIAN rsETH':v*=rs[t]
   data.append({'timestamp':t,'UTC':dt.datetime.fromtimestamp(t,dt.timezone.utc).isoformat(),'ETH_book_unit_value':v})
  assert data[0]['timestamp']==start and data[-1]['timestamp']==T
  v0=data[0]['ETH_book_unit_value']
  for p in data:p['normalized_ETH_book_wealth']=100*p['ETH_book_unit_value']/v0
  series[name]=data
 (dest/'comparable_ETH_wealth.json').write_text(json.dumps({'start_timestamp':start,'end_timestamp':T,'basis':'published book PPS or issuer conversion rate, ETH denominated; no external rewards, execution, market depeg or redemption costs','series':series},indent=2))
 hist=read('protocol_eth_history_monthly');obs=[x for x in read('protocol_eth_observations') if x['period']=='snapshot'];top=sorted(obs,key=lambda x:x['eth_family_reported_usd'],reverse=True)[:25];rows=[]
 for x in top:
  ps=sorted([h for h in hist if h['protocol']==x['protocol'] and h.get('eth_family_reported_usd') is not None],key=lambda h:h['target_timestamp'])
  a=ps[0] if ps else None;b=ps[-1] if ps else None
  rows.append({'protocol':x['protocol'],'name':x['name'],'first_available_period':a['period'] if a else None,'first_reported_USD':a['eth_family_reported_usd'] if a else None,'last_closed_period':b['period'] if b else None,'last_reported_USD':b['eth_family_reported_usd'] if b else None,'USD_change_percent':100*(b['eth_family_reported_usd']/a['eth_family_reported_usd']-1) if a and a['eth_family_reported_usd'] else None,'nonmissing_months':len(ps),'first_native_ETH_units':(a.get('tokens_units') or {}).get('ETH') if a else None,'last_native_ETH_units':(b.get('tokens_units') or {}).get('ETH') if b else None,'not_net_inflows':True,'source':x['source_url']})
 (dest/'protocol_trend_screen.json').write_text(json.dumps(rows,indent=2))
 lines=['# История рынка и дохода ETH','', 'Окно wealth: 2 октября 2024, 23:59:59 UTC — T. 24 закрытых месячных среза охватывают октябрь 2024–сентябрь 2026. Исторические observations описывают опубликованные balances и PPS; они не являются полной реконструкцией всех существовавших продуктов.','', '## Сопоставимый результат инвестора в ETH','', '![Рост опубликованной ETH book стоимости](figures/eth-wealth.png)','', 'Начальная стоимость каждой позиции — 100 ETH-equivalent units. Цена ETH/USD не влияет на график. Fluid уже denominated в rebasing stETH; дополнительное умножение на wstETH rate дало бы double count. Treehouse IAU конвертирован через исторически проверенный wstETH underlying; CIAN rsETH — через проверенный issuer oracle. Результат не включает отдельно выплаченные rewards, slippage, withdrawal fee, depeg и private distributions.','', '| Продукт | 730 дней, % | Первый год, % | Последний год, % | Annualized 730 дней, % |','|---|---:|---:|---:|---:|']
 for name,data in series.items():
  p={r['timestamp']:r['ETH_book_unit_value'] for r in data};r2=p[T]/p[start];r1=p[T-365*86400]/p[start];r3=p[T]/p[T-365*86400]
  lines.append(f'| {name} | {(r2-1)*100:.4f} | {(r1-1)*100:.4f} | {(r3-1)*100:.4f} | {(r2**.5-1)*100:.4f} |')
 lines += ['', 'Рейтинг меняется между первым и вторым годом. Прирост токенов на долю и доход в ETH — разные величины; negative receipt return способен сосуществовать с positive ETH conversion return. Сравнение PPS говорит о результате учёта, но не объясняет его причину. Для attribution нужны позиции, fees и внешние выплаты во времени.','', '## История 25 крупнейших наблюдаемых протоколов','', 'Ниже ETH-family USD observations по API, без суммирования строк. Первая доступная точка внутри окна не всегда равна октябрю 2024. Дата начала истории способна отражать launch/migration/adapter change; missing не означает ноль. USD-изменение смешивает цену ETH, flow и methodology. Поле ETH units показано только для прямого токена ETH и не отражает всех receipts.','', '| Протокол | Первая точка | USD млн | Сентябрь 2026, USD млн | Изменение USD, % | Месяцев с данными / 24 |','|---|---|---:|---:|---:|---:|']
 for r in rows:
  fmt=lambda x:'нет данных' if x is None else f'{x:.2f}'
  lines.append(f"| {r['name']} | {r['first_available_period']} | {fmt(r['first_reported_USD']/1e6 if r['first_reported_USD'] is not None else None)} | {fmt(r['last_reported_USD']/1e6 if r['last_reported_USD'] is not None else None)} | {fmt(r['USD_change_percent'])} | {r['nonmissing_months']} |")
 lines += ['', 'Полные исходные 2 088 protocol-month rows сохранены в `data/eth/protocol_eth_history_monthly.json`; 247 строк не имеют token observation. Universe выбран по current discovery, поэтому closed/dead products могут быть недопредставлены. Это survivorship limitation, а не доказательство отсутствия таких продуктов.','', '## Изменения конструкции рынка','', 'Liquid ETH имеет 719 Accountant events, включая 653 updates курса и 66 parameter events. Fees менялись внутри исторического окна, поэтому current 35 bps нельзя распространить на все два года. Собственные Optimism rates восстановлены отдельно: в прошлом они отличались от Ethereum.','', 'К 3 октября Pendle discovery показывает 122 expired ETH-family markets из 126. Для market history должны сохраняться maturity cohorts и redemption claims; удаление expired markets создало бы ложное обрушение fixed-yield сегмента.','', 'В апреле 2026 rsETH пережил bridge incident; с июня часть remote networks переведена на recovery process. Исторический issuer oracle не доказывает, что держатель на каждой сети мог реализовать ту же цену в тот же момент. Подробнее: [staking/restaking](dossiers/staking-restaking.md).','', 'Протокольные источники указаны в каждой строке semantic JSON. Прямые contracts, archive blocks и hash manifest описаны в [AUDIT.md](AUDIT.md).']
 (ROOT/'research/eth/HISTORY.md').write_text('\n'.join(lines)+'\n')
 print('Comparable series',[(n,len(s),s[-1]['normalized_ETH_book_wealth']) for n,s in series.items()])

if __name__=='__main__':run()
