"""Flow-adjusted dollar claims and liability costs from archived events.
Amounts are claim accounting, not complete wallet P&L or executable exit cash.
"""
import csv
from decimal import Decimal as Q
from finalization_reconstruction_build import Evidence,D,read,save,words,date

def run():
 e=Evidence();rr=read('finalization_carry_month_complete')['records'];assert len(rr)==12 and all(isinstance(r['response'].get('result'),list)for r in rr)
 events=[]
 for r in rr:
  for l in r['response']['result']:
   events.append({'kind':r['label'].removesuffix('_month'),'block':int(l['blockNumber'],16),'logIndex':int(l['logIndex'],16),'tx':l['transactionHash'],'address':l['address'],'topics':l['topics'],'amountRaw':str(words(l['data'])[1]if'borrow'in r['label']else words(l['data'])[0]),'useATokens':bool(words(l['data'])[1])if'repay'in r['label']else None})
 bykind={r['label'].removesuffix('_month'):r['response']['result']for r in rr}
 def amount(l,kind):return Q(words(l['data'])[1]if'borrow'in kind else words(l['data'])[0])
 accounts={'lido':'181cb55f872450d16ae858d532b4e35e50eaa76d','vesper':'666c80feca6fcd371b0535a9846e2d223cbf1d10'}
 results=[]
 for id in accounts:
  a=accounts[id];scale=6 if id=='lido'else 18;borrow=repay=Q(0)
  for r in events:
   if any(z in r['kind']for z in ['borrow','repay'])and r['topics'][2].endswith(a):
    units=Q(r['amountRaw'])/10**scale
    if'borrow'in r['kind']:borrow+=units
    else:repay+=units
  if id=='lido':
   ds=sum(e.n('Lido'+v+'USDT_start_balanceOf(address)',6)for v in ['Aave','Spark']);de=sum(e.n('Lido'+v+'USDT_end_balanceOf(address)',6)for v in ['Aave','Spark'])
   s=e.n('earnUSDAllShares_25893051');end=e.n('earnUSDAllShares_26108081');p0=Q(10)**30/e.raw('earnUSD_report_30d_start')[0];p1=Q(10)**30/e.raw('earnUSD_report_snapshot')[0]
   last=26081188;delta=end-s;acquisitionPrice=Q(10)**30/e.raw('earnUSDMark_'+str(last))[0]
   flow=delta*acquisitionPrice;income=end*p1-s*p0-flow
   allStart=s;mintedStart=e.n('LidoEarnedUSD_30d_start');unclaimed=s-mintedStart
   extra={'openingAllocatedUnclaimedShares':float(unclaimed),'newEconomicShares':float(delta),'mintedSharesInMonth':float(sum(amount(l,'transfer')for l in bykind['EARNUSD_in'])/10**18),'ownershipConvention':'sharesOf includes allocated, unclaimed shares. Minting 9.855M previously allocated shares is not a new acquisition. The observed increase in total claims is valued at the archived oracle price in its allocation / claim transaction.','cashTransferredToParentUSDT':float(sum(Q(r['amountRaw'])/10**6 for r in events if r['kind']=='USDT_out'and r['topics'][2].endswith('277c6a642564a91ff78b008022d65683cee5ccc5')))}
  else:
   ds=e.n('vesper_DAI_debt_30d_start');de=e.n('vesper_DAI_debt_snapshot');s=e.n('vesper_vDAI_shares_30d_start');end=e.n('vesper_vDAI_shares_snapshot');p0=e.n('vesper_vDAI_30d_start');p1=e.n('vesper_vDAI_snapshot');flow=Q(0);netshares=Q(0)
   for kind in ['vDAI_in','vDAI_out']:
    for l in bykind[kind]:
     signed=amount(l,kind)/10**18*(1 if kind.endswith('_in')else-1);netshares+=signed;flow+=signed*e.n('vDAIMark_'+str(int(l['blockNumber'],16)))
   assert abs(end-s-netshares)<Q('0.000000001'),('Vesper receipt reconciliation',end-s,netshares)
   income=end*p1-s*p0-flow;extra={'receiptReconciliationResidualShares':float(end-s-netshares),'ownershipConvention':'All mint and burn transfers reconcile opening and closing vDAI shares. Each transfer is valued at its archived DAI-per-share price. Reinvested reward acquisitions are flows, not organic share-price income.'}
  interest=de-ds-borrow+repay;assert interest>=0
  results.append({'id':id,'currency':'USDT'if id=='lido'else'DAI','start':'2026-09-02T23:59:59Z','end':'2026-10-02T23:59:59Z','openingDebt':float(ds),'closingDebt':float(de),'newBorrowing':float(borrow),'repayments':float(repay),'accruedFundingCost':float(interest),'openingInvestmentClaim':float(s*p0),'closingInvestmentClaim':float(end*p1),'netInvestmentAcquisitionMark':float(flow),'investmentSharePriceIncome':float(income),'claimIncomeLessFullAccountInterest':float(income-interest),'scope':'Flow-adjusted recognised investment price growth versus full account debt interest. Different equity and loan principals are explicit; this is not organic carry-only, whole-wallet or investor cash profit. External rewards, cash transfers, gas and exit costs are separate.',**extra})
 # A new loan and acquisition match directly in one transaction; no repayment follows.
 b=26081188;price=Q(10)**30/e.raw('earnUSDMark_'+str(b))[0];endPrice=Q(10)**30/e.raw('earnUSD_report_snapshot')[0];shares=e.n('earnUSDAllShares_26108081')-e.n('earnUSDAllShares_25893051');principal=Q(5000000)
 claimIncome=shares*endPrice-principal;indices=[e.n('LidoAaveUSDTindex_'+str(n),27)for n in [b,26108081]];cost=principal*(indices[1]/indices[0]-1)
 timestamp=int(next(r['response']['result']['timestamp']for r in read('finalization_ledger_marks')['records']if r['label']=='ledgerBlock_'+str(b)),16)
 matched={'id':'lido-direct-usdt','currency':'USDT','borrowed':5000000,'acquiredEconomicShares':float(shares),'recognisedAcquisitionValue':float(shares*price),'start':date(timestamp),'end':'2026-10-02T23:59:59Z','income':float(claimIncome),'fundingCost':float(cost),'resultBeforeGas':float(claimIncome-cost),'receipt':'https://etherscan.io/tx/0x48c24a9436a519bd778454ff6946404afa79f943afc1952e36c08d69949adbc1','scope':'The 5M USDT Aave borrowing and transfer to the earnUSD deposit queue occur in the same transaction. Newly allocated economic shares exclude the separately minted old 9.855M claim. Funding uses the archived normalised debt index; no subsequent account repayment appears before T. Value is a recognised claim, not redemption cash; external rewards, gas and outer fees excluded.'}
 out={'events':events,'flowAdjustedLedgers':results,'directFinancedLot':matched,'formulas':{'interest':'closing accrued debt - opening accrued debt - new principal borrowed + principal/interest repaid','claimIncome':'closing investment claim - opening investment claim - signed acquisitions valued at event share price','directLot':'ending value of newly acquired economic shares - 5M transferred USDT - allocated debt-index interest'},'sourceFiles':['finalization_carry_month_complete.json','finalization_ledger_marks.json','finalization_allocation_shares.json','finalization_matched_liabilities.json','finalization_loan_index.json']};save('finalization_financial_ledgers',out)
 with (D/'carry-flow-adjusted-ledgers.csv').open('w',newline='')as f:
  w=csv.writer(f);w.writerow(['case','currency','opening_debt','closing_debt','new_borrowing','repayments','investment_price_income','full_account_interest','difference','scope'])
  for r in results:w.writerow([r['id'],r['currency'],r['openingDebt'],r['closingDebt'],r['newBorrowing'],r['repayments'],r['investmentSharePriceIncome'],r['accruedFundingCost'],r['claimIncomeLessFullAccountInterest'],r['scope']])
 return out
if __name__=='__main__':
 out=run();print(out['flowAdjustedLedgers']);print(out['directFinancedLot'])
