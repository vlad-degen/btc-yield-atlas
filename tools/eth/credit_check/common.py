"""Helpers for the Credit-row check (ETH snapshot T = 2026-10-02 23:59:59 UTC, Ethereum block 26,108,081)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
import importlib.util
_s = importlib.util.spec_from_file_location('lslib', os.path.join(ROOT, 'tools', 'eth', 'lending_split', 'lib.py')); lslib = importlib.util.module_from_spec(_s); _s.loader.exec_module(lslib)
_k = importlib.util.spec_from_file_location('kl', os.path.join(ROOT, 'tools', 'top5', 'etherfi', 'keccak_lib.py')); kl = importlib.util.module_from_spec(_k); _k.loader.exec_module(kl)
rpc, call1, mcall, a32, u32, U, A, words, addr_list, dec_str, post_raw, RPCS = (lslib.rpc, lslib.call1, lslib.mcall, lslib.a32, lslib.u32, lslib.U, lslib.A, lslib.words, lslib.addr_list, lslib.dec_str, lslib.post_raw, lslib.RPCS)
keccak, _sel = kl.keccak, kl.sel
OUT = os.path.join(ROOT, 'raw', 'eth', 'credit-check-2026-10-08')
os.makedirs(OUT, exist_ok=True)
B1 = 26108081
TS = 1790985599
L2 = {8453: 52098126, 42161: 511139919}
WETH = {1: '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2', 8453: '0x4200000000000000000000000000000000000006',
        42161: '0x82af49447d8a07e3bd95bd0d56f35241523fbab1'}
WSTETH = '0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0'
WEETH = '0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee'

def sel(sig): return '0x' + _sel(sig)
def topic(sig): return '0x' + keccak(sig.encode()).hex()
def c(chain, to, sig, *args, block=None):
    data = sel(sig) + ''.join(a32(a) if isinstance(a, str) else u32(a) for a in args)
    return call1(chain, to, data, block if block is not None else (B1 if chain == 1 else L2[chain]))
def bal(chain, token, owner, block=None): return U(c(chain, token, 'balanceOf(address)', owner, block=block))

def logs(chain, address, topics, frm, to, step=500000):
    out = []; b = frm
    while b <= to:
        e = min(to, b + step - 1)
        try:
            r = rpc(chain, 'eth_getLogs', [{'address': address, 'fromBlock': hex(b), 'toBlock': hex(e), 'topics': topics}], retries=3)
        except Exception as ex:
            if step > 2000:
                out += logs(chain, address, topics, b, e, step // 5); b = e + 1; continue
            raise
        out += r or []; b = e + 1
    return out

def save(name, obj):
    p = os.path.join(OUT, name); json.dump(obj, open(p, 'w'), indent=1, default=str); return p
