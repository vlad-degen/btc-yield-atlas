# Build scan_borrowers_all.csv: every BTC-collateral borrower with >= $2M dollar debt found in the scans, with EOA/contract class and identification
import json, csv, re, os
R='../raw/'
LABEL={  # manual identifications (evidence in top5_selection.md)
 '0x0774b5b15b0cee5e2e14814ccf4d4611ff78ccf5':('Kraken Bitcoin Vault - LoanManager (owner BoringVault 0x7dee...19b2)','Y'),
 '0x7fb9f8f775e3ff458ce5d9d146f36e9e4639205e':('Kraken Bitcoin Vault - LoanManager','Y'),
 '0xd18df3c05d2d11bdedbd9f7501f651e43b9bd986':('Kraken Bitcoin Vault - LoanManager','Y'),
 '0x1e8f4752209a50efe5b6126f5c534dc7018d9489':('Kraken Bitcoin Vault - LoanManager','Y'),
 '0x5ee1e2e3540efce54fc477d6648537e07080f884':('Kraken Bitcoin Vault - LoanManager (WBTC/USDT)','Y'),
 '0xf523259262979a26095474974b56443ad34c53b7':('Kraken Bitcoin Vault - LoanManager (Aave WBTC/USDT)','Y'),
 '0x5f46d540b6ed704c3c8789105f30e075aa900726':('ether.fi Liquid BTC (Veda BoringVault)','Y'),
 '0x933adedd85824da75ec8a334a7907e69e7c02833':('Midas mHyperBTC strategy wallet (MPC EOA, per Midas transparency API)','Y'),
 '0x70fce97d671e81080ca3ab4cc7a59aac2e117137':('Safe 2/4 holding OETH/ARM LP (Origin-related treasury); no share token','N'),
 '0xe40d278afd00e6187db21ff8c96d572359ef03bf':('Safe 2/5 multi-asset treasury/fund (33.4k aWETH + 1,849 cbBTC); no share token','N'),
 '0x4093f559f38c4c87c280d64c85396f649c0d9987':('Safe 4/8 treasury (900.6 WBTC + ~20k wstETH on Compound); no share token','N'),
 '0x9dc8f41a45bfa500d29ebd7b3842c689973da175':('Unverified proxy (FBTC collateral; USDT/USDe sent to EOA 0x68A2...9b70); unidentified','?'),
}
KINDFITS={'EOA':'N (EOA - out of scope)','EIP7702':'N (EIP-7702 delegated EOA - individual)'}
def impl_label(c):
    im=' '.join((n or '') for n,_ in (c.get('impl') or []))
    if 'CoinbaseSmartWallet' in im: return 'Coinbase Smart Wallet (retail borrower)'
    if 'InstaAccountV2' in im: return 'Instadapp DSA (individual account)'
    if 'AccountImplementation' in im: return 'Summer.fi DPM proxy (individual account)'
    if 'Kernel' in im: return 'ZeroDev Kernel smart account (individual)'
    if 'Ambire' in im: return 'Ambire smart account (individual)'
    if c.get('bs_name')=='DSProxy': return 'DSProxy (individual, DeFi Saver/Maker style)'
    if c.get('safe'): return 'Safe %d/%d multisig (no vault or share-token logic; self-directed position)'%(c['safe']['threshold'],len(c['safe']['owners']))
    return c.get('bs_name') or ''
rows=[]
def add(venue,chain,addr,kind,btc,coll_usd,debt_usd,assets,c=None):
    a=addr.lower(); lab,fit=LABEL.get(a,(None,None))
    if lab is None:
        k=(kind or '').split('(')[0]
        if k=='EOA': lab,fit='EOA','N (EOA)'
        elif k.startswith('EIP7702'): lab,fit='EIP-7702 delegated EOA','N (EOA)'
        else: lab,fit=(impl_label(c or {}) or 'contract (unidentified)'),'N'
    rows.append(dict(venue=venue,chain=chain,address=addr,kind=kind,btc_collateral=btc,collateral_usd=round(coll_usd or 0),debt_usd=round(debt_usd or 0),borrowed=assets,identified_as=lab,fits_definition=fit))
# Morpho
mb=json.load(open(R+'morpho_top_borrowers.json')); mc=json.load(open(R+'morpho_borrowers_classified.json'))
for r in mb:
    c=mc.get('%d:%s'%(r['chainId'],r['user']),{})
    dec=8 if r['pair'].split('/')[0] in ('cbBTC','WBTC','kBTC','LBTC','cirBTC','vbWBTC') else 18
    add('Morpho Blue '+r['pair'],r['chain'],r['user'],c.get('kind'),round(int(r['coll_raw'])/10**dec,4),r['coll_usd'],r['debt_usd'],r['pair'].split('/')[1],c)
# Aave v3 / Spark
for r in json.load(open(R+'aave_spark_classified.json')):
    c=r['class']; add(r['market'],r['chain'],r['user'],c.get('kind'),round(sum(r['btc_coll'].values()),4),r['coll_usd'],r['stable_debt'],'+'.join(k for k,v in r['debts'].items() if v>1e5),c)
# Aave deep pages (holder ranks 101-400)
dcl={}
for line in open(R+'aave_deep_classified.txt'):
    p=line.split()
    if p: dcl[p[0].lower()]=line
known={r['address'].lower() for r in rows}
for r in json.load(open(R+'aave_deep_pages.json')):
    if r['user'].lower() in known: continue
    l=dcl.get(r['user'].lower())
    if l is None: k='EOA'; c={}
    else:
        k=l.split()[1]; c={'impl':[(x,None) for x in re.findall(r"\('(\w+)'",l)]}
        sm=re.search(r'safe=(\d+)/(\d+)',l)
        if sm: c['safe']={'threshold':int(sm.group(1)),'owners':[0]*int(sm.group(2))}
    add(r['market']+' (deep pages)',r['chain'],r['user'],k,round(r['btc'],4),r['coll_usd'],r['debt_usd'],'total debt (all assets)',c)
# Compound v3 Ethereum (from log) + classification text
cls={}
for line in open(R+'compound_fluid_classified.txt'):
    p=line.split(); 
    if p: cls[p[0].lower()]=(p[1],line)
comet=None; seen=set()
for line in open(R+'compound_scan.log'):
    m=re.match(r'1 (cUSD\w+) (\w+) accounts',line)
    if m: comet=m.group(1); asset=m.group(2); continue
    m=re.match(r'\s+(0x[0-9a-f]{40}) BTC coll ([\d.]+) debt \$([\d.]+)M',line)
    if m and float(m.group(2))>0:
        a=m.group(1); k,l=cls.get(a,('?',''))
        c={'impl':[(x,None) for x in re.findall(r"\('(\w+)'",l)],'bs_name':'DSProxy' if 'DSProxy' in l else None}
        sm=re.search(r'safe=(\d+)/(\d+)',l)
        if sm: c['safe']={'threshold':int(sm.group(1)),'owners':[0]*int(sm.group(2))}
        add('Compound v3 '+comet+' ('+asset+')','Ethereum',a,k,float(m.group(2)),None,float(m.group(3))*1e6,comet[1:5],c)
# Fluid
for r in json.load(open(R+'fluid_btc_borrowers.json')):
    if (r.get('debt_usd') or 0)>=2e6:
        k,l=cls.get(r['owner'].lower(),('?',''))
        add('Fluid vault %s %s'%(r['vault_id'],r['pair']),'Ethereum',r['owner'],k,r['coll_btc'],None,r['debt_usd'],r['pair'].split('->')[1])
# Kamino
for r in json.load(open(R+'kamino_btc_borrowers.json')):
    add('Kamino main market','Solana',r['owner'],'System-owned wallet (EOA equivalent)',None,r['btc_coll_usd'],r['borrow_usd'],'+'.join(s for s,_ in r['borrows']))
    rows[-1]['fits_definition']='N (wallet)'; rows[-1]['identified_as']='Solana wallet'
# Aave v4
if os.path.exists(R+'aave_v4_classified.json'):
    for r in json.load(open(R+'aave_v4_classified.json')):
        c=r.get('class',{}); add('Aave v4 spoke '+r['spoke'][:10],'Ethereum',r['user'],c.get('kind'),round(sum(r['btc_coll'].values()),4),r['coll_usd'],r['debt_usd'],'+'.join(r['debts']),c)
rows.sort(key=lambda r:-(r['debt_usd'] or 0))
with open('../scan_borrowers_all.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
import collections
print(len(rows)); print(collections.Counter(r['fits_definition'] for r in rows))
print(collections.Counter((r['venue'][:14], r['identified_as'].split(' (')[0][:40]) for r in rows).most_common(30))
