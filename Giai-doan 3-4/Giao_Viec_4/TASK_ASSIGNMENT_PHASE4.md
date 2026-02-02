# 📋 TASK ASSIGNMENT - PHASE 4: AI & EVALUATION

> **Phase 4** - Advanced Features: AI Mentoring, Peer Reviews, Milestones, Submissions, Resources
> **Duration:** ~2 weeks
> **Target:** 30 thêm endpoints, hoàn thành MVP

---

## 🎯 PHASE 4 OVERVIEW

### Mục tiêu chính
1. **AI Mentoring** - Tích hợp Google Gemini cho gợi ý mentoring
2. **Peer Reviews** - Đánh giá đồng nghiệp với ẩn danh
3. **Milestones & Checkpoints** - Quản lý mốc dự án
4. **Submissions** - Nộp bài và chấm điểm
5. **Resources** - Quản lý tài liệu dự án

### Endpoints cần hoàn thành (~30)

| Module | Endpoints | Priority |
|--------|-----------|----------|
| Mentoring | 6 | HIGH |
| Peer Reviews | 6 | HIGH |
| Milestones | 5 | HIGH |
| Checkpoints | 3 | MEDIUM |
| Submissions | 6 | HIGH |
| Resources | 5 | MEDIUM |

---

## 👥 TEAM ASSIGNMENT

### 🔵 BE1 - AI Mentoring & Peer Reviews

**Files cần làm:**
1. Copy `Giao_Viec_4/CODE/be/mentoring.py` → `backend/app/api/v1/mentoring.py`
2. Copy `Giao_Viec_4/CODE/be/peer_reviews.py` → `backend/app/api/v1/peer_reviews.py`
3. Cập nhật `backend/app/services/ai_service.py` (Google Gemini integration)

**Công việc chi tiết:**

#### Task 4.1.1: AI Mentoring API
```python
# Endpoints:
POST   /api/v1/mentoring/              # Tạo mentoring log
GET    /api/v1/mentoring/              # List logs by team
GET    /api/v1/mentoring/{log_id}      # Chi tiết log
PUT    /api/v1/mentoring/{log_id}      # Update log
POST   /api/v1/mentoring/{log_id}/ai-suggestions  # Generate AI suggestions
DELETE /api/v1/mentoring/{log_id}      # Xóa log
```

**Cách test:**
```bash
# 1. Tạo mentoring log
POST /api/v1/mentoring/
Body: {
  "team_id": 1,
  "session_notes": "Thảo luận về tiến độ dự án",
  "discussion_points": "UI design, database optimization"
}

# 2. Tạo AI suggestions
POST /api/v1/mentoring/1/ai-suggestions
Body: {
  "team_id": 1,
  "context": "Team cần cải thiện UI/UX"
}
```

#### Task 4.1.2: Peer Reviews API
```python
# Endpoints:
POST   /api/v1/peer-reviews/           # Tạo review
GET    /api/v1/peer-reviews/           # List reviews (ẩn danh cho students)
GET    /api/v1/peer-reviews/my-reviews # Xem reviews về mình (ẩn danh)
GET    /api/v1/peer-reviews/summary/{team_id}  # Summary (Lecturer only)
PUT    /api/v1/peer-reviews/{id}       # Update review
DELETE /api/v1/peer-reviews/{id}       # Xóa review
```

**Business rules:**
- Không thể tự review chính mình
- Mỗi người chỉ review 1 lần cho mỗi teammate
- Students xem reviews về mình = ẩn danh (không thấy reviewer)
- Lecturer xem được tất cả + summary với average scores

---

### 🔵 BE2 - Milestones & Submissions

**Files cần làm:**
1. Copy `Giao_Viec_4/CODE/be/milestones.py` → `backend/app/api/v1/milestones.py`
2. Copy `Giao_Viec_4/CODE/be/submissions.py` → `backend/app/api/v1/submissions.py`

**Công việc chi tiết:**

#### Task 4.2.1: Milestones API
```python
# Endpoints:
POST   /api/v1/milestones/                      # Tạo milestone (Lecturer)
GET    /api/v1/milestones/                      # List by project
GET    /api/v1/milestones/{id}                  # Chi tiết + checkpoints
PUT    /api/v1/milestones/{id}                  # Update (Lecturer)
DELETE /api/v1/milestones/{id}                  # Xóa (cascade checkpoints)
POST   /api/v1/milestones/checkpoints/          # Tạo checkpoint
PUT    /api/v1/milestones/checkpoints/{id}      # Update checkpoint
DELETE /api/v1/milestones/checkpoints/{id}      # Xóa checkpoint
```

#### Task 4.2.2: Submissions API
```python
# Endpoints:
POST   /api/v1/submissions/                     # Nộp bài (team members)
GET    /api/v1/submissions/                     # List submissions
GET    /api/v1/submissions/{id}                 # Chi tiết
PUT    /api/v1/submissions/{id}                 # Update (trước khi chấm)
POST   /api/v1/submissions/{id}/grade           # Chấm điểm (Lecturer)
DELETE /api/v1/submissions/{id}                 # Xóa (trước khi chấm)
```

**Business rules:**
- Mỗi team chỉ nộp 1 bài cho mỗi milestone
- Không thể sửa/xóa sau khi đã chấm điểm
- Lecturer chấm điểm 0-10 + feedback

---

### 🔵 BE3 - Resources API

**Files cần làm:**
1. Copy `Giao_Viec_4/CODE/be/resources.py` → `backend/app/api/v1/resources.py`
2. Register tất cả routers trong `backend/app/api/v1/api.py`

**Công việc chi tiết:**

#### Task 4.3.1: Resources API
```python
# Endpoints:
POST   /api/v1/resources/           # Tạo resource
GET    /api/v1/resources/           # List (filter by project/team/type)
GET    /api/v1/resources/{id}       # Chi tiết
PUT    /api/v1/resources/{id}       # Update (owner only)
DELETE /api/v1/resources/{id}       # Xóa (owner only)
```

#### Task 4.3.2: Register All Phase 4 Routers
```python
# backend/app/api/v1/api.py
from app.api.v1 import mentoring, peer_reviews, milestones, submissions, resources

api_router.include_router(mentoring.router, prefix="/mentoring", tags=["mentoring"])
api_router.include_router(peer_reviews.router, prefix="/peer-reviews", tags=["peer-reviews"])
api_router.include_router(milestones.router, prefix="/milestones", tags=["milestones"])
api_router.include_router(submissions.router, prefix="/submissions", tags=["submissions"])
api_router.include_router(resources.router, prefix="/resources", tags=["resources"])
```

---

### 🟢 FE1 - AI Mentoring & Peer Review UI

**Files cần làm:**
1. Copy `Giao_Viec_4/CODE/fe/mentoringService.js` → `frontend/src/services/mentoringService.js`
2. Copy `Giao_Viec_4/CODE/fe/peerReviewService.js` → `frontend/src/services/peerReviewService.js`
3. Tạo `frontend/src/pages/MentoringPage.jsx`
4. Tạo `frontend/src/pages/PeerReviewPage.jsx`

**UI Components:**

#### MentoringPage.jsx
```jsx
// Features:
// - List mentoring logs của team
// - Form tạo mentoring log mới
// - Button "Generate AI Suggestions" 
// - Hiển thị AI suggestions với loading spinner
// - Edit/Delete log (mentor only)
```

#### PeerReviewPage.jsx
```jsx
// Features:
// - List team members cần review (trừ bản thân)
// - Form review: score (0-10) + feedback + criteria
// - Tab "My Reviews" - xem reviews về mình (ẩn danh)
// - Summary chart cho Lecturers (average scores)
```

---

### 🟢 FE2 - Milestones & Submissions UI

**Files cần làm:**
1. Copy `Giao_Viec_4/CODE/fe/milestoneService.js` → `frontend/src/services/milestoneService.js`
2. Copy `Giao_Viec_4/CODE/fe/submissionService.js` → `frontend/src/services/submissionService.js`
3. Tạo `frontend/src/pages/MilestonesPage.jsx`
4. Tạo `frontend/src/pages/SubmissionsPage.jsx`

**UI Components:**

#### MilestonesPage.jsx
```jsx
// Features:
// - Timeline view của milestones
// - Progress bar cho mỗi milestone (dựa trên checkpoints)
// - Create milestone form (Lecturer only)
// - Checkbox list cho checkpoints
// - Due date warnings (quá hạn = red)
```

#### SubmissionsPage.jsx
```jsx
// Features:
// - List submissions của team
// - Upload/link file submission
// - View submission details
// - Grading form (Lecturer only): score + feedback
// - Score display with colors (8+ = green, 5-7 = orange, <5 = red)
```

---

### 🟢 FE3 - Resources UI

**Files cần làm:**
1. Copy `Giao_Viec_4/CODE/fe/resourceService.js` → `frontend/src/services/resourceService.js`
2. Tạo `frontend/src/pages/ResourcesPage.jsx`
3. Update routing trong `App.jsx`

**UI Components:**

#### ResourcesPage.jsx
```jsx
// Features:
// - Card grid cho resources
// - Filter by type (document, link, video, etc.)
// - Upload form với auto-detect type
// - Icon/color per resource type
// - Click to open resource URL
// - Delete confirmation modal
```

---

## 📦 SCHEMAS REFERENCE

Schemas đã tạo sẵn trong `Giao_Viec_4/SCHEMAS/phase4_schemas.py`:

```python
# Mentoring
- MentoringLogCreate, MentoringLogUpdate, MentoringLogResponse
- AISuggestionRequest, AISuggestionResponse

# Peer Reviews  
- PeerReviewCreate, PeerReviewUpdate, PeerReviewResponse
- PeerReviewAnonymousResponse, PeerReviewSummary

# Milestones
- MilestoneCreate, MilestoneUpdate, MilestoneResponse
- CheckpointCreate, CheckpointUpdate, CheckpointResponse

# Submissions
- SubmissionCreate, SubmissionUpdate, SubmissionResponse
- SubmissionGrade, SubmissionListResponse

# Resources
- ResourceCreate, ResourceUpdate, ResourceResponse
```

---

## 🧪 TESTING CHECKLIST

### BE Testing
```bash
# 1. Start server
docker-compose up

# 2. Open Swagger
http://localhost:8000/docs

# 3. Test từng endpoint
# - Login trước để lấy token
# - Try it out cho từng endpoint
# - Check response codes (201, 200, 403, 404)
```

### FE Testing
```bash
# 1. Start frontend
cd frontend && npm run dev

# 2. Test flows:
# - Lecturer tạo milestone → Student nộp bài → Lecturer chấm điểm
# - Team members peer review nhau → Student xem reviews ẩn danh
# - Lecturer tạo mentoring log → Generate AI suggestions
# - Upload resources → Filter by type → Delete
```

---

## ✅ DONE CRITERIA

### BE hoàn thành khi:
- [ ] Tất cả endpoints return đúng status codes
- [ ] Authentication hoạt động (bearer token)
- [ ] Role-based access đúng (Lecturer vs Student)
- [ ] Business rules đúng (ẩn danh, không tự review, etc.)
- [ ] Swagger docs đầy đủ

### FE hoàn thành khi:
- [ ] Tất cả pages render không lỗi
- [ ] CRUD operations hoạt động
- [ ] Error handling có thông báo user-friendly
- [ ] Loading states cho async operations
- [ ] Responsive design (mobile-friendly)

---

## 📝 NOTES CHO TEAM

1. **AI Service**: Cần có `GOOGLE_API_KEY` trong `.env` để dùng Gemini
2. **Ẩn danh**: Frontend KHÔNG được hiển thị reviewer_id/name khi student xem reviews
3. **Score validation**: Backend enforce 0-10, Frontend show color coding
4. **File uploads**: Hiện tại chỉ lưu URL, không upload trực tiếp
5. **Cascade deletes**: Xóa milestone → xóa checkpoints + submissions liên quan

---

**🚀 Hoàn thành Phase 4 = MVP Complete!**

Sau Phase 4, hệ thống có đầy đủ:
- ✅ User authentication + roles
- ✅ Project & Topic management
- ✅ Team formation + tasks
- ✅ Real-time chat & video (Phase 3)
- ✅ AI Mentoring suggestions (Phase 4)
- ✅ Peer reviews + evaluations (Phase 4)
- ✅ Milestones + submissions (Phase 4)
