# 📑 GIAO_VIEC_4 - Phase 4 Index

**Mục tiêu:** AI Features, Advanced Evaluation, Peer Reviews, Submissions

## ✅ Đọc theo thứ tự:
1. **giao_viec.md** ⭐ (phân công chi tiết từng người)
2. TASK_ASSIGNMENT_PHASE4.md (chi tiết kỹ thuật - endpoints, business rules)
3. SCHEMAS/phase4_schemas.py (Pydantic models)
4. CODE/be/ (BE starter code - copy vào backend/app/api/v1/)
5. CODE/fe/ (FE services - copy vào frontend/src/services/)

---

## 📂 Cấu trúc thư mục

```
Giao_Viec_4/
├── INDEX.md (file này)
├── giao_viec.md ⭐ (đọc đầu tiên)
├── TASK_ASSIGNMENT_PHASE4.md ✅
├── CODE/
│   ├── be/
│   │   ├── mentoring.py     ✅ (copy → backend/app/api/v1/mentoring.py)
│   │   ├── peer_reviews.py  ✅ (copy → backend/app/api/v1/peer_reviews.py)
│   │   ├── milestones.py    ✅ (copy → backend/app/api/v1/milestones.py)
│   │   ├── submissions.py   ✅ (copy → backend/app/api/v1/submissions.py)
│   │   └── resources.py     ✅ (copy → backend/app/api/v1/resources.py)
│   └── fe/
│       ├── mentoringService.js   ✅ (copy → frontend/src/services/)
│       ├── peerReviewService.js  ✅ (copy → frontend/src/services/)
│       ├── milestoneService.js   ✅ (copy → frontend/src/services/)
│       ├── submissionService.js  ✅ (copy → frontend/src/services/)
│       └── resourceService.js    ✅ (copy → frontend/src/services/)
└── SCHEMAS/
    └── phase4_schemas.py ✅ (All Phase 4 Pydantic schemas)
```

---

## 🎯 Mục tiêu Phase 4

| Feature | Owner | Priority | Endpoints |
|---------|-------|----------|-----------|
| AI Mentoring (Gemini) | BE1 | 🔴 HIGH | 6 |
| Peer Reviews | BE2 | 🔴 HIGH | 6 |
| Milestones & Checkpoints | BE3 | 🟡 MEDIUM | 8 |
| Submissions | BE3 | 🟡 MEDIUM | 6 |
| Resources | BE4 | 🟢 LOW | 5 |
| AI + Evaluation UI | FE1 | 🔴 HIGH | 2 pages |
| Peer Reviews + Submissions UI | FE2 | 🟡 MEDIUM | 2 pages |

---

## 📊 API Status

**Tổng endpoints sau Phase 3:** ~80 endpoints
**Cần thêm Phase 4:** ~30 endpoints
**Target Phase 4:** ~110 endpoints total

---

## 📋 Quick Start

### Backend:
```bash
# 1. Copy files
cp Giao_Viec_4/CODE/be/*.py backend/app/api/v1/

# 2. Uncomment routers trong api.py
# Tìm dòng "# PHASE 4 ENDPOINTS" và bỏ comment

# 3. Cấu hình Gemini API Key trong .env
GOOGLE_API_KEY=your_api_key_here

# 4. Restart server
docker-compose restart backend
```

### Frontend:
```bash
# 1. Copy service files
cp Giao_Viec_4/CODE/fe/*.js frontend/src/services/
```

---

## 🔴 IMPORTANT NOTES

1. **AI Service**: Cần `GOOGLE_API_KEY` trong `.env` để dùng Gemini API
2. **Peer Reviews ẩn danh**: FE không được hiển thị reviewer info cho students
3. **Submission rules**: Không thể sửa/xóa sau khi đã chấm điểm
4. **Role checks**: Lecturer (role_id=4) mới có quyền chấm điểm

---

---

## 🎓 Phase 4 = MVP Complete!

Sau Phase 4, CollabSphere sẽ có đầy đủ chức năng cho một hệ thống quản lý học tập dựa trên dự án hoàn chỉnh.

---

**🚀 Ready to start Phase 4!**
