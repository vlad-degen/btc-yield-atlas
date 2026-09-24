"""Retrying client for the Morpho API (blue-api.morpho.org/graphql)."""
import json, subprocess, time
def gql(q, v=None, tries=6):
    body = json.dumps({'query': q, 'variables': v or {}})
    last = None
    for a in range(tries):
        r = subprocess.run(['curl', '-sS', '-m', '120', '-A', 'Mozilla/5.0', '-H', 'Content-Type: application/json',
                            'https://blue-api.morpho.org/graphql', '-d', body], capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
            if d.get('data'):
                return d
            last = d
        except Exception as e:
            last = r.stdout[:300]
        time.sleep(4 * (a + 1))
    raise SystemExit(f'gql failed: {str(last)[:400]}')
