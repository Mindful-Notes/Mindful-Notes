import urllib.request
import urllib.parse
import urllib.error
import json
import random
import string

BASE_URL = "http://127.0.0.1:8000"

def generate_random_email():
    return f"test_{''.join(random.choices(string.ascii_lowercase, k=8))}@example.com"

def make_request(method, endpoint, data=None, headers=None):
    url = f"{BASE_URL}{endpoint}"
    if headers is None:
        headers = {}
    
    if data:
        json_data = json.dumps(data).encode('utf-8')
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
        req = urllib.request.Request(url, data=json_data, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            response_body = response.read().decode('utf-8')
            return status_code, json.loads(response_body) if response_body else {}
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))

def form_login(email, password):
    url = f"{BASE_URL}/auth/login"
    data = urllib.parse.urlencode({'username': email, 'password': password}).encode('utf-8')
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            response_body = response.read().decode('utf-8')
            return status_code, json.loads(response_body)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))

def test_logout_flow():
    print("--- 1. Testing Logout without Token ---")
    status, body = make_request("GET", "/auth/logout")
    print(f"Status: {status}, Body: {body}")
    if status == 401:
        print("PASS: Logout without token returned 401.")
    else:
        print("FAIL: Expected 401.")

    print("\n--- 2. Registering New User ---")
    email = generate_random_email()
    password = "password123"
    print(f"Email: {email}")
    status, body = make_request("POST", "/auth/register", {"email": email, "password": password, "nickname": "testuser"})
    
    # Note: UserCreate schema in router.register might only strictly match usage.
    # Looking at UserCreate usage in router.py: `user: UserCreate`
    # I should check UserCreate schema. Assuming `email`, `password`.
    # But wait, looking at code: `user_email=user.email, hashed_pass=...`
    # Let's hope the schema matches my guess. 
    # If this fails, I'll need to check `app/auth/schemas.py`.
    
    print(f"Status: {status}, Body: {body}")
    
    if status != 201:
        print("FAIL: Registration failed.")
        return

    print("\n--- 3. Logging in ---")
    status, body = form_login(email, password)
    print(f"Status: {status}, Body: {body}")
    
    if status != 200:
        print("FAIL: Login failed.")
        return

    token = body.get("access_token")
    if not token:
        print("FAIL: No access token returned.")
        return
    print("Got access token.")

    print("\n--- 4. Logging out with Token ---")
    headers = {"Authorization": f"Bearer {token}"}
    status, body = make_request("GET", "/auth/logout", headers=headers)
    print(f"Status: {status}, Body: {body}")
    
    if status == 200:
        print("PASS: Logout with token succeeded.")
    else:
        print(f"FAIL: Expected 200, got {status}.")

if __name__ == "__main__":
    test_logout_flow()
