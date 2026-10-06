"""Financial invariants for the newly reconstructed routes and archived stake."""
import hashlib,json,math,re
from pathlib import Path
from decimal import Decimal as Q
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'data/eth'
def run():
 f=json.loads((D/'finalization_reconstruction.json').read_text());c=json.loads((D/'report_contract.json').read_text());pc=json.loads((D/'reader_product_chapters.json').read_text());checks=[]
 def ck(name,ok):checks.append({'name':name,'passed':bool(ok)})
 ck('new_top_five_order',[p['id']for p in pc['products'][:5]]==['concrete','liquid','lido-earn','avant','yieldbasis'])
 ck('all_material_routes_in_census',len(c['census'])==13 and c['headline']['currentRoutes']==10)
 reader=(ROOT/'eth/index.html').read_text();template=(ROOT/'tools/eth/site/index.html').read_text()
 ck('history_description_matches_census',all('Thirteen whole-product books' in s and 'All 13 products' in s and 'Eight whole-product books' not in s for s in [reader,template]))
 ck('sample_concentration_conserves_books',math.isclose(c['sampleTopTwoShare'],sum(p['bookETH']for p in c['census'][:2])/sum(p['bookETH']for p in c['census'])))
 ck('no_nested_strATEGY_double_count',not any(r['name']=='stRATEGY'for r in c['census']))
 for p in f['newProducts']:
  ck('full_month_grid:'+p['id'],len(p['history'])==24 and p['history'][0]['month']=='2024-10'and p['history'][-1]['month']=='2026-09')
  ck('same_return_window:'+p['id'],p['window']['startDate']=='2026-09-02T23:59:59Z'and p['window']['date']==c['snapshot'])
  ck('claim_return_recomputed:'+p['id'],math.isclose(p['window']['cumulativeReturnPct'],100*(p['window']['endBookPrice']/p['window']['startBookPrice']-1),abs_tol=1e-10))
  ck('no_inferred_carry_weights:'+p['id'],all(r['carryAllocationPercent']is None for r in p['history']))
 for r in f['flowAdjustedLedgers']:
  ck('debt_flow_conservation:'+r['id'],math.isclose(r['accruedFundingCost'],r['closingDebt']-r['openingDebt']-r['newBorrowing']+r['repayments'],abs_tol=1e-8))
  ck('claim_flow_conservation:'+r['id'],math.isclose(r['investmentSharePriceIncome'],r['closingInvestmentClaim']-r['openingInvestmentClaim']-r['netInvestmentAcquisitionMark'],abs_tol=1e-8))
 lido=f['flowAdjustedLedgers'][0];ck('allocated_unclaimed_claim_not_new_deposit',lido['openingAllocatedUnclaimedShares']>9.85e6 and lido['mintedSharesInMonth']>lido['newEconomicShares']*3)
 ck('cash_return_to_parent_identified',lido['cashTransferredToParentUSDT']==13304800)
 lot=f['directFinancedLot'];ck('loan_investment_same_principal',lot['borrowed']==lot['recognisedAcquisitionValue']==5000000 and lot['start']=='2026-09-29T05:59:35Z')
 ck('direct_lot_result_recomputed',math.isclose(lot['resultBeforeGas'],lot['income']-lot['fundingCost'])and 1400<lot['resultBeforeGas']<1401)
 ck('all_log_queries_complete',all(isinstance(r['response'].get('result'),list)for r in json.loads((D/'finalization_carry_month_complete.json').read_text())['records']))
 ck('lido_debt_currencies_distinguished',{r['debtAsset']for r in f['loanLegs']['lido-earn']}=={'WETH','USDT','USDC'})
 ck('makina_USDT_not_ETH_loop',any(r['debtAsset']=='USDT'and 384700<r['debtUnits']<384702 for r in f['loanLegs']['makina-deth']))
 ck('avant_multi_currency_credit',{r['debtAsset']for r in f['loanLegs']['avant']}=={'USDC','USDS','PYUSD'})
 ck('PT_identity_and_native_ETH_unit',len(f['fixedMaturity'])==4 and {r['accountingUnit']for r in f['fixedMaturity']}=={'WETH','stETH','native ETH'})
 ck('residual_options_not_active_capacity',f['options']['ribbonResidualBookETH']>712 and f['options']['currentOptionExpiry']=='2025-12-12T08:00:00Z'and not f['options']['ongoingPremiumActivityProven']and f['options']['thetanutsFullCapacity']is None)
 for id,h in f['topFiveHolderReconstruction'].items():
  ck('all_transfer_supply_reconciliation:'+id,int(h['issuedSupplyRaw'])==sum(int(v)for v in h['positiveBalancesRaw'].values())and h['count']==len(h['positiveBalancesRaw']))
  prefix='lidoEarn'if id=='lido-earn'else'avETH'
  archived=json.loads((D/'finalization_holder_balances_T.json').read_text())['records']
  found={r['label'].removeprefix(prefix+'_holderBalance_'):r for r in archived if r['label'].startswith(prefix+'_holderBalance_')}
  ck('all_positive_holder_archive_balances:'+id,all(a in found and found[a]['response'].get('result')is not None and int(found[a]['response']['result'],16)==int(v)for a,v in h['positiveBalancesRaw'].items()))
 n=f['native'];raw=(ROOT/n['source']['path']).read_bytes();ck('full_native_receipt_hash',hashlib.sha256(raw).hexdigest()==n['source']['sha256'])
 # Independent field aggregation: distinguish actual balance from effective balance.
 actual=sum(int(m[1])for m in re.finditer(rb'"balance":"(\d+)"',raw));effective=sum(int(m[1])for m in re.finditer(rb'"effective_balance":"(\d+)"',raw));count=raw.count(b'"index":')
 ck('all_validator_actual_balances',actual==int(n['activeBalanceGwei'])and count==n['activeValidatorCount'])
 ck('all_validator_effective_balances',effective==int(n['activeEffectiveBalanceGwei'])and actual!=count*32*10**9)
 ck('native_not_receipt_claim_total',c['headline']['nativeActiveETH']>43e6 and c['headline']['receiptClaimsETH']<21e6 and c['globalUniqueETH']is None)
 ck('pruned_native_months_not_fabricated',sum(r['status']=='observed'for r in f['nativeHistory'])==5 and all('activeBalanceGwei'not in r for r in f['nativeHistory']if r['status']!='observed'))
 for name,sha in f['sourceFileHashes'].items():ck('frozen_source:'+name,hashlib.sha256((D/name).read_bytes()).hexdigest()==sha)
 out={'financialSnapshot':c['snapshot'],'checks':checks,'allPassed':all(r['passed']for r in checks),'scope':'Archived native-state aggregation, product ordering, monthly grids, distinct debt currencies, PT units and flow-adjusted financed claims. No claim of complete private-wallet coverage or executable cash NAV.'}
 (D/'finalization_verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'checks':len(checks),'allPassed':out['allPassed'],'failed':[r['name']for r in checks if not r['passed']]}));assert out['allPassed']
if __name__=='__main__':run()
