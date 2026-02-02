# 🧪 DETAILED API TESTING GUIDE

## Pre-requisites

1. Backend running: `docker-compose up` or `uvicorn app.main:app --reload`
2. PowerShell or bash terminal
3. Postman (optional, for GUI testing)

---

## 🔄 Complete Testing Flow

### Phase 1: User Setup (5 min)

**1.1 Initialize Database**
```bash
curl -X POST http://localhost:8000/api/v1/admin/init-db
```

Expected response:
```json
{
  "message": "Database initialized successfully",
  "tables_created": [
    "roles", "users", "topics", "teams", "sprints", "tasks", ...
  ],
  "roles_created": 5
}
```

**1.2 Create Users**

Create a Lecturer:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lecturer@example.com",
    "password": "password123",
    "role_id": 4,
    "full_name": "Dr. Lecturer"
  }'
```

Create Admin:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "password123",
    "role_id": 1,
    "full_name": "Admin User"
  }'
```

Create Student 1:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student1@example.com",
    "password": "password123",
    "role_id": 5,
    "full_name": "Student One"
  }'
```

Create Student 2:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student2@example.com",
    "password": "password123",
    "role_id": 5,
    "full_name": "Student Two"
  }'
```

---

### Phase 2: Get Authentication Tokens (5 min)

**2.1 Login Lecturer**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=lecturer@example.com&password=password123&grant_type=password"
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

Save token:
```bash
export LECTURER_TOKEN="eyJhbGc..."
```

**2.2 Login Admin**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=password123&grant_type=password"

export ADMIN_TOKEN="eyJhbGc..."
```

**2.3 Login Students**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student1@example.com&password=password123&grant_type=password"

export STUDENT1_TOKEN="eyJhbGc..."

curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student2@example.com&password=password123&grant_type=password"

export STUDENT2_TOKEN="eyJhbGc..."
```

---

## ✅ Flow 1: Topic Lifecycle (15 min)

### Step 1: Lecturer Creates Topic

```bash
curl -X POST http://localhost:8000/api/v1/topics \
  -H "Authorization: Bearer $LECTURER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Chatbot Project",
    "description": "Build an AI-powered chatbot using NLP",
    "requirements": "Python 3.9+, Basic ML knowledge"
  }'
```

✅ Expected:
- Status: 201 Created
- Response includes: `topic_id`, `status: "DRAFT"`, `created_by: "Dr. Lecturer"`

Save topic_id:
```bash
export TOPIC_ID=1
```

### Step 2: Student Tries to View Topic (Should be Hidden)

```bash
curl http://localhost:8000/api/v1/topics \
  -H "Authorization: Bearer $STUDENT1_TOKEN"
```

✅ Expected:
- Status: 200 OK
- `topics: []` (empty - students can only see APPROVED)

### Step 3: Admin Approves Topic

```bash
curl -X PATCH http://localhost:8000/api/v1/topics/$TOPIC_ID/approve \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

✅ Expected:
- Status: 200 OK
- Response: `status: "APPROVED"`, `approved_by: "Admin User"`

### Step 4: Student Can Now See Topic

```bash
curl http://localhost:8000/api/v1/topics \
  -H "Authorization: Bearer $STUDENT1_TOKEN"
```

✅ Expected:
- Status: 200 OK
- Response includes topic with `status: "APPROVED"`

### Step 5: Get Topic Details

```bash
curl http://localhost:8000/api/v1/topics/$TOPIC_ID \
  -H "Authorization: Bearer $STUDENT1_TOKEN"
```

✅ Expected:
- Status: 200 OK
- Full topic details with description, requirements, etc.

---

## ✅ Flow 2: Team Formation (20 min)

### Step 1: Student 1 Creates Team

```bash
curl -X POST http://localhost:8000/api/v1/teams \
  -H "Authorization: Bearer $STUDENT1_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Team Alpha",
    "project_id": 1,
    "description": "A team to build the AI chatbot"
  }'
```

✅ Expected:
- Status: 201 Created
- Response includes: `team_id`, `join_code: "A1B2C3"` (6-char hex), `member_count: 1`

Save:
```bash
export TEAM_ID=1
export JOIN_CODE="A1B2C3"
```

### Step 2: Get All Teams

```bash
curl http://localhost:8000/api/v1/teams \
  -H "Authorization: Bearer $STUDENT1_TOKEN"
```

✅ Expected:
- Status: 200 OK
- Response lists all teams with member counts

### Step 3: Student 2 Joins Team

```bash
curl -X POST "http://localhost:8000/api/v1/teams/$TEAM_ID/join?join_code=$JOIN_CODE" \
  -H "Authorization: Bearer $STUDENT2_TOKEN"
```

✅ Expected:
- Status: 200 OK
- Response: `message: "Successfully joined team"`, `role: "MEMBER"`

### Step 4: Verify Team Members

```bash
curl http://localhost:8000/api/v1/teams/$TEAM_ID \
  -H "Authorization: Bearer $STUDENT1_TOKEN"
```

✅ Expected:
- Status: 200 OK
- `members` array with 2 items:
  - Student 1 with role: "LEADER"
  - Student 2 with role: "MEMBER"

### Step 5: Lecturer Finalizes Team

```bash
curl -X PATCH http://localhost:8000/api/v1/teams/$TEAM_ID/finalize \
  -H "Authorization: Bearer $LECTURER_TOKEN"
```

✅ Expected:
- Status: 200 OK
- Response: `is_finalized: true`

### Step 6: Verify No More Members Can Join

```bash
# Try to join with correct code but team is finalized
curl -X POST "http://localhost:8000/api/v1/teams/$TEAM_ID/join?join_code=$JOIN_CODE" \
  -H "Authorization: Bearer $STUDENT2_TOKEN"
```

❌ Expected Error:
- Status: 400 Bad Request
- Message: "Team is finalized and cannot accept new members"

---

## ✅ Flow 3: Task Management (15 min)

### Step 1: Create Sprint

```bash
curl -X POST "http://localhost:8000/api/v1/tasks/sprints?team_id=$TEAM_ID&name=Sprint%201&start_date=2026-01-28&end_date=2026-02-04" \
  -H "Authorization: Bearer $STUDENT1_TOKEN"
```

✅ Expected:
- Status: 201 Created
- Response: `sprint_id`, `team_id`, `name: "Sprint 1"`

Save:
```bash
export SPRINT_ID=1
```

### Step 2: Create Tasks

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $STUDENT1_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Setup project structure",
    "sprint_id": '$SPRINT_ID',
    "description": "Create folder structure",
    "priority": "HIGH"
  }'
```

✅ Expected:
- Status: 201 Created
- Response: `task_id`, `status: "TODO"`

Save:
```bash
export TASK_ID=1
```

### Step 3: Get Tasks in Sprint

```bash
curl "http://localhost:8000/api/v1/tasks?sprint_id=$SPRINT_ID" \
  -H "Authorization: Bearer $STUDENT1_TOKEN"
```

✅ Expected:
- Status: 200 OK
- Response lists all tasks in sprint

### Step 4: Update Task Status

```bash
curl -X PUT http://localhost:8000/api/v1/tasks/$TASK_ID \
  -H "Authorization: Bearer $STUDENT1_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "DOING"
  }'
```

✅ Expected:
- Status: 200 OK
- Response: `status: "DOING"`, `updated_at` timestamp

### Step 5: Mark Task as Done

```bash
curl -X PUT http://localhost:8000/api/v1/tasks/$TASK_ID \
  -H "Authorization: Bearer $STUDENT1_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "DONE"
  }'
```

✅ Expected:
- Status: 200 OK
- Response: `status: "DONE"`

### Step 6: Get Sprint Summary

```bash
curl http://localhost:8000/api/v1/tasks/sprints/$SPRINT_ID \
  -H "Authorization: Bearer $STUDENT1_TOKEN"
```

✅ Expected:
- Status: 200 OK
- Response includes `task_counts: { "TODO": 0, "DOING": 0, "DONE": 1, "BLOCKED": 0 }`

---

## ⚠️ Error Testing

### Test Invalid Status
```bash
curl -X PUT http://localhost:8000/api/v1/tasks/$TASK_ID \
  -H "Authorization: Bearer $STUDENT1_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "INVALID"
  }'
```

❌ Expected:
- Status: 400 Bad Request
- Message: "Status must be one of: TODO, DOING, DONE, BLOCKED"

### Test Unauthorized Access
```bash
curl http://localhost:8000/api/v1/topics/$TOPIC_ID \
  -H "Authorization: Bearer INVALID_TOKEN"
```

❌ Expected:
- Status: 401 Unauthorized
- Message: "Not authenticated"

### Test Permission Denied
```bash
# Student trying to approve topic (only admin can)
curl -X PATCH http://localhost:8000/api/v1/topics/$TOPIC_ID/approve \
  -H "Authorization: Bearer $STUDENT1_TOKEN"
```

❌ Expected:
- Status: 403 Forbidden
- Message: "Only admins or heads of department can approve topics"

---

## 📊 Response Status Codes Checklist

**2xx Success:**
- [x] 200 OK - GET, Update successful
- [x] 201 Created - POST successful

**4xx Client Errors:**
- [x] 400 Bad Request - Invalid data (e.g., invalid status)
- [x] 401 Unauthorized - Missing/invalid token
- [x] 403 Forbidden - Insufficient permissions
- [x] 404 Not Found - Resource doesn't exist

**5xx Server Errors:**
- [ ] 500 Internal Server Error - If any occur, check logs!

---

## 🐛 Debugging Checklist

If tests fail, check:

1. **Is backend running?**
   ```bash
   curl http://localhost:8000/api/v1/admin/db-status
   ```

2. **Check logs:**
   ```bash
   docker-compose logs backend | tail -50
   ```

3. **Is token valid?**
   ```bash
   echo $LECTURER_TOKEN
   ```

4. **Is database initialized?**
   ```bash
   curl http://localhost:8000/api/v1/admin/db-status
   # Should show roles_count: 5
   ```

5. **Check database directly:**
   ```bash
   docker-compose exec db psql -U collabsphere -d collabsphere_db
   \dt  # List tables
   SELECT * FROM users LIMIT 1;  # Check users exist
   ```

---

## 📝 Test Results Template

Copy this for daily testing:

```
Date: [2026-01-28]
Tester: [Name]

Flow 1 - Topics: [ ] PASS [ ] FAIL
  - Create topic: [ ] PASS
  - View as student (hidden): [ ] PASS
  - Admin approves: [ ] PASS
  - View as student (visible): [ ] PASS
  
Flow 2 - Teams: [ ] PASS [ ] FAIL
  - Create team: [ ] PASS
  - Join team: [ ] PASS
  - Get team members: [ ] PASS
  - Finalize team: [ ] PASS
  - Verify locked: [ ] PASS
  
Flow 3 - Tasks: [ ] PASS [ ] FAIL
  - Create sprint: [ ] PASS
  - Create task: [ ] PASS
  - Update task status: [ ] PASS
  - Get sprint summary: [ ] PASS

ISSUES FOUND:
[List any failures here]

ACTIONS TAKEN:
[What was fixed]
```

