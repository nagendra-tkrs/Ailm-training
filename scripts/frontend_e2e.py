import requests
import time
import json
from datetime import date, timedelta

API = "http://localhost:5000/api"

report = []

def now_ts():
    return int(time.time())

# Helper to pretty log
def log_test(name, ok, details=None):
    entry = {"test": name, "ok": bool(ok), "details": details}
    report.append(entry)
    print(f"[{ 'PASS' if ok else 'FAIL' }] {name} - {details or ''}")

# 1) Register two users: employee and admin
unique = now_ts()
emp_email = f"e{unique}@example.com"
admin_email = f"a{unique}@example.com"
password = "P@ssw0rd!1"

def register(name, email, pwd, role="employee"):
    url = f"{API}/auth/register"
    payload = {"name": name, "email": email, "password": pwd, "role": role}
    r = requests.post(url, json=payload)
    return r

r = register("Test Employee", emp_email, password, "employee")
log_test("Register employee", r.status_code in (200,201), {"status": r.status_code, "body": r.json() if r.content else None})

r = register("Test Admin", admin_email, password, "admin")
log_test("Register admin", r.status_code in (200,201), {"status": r.status_code, "body": r.json() if r.content else None})

# 2) Login employee

def login(email, pwd):
    url = f"{API}/auth/login"
    r = requests.post(url, json={"email": email, "password": pwd})
    return r

r = login(emp_email, password)
emp_token = None
if r.ok:
    emp_token = r.json().get("access_token")
log_test("Employee login", emp_token is not None, {"status": r.status_code, "body": r.json() if r.content else None})

# 3) Login admin
r = login(admin_email, password)
admin_token = None
if r.ok:
    admin_token = r.json().get("access_token")
log_test("Admin login", admin_token is not None, {"status": r.status_code, "body": r.json() if r.content else None})

# 4) Employee: get dashboard
headers = {"Authorization": f"Bearer {emp_token}"} if emp_token else {}
try:
    r = requests.get(f"{API}/employee/dashboard", headers=headers)
    ok = r.status_code == 200
    log_test("Employee dashboard", ok, {"status": r.status_code, "body": r.json() if r.content else None})
except Exception as e:
    log_test("Employee dashboard", False, str(e))

# 5) Employee: apply leave
start = date.today() + timedelta(days=2)
end = start + timedelta(days=1)
apply_payload = {
    "leaveType": "Casual Leave",  # frontend sends display names ("Casual Leave")
    "startDate": start.isoformat(),
    "endDate": end.isoformat(),
    "leaveDays": 2,
    "reason": "E2E test leave"
}
try:
    r = requests.post(f"{API}/leave", json=apply_payload, headers=headers)
    ok = r.status_code in (200,201)
    body = r.json() if r.content else None
    log_test("Apply leave (employee)", ok, {"status": r.status_code, "body": body})
    leave_id = None
    if ok and body and "leave" in body:
        leave_id = body["leave"].get("id")
    else:
        # Try to find via my leaves
        leave_id = None
except Exception as e:
    log_test("Apply leave (employee)", False, str(e))
    leave_id = None

# 6) If leave not returned directly, fetch my leaves to find it
if not leave_id and emp_token:
    try:
        r = requests.get(f"{API}/leave/my", headers=headers)
        items = r.json().get("leaves", [])
        found = [l for l in items if l.get("reason") == "E2E test leave"]
        if found:
            leave_id = found[0].get("id")
        log_test("Find applied leave in my list", bool(found), {"count": len(found)})
    except Exception as e:
        log_test("Find applied leave in my list", False, str(e))

# 7) Admin: list all pending leaves and approve the leave
if admin_token and leave_id:
    ah = {"Authorization": f"Bearer {admin_token}"}
    try:
        r = requests.put(f"{API}/leave/{leave_id}/approve", headers=ah)
        ok = r.status_code == 200
        log_test("Admin approve leave", ok, {"status": r.status_code, "body": r.json() if r.content else None})
    except Exception as e:
        log_test("Admin approve leave", False, str(e))
else:
    log_test("Admin approve leave", False, "No admin token or leave id")

# 8) Employee: verify leave status updated
if emp_token and leave_id:
    try:
        r = requests.get(f"{API}/leave/my", headers=headers)
        items = r.json().get("leaves", [])
        target = next((l for l in items if l.get("id") == leave_id), None)
        ok = target and target.get("status") in ("approved", "approved")
        log_test("Employee sees approved leave", ok, {"status": r.status_code, "leave": target})
    except Exception as e:
        log_test("Employee sees approved leave", False, str(e))

# 9) Employee: profile get & update
if emp_token:
    try:
        r = requests.get(f"{API}/profile", headers=headers)
        profile = r.json()
        log_test("Get profile", r.status_code==200, {"profile": profile})

        # Update name briefly
        new_name = profile.get("name", "") + " E2E"
        upd = {"name": new_name, "email": profile.get("email"), "address": profile.get("address"), "phone_number": profile.get("phone_number")}
        r2 = requests.put(f"{API}/profile", json=upd, headers=headers)
        ok = r2.status_code == 200
        log_test("Update profile", ok, {"status": r2.status_code, "body": r2.json() if r2.content else None})
    except Exception as e:
        log_test("Profile tests", False, str(e))

# 10) Cleanup: admin reject/delete demonstration - attempt to delete via employee (should fail for approved)
if emp_token and leave_id:
    try:
        r = requests.delete(f"{API}/leaves/{leave_id}", headers=headers)
        # If approved, delete should fail; expect 400 or 403
        ok = (r.status_code >= 400)
        log_test("Attempt employee delete approved leave (should fail)", ok, {"status": r.status_code, "body": r.json() if r.content else None})
    except Exception as e:
        log_test("Attempt employee delete approved leave (should fail)", False, str(e))

# Save report
with open("frontend_e2e_report.json", "w") as f:
    json.dump(report, f, indent=2)

print("\nE2E script completed. Report saved to frontend_e2e_report.json")
