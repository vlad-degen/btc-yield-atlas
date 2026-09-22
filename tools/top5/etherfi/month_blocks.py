import lib,datetime,json
pts=[]
d=datetime.datetime(2024,11,1,tzinfo=datetime.UTC)
while d<datetime.datetime(2026,9,1,tzinfo=datetime.UTC):
    nd=(d.replace(day=28)+datetime.timedelta(days=4)).replace(day=1)
    pts.append((d.strftime('%Y-%m'), int(nd.timestamp())-1))
    d=nd
pts.append(('2026-09-20', int(datetime.datetime(2026,9,20,14,0,tzinfo=datetime.UTC).timestamp())))
pts.append(('2024-11-14launch', 1731626531+60))
out={}
for k,ts in pts:
    for ch in ['eth','op']:
        try:
            b=lib.block_at(ts,ch)
        except Exception as e:
            b=None
        out.setdefault(k,{})[ch]=b
    out[k]['ts']=ts
    print(k,out[k])
lib.save('month_blocks.json',out)
