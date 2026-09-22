import json,urllib.request,urllib.parse,time,sys
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
B='https://api.yieldbasis.com'
def api(path,**q):
    url=B+path+('?'+urllib.parse.urlencode(q) if q else '')
    for k in range(4):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/json','Origin':'https://yieldbasis.com','Referer':'https://yieldbasis.com/'}),timeout=90).read())
        except urllib.error.HTTPError as e:
            return {'error':e.code,'body':e.read().decode()[:500]}
        except Exception as e:
            last=e; time.sleep(2)
    raise last
