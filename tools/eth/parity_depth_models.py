"""Offline cohort sensitivity, fee conversion and intermediary ownership at T.

Uses actual event quantities and archive getter results. FIFO/LIFO/pro-rata are
alternative accounting conventions, never claims about unique dollar provenance.
"""
import collections, csv, hashlib, json
from datetime import datetime, timezone
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 75
ROOT = Path(__file__).resolve().parents[2]
D = ROOT / 'data/eth'
def read(name): return json.loads((D / (name + '.json')).read_text())
def result(rows, label):
    r = next(r for r in rows if r['label'] == label)
    assert 'result' in r['response'], (label, r['response'])
    return int(r['response']['result'], 16)

def ownership():
    checks = read('parity_depth_holder_checks')['records']
    bindings = read('parity_depth_holder_bindings')['records']
    out = []
    for r in read('parity_depth_holder_transfers')['records']:
        key = r['label'].split('_')[0]; balances = collections.defaultdict(int)
        for e in sorted(r['response']['result'], key=lambda e:(int(e['blockNumber'],16),int(e['logIndex'],16))):
            a,b = ['0x'+t[-40:] for t in e['topics'][1:3]]; n=int(e['data'],16)
            if int(a,16): balances[a]-=n
            if int(b,16): balances[b]+=n
            assert min(balances.values()) >= 0
        live = {a:n for a,n in balances.items() if n}
        supply = result(bindings,key+'_totalSupply()')
        assert sum(live.values()) == supply
        for a,n in live.items(): assert result(checks,key+'_balance_'+a) == n
        assets = result(checks,key+'_totalAssets()')
        unit = result(checks,key+'_convertToAssets(uint256)')
        rows = [{'address':a,'sharesRaw':str(n),'sharePct':100*n/supply,
                 'proportionalUnderlyingClaim':float(Decimal(n)*assets/Decimal(supply)/10**18),
                 'url':'https://etherscan.io/address/'+a} for a,n in sorted(live.items(),key=lambda r:-r[1])]
        out.append({'key':key,'receipt':r['params'][0]['address'].lower(),'holderCount':len(live),
                    'supplyRaw':str(supply),'totalAssetsRaw':str(assets),'assetsPerShare':unit/10**18,
                    'underlying':'avETH' if key=='savETH' else 'YB WETH LT',
                    'allBalancesVerifiedAtT':True,'rows':rows,
                    'scope':'Receipt claims are proportional to totalAssets before individual redemption rounding; pending cooldown/silo claims and unvested rewards are separate. Addresses are not unique investors.'})
    owners = {r['label'].split('_',1)[1]:'0x'+r['response']['result'][-40:] for r in read('parity_depth_fees_owners')['records'] if r['label'].startswith('hybridOwner_')}
    # Cash deposits are account positions in a spoke, rather than ERC20 holders.
    events=read('parity_depth_op_beneficiary_events')['records']; replay=collections.defaultdict(int)
    for r in events[:2]:
        for e in r['response']['result']:
            a='0x'+e['topics'][3][-40:]; n=int(e['data'][2:66],16)
            replay[a]+=n if r['label']=='cash_Supply' else -n
    assert not read('parity_depth_op_liquidations')['records'][0]['response']['result']
    actual={}
    for batch in read('parity_depth_op_user_balances')['records']:
        wire=bytes.fromhex(batch['response']['result'][2:])
        def word(offset):return int.from_bytes(wire[offset:offset+32],'big')
        base=word(0); count=word(base); assert count==len(batch['addresses'])
        for i,a in enumerate(batch['addresses']):
            item=base+32+word(base+32+i*32); assert word(item)==1
            body=item+word(item+32); assert word(body)==32
            actual[a]=word(body+32); assert actual[a]==replay[a]
    supply=result(events,'spoke_getReserveSuppliedShares(uint256)')
    assert len(actual)==len(replay) and sum(actual.values())==supply and min(actual.values())>=0
    live=sorted(((a,n) for a,n in actual.items() if n),key=lambda r:-r[1])
    rate=read('etherfi_verified_metrics')['rate_eth_per_share']
    cash={'holderCount':len(live),'testedAccounts':len(actual),'allBalancesVerifiedAtT':True,
          'spoke':'0xdffcc3536d932eb51df51a7f5fa407c4270d5308','hub':'0x66753c4e3fc84f1ed0e3c267c927284e9d90c572',
          'hubLiquidSharesRaw':str(supply),'wholeBookSharePct':100*supply/10**18/(read('etherfi_verified_metrics')['ethereum_shares']+read('etherfi_verified_metrics')['optimism_shares']),
          'firstSupplyDate':datetime.fromtimestamp(int(events[0]['response']['result'][0]['blockTimestamp'],16),timezone.utc).isoformat(),
          'rows':[{'address':a,'sharesRaw':str(n),'shareOfHubPct':100*n/supply,'capitalETH':n/10**18*rate,'url':'https://optimistic.etherscan.io/address/'+a} for a,n in live],
          'scope':'One Hub balance represents 7,012 positive Cash account positions. All 7,351 event-discovered accounts were checked through getUserSuppliedShares at Optimism block 157693411; their sum equals spoke and Hub assets. No Liquid ETH collateral liquidation event is observed. Cash smart accounts can share owners; this is not a count of unique people.'}
    # Replace Morpho custody with actual historical collateral owners, and a
    # Gearbox credit account with the borrower returned by its CreditManager.
    senior=out[0]; morpho='0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb'
    direct={r['address']:int(r['sharesRaw']) for r in senior['rows']}; morphoRows=[]
    for r in read('parity_depth_sav_morpho_positions')['records']:
        wire=r['response']['result'];words=[int(wire[i:i+64],16) for i in range(2,len(wire),64)]
        _,_,mid,a=r['label'].split('_');n=words[2]
        if n:morphoRows.append({'marketId':mid,'address':a,'collateralSharesRaw':str(n)})
    assert sum(int(r['collateralSharesRaw']) for r in morphoRows)==direct[morpho]
    del direct[morpho]
    for r in morphoRows:direct[r['address']]=direct.get(r['address'],0)+int(r['collateralSharesRaw'])
    gearbox='0x6cc892a7ad2c72b8f0d49ce8660da928f7e6101b'
    borrower='0x'+read('parity_depth_sav_gearbox_owner')['records'][0]['response']['result'][-40:]
    direct[borrower]=direct.get(borrower,0)+direct.pop(gearbox)
    seniorSupply=int(senior['supplyRaw']);assert sum(direct.values())==seniorSupply
    seniorLook={'rows':[{'address':a,'sharesRaw':str(n),'sharePct':100*n/seniorSupply} for a,n in sorted(direct.items(),key=lambda r:-r[1])],
                'morphoPositions':morphoRows,'gearboxBorrower':borrower,'bridgeAddress':'0x43f47a434dadd5a122c42e49378365cca949fa54',
                'scope':'Named-owner look-through: replace two Morpho market custody balances with archive-verified collateral positions and the largest Gearbox account with its current borrower. The CCIP pool remains a bridge claim; remote wrapped holders and other private account ownership are not consolidated. No extra avETH is added.'}
    yb=read('yb_LT_holders_T');gau=out[1];gauge=gau['receipt'];directYB={r['address']:Decimal(str(r['shares'])) for r in yb['addresses']};gaugeHeld=directYB.pop(gauge)
    for r in gau['rows']:
        n=gaugeHeld*Decimal(r['sharesRaw'])/Decimal(gau['supplyRaw']);a=r['address'];directYB[a]=directYB.get(a,Decimal(0))+n
    for a,owner in owners.items():
        if a in directYB:directYB[owner]=directYB.get(owner,Decimal(0))+directYB.pop(a)
    ybSupply=Decimal(str(yb['totalShares']));assert abs(sum(directYB.values())-ybSupply)<Decimal('0.00000001')
    ybLook={'rows':[{'address':a,'underlyingLTShares':float(n),'sharePct':float(100*n/ybSupply)} for a,n in sorted(directYB.items(),key=lambda r:-r[1])],
            'scope':'Replace the gauge claim with its 155 verified receipt balances, then map four large personal HybridVaults to owner() at T. Other custody addresses remain separate. LT amounts use the original floating-point direct-holder ledger; aggregate rounding is below 0.00000001 LT. Addresses need not be independent investors.'}
    return {'receipts':out,'yieldBasisPersonalVaultOwners':owners,'liquidCash':cash,'savETHLookThrough':seniorLook,'yieldBasisLookThrough':ybLook}

def funding_history():
    sources=read('parity_depth_lending_events')['records']; grouped=collections.defaultdict(list)
    known={'0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2':('WETH',18),'0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48':('USDC',6),'0xdac17f958d2ee523a2206206994597c13d831ec7':('USDT',6),'0x6c3ea9036406852006290770bedfcaba0e23a0e8':('PYUSD',6)}
    for r in sources[:4]:
        venue,event=r['label'].split('_')
        for e in r['response']['result']:
            token='0x'+e['topics'][1][-40:];account='0x'+e['topics'][2][-40:];symbol,dec=known[token]
            w=[int(e['data'][i:i+64],16) for i in range(2,len(e['data']),64)]
            grouped[(venue,account,token)].append({'event':event,'date':datetime.fromtimestamp(int(e['blockTimestamp'],16),timezone.utc).isoformat(),
                'block':int(e['blockNumber'],16),'logIndex':int(e['logIndex'],16),'amount':w[1 if event=='Borrow' else 0]/10**dec,
                'symbol':symbol,'tx':e['transactionHash'],'url':'https://etherscan.io/tx/'+e['transactionHash']})
    legs=[]
    for (venue,account,token),events in grouped.items():
        events.sort(key=lambda e:(e['block'],e['logIndex']));borrows=[e for e in events if e['event']=='Borrow'];repays=[e for e in events if e['event']=='Repay']
        legs.append({'venue':venue,'account':account,'token':token,'symbol':known[token][0],'firstBorrow':borrows[0],
            'borrowCount':len(borrows),'repayCount':len(repays),'borrowedCash':sum(e['amount'] for e in borrows),'repaidCash':sum(e['amount'] for e in repays),
            'events':events,'scope':'Complete Borrow and Repay event query for four named controlled accounts. Cumulative cash turnover is not ending debt, TVL or income. Previously unknown, sold or other managed accounts are outside this ledger.'})
    monthly=[]
    for r in read('parity_depth_monthly_debt')['records']:
        wire=r['response']['result'];monthly.append({k:r[k] for k in ['venue','symbol','account','asset','month','timestamp','block']}|{'indexedDebt':int(wire,16)/10**r['decimals'] if wire!='0x' else None,
            'status':'observed' if wire!='0x' else 'debt token not deployed','debtToken':r['address']})
    state=read('carry_attribution_states')['records'];pilot=read('pilot_details_T');responses={r['id']:r for r in pilot['responses']}
    oracles={r['label'].removeprefix('morpho_oracle_'):int(responses[i+1]['result'],16) for i,r in enumerate(pilot['labels']) if r['label'].startswith('morpho_oracle_')}
    rates={r['id']:r['borrow_apr'] for r in read('carry_economics_chapter')['borrow_markets'] if r['venue']=='Morpho Blue'}
    prime='0x41c41d0c9aadbf4751f5ee215ed5a16954a4b34e1b70fca5393d4b08858fa3fa'
    rates[prime]=int(read('parity_depth_prime_rate')['records'][0]['response']['result'],16)/1e18*365*86400
    morpho=[]
    for loan in read('carry_attribution_ledger')['borrowing_ledgers']:
        mid=loan['market_id'];p=next(r['response']['result']for r in state if r['id']==mid and r['field']=='params');pos=next(r['response']['result']for r in state if r['id']==mid and r['field']=='position' and r['account']==loan['account'])
        threshold=int(p[2+4*64:2+5*64],16);collateral=int(pos[2+2*64:2+3*64],16)
        value=Decimal(collateral)*oracles[mid]/Decimal(10**36)/Decimal(10**loan['decimals'])
        debt=Decimal(str(loan['ending_accrued_debt_assets']))
        morpho.append({'marketId':mid,'account':loan['account'],'collateralValueLoanUnits':float(value),'liquidationThreshold':threshold/1e18,'healthFactor':float(value*threshold/Decimal(1e18)/debt)if debt else None,'borrowAPR_pct':rates[mid]*100 if mid in rates else None,'basis':'Archived collateral × bound oracle price × market LLTV / accrued debt, in native loan units. Quote APR is annualised borrowRateView, not a realised average cost.'})
    first=sources[-1]['response']['result'][0]
    return {'legs':sorted(legs,key=lambda r:r['firstBorrow']['date']),'monthlyDebt':monthly,
            'morphoAtT':morpho,
            'firstShareMint':{'date':datetime.fromtimestamp(int(first['blockTimestamp'],16),timezone.utc).isoformat(),'shares':int(first['data'],16)/10**18,'url':'https://etherscan.io/tx/'+first['transactionHash']},
            'scope':'Indexed account debt on current identified reserve debt tokens at verified month-end blocks. Earlier token absence remains null. This supplements the dated Morpho ledgers and does not reconstruct a complete historical asset allocation.'}

def cohort_models():
    ledger=read('carry_attribution_ledger'); tranche=read('carry_attribution_tranches')
    dest=next(d for d in ledger['destination_ledgers'] if d['id']=='pyusd-prime-v2')
    assert len(dest['accounts'])==1 and dest['accounts'][0]['outside_share_receipts']==dest['accounts'][0]['outside_share_sends']==0
    endingShares=Decimal(dest['accounts'][0]['ending_shares_raw']); endingAssets=Decimal(str(dest['ending_claim_assets']))
    loanRows=[r for r in tranche['debt_cohorts'] if r['loan_symbol']=='PYUSD' and r['destination_deposits']]
    matched={}
    for loan in loanRows:
        for d in loan['destination_deposits']:
            if d['destination_id']==dest['id'] and d['same_native_asset_as_loan']:
                matched[(loan['transaction_hash'],d['deposit_shares_raw'])]=loan
    scenarios=[]
    for method in ['FIFO','LIFO','Pro rata']:
        lots=[]; checks=[]
        events=sorted([r for r in ledger['destination_events'] if r['destination_id']==dest['id']],key=lambda r:(r['block'],r['log_index']))
        for event in events:
            shares=Decimal(event['shares_raw']); assets=Decimal(event['assets_raw'])/10**6
            if event['event']=='deposit':
                lots.append({'tx':event['transaction_hash'],'initialShares':shares,'remainingShares':shares,'paid':assets,'proceeds':Decimal(0),'removedBasis':Decimal(0),'matched':matched.get((event['transaction_hash'],event['shares_raw']))})
            else:
                remaining=shares; total=sum(l['remainingShares'] for l in lots)
                assert total >= shares
                candidates=lots if method!='LIFO' else list(reversed(lots))
                for lot in candidates:
                    take=min(lot['remainingShares'],remaining) if method!='Pro rata' else shares*lot['remainingShares']/total
                    lot['remainingShares']-=take; remaining-=take
                    lot['proceeds']+=assets*take/shares
                    lot['removedBasis']+=lot['paid']*take/lot['initialShares']
                    if method!='Pro rata' and remaining==0: break
                assert abs(remaining)<Decimal('0.000000000000000000001')
        assert abs(sum(l['remainingShares'] for l in lots)-endingShares)<Decimal('0.000000000000000000001')
        allIncome=sum(l['proceeds']+endingAssets*l['remainingShares']/endingShares-l['paid'] for l in lots)
        assert abs(allIncome-Decimal(str(dest['net_accrued_claim_income_assets'])))<Decimal('0.000001')
        for lot in lots:
            loan=lot['matched']
            if not loan:continue
            # Extra own cash in a financed deposit earns its own proportional income.
            fundedFraction=min(Decimal(loan['borrowed_cash_raw'])/10**6/lot['paid'],Decimal(1))
            gain=(lot['proceeds']+endingAssets*lot['remainingShares']/endingShares-lot['paid'])*fundedFraction
            cost=Decimal(loan['accrued_borrowing_interest_raw'])/10**6
            scenarios.append({'method':method,'loanTransaction':loan['transaction_hash'],'originationDate':loan['origination_date'],
                              'loanPrincipalPYUSD':loan['borrowed_cash_assets'],'depositCashPYUSD':float(lot['paid']),
                              'retainedShareFraction':float(lot['remainingShares']/lot['initialShares']),
                              'allocatedClaimGainPYUSD':float(gain),'exactLoanInterestPYUSD':float(cost),
                              'claimLessFundingPYUSD':float(gain-cost),'modelled':True})
    return {'rows':scenarios,'wholeDestinationClaimGainPYUSD':dest['net_accrued_claim_income_assets'],
            'method':'Replay every actual destination mint and burn from inception. Assign withdrawals with FIFO, LIFO and proportional share conventions. Value remaining lots against the observed ending claim. Allocate deposit earnings to borrowed cash in proportion to loan cash/deposit cash, then subtract the exact debt-share cohort interest.',
            'scope':'Sensitivity scenarios, not rigorous economic bounds or observed unique provenance. The same whole-account gain reconciles under all conventions. Rewards, gas, outer fees, collateral earnings and private PRIME backing are excluded. The final 108-second lot is an accounting diagnostic, not a representative annual return.'}

def fees():
    p=read('presentation_analysis')['fees']; rows=read('parity_depth_fees_owners')['records']
    claims=[r for r in read('etherfi_parameter_events') if r['event']=='FeesClaimed' and p['window_start']<=r['timestamp']<=p['window_end']]
    receipts={r['params'][0]:r['response']['result'] for r in read('parity_depth_fee_receipts')['records']}
    assert len(receipts)==len(claims)==19
    verified=[]
    for claim in claims:
        tx=claim['transaction_hash'];receipt=receipts[tx]
        asset=claim['decoded']['parameters'][0]['value'].lower();amount=int(claim['decoded']['parameters'][1]['value'])
        assert receipt['status']=='0x1' and int(receipt['blockNumber'],16)==claim['block']
        feeEvents=[e for e in receipt['logs'] if e['address'].lower()=='0x0d05d94a5f1e76c18fbeb7a13d17c8a314088198' and e['topics'][0].startswith('0x9493e5bb') and '0x'+e['topics'][1][-40:]==asset and int(e['data'],16)==amount]
        transfers=[e for e in receipt['logs'] if e['address'].lower()==asset and e['topics'][0]=='0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef' and '0x'+e['topics'][1][-40:]=='0xf0bb20865277abd641a307ece5ee04e79073416c' and int(e['data'],16)==amount]
        assert len(feeEvents)==len(transfers)==1
        verified.append({'transaction':tx,'block':claim['block'],'asset':asset,'rawAmount':str(amount),'recipient':'0x'+transfers[0]['topics'][2][-40:],'receiptConfirmed':True})
    assert all(sum(int(r['rawAmount']) for r in verified if r['asset']==c['asset'].lower())==int(c['raw_amount']) for c in p['claims'])
    converted=[{'transaction':r['label'].split('_',2)[2],'paidETH':int(r['response']['result'],16)/10**18} for r in rows if r['label'].startswith('fee_weETH_')]
    weth=next(r['amount_units'] for r in p['claims'] if r['symbol']=='WETH')
    return {'weETHPayments':converted,'weETHPaymentsETH':sum(r['paidETH'] for r in converted),'WETHPaymentsETH':weth,
            'totalClaimedETH':weth+sum(r['paidETH'] for r in converted),'paymentCount':sum(r['claims'] for r in p['claims']),'verifiedPayments':verified,
            'scope':'Ethereum Accountant payments in the 730-day research window, weETH converted by its own historical getter at each payment block. Claimed cash is neither gross strategy income nor operator profit. Optimism fees and operating costs are not included.'}

def build():
    inputs=sorted(p.name for p in D.glob('parity_depth_*.json') if p.stem not in ['parity_depth_measurements','parity_depth_reader','parity_depth_verification'])
    inputs+=['carry_attribution_ledger.json','carry_attribution_tranches.json','presentation_analysis.json','etherfi_parameter_events.json','etherfi_verified_metrics.json','yb_LT_holders_T.json','carry_attribution_states.json','pilot_details_T.json','carry_economics_chapter.json']
    output={'snapshot':'2026-10-02T23:59:59Z','ethereumBlock':26108081,'ownership':ownership(),'cohortSensitivity':cohort_models(),'feePayments':fees(),'fundingHistory':funding_history(),
            'sourceFiles':inputs,'sourceHashes':{name:hashlib.sha256((D/name).read_bytes()).hexdigest() for name in inputs}}
    (D/'parity_depth_measurements.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    for receipt in output['ownership']['receipts']:
        with (D/('parity-'+receipt['key']+'-holders.csv')).open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(receipt['rows'][0]));w.writeheader();w.writerows(receipt['rows'])
    for name,rows in [('parity-Liquid-Cash-beneficiaries.csv',output['ownership']['liquidCash']['rows']),('parity-Liquid-monthly-debt.csv',output['fundingHistory']['monthlyDebt']),('parity-Liquid-cohort-sensitivity.csv',output['cohortSensitivity']['rows'])]:
        with (D/name).open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('Verified ownership:', ', '.join(r['key']+' '+str(r['holderCount']) for r in output['ownership']['receipts']),
          '| Cash',output['ownership']['liquidCash']['holderCount'],'| Fee cash ETH',round(output['feePayments']['totalClaimedETH'],6))
    return output
if __name__=='__main__':build()
