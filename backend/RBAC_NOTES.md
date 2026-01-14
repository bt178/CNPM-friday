# Role-Based Access Control (RBAC) - Backend API

## Roles (theo database)

| role_id | Role Name | Mô tả |
|---------|-----------|-------|
| 1 | ADMIN | Quản trị viên hệ thống |
| 2 | STAFF | Nhân viên |
| 3 | HEAD_DEPT | Trưởng khoa/bộ môn |
| 4 | LECTURER | Giảng viên |
| 5 | STUDENT | Sinh viên |

---

## BE-PROJ-01: Topics (Đề tài)

| Endpoint | Chức năng | Roles được phép |
|----------|-----------|-----------------|
| `POST /topics` | Tạo đề tài mới | ADMIN, LECTURER |
| `GET /topics` | Xem danh sách đề tài | Tất cả (Student chỉ thấy APPROVED) |
| `GET /topics/{id}` | Xem chi tiết đề tài | Tất cả (Student chỉ thấy APPROVED) |
| `PUT /topics/{id}` | Cập nhật đề tài | ADMIN, Creator (Lecturer) |
| `DELETE /topics/{id}` | Xóa đề tài | ADMIN, Creator (Lecturer) |
| `PATCH /topics/{id}/status` | Chuyển trạng thái | Xem bên dưới |

### Status Transitions (Đề tài)
```
DRAFT → PENDING     : Creator (Lecturer) submit
PENDING → APPROVED  : HEAD_DEPT hoặc ADMIN approve
PENDING → DRAFT     : HEAD_DEPT hoặc ADMIN reject
```

---

## BE-TEAM-01: Teams (Nhóm)

| Endpoint | Chức năng | Roles được phép |
|----------|-----------|-----------------|
| `POST /teams` | Tạo nhóm mới | STUDENT only |
| `GET /teams` | Xem danh sách nhóm | Tất cả |
| `GET /teams/{id}` | Xem chi tiết + members | Tất cả |
| `POST /teams/join` | Join nhóm bằng code | STUDENT only |
| `POST /teams/{id}/leave` | Rời nhóm | STUDENT (member, không phải leader) |
| `PATCH /teams/{id}/finalize` | Chốt nhóm | ADMIN, LECTURER |

### Business Logic (Teams)
- Student tạo nhóm → tự động thành Leader
- Join code được tự động generate (6 ký tự)
- Sau khi finalize → không thể join/leave

---

## BE-TASK-01: Tasks (Công việc)

| Endpoint | Chức năng | Roles được phép |
|----------|-----------|-----------------|
| `POST /tasks` | Tạo task mới | Tất cả (authenticated) |
| `GET /tasks` | Xem danh sách tasks | Tất cả (authenticated) |
| `GET /tasks/{id}` | Xem chi tiết task | Tất cả (authenticated) |
| `PUT /tasks/{id}` | Cập nhật task | Tất cả (authenticated) |
| `DELETE /tasks/{id}` | Xóa task | Tất cả (authenticated) |

### Status Transitions (Tasks)
```
TODO → DOING   : Bắt đầu làm
DOING → TODO   : Quay lại backlog
DOING → DONE   : Hoàn thành
DONE → DOING   : Mở lại task
```

---

## Summary Diagram

```
┌─────────────┬─────────────────────────────────────────────────────────┐
│   Role      │  Topics         │  Teams              │  Tasks         │
├─────────────┼─────────────────┼─────────────────────┼────────────────┤
│ ADMIN       │  CRUD + Approve │  View + Finalize    │  CRUD          │
│ HEAD_DEPT   │  Approve only   │  View               │  CRUD          │
│ LECTURER    │  CRUD (own)     │  View + Finalize    │  CRUD          │
│ STUDENT     │  View (approved)│  Create/Join/Leave  │  CRUD          │
└─────────────┴─────────────────┴─────────────────────┴────────────────┘
```
