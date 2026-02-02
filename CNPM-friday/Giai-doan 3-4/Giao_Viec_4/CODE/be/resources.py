"""
Resources API Endpoints - Phase 4
Copy file này vào: backend/app/api/v1/resources.py
Sau đó register router trong api.py
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.all_models import Resource, Project, Team, TeamMember, User

from pydantic import BaseModel, Field

# ========== SCHEMAS ==========

class ResourceCreate(BaseModel):
    project_id: Optional[int] = None
    team_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    resource_type: str = Field(..., description="Type: document, link, video, image, etc.")
    url: str = Field(..., description="URL hoặc đường dẫn tới resource")

class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[str] = None
    url: Optional[str] = None

class ResourceResponse(BaseModel):
    resource_id: int
    project_id: Optional[int]
    team_id: Optional[int]
    title: str
    description: Optional[str]
    resource_type: str
    url: str
    uploaded_by: UUID
    uploader_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== ROUTER ==========

router = APIRouter()


@router.post("/", response_model=ResourceResponse, status_code=201)
async def create_resource(
    resource_data: ResourceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Tạo resource mới.
    Phải có project_id hoặc team_id.
    """
    if not resource_data.project_id and not resource_data.team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phải có project_id hoặc team_id"
        )
    
    # Nếu là team resource, kiểm tra team member
    if resource_data.team_id:
        member_check = await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == resource_data.team_id,
                TeamMember.user_id == current_user.user_id
            )
        )
        if not member_check.scalar() and current_user.role_id not in [1, 4]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn phải là thành viên của team mới có thể tạo resource"
            )
    
    new_resource = Resource(
        project_id=resource_data.project_id,
        team_id=resource_data.team_id,
        title=resource_data.title,
        description=resource_data.description,
        resource_type=resource_data.resource_type,
        url=resource_data.url,
        uploaded_by=current_user.user_id
    )
    db.add(new_resource)
    await db.commit()
    await db.refresh(new_resource)
    
    return ResourceResponse(
        resource_id=new_resource.resource_id,
        project_id=new_resource.project_id,
        team_id=new_resource.team_id,
        title=new_resource.title,
        description=new_resource.description,
        resource_type=new_resource.resource_type,
        url=new_resource.url,
        uploaded_by=new_resource.uploaded_by,
        uploader_name=current_user.full_name,
        created_at=new_resource.created_at
    )


@router.get("/", response_model=List[ResourceResponse])
async def list_resources(
    project_id: Optional[int] = None,
    team_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách resources.
    Có thể filter theo project_id, team_id, hoặc resource_type.
    """
    query = select(Resource)
    
    if project_id:
        query = query.where(Resource.project_id == project_id)
    if team_id:
        query = query.where(Resource.team_id == team_id)
    if resource_type:
        query = query.where(Resource.resource_type == resource_type)
    
    query = query.order_by(Resource.created_at.desc())
    
    result = await db.execute(query)
    resources = result.scalars().all()
    
    response = []
    for resource in resources:
        uploader = await db.get(User, resource.uploaded_by)
        response.append(ResourceResponse(
            resource_id=resource.resource_id,
            project_id=resource.project_id,
            team_id=resource.team_id,
            title=resource.title,
            description=resource.description,
            resource_type=resource.resource_type,
            url=resource.url,
            uploaded_by=resource.uploaded_by,
            uploader_name=uploader.full_name if uploader else "Unknown",
            created_at=resource.created_at
        ))
    
    return response


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lấy chi tiết resource."""
    resource = await db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource không tồn tại"
        )
    
    uploader = await db.get(User, resource.uploaded_by)
    
    return ResourceResponse(
        resource_id=resource.resource_id,
        project_id=resource.project_id,
        team_id=resource.team_id,
        title=resource.title,
        description=resource.description,
        resource_type=resource.resource_type,
        url=resource.url,
        uploaded_by=resource.uploaded_by,
        uploader_name=uploader.full_name if uploader else "Unknown",
        created_at=resource.created_at
    )


@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: int,
    update_data: ResourceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cập nhật resource.
    Chỉ người upload hoặc admin mới có quyền cập nhật.
    """
    resource = await db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource không tồn tại"
        )
    
    if resource.uploaded_by != current_user.user_id and current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền cập nhật resource này"
        )
    
    if update_data.title is not None:
        resource.title = update_data.title
    if update_data.description is not None:
        resource.description = update_data.description
    if update_data.resource_type is not None:
        resource.resource_type = update_data.resource_type
    if update_data.url is not None:
        resource.url = update_data.url
    
    await db.commit()
    await db.refresh(resource)
    
    return ResourceResponse(
        resource_id=resource.resource_id,
        project_id=resource.project_id,
        team_id=resource.team_id,
        title=resource.title,
        description=resource.description,
        resource_type=resource.resource_type,
        url=resource.url,
        uploaded_by=resource.uploaded_by,
        uploader_name=current_user.full_name,
        created_at=resource.created_at
    )


@router.delete("/{resource_id}", status_code=204)
async def delete_resource(
    resource_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Xóa resource.
    Chỉ người upload hoặc admin mới có quyền xóa.
    """
    resource = await db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource không tồn tại"
        )
    
    if resource.uploaded_by != current_user.user_id and current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xóa resource này"
        )
    
    await db.delete(resource)
    await db.commit()
    return None
