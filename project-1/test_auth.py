from fastapi.testclient import TestClient
import main

client = TestClient(main.app)

# Test create user
resp = client.post('/auth/', json={'username':'debug_user','password':'secret'})
print('status_code:', resp.status_code)
print('content:', resp.text)

# Test token
resp2 = client.post('/auth/token', data={'username':'debug_user','password':'secret'})
print('token status:', resp2.status_code)
print('token content:', resp2.text)
