import sys; sys.path.insert(0,'.')
from mechB_rpc import *
vaults=[('ethereum','LBTCv','0x5401b8620E5FB570064CA9114fd1e135fd77D57c','0x28634D0c5edC67CF2450E74deA49B90a4FF93dCE'),
('ethereum','eBTC','0x657e8C867D8B37dCC18fA4Caead9C45EB088C642','0x1b293DC39F94157fA0D1D36d7e0090C8B8B8c13F'),
('ethereum','Coinbase BTCv','0x42A03534DBe07077d705311854E3B6933dD6Af85','0x1c217f17d57d3CCD1CB3d8CB16B21e8f0b544156'),
('ethereum','Pump BTC-Fi','0xFE0C961A49E1aEe2AE2d842fE40157365C6d978f',None),
('ethereum','Bedrock Uni BTC-Fi','0xf6d71c15657A7f2B9aeDf561615feF9E05fE2cb3',None),
('ethereum','Liquid BTC','0x5f46d540b6eD704C3c8789105F30E075AA900726',None),
('ethereum','Lombard Loop BTC','0x1293b71644e7E55A692Cade85a0EDB381868AA7c',None),
('ethereum','sBTCN','0x5E272ca4bD94e57Ec5C51D26703621Ccac1A7089',None),
('ethereum','Hourglass BTC','0xAF135099ab69024701CEC9D726f26F508bd05837',None),
('ethereum','LBTCv Sonic','0x309f25d839A2fe225E80210e110C99150Db98AAF',None),
('ethereum','tacBTC','0x6Bf340dB729d82af1F6443A0Ea0d79647b1c3DDf',None),
('berachain','Prime Liquid Bera BTC','0x46fcd35431f5B371224ACC2e2E91732867B1A77e',None),
('base','Coinbase BTC','0x42A03534DBe07077d705311854E3B6933dD6Af85',None),
('bob','Hybrid BTC','0x9998e05030Aee3Af9AD3df35A34F5C51e1628779',None),
('sonic','Sonic scBTC','0xBb30e76d9Bb2CC9631F7fC5Eb8e87B5Aff32bFbd',None),
('sonic','Sonic LBTC Vault','0x309f25d839A2fe225E80210e110C99150Db98AAF',None),
('ink','Advanced Strategies BTC','0x7Dee0120739b7ec048B469939EFB178ADbbB19B2',None),
]
for ch,n,v,acc in vaults:
    try:
        ts=u(ch,v,'totalSupply'); d=u(ch,v,'decimals'); sym=s(ch,v)
        print(f"{ch}|{n}|{v}|{sym}|supply={ts/10**d:.4f}")
    except Exception as e: print(ch,n,v,'ERR',e)
