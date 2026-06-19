import requests, json
from pprint import pprint

PAYLOAD = {
    "query": "What was NVIDIA YoY revenue growth rate in June 2024?",
    "use_teacher_model": False,
    "temperature": 0.0,
}

try:
    r = requests.post('http://localhost:8000/query', json=PAYLOAD, timeout=30)
    print('HTTP', r.status_code)
    try:
        data = r.json()
    except Exception:
        print('Response not JSON, raw text:')
        print(r.text[:4000])
        raise

    def find_keys(obj, keys):
        found = []
        def rec(o, path=''):
            if isinstance(o, dict):
                for k,v in o.items():
                    p = f"{path}.{k}" if path else k
                    if k.lower() in keys:
                        found.append((p, v))
                    rec(v, p)
            elif isinstance(o, list):
                for i,v in enumerate(o):
                    rec(v, f"{path}[{i}]")
        rec(obj)
        return found

    keys_to_find = {'confidence','score','scores','components','relevance','factual','numerical','entailment','answer','answers','sources','source'}
    found = find_keys(data, keys_to_find)

    print('\nTop-level keys:')
    if isinstance(data, dict):
        pprint(list(data.keys()))
    elif isinstance(data, list):
        print('List length:', len(data))
        if len(data)>0 and isinstance(data[0], dict):
            pprint(list(data[0].keys()))

    print('\nFound keys and values (truncated):')
    for p,v in found:
        s = json.dumps(v) if not isinstance(v, str) else v
        print(f"- {p}: {s[:400]}")

    print('\nFull JSON length:', len(json.dumps(data)))

except Exception as e:
    print('ERR', e)
