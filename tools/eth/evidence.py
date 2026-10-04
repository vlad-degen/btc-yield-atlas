"""Claim ledger with semantic input hashes and raw source provenance."""
import hashlib,json
from collect import ROOT,RAW,T

def run():
 rows=[json.loads(s) for s in (RAW/'requests.jsonl').read_text().splitlines()];latest={}
 for r in rows:
  if r.get('path'):latest[r['key']]=r
 specs=[
 ('C01','5 688 ETH-family pools / 57 chains / 197 feed projects','current screen, не net total','aggregator discovery',['discovery_summary','chain_screen'],['yield_pools','protocols']),
 ('C02','82 protocol sources с token history; 24 месяца и 247 missing rows','dated API observations','aggregator accounting',['protocol_source_coverage','protocol_eth_history_monthly'],['protocol_']),
 ('C03','Liquid ETH book NAV 177 171,063302 ETH','T, book value','fixed-block supply/PPS',['etherfi_verified_metrics','pilot_ethereum_rpc','pilot_optimism_rpc'],['pilot_ethereum_T','pilot_optimism_T']),
 ('C04','Частичный баланс $460,231 млн; residual $12,453 млн','T, marks + nested book claims, backing не audited','derived reconstruction',['etherfi_partial_balance_sheet'],['pilot_details_T','balances_','fluid_','mono_accountant_T']),
 ('C05','Loop Aave 13,325× и HF 1,02708','T oracle-valued account','fixed-block account getter',['etherfi_verified_metrics','stress_scenarios'],['pilot_ethereum_T']),
 ('C06','Carry 64,66% и loops 21,65% в опубликованном breakdown','3 октября UI, не fixed-block allocation','manual public UI',['etherfi_verified_metrics'],[]),
 ('C07','Liquid ETH +6,8501% / stETH +5,4875% за 730 дней','Published PPS/conversion; external rewards и costs excluded','archive RPC and rate logs',['etherfi_staking_comparison','etherfi_history_points'],['benchmark_history_','accountant_logs_','rate_logs_']),
 ('C08','senRLUSD: kBTC 52,89%, weETH 24,09% book allocation','T, expected assets and raw supply shares','fixed-block allocator/markets',['carry_credit_lookthrough','carry_collateral_assets_T'],['carry_market','carry_asset']),
 ('C09','PRIME/PYUSD около 95,04% carry vault assets','T, credit economics via separate disclosure','fixed-block claim + primary disclosure',['carry_credit_lookthrough'],['carry_market','sentora_prime_case']),
 ('C10','Self-credit notional 8,709m RLUSD и 4,759m PYUSD','economic overlap, не added asset или measured income','derived shares/debt',['carry_credit_lookthrough'],['carry_market']),
 ('C11','Concrete vaults имеют общий 3-of-5 Safe','T; exclusive backing allocation неизвестна','fixed-block getters',['concrete_lookthrough_T'],['concrete_strategies_T','concrete_wallet_accounts_T','concrete_multisig_strategy_abi']),
 ('C12','Concrete Delta supply целиком у sole holder; ctwst supply у Safe','T; genesis mint не доказывает отсутствия backing','fixed-block balances / event trace',['concrete_self_holdings_T','segment_checks_T'],['concrete_self','segment_checks','concrete_logs_','concrete_holders_']),
 ('C13','Fluid Lite L=7,759×; 730-day ETH book return +8,8243%','T contract valuation; parity assumptions','fixed-block view + archive RPC',['fluid_lite_balance_T','vault_history_comparison'],['segment_checks','vault_history']),
 ('C14','Treehouse IAU исторически wstETH-denominated; ETH return +6,2761%','730 дней; independent backing не reconstructed','archive identity/conversion',['treehouse_denomination_history','vault_history_comparison'],['treehouse_denomination','vault_history']),
 ('C15','CIAN rsETH ETH book return +1,0854% за 730 дней','issuer oracle conversion; rewards/recovery costs excluded','archive identity/conversion',['rseth_benchmark_rpc','vault_history_comparison'],['rseth_benchmark','vault_history']),
 ('C16','JustLend mapped ETH около 484k units, APY 0,0002899%','current 3 октября; Ethereum backing не verified','primary public API',['justlend_eth_semantics'],['justlend']),
 ('C17','Ethena ETH basis legs около $374,44m','3 октября rounded UI disclosure; no custodial audit','manual public UI',['ethena_ETH_basis_observation'],[]),
 ('C18','Pendle 626 listed / 126 ETH-family / 122 expired','four-chain current API; expiry evaluated against T','primary public API',['pendle_source_coverage','pendle_eth_market_screen'],['pendle_markets']),
 ('C19','Nested Monad claim около $21,687m; rates ETH/Monad различаются','T; remote backing open','fixed-block getters',['mono_identity_T','mono_accountant_T','mono_remote_T'],['mono_identity','mono_hook','mono_accountant','mono_remote']),
 ('C20','Main Aave debt 410134 WETH; reserve cash 269693 WETH','T, reserve cash не guarantee flashloan eligibility','fixed-block token balances',['lending_reserve_T','loop_economics_T'],['lending_reserve','lending_cash','balances_ethereum']),
 ('C21','Model zero-return borrow uplift Aave 44,3bp','mixed trailing-30d staking proxy / T APR; no forecast','model sensitivity',['loop_economics_T'],['lending_reserve']),
 ('C22','Unique underlying и external equity market totals остаются null','overlap / consensus / custody / identity gaps','research limitation',['market_summary','dependency_graph'],[]),
 ('C23','Пять выбранных WETH markets: 2,881m lender claims / 2,388m debt','T; gross lending claims, не unique underlying','fixed-block reserve/token state',['weth_lending_markets_T','weth_lending_summary_T'],['weth_market','aave_addressbook']),
 ('C24','Aave WETH reserve deficit: ETH 52964 / Arbitrum 29835 WETH','T contract getter; не established final investor haircut','fixed-block deficit getter + primary mechanics',['weth_lending_markets_T'],['weth_market_deficit','aave_deficit_feature_doc','aave_pool_source']),
 ('C25','Liquid ETH main account: 23,28% variable WETH debt Aave ETH','T; selected borrower concentration','fixed-block debt-token ratios',['weth_lending_summary_T'],['weth_market_balances','balances_ethereum']),
 ]
 claims=[]
 for cid,claim,scope,kind,files,prefixes in specs:
  inputs=[]
  for n in files:
   p=ROOT/'data/eth'/f'{n}.json';inputs.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  rs=[{'key':r['key'],'url':r['url'],'path':r['path'],'sha256':r['sha256'],'retrieved_at':r['retrieved_at']} for k,r in latest.items() if any(k.startswith(pr) for pr in prefixes)]
  manual=['raw/eth/2026-10-02/etherfi_ui_observation.json'] if cid=='C06' else ['raw/eth/2026-10-02/ethena_ui_observation.json'] if cid=='C17' else []
  claims.append({'id':cid,'claim':claim,'time_scope_and_limit':scope,'evidence_type':kind,'semantic_inputs':inputs,'source_responses':rs,'manual_UI_files':manual,'market_net_total_proof':False})
 (ROOT/'data/eth/evidence_ledger.json').write_text(json.dumps({'target_timestamp':T,'claims':claims},indent=2,ensure_ascii=False))
 lines=['# Evidence ledger: что именно подтверждает каждый вывод','', 'Это claim ledger исследовательского выпуска. Confidence относится к конкретной части вывода: fixed-block state может быть надёжен, тогда как independent backing и cash realization той же позиции неизвестны. Hashes semantic inputs и raw source responses сохранены в `data/eth/evidence_ledger.json`. Manual public UI observations отмечены отдельно.','', '| ID | Проверенный результат / исследовательское ограничение | Время и предел вывода | Основной data artifact |','|---|---|---|---|']
 for c in claims:
  p=c['semantic_inputs'][0]['path'];lines.append(f"| {c['id']} | {c['claim']} | {c['time_scope_and_limit']} | [{p.split('/')[-1]}](../../{p}) |")
 lines+=['','## Первичные связи и воспроизводимость','', 'Claim ledger не превращает secondary adapters в первичное доказательство reserves. Для RPC claims полные request payloads содержат block tags, addresses, selectors и результаты; verified source/ABI и identity getters привязаны к relevant contracts. [AUDIT.md](AUDIT.md) описывает уровни источников.','', 'Цена доли, размер кредита, cash balance, oracle mark и исполненная выплата — разные факты. Row C22 преднамеренно оставляет неизвестные totals открытыми. Если появятся данные, противоречащие книгам или disclosures, нужно сохранить обе vintage и объяснить reconciliation. Ошибки источников не заменяются нулём.']
 (ROOT/'research/eth/EVIDENCE.md').write_text('\n'.join(lines)+'\n');print('Claims',len(claims))

if __name__=='__main__':run()
