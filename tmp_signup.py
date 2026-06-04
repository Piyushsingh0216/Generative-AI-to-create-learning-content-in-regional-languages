import json
import urllib.request
import urllib.error
import traceback
payload={'email':'testuser12345@example.com','password':'Password123!','full_name':'Test User'}
req=urllib.request.Request('http://127.0.0.1:8000/api/auth/signup',data=json.dumps(payload).encode('utf-8'),headers={'Content-Type':'application/json'})
try:
    with urllib.request.urlopen(req,timeout=10) as resp:
        print('SIGNUP',resp.status)
        print(resp.read().decode())
except urllib.error.HTTPError as e:
    print('HTTP',e.code)
    print(e.read().decode())
except Exception:
    traceback.print_exc()

