# 📑 GIAO_VIEC_3 - Phase 3 Index

**Mục tiêu:** Real-time Features (Chat, Messages, Meetings, Video Calls)

## ✅ Đọc theo thứ tự:
1. **giao_viec.md** ⭐ (phân công chi tiết từng người)
2. TASK_ASSIGNMENT_PHASE3.md (chi tiết kỹ thuật)
3. SCHEMAS/phase3_schemas.py (Pydantic models)
4. CODE/be/ (BE starter code - copy vào backend/app/api/v1/)
5. CODE/fe/ (FE services - copy vào frontend/src/services/)

---

## 📂 Cấu trúc thư mục

```
Giao_Viec_3/
├── INDEX.md (file này)
├── giao_viec.md ⭐ (đọc đầu tiên)
├── TASK_ASSIGNMENT_PHASE3.md
├── CODE/
│   ├── be/
│   │   ├── channels.py  ✅ (copy → backend/app/api/v1/channels.py)
│   │   ├── messages.py  ✅ (copy → backend/app/api/v1/messages.py)
│   │   └── meetings.py  ✅ (copy → backend/app/api/v1/meetings.py)
│   └── fe/
│       ├── chatService.js    ✅ (copy → frontend/src/services/)
│       ├── socketService.js  ✅ (copy → frontend/src/services/)
│       └── meetingService.js ✅ (copy → frontend/src/services/)
└── SCHEMAS/
    └── phase3_schemas.py ✅ (Channel, Message, Meeting schemas)
```

---

## 🎯 Mục tiêu Phase 3

| Feature | Owner | Priority | Files |
|---------|-------|----------|-------|
| Socket.IO infrastructure | BE1 | 🔴 HIGH | socket_manager.py |
| Channels + Messages API | BE2 | 🔴 HIGH | channels.py, messages.py |
| Meetings API | BE3 | 🟡 MEDIUM | meetings.py |
| Semesters completion | BE4 | 🟢 LOW | semesters.py |
| Chat UI + Real-time | FE1 | 🔴 HIGH | ChatPage.jsx |
| Meetings UI + Video | FE2 | 🟡 MEDIUM | MeetingsPage.jsx |

---

## 📋 Quick Start

### Backend:
```bash
# 1. Copy files
cp Giao_Viec_3/CODE/be/*.py backend/app/api/v1/

# 2. Uncomment routers trong api.py
# Tìm dòng "# PHASE 3 ENDPOINTS" và bỏ comment

# 3. Restart server
docker-compose restart backend
```

### Frontend:
```bash
# 1. Copy service files
cp Giao_Viec_3/CODE/fe/*.js frontend/src/services/

# 2. Install socket.io-client và peerjs nếu chưa có
cd frontend && npm install socket.io-client peerjs
```

---

## 📊 API Status sau Phase 2

**Tổng endpoints đã có:** ~60 endpoints
**Cần thêm Phase 3:** ~20 endpoints (Channels 4, Messages 5, Meetings 6, Semesters 4)
**Target Phase 3:** ~80 endpoints total

---

**🚀 Ready to start Phase 3!**
