import lib,json
res=lib.load('vault_topic_logs.json'); names=lib.load('event_names.json')
seen=set(); ev=[]
for l in res:
    key=(l['transactionHash'],l['logIndex'])
    if key in seen: continue
    seen.add(key); ev.append(l)
lib.save('vault_topic_logs_dedup.json',ev)
blk_ts={}
def ts(b):
    if b not in blk_ts: blk_ts[b]=int(lib.rpc('eth_getBlockByNumber',[hex(b),False])['timestamp'],16)
    return blk_ts[b]
want={'0x6ee3aaccf9f2321e49063c4f8da775ddbd407268':'eBTC-LZteller','0x6bc15d7930839ec18a57f6f7df72ae1b439d077f':'LBTC-OFT','0x386e7a3a0c0919c9d53c3b04ff67e73ff9e45fb6':'BTCN-OFT','0x99c9fc46f92e8a1c0dec1b1747d010903e884be1':'OP-bridge','0xd8a791fe2be73eb6e6cf1eb0cb3f36adc9b3f8f9':'L1gateway?','0x28b5a0e9c621a5badaa536219b3a228c8168cf5d':'CCTP','0xc026395860db2d07ee33e05fe50ed7bd583189c7':'OFT?','0x7c75cbb851d321b2ec8034d58a9b5075e991e584':'tacBTC-teller','0xbf5eb70b93d5895c839b8beb3c27dc36f6b56fea':'Bitcorn-swap','0x9a214cdd8967d7616cfaf7b92a10b2116a0c39a7':'BoringQueue'}
for l in sorted(ev,key=lambda x:int(x['blockNumber'],16)):
    a=l['address']
    if a not in want: continue
    n=names.get(l['topics'][0],l['topics'][0])
    if n.startswith('Deposit(uint256'): continue
    d=l['data'][2:]; vals=[d[i:i+64] for i in range(0,len(d),64)]
    b=int(l['blockNumber'],16)
    print(lib.dt(ts(b)),b,want[a],n.split('(')[0],[x[-40:] if x.startswith('000000000000000000000000') and int(x,16)>2**100 else int(x,16) for x in vals[:6]],[t[-40:] for t in l['topics'][1:]])
