# Read all zero-arg view functions of a (proxy) contract using the implementation ABI from Blockscout
import sys, json, urllib.request
sys.path.insert(0,'scripts'); from rpc import *
UA={'user-agent':'Mozilla/5.0 (Macintosh) Chrome/126.0'}
def abi_of(impl,host='https://eth.blockscout.com'):
    d=json.load(urllib.request.urlopen(urllib.request.Request(f'{host}/api/v2/smart-contracts/{impl}',headers=UA),timeout=60))
    return d['abi']
def views(chain,proxy,impl,host='https://eth.blockscout.com',block='latest'):
    out={}
    for f in abi_of(impl,host):
        if f.get('type')=='function' and f.get('stateMutability') in ('view','pure') and not f['inputs']:
            sig=f['name']+'()'
            try:
                r=ecall(chain,proxy,sel(sig),block)
                outs=[o['type'] for o in f['outputs']]
                if outs==['string']: v=dec_str(r)
                elif outs==['address']: v='0x'+r[-40:]
                elif len(outs)==1 and outs[0].startswith(('uint','int','bool','bytes32')): v=int(r,16) if not outs[0].startswith('bytes') else r
                else: v=words(r)
                out[f['name']]=v
            except Exception as e: out[f['name']]='ERR'
    return out
if __name__=='__main__':
    ch,px,impl=sys.argv[1:4]; host=sys.argv[4] if len(sys.argv)>4 else 'https://eth.blockscout.com'
    print(json.dumps(views(ch,px,impl,host),indent=0,default=str))
