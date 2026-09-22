import json, urllib.request, urllib.error, time
URL='https://blue-api.morpho.org/graphql'
def gql(q, variables=None, retries=5):
    body=json.dumps({'query':q,'variables':variables or {}}).encode()
    for i in range(retries):
        try:
            req=urllib.request.Request(URL,data=body,headers={'content-type':'application/json','user-agent':'curl/8'})
            r=json.load(urllib.request.urlopen(req,timeout=120))
            if 'errors' in r and not r.get('data'):
                print('ERR',r['errors'][:2]); time.sleep(2*(i+1)); continue
            return r
        except urllib.error.HTTPError as e:
            b=e.read().decode()[:500]; print('HTTP',e.code,b)
            if e.code==400: raise
            time.sleep(3*(i+1))
        except Exception as e:
            print('exc',e); time.sleep(3*(i+1))
    raise Exception('failed')
