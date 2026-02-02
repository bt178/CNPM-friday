# 🔴 CRITICAL FIXES (phải làm trước)

## 1) Đồng bộ schema vs doc
- `Giao_Viec/IMPLEMENTATION_GUIDE.md` nói có `TopicResponse`
- `Giao_Viec/SCHEMAS/topic.py` **chưa có** `TopicResponse`
**Fix:** thêm `TopicResponse` hoặc cập nhật doc cho khớp.

## 2) Đồng bộ INDEX.md vs file thực tế
- `Giao_Viec/INDEX.md` vẫn nhắc các file đã bị xóa (00_START_HERE, QUICK_START...)
**Fix:** update INDEX.md để tránh nhầm lẫn.

## 3) Auth config/DB
- Đảm bảo backend dùng đúng DATABASE_URL (Supabase)
- Xác nhận DNS/Supabase pooler host hoạt động

## 4) FE API baseURL
- FE phải gọi `/api/v1/...` (không /auth trực tiếp)
- Không hardcode sai baseURL khi build

---

## Nếu chưa xong CRITICAL FIXES → **không bắt đầu feature mới**
