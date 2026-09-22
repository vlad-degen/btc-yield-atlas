# Compound v3: BTC collateral totals per Comet
from addrinfo import ecall, dec_str
COMETS=[(1,'cUSDCv3','0xc3d688B66703497DAA19211EEdff47f25384cdc3'),(1,'cUSDTv3','0x3Afdc9BCA9213A35503b077a6072F3D0d5AB0840'),(1,'cUSDSv3','0x5D409e56D886231aDAf00c8775665AD0f9897b56'),
        (8453,'cUSDCv3','0xb125E6687d4313864e53df431d5425969c15Eb2F'),(42161,'cUSDCv3','0x9c4ec768c28520B50860ea7a15bd7213a9fF58bf'),(42161,'cUSDTv3','0xd98Be00b5D27fc98112BdE293e487f8D4cA57d07'),(42161,'cUSDC.ev3','0xA5EDBDD9646f8dFF606d7448e414884C7d905dCA')]
for ch,n,c in COMETS:
    k=int(ecall(ch,c,'0xa46fe83b'),16)  # numAssets()
    tb=int(ecall(ch,c,'0x8285ef40'),16) if ecall(ch,c,'0x8285ef40') else 0  # totalBorrow()
    out=[]
    for i in range(k):
        info=ecall(ch,c,'0xc8c7fe6b'+hex(i)[2:].rjust(64,'0'))  # getAssetInfo(uint8)
        h=info[2:]; asset='0x'+h[64+24:128]
        sym=dec_str(ecall(ch,asset,'0x95d89b41'))
        if sym and 'BTC' in sym.upper():
            tot=ecall(ch,c,'0x59e017bd'+asset[2:].rjust(64,'0'))  # totalsCollateral(address)
            dec=int(ecall(ch,asset,'0x313ce567'),16)
            out.append((sym,int(tot[2:66],16)/10**dec))
    print(ch,n,'totalBorrow %.1fM'%(tb/1e6),out)
