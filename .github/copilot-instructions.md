# CollabSphere AI Coding Instructions

## Project Overview
CollabSphere is a comprehensive **Project-Based Learning Management System** built with FastAPI (backend) and React/Vite (frontend). It manages academic projects with team collaboration, agile methodologies, and AI-powered mentoring.

## Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with SQLAlchemy 2.0
- **Database**: PostgreSQL with complex relational models
- **Cache**: Redis for session management
- **Auth**: JWT tokens with role-based access (Admin, Staff, Head_Dept, Lecturer, Student)
- **AI**: Google Gemini integration for mentoring suggestions
- **Real-time**: Socket.IO for chat and notifications

### Frontend (React)
- **Framework**: React 18 with Vite
- **UI**: Ant Design components
- **Routing**: React Router
- **Real-time**: Socket.IO client + PeerJS for video calls
- **API**: Axios for REST communication

### Data Model Clusters
1. **System Identity**: Users, Roles, Departments, System Settings, Audit Logs
2. **Academic Management**: Semesters, Subjects, Classes, Enrollments
3. **Project Formation**: Topics, Projects, Teams, Team Members
4. **Agile Collaboration**: Sprints, Tasks, Meetings, Channels, Messages
5. **Milestones & Submissions**: Milestones, Checkpoints, Submissions
6. **Evaluation & Resources**: Criteria, Evaluations, Peer Reviews, Mentoring, Resources

## Key Patterns & Conventions

### Database Relationships
- Use **cascade deletes** for dependent entities (e.g., `ondelete="CASCADE"`)
- **Foreign key naming**: `{table}_{column}` (e.g., `user_id`, `team_id`)
- **UUID primary keys** for users, **integer autoincrement** for entities
- **Timezone-aware datetimes**: `DateTime(timezone=True)`

### API Structure
- **Versioned endpoints**: `/api/v1/`
- **Dependency injection**: Use `deps.py` for auth dependencies
- **Pydantic schemas**: Separate input/output models in `schemas/`
- **Service layer**: Business logic in `services/` - services can directly query database using SQLAlchemy

### Pragmatic Service-Layered Architecture
- **Endpoints**: Handle HTTP requests/responses, auth checks, call service functions
- **Services**: Contain business logic (e.g., "assign student to team", "calculate grade") - can execute DB queries directly
- **Models**: SQLAlchemy tables (complete)
- **Schemas**: Pydantic models (complete)
- **No Repository Layer**: Services query database directly for simplicity and development speed
- **Velocity First**: Prioritize getting features working over architectural purity

### Authentication Flow
- **JWT tokens** with 30-minute expiration
- **Role-based access** via `role_id` foreign key
- **CORS configured** for frontend origins (localhost:3000, localhost:5173)

### Development Workflow
- **Docker Compose** for local development (`docker-compose up`)
- **Hot reload** enabled for both backend (uvicorn) and frontend (vite)
- **Health checks** for database and Redis dependencies
- **PowerShell testing** via `test-endpoints.ps1`

### Docker Setup & Troubleshooting
- **Start Docker**: Run `docker desktop start` on Windows before using docker-compose
- **Restart services**: Use `docker-compose restart <service_name>` (e.g., `docker-compose restart backend`)
- **View logs**: Use `docker-compose logs <service_name>` to debug issues
- **Clean restart**: Run `docker-compose down && docker-compose up --build` for fresh start
- **Database persistence**: PostgreSQL and Redis data persist in named volumes

### File Organization
```
backend/app/
├── main.py              # FastAPI app instance + CORS
├── core/config.py       # Pydantic settings from .env (uses API_V1_STR=/api/v1)
├── core/security.py     # JWT utilities ✅ Working
├── db/base.py           # SQLAlchemy DeclarativeBase
├── db/session.py        # Database session management ✅ Working
├── models/all_models.py # Complete SQLAlchemy 2.0 models
├── schemas/             # Pydantic request/response models
└── api/v1/              # API v1 endpoints
    ├── api.py           # Main API router with admin endpoints
    ├── auth.py          # Authentication endpoints
    ├── users.py         # User endpoints
    └── deps.py          # Dependency injection & auth
```

**✅ Architecture (Jan 28, 2026):**
- Using `/api/v1/` versioning (kept as per team's existing code)
- All endpoints under `api/v1/` folder
- Admin endpoints (init-db, db-status) in `api.py`
- Frontend connects to `VITE_API_URL=http://localhost:8000/api/v1`

## Critical Implementation Notes

### Database Setup
- Models are fully defined in `all_models.py` - **do not modify existing relationships**
- Implement `session.py` with async SQLAlchemy engine ✅ **Done**
- Use Alembic for migrations (not yet configured)
- **Environment variables** in `.env` override defaults in `config.py`
- **Supabase Support**: Can migrate to Supabase PostgreSQL using `supabase_migration.py` script
  - Connection format: `postgresql://postgres.[PROJECT-ID]:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres`
  - Use asyncpg driver: `postgresql+asyncpg://...`
  - See [SUPABASE_MIGRATION.md](../SUPABASE_MIGRATION.md) for full instructions

### Authentication Implementation Status ✅
**COMPLETED COMPONENTS:**
1. ✅ **Backend Auth Endpoints**
   - `POST /api/v1/auth/login` - OAuth2 compatible token endpoint
   - `POST /api/v1/auth/register` - User registration with role support
   - `GET /api/v1/users/me` - Get current authenticated user

2. ✅ **Backend Security**
   - JWT token generation & verification in `app/core/security.py`
   - Password hashing with PBKDF2 (MAX_BCRYPT_BYTES = 72 bytes limit)
   - OAuth2PasswordBearer token validation in `app/api/deps.py`
   - Database session management with async SQLAlchemy

3. ✅ **Frontend Auth Integration**
   - `AuthContext.jsx` - Complete auth state management with session persistence
   - `LoginPage.jsx` - Form with email/password inputs
   - `RegisterPage.jsx` - Registration form with role selection
   - Role-based dashboard routing (admin vs student)
   - Idle session timeout with 5-minute auto-logout

4. ✅ **Environment Configuration**
   - Frontend `.env` with `VITE_API_URL=http://localhost:8000/api/v1`
   - Backend `.env` with Supabase PostgreSQL connection
   - Docker-compose overrides DB with local PostgreSQL for local dev

### API Development
- Start with **auth endpoints** (login, register, token refresh)
- Use **dependency injection** for current user (`deps.py`)
- **Role checking** in endpoints (e.g., lecturers only for class management)
- **Pagination** for list endpoints (teams, tasks, messages)

### Login/Registration Flow (Working)
1. User enters email + password on LoginPage
2. FE sends POST to `/api/v1/auth/login` with OAuth2 URLencoded form
3. BE validates credentials, returns JWT access_token
4. FE stores token in localStorage and calls `/api/v1/users/me`
5. FE stores user profile and navigates to appropriate dashboard
6. All subsequent requests include `Authorization: Bearer {token}` header

### Register Flow (Working)
1. User fills email, password, role, full_name on RegisterPage
2. FE sends POST to `/api/v1/auth/register` with JSON body
3. BE validates email uniqueness, hashes password, creates user
4. FE navigates to LoginPage for user to sign in

### Frontend Integration
- **API base URL** from `VITE_API_URL` environment variable
- **Auth tokens** in localStorage with axios interceptors
- **Real-time updates** via Socket.IO for chat and notifications
- **Role-based UI** rendering (different views for students vs lecturers)

### Recent Fixes (January 28, 2026)
**✅ HOÀN THÀNH - V1 Architecture + Registration/Login Working:**
1. ✅ **Reverted to V1 Architecture**
   - Using `/api/v1/` versioning (as per team's existing code structure)
   - `API_V1_STR = "/api/v1"` in config.py
   - All auth code in `app/api/v1/` folder
   - Frontend `.env` uses `VITE_API_URL=http://localhost:8000/api/v1`

2. ✅ **Admin Endpoints in V1**
   - `POST /api/v1/admin/init-db` creates tables and seeds 5 roles
   - `GET /api/v1/admin/db-status` checks database health
   - Integrated into `app/api/v1/api.py` main router

3. ✅ **Registration & Login Working**
   - `POST /api/v1/auth/register` - Create user with role_id
   - `POST /api/v1/auth/login` - OAuth2 token endpoint
   - `GET /api/v1/users/me` - Get authenticated user profile

**Cách sử dụng:**
- **Init Database**: `POST http://localhost:8000/api/v1/admin/init-db`
- **Register**: `POST http://localhost:8000/api/v1/auth/register` với role_id 1-5
- **Login**: `POST http://localhost:8000/api/v1/auth/login` (form data)
- **Frontend**: Tự động kết nối đến `http://localhost:8000/api/v1`

### AI Features
- **Google Gemini API** for mentoring suggestions in `MentoringLog.ai_suggestions`
- **Context-aware prompts** using team progress, evaluations, and peer reviews
- **Rate limiting** and error handling for API calls

### Testing & Deployment
- **PowerShell scripts** for endpoint testing
- **Container health checks** ensure service dependencies
- **Volume mounts** for hot reload during development
- **Production secrets** via environment variables (no hardcoded keys)
- **Test Auth Flow**: 
  ```bash
  # 1. Start services
  docker-compose up
  
  # 2. Register new user (POST http://localhost:8000/api/v1/auth/register)
  {
    "email": "student@example.com",
    "password": "password123",
    "role_id": 5,
    "full_name": "Test Student"
  }
  
  # 3. Login (POST http://localhost:8000/api/v1/auth/login)
  # Send as form data: username=student@example.com&password=password123&grant_type=password
  # Returns: {"access_token": "...", "token_type": "bearer"}
  
  # 4. Get user profile (GET http://localhost:8000/api/v1/users/me)
  # Add header: Authorization: Bearer <access_token>
  ```

## Common Tasks
- **User registration**: Create user with role, department, generate UUID
- **Team formation**: Students join via `join_code`, auto-assign to projects
- **Sprint management**: Create tasks under sprints, assign to team members
- **Evaluation workflow**: Lecturers evaluate submissions against criteria
- **Peer reviews**: Team members review each other anonymously
- **Mentoring sessions**: Log meetings with AI-generated suggestions

## Gotchas
- **Cascade deletes** are critical - deleting a team removes all related data
- **Foreign key constraints** prevent orphaned records
- **Timezone handling** - all datetimes should be UTC with timezone info
- **UUID vs Integer keys** - users use UUIDs, most entities use integers
- **Role permissions** - implement checks in API endpoints, not just UI</content>
<parameter name="filePath">d:\Python_Project\WEB TEAMWORK\web app\CollabSphere\CNPM-friday\.github\copilot-instructions.md