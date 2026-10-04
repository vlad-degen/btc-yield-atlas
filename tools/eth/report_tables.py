"""Generate dated, explicitly non-additive tables from the semantic dataset."""
import json,datetime as dt
from collect import ROOT,T
from package_metrics import read
def fmt(n):return f'{n:,.3f}'.replace(',',' ')
def build():
 s=read('market_summary');obs=[r for r in read('protocol_eth_observations') if r['period']=='snapshot'];obs.sort(key=lambda r:r['eth_family_reported_usd'],reverse=True)
 text=['# Таблицы охвата рынка ETH yield','',f'Дата: 3 октября 2026. T: {dt.datetime.fromtimestamp(T,dt.timezone.utc).isoformat()}.','',
 'Таблица сетей — current discovery feed после T. Это сумма полных TVL выбранных пулов, включая не-ETH стороны mixed pools, повторные LST deposits и leverage. Она не является ни net market capital, ни доказанной верхней/нижней границей unique ETH.','',
 '| Сеть | Пулы-кандидаты | Full-pool TVL, $млн | Пулы ≥$5млн | Углублённый отбор |','|---|---:|---:|---:|---|']
 for c in s['chain_screen']:text.append(f"| {c['chain']} | {c['pools']} | {fmt(c['reported_full_pool_tvl_usd']/1e6)} | {c['above_5m_pools']} | {'да' if c['deep_candidate'] else 'screen'} |")
 text+=['','## Датированные наблюдения по протоколам','',
 'Последняя доступная token observation не позднее T. В таблице только выбранная ETH-family часть adapter accounting. Она не равна всему protocol TVL, external investor equity или уникальному underlying. Строки с отрицательными balances сохраняют знак. Неизвестные обёртки остаются ограничением охвата. Текущая category — подсказка для классификации, не доказательство исторической стратегии.','',
 '| Протокол | ETH-family, $млн | Категория источника сейчас | Дата token observation UTC | Возраст на T, часов |','|---|---:|---|---|---:|']
 for r in obs:
  date=dt.datetime.fromtimestamp(r['source_timestamp'],dt.timezone.utc).strftime('%Y-%m-%d %H:%M');text.append(f"| [{r['name']}]({r['source_url']}) | {fmt(r['eth_family_reported_usd']/1e6)} | {r['category_current_hint']} | {date} | {r['source_age_seconds']/3600:.2f} |")
 text+=['','## Сопоставимый результат в ETH по цене доли','',
 'Окна до T: 365 и 730 дней. Доход по published PPS/contract conversion, без внешних rewards, комиссии выхода и market depeg. Это не доказательство реализуемого cash payout.','',
 '| Продукт или benchmark | 365 дней | 730 дней | Годовой эквивалент 730 дней |','|---|---:|---:|---:|']
 b={r['days']:r for r in read('etherfi_staking_comparison')}
 for name,key in [('Liquid ETH','liquidETH'),('stETH/wstETH benchmark','stETH'),('weETH benchmark','weETH')]:
  r1=b[365][key+'_cumulative_return'];r2=b[730][key+'_cumulative_return'];text.append(f'| {name} | {r1*100:.4f}% | {r2*100:.4f}% | {((1+r2)**.5-1)*100:.4f}% |')
 vh=read('vault_history_comparison')
 for name in ['Fluid Lite ETH','Treehouse tETH','CIAN rsETH']:
  r1=next(r for r in vh if r['product']==name and r['days']==365);r2=next(r for r in vh if r['product']==name and r['days']==730);assert r1['ETH_return_confirmed'] and r2['ETH_return_confirmed'];text.append(f"| {name} | {r1['ETH_pps_cumulative_return']*100:.4f}% | {r2['ETH_pps_cumulative_return']*100:.4f}% | {r2['ETH_pps_annualized_apy']*100:.4f}% |")
 text+=['','Treehouse: исторически подтверждена wstETH denomination внутренней IAU; она не является физическим запасом wstETH. CIAN: rsETH conversion использует исторически проверенный oracle и не включает рыночный bridge/depeg loss. Concrete не получает нулевой APR из плоского PPS: private distributions и более короткая история остаются неизвестными.','',
 'Источники таблиц: `market_summary.json`, `chain_screen.json`, `protocol_eth_observations.json`, `etherfi_staking_comparison.json`, `vault_history_comparison.json`. Все пути данных относительно `data/eth/`.']
 (ROOT/'research/eth/MARKET-TABLES.md').write_text('\n'.join(text)+'\n')
 print('Generated chain table',len(s['chain_screen']),'protocol observations',len(obs))
if __name__=='__main__':build()
