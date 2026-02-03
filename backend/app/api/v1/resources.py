"""
BE4 - Resource Management Endpoints
Phase 4: Learning Materials & Project Resources

Endpoints:
- POST /resources - Share a new resource
- GET /resources - List resources (filter by team_id, class_id, type)
- GET /resources/{id} - Get resource details
- DELETE /resources/{id} - Remove resource

Role Permissions (from permission matrix):
- Lecturer: Upload/Download learning materials ✓
- Student: Download/View materials ✓
- Staff/Admin: Full access ✓
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timezone
import json

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.all_models import User, Resource, Team, TeamMember, AcademicClass
from app.schemas.resource import (
    ResourceCreate, ResourceUpdate, ResourceResponse, ResourceListResponse
)

router = APIRouter()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def can_upload_resource(user: User) -> bool:
    """Check if user can upload resources (Lecturer, Staff, Admin)"""
    # Role IDs: 1=Admin, 2=Staff, 3=Head_Dept, 4=Lecturer, 5=Student
    return user.role_id in [1, 2, 3, 4]


def can_delete_resource(user: User, resource: Resource) -> bool:
    """Check if user can delete resource (uploader or admin)"""
    if user.role_id in [1, 2]:  # Admin or Staff
        return True
    return resource.uploaded_by == user.user_id


async def check_team_access(db: AsyncSession, user: User, team_id: int) -> bool:
    """Check if user has access to the team"""
    if user.role_id in [1, 2, 3, 4]:  # Admin, Staff, Head_Dept, Lecturer
        return True
    
    # Check if student is member of the team
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user.user_id
        )
    )
    return result.scalars().first() is not None


# ============================================================================
# RESOURCE ENDPOINTS
# ============================================================================

@router.post("", response_model=ResourceResponse, status_code=201)
async def create_resource(
    resource_in: ResourceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Share a new resource (Lecturer, Staff, Admin only for upload).
    
    Request:
        {
            "team_id": 1,
            "title": "Project Guidelines",
            "description": "Official project setup guide",
            "resource_type": "document",
            "url": "https://drive.google.com/...",
            "tags": ["guide", "setup"]
        }
    """
    if not can_upload_resource(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers, staff, or admins can upload resources"
        )
    
    # Validate team if provided
    if resource_in.team_id:
        team_result = await db.execute(
            select(Team).where(Team.team_id == resource_in.team_id)
        )
        if not team_result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team {resource_in.team_id} not found"
            )
    
    # Validate class if provided
    if resource_in.class_id:
        class_result = await db.execute(
            select(AcademicClass).where(AcademicClass.class_id == resource_in.class_id)
        )
        if not class_result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Class {resource_in.class_id} not found"
            )
    
    # Convert tags list to JSON string for storage
    tags_json = json.dumps(resource_in.tags) if resource_in.tags else None
    
    # Create resource
    new_resource = Resource(
        team_id=resource_in.team_id,
        class_id=resource_in.class_id,
        uploaded_by=current_user.user_id,
        file_url=resource_in.url,  # Using file_url for URL storage
        file_type=resource_in.resource_type
    )
    
    db.add(new_resource)
    await db.commit()
    await db.refresh(new_resource)
    
    return ResourceResponse(
        resource_id=new_resource.resource_id,
        team_id=new_resource.team_id,
        class_id=new_resource.class_id,
        title=resource_in.title,
        description=resource_in.description,
        resource_type=resource_in.resource_type,
        url=resource_in.url,
        file_url=new_resource.file_url,
        file_type=new_resource.file_type,
        tags=resource_in.tags,
        uploaded_by=new_resource.uploaded_by,
        uploader_name=current_user.full_name,
        created_at=datetime.now(timezone.utc)
    )


@router.get("", response_model=ResourceListResponse)
async def list_resources(
    team_id: Optional[int] = Query(None, description="Filter by team"),
    class_id: Optional[int] = Query(None, description="Filter by class"),
    resource_type: Optional[str] = Query(None, description="Filter by type (link, file, document)"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List resources with optional filters.
    Students can only see resources for their teams/classes.
    
    Query params:
        ?team_id=1
        ?class_id=2
        ?resource_type=document
        ?page=1&per_page=20
    """
    query = select(Resource, User).join(User, Resource.uploaded_by == User.user_id)
    
    # Apply filters
    if team_id:
        # Check team access for students
        if current_user.role_id == 5:  # Student
            has_access = await check_team_access(db, current_user, team_id)
            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this team's resources"
                )
        query = query.where(Resource.team_id == team_id)
    
    if class_id:
        query = query.where(Resource.class_id == class_id)
    
    if resource_type:
        query = query.where(Resource.file_type == resource_type.lower())
    
    # For students without filters, show only their accessible resources
    if current_user.role_id == 5 and not team_id and not class_id:
        # Get student's team IDs
        team_ids_result = await db.execute(
            select(TeamMember.team_id).where(TeamMember.user_id == current_user.user_id)
        )
        team_ids = [t[0] for t in team_ids_result.all()]
        
        if team_ids:
            query = query.where(
                or_(
                    Resource.team_id.in_(team_ids),
                    Resource.class_id.isnot(None)  # Class resources are visible
                )
            )
        else:
            # Only show class resources if student has no teams
            query = query.where(Resource.class_id.isnot(None))
    
    # Pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    rows = result.all()
    
    # Count total
    count_query = select(Resource)
    if team_id:
        count_query = count_query.where(Resource.team_id == team_id)
    if class_id:
        count_query = count_query.where(Resource.class_id == class_id)
    
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    resources = []
    for resource, uploader in rows:
        resources.append(ResourceResponse(
            resource_id=resource.resource_id,
            team_id=resource.team_id,
            class_id=resource.class_id,
            title=None,  # Would need model update for title
            description=None,
            resource_type=resource.file_type,
            url=resource.file_url,
            file_url=resource.file_url,
            file_type=resource.file_type,
            tags=[],
            uploaded_by=resource.uploaded_by,
            uploader_name=uploader.full_name,
            created_at=None
        ))
    
    return ResourceListResponse(
        resources=resources,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource_details(
    resource_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information of a specific resource.
    """
    result = await db.execute(
        select(Resource, User)
        .join(User, Resource.uploaded_by == User.user_id)
        .where(Resource.resource_id == resource_id)
    )
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource {resource_id} not found"
        )
    
    resource, uploader = row
    
    # Check access for students
    if current_user.role_id == 5 and resource.team_id:
        has_access = await check_team_access(db, current_user, resource.team_id)
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this resource"
            )
    
    return ResourceResponse(
        resource_id=resource.resource_id,
        team_id=resource.team_id,
        class_id=resource.class_id,
        title=None,
        description=None,
        resource_type=resource.file_type,
        url=resource.file_url,
        file_url=resource.file_url,
        file_type=resource.file_type,
        tags=[],
        uploaded_by=resource.uploaded_by,
        uploader_name=uploader.full_name,
        created_at=None
    )


@router.delete("/{resource_id}", status_code=204)
async def delete_resource(
    resource_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a resource.
    Only the uploader or admin/staff can delete.
    """
    result = await db.execute(
        select(Resource).where(Resource.resource_id == resource_id)
    )
    resource = result.scalars().first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource {resource_id} not found"
        )
    
    if not can_delete_resource(current_user, resource):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this resource"
        )
    
    await db.delete(resource)
    await db.commit()
    
    return None
