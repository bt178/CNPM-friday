# 📑 GIAO VIỆC - Hướng Dẫn Sử Dụng Folder

**⚠️ Bạn chỉ cần đọc file này trước! Sau đó xem file tương ứng với công việc của mình.**

---

## 🎯 Bước 1: Xác Định Công Việc Của Bạn

| Bạn là | Công việc | File chính |
|--------|---------|-----------|
| **BE2** | Topics & Evaluation APIs | `TASK_ASSIGNMENT.md` → tìm "BE2" |
| **BE3** | Teams & Join Logic APIs | `TASK_ASSIGNMENT.md` → tìm "BE3" |
| **BE4** | Tasks & Sprints APIs | `TASK_ASSIGNMENT.md` → tìm "BE4" |
| **FE1** | Lecturer Dashboard | `TASK_ASSIGNMENT.md` → tìm "FE1" |
| **FE2** | Student Dashboard | `TASK_ASSIGNMENT.md` → tìm "FE2" |
| **BE1** | Code review & Testing | `TASK_ASSIGNMENT.md` → tìm "BE1" |

---

## 📚 Bước 2: Đọc Theo Thứ Tự Này

### Cho Backend (BE2, BE3, BE4):

**1️⃣ Công việc cụ thể của bạn:**
- Mở → `TASK_ASSIGNMENT.md` → tìm tên bạn (BE2/BE3/BE4) → đọc kỹ phần "Detailed Tasks"
- **Nội dung:** Chính xác những gì bạn phải làm, deadline, test case

**2️⃣ Cách code từng bước:**
- Mở → `IMPLEMENTATION_GUIDE.md` → tìm tên bạn → follow từng bước
- **Nội dung:** Copy code, đăng ký router, chỉnh sửa, save

**3️⃣ Cách test:**
- Mở → `TESTING_GUIDE.md` → tìm "Flow 1/2/3" tương ứng với bạn
- **Nội dung:** Chạy curl command để test endpoints

**4️⃣ Tham khảo nhanh:**
- Mở → `QUICK_REFERENCE.md` → tìm command/curl bạn cần
- **Nội dung:** Các lệnh PowerShell, curl, endpoints

---

### Cho Frontend (FE1, FE2):

**1️⃣ Công việc cụ thể của bạn:**
- Mở → `TASK_ASSIGNMENT.md` → tìm "FE1" hoặc "FE2" → đọc kỹ
- **Nội dung:** Chính xác những UI component bạn phải tạo

**2️⃣ Cách code:**
- Mở → `IMPLEMENTATION_GUIDE.md` → tìm "FE1" hoặc "FE2"
- **Nội dung:** JSX template, component structure, API calls

**3️⃣ API reference:**
- Mở → `QUICK_REFERENCE.md` → phần "API Endpoints"
- **Nội dung:** Các endpoint tương ứng với component của bạn

---

### Cho Lead (BE1):

**1️⃣ Công việc cụ thể:**
- Mở → `TASK_ASSIGNMENT.md` → tìm "BE1"
- **Nội dung:** Review code, test, fix bugs

**2️⃣ Cách test:**
- Mở → `TESTING_GUIDE.md` → chạy 3 flows (Flow 1, 2, 3) hàng ngày
- **Nội dung:** Integration test từ A-Z

---

## 📂 Code & Schema Folder

### `CODE/` folder:
```
CODE/
├── topics.py             ← Copy vào backend/app/api/v1/topics.py (BE2)
├── teams.py              ← Copy vào backend/app/api/v1/teams.py (BE3)
├── tasks.py              ← Copy vào backend/app/api/v1/tasks.py (BE4)
├── STARTER_BE2_TOPICS.py ← (Optional: tham khảo cấu trúc)
├── STARTER_BE3_TEAMS.py  ← (Optional: tham khảo cấu trúc)
└── STARTER_BE4_TASKS.py  ← (Optional: tham khảo cấu trúc)
```

### `SCHEMAS/` folder:
```
SCHEMAS/
├── topic.py  ← Copy vào backend/app/schemas/topic.py (BE2)
├── team.py   ← Copy vào backend/app/schemas/team.py (BE3)
└── task.py   ← Copy vào backend/app/schemas/task.py (BE4)
```

### `DOCS/` folder (same as root):
```
DOCS/ = Root folder
- TASK_ASSIGNMENT.md     (bạn đang dùng)
- IMPLEMENTATION_GUIDE.md (bạn đang dùng)
- TESTING_GUIDE.md       (bạn đang dùng)
- QUICK_REFERENCE.md     (bạn đang dùng)
```

---

## ✅ Quick Checklist

Hôm nay làm:
- [ ] Đọc `TASK_ASSIGNMENT.md` - tìm tên bạn
- [ ] Chạy `docker-compose up` (nếu chưa chạy)
- [ ] Chạy `curl -X POST http://localhost:8000/api/v1/admin/init-db`
- [ ] Đọc `IMPLEMENTATION_GUIDE.md` - phần của bạn
- [ ] Copy code từ `CODE/` folder
- [ ] Paste vào project
- [ ] Test theo `TESTING_GUIDE.md`

---

## 🚨 QUAN TRỌNG

**Folder đã được làm gọn, không còn file dư.**
Chỉ cần dùng 4 file chính dưới đây:

**Chính file quan trọng nhất:**
1. `TASK_ASSIGNMENT.md` ⭐ (công việc của bạn)
2. `IMPLEMENTATION_GUIDE.md` ⭐ (cách code)
3. `TESTING_GUIDE.md` ⭐ (cách test)
4. `QUICK_REFERENCE.md` ⭐ (command nhanh)

---

## 🎯 Summary

```
Làm gì? → Tìm trong TASK_ASSIGNMENT.md
Cách làm? → Tìm trong IMPLEMENTATION_GUIDE.md
Test thế nào? → Tìm trong TESTING_GUIDE.md
Command gì? → Tìm trong QUICK_REFERENCE.md
```

**Start bây giờ!** 🚀
