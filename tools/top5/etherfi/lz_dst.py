import lib,time
ev=lib.load('vault_topic_logs_dedup.json'); names=lib.load('event_names.json')
EP='0x1a44076050125825900e736c501f859c50fe728c'
PS=lib.topic('PacketSent(bytes,bytes,address)')
EIDS={30101:'Ethereum',30110:'Arbitrum',30111:'Optimism',30184:'Base',30331:'Corn',30362:'Berachain',30214:'Scroll',30260:'Sonic?',30332:'Sonic',30335:'Swell',30367:'HyperEVM',30106:'Avalanche',30102:'BSC',30183:'Linea',30181:'Mantle',30109:'Polygon',30280:'Sei',30339:'Ink',30320:'Unichain',30340:'Katana?',30375:'Katana?'}
rows=[]
for l in ev:
    n=names.get(l['topics'][0]) or ''
    if l['address'] in ('0x6ee3aaccf9f2321e49063c4f8da775ddbd407268',) and n.startswith('MessageSent'):
        amt=int(l['data'],16)/1e8
        rc=None
        for t in range(4):
            try: rc=lib.rpc('eth_getTransactionReceipt',[l['transactionHash']])
            except Exception: rc=None
            if rc: break
            time.sleep(2)
        dst=None
        for x in (rc or {}).get('logs',[]):
            if x['address'].lower()==EP and x['topics'][0]==PS:
                d=x['data'][2:]
                off=int(d[0:64],16)*2; ln=int(d[off:off+64],16); pk=d[off+64:off+64+ln*2]
                # version 1B, nonce 8B, srcEid 4B, sender 32B, dstEid 4B
                dst=int(pk[2+16+8+64:2+16+8+64+8],16)
        rows.append((int(l['blockNumber'],16),amt,dst,EIDS.get(dst,dst)))
for r in sorted(rows): print(*r)
