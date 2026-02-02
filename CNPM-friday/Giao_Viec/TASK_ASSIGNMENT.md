# 👥 TASK ASSIGNMENT - Week 1 (Jan 28 - Feb 4)

## 📋 Team Structure

| Role | Name | Tasks | Hours |
|------|------|-------|-------|
| **BE1** | Backend Lead | Code review, testing, bug fixes, database checks | 40h |
| **BE2** | Backend Dev 2 | Topics & Evaluation endpoints | 5h |
| **BE3** | Backend Dev 3 | Teams & Join logic endpoints | 6h |
| **BE4** | Backend Dev 4 | Tasks & Sprints endpoints | 5h |
| **FE1** | Frontend Dev 1 | Lecturer topics UI + approval page | 7h |
| **FE2** | Frontend Dev 2 | Student dashboard + team management | 7h |

**Total: 70 hours for 6 people = ~11.6 hours/person/week (reasonable for crunch)**

---

## 🔴 BE1: Backend Lead - Code Review & Integration

### Responsibilities
- Daily code reviews for BE2/3/4 (max 1 hour response time)
- Database integrity checks (cascade deletes, orphaned records)
- Bug fixes and debugging
- Testing the full integration daily
- Unblock team when issues arise

### Daily Workflow
- **9:00 AM** (30 min): Standup with team
  - What was completed yesterday?
  - What blockers exist?
  - What's the plan today?
  
- **10:00 AM - 1:00 PM** (3h): Code review
  - Review PRs from BE2, BE3, BE4
  - Check database queries for N+1 problems
  - Verify error handling
  
- **2:00 PM - 5:00 PM** (3h): Testing
  - Run daily test checklist (TESTING_GUIDE.md)
  - Check for regression bugs
  - Verify CORS, auth, database connections
  
- **5:00 PM - 6:00 PM** (1h): Debugging
  - Fix critical issues same day
  - Document solutions for team

### Success Criteria
- No code from BE2/3/4 merges without review ✅
- All tests pass daily ✅
- Response to critical bugs < 1 hour ✅
- Database stays clean (no orphaned records) ✅

---

## 🔵 BE2: Topics & Evaluation - 5 Hours Total

### Assignment Details

**Files to Create/Edit:**
- Create: `backend/app/api/v1/topics.py` (copy from provided template)
- Create: `backend/app/schemas/topic.py` (schema definitions)
- Edit: `backend/app/api/v1/api.py` (add router registration)

**Endpoints to Implement:** (6 total)

| # | Method | Endpoint | Role | Time |
|---|--------|----------|------|------|
| 1 | POST | `/topics` | Lecturer (4) | 1.5h |
| 2 | GET | `/topics` | All (students see APPROVED only) | 1h |
| 3 | GET | `/topics/{id}` | All | 0.5h |
| 4 | PATCH | `/topics/{id}/approve` | Admin/HeadDept (1,3) | 0.5h |
| 5 | PATCH | `/topics/{id}/reject` | Admin/HeadDept (1,3) | 0.5h |
| 6 | POST | `/evaluations` | Lecturer (4) | 1h |

### Detailed Tasks

#### Task 1: Create Schema File (20 min)
File: `backend/app/schemas/topic.py`

**Required Classes:**
- `TopicCreate` - with fields: title (str), description (Optional[str])
- `EvaluationCreate` - with fields: team_id (int), project_id (int), score (float)

**Implementation Guide:**
```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TopicCreate(BaseModel):
    title: str
    description: Optional[str] = None
    requirements: Optional[str] = None

class EvaluationCreate(BaseModel):
    team_id: int
    project_id: int
    score: float
    feedback: Optional[str] = None
```

#### Task 2: Create Endpoints File (3.5 hours)
File: `backend/app/api/v1/topics.py`

**Key Patterns:**
- Use `async def` for all functions
- Use `Depends(get_current_user)` for authentication
- Check `current_user.role_id` for authorization
- Use `db.execute(select(...).where(...))` for queries
- Return proper HTTP status codes (201 for POST, 200 for GET/PATCH)
- Use `datetime.now(timezone.utc)` for timestamps

**Template provided:** Complete working code in `/STARTER_BE2_TOPICS.py` - copy and adapt!

#### Task 3: Register Routes (10 min)
Edit: `backend/app/api/v1/api.py`

Add these lines (after line 21):
```python
from app.api.v1.topics import router as topics_router
api_router.include_router(topics_router, prefix="/topics", tags=["topics"])
```

#### Task 4: Testing (1 hour)

Run these tests in order:

```bash
# 1. Create topic as lecturer
curl -X POST http://localhost:8000/api/v1/topics \
  -H "Authorization: Bearer $LECTURER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "AI Project", "description": "..."}' \
  
# Expected: 201, status=DRAFT, created_by=lecturer name

# 2. List topics as student
curl http://localhost:8000/api/v1/topics \
  -H "Authorization: Bearer $STUDENT_TOKEN"
  
# Expected: 200, empty list (topic is DRAFT)

# 3. Approve as admin
curl -X PATCH http://localhost:8000/api/v1/topics/1/approve \
  -H "Authorization: Bearer $ADMIN_TOKEN"
  
# Expected: 200, status=APPROVED

# 4. List topics as student again
curl http://localhost:8000/api/v1/topics \
  -H "Authorization: Bearer $STUDENT_TOKEN"
  
# Expected: 200, shows the approved topic
```

### Timeline
- **Day 1 (9 AM - 2 PM):** Tasks 1-2 (4 hours)
- **Day 1 (2 PM - 3 PM):** Task 3 (1 hour)
- **Day 1 (3 PM - 4 PM):** Task 4 testing (1 hour)

### Dependency: None - can start immediately ✅

---

## 🟢 BE3: Teams & Join Logic - 6 Hours Total

### Assignment Details

**Files to Create/Edit:**
- Create: `backend/app/api/v1/teams.py` (copy from provided template)
- Edit: `backend/app/schemas/team.py` (update existing)
- Edit: `backend/app/api/v1/api.py` (add router registration)

**Endpoints to Implement:** (5 total)

| # | Method | Endpoint | Role | Time |
|---|--------|----------|------|------|
| 1 | POST | `/teams` | Student (5) | 1.5h |
| 2 | GET | `/teams` | All | 1h |
| 3 | GET | `/teams/{id}` | All | 1h |
| 4 | POST | `/teams/{id}/join` | Student (5) | 1h |
| 5 | PATCH | `/teams/{id}/finalize` | Lecturer/Admin (1,4) | 1h |

### Detailed Tasks

#### Task 1: Update Schema File (20 min)
File: `backend/app/schemas/team.py` (already exists, update it)

**Key Pattern:**
```python
class TeamCreate(BaseModel):
    name: str
    project_id: int
    description: Optional[str] = None
```

#### Task 2: Create Endpoints File (4 hours)
File: `backend/app/api/v1/teams.py`

**⚠️ Critical Logic:**

1. **Auto-generate join_code:**
   ```python
   import secrets
   join_code = secrets.token_hex(3).upper()  # 6-char hex like "A1B2C3"
   ```

2. **Auto-add creator as LEADER:**
   ```python
   new_team = Team(...)
   db.add(new_team)
   await db.flush()  # ← IMPORTANT: Get team_id before creating member
   
   team_member = TeamMember(
       team_id=new_team.team_id,
       user_id=current_user.user_id,
       role="LEADER"
   )
   db.add(team_member)
   ```

3. **Validate join before joining:**
   - Check team exists
   - Check team not finalized
   - Check join_code matches
   - Check user not already member

4. **Finalize removes join_code:**
   ```python
   team.is_finalized = True
   team.join_code = None
   ```

**Template provided:** Complete working code in `/STARTER_BE3_TEAMS.py` - copy!

#### Task 3: Register Routes (10 min)
Edit: `backend/app/api/v1/api.py`

```python
from app.api.v1.teams import router as teams_router
api_router.include_router(teams_router, prefix="/teams", tags=["teams"])
```

#### Task 4: Testing (1.5 hours)

```bash
# 1. Create team
curl -X POST http://localhost:8000/api/v1/teams \
  -H "Authorization: Bearer $STUDENT1_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Team A", "project_id": 1}'
  
# Expected: 201, join_code like "A1B2C3"
export TEAM_ID=1
export JOIN_CODE="A1B2C3"

# 2. Get teams
curl http://localhost:8000/api/v1/teams \
  -H "Authorization: Bearer $STUDENT1_TOKEN"
  
# Expected: 200, list with 1 team, member_count=1

# 3. Get team detail
curl http://localhost:8000/api/v1/teams/1 \
  -H "Authorization: Bearer $STUDENT1_TOKEN"
  
# Expected: 200, members array with creator as LEADER

# 4. Join with code
curl -X POST "http://localhost:8000/api/v1/teams/1/join?join_code=$JOIN_CODE" \
  -H "Authorization: Bearer $STUDENT2_TOKEN"
  
# Expected: 200, role=MEMBER

# 5. Finalize
curl -X PATCH http://localhost:8000/api/v1/teams/1/finalize \
  -H "Authorization: Bearer $LECTURER_TOKEN"
  
# Expected: 200, is_finalized=true

# 6. Verify can't join finalized
curl -X POST "http://localhost:8000/api/v1/teams/1/join?join_code=$JOIN_CODE" \
  -H "Authorization: Bearer $STUDENT2_TOKEN"
  
# Expected: 400, "Team is finalized"
```

### Timeline
- **Day 1 (2 PM - 3 PM):** Task 1 (20 min)
- **Day 2 (9 AM - 1 PM):** Tasks 2-3 (4 hours)
- **Day 2 (1 PM - 3 PM):** Task 4 testing (1.5 hours)

### Dependency: None - can start Day 1 ✅

---

## 🟣 BE4: Tasks & Sprints - 5 Hours Total

### Assignment Details

**Files to Create/Edit:**
- Create: `backend/app/api/v1/tasks.py` (copy from provided template)
- Edit: `backend/app/schemas/task.py` (add TaskCreate, TaskUpdate)
- Edit: `backend/app/api/v1/api.py` (add router registration)

**Endpoints to Implement:** (7 total)

| # | Method | Endpoint | Time |
|---|--------|----------|------|
| 1 | POST | `/sprints` | 0.5h |
| 2 | GET | `/sprints/{id}` | 0.5h |
| 3 | POST | `/tasks` | 1h |
| 4 | GET | `/tasks` | 1h |
| 5 | GET | `/tasks/{id}` | 0.5h |
| 6 | PUT | `/tasks/{id}` | 1h |
| 7 | DELETE | `/tasks/{id}` | 0.5h |

### Detailed Tasks

#### Task 1: Update Schema File (20 min)
File: `backend/app/schemas/task.py`

```python
class TaskCreate(BaseModel):
    title: str
    sprint_id: int
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    priority: str = "MEDIUM"

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
```

#### Task 2: Create Endpoints File (3.5 hours)
File: `backend/app/api/v1/tasks.py`

**Key Patterns:**

1. **Valid statuses:**
   ```python
   valid_statuses = ["TODO", "DOING", "DONE", "BLOCKED"]
   if status not in valid_statuses:
       raise HTTPException(400, detail="Invalid status")
   ```

2. **Count tasks by status:**
   ```python
   task_counts = {
       "TODO": sum(1 for t in all_tasks if t.status == "TODO"),
       "DOING": sum(1 for t in all_tasks if t.status == "DOING"),
       "DONE": sum(1 for t in all_tasks if t.status == "DONE"),
       "BLOCKED": sum(1 for t in all_tasks if t.status == "BLOCKED"),
   }
   ```

3. **Filter tasks:**
   ```python
   query = select(Task)
   if sprint_id:
       query = query.where(Task.sprint_id == sprint_id)
   if status:
       query = query.where(Task.status == status)
   ```

**Template provided:** Complete in `/STARTER_BE4_TASKS.py` - copy!

#### Task 3: Register Routes (10 min)
```python
from app.api.v1.tasks import router as tasks_router
api_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
```

#### Task 4: Testing (1.5 hours)

```bash
# 1. Create sprint
curl -X POST "http://localhost:8000/api/v1/tasks/sprints?team_id=1&name=Sprint%201" \
  -H "Authorization: Bearer $STUDENT_TOKEN"
  
# Expected: 201, sprint_id
export SPRINT_ID=1

# 2. Create task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Task 1", "sprint_id": 1, "priority": "HIGH"}'
  
# Expected: 201, status=TODO
export TASK_ID=1

# 3. Get tasks
curl "http://localhost:8000/api/v1/tasks?sprint_id=1" \
  -H "Authorization: Bearer $STUDENT_TOKEN"
  
# Expected: 200, list with 1 task

# 4. Update status
curl -X PUT http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "DOING"}'
  
# Expected: 200, status=DOING

# 5. Check sprint summary
curl http://localhost:8000/api/v1/tasks/sprints/1 \
  -H "Authorization: Bearer $STUDENT_TOKEN"
  
# Expected: 200, task_counts: {DOING: 1, TODO: 0, ...}

# 6. Delete task
curl -X DELETE http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer $STUDENT_TOKEN"
  
# Expected: 200, deleted
```

### Timeline
- **Day 2 (2 PM - 3 PM):** Task 1 (20 min)
- **Day 3 (9 AM - 1 PM):** Tasks 2-3 (3.5 hours)
- **Day 3 (1 PM - 3 PM):** Task 4 testing (1.5 hours)

### Dependency: None - can start immediately ✅

---

## 🟠 FE1: Lecturer Dashboard - 7 Hours Total

### Assignment Details

**Files to Create:**
- Create: `frontend/src/pages/LecturerDashboard.jsx` (main topics list + create form)
- Create: `frontend/src/pages/ApproveTopics.jsx` (optional - admin approval page)
- Edit: `frontend/src/App.jsx` (add routes)

**UI Components:**

| Component | Hours | Details |
|-----------|-------|---------|
| Topics List Table | 2h | Ant Design Table, GET /topics |
| Create Topic Modal | 2h | Form with title, description, POST /topics |
| Approval Buttons | 1h | Approve/Reject, PATCH /approve,/reject |
| Error Handling | 1h | Messages, loading states |
| Styling | 1h | Colors, responsive layout |

### Detailed Tasks

#### Task 1: Create Main Component (2.5 hours)
File: `frontend/src/pages/LecturerDashboard.jsx`

**Structure:**
```jsx
import React, { useState, useEffect } from 'react';
import { Table, Button, Form, Modal, message } from 'antd';
import api from '../services/api';

export default function LecturerDashboard() {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  // Load topics on mount
  useEffect(() => {
    fetchTopics();
  }, []);

  const fetchTopics = async () => {
    setLoading(true);
    try {
      const response = await api.get('/topics');
      setTopics(response.data.topics);
    } catch (error) {
      message.error('Failed to load topics');
    }
    setLoading(false);
  };

  const handleCreateTopic = async (values) => {
    try {
      await api.post('/topics', values);
      message.success('Topic created successfully');
      form.resetFields();
      setModalVisible(false);
      fetchTopics();
    } catch (error) {
      message.error('Failed to create topic');
    }
  };

  const handleApprove = async (topicId) => {
    try {
      await api.patch(`/topics/${topicId}/approve`);
      message.success('Topic approved');
      fetchTopics();
    } catch (error) {
      message.error('Failed to approve topic');
    }
  };

  const columns = [
    { title: 'Title', dataIndex: 'title', key: 'title' },
    { title: 'Status', dataIndex: 'status', key: 'status' },
    { title: 'Created By', dataIndex: 'created_by', key: 'created_by' },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <>
          {record.status === 'DRAFT' && (
            <Button onClick={() => handleApprove(record.topic_id)}>Approve</Button>
          )}
        </>
      ),
    },
  ];

  return (
    <div>
      <h1>Topics</h1>
      <Button type="primary" onClick={() => setModalVisible(true)}>
        Create Topic
      </Button>
      <Table columns={columns} dataSource={topics} loading={loading} />
      <Modal
        title="Create Topic"
        visible={modalVisible}
        onOk={() => form.submit()}
        onCancel={() => setModalVisible(false)}
      >
        <Form form={form} onFinish={handleCreateTopic}>
          <Form.Item name="title" label="Title" rules={[{ required: true }]}>
            <input />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <input />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
```

#### Task 2: Add Route (30 min)
File: `frontend/src/App.jsx`

```jsx
import LecturerDashboard from './pages/LecturerDashboard';

// In BrowserRouter:
<Route path="/lecturer/topics" element={<LecturerDashboard />} />
```

#### Task 3: Add Approval Page (2 hours) [Optional for now]
File: `frontend/src/pages/ApproveTopics.jsx`

For HEAD_DEPT/ADMIN to approve topics before lecturers can use them.

#### Task 4: Polish & Testing (2.5 hours)
- Test creation form
- Test approval workflow
- Check error messages
- Test responsive design (mobile viewport)

### Timeline
- **Day 3 (2 PM - 5 PM):** Task 1 (3 hours)
- **Day 4 (9 AM - 10 AM):** Task 2 (1 hour)
- **Day 4 (10 AM - 12 PM):** Tasks 3-4 (2 hours)

### Dependency: BE2 (Topics API) - starts Day 2 ✅

---

## 🟡 FE2: Student Dashboard - 7 Hours Total

### Assignment Details

**Files to Create:**
- Create: `frontend/src/pages/StudentDashboard.jsx` (main dashboard)
- Create: `frontend/src/pages/TeamDetail.jsx` (team detail + task board)
- Edit: `frontend/src/App.jsx` (add routes)

**UI Components:**

| Component | Hours | Details |
|-----------|-------|---------|
| Available Topics List | 1.5h | GET /topics, filter APPROVED |
| Your Teams Table | 1.5h | GET /teams, join_code column |
| Create Team Modal | 1.5h | Form + show join_code in response |
| Join Team Modal | 1h | Input join code, POST /join |
| Team Detail Page | 1.5h | Members list, team info |
| Task Board/Kanban | 1h | 3 columns: TODO, DOING, DONE |
| Styling | 0.5h | Responsive, colors |

### Detailed Tasks

#### Task 1: Create StudentDashboard (2 hours)
File: `frontend/src/pages/StudentDashboard.jsx`

**Features:**
- Tab 1: Available Topics (from APPROVED topics)
- Tab 2: Your Teams (teams user is member of)
- Create Team button → Modal
- Join Team button → Modal

```jsx
import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Tabs, message } from 'antd';
import api from '../services/api';

export default function StudentDashboard() {
  const [topics, setTopics] = useState([]);
  const [teams, setTeams] = useState([]);
  const [createTeamModal, setCreateTeamModal] = useState(false);
  const [joinTeamModal, setJoinTeamModal] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchTopics();
    fetchTeams();
  }, []);

  const fetchTopics = async () => {
    const response = await api.get('/topics');
    // Should already be filtered to APPROVED only for students
    setTopics(response.data.topics);
  };

  const fetchTeams = async () => {
    const response = await api.get('/teams');
    setTeams(response.data.teams);
  };

  const handleCreateTeam = async (values) => {
    try {
      const response = await api.post('/teams', values);
      message.success(`Team created! Join code: ${response.data.join_code}`);
      form.resetFields();
      setCreateTeamModal(false);
      fetchTeams();
    } catch (error) {
      message.error('Failed to create team');
    }
  };

  const handleJoinTeam = async (values) => {
    try {
      await api.post(`/teams/1/join?join_code=${values.join_code}`);
      message.success('Joined team successfully!');
      setJoinTeamModal(false);
      fetchTeams();
    } catch (error) {
      message.error('Failed to join team');
    }
  };

  const topicsColumns = [
    { title: 'Title', dataIndex: 'title', key: 'title' },
    { title: 'Created By', dataIndex: 'created_by', key: 'created_by' },
  ];

  const teamsColumns = [
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: 'Members', dataIndex: 'member_count', key: 'member_count' },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Button onClick={() => window.location.href = `/teams/${record.team_id}`}>
          View
        </Button>
      ),
    },
  ];

  return (
    <Tabs>
      <Tabs.TabPane tab="Available Topics">
        <Table columns={topicsColumns} dataSource={topics} />
      </Tabs.TabPane>
      <Tabs.TabPane tab="Your Teams">
        <Button onClick={() => setCreateTeamModal(true)}>Create Team</Button>
        <Button onClick={() => setJoinTeamModal(true)}>Join Team</Button>
        <Table columns={teamsColumns} dataSource={teams} />
      </Tabs.TabPane>
    </Tabs>
  );
}
```

#### Task 2: Create Team Detail Page (2 hours)
File: `frontend/src/pages/TeamDetail.jsx`

**Features:**
- Show team info, description
- List members with roles
- Tasks by status (TODO, DOING, DONE)
- Simple drag-drop or status dropdown

```jsx
import React, { useState, useEffect } from 'react';
import { Card, List, Button, Table, message } from 'antd';
import api from '../services/api';

export default function TeamDetail({ params }) {
  const { teamId } = params;
  const [team, setTeam] = useState(null);
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    fetchTeamDetail();
    fetchTasks();
  }, [teamId]);

  const fetchTeamDetail = async () => {
    const response = await api.get(`/teams/${teamId}`);
    setTeam(response.data);
  };

  const fetchTasks = async () => {
    const response = await api.get('/tasks?team_id=' + teamId);
    setTasks(response.data.tasks);
  };

  if (!team) return <div>Loading...</div>;

  return (
    <div>
      <h1>{team.name}</h1>
      <p>{team.description}</p>
      
      <h2>Members</h2>
      <List
        dataSource={team.members}
        renderItem={(member) => (
          <List.Item>
            {member.full_name} ({member.role})
          </List.Item>
        )}
      />

      <h2>Tasks</h2>
      <div style={{ display: 'flex', gap: '20px' }}>
        {['TODO', 'DOING', 'DONE'].map((status) => (
          <div key={status} style={{ flex: 1 }}>
            <h3>{status}</h3>
            {tasks
              .filter((t) => t.status === status)
              .map((task) => (
                <Card key={task.task_id} style={{ marginBottom: '10px' }}>
                  {task.title}
                </Card>
              ))}
          </div>
        ))}
      </div>
    </div>
  );
}
```

#### Task 3: Add Routes (30 min)
```jsx
<Route path="/student/dashboard" element={<StudentDashboard />} />
<Route path="/teams/:teamId" element={<TeamDetail />} />
```

#### Task 4: Polish & Testing (2 hours)
- Create team, verify join code
- Join team with code
- View team members
- Create tasks
- Change task status (via dropdown)
- Test responsive design

### Timeline
- **Day 3 (5 PM - 6 PM):** Task 1 start (1 hour, finish next day)
- **Day 4 (12 PM - 3 PM):** Task 1 finish + Task 2 (2 hours)
- **Day 5 (9 AM - 11 AM):** Tasks 3-4 (2 hours)

### Dependency: BE3 (Teams API), BE4 (Tasks API) - starts Day 2 ✅

---

## 📅 Week-by-Week Timeline

### **DAY 1 (Monday Jan 28) - Setup & BE2**
- 9:00 AM: Team standup
- 9:30 AM - 1:00 PM: BE2 creates topics.py + schemas
- 1:00 PM - 2:00 PM: BE2 testing
- 2:00 PM: BE1 code review of BE2
- 2:30 PM: FE1 starts component structure (without API calls yet)

### **DAY 2 (Tuesday Jan 29) - BE3 & FE1 Start**
- 9:00 AM: Standup, discuss any BE2 issues
- 9:30 AM - 1:30 PM: BE3 implements teams.py
- 2:00 PM - 4:00 PM: BE1 reviews both BE2 and BE3, runs integration test
- 4:00 PM: FE1 connects Topics list to real API
- BE4 starts if ahead of schedule

### **DAY 3 (Wednesday Jan 30) - BE4 & FE2 Start**
- 9:00 AM: Standup + discuss BE2/BE3 fixes
- 9:30 AM - 1:30 PM: BE4 implements tasks.py
- 2:00 PM - 4:00 PM: BE1 reviews all endpoints, runs full integration
- 4:00 PM: FE2 starts StudentDashboard component
- FE1 finishes topics UI with approval buttons

### **DAY 4 (Thursday Jan 31) - Full Integration**
- 9:00 AM: Standup
- 9:30 AM: Run full TESTING_GUIDE.md flows (all 3 flows)
- 10:00 AM - 12:00 PM: Bug fixes and polish
- 12:00 PM - 3:00 PM: FE1 & FE2 continue UI
- 3:00 PM: BE1 writes any missing unit tests (optional)

### **DAY 5 (Friday Feb 1) - Testing & Polish**
- 9:00 AM: Standup
- 9:30 AM - 12:00 PM: Full integration testing
- 12:00 PM - 1:00 PM: Critical bug fixes only
- 1:00 PM - 3:00 PM: UI polish, styling, responsiveness
- 3:00 PM - 4:00 PM: Final demo prep

### **DAY 6-7 (Weekend) - Buffer & Contingency**
- Only if critical issues need fixing
- Preferred: rest and review

---

## 🚨 Critical Success Factors

### Must Complete (Day 1-5):
- [x] All 6 backend APIs working and tested
- [x] All 2 frontend UIs functional (even basic styling OK)
- [x] Full end-to-end flow testable (Topic → Team → Task → Evaluation)
- [x] No database errors
- [x] No 500 errors

### Nice to Have (if time):
- [ ] Drag-drop task board
- [ ] Edit existing topics
- [ ] Delete teams
- [ ] Pagination on large lists
- [ ] Advanced filtering

### Do NOT Do (saves time):
- [ ] Unit tests
- [ ] Complex validation
- [ ] Repository pattern refactoring
- [ ] Database migrations (use init-db)
- [ ] Animations or transitions

---

## 📞 Communication Protocol

### Daily Standup (9:00 AM - 9:30 AM)
Each person reports (2-3 min each):
1. **Yesterday:** What was completed?
2. **Today:** What will be done?
3. **Blocker:** Any issues?

**Format:**
```
BE2: [completed] Create Topic POST. [today] GET endpoint. [blocker] None.
BE3: [completed] Nothing yet. [today] Start Teams endpoint. [blocker] Need DB schema review.
FE1: [completed] Set up component. [today] Connect to API. [blocker] Axios interceptor working?
```

### Code Review Process (1 PM)
- Push code to branch
- Notify BE1 in Slack
- BE1 reviews within 1 hour
- Comments on specific lines
- Approve or request changes

### Integration Test (4 PM)
- Run TESTING_GUIDE.md flows
- Log results in test checklist
- Report any regressions immediately

### Critical Blocker Protocol
- If stuck > 15 min: ask in group chat
- If stuck > 30 min: escalate to BE1
- BE1 responds within 1 hour max
- Document solution in Slack for team

---

## 📊 Success Metrics

**By EOD Friday:**
- ✅ 100% of 6 APIs working
- ✅ 100% of 2 frontend screens functional
- ✅ 0 database errors in logs
- ✅ 0 authentication failures
- ✅ All 3 test flows passing
- ✅ Responsive on mobile (320px width)
- ✅ No console errors

**Code Quality (but not priority):**
- ✅ Consistent error handling
- ✅ Proper HTTP status codes
- ✅ Clear variable names
- ✅ Comments on complex logic

**Performance (not priority):**
- Can be slow initially
- API response time < 1 sec acceptable
- No need for optimization

