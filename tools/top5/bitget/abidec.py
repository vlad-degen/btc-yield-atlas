import json
from rpc import k256
def evsig(e): 
    def t(i):
        if i['type'].startswith('tuple'):
            return '('+','.join(t(c) for c in i['components'])+')'+i['type'][5:]
        return i['type']
    return e['name']+'('+','.join(t(i) for i in e['inputs'])+')'
def build(abi):
    return {'0x'+k256(evsig(e).encode()).hex():e for e in abi if e.get('type')=='event'}
def dec_word(t,wd):
    if t=='address': return '0x'+wd[-40:]
    if t=='bool': return bool(int(wd,16))
    if t.startswith('uint') or t.startswith('int'): return int(wd,16)
    return '0x'+wd
def decode(l,EV):
    e=EV.get(l['topics'][0])
    if not e: return {'event':l['topics'][0][:10]}
    tp=[x for x in l['topics'][1:] if x]; d=l['data'][2:]; words=[d[i:i+64] for i in range(0,len(d),64)]
    out={'event':e['name']}; ti=0; wi=0
    for i in e['inputs']:
        if i.get('indexed'):
            out[i['name']]=dec_word(i['type'],tp[ti][2:]) if ti<len(tp) else None; ti+=1
        else:
            if i['type'] in ('bytes','string') or i['type'].endswith('[]'):
                out[i['name']]='<dyn>'; wi+=1
            else:
                out[i['name']]=dec_word(i['type'],words[wi]) if wi<len(words) else None; wi+=1
    return out
