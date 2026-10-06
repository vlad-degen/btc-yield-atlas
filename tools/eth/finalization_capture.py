"""Journalled public reads for the final ETH market and strategy reconstruction."""
import concurrent.futures, datetime, gzip, hashlib, json, pathlib, re, sys, time, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / 'raw/eth/finalization-2026-10-06'
DATA = ROOT / 'data/eth'
RAW.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / 'tools/top5/etherfi'))
from keccak_lib import sel, enc_addr, enc_uint, keccak

T = 1790985599
BLOCK = 26108081
RPC = 'https://eth-mainnet.public.blastapi.io'

def fetch(key, url, payload=None):
    record = {'key': key, 'url': url, 'capturedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'request': payload}
    request = urllib.request.Request(url, data=json.dumps(payload).encode() if payload is not None else None,
                                    headers={'User-Agent': 'ETH-Yield-Research/1.0', 'Content-Type': 'application/json'})
    try:
        # An archived all-validator state is large; keep the shell capture
        # asynchronous while allowing the public node time to stream it.
        timeout = 180 if '/validators?' in url else 40
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
            record.update(status=response.status, HTTPDate=response.headers.get('Date'))
    except urllib.error.HTTPError as error:
        body = error.read()
        record.update(status=error.code, error=str(error))
    except Exception as error:
        body = b''
        record.update(error=str(error))
    digest = hashlib.sha256(body).hexdigest()
    try:
        value = json.loads(body)
        suffix = '.json'
    except (ValueError, UnicodeDecodeError):
        value = None
        suffix = '.txt'
    path = RAW / (key + '-' + digest[:16] + suffix)
    path.write_bytes(body)
    record.update(path=str(path.relative_to(ROOT)), sha256=digest, bytes=len(body))
    with (RAW / 'requests.jsonl').open('a') as journal:
        journal.write(json.dumps(record) + '\n')
    return record, value

def capture_urls(items, name):
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(lambda item: fetch(item['key'], item['url']), items))
    records = [record for record, _ in results]
    (DATA / (name + '.json')).write_text(json.dumps(records, indent=2) + '\n')
    print(json.dumps([{'key':r['key'], 'status':r.get('status'), 'bytes':r['bytes'], 'error':r.get('error')} for r in records]), flush=True)
    return results

def call(label, address, signature, args='', block=BLOCK, sender=None):
    transaction = {'to':address, 'data':'0x' + sel(signature) + args}
    if sender:
        transaction['from'] = sender
    return {'label':label, 'address':address, 'signature':signature, 'block':block,
            'method':'eth_call', 'params':[transaction, hex(block)]}

def rpc(name, rows, url=RPC, batch_size=8, delay=0.6):
    result = []
    for offset in range(0, len(rows), batch_size):
        batch = rows[offset:offset + batch_size]
        payload = [{'jsonrpc':'2.0', 'id':i+1, 'method':row['method'], 'params':row['params']} for i,row in enumerate(batch)]
        record, values = fetch(name + '_' + str(offset // batch_size), url, payload)
        values = [values] if isinstance(values, dict) else values or []
        responses = {r.get('id'):r for r in values if isinstance(r, dict)}
        result.extend({**row, 'response':responses.get(i+1, {'error':{'message':'No response'}}), 'capture':record}
                      for i,row in enumerate(batch))
        print(name, min(offset+batch_size,len(rows)), '/', len(rows), flush=True)
        time.sleep(delay)
    output = {'snapshotTimestamp':T, 'ethereumBlock':BLOCK, 'records':result}
    (DATA / (name + '.json')).write_text(json.dumps(output, indent=2) + '\n')
    return result

def repair_rate_limits(files):
    for filename in files:
        path = DATA / (filename + '.json')
        data = json.loads(path.read_text())
        for attempt in range(3):
            pending = [r for r in data['records'] if r.get('response', {}).get('error', {}).get('code') == 429]
            if not pending:
                break
            print(filename, 'retry', attempt+1, 'rate-limited calls', len(pending), flush=True)
            time.sleep(2)
            recovered = rpc(filename + '_retry_' + str(attempt+1), pending)
            bylabel = {r['label']:r for r in recovered}
            for row in data['records']:
                if row['label'] in bylabel:
                    fresh = bylabel[row['label']]
                    row.setdefault('earlierAttempts', []).append({'response':row['response'], 'capture':row['capture']})
                    row['response'], row['capture'] = fresh['response'], fresh['capture']
            path.write_text(json.dumps(data,indent=2)+'\n')
        remaining = sum(r.get('response',{}).get('error',{}).get('code') == 429 for r in data['records'])
        print(filename, 'remaining rate limits',remaining,flush=True)
        assert remaining == 0

def interfaces(addresses, name):
    return capture_urls([{'key':key+'_interface', 'url':'https://eth.blockscout.com/api/v2/smart-contracts/' + address}
                         for key,address in addresses.items()], name)

def native_history(months, name):
    """Aggregate the archived active validator state, retaining compressed receipts.

    Match complete validator objects rather than estimating stake from counts.
    The fixed field ordering is checked against the number of index fields.
    """
    endpoint = 'http://testing.mainnet.beacon-api.nimbus.team'
    pattern = re.compile(rb'\{"index":"\d+","balance":"(\d+)","status":"([^"]+)","validator":\{[^{}]*?"effective_balance":"(\d+)"[^{}]*?\}\}')
    output = []
    for month in months:
        slot = (month['timestamp'] - 1606824023) // 12
        header_record = header = None
        for candidate in range(slot, slot - 5, -1):
            header_record, header = fetch(name + '_' + month['month'] + '_header_' + str(candidate), endpoint + '/eth/v1/beacon/headers/' + str(candidate))
            if isinstance(header, dict) and header.get('data', {}).get('canonical'):
                slot = candidate
                break
        if not isinstance(header, dict) or not header.get('data', {}).get('canonical'):
            output.append({**month, 'status':'header unavailable', 'source':header_record})
            continue
        print('Active validator state:', month['month'], slot, flush=True)
        url = endpoint + '/eth/v1/beacon/states/' + str(slot) + '/validators?status=active_ongoing,active_exiting,active_slashed'
        record = {'key':name + '_' + month['month'], 'url':url, 'capturedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'request':None}
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'ETH-Yield-Research/1.0', 'Accept-Encoding':'gzip'})
            with urllib.request.urlopen(req, timeout=180) as response:
                wire = response.read()
                record.update(status=response.status, HTTPDate=response.headers.get('Date'), encoding=response.headers.get('Content-Encoding'))
            body = gzip.decompress(wire) if record['encoding'] == 'gzip' else wire
            digest = hashlib.sha256(body).hexdigest()
            compressed = wire if record['encoding'] == 'gzip' else gzip.compress(body, compresslevel=1, mtime=0)
            path = RAW / (record['key'] + '-' + digest[:16] + '.json.gz')
            path.write_bytes(compressed)
            record.update(path=str(path.relative_to(ROOT)), sha256=digest, bytes=len(body), compressedBytes=len(compressed), compressedSha256=hashlib.sha256(compressed).hexdigest())
            total = effective = count = 0
            statuses = {}
            for match in pattern.finditer(body):
                count += 1
                total += int(match[1]); effective += int(match[3])
                status = match[2].decode()
                assert status in ('active_ongoing', 'active_exiting', 'active_slashed')
                statuses[status] = statuses.get(status,0) + 1
            assert count == body.count(b'"index":') and count > 100000
            flags = body[:body.index(b'"data":')]
            row = {**month, 'status':'observed', 'slot':slot, 'stateTimestamp':1606824023+slot*12,
                   'stateRoot':header['data']['header']['message']['state_root'], 'blockRoot':header['data']['root'],
                   'activeValidatorCount':count, 'activeBalanceGwei':str(total), 'activeEffectiveBalanceGwei':str(effective),
                   'statusCounts':statuses, 'finalized':b'"finalized":true' in flags,
                   'executionOptimistic':b'"execution_optimistic":true' in flags, 'source':record, 'headerSource':header_record}
            print(month['month'], 'active ETH', total/1e9, 'effective ETH', effective/1e9, 'wire MB',len(wire)/1e6, flush=True)
            del body, wire, compressed
        except Exception as error:
            record['error'] = str(error)
            row = {**month, 'status':'capture failed', 'source':record}
        with (RAW / 'requests.jsonl').open('a') as journal:
            journal.write(json.dumps(record) + '\n')
        output.append(row)
        (DATA / (name+'.json')).write_text(json.dumps(output,indent=2)+'\n')
    return output

if __name__ == '__main__':
    jobs = json.loads(pathlib.Path(sys.argv[2]).read_text())
    if sys.argv[1] == 'urls':
        capture_urls(jobs['items'], jobs['name'])
    elif sys.argv[1] == 'interfaces':
        interfaces(jobs['addresses'], jobs['name'])
    elif sys.argv[1] == 'rpc':
        rpc(jobs['name'], jobs['rows'], jobs.get('url',RPC), jobs.get('batchSize',8), jobs.get('delay',0.6))
    elif sys.argv[1] == 'native-history':
        native_history(jobs['months'], jobs['name'])
    elif sys.argv[1] == 'repair':
        repair_rate_limits(jobs['files'])
    else:
        raise SystemExit('Use urls, interfaces or rpc')
