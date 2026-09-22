import json, urllib.request, urllib.error, sys
def gql(q, v=None):
    req=urllib.request.Request('https://blue-api.morpho.org/graphql', data=json.dumps({'query':q,'variables':v or {}}).encode(), headers={'Content-Type':'application/json','User-Agent':'Mozilla/5.0'})
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())
