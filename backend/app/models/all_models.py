"""
SQLAlchemy 2.0 Models for CollabSphere Application.
Updated: Added Cascade Deletes and Timezone Awareness for Production Stability.
"""
from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Column,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


# ==========================================
# CLUSTER 1: SYSTEM IDENTITY & ACCESS
# ==========================================


class Role(Base):
    """Role model for user roles (ADMIN, STAFF, HEAD_DEPT, LECTURER, STUDENT)."""
    __tablename__ = "roles"

    role_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column(String, unique=True)

    users: Mapped[list["User"]] = relationship("User", back_populates="role")


class Department(Base):
    __tablename__ = "departments"

    dept_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dept_name: Mapped[str] = mapped_column(String, unique=True)

    dept_head_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=True
    )

    users: Mapped[list["User"]] = relationship("User", back_populates="department", foreign_keys="[User.dept_id]")
    subjects: Mapped[list["Subject"]] = relationship("Subject", back_populates="department")
    topics: Mapped[list["Topic"]] = relationship("Topic", back_populates="department")

    # FIX: Explicitly specify foreign_keys to resolve ambiguity
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="department",
        foreign_keys="User.dept_id"  # This tells SQLAlchemy which FK to use
    )

    dept_head: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[dept_head_id],
        post_update=True  # Prevents circular dependency issues
    )

    subjects: Mapped[list["Subject"]] = relationship(
        "Subject",
        back_populates="department"
    )


class User(Base):
    """User model storing Admin, Staff, Lecturer, and Student accounts."""
    __tablename__ = "users"

    # Primary fields
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid()
    )
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.role_id"))
    dept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("departments.dept_id"),
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    role: Mapped["Role"] = relationship("Role", back_populates="users")
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="users", foreign_keys=[dept_id])

    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )

    system_settings: Mapped[list["SystemSetting"]] = relationship("SystemSetting", back_populates="updated_by_user")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="actor")
    
    # Lecturer relations
    taught_classes: Mapped[list["AcademicClass"]] = relationship("AcademicClass", back_populates="lecturer", foreign_keys="AcademicClass.lecturer_id")
    created_topics: Mapped[list["Topic"]] = relationship("Topic", back_populates="creator", foreign_keys="Topic.creator_id")
    created_milestones: Mapped[list["Milestone"]] = relationship("Milestone", back_populates="creator", foreign_keys="Milestone.created_by")
    evaluations: Mapped[list["Evaluation"]] = relationship("Evaluation", back_populates="evaluator", foreign_keys="Evaluation.evaluator_id")
    mentoring_logs: Mapped[list["MentoringLog"]] = relationship("MentoringLog", back_populates="lecturer", foreign_keys="MentoringLog.lecturer_id")

    # Student relations
    enrollments: Mapped[list["ClassEnrollment"]] = relationship("ClassEnrollment", back_populates="student")
    led_teams: Mapped[list["Team"]] = relationship("Team", back_populates="leader", foreign_keys="Team.leader_id")
    team_memberships: Mapped[list["TeamMember"]] = relationship("TeamMember", back_populates="student")
    assigned_tasks: Mapped[list["Task"]] = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    submissions: Mapped[list["Submission"]] = relationship("Submission", back_populates="submitter", foreign_keys="Submission.submitted_by")
    
    # Collaboration
    organized_meetings: Mapped[list["Meeting"]] = relationship("Meeting", back_populates="organizer", foreign_keys="Meeting.organizer_id")
    sent_messages: Mapped[list["Message"]] = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    uploaded_resources: Mapped[list["Resource"]] = relationship("Resource", back_populates="uploader", foreign_keys="Resource.uploaded_by")
    
    # Peer Reviews
    peer_reviews_given: Mapped[list["PeerReview"]] = relationship("PeerReview", back_populates="reviewer", foreign_keys="PeerReview.reviewer_id")
    peer_reviews_received: Mapped[list["PeerReview"]] = relationship("PeerReview", back_populates="reviewee", foreign_keys="PeerReview.reviewee_id")

    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

class SystemSetting(Base):
    """System settings model."""
    __tablename__ = "system_settings"

    config_key: Mapped[str] = mapped_column(String, primary_key=True)
    config_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_encrypted: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_by: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)

    updated_by_user: Mapped[Optional["User"]] = relationship("User", back_populates="system_settings")


class AuditLog(Base):
    """Audit log model."""
    __tablename__ = "audit_logs"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    action: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    target_entity: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    actor: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")


# ==========================================
# CLUSTER 2: ACADEMIC MANAGEMENT
# ==========================================


class Semester(Base):
    __tablename__ = "semesters"
    
    semester_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    semester_code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    semester_name: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    academic_classes: Mapped[list["AcademicClass"]] = relationship("AcademicClass", back_populates="semester")

class Subject(Base):
    __tablename__ = "subjects"
    
    subject_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_code: Mapped[str] = mapped_column(String, unique=True)
    subject_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    dept_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.dept_id"))
    credits: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    department: Mapped["Department"] = relationship("Department", back_populates="subjects")
    syllabuses: Mapped[list["Syllabus"]] = relationship("Syllabus", back_populates="subject")
    academic_classes: Mapped[list["AcademicClass"]] = relationship("AcademicClass", back_populates="subject")
    
class Syllabus(Base):
    __tablename__ = "syllabuses"
    
    syllabus_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey("subjects.subject_id"))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    min_score_to_pass: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    effective_date: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # ✅ ĐỔI từ Date -> String
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    subject: Mapped["Subject"] = relationship("Subject", back_populates="syllabuses")
    evaluation_criteria: Mapped[list["EvaluationCriterion"]] = relationship("EvaluationCriterion", back_populates="syllabus")


class AcademicClass(Base):
    __tablename__ = "academic_classes"
    class_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    class_code: Mapped[str] = mapped_column(String, unique=True)
    semester_id: Mapped[int] = mapped_column(Integer, ForeignKey("semesters.semester_id"))
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey("subjects.subject_id"))
    lecturer_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.user_id"))

    semester: Mapped["Semester"] = relationship("Semester", back_populates="academic_classes")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="academic_classes")
    lecturer: Mapped["User"] = relationship("User", back_populates="taught_classes")
    
    # FIX: Added Cascade delete for Enrollments
    enrollments: Mapped[list["ClassEnrollment"]] = relationship("ClassEnrollment", back_populates="academic_class", cascade="all, delete-orphan")
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="academic_class")
    teams: Mapped[list["Team"]] = relationship("Team", back_populates="academic_class")
    milestones: Mapped[list["Milestone"]] = relationship("Milestone", back_populates="academic_class")
    resources: Mapped[list["Resource"]] = relationship("Resource", back_populates="academic_class")


class ClassEnrollment(Base):
    __tablename__ = "class_enrollments"
    
    enrollment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("academic_classes.class_id", ondelete="CASCADE"))
    student_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.user_id"))
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # "active", "dropped", etc.
    
    academic_class: Mapped["AcademicClass"] = relationship("AcademicClass", back_populates="enrollments")
    student: Mapped["User"] = relationship("User", back_populates="enrollments")

# ==========================================
# CLUSTER 3: PROJECT & TEAM FORMATION
# ==========================================


class Topic(Base):
    __tablename__ = "topics"
    topic_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    objectives: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tech_stack: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    creator_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.user_id"))
    dept_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.dept_id"))
    status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    creator: Mapped["User"] = relationship("User", back_populates="created_topics")
    department: Mapped["Department"] = relationship("Department", back_populates="topics")
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="topic")


class Project(Base):
    __tablename__ = "projects"
    project_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.topic_id"))
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("academic_classes.class_id"))
    project_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    topic: Mapped["Topic"] = relationship("Topic", back_populates="projects")
    academic_class: Mapped["AcademicClass"] = relationship("AcademicClass", back_populates="projects")
    teams: Mapped[list["Team"]] = relationship("Team", back_populates="project")


class Team(Base):
    __tablename__ = "teams"
    team_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("projects.project_id"), nullable=True)
    leader_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.user_id"))
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("academic_classes.class_id"))
    team_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    join_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="teams")
    leader: Mapped["User"] = relationship("User", back_populates="led_teams")
    academic_class: Mapped["AcademicClass"] = relationship("AcademicClass", back_populates="teams")

    # FIX: Added Cascade delete for team artifacts
    members: Mapped[list["TeamMember"]] = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    sprints: Mapped[list["Sprint"]] = relationship("Sprint", back_populates="team", cascade="all, delete-orphan")
    meetings: Mapped[list["Meeting"]] = relationship("Meeting", back_populates="team", cascade="all, delete-orphan")
    channels: Mapped[list["Channel"]] = relationship("Channel", back_populates="team", cascade="all, delete-orphan")
    checkpoints: Mapped[list["Checkpoint"]] = relationship("Checkpoint", back_populates="team", cascade="all, delete-orphan")
    peer_reviews: Mapped[list["PeerReview"]] = relationship("PeerReview", back_populates="team", cascade="all, delete-orphan")
    mentoring_logs: Mapped[list["MentoringLog"]] = relationship("MentoringLog", back_populates="team")
    resources: Mapped[list["Resource"]] = relationship("Resource", back_populates="team")


class TeamMember(Base):
    __tablename__ = "team_members"
    # FIX: Added ondelete=CASCADE
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.team_id", ondelete="CASCADE"), primary_key=True)
    student_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    team: Mapped["Team"] = relationship("Team", back_populates="members")
    student: Mapped["User"] = relationship("User", back_populates="team_memberships")


# ==========================================
# CLUSTER 4: AGILE & COLLABORATION
# ==========================================


class Sprint(Base):
    __tablename__ = "sprints"
    sprint_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.team_id", ondelete="CASCADE"))
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    team: Mapped["Team"] = relationship("Team", back_populates="sprints")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="sprint", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"
    task_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sprint_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sprints.sprint_id", ondelete="CASCADE"), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assignee_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    priority: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    sprint: Mapped[Optional["Sprint"]] = relationship("Sprint", back_populates="tasks")
    assignee: Mapped[Optional["User"]] = relationship("User", back_populates="assigned_tasks")


class Meeting(Base):
    __tablename__ = "meetings"
    meeting_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.team_id", ondelete="CASCADE"))
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    link_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    organizer_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.user_id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    team: Mapped["Team"] = relationship("Team", back_populates="meetings")
    organizer: Mapped["User"] = relationship("User", back_populates="organized_meetings")


class Channel(Base):
    __tablename__ = "channels"
    channel_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.team_id", ondelete="CASCADE"))
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    team: Mapped["Team"] = relationship("Team", back_populates="channels")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="channel", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    message_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(Integer, ForeignKey("channels.channel_id", ondelete="CASCADE"))
    sender_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.user_id"))
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    channel: Mapped["Channel"] = relationship("Channel", back_populates="messages")
    sender: Mapped["User"] = relationship("User", back_populates="sent_messages")


# ==========================================
# CLUSTER 5: MILESTONES & SUBMISSIONS
# ==========================================


class Milestone(Base):
    __tablename__ = "milestones"
    milestone_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("academic_classes.class_id"))
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.user_id"))

    academic_class: Mapped["AcademicClass"] = relationship("AcademicClass", back_populates="milestones")
    creator: Mapped["User"] = relationship("User", back_populates="created_milestones")
    checkpoints: Mapped[list["Checkpoint"]] = relationship("Checkpoint", back_populates="milestone", cascade="all, delete-orphan")


class Checkpoint(Base):
    __tablename__ = "checkpoints"
    checkpoint_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.team_id", ondelete="CASCADE"))
    milestone_id: Mapped[int] = mapped_column(Integer, ForeignKey("milestones.milestone_id", ondelete="CASCADE"))
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    team: Mapped["Team"] = relationship("Team", back_populates="checkpoints")
    milestone: Mapped["Milestone"] = relationship("Milestone", back_populates="checkpoints")
    submissions: Mapped[list["Submission"]] = relationship("Submission", back_populates="checkpoint", cascade="all, delete-orphan")


class Submission(Base):
    __tablename__ = "submissions"
    submission_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    checkpoint_id: Mapped[int] = mapped_column(Integer, ForeignKey("checkpoints.checkpoint_id", ondelete="CASCADE"))
    submitted_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.user_id"))
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    checkpoint: Mapped["Checkpoint"] = relationship("Checkpoint", back_populates="submissions")
    submitter: Mapped["User"] = relationship("User", back_populates="submissions")
    evaluations: Mapped[list["Evaluation"]] = relationship("Evaluation", back_populates="submission", cascade="all, delete-orphan")


# ==========================================
# CLUSTER 6: EVALUATION & RESOURCES
# ==========================================


class EvaluationCriterion(Base):
    __tablename__ = "evaluation_criteria"
    criteria_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    syllabus_id: Mapped[int] = mapped_column(Integer, ForeignKey("syllabuses.syllabus_id"))
    criteria_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    syllabus: Mapped["Syllabus"] = relationship("Syllabus", back_populates="evaluation_criteria")
    evaluation_details: Mapped[list["EvaluationDetail"]] = relationship("EvaluationDetail", back_populates="criterion")


class Evaluation(Base):
    __tablename__ = "evaluations"
    evaluation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(Integer, ForeignKey("submissions.submission_id", ondelete="CASCADE"))
    evaluator_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.user_id"))
    total_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    submission: Mapped["Submission"] = relationship("Submission", back_populates="evaluations")
    evaluator: Mapped["User"] = relationship("User", back_populates="evaluations")
    evaluation_details: Mapped[list["EvaluationDetail"]] = relationship("EvaluationDetail", back_populates="evaluation", cascade="all, delete-orphan")


class EvaluationDetail(Base):
    __tablename__ = "evaluation_details"
    detail_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    evaluation_id: Mapped[int] = mapped_column(Integer, ForeignKey("evaluations.evaluation_id", ondelete="CASCADE"))
    criteria_id: Mapped[int] = mapped_column(Integer, ForeignKey("evaluation_criteria.criteria_id"))
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    evaluation: Mapped["Evaluation"] = relationship("Evaluation", back_populates="evaluation_details")
    criterion: Mapped["EvaluationCriterion"] = relationship("EvaluationCriterion", back_populates="evaluation_details")


class PeerReview(Base):
    __tablename__ = "peer_reviews"
    review_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reviewer_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.user_id"))
    reviewee_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.user_id"))
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.team_id", ondelete="CASCADE"))
    criteria_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    reviewer: Mapped["User"] = relationship("User", back_populates="peer_reviews_given", foreign_keys=[reviewer_id])
    reviewee: Mapped["User"] = relationship("User", back_populates="peer_reviews_received", foreign_keys=[reviewee_id])
    team: Mapped["Team"] = relationship("Team", back_populates="peer_reviews")


class MentoringLog(Base):
    __tablename__ = "mentoring_logs"
    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.team_id", ondelete="CASCADE"))
    lecturer_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.user_id"))
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meeting_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ai_suggestions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    team: Mapped["Team"] = relationship("Team", back_populates="mentoring_logs")
    lecturer: Mapped["User"] = relationship("User", back_populates="mentoring_logs")


class Resource(Base):
    __tablename__ = "resources"
    resource_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uploaded_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.user_id"))
    class_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("academic_classes.class_id"), nullable=True)
    team_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("teams.team_id", ondelete="CASCADE"), nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    file_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    uploader: Mapped["User"] = relationship("User", back_populates="uploaded_resources")
    academic_class: Mapped[Optional["AcademicClass"]] = relationship("AcademicClass", back_populates="resources")
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="resources")

    # ==========================================
# CLUSTER 7: NOTIFICATIONS
# ==========================================

class Notification(Base):
    __tablename__ = "notifications"
    
    notification_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    )
    
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    related_entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    related_entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    action_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    user: Mapped["User"] = relationship("User", back_populates="notifications")