# Blockscout v2 paginator: python3 bs_fetch.py <base> <path> <outname> [maxpages]
import lib,sys,json,time
def fetch(base,path,maxpages=2000,extra=''):
    items=[];params=extra
    for i in range(maxpages):
        url=f'{base}/api/v2/{path}'+(('?'+params) if params else '')
        d=lib.get(url)
        items+=d.get('items',[])
        np=d.get('next_page_params')
        if not np: break
        params='&'.join(f'{k}={v}' for k,v in np.items() if v is not None)
        if extra: params=extra+'&'+params
        if i%20==0: print(i,len(items),file=sys.stderr)
    return items
if __name__=='__main__':
    base,path,out=sys.argv[1:4]
    mp=int(sys.argv[4]) if len(sys.argv)>4 else 2000
    extra=sys.argv[5] if len(sys.argv)>5 else ''
    it=fetch(base,path,mp,extra)
    lib.save(out,it); print(out,len(it))
