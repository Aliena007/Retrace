import urllib.request

try:
    resp = urllib.request.urlopen('http://127.0.0.1:8000/ai/search/?q=test')
    data = resp.read().decode('utf-8')
    print('STATUS', resp.getcode())
    print('LENGTH', len(data))
    print(data[:1000])
except Exception as e:
    print('ERROR', e)
    raise
