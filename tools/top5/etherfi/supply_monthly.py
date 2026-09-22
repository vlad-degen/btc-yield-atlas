import lib
V='0x5f46d540b6eD704C3c8789105F30E075AA900726'
mb=lib.load('month_blocks.json')
out={}
for k,v in mb.items():
    e=lib.u(lib.c(V,'totalSupply()',block=v['eth']))
    o=lib.u(lib.c(V,'totalSupply()',block=v['op'],chain='op'))
    out[k]={'eth':e,'op':o}
    print(k,e and e/1e8,o and o/1e8)
lib.save('supply_monthly.json',out)
