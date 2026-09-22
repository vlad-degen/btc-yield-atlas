# Fetch all mHyperBTC PoR attestations (Midas Attestation Engine) from IPFS (pinata gateway, gzip) and tabulate
import json, gzip, urllib.request, os, datetime
D=os.path.dirname(os.path.abspath(__file__))+'/../raw/'
idx=json.load(open(D+'por_index.json'))
rows=[]
for ts,h,tx in idx:
    fn=D+'por/'+h+'.json'
    if not os.path.exists(fn):
        for g in ['https://gateway.pinata.cloud/ipfs/','https://ipfs.io/ipfs/','https://dweb.link/ipfs/']:
            try:
                b=urllib.request.urlopen(urllib.request.Request(g+h,headers={'user-agent':'Mozilla/5.0'}),timeout=60).read()
                if b[:2]==b'\x1f\x8b': b=gzip.decompress(b)
                json.loads(b); open(fn,'wb').write(b); break
            except Exception as e: print('fail',g,h,e)
    d=json.load(open(fn)); c={x['id']:x for x in d['claims']}
    ops=c['ops_claim']['data']; oc=c.get('overcollateralization',{}).get('data',{}); r=c.get('onetoken_report',{}).get('data',{})
    rows.append(dict(created=datetime.datetime.utcfromtimestamp(ts).isoformat(),snapshot=r.get('_metadata',{}).get('timestamp'),
        nav_btc=float(ops['navReportedByOps']),nav_gross_btc=float(ops.get('navReportedByOpsGross') or 0),price=float(ops['tokenPriceReportedByOps']),
        supply=int(ops['totalSupplyCrossChainReportedByOps'])/1e18,btc_usd=float(oc.get('oracleQuoteRate') or 0),
        assets=r.get('assets',{}),liab=r.get('liabilities',{}),equity=r.get('equity',{})))
json.dump(rows,open(D+'por_table.json','w'),indent=1)
for x in sorted(rows,key=lambda r:r['created']):
    a=x['assets'].get('total',0); l=-x['liab'].get('total',0); e=x['equity'].get('total',0)
    print(x['created'][:16],x['snapshot'],'NAV %.2f BTC px %.8f sup %.3f BTCUSD %.0f | assets $%.2fM liab $%.2fM eq $%.2fM  L/A %.1f%%'%(x['nav_btc'],x['price'],x['supply'],x['btc_usd'],a,l,e,100*l/a if a else 0), {k:round(v,2) for k,v in x['liab'].items() if v})
