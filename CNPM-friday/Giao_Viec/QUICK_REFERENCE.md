# 🎯 QUICK COMMAND REFERENCE

## 🚀 Backend Startup

```bash
# Start Docker (recommended)
docker-compose up

# OR start local Python
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Check if running
curl http://localhost:8000/api/v1/admin/db-status
```

## 🔧 Database

```bash
# Initialize (creates tables + seeds 5 roles)
curl -X POST http://localhost:8000/api/v1/admin/init-db

# Check status
curl http://localhost:8000/api/v1/admin/db-status

# Query directly
docker-compose exec db psql -U collabsphere -d collabsphere_db
SELECT * FROM roles;
\q  # Exit
```

## 🔐 Authentication

```bash
# Register Lecturer
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "lecturer@example.com", "password": "password123", "role_id": 4, "full_name": "Dr. Lecturer"}'

# Register Student
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "student@example.com", "password": "password123", "role_id": 5, "full_name": "Student One"}'

# Login (get token)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=lecturer@example.com&password=password123&grant_type=password"

# Save token for later
export TOKEN="eyJhbGc..."

# Use token in API calls
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

## 📝 Topics Endpoints

```bash
# Create (Lecturer only, role_id=4)
curl -X POST http://localhost:8000/api/v1/topics \
  -H "Authorization: Bearer $LECTURER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "AI Project", "description": "Build AI chatbot"}'

# List (Students see APPROVED only)
curl http://localhost:8000/api/v1/topics \
  -H "Authorization: Bearer $TOKEN"

# Get detail
curl http://localhost:8000/api/v1/topics/1 \
  -H "Authorization: Bearer $TOKEN"

# Approve (Admin only, role_id=1)
curl -X PATCH http://localhost:8000/api/v1/topics/1/approve \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Reject
curl -X PATCH http://localhost:8000/api/v1/topics/1/reject \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Create evaluation
curl -X POST http://localhost:8000/api/v1/topics/evaluations/1 \
  -H "Authorization: Bearer $LECTURER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"team_id": 1, "project_id": 1, "score": 8.5, "feedback": "Great work"}'
```

## 👥 Teams Endpoints

```bash
# Create (Student only, role_id=5)
curl -X POST http://localhost:8000/api/v1/teams \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Team A", "project_id": 1}'
# Response includes join_code

# List
curl http://localhost:8000/api/v1/teams \
  -H "Authorization: Bearer $TOKEN"

# Get detail (with members)
curl http://localhost:8000/api/v1/teams/1 \
  -H "Authorization: Bearer $TOKEN"

# Join (Student only)
curl -X POST "http://localhost:8000/api/v1/teams/1/join?join_code=A1B2C3" \
  -H "Authorization: Bearer $TOKEN"

# Leave
curl -X POST http://localhost:8000/api/v1/teams/1/leave \
  -H "Authorization: Bearer $TOKEN"

# Finalize (Lecturer only, role_id=4)
curl -X PATCH http://localhost:8000/api/v1/teams/1/finalize \
  -H "Authorization: Bearer $LECTURER_TOKEN"
```

## 📋 Tasks Endpoints

```bash
# Create sprint
curl -X POST "http://localhost:8000/api/v1/tasks/sprints?team_id=1&name=Sprint%201" \
  -H "Authorization: Bearer $TOKEN"

# Get sprint detail (with task counts)
curl http://localhost:8000/api/v1/tasks/sprints/1 \
  -H "Authorization: Bearer $TOKEN"

# Create task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Setup", "sprint_id": 1, "priority": "HIGH"}'

# List tasks (filter by sprint)
curl "http://localhost:8000/api/v1/tasks?sprint_id=1&status=TODO" \
  -H "Authorization: Bearer $TOKEN"

# Get task detail
curl http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer $TOKEN"

# Update task
curl -X PUT http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "DOING"}'

# Delete task
curl -X DELETE http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer $TOKEN"
```

## 🐛 Debugging

```bash
# Check backend logs
docker-compose logs backend | tail -50

# Watch logs in real-time
docker-compose logs -f backend

# Check specific service
docker-compose logs database

# Restart service
docker-compose restart backend

# Full restart
docker-compose down && docker-compose up

# Check if port is in use
netstat -ano | findstr :8000  # Windows PowerShell
lsof -i :8000  # macOS/Linux
```

## 📊 Testing Workflow

```bash
# Step 1: Initialize
curl -X POST http://localhost:8000/api/v1/admin/init-db

# Step 2: Create users
curl -X POST http://localhost:8000/api/v1/auth/register ...

# Step 3: Get tokens
export LECTURER_TOKEN="..."
export STUDENT_TOKEN="..."

# Step 4: Test each endpoint
curl -X POST http://localhost:8000/api/v1/topics ...
```

## 🎯 Role IDs

```
1 = Admin
2 = Staff  
3 = Head_Dept
4 = Lecturer
5 = Student
```

## 📝 Status Codes

```
201 = Created (POST successful)
200 = OK (GET, PATCH, PUT successful)
400 = Bad Request (invalid data)
401 = Unauthorized (no token or expired)
403 = Forbidden (wrong role)
404 = Not Found (resource doesn't exist)
500 = Server Error (bug in code - check logs!)
```

## 💾 Status Values

```
Topics:
  - DRAFT
  - APPROVED
  - REJECTED

Tasks:
  - TODO
  - DOING
  - DONE
  - BLOCKED
```

## 🔑 Always Remember

1. **Add Bearer token** to all requests (except login/register)
   ```bash
   -H "Authorization: Bearer $TOKEN"
   ```

2. **Use correct Content-Type**
   ```bash
   -H "Content-Type: application/json"  # For JSON
   -H "Content-Type: application/x-www-form-urlencoded"  # For login
   ```

3. **Check role_id** - some endpoints restricted:
   - Topics create: Lecturer only (4)
   - Teams create: Student only (5)
   - Approval: Admin only (1)

4. **Save IDs** for next requests:
   ```bash
   export TOPIC_ID=1
   export TEAM_ID=1
   export TASK_ID=1
   ```

## 🚀 Pro Tips

```bash
# Pretty print JSON response
curl ... | python -m json.tool

# Save response to file
curl ... > response.json

# Test with Postman instead
# Import: http://localhost:8000/openapi.json
```

## 📱 Frontend Startup

```bash
# Start dev server
cd frontend
npm run dev

# Should be at http://localhost:3000 or http://localhost:5173

# Build for production
npm run build
```

## 🔗 Important URLs

```
Backend docs: http://localhost:8000/docs
Frontend app: http://localhost:3000 or http://localhost:5173
Database: localhost:5432 (when using docker)
Redis: localhost:6379 (when using docker)
```

## 📋 Environment Variables

```bash
# Backend (.env)
DATABASE_URL=postgresql://collabsphere:collabsphere_password@localhost:5432/collabsphere_db
REDIS_URL=redis://localhost:6379/0

# Frontend (.env)
VITE_API_URL=http://localhost:8000/api/v1
```

---

**Need more help? Check TESTING_GUIDE.md for detailed testing flows.**

