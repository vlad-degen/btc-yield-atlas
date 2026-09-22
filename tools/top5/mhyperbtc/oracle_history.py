# NAV oracle (MHyperBtcCustomAggregatorFeed proxy 0x3359...517C) AnswerUpdated history via Blockscout v2
import json, urllib.request, urllib.parse, datetime, time
UA={'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36'}
def get(u):
    for i in range(6):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
        except Exception as e: print('retry',e); time.sleep(3)
def all_logs(addr, host='https://eth.blockscout.com'):
    u=f'{host}/api/v2/addresses/{addr}/logs'; out=[]; p=None
    while True:
        d=get(u+('?'+urllib.parse.urlencode(p) if p else '')); out+=d['items']; p=d.get('next_page_params')
        if not p: break
    return out
if __name__=='__main__':
    L=all_logs('0x3359921992C33ef23169193a6C91F2944A82517C')
    json.dump(L,open('raw/oracle_logs_all.json','w'))
    rows=[]
    for x in L:
        dec=x.get('decoded') or {}
        if dec.get('method_call','').startswith('AnswerUpdated'):
            p={q['name']:q['value'] for q in dec['parameters']}
            rows.append((int(p['roundId']),int(p['timestamp']),int(p['data'])/1e8,x['block_number'],x['transaction_hash']))
        else:
            print('other event', x['block_number'], dec.get('method_call'), [ (q['name'],q['value']) for q in dec.get('parameters',[])] if dec else x['topics'][0])
    rows.sort()
    with open('raw/oracle_rounds.csv','w') as f:
        f.write('round,timestamp,utc,nav,block,tx\n')
        for r in rows: f.write('%d,%d,%s,%.8f,%d,%s\n'%(r[0],r[1],datetime.datetime.fromtimestamp(r[1],datetime.timezone.utc).strftime('%Y-%m-%d %H:%M'),r[2],r[3],r[4]))
    prev=None
    for r in rows:
        ch='' if prev is None else '%+.4f%%'%(100*(r[2]/prev-1))
        print(r[0],datetime.datetime.fromtimestamp(r[1],datetime.timezone.utc).strftime('%Y-%m-%d %H:%M'),'%.8f'%r[2],ch); prev=r[2]
