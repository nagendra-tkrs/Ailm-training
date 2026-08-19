import requests
import time
import json
import csv
import os
from datetime import date, timedelta

API = "http://localhost:5000/api"
BASE = "http://localhost:5000"
TIMEOUT = 10

report = []
test_id = 0


def now_ts():
    return int(time.time())


def log_test(name, ok, status_code=None, body=None, notes=""):
    global test_id
    test_id += 1
    entry = {
        "test": name,
        "ok": bool(ok),
        "status_code": status_code,
        "body": body,
        "notes": notes,
    }
    report.append(entry)
    label = "PASS" if ok else "FAIL"
    print(f"[{label}] {test_id}. {name} (HTTP {status_code}) - {notes or ''}", flush=True)


def auth(token):
    return {"Authorization": f"Bearer {token}"} if token else {}


def strip_token(body):
    if not body:
        return body
    if isinstance(body, dict):
        return {k: v for k, v in body.items() if k != "access_token"}
    return body


def api_get(path, headers=None):
    return requests.get(f"{API}{path}", headers=headers, timeout=TIMEOUT)


def api_post(path, json=None, headers=None):
    return requests.post(f"{API}{path}", json=json, headers=headers, timeout=TIMEOUT)


def api_put(path, json=None, headers=None):
    return requests.put(f"{API}{path}", json=json, headers=headers, timeout=TIMEOUT)


def api_delete(path, headers=None):
    return requests.delete(f"{API}{path}", headers=headers, timeout=TIMEOUT)


def base_get(path):
    return requests.get(f"{BASE}{path}", timeout=TIMEOUT)


# ===== Test Data =====

ts = now_ts()
emp_email = f"testemp{ts}@gmail.com"
emp2_email = f"testemp2{ts}@yahoo.com"
emp3_email = f"testemp3{ts}@company.com"
bad_email = f"test{ts}@hotmail.com"
password = "Test@1234"
new_password = "NewPass@12"

emp_token = None
admin_token = None
emp2_token = None
emp3_token = None
emp_id = None
admin_id = None
emp2_id = None
emp3_id = None
leave_id = None
crud_leave_id = None
emp2_leave_id = None

# ===== 1. ROOT ENDPOINTS =====

print("\n=== ROOT ENDPOINTS ===", flush=True)

for name, path in [("GET /", "/"), ("GET /health", "/health"), ("GET /db-test", "/db-test")]:
    try:
        r = base_get(path)
        log_test(name, r.status_code == 200, r.status_code, r.json() if r.content else None, "OK")
    except Exception as e:
        log_test(name, False, 0, None, str(e))

# ===== 2. REGISTRATION =====

print("\n=== AUTH: REGISTRATION ===", flush=True)

try:
    r = api_post("/auth/register", json={"name": "Test Employee", "email": emp_email, "password": password})
    ok = r.status_code in (200, 201)
    body = r.json() if r.content else None
    if ok and body and "user" in body:
        emp_id = body["user"].get("id")
    log_test("Register employee", ok, r.status_code, body, f"user_id={emp_id}")
except Exception as e:
    log_test("Register employee", False, 0, None, str(e))

try:
    r = api_post("/auth/login", json={"email": "admin@gmail.com", "password": "Admin@123"})
    ok = r.status_code == 200
    body = r.json() if r.content else None
    if ok and body:
        admin_token = body.get("access_token")
        admin_id = body.get("user", {}).get("id")
    log_test("Login seed admin", ok, r.status_code, strip_token(body), f"user_id={admin_id}")
except Exception as e:
    log_test("Login seed admin", False, 0, None, str(e))

try:
    r = api_post("/auth/register", json={"name": "Employee Two", "email": emp2_email, "password": password})
    ok = r.status_code in (200, 201)
    body = r.json() if r.content else None
    if ok and body and "user" in body:
        emp2_id = body["user"].get("id")
    log_test("Register employee 2 (yahoo)", ok, r.status_code, body, f"user_id={emp2_id}")
except Exception as e:
    log_test("Register employee 2 (yahoo)", False, 0, None, str(e))

try:
    r = api_post("/auth/register", json={"name": "Employee Three", "email": emp3_email, "password": password})
    ok = r.status_code in (200, 201)
    body = r.json() if r.content else None
    if ok and body and "user" in body:
        emp3_id = body["user"].get("id")
    log_test("Register employee 3 (company)", ok, r.status_code, body, f"user_id={emp3_id}")
except Exception as e:
    log_test("Register employee 3 (company)", False, 0, None, str(e))

validation_tests = [
    ("Register duplicate email", {"name": "Dup", "email": emp_email, "password": password}),
    ("Register invalid domain", {"name": "Bad", "email": bad_email, "password": password}),
    ("Register short password", {"name": "Short", "email": f"short{ts}@gmail.com", "password": "ab"}),
    ("Register short name", {"name": "X", "email": f"sn{ts}@gmail.com", "password": password}),
    ("Register empty name", {"name": "", "email": f"ne{ts}@gmail.com", "password": password}),
    ("Register empty body", None),
]

for name, payload in validation_tests:
    try:
        r = api_post("/auth/register", json=payload)
        log_test(f"{name} (should fail)", r.status_code >= 400, r.status_code, r.json() if r.content else None, f"Expected 4xx")
    except Exception as e:
        log_test(f"{name} (should fail)", False, 0, None, str(e))

# ===== 3. LOGIN =====

print("\n=== AUTH: LOGIN ===", flush=True)

login_success = [
    ("Employee login", emp_email, password),
    ("Employee 2 login (yahoo)", emp2_email, password),
    ("Employee 3 login (company)", emp3_email, password),
]

for name, email, pwd in login_success:
    try:
        r = api_post("/auth/login", json={"email": email, "password": pwd})
        ok = r.status_code == 200
        body = r.json() if r.content else None
        token_val = body.get("access_token") if ok and body else None
        if name == "Employee login" and token_val:
            emp_token = token_val
        elif name == "Employee 2 login (yahoo)" and token_val:
            emp2_token = token_val
        elif name == "Employee 3 login (company)" and token_val:
            emp3_token = token_val
        log_test(name, ok, r.status_code, strip_token(body), "token obtained")
    except Exception as e:
        log_test(name, False, 0, None, str(e))

login_fail = [
    ("Login wrong password", {"email": emp_email, "password": "WrongPassword"}),
    ("Login non-existent user", {"email": f"noexist{ts}@gmail.com", "password": password}),
    ("Login invalid domain", {"email": bad_email, "password": password}),
    ("Login empty body", {}),
]

for name, payload in login_fail:
    try:
        r = api_post("/auth/login", json=payload)
        log_test(f"{name} (should fail)", r.status_code >= 400, r.status_code, r.json() if r.content else None, f"Expected 4xx")
    except Exception as e:
        log_test(f"{name} (should fail)", False, 0, None, str(e))

# ===== 4. AUTH /me =====

print("\n=== AUTH: /me ===", flush=True)

try:
    r = api_get("/auth/me", headers=auth(emp_token))
    log_test("GET /auth/me (employee)", r.status_code == 200, r.status_code, r.json() if r.content else None, "User info")
except Exception as e:
    log_test("GET /auth/me (employee)", False, 0, None, str(e))

try:
    r = api_get("/auth/me", headers=auth(admin_token))
    log_test("GET /auth/me (admin)", r.status_code == 200, r.status_code, r.json() if r.content else None, "Admin info")
except Exception as e:
    log_test("GET /auth/me (admin)", False, 0, None, str(e))

for name, h in [("GET /auth/me no token", None), ("GET /auth/me bad token", {"Authorization": "Bearer badtoken"})]:
    try:
        r = api_get("/auth/me", headers=h)
        log_test(f"{name} (should fail)", r.status_code >= 400, r.status_code, r.json() if r.content else None, "Expected 401")
    except Exception as e:
        log_test(f"{name} (should fail)", False, 0, None, str(e))

# ===== 5. EMPLOYEE DASHBOARD =====

print("\n=== DASHBOARD: EMPLOYEE ===", flush=True)

try:
    r = api_get("/employee/dashboard", headers=auth(emp_token))
    log_test("GET /employee/dashboard (employee)", r.status_code == 200, r.status_code, r.json() if r.content else None, "Balances + leaves")
except Exception as e:
    log_test("GET /employee/dashboard (employee)", False, 0, None, str(e))

try:
    r = api_get("/employee/dashboard", headers=auth(admin_token))
    log_test("GET /employee/dashboard as admin (should fail)", r.status_code >= 400, r.status_code, r.json() if r.content else None, "Expected 403")
except Exception as e:
    log_test("GET /employee/dashboard as admin (should fail)", False, 0, None, str(e))

try:
    r = api_get("/employee/dashboard")
    log_test("GET /employee/dashboard no token (should fail)", r.status_code >= 400, r.status_code, r.json() if r.content else None, "Expected 401")
except Exception as e:
    log_test("GET /employee/dashboard no token (should fail)", False, 0, None, str(e))

# ===== 6. ADMIN DASHBOARD =====

print("\n=== DASHBOARD: ADMIN ===", flush=True)

try:
    r = api_get("/admin/dashboard", headers=auth(admin_token))
    log_test("GET /admin/dashboard (admin)", r.status_code == 200, r.status_code, r.json() if r.content else None, "Admin summary")
except Exception as e:
    log_test("GET /admin/dashboard (admin)", False, 0, None, str(e))

try:
    r = api_get("/admin/dashboard", headers=auth(emp_token))
    log_test("GET /admin/dashboard as employee (should fail)", r.status_code >= 400, r.status_code, r.json() if r.content else None, "Expected 403")
except Exception as e:
    log_test("GET /admin/dashboard as employee (should fail)", False, 0, None, str(e))

try:
    r = api_get("/admin/dashboard")
    log_test("GET /admin/dashboard no token (should fail)", r.status_code >= 400, r.status_code, r.json() if r.content else None, "Expected 401")
except Exception as e:
    log_test("GET /admin/dashboard no token (should fail)", False, 0, None, str(e))

# ===== 7. APPLY LEAVE =====

print("\n=== LEAVES: APPLY ===", flush=True)

start = date.today() + timedelta(days=10)
end = start + timedelta(days=1)

try:
    r = api_post("/leave", json={
        "leaveType": "CASUAL", "startDate": start.isoformat(),
        "endDate": end.isoformat(), "leaveDays": 2, "reason": "E2E test leave"
    }, headers=auth(emp_token))
    ok = r.status_code in (200, 201)
    body = r.json() if r.content else None
    if ok and body and "leave" in body:
        leave_id = body["leave"].get("id")
    log_test("Apply leave (employee)", ok, r.status_code, body, f"leave_id={leave_id}")
except Exception as e:
    log_test("Apply leave (employee)", False, 0, None, str(e))

try:
    r = api_post("/leave", json={
        "leaveType": "SICK", "startDate": (date.today() + timedelta(days=20)).isoformat(),
        "endDate": (date.today() + timedelta(days=21)).isoformat(), "leaveDays": 2, "reason": "Employee 2 sick leave"
    }, headers=auth(emp2_token))
    ok = r.status_code in (200, 201)
    body = r.json() if r.content else None
    if ok and body and "leave" in body:
        emp2_leave_id = body["leave"].get("id")
    log_test("Apply leave (employee 2)", ok, r.status_code, body, f"leave_id={emp2_leave_id}")
except Exception as e:
    log_test("Apply leave (employee 2)", False, 0, None, str(e))

leave_fail = [
    ("Apply leave invalid type", {"leaveType": "INVALID", "startDate": start.isoformat(), "endDate": end.isoformat(), "leaveDays": 2, "reason": "Bad"}),
    ("Apply leave zero days", {"leaveType": "EARNED", "startDate": start.isoformat(), "endDate": end.isoformat(), "leaveDays": 0, "reason": "Zero"}),
    ("Apply leave empty body", {}),
]

for name, payload in leave_fail:
    try:
        r = api_post("/leave", json=payload, headers=auth(emp_token))
        log_test(f"{name} (should fail)", r.status_code >= 400, r.status_code, r.json() if r.content else None, "Expected 4xx")
    except Exception as e:
        log_test(f"{name} (should fail)", False, 0, None, str(e))

try:
    r = api_post("/leave", json={"leaveType": "SICK", "startDate": start.isoformat(), "endDate": end.isoformat(), "leaveDays": 2, "reason": "No auth"})
    log_test("Apply leave no token (should fail)", r.status_code >= 400, r.status_code, r.json() if r.content else None, "Expected 401")
except Exception as e:
    log_test("Apply leave no token (should fail)", False, 0, None, str(e))

# ===== 8. MY LEAVES =====

print("\n=== LEAVES: MY ===", flush=True)

try:
    r = api_get("/leave/my", headers=auth(emp_token))
    log_test("GET /leave/my (employee)", r.status_code == 200, r.status_code, r.json() if r.content else None, "My leaves")
except Exception as e:
    log_test("GET /leave/my (employee)", False, 0, None, str(e))

try:
    r = api_get("/leave/my")
    log_test("GET /leave/my no token (should fail)", r.status_code >= 400, r.status_code, r.json() if r.content else None, "Expected 401")
except Exception as e:
    log_test("GET /leave/my no token (should fail)", False, 0, None, str(e))

# ===== 9. LEAVES CRUD =====

print("\n=== LEAVES CRUD ===", flush=True)

try:
    r = api_post("/leaves", json={
        "leave_type": "EARNED", "start_date": (date.today() + timedelta(days=30)).isoformat(),
        "end_date": (date.today() + timedelta(days=31)).isoformat(), "reason": "CRUD test leave"
    }, headers=auth(emp_token))
    ok = r.status_code in (200, 201)
    body = r.json() if r.content else None
    if ok and body:
        crud_leave_id = body.get("id") or (body.get("leave", {}) or {}).get("id")
    log_test("POST /leaves (create)", ok, r.status_code, body, f"leave_id={crud_leave_id}")
except Exception as e:
    log_test("POST /leaves (create)", False, 0, None, str(e))

try:
    r = api_get("/leaves", headers=auth(emp_token))
    log_test("GET /leaves (list)", r.status_code == 200, r.status_code, r.json() if r.content else None, "List leaves")
except Exception as e:
    log_test("GET /leaves (list)", False, 0, None, str(e))

if crud_leave_id:
    try:
        r = api_put(f"/leaves/{crud_leave_id}", json={
            "leave_type": "SICK", "start_date": (date.today() + timedelta(days=32)).isoformat(),
            "end_date": (date.today() + timedelta(days=33)).isoformat(), "reason": "Updated CRUD leave"
        }, headers=auth(emp_token))
        log_test(f"PUT /leaves/{crud_leave_id} (update)", r.status_code == 200, r.status_code, r.json() if r.content else None, "Updated")
    except Exception as e:
        log_test(f"PUT /leaves/{crud_leave_id} (update)", False, 0, None, str(e))

# ===== 10. ADMIN: ALL LEAVES =====

print("\n=== LEAVES: ALL (admin) ===", flush=True)

try:
    r = api_get("/leave/all", headers=auth(admin_token))
    log_test("GET /leave/all (admin)", r.status_code == 200, r.status_code, r.json() if r.content else None, "All leaves")
except Exception as e:
    log_test("GET /leave/all (admin)", False, 0, None, str(e))

try:
    r = api_get("/leave/all?status=pending", headers=auth(admin_token))
    log_test("GET /leave/all?status=pending", r.status_code == 200, r.status_code, None, "Filtered")
except Exception as e:
    log_test("GET /leave/all?status=pending", False, 0, None, str(e))

try:
    r = api_get("/leave/all?status=approved", headers=auth(admin_token))
    log_test("GET /leave/all?status=approved", r.status_code == 200, r.status_code, None, "Filtered")
except Exception as e:
    log_test("GET /leave/all?status=approved", False, 0, None, str(e))

try:
    r = api_get("/leave/all", headers=auth(emp_token))
    log_test("GET /leave/all as employee (should fail)", r.status_code >= 400, r.status_code, r.json() if r.content else None, "Expected 403")
except Exception as e:
    log_test("GET /leave/all as employee (should fail)", False, 0, None, str(e))

# ===== 11. APPROVE / REJECT =====

print("\n=== LEAVES: APPROVE / REJECT ===", flush=True)

if leave_id:
    try:
        r = api_put(f"/leave/{leave_id}/approve", headers=auth(admin_token))
        log_test(f"Admin approve leave {leave_id}", r.status_code == 200, r.status_code, r.json() if r.content else None, "Approved")
    except Exception as e:
        log_test("Admin approve leave", False, 0, None, str(e))

    try:
        r = api_put(f"/leave/{leave_id}/approve", headers=auth(emp_token))
        log_test("Employee approve (should fail)", r.status_code >= 400, r.status_code, r.json() if r.content else None, "Expected 403")
    except Exception as e:
        log_test("Employee approve (should fail)", False, 0, None, str(e))
else:
    log_test("Admin approve leave", False, 0, None, "No leave_id")

try:
    r = api_put("/leave/99999/approve", headers=auth(admin_token))
    log_test("Approve non-existent (should fail)", r.status_code >= 400, r.status_code, r.json() if r.content else None, "Expected 404")
except Exception as e:
    log_test("Approve non-existent (should fail)", False, 0, None, str(e))

if emp2_leave_id:
    try:
        r = api_put(f"/leave/{emp2_leave_id}/reject", headers=auth(admin_token))
        log_test(f"Admin reject leave {emp2_leave_id}", r.status_code == 200, r.status_code, r.json() if r.content else None, "Rejected")
    except Exception as e:
        log_test("Admin reject leave", False, 0, None, str(e))
else:
    log_test("Admin reject leave", False, 0, None, "No emp2_leave_id")

# ===== 12. VERIFY STATUS =====

print("\n=== LEAVES: VERIFY STATUS ===", flush=True)

if emp_token and leave_id:
    try:
        r = api_get("/leave/my", headers=auth(emp_token))
        items = r.json().get("leaves", []) if r.status_code == 200 else []
        target = next((l for l in items if l.get("id") == leave_id), None)
        ok = target and target.get("status") in ("approved", "APPROVED")
        log_test("Employee sees approved leave", ok, r.status_code, None, f"status={target.get('status') if target else 'not found'}")
    except Exception as e:
        log_test("Employee sees approved leave", False, 0, None, str(e))

if emp2_token and emp2_leave_id:
    try:
        r = api_get("/leave/my", headers=auth(emp2_token))
        items = r.json().get("leaves", []) if r.status_code == 200 else []
        target = next((l for l in items if l.get("id") == emp2_leave_id), None)
        ok = target and target.get("status") in ("rejected", "REJECTED")
        log_test("Employee 2 sees rejected leave", ok, r.status_code, None, f"status={target.get('status') if target else 'not found'}")
    except Exception as e:
        log_test("Employee 2 sees rejected leave", False, 0, None, str(e))

# ===== 13. DELETE =====

print("\n=== LEAVES: DELETE ===", flush=True)

if crud_leave_id:
    try:
        r = api_delete(f"/leaves/{crud_leave_id}", headers=auth(emp_token))
        log_test(f"DELETE /leaves/{crud_leave_id} (own pending)", r.status_code in (200, 204), r.status_code, r.json() if r.content else None, "Deleted")
    except Exception as e:
        log_test("DELETE own pending", False, 0, None, str(e))

if leave_id:
    try:
        r = api_delete(f"/leaves/{leave_id}", headers=auth(emp_token))
        log_test("Delete approved leave (should fail)", r.status_code >= 400, r.status_code, r.json() if r.content else None, "Cannot delete approved")
    except Exception as e:
        log_test("Delete approved leave (should fail)", False, 0, None, str(e))

if emp2_leave_id:
    try:
        r = api_delete(f"/leaves/{emp2_leave_id}", headers=auth(emp_token))
        log_test("Delete other employee's leave (should fail)", r.status_code >= 400, r.status_code, r.json() if r.content else None, "Cannot delete other's")
    except Exception as e:
        log_test("Delete other's leave (should fail)", False, 0, None, str(e))

try:
    r = api_delete("/leaves/99999", headers=auth(emp_token))
    log_test("Delete non-existent (should fail)", r.status_code >= 400, r.status_code, r.json() if r.content else None, "Expected 404")
except Exception as e:
    log_test("Delete non-existent (should fail)", False, 0, None, str(e))

# ===== 14. USERS =====

print("\n=== USERS ===", flush=True)

try:
    r = api_get("/users/profile", headers=auth(emp_token))
    log_test("GET /users/profile (employee)", r.status_code == 200, r.status_code, r.json() if r.content else None, "Profile + balances")
except Exception as e:
    log_test("GET /users/profile (employee)", False, 0, None, str(e))

try:
    r = api_get("/users/profile")
    log_test("GET /users/profile no token (should fail)", r.status_code >= 400, r.status_code, None, "Expected 401")
except Exception as e:
    log_test("GET /users/profile no token (should fail)", False, 0, None, str(e))

try:
    r = api_get("/users", headers=auth(admin_token))
    body = r.json() if r.content else None
    count = len(body) if isinstance(body, list) else "N/A"
    log_test("GET /users (admin)", r.status_code == 200, r.status_code, None, f"Found {count} users")
except Exception as e:
    log_test("GET /users (admin)", False, 0, None, str(e))

try:
    r = api_get("/users", headers=auth(emp_token))
    log_test("GET /users as employee (should fail)", r.status_code >= 400, r.status_code, None, "Expected 403")
except Exception as e:
    log_test("GET /users as employee (should fail)", False, 0, None, str(e))

if emp_id:
    try:
        r = api_get(f"/users/{emp_id}", headers=auth(admin_token))
        log_test(f"GET /users/{emp_id} (admin)", r.status_code == 200, r.status_code, r.json() if r.content else None, "User detail")
    except Exception as e:
        log_test(f"GET /users/{emp_id} (admin)", False, 0, None, str(e))

try:
    r = api_get("/users/99999", headers=auth(admin_token))
    log_test("GET /users/99999 (should fail)", r.status_code >= 400, r.status_code, None, "Expected 404")
except Exception as e:
    log_test("GET /users/99999 (should fail)", False, 0, None, str(e))

if emp_id:
    try:
        r = api_get(f"/users/{emp_id}", headers=auth(emp_token))
        log_test("GET /users/{id} as employee (should fail)", r.status_code >= 400, r.status_code, None, "Expected 403")
    except Exception as e:
        log_test("GET /users/{id} as employee (should fail)", False, 0, None, str(e))

# ===== 15. PROFILE =====

print("\n=== PROFILE ===", flush=True)

profile = None
try:
    r = api_get("/profile", headers=auth(emp_token))
    ok = r.status_code == 200
    profile = r.json() if ok and r.content else None
    log_test("GET /profile (employee)", ok, r.status_code, profile, "Profile details")
except Exception as e:
    log_test("GET /profile (employee)", False, 0, None, str(e))

try:
    r = api_get("/profile", headers=auth(admin_token))
    log_test("GET /profile (admin - employee only)", r.status_code >= 400, r.status_code, r.json() if r.content else None, "Expected 403 - employee only endpoint")
except Exception as e:
    log_test("GET /profile (admin)", False, 0, None, str(e))

if profile:
    try:
        upd = {"name": profile.get("name", "Test") + " Updated", "email": profile.get("email"), "address": "123 Test St", "phone_number": "+919876543210"}
        r = api_put("/profile", json=upd, headers=auth(emp_token))
        log_test("PUT /profile (update)", r.status_code == 200, r.status_code, r.json() if r.content else None, "Updated")
    except Exception as e:
        log_test("PUT /profile (update)", False, 0, None, str(e))

profile_fail = [
    ("Update profile short name", {"name": "X", "email": emp_email}),
    ("Update profile invalid email", {"name": "Test", "email": f"bad{ts}@hotmail.com"}),
    ("Update profile missing fields", {"name": "Test"}),
]

for name, payload in profile_fail:
    try:
        r = api_put("/profile", json=payload, headers=auth(emp_token))
        log_test(f"{name} (should fail)", r.status_code >= 400, r.status_code, r.json() if r.content else None, "Expected 4xx")
    except Exception as e:
        log_test(f"{name} (should fail)", False, 0, None, str(e))

# ===== 16. CHANGE PASSWORD =====

print("\n=== PASSWORD ===", flush=True)

try:
    r = api_put("/profile/password", json={"current_password": password, "new_password": new_password}, headers=auth(emp_token))
    log_test("Change password", r.status_code == 200, r.status_code, r.json() if r.content else None, "Password changed")
except Exception as e:
    log_test("Change password", False, 0, None, str(e))

try:
    r = api_post("/auth/login", json={"email": emp_email, "password": new_password})
    ok = r.status_code == 200
    body = r.json() if r.content else None
    if ok and body:
        emp_token = body.get("access_token")
    log_test("Login with new password", ok, r.status_code, strip_token(body), "Verified")
except Exception as e:
    log_test("Login with new password", False, 0, None, str(e))

password_fail = [
    ("Wrong current password", {"current_password": "WrongOld", "new_password": "Another@1234"}),
    ("Too short new password", {"current_password": new_password, "new_password": "short"}),
]

for name, payload in password_fail:
    try:
        r = api_put("/profile/password", json=payload, headers=auth(emp_token))
        log_test(f"{name} (should fail)", r.status_code >= 400, r.status_code, r.json() if r.content else None, "Expected 4xx")
    except Exception as e:
        log_test(f"{name} (should fail)", False, 0, None, str(e))

# ===== 17. LEAVE BALANCE =====

print("\n=== LEAVE BALANCE ===", flush=True)

try:
    r = api_get("/employee/dashboard", headers=auth(emp_token))
    if r.status_code == 200:
        bal = r.json().get("leaveBalance", {})
        log_test("Leave balance check", True, r.status_code, None, f"casual={bal.get('casual')}, sick={bal.get('sick')}, earned={bal.get('earned')}")
    else:
        log_test("Leave balance check", False, r.status_code, None, "Dashboard fetch failed")
except Exception as e:
    log_test("Leave balance check", False, 0, None, str(e))

# ===== 18. ERROR HANDLING =====

print("\n=== ERROR HANDLING ===", flush=True)

try:
    r = api_get("/nonexistent")
    log_test("GET /api/nonexistent (should 404)", r.status_code == 404, r.status_code, None, "Expected 404")
except Exception as e:
    log_test("GET /api/nonexistent", False, 0, None, str(e))

# ===== 19. ROLE-BASED ACCESS CONTROL =====

print("\n=== ROLE-BASED ACCESS ===", flush=True)

emp_only = ["/employee/dashboard", "/leave/my", "/leaves", "/profile"]
admin_only = ["/leave/all", "/admin/dashboard", "/users"]

for path in emp_only:
    try:
        r = api_get(path, headers=auth(admin_token))
        log_test(f"Admin -> {path} (should fail)", r.status_code >= 400, r.status_code, None, "Role isolation")
    except Exception as e:
        log_test(f"Admin -> {path} (should fail)", False, 0, None, str(e))

for path in admin_only:
    try:
        r = api_get(path, headers=auth(emp_token))
        log_test(f"Employee -> {path} (should fail)", r.status_code >= 400, r.status_code, None, "Role isolation")
    except Exception as e:
        log_test(f"Employee -> {path} (should fail)", False, 0, None, str(e))

# ===== GENERATE REPORTS =====

print("\n=== GENERATING REPORTS ===", flush=True)

script_dir = os.path.dirname(os.path.abspath(__file__))
report_dir = os.path.join(os.path.dirname(script_dir), "reports")
os.makedirs(report_dir, exist_ok=True)

json_path = os.path.join(script_dir, "backend_e2e_report.json")
with open(json_path, "w") as f:
    json.dump(report, f, indent=2, default=str)
print(f"JSON: {json_path}", flush=True)

csv_path = os.path.join(report_dir, "backend_e2e_report.csv")
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Test ID", "Test Name", "Passed", "HTTP Status", "Short Details", "Notes"])
    for i, entry in enumerate(report, 1):
        status = "PASS" if entry["ok"] else "FAIL"
        detail = ""
        if entry.get("body"):
            if isinstance(entry["body"], str):
                detail = entry["body"][:100]
            elif isinstance(entry["body"], dict):
                detail = str({k: str(v)[:50] for k, v in list(entry["body"].items())[:3]})[:150]
            else:
                detail = str(entry["body"])[:150]
        writer.writerow([i, entry["test"], status, entry.get("status_code", ""), detail, entry.get("notes", "")])
print(f"CSV: {csv_path}", flush=True)

total = len(report)
passed = sum(1 for e in report if e["ok"])
failed = total - passed

html_path = os.path.join(report_dir, "backend_test_report.html")
html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Backend E2E Test Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
h1 {{ color: #333; }}
.summary {{ background: #fff; padding: 15px 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
.summary span {{ margin-right: 20px; font-size: 18px; }}
.pass {{ color: #2e7d32; font-weight: bold; }}
.fail {{ color: #c62828; font-weight: bold; }}
.total {{ color: #1565c0; font-weight: bold; }}
table {{ border-collapse: collapse; width: 100%; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
th {{ background: #1565c0; color: white; padding: 12px 15px; text-align: left; }}
td {{ padding: 10px 15px; border-bottom: 1px solid #eee; }}
tr:hover {{ background: #f0f7ff; }}
.pass-row {{ color: #2e7d32; }}
.fail-row {{ color: #c62828; font-weight: bold; }}
</style></head><body>
<h1>Backend E2E Test Report</h1>
<div class="summary">
  <span class="total">Total: {total}</span>
  <span class="pass">Passed: {passed}</span>
  <span class="fail">Failed: {failed}</span>
  <span>Generated: {date.today().isoformat()}</span>
</div>
<table><tr><th>#</th><th>Test Name</th><th>Status</th><th>HTTP</th><th>Notes</th></tr>
"""

for i, entry in enumerate(report, 1):
    cls = "pass-row" if entry["ok"] else "fail-row"
    status = "PASS" if entry["ok"] else "FAIL"
    html += f'<tr class="{cls}"><td>{i}</td><td>{entry["test"]}</td><td>{status}</td><td>{entry.get("status_code", "")}</td><td>{entry.get("notes", "")}</td></tr>\n'

html += "</table></body></html>"
with open(html_path, "w") as f:
    f.write(html)
print(f"HTML: {html_path}", flush=True)

# ===== SUMMARY =====

print(f"\n{'='*60}", flush=True)
print(f"BACKEND E2E TEST SUMMARY", flush=True)
print(f"{'='*60}", flush=True)
print(f"Total:  {total}", flush=True)
print(f"Passed: {passed}", flush=True)
print(f"Failed: {failed}", flush=True)
print(f"Rate:   {passed/total*100:.1f}%" if total > 0 else "Rate: N/A", flush=True)
print(f"{'='*60}", flush=True)
