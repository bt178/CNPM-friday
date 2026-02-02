import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000/api/v1"

def make_request(endpoint, data=None):
    url = f"{BASE_URL}/{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    try:
        if data:
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
        else:
            req = urllib.request.Request(url, headers=headers, method='POST')
            
        with urllib.request.urlopen(req) as response:
            return response.status, response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return 0, str(e)

def register(email, password, role_id, full_name):
    payload = {
        "email": email,
        "password": password,
        "role_id": role_id,
        "full_name": full_name
    }
    status, response = make_request("auth/register", payload)
    
    if status == 201:
        print(f"[SUCCESS] Created {full_name} ({email})")
    elif status == 400 and "already exists" in response:
         print(f"[INFO] User {email} already exists")
    else:
        print(f"[ERROR] Failed to create {email}: {status} - {response}")

def init_db():
    print("--- Initializing DB tables and roles ---")
    status, response = make_request("admin/init-db")
    if status == 200:
        print(f"Init DB response: {response}")
    else:
        print(f"Init DB failed: {status} - {response}")

if __name__ == "__main__":
    # 1. Init DB (ensure tables exist)
    init_db()
    
    # 2. Create Users
    print("\n--- Seeding Users ---")
    # Role IDs: 1=Admin, 4=Lecturer, 5=Student (based on api.py)
    register("admin@example.com", "password", 1, "Admin User")
    register("lecturer@example.com", "password", 4, "Dr. Lecturer")
    register("student1@example.com", "password", 5, "Student One")
    register("student2@example.com", "password", 5, "Student Two")
    register("head@example.com", "password", 3, "Head of Dept")
    
    print("\n[DONE] You can now login with password: 'password'")
