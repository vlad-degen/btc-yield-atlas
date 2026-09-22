from rpc import k256
EV={
 'AccrueInterest':'AccrueInterest(bytes32,uint256,uint256,uint256)',
 'Supply':'Supply(bytes32,address,address,uint256,uint256)',
 'Withdraw':'Withdraw(bytes32,address,address,address,uint256,uint256)',
 'Borrow':'Borrow(bytes32,address,address,address,uint256,uint256)',
 'Repay':'Repay(bytes32,address,address,uint256,uint256)',
 'SupplyCollateral':'SupplyCollateral(bytes32,address,address,uint256)',
 'WithdrawCollateral':'WithdrawCollateral(bytes32,address,address,address,uint256)',
 'Liquidate':'Liquidate(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)',
 'CreateMarket':'CreateMarket(bytes32,(address,address,address,address,uint256))',
 'SetFee':'SetFee(bytes32,uint256)',
 'FlashLoan':'FlashLoan(address,address,uint256)',
}
T={('0x'+k256(v.encode()).hex()):k for k,v in EV.items()}
def words(d):
    d=d[2:]; return [int(d[i:i+64],16) for i in range(0,len(d),64)]
def addr(t): return '0x'+t[-40:]
def decode(l):
    n=T.get(l['topics'][0],'?'); w=words(l['data']); tp=l['topics']
    b=int(l['blockNumber'],16); ts=int(l['timeStamp'],16)
    d={'ev':n,'block':b,'ts':ts,'tx':l['transactionHash']}
    if n=='AccrueInterest': d.update(prevBorrowRate=w[0],interest=w[1],feeShares=w[2])
    elif n=='Supply': d.update(caller=addr(tp[2]),onBehalf=addr(tp[3]),assets=w[0],shares=w[1])
    elif n=='Withdraw': d.update(caller=addr('0x'+hex(w[0])[2:].rjust(40,'0')),onBehalf=addr(tp[2]),receiver=addr(tp[3]),assets=w[1],shares=w[2])
    elif n=='Borrow': d.update(caller=addr('0x'+hex(w[0])[2:].rjust(40,'0')),onBehalf=addr(tp[2]),receiver=addr(tp[3]),assets=w[1],shares=w[2])
    elif n=='Repay': d.update(caller=addr(tp[2]),onBehalf=addr(tp[3]),assets=w[0],shares=w[1])
    elif n=='SupplyCollateral': d.update(caller=addr(tp[2]),onBehalf=addr(tp[3]),assets=w[0])
    elif n=='WithdrawCollateral': d.update(caller=addr('0x'+hex(w[0])[2:].rjust(40,'0')),onBehalf=addr(tp[2]),receiver=addr(tp[3]),assets=w[1])
    elif n=='Liquidate': d.update(caller=addr(tp[2]),borrower=addr(tp[3]),repaidAssets=w[0],repaidShares=w[1],seizedAssets=w[2],badDebtAssets=w[3],badDebtShares=w[4])
    elif n=='SetFee': d.update(fee=w[0])
    return d
