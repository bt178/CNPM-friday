# 🎯 GIAO_VIEC_4 - Phase 4 (AI Features, Evaluation & Advanced)

**Ngày bắt đầu:** Feb 15, 2026  
**Deadline:** Feb 21, 2026  
**Mục tiêu:** AI Mentoring, Advanced Evaluation, Peer Reviews, Reports

---

## � TIẾN ĐỘ PHASE 4

| Thành viên | Task | Status |
|------------|------|--------|
| **BE1** | AI Mentoring Integration | ✅ **HOÀN THÀNH** |
| BE2 | Peer Reviews Module | 🔄 Chưa bắt đầu |
| BE3 | Milestones & Submissions | 🔄 Chưa bắt đầu |
| BE4 | Evaluation Details & Resources | 🔄 Chưa bắt đầu |
| FE1 | AI Mentoring UI | 🔄 Chưa bắt đầu |
| FE2 | Peer Review UI | 🔄 Chưa bắt đầu |
| FE3 | Milestones & Reports UI | 🔄 Chưa bắt đầu |

### ✅ BE1 Đã hoàn thành (các thành viên khác có thể sử dụng):

**Files đã tạo:**
- `backend/app/services/ai_service.py` - AIService với Google Gemini integration
- `backend/app/api/v1/mentoring.py` - All CRUD + AI suggestion endpoints

**API Endpoints có sẵn:**
| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/api/v1/mentoring/logs` | POST | Tạo mentoring log |
| `/api/v1/mentoring/logs` | GET | Danh sách logs (query: team_id) |
| `/api/v1/mentoring/logs/{id}` | GET | Chi tiết log |
| `/api/v1/mentoring/logs/{id}` | PUT | Cập nhật log |
| `/api/v1/mentoring/logs/{id}` | DELETE | Xóa log |
| `/api/v1/mentoring/suggestions` | POST | Lấy AI suggestions |
| `/api/v1/mentoring/team-progress/{id}` | GET | Team progress analytics |
| `/api/v1/mentoring/analyze-reviews/{id}` | POST | AI analyze peer reviews |

**Cách sử dụng AIService cho BE2, BE3, BE4:**
```python
from app.services.ai_service import AIService

ai = AIService()

# Generate mentoring suggestions
suggestions = await ai.generate_mentoring_suggestions(team_data, reviews, tasks)

# Analyze peer reviews
analysis = await ai.analyze_peer_reviews(reviews)

# Generate task breakdown
breakdown = await ai.generate_task_breakdown(task_description)
```

**Lưu ý:**
- Nếu không có `GOOGLE_GEMINI_API_KEY` trong .env, AI sẽ trả về mock response
- Rate limiting: 1 second minimum giữa các API calls

---

## �📊 Tình trạng API sau Phase 3

### ✅ Đã hoàn thành (Phase 1-3):
| Module | Endpoints | Status |
|--------|-----------|--------|
| Core (Auth, Users, Profile) | 5 | ✅ |
| Topics & Evaluations | 7 | ✅ |
| Teams | 7 | ✅ |
| Tasks & Sprints | 10 | ✅ |
| Projects | 4 | ✅ |
| Academic (Classes, Subjects, etc.) | 22 | ✅ |
| Notifications | 6 | ✅ |
| Channels | 4 | ✅ (Phase 3) |
| Messages | 5 | ✅ (Phase 3) |
| Meetings | 6 | ✅ (Phase 3) |
| Semesters (complete) | 5 | ✅ (Phase 3) |

**Tổng: ~80 endpoints**

### 🔴 Cần làm Phase 4:
| Module | Endpoints cần | Priority |
|--------|--------------|----------|
| AI Mentoring | 4 | HIGH |
| Peer Reviews | 5 | HIGH |
| Milestones & Checkpoints | 6 | MEDIUM |
| Submissions | 5 | MEDIUM |
| Evaluation Details | 4 | MEDIUM |
| Resources | 4 | LOW |
| Reports/Analytics | 3 | LOW |

**Target Phase 4:** ~110 endpoints total

---

## 👥 Phân công Phase 4

### 🔴 BE1 (AI Mentoring Integration) ✅ HOÀN THÀNH
**Mục tiêu:** Integrate Google Gemini API for mentoring suggestions

**Công việc:**
- [x] Configure Gemini API in `app/core/config.py`
- [x] Create `app/services/ai_service.py` (enhance existing)
- [x] Create `app/schemas/mentoring.py` (trong mentoring.py endpoint)
- [x] Create `app/api/v1/mentoring.py`
- [x] Implement endpoints:
  - `POST /api/v1/mentoring/logs` (create mentoring log)
  - `GET /api/v1/mentoring/logs?team_id={id}` (list logs)
  - `GET /api/v1/mentoring/logs/{id}` (log details)
  - `PUT /api/v1/mentoring/logs/{id}` (update log)
  - `DELETE /api/v1/mentoring/logs/{id}` (delete log)
  - `POST /api/v1/mentoring/suggestions` (get AI suggestions)
  - `GET /api/v1/mentoring/team-progress/{team_id}` (get team analytics)
  - `POST /api/v1/mentoring/analyze-reviews/{team_id}` (AI analyze peer reviews)
- [x] Implement AI suggestion generation:
  - Analyze team progress (sprint velocity, task completion)
  - Analyze peer reviews (sentiment, issues)
  - Generate actionable recommendations
- [x] Add rate limiting for Gemini API
- [x] Test AI responses for quality

**Success criteria:**
- ✅ AI generates relevant mentoring suggestions
- ✅ Rate limiting prevents API abuse (1 second minimum interval)
- ✅ Suggestions are stored in mentoring logs
- ✅ Response time < 5 seconds

**Files đã tạo:**
```
backend/app/
├── services/ai_service.py        # ✅ Google Gemini integration (~350 lines)
├── api/v1/mentoring.py           # ✅ All CRUD + AI endpoints (~520 lines)
└── core/config.py                # ✅ GOOGLE_GEMINI_API_KEY added
```

**Ghi chú BE1 (Hoàn thành ngày: Feb 2026):**
- Sử dụng `google-generativeai==0.8.0` với model `gemini-1.5-flash`
- Mock fallback khi không có API key (development mode)
- AIService class với lazy initialization của Gemini client
- Rate limiting: 1 second minimum giữa các request
- Vietnamese language prompts và responses
- MentoringLog model đã cập nhật với các fields: mentor_id, session_notes, discussion_points, feedback
- Endpoints đã đăng ký trong api.py router

**Endpoints Testing Status:**
| Endpoint | Status |
|----------|--------|
| POST /api/v1/mentoring/logs | ✅ Tested |
| GET /api/v1/mentoring/logs | ✅ Tested |
| POST /api/v1/mentoring/suggestions | ✅ Tested (mock response) |

**AI Prompt Template:**
```python
def generate_mentoring_prompt(team_data, reviews, tasks):
    return f"""
    You are an academic mentor for a project team.
    
    Team Progress:
    - Sprint completion rate: {team_data.sprint_velocity}%
    - Tasks completed: {team_data.tasks_done}/{team_data.tasks_total}
    - Days until deadline: {team_data.days_remaining}
    
    Recent Peer Reviews (anonymized):
    {format_reviews(reviews)}
    
    Current Blockers:
    {format_blockers(tasks)}
    
    Provide 3-5 specific, actionable recommendations for:
    1. Improving team collaboration
    2. Addressing any skill gaps
    3. Meeting the project deadline
    
    Be constructive and supportive in tone.
    """
```

---

### 🟡 BE2 (Peer Reviews Module)
**Mục tiêu:** Implement anonymous peer review system

**Công việc:**
- [ ] Create `app/schemas/peer_review.py`
- [ ] Create `app/api/v1/peer_reviews.py`
- [ ] Register routes in `api.py`
- [ ] Implement endpoints:
  - `POST /api/v1/peer-reviews` (submit review)
  - `GET /api/v1/peer-reviews?team_id={id}` (list reviews for team)
  - `GET /api/v1/peer-reviews/my-reviews` (reviews I've submitted)
  - `GET /api/v1/peer-reviews/about-me` (reviews about me)
  - `GET /api/v1/peer-reviews/{id}` (review details)
- [ ] Implement anonymization logic
- [ ] Add review period enforcement (only during sprints)
- [ ] Create aggregation for team analytics

**Success criteria:**
- Reviews are truly anonymous (reviewer not visible to reviewed)
- Can only review team members
- One review per team member per sprint
- Aggregated scores calculated correctly

**Schema:**
```python
class PeerReviewCreate(BaseModel):
    team_id: int
    reviewed_user_id: UUID
    sprint_id: int
    collaboration_score: int  # 1-5
    communication_score: int  # 1-5
    contribution_score: int  # 1-5
    comment: Optional[str] = None
    
    @validator('collaboration_score', 'communication_score', 'contribution_score')
    def validate_score(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Score must be between 1 and 5')
        return v

class PeerReviewResponse(BaseModel):
    id: int
    team_id: int
    # NO reviewer_id for anonymity!
    reviewed_user_id: UUID
    reviewed_user_name: str
    sprint_id: int
    collaboration_score: int
    communication_score: int
    contribution_score: int
    comment: Optional[str]
    created_at: datetime
```

---

### 🟠 BE3 (Milestones & Submissions)
**Mục tiêu:** Implement milestone tracking and submission system

**Công việc:**
- [ ] Create `app/schemas/milestone.py`
- [ ] Create `app/schemas/submission.py`
- [ ] Create `app/api/v1/milestones.py`
- [ ] Create `app/api/v1/submissions.py`
- [ ] Implement endpoints:
  - **Milestones:**
    - `POST /api/v1/milestones` (create milestone)
    - `GET /api/v1/milestones?project_id={id}` (list)
    - `GET /api/v1/milestones/{id}` (details)
    - `PUT /api/v1/milestones/{id}` (update)
    - `DELETE /api/v1/milestones/{id}` (delete)
  - **Checkpoints:**
    - `POST /api/v1/milestones/{id}/checkpoints` (add checkpoint)
    - `GET /api/v1/milestones/{id}/checkpoints` (list checkpoints)
  - **Submissions:**
    - `POST /api/v1/submissions` (submit for checkpoint)
    - `GET /api/v1/submissions?checkpoint_id={id}` (list)
    - `GET /api/v1/submissions/{id}` (details)
    - `PUT /api/v1/submissions/{id}` (update - before deadline)
    - `PATCH /api/v1/submissions/{id}/grade` (lecturer grades)

**Success criteria:**
- Milestones have deadlines enforced
- Submissions blocked after deadline (unless lecturer allows late)
- Grading workflow works
- File upload support (if needed)

**Schema:**
```python
class MilestoneCreate(BaseModel):
    project_id: int
    name: str
    description: Optional[str]
    deadline: datetime
    weight: float = 1.0  # Weight in final grade

class CheckpointCreate(BaseModel):
    milestone_id: int
    description: str
    required: bool = True

class SubmissionCreate(BaseModel):
    checkpoint_id: int
    team_id: int
    content: str
    file_url: Optional[str]  # Link to uploaded file
```

---

### 🟠 BE4 (Evaluation Details & Resources)
**Mục tiêu:** Complete evaluation system and resource management

**Công việc:**
- [ ] Enhance existing evaluation endpoints with details
- [ ] Create `app/schemas/resource.py`
- [ ] Create `app/api/v1/resources.py`
- [ ] Implement endpoints:
  - **Evaluation Details:**
    - `POST /api/v1/evaluations/{id}/details` (add criteria score)
    - `GET /api/v1/evaluations/{id}/details` (list all criteria scores)
    - `PUT /api/v1/evaluations/{id}/details/{criteria_id}` (update score)
    - `GET /api/v1/evaluations/{id}/summary` (aggregated scores)
  - **Resources:**
    - `POST /api/v1/resources` (share resource)
    - `GET /api/v1/resources?team_id={id}` (list team resources)
    - `GET /api/v1/resources/{id}` (resource details)
    - `DELETE /api/v1/resources/{id}` (remove resource)
- [ ] Add resource types (link, file, document)
- [ ] Add resource tagging for search

**Success criteria:**
- Evaluation details linked to criteria
- Final scores calculated from criteria weights
- Resources organized by team
- Search/filter by resource type

**Schema:**
```python
class EvaluationDetailCreate(BaseModel):
    evaluation_id: int
    criteria_id: int
    score: float
    comment: Optional[str]
    
    @validator('score')
    def validate_score(cls, v, values):
        # Score should not exceed max_score from criteria
        return v

class ResourceCreate(BaseModel):
    team_id: int
    title: str
    description: Optional[str]
    resource_type: str  # "link", "file", "document"
    url: str
    tags: List[str] = []
```

---

### 🟢 FE1 (AI Mentoring + Evaluation UI)
**Mục tiêu:** Build AI mentoring dashboard and evaluation interface

**Công việc:**
- [ ] Create `frontend/src/services/mentoringService.js`
- [ ] Create `frontend/src/services/evaluationService.js`
- [ ] Create components:
  - [ ] `MentoringDashboard.jsx` (main page)
  - [ ] `MentoringLogList.jsx` (history)
  - [ ] `AIRecommendations.jsx` (AI suggestions display)
  - [ ] `RequestMentoringModal.jsx` (trigger AI analysis)
  - [ ] `EvaluationForm.jsx` (lecturer evaluates team)
  - [ ] `EvaluationCriteriaList.jsx` (criteria with scores)
  - [ ] `GradesSummary.jsx` (show final grades)
- [ ] Create page: `frontend/src/pages/MentoringPage.jsx`
- [ ] Create page: `frontend/src/pages/EvaluationPage.jsx`
- [ ] Add to lecturer navigation menu
- [ ] Style AI suggestions attractively (cards, icons)

**Success criteria:**
- Lecturer can request AI analysis for any team
- AI suggestions display within 5 seconds
- Evaluation form saves all criteria scores
- Grade summary calculates correctly

**UI Features:**
- [ ] AI suggestions shown as cards with icons
- [ ] Loading animation while AI processes
- [ ] Evaluation criteria as sliders (1-10 scale)
- [ ] Auto-save evaluation progress
- [ ] Export grades to CSV

---

### 🔵 FE2 (Peer Reviews + Submissions UI)
**Mục tiêu:** Build peer review and submission interfaces

**Công việc:**
- [ ] Create `frontend/src/services/peerReviewService.js`
- [ ] Create `frontend/src/services/submissionService.js`
- [ ] Create components:
  - [ ] `PeerReviewForm.jsx` (submit review)
  - [ ] `PeerReviewResults.jsx` (view anonymized feedback)
  - [ ] `TeamMemberRatings.jsx` (aggregate scores)
  - [ ] `MilestoneTimeline.jsx` (visual timeline)
  - [ ] `SubmissionForm.jsx` (submit for checkpoint)
  - [ ] `SubmissionHistory.jsx` (past submissions)
  - [ ] `ResourceLibrary.jsx` (team resources)
- [ ] Create page: `frontend/src/pages/PeerReviewsPage.jsx`
- [ ] Create page: `frontend/src/pages/SubmissionsPage.jsx`
- [ ] Add countdown timer for submission deadlines
- [ ] Add file upload component (if needed)

**Success criteria:**
- Students can review all team members
- Anonymized results viewable after sprint ends
- Submissions work before deadline
- Visual countdown for deadlines
- Resources organized and searchable

**UI Features:**
- [ ] Star rating component for scores
- [ ] Anonymous feedback display (no names)
- [ ] Milestone timeline with checkpoints
- [ ] Deadline countdown widget
- [ ] File drag-and-drop upload
- [ ] Resource cards with type icons

---

## 🧪 Testing Checklist Phase 4

### AI Mentoring Test
```
1. Lecturer navigates to Mentoring page
2. Selects team to analyze
3. Clicks "Get AI Suggestions"
4. Loading indicator appears
5. AI suggestions display within 5 seconds
6. Suggestions are relevant to team data
7. Log is saved for future reference
```

### Peer Review Test
```
1. Student opens Peer Review form
2. Sees all team members except self
3. Rates each member on 3 criteria
4. Submits review
5. Cannot submit another for same member/sprint
6. After sprint ends, sees anonymized results
7. Average scores calculated correctly
```

### Submission Test
```
1. Team views project milestones
2. Sees upcoming checkpoint deadline
3. Creates submission with content/file
4. Submits before deadline (success)
5. Tries to edit after deadline (blocked)
6. Lecturer grades submission
7. Team sees grade and feedback
```

---

## ⏰ Timeline Phase 4

| Ngày | Milestone | Owner |
|-----|-----------|-------|
| Feb 15-16 | AI integration + Peer Reviews BE | BE1, BE2 |
| Feb 17-18 | Milestones/Submissions + Evaluation BE | BE3, BE4 |
| Feb 19-20 | FE Mentoring + Peer Reviews UI | FE1, FE2 |
| Feb 21 | Full integration test + bug fixes | All |

---

## 🚨 Common Issues Phase 4

**Issue:** Gemini API rate limit exceeded  
→ Implement request queuing  
→ Add exponential backoff retry

**Issue:** AI suggestions not relevant  
→ Improve prompt with more context  
→ Add team history data to prompt

**Issue:** Peer review not anonymous  
→ Verify API response doesn't include reviewer_id  
→ Check frontend doesn't display reviewer info

**Issue:** Submission deadline check wrong  
→ Use UTC timezone for all datetime comparisons  
→ Add buffer time (5 min grace period)

**Issue:** File upload fails  
→ Check file size limits  
→ Verify storage service configured

---

## 🎓 Phase 4 Complete = MVP Ready!

Sau khi Phase 4 hoàn thành, hệ thống có đầy đủ:
- ✅ User management + Auth
- ✅ Academic management (classes, subjects, semesters)
- ✅ Project formation (topics, teams, projects)
- ✅ Agile workflow (sprints, tasks)
- ✅ Real-time communication (chat, video)
- ✅ AI-powered mentoring
- ✅ Peer reviews + Evaluation
- ✅ Milestones + Submissions

**Tổng: ~110 API endpoints + Full-featured UI**

---

## ✅ Khi xong Phase 4

1. Run full system test (all features)
2. Performance testing (load test)
3. Security audit (auth, CORS, SQL injection)
4. Documentation update (API docs, user manual)
5. Deploy to staging environment
6. User acceptance testing (UAT)

---

**Chúc bạn làm việc vui vẻ! 🚀**  
*Phase 4 hoàn thành = CollabSphere MVP ready for production! 🎉*
