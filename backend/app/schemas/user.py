from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr

# Dữ liệu chung
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True

# Dữ liệu cần để tạo User (Client gửi lên)
class UserCreate(UserBase):
    password: str
    role_id: int  # 1=Admin, 5=Student (tùy quy định DB của bạn)

# Dữ liệu User trả về cho Client (Không được trả password!)
class UserResponse(UserBase):
    user_id: UUID
    role_id: int
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True  # Để đọc được dữ liệu từ SQLAlchemy model