import urllib.request
import json
import time

time.sleep(1)

def request_json(url, method="GET", data=None, token=None):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        res = urllib.request.urlopen(req)
        return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

print("=== VERIFYING JWT AUTHENTICATION API ===")

# 1. Login with demo account
status, res = request_json(
    "http://127.0.0.1:8000/api/v1/auth/login",
    method="POST",
    data={"email": "engineer@oilindia.in", "password": "OilIndia@2026"}
)
print(f"[1] POST /api/v1/auth/login -> HTTP {status}")
assert status == 200, f"Login failed: {res}"
token = res["access_token"]
user = res["user"]
print(f"    Authenticated User: {user['full_name']} ({user['role']}) - Field: {user['asset_field']}")
print(f"    JWT Token (length {len(token)}): {token[:25]}...{token[-15:]}")

# 2. Get profile with Bearer Token
status, res = request_json(
    "http://127.0.0.1:8000/api/v1/auth/me",
    method="GET",
    token=token
)
print(f"[2] GET /api/v1/auth/me (with Bearer Token) -> HTTP {status}")
assert status == 200, f"Get /me failed: {res}"
print(f"    Verified Profile: {res['email']} | {res['full_name']}")

# 3. Test register new account
new_email = f"operator_{int(time.time())}@oilindia.in"
status, res = request_json(
    "http://127.0.0.1:8000/api/v1/auth/register",
    method="POST",
    data={
        "email": new_email,
        "password": "Password@123",
        "full_name": "R. K. Hazarika",
        "role": "Assistant Drilling Engineer",
        "asset_field": "Moran Field"
    }
)
print(f"[3] POST /api/v1/auth/register -> HTTP {status}")
assert status == 201, f"Registration failed: {res}"
print(f"    Registered & Issued Token for: {res['user']['email']}")

# 4. Test unauthorized request with invalid token
status, res = request_json(
    "http://127.0.0.1:8000/api/v1/auth/me",
    method="GET",
    token="invalid-tampered-token-123"
)
print(f"[4] GET /api/v1/auth/me (with tampered token) -> HTTP {status} (Expected 401)")
assert status == 401, f"Expected 401 for bad token, got {status}"

# 5. Access secured nearby wells endpoint with token
status, res = request_json(
    "http://127.0.0.1:8000/api/v1/wells/nearby?latitude=27.2891&longitude=95.3524&radius_km=10",
    method="GET",
    token=token
)
print(f"[5] GET /api/v1/wells/nearby (with Bearer token) -> HTTP {status}")
assert status == 200, f"Nearby failed: {res}"
print(f"    Offset wells found: {res['total_found']}")

print("\nALL BACKEND JWT AUTHENTICATION TESTS PASSED SUCCESSFULLY!")
