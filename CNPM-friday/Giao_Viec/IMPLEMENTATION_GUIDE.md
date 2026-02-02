# 🔨 STEP-BY-STEP IMPLEMENTATION GUIDE

## BE2: Topics & Evaluation (5 hours)

### Step 1: Create Schema File (20 min)
File: `backend/app/schemas/topic.py`

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TopicCreate(BaseModel):
    title: str
    description: Optional[str] = None
    requirements: Optional[str] = None

class TopicUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class TopicResponse(BaseModel):
    topic_id: int
    title: str
    description: Optional[str]
    status: str
    created_by: str
    created_at: Optional[datetime]
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class EvaluationCreate(BaseModel):
    team_id: int
    project_id: int
    score: float
    feedback: Optional[str] = None
```

### Step 2: Create Router File (3 hours)
File: `backend/app/api/v1/topics.py`

Copy from `STARTER_BE2_TOPICS.py` - it has all endpoints!

```python
# Endpoints to implement:
# 1. POST /topics
# 2. GET /topics
# 3. GET /topics/{id}
# 4. PATCH /topics/{id}/approve
# 5. PATCH /topics/{id}/reject
# 6. POST /evaluations
# 7. GET /evaluations/{id}
```

**Testing after each endpoint:**
```bash
# POST
curl -X POST http://localhost:8000/api/v1/topics \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "AI Project", "description": "Create an AI chatbot"}'

# Should return: {"topic_id": 1, "title": "AI Project", "status": "DRAFT"}
```

### Step 3: Register Router in api.py (10 min)
File: `backend/app/api/v1/api.py`

Add these lines in the api_router setup:
```python
from app.api.v1.topics import router as topics_router
api_router.include_router(topics_router, prefix="/topics", tags=["topics"])
```

### Step 4: Test All Endpoints (1.5 hours)
Use `TESTING_GUIDE.md` → FLOW 1: Topic Creation & Approval

**Success Criteria:**
- [x] Create topic → 200, status=DRAFT
- [x] List topics → Student sees only APPROVED
- [x] Approve topic → status changes to APPROVED
- [x] Evaluate team → evaluation_id returned

---

## BE3: Teams & Join Logic (6 hours)

### Step 1: Create Schema File (20 min)
File: `backend/app/schemas/team.py`

```python
from pydantic import BaseModel
from typing import Optional

class TeamCreate(BaseModel):
    name: str
    project_id: int
    description: Optional[str] = None

class TeamMemberResponse(BaseModel):
    user_id: str
    role: str  # LEADER or MEMBER
    joined_at: Optional[str]

class TeamResponse(BaseModel):
    team_id: int
    name: str
    project_id: int
    description: Optional[str]
    join_code: Optional[str]  # None if finalized
    is_finalized: bool
    created_by: str
    member_count: Optional[int]
    
    class Config:
        from_attributes = True
```

### Step 2: Create Router File (4 hours)
File: `backend/app/api/v1/teams.py`

Copy from `STARTER_BE3_TEAMS.py`

```python
# Critical logic:
# 1. POST /teams generates join_code = secrets.token_hex(3).upper()
# 2. Auto-add creator as LEADER
# 3. POST /join validates join_code exists & team not finalized
# 4. GET /{id} includes members list
# 5. PATCH /finalize locks team
```

**⚠️ Common Pitfall:** Forgetting to flush() before commit() when you need the team_id!

```python
db.add(team)
await db.flush()  # ← Important!
team_member = TeamMember(team_id=team.team_id, ...)
db.add(team_member)
await db.commit()
```

### Step 3: Register Router (10 min)
In `api.py`:
```python
from app.api.v1.teams import router as teams_router
api_router.include_router(teams_router, prefix="/teams", tags=["teams"])
```

### Step 4: Test All Endpoints (1.5 hours)
Use `TESTING_GUIDE.md` → FLOW 2: Team Creation

**Success Criteria:**
- [x] Create team → join_code generated (e.g., "A1B2C3")
- [x] Join with code → 200, member added
- [x] Cannot join finalized team → 400 error
- [x] Get team detail → members list correct

---

## BE4: Tasks & Sprints (5 hours)

### Step 1: Create Schema File (20 min)
File: `backend/app/schemas/task.py`

```python
from pydantic import BaseModel
from typing import Optional

class TaskCreate(BaseModel):
    title: str
    sprint_id: int
    description: Optional[str] = None
    assigned_to: Optional[str] = None  # user_id
    priority: str = "MEDIUM"

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None  # TODO, DOING, DONE
    assigned_to: Optional[str] = None
    priority: Optional[str] = None

class TaskResponse(BaseModel):
    task_id: int
    title: str
    sprint_id: int
    status: str
    priority: str
    assigned_to: Optional[str]
    created_by: str
    
    class Config:
        from_attributes = True
```

### Step 2: Create Router File (3 hours)
File: `backend/app/api/v1/tasks.py`

Copy from `STARTER_BE4_TASKS.py`

```python
# Endpoints:
# 1. POST /tasks (create)
# 2. GET /tasks?sprint_id={id} (list by sprint)
# 3. GET /tasks/{id} (detail)
# 4. PUT /tasks/{id} (update - validate status!)
# 5. DELETE /tasks/{id}
# BONUS: POST /sprints, GET /sprints/{id}
```

**Important:** Status validation!
```python
valid_statuses = ["TODO", "DOING", "DONE", "BLOCKED"]
if status not in valid_statuses:
    raise HTTPException(400, detail="...")
```

### Step 3: Register Router (10 min)
In `api.py`:
```python
from app.api.v1.tasks import router as tasks_router
api_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
```

### Step 4: Test Workflow (1.5 hours)
Use `TESTING_GUIDE.md` → FLOW 3: Task Management

**Success Criteria:**
- [x] Create task → status=TODO
- [x] List tasks → filters by sprint_id
- [x] Update status → TODO→DOING→DONE valid
- [x] Invalid status → 400 error

---

## FE1: Lecturer Topics & Approval (7 hours)

### Step 1: Install Dependencies (5 min)
```bash
# Already installed: antd, axios, react-router
# Just make sure versions match package.json
```

### Step 2: Create TopicList Component (2 hours)
File: `frontend/src/pages/LecturerTopics.jsx`

Copy from `STARTER_FE1_LECTURER.jsx`

**Key Features:**
- GET `/topics` on mount
- Table with title, status, description, actions
- Create button → Modal form
- Approve/Reject buttons (POST to /approve endpoint)

### Step 3: Add Routing (30 min)
File: `frontend/src/App.jsx`

Add to your router:
```jsx
import LecturerDashboard from './pages/LecturerDashboard';

// In BrowserRouter:
<Route path="/lecturer/topics" element={<LecturerDashboard />} />
```

### Step 4: Test UI (1 hour)
```bash
# Start frontend
cd frontend
npm run dev  # http://localhost:3000

# Test:
1. Login as lecturer
2. Navigate to /lecturer/topics
3. Create a topic → form submits to POST /api/v1/topics
4. See topic in list with status DRAFT
5. (Have BE1/admin approve via API)
6. Refresh → see approved topics
```

### Step 5: Create Approval Page (2 hours)
File: `frontend/src/pages/ApproveTopics.jsx`

```jsx
// New page for HEAD_DEPT to approve topics
// GET /topics (filter status=DRAFT)
// Show in list
// Approve button → PATCH /approve
// Reject button → PATCH /reject
```

Route:
```jsx
<Route path="/admin/approve-topics" element={<ApproveTopics />} />
```

### Step 6: Styling & Polish (1.5 hours)
- Add colors to status badges (DRAFT=orange, APPROVED=green)
- Loading states on buttons
- Error message display
- Success notifications

---

## FE2: Student Dashboard & Team (7 hours)

### Step 1: Create StudentDashboard (2 hours)
File: `frontend/src/pages/StudentDashboard.jsx`

Copy from `STARTER_FE2_STUDENT.jsx`

**Components:**
- Available Topics table (GET `/topics`, filter APPROVED)
- Your Teams table (GET `/teams`)
- Buttons: Create Team, Join Team

### Step 2: Create Team Modal (1.5 hours)
```jsx
// Form fields: Team Name, Project ID, Description
// POST /api/v1/teams
// Show join_code in success message!
```

### Step 3: Join Team Modal (1 hour)
```jsx
// Form field: Join Code
// POST /api/v1/teams/join
// Validate response
```

### Step 4: Team Detail Page (2 hours)
File: `frontend/src/pages/TeamDetail.jsx`

Route: `/student/teams/{team_id}`

```jsx
// GET /teams/{team_id}
// Show:
// - Team name, description
// - Members list (with roles)
// - Join code (if you're leader & team not finalized)
// - Task list (TODO, DOING, DONE columns)
```

### Step 5: Task Board/Kanban (1 hour)
```jsx
// Simple version:
// - 3 columns: TODO | DOING | DONE
// - Each task as a card
// - Click task → dropdown to change status
// - PUT /api/v1/tasks/{id} with new status
```

Advanced:
```jsx
// Drag-drop columns (optional - can skip for now)
```

### Step 6: Polish & Test (0.5 hours)
- Loading states
- Error handling
- Responsive layout

---

## 🎯 Integration Checklist

After each component is done:

### BE Team
```
[ ] Endpoint working (tested via curl/Postman)
[ ] Correct status codes (200, 201, 400, 403, 404)
[ ] Role-based access enforced
[ ] Database records created correctly
[ ] No SQL errors in logs
[ ] Response format matches schema
[ ] Registered in api.py router
```

### FE Team
```
[ ] Component renders without errors
[ ] API calls use correct endpoint URLs
[ ] Handles loading state
[ ] Shows error messages
[ ] Success notifications work
[ ] Navigation to other pages works
[ ] No console errors (F12)
[ ] Responsive on mobile viewport
```

---

## ⏰ Time Breakdown

| Task | Person | Hours | Start | End |
|------|--------|-------|-------|-----|
| BE2 Topics | BE2 | 5h | Day1 9am | Day1 2pm |
| BE3 Teams | BE3 | 6h | Day1 9am | Day2 3pm |
| BE4 Tasks | BE4 | 5h | Day1 9am | Day1 2pm |
| FE1 Lecturer | FE1 | 7h | Day1 2pm | Day3 11am |
| FE2 Student | FE2 | 7h | Day1 2pm | Day3 11am |
| BE1 Review & Fix | BE1 | 8h | Ongoing | - |

---

## 📞 Help Resources

**Stuck on something?**

1. Check `STARTER_BE{2,3,4}.py` files - they have working code!
2. Run `TESTING_GUIDE.md` test flows
3. Check database directly:
   ```bash
   docker-compose exec db psql -U collabsphere -d collabsphere_db
   \dt  # list tables
   SELECT * FROM topics;
   ```
4. Check logs:
   ```bash
   docker-compose logs backend | tail -50
   ```
5. Ask BE1 (Leader) - response time < 1 hour

