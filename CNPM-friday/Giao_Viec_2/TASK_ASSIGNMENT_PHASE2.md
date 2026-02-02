# 👥 TASK ASSIGNMENT - Phase 2 (Ổn định + Mở rộng)

## BE1 (Lead) - 10h
- Kiểm tra toàn bộ auth flow (register/login/me)
- Chuẩn hóa config DB (Supabase pooler nếu cần)
- Review các fix từ BE2/BE3/BE4
- Chạy TESTING_GUIDE.md flows mỗi ngày

## BE2 - 6h
- Bổ sung/chuẩn hóa schema response cho Topics
- Đồng bộ docs vs code (TopicResponse mismatch)
- Rà lại Topics endpoints, sửa lỗi nhỏ nếu có

## BE3 - 6h
- Hoàn thiện Teams endpoints (join/leave/finalize edge cases)
- Kiểm tra join_code logic + lỗi duplicate join

## BE4 - 6h
- Hoàn thiện Tasks/Sprints endpoints
- Rà logic status transition TODO→DOING→DONE

## FE1 - 8h
- Kết nối Lecturer dashboard với API thật
- Hiển thị list topics, approve/reject
- Add loading/error UI

## FE2 - 8h
- Kết nối Student dashboard với API thật
- Create team + join code
- View team details

---

## Definition of Done (Phase 2)
- Auth register/login ổn định 100%
- Tất cả API gọi được từ FE (không 404/422)
- FE dashboards hiển thị dữ liệu thật
- Không còn mismatch giữa docs và code
