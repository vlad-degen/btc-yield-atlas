import lib,json,datetime,csv
acc=lib.load('acc_logs_rpc.json')
T=lib.topic('ExchangeRateUpdated(uint96,uint96,uint64)')
rows=[]
for l in acc:
    if l['topics'][0]!=T: continue
    d=l['data'][2:]
    old=int(d[0:64],16); new=int(d[64:128],16); t=int(d[128:192],16)
    rows.append({'block':int(l['blockNumber'],16),'ts':t,'old':old,'new':new,'tx':l['transactionHash']})
rows.sort(key=lambda r:(r['block']))
lib.save('rate_updates.json',rows)
print(len(rows), lib.dt(rows[0]['ts']), rows[0]['old'], rows[0]['new'], lib.dt(rows[-1]['ts']), rows[-1]['new'])
# drops
for r in rows:
    ch=r['new']/r['old']-1
    if ch<0 or abs(ch)>0.002: print(lib.dt(r['ts']), r['block'], r['old'], r['new'], f'{ch*100:+.4f}%')
# gaps
for i in range(1,len(rows)):
    g=(rows[i]['ts']-rows[i-1]['ts'])/86400
    if g>5: print('gap',lib.dt(rows[i-1]['ts']),lib.dt(rows[i]['ts']),round(g,1))
