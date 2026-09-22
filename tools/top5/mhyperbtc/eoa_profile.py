# Profile unknown counterparties: Blockscout tags + where they forward tokens (top outgoing counterparties)
import json,sys,urllib.request,collections,time
UA={'user-agent':'Mozilla/5.0 (Macintosh) Chrome/126.0'}
def get(u):
    for i in range(5):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
        except Exception as e: time.sleep(3)
    return {}
for a in sys.argv[1:]:
    info=get(f'https://eth.blockscout.com/api/v2/addresses/{a}')
    cnt=get(f'https://eth.blockscout.com/api/v2/addresses/{a}/counters')
    tt=get(f'https://eth.blockscout.com/api/v2/addresses/{a}/token-transfers?type=ERC-20')
    outs=collections.Counter(); ins=collections.Counter(); nm={}
    for x in tt.get('items',[]):
        if int(x['token'].get('holders_count') or 0)<50: continue
        v=int(x['total']['value'])/10**int(x['total']['decimals'] or 18)
        if x['from']['hash'].lower()==a.lower(): outs[(x['to']['hash'],x['token']['symbol'])]+=v; nm[x['to']['hash']]=x['to'].get('name') or ''
        else: ins[(x['from']['hash'],x['token']['symbol'])]+=v; nm[x['from']['hash']]=x['from'].get('name') or ''
    print('==',a,'contract' if info.get('is_contract') else 'EOA',info.get('name'),[t.get('label') for t in (info.get('metadata') or {}).get('tags',[])] if info.get('metadata') else '', 'txs',cnt.get('transactions_count'),'tt',cnt.get('token_transfers_count'))
    for (c,s),v in outs.most_common(4): print('   OUT',s,round(v,2),c,nm.get(c))
    for (c,s),v in ins.most_common(3): print('   IN ',s,round(v,2),c,nm.get(c))
