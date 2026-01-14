# How To Use Backend

## 1. Database PostgreSQL

```
Database: collabsphere_db
Username: postgres
Password: 117206
Port: 5432
```

---

## 2. run sever

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
python scripts/seed_data.py
python -m uvicorn app.main:app --reload --port 8000
```

Swagger UI: http://localhost:8000/docs

---

## 3. test acc

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@collabsphere.com | admin123 |
| Lecturer | lecturer@collabsphere.com | lecturer123 |
| Head of Dept | head_dept@collabsphere.com | head123 |
| Student 1 | student1@collabsphere.com | student123 |
| Student 2 | student2@collabsphere.com | student123 |

---

## 4. role

### Topics (Đề tài)
- **Tạo**: Lecturer
- **Duyệt**: Head of Dept / Admin
- **Xem**: Tất cả (Student chỉ thấy đã duyệt)

### Teams
- **Tạo / Join**: Student
- **Finalize**: Lecturer
- Max 6 người/nhóm

### Tasks (TODO)
- **CRUD**: Team members
- **Xóa**: Team Leader only
- Student chỉ thấy task của team mình

---

## 5. Lưu Ý

- Tất cả API cần token (lấy từ login)
- Status không phân biệt hoa thường
- dept_id: 1 hoặc 2
- class_id: phải tồn tại trong DB [trong posrgresql nếu được hãy tự kết nối đi kh thì tạo mới db localhost test cx dc]
