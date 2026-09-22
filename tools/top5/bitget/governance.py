"""Read roles/keys/timelocks of the whole stack (Morph + Ethereum) -> ../raw/governance.json"""
import json
from rpc import *
out={}
def safe(a,ch='morph'):
    try: return dict(threshold=dec_uint(eth_call(ch,a,sel('getThreshold()'))),owners=dec_addr_array(eth_call(ch,a,sel('getOwners()'))))
    except Exception: return None
V='0x85a1d961f1d1bbd9b4a6d96106c5bf9ae91f0510'; G='0x9131eb40bd0bdce73c72755f1bb2cf39a9453341'
out['aera_vault']=dict(owner=dec_addr(ca(V,'owner()')),authority=dec_addr(ca(V,'authority()')),provisioner=dec_addr(ca(V,'provisioner()')),feeCalculator=dec_addr(ca(V,'feeCalculator()')),guardians=dec_addr_array(ca(V,'getActiveGuardians()')))
out['aera_timelock_0xcda0']=dict(minDelay_s=dec_uint(ca('0xcda0556acf68679a525e1972185574a9a1dd0d94','getMinDelay()')),proposer_safe=safe('0x4b6caf5652ab97db7d5dd0ee722d2580795531c5'))
out['pfc_timelock_0xf77a']=dict(minDelay_s=dec_uint(ca('0xf77af623889c1a6decbbbefb7871a0469ee84ee5','getMinDelay()')),proposer_safe=safe('0x55483fc7ebd7e4ed30ab2897b4e0a606a510a7ee'))
out['forwarder_owner_safe_0x759b']=safe('0x759bf4B6153875346f4E2f959676f864bbC97830')
out['gtusdc']=dict(owner=dec_addr(ca(G,'owner()')),owner_safe=safe('0xc2ae41727e377cf4e617e387b0988a70de5883ba'),curator=dec_addr(ca(G,'curator()')),curator_safe=safe('0xae95cef61933a6047dc723e9a850adf29d4b9430'),
    sentinels={a:safe(a) for a in ['0x41a5c880f165b2c891787a013803b54676b81eed','0x72c5a62d1ec964da5d0a955fe4bc709526255a19','0xaff299612185830d94383349f4fdbf0d7dc7f576']},
    allocators=[a for a in ['0xae95cef61933a6047dc723e9a850adf29d4b9430','0xa690308421f6160273983fd86e3f82919e6cda21'] if dec_uint(ca(G,'isAllocator(address)',enc_addr(a)))],
    timelocks={s:dec_uint(ca(G,'timelock(bytes4)',s[2:]+'0'*56)) for s in ['0xf6f98fd5','0x2438525b','0x60d54d41','0x585cd34b','0x47966291','0xb192a84a','0x70897b23','0xfe56e232','0x3e9d2ac7','0xe90956cf']})
BG='0x31011317764e097b28d159a8145b92bfa453f606'
out['bgbtc_morph']=dict(owner=dec_addr(ca(BG,'owner()')),ccip_admin=dec_addr(ca(BG,'getCCIPAdmin()')),minters=dec_addr_array(ca(BG,'getMinters()')),pool_owner=dec_addr(ca('0xf50be8eade267fc8495e1bd6db55ca94e71f4e4b','owner()')))
T='0x0520930f21b14cafac7a27b102487bee7138a017'; MC='0x0b24cf5aaad905ae19c146f60281f2ee2b4fc6d6'
out['bgbtc_eth']=dict(owner=dec_addr(eth_call('eth',T,sel('owner()'))),minter=dec_addr(eth_call('eth',T,sel('minter()'))),mintDestination=dec_addr(eth_call('eth',T,sel('mintDestination()'))),
    minter_owner=dec_addr(eth_call('eth',MC,sel('owner()'))),minter_caller=dec_addr(eth_call('eth',MC,sel('caller()'))),maxMintPerDay=dec_uint(eth_call('eth',MC,sel('maxMintPerDay()')))/1e8,
    pool_owner=dec_addr(eth_call('eth','0xa1f0caf824d5bbf103b33172a711e58c6cab2a04',sel('owner()'))))
F='0xb81131B6368b3F0a83af09dB4E39Ac23DA96C2Db'
adm='0x'+call('morph','eth_getStorageAt',[F,'0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103','latest'])[-40:]
own=dec_addr(ca(adm,'owner()')); out['redstone_btc_feed_proxy']=dict(proxy_admin=adm,admin_owner=own,admin_owner_safe=safe(own))
json.dump(out,open('../raw/governance.json','w'),indent=1)
print(json.dumps(out,indent=1)[:3000])
