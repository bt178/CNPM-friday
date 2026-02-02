# 🎯 GIAO_VIEC - Phase 2 (Stabilization & Integration) ✅ COMPLETED

**Ngày bắt đầu:** Feb 1, 2026  
**Hoàn thành:** Feb 2, 2026  
**Trạng thái:** ✅ **HOÀN THÀNH - Chuyển sang Phase 3**

---

## ✅ Kết quả Phase 2

| Task | Owner | Trạng thái |
|------|-------|-----------|
| API Performance Review | BE1 | ✅ Done |
| FE Dashboard Integration | FE1, FE2 | ✅ Done |
| LecturerDashboard.jsx | FE1 | ✅ Done |
| TopicManagement.jsx | FE1 | ✅ Done |
| FE Services (apiClient, etc.) | FE1, FE2 | ✅ Done |
| Swagger/OpenAPI docs | BE1 | ✅ Done |
| CORS & Auth Headers | BE1 | ✅ Done |

**Frontend pages đã có:**
- LoginPage.jsx, RegisterPage.jsx
- DashboardPage.jsx (role-based routing)
- AdminDashboard.jsx
- LecturerDashboard.jsx + TopicManagement.jsx
- ProjectListView.jsx, UserProfile.jsx, SettingsPage.jsx

---

## 👉 Tiếp theo

**Mở file:** `Giao_Viec_3/giao_viec.md`

Phase 3 bao gồm:
- Socket.IO real-time infrastructure (BE1)
- Channels & Messages API (BE2)
- Meetings API (BE3)
- Semesters completion (BE4)
- Chat UI (FE1)
- Video Call UI (FE2)

---

## 📂 Archive - Phân công gốc (đã hoàn thành)

### 🔴 BE1 (Backend Lead - Architecture Review)
**Mục tiêu:** Oversee DAO layer implementation, performance optimization

**Công việc:**
- [x] Review DAO layer design from BE2/BE3/BE4 (if implementing)
- [x] Check API response times (target: <200ms for list endpoints)
- [x] Verify JWT token refresh mechanism
- [x] Set up error handling for all endpoints
- [x] Create API documentation (Swagger/OpenAPI)
- [x] Code review FE API integration (CORS, headers, auth)

**Success criteria:**
- All endpoints respond in <200ms ✅
- Swagger docs generated and accessible ✅
- Zero CORS errors ✅
- Team reports no API-related blockers ✅

---

### 🟡 BE2 (Topics Module - DAO Layer)
**Mục tiêu:** Optimize topics queries + implement caching

**Công việc:**
- [x] Create DAO layer: `app/dao/topic_dao.py`
- [x] Implement batch queries (reduce N+1 problem)
- [x] Add caching for frequently accessed topics
- [x] Optimize topic list query (pagination + filtering)
- [x] Add relationship loading strategy
- [x] Test performance improvement

**Success criteria:**
- Topic list query returns in <100ms
- No N+1 queries in logs
- Caching reduces duplicate queries by 50%+

**Code pattern:**
```python
class TopicDAO:
    async def get_topics_with_evaluations(self, skip, limit):
        # Load topics with evaluations eager-loaded
        # Use joinedload to avoid N+1
        pass
```

**Tài liệu tham khảo:**
- CRITICAL_FIXES.md (section: Query optimization)
- CODE/backend/dao_examples/ (if available)

---

### 🟠 BE3 (Teams Module - Member Management)
**Mục tiêu:** Implement team member features + validation

**Công việc:**
- [ ] Implement team member role system (Leader, Member, Reviewer)
- [ ] Add permission checks for team operations
- [ ] Implement team deletion (cascade delete validation)
- [ ] Create endpoint: `GET /api/v1/teams/{id}/members` (with roles)
- [ ] Create endpoint: `PATCH /api/v1/teams/{id}/members/{member_id}` (update role)
- [ ] Test cascade behavior

**Success criteria:**
- Team members can have different roles
- Role-based permissions enforced
- Delete team removes all related data
- No orphaned records

**New endpoints:**
- `GET /api/v1/teams/{id}/members` (list with roles)
- `PATCH /api/v1/teams/{id}/members/{member_id}` (change role)
- `DELETE /api/v1/teams/{id}/members/{member_id}` (remove member)

**Tài liệu tham khảo:**
- CRITICAL_FIXES.md (section: Role permissions)
- app/models/all_models.py (TeamMember model)

---

### 🟠 BE4 (Tasks/Sprints - Status Workflow)
**Mục tiêu:** Implement complete task lifecycle + status transitions

**Công việc:**
- [ ] Define task status workflow (Todo → In Progress → Review → Done)
- [ ] Add validation: only valid status transitions allowed
- [ ] Implement task assignment (only to team members)
- [ ] Add task dependency support
- [ ] Create endpoint: `GET /api/v1/sprints/{id}/tasks` (with status filter)
- [ ] Test workflow edge cases

**Success criteria:**
- Task status transitions work correctly
- Invalid transitions rejected (422 error)
- Task assignments validated
- No "unassigned" tasks allowed

**Status workflow:**
```
Todo → In Progress → Review → Done
            ↓
       Blocked (with reason)
```

**New endpoints:**
- `GET /api/v1/sprints/{id}/tasks?status=in_progress`
- `PATCH /api/v1/tasks/{id}/assign` (assign to member)
- `PATCH /api/v1/tasks/{id}/status` (change status with validation)

**Tài liệu tham khảo:**
- CRITICAL_FIXES.md (section: Task workflow)
- app/models/all_models.py (Task model)

---

### 🟢 FE1 (Lecturer Dashboard - Topics Management)
**Mục tiêu:** Build fully functional topics management UI

**Công việc:**
- [ ] Copy service file: `Giao_Viec_2/CODE/fe/lecturerTopicsService.js` → `frontend/src/services/`
- [ ] Create `frontend/src/pages/LecturerDashboard.jsx`
- [ ] Create components:
  - [ ] TopicsTable.jsx (list all topics with status)
  - [ ] TopicDetailModal.jsx (view full topic + team info)
  - [ ] ApprovalSection.jsx (approve/reject buttons)
  - [ ] EvaluationForm.jsx (add evaluation criteria)
- [ ] Implement features:
  - [ ] Real-time data fetching from API
  - [ ] Approve/reject with modal confirmation
  - [ ] Add/edit evaluation criteria
  - [ ] Filter by status (Pending, Approved, Rejected)
  - [ ] Search by group name
- [ ] Add navigation link to main menu

**Success criteria:**
- Dashboard loads all topics from API (not mock data)
- Can approve/reject topics with visual feedback
- Can add evaluation criteria
- Filters and search work
- No console errors

**UI Features:**
- [ ] Topics table with columns: ID, Title, Group, Status, Actions
- [ ] Action buttons: View, Approve, Reject, Evaluate
- [ ] Status badge: Pending (yellow), Approved (green), Rejected (red)
- [ ] Modal for topic details
- [ ] Loading spinner while fetching
- [ ] Error message if API fails

**Tài liệu tham khảo:**
- Giao_Viec_2/CODE/fe/lecturerTopicsService.js (API methods)
- TASK_ASSIGNMENT_PHASE2.md (detailed requirements)
- Ant Design docs (Table, Modal, Button)

---

### 🔵 FE2 (Student Dashboard - Teams & Projects)
**Mục tiêu:** Build fully functional team management UI

**Công việc:**
- [ ] Copy service file: `Giao_Viec_2/CODE/fe/studentTeamsService.js` → `frontend/src/services/`
- [ ] Copy service file: `Giao_Viec_2/CODE/fe/tasksService.js` → `frontend/src/services/`
- [ ] Create `frontend/src/pages/StudentDashboard.jsx`
- [ ] Create components:
  - [ ] AvailableTopics.jsx (list topics to create team from)
  - [ ] CreateTeamModal.jsx (form to create team)
  - [ ] JoinTeamModal.jsx (input join code)
  - [ ] TeamsList.jsx (student's teams)
  - [ ] TeamMembersPanel.jsx (display team members)
  - [ ] TasksPanel.jsx (team tasks/sprints)
- [ ] Implement features:
  - [ ] View all approved topics
  - [ ] Create team (select topic, team name, member emails)
  - [ ] Join existing team (input code)
  - [ ] View team members and roles
  - [ ] View team tasks and sprints
  - [ ] Quick switch between teams
- [ ] Add navigation link to main menu

**Success criteria:**
- Dashboard loads all student data from API (not mock)
- Can create and join teams
- Team members display correctly
- Can switch between multiple teams
- No console errors
- Mobile responsive

**UI Features:**
- [ ] Topics carousel/grid with "Create Team" button
- [ ] Teams list on left sidebar
- [ ] Team details panel on right
- [ ] Team members table
- [ ] Tasks/sprints table with status filter
- [ ] Join team modal with code input
- [ ] Loading spinners for async operations

**Tài liệu tham khảo:**
- Giao_Viec_2/CODE/fe/studentTeamsService.js
- Giao_Viec_2/CODE/fe/tasksService.js (for tasks panel)
- TASK_ASSIGNMENT_PHASE2.md
- Ant Design docs (Layout, Table, Modal, Button)

---

## 🔧 Critical Fixes (Must complete before Phase 3)

**Priority 1: Authentication**
- [ ] JWT token refresh endpoint working
- [ ] Session timeout implemented
- [ ] Role-based access control validated

**Priority 2: Database**
- [ ] All foreign key constraints active
- [ ] Cascade delete tested
- [ ] No orphaned records in production

**Priority 3: API Error Handling**
- [ ] All endpoints return proper error codes (400, 401, 403, 422, 500)
- [ ] Error messages clear and actionable
- [ ] Logging enabled for debugging

**Priority 4: Frontend Integration**
- [ ] No CORS errors
- [ ] API base URL correctly configured
- [ ] Bearer token injected in all requests
- [ ] Error messages displayed to user

---

## 🧪 Integration Testing Checklist

### End-to-end Flow 1: Lecturer Topic Approval
```
1. Lecturer login
2. Navigate to Topics dashboard
3. See list of topics from database
4. Click Approve button on one topic
5. Topic status changes to "Approved"
6. Get notification/confirmation
```

### End-to-end Flow 2: Student Team Creation
```
1. Student login
2. Navigate to Dashboard
3. See available approved topics
4. Click "Create Team"
5. Fill form (team name, members)
6. Submit
7. Team created in database
8. Student can see team in "My Teams"
```

### End-to-end Flow 3: Team Task Assignment
```
1. Team Lead login
2. Create sprint
3. Create tasks under sprint
4. Assign task to team member
5. Task appears in member's view
6. Member can update task status
7. Status changes visible to all team members
```

---

## 📋 Dùng file nào?

| Tên file | Dùng khi nào |
|----------|-----------|
| TASK_ASSIGNMENT_PHASE2.md | Chi tiết công việc của bạn |
| CRITICAL_FIXES.md | Cần fix blocking issues |
| PHASE3_PLAN.md | Chuẩn bị cho Phase 3 |
| CODE/ | Cần code mẫu |
| SCHEMAS/ | Cần xem Pydantic models |

---

## ⏰ Timeline

| Ngày | Milestone | Owner |
|-----|-----------|-------|
| Feb 1-2 | FE1/FE2 start dashboard implementation | FE1-2 |
| Feb 2-3 | BE2/BE3/BE4 critical fixes | BE2-4 |
| Feb 4 | FE dashboards integrated with real data | FE1-2 |
| Feb 5-6 | Full end-to-end testing | All |
| Feb 7 | Phase 2 complete, ready for Phase 3 | All |

---

## 🚨 Common Issues in Phase 2

**Issue:** FE dashboard shows empty (no data from API)  
→ Check browser console for errors  
→ Verify API endpoint URL  
→ Check if auth token is being sent

**Issue:** API returns 401 (Unauthorized)  
→ Token might be expired (15 min timeout)  
→ Re-login and try again  
→ Check Authorization header format

**Issue:** CORS error in browser  
→ Make sure backend CORS is configured for `http://localhost:3000`  
→ Restart backend: `docker-compose restart backend`

**Issue:** Task status update not working  
→ Check if user is team member  
→ Verify task ownership  
→ Check task status workflow rules

**Issue:** Team delete fails  
→ Check if cascade delete is configured  
→ Verify no constraint violations  
→ Check database logs

---

## ✅ Khi xong Phase 2

Sau khi tất cả critical fixes completed + 2 FE dashboards fully integrated:

1. Run full end-to-end test (Flow 1, 2, 3)
2. Check database for data integrity
3. Document any remaining technical debt
4. Mở file `Giao_Viec_2/PHASE3_PLAN.md`
5. Bắt đầu Phase 3 planning

---

**Chúc bạn làm việc vui vẻ! 🚀**  
*Phase 2 là giai đoạn ổn định cơ sở hạ tầng. Làm kỹ để Phase 3 smooth! 💪*
