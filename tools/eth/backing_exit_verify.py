"""Offline verification of the bounded backing/exit captures and derived ledger.

Run after the builder: python3 tools/eth/backing_exit_verify.py
No network calls, signing or transactions. No output files are changed.
"""
import hashlib,json,math,pathlib,sys
from backing_exit_build import ROOT,RAW,read,records,result,number,logs,topic,words,log_order

def main():
    checks=[]
    def check(name,ok):
        checks.append({'check':name,'passed':bool(ok)})
        if not ok:raise AssertionError(name)
    def near(a,b):return math.isclose(a,b,rel_tol=1e-12,abs_tol=.000001)
    data=read(ROOT/'data/eth/backing_exit_closure.json')
    manifest=read(ROOT/'data/eth/backing_exit_manifest.json')
    for group in ['inputs','builders','outputs']:
        for x in manifest[group]:
            p=ROOT/x['path'];check('SHA256 '+x['path'],p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256'])
    ps={p['id']:p for p in data['products']}
    check('Exactly the five examined products',set(ps)=={'concrete','liquid','rocksolid','liquity','royco'})
    check('Frozen financial boundary',data['snapshot']['timestamp']==1790985599 and data['snapshot']['ethereumBlock']==26108081 and data['snapshot']['monadBlock']==110031481)
    frozen=read(RAW/'financial_inputs_frozen_T.json')
    for p in frozen['products']:
        q=ps[p['id']];b=q['backing']
        check(p['id']+' book NAV preserved',q['bookNAV_ETH']==p['bookNAV_ETH'] and q['bookNAV_USD']==p['bookNAV_USD'])
        check(p['id']+' reconstruction line sum',near(sum(x.get('USD',x.get('usd'))for x in b['lines']),b['reconstructedUSD']))
        check(p['id']+' book/reconstruction/residual equation',near(q['bookNAV_USD'],b['reconstructedUSD']+b['residualUSD']))
        for pct,row in zip([1,10,30],q['demandScenarios']):
            check(p['id']+f' {pct}% demand denominator',row['navPct']==pct and near(row['USD'],q['bookNAV_USD']*pct/100) and near(row['ETH'],q['bookNAV_ETH']*pct/100))
        hist=q['historicalExits']
        check(p['id']+' complete queried event intervals',hist['successfulIntervals']==hist['queriedIntervals'] and hist['toBlock']==26108081)
        check(p['id']+' every captured historical payout token-verified',hist['fulfilledCount']==hist['receiptVerifiedCount'])
        for path in b['sourcePaths']+hist['sourcePaths']+q['controlsClosure'].get('sourcePaths',[]):check('Source link '+path,(ROOT/path).is_file())
    h=ps['liquid']['historicalExits']
    check('Liquid requests reconcile to statuses',h['requestCount']==h['fulfilledCount']+h['cancelledCount']+h['pendingCount'] and not h['unmatchedRequestIds'])
    ll=logs('liquid_queue')
    solved={l['topics'][1]for l in ll if l['topics'][0]==topic('OnChainWithdrawSolved(bytes32,address,uint256)')}
    cancelled={l['topics'][1]for l in ll if l['topics'][0]==topic('OnChainWithdrawCancelled(bytes32,address,uint256)')}
    check('Liquid solved/cancelled request IDs are disjoint',not solved&cancelled and len(solved)==h['fulfilledCount'] and len(cancelled)==h['cancelledCount'])
    check('Liquid exact payout units',{x['unit']for x in h['totalPaidByAsset']}=={'eETH','weETH'} and number(records('remaining_known_claims_T'),'eETH_decimals',0)==18)
    lb=ps['liquid']['backing'];bounds=lb['unattributedBounds']
    check('Liquid nested claim replaces, not adds to, parent receipt',near(lb['nestedReceiptReplacementReconstructionUSD'],lb['reconstructedUSD']-bounds['nestedMonadBookUSD']+bounds['nestedMonadCapturedEthereumAndRemoteClaimsUSD']))
    for row in ps['liquid']['demandScenarios']:check('Liquid aggregate exit untested '+str(row['navPct']),row['response']is None and row['simulatedRequest']is None and row['simulationStatus']=='not tested as aggregate withdrawal')
    check('Steak getter/call disagreement retained',lb['nestedMonad']['SteakMaxWithdrawGetterWETH']==0 and 'result'in lb['nestedMonad']['oneWETHWithdrawalSimulation']['response'])
    for row in ps['concrete']['demandScenarios']:check('Concrete queue acceptance is not payout '+str(row['navPct']),row['simulatedRequest']is True and row['successfulWithdrawalSimulation']is False and 'result'in row['withdrawalCall']['response'])
    for row in ps['rocksolid']['demandScenarios']:
        check('Rocksolid separate request/withdraw responses '+str(row['navPct']),'error'in row['requestCall']['response'] and row['withdrawalCall']['response']['error']['data'].startswith('0x4e487b71'))
    rock=ps['rocksolid'];h=rock['historicalExits'];order=h['orderingInvariant']
    check('Rocksolid complete matched settlement-before-cash invariant',order['uniquelyMatchedCashClaims']==427 and order['settlementFound']==427 and order['settlementBeforeOrAtCash'] and not order['violations'])
    check('Rocksolid unpaired claim excluded from wait denominator',h['waitHours']['observations']+h['cashWaitUnpairedClaims']==h['fulfilledCount'])
    check('Rocksolid matched settlement waits no longer exceed cash waits',h['matchedCashRequestToSettlementHours']['median']<=h['waitHours']['median'])
    controls=rock['controlsClosure']
    check('Rocksolid T source/runtime binding',controls['exactMatchToVerifiedSourceDeployedBytecode'] and controls['snapshotState']=='Closing' and controls['stateEnumValue']==1 and controls['stateTransitionFunction']=='initiateClosing()')
    check('Liquity only 1% withdrawal simulation succeeds',[x['successfulWithdrawalSimulation']for x in ps['liquity']['demandScenarios']]==[True,False,False])
    rc=ps['royco']['controlsClosure']
    check('Royco T implementation/source bindings',rc['machineImplementationBinding']['exactMatchToVerifiedSourceDeployedBytecode'] and rc['caliberImplementationBinding']['exactMatchToVerifiedSourceDeployedBytecode'])
    check('Royco mapped role and scheduling enforcement',rc['durationChangeExecutionDelaySeconds']==259200 and rc['configuredInstructionRootDelaySeconds']==172800 and rc['unscheduledExecuteReverts'])
    check('Royco actual accounting loan venue binding',ps['royco']['liveLoan']['marketId']=='0xf5c5df23559b0fb56560a7578ea17d81e245153ba64b8132df026c9358864d27' and ps['royco']['liveLoan']['debt']=='PYUSD' and ps['royco']['cachedAccountingScope']['isAccountingFresh']is False)
    for row in ps['royco']['demandScenarios']:check('Royco snapshot withdrawal fails '+str(row['navPct']),'error'in row['withdrawalCall']['response'])
    article=ROOT/'research/eth/review/BACKING-EXIT-CLOSURE.md'
    check('English closure article exists without long dashes',article.is_file() and '\u2013'not in article.read_text() and '\u2014'not in article.read_text())
    print(json.dumps({'status':'passed','checks':len(checks),'rawCaptureFiles':sum(1 for x in RAW.rglob('*')if x.is_file()),'outputSHA256':hashlib.sha256((ROOT/'data/eth/backing_exit_closure.json').read_bytes()).hexdigest(),'manifestInputs':len(manifest['inputs']),'products':{p['id']:{'reconstructedUSD':p['backing']['reconstructedUSD'],'residualUSD':p['backing']['residualUSD'],'verifiedCashPayouts':p['historicalExits']['receiptVerifiedCount']}for p in data['products']}},indent=2))

if __name__=='__main__':main()
