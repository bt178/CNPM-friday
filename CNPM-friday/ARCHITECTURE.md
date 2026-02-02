# CollabSphere Architecture Documentation

**Project**: Project-Based Learning Management System with AI-Powered Team Collaboration  
**Last Updated**: January 2026  
**Status**: In Development

---

## 1. Project Overview

CollabSphere is a comprehensive web application designed to manage project-based learning in academic environments. It integrates:
- **Team collaboration** with agile methodologies
- **AI-powered mentoring** using Google Gemini API
- **Real-time communication** via Socket.IO
- **Video conferencing** via PeerJS

The system supports multiple user roles (Admin, Staff, Head_Dept, Lecturer, Student) with role-based access control for managing semesters, classes, projects, teams, sprints, and evaluations.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER (React)                   │
│  - Pages (UI components)                                    │
│  - Services (API calls via Axios)                           │
│  - Hooks (Business logic)                                   │
│  - Real-time: Socket.IO Client + PeerJS                    │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/WebSocket
┌────────────────────▼────────────────────────────────────────┐
│              API GATEWAY LAYER (FastAPI)                    │
│  - Versioned REST API (/api/v1)                             │
│  - CORS Middleware                                          │
│  - JWT Authentication                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──┐  ┌──────▼──┐  ┌─────▼─────┐
│ Services │  │ Schemas │  │   Deps    │
│  (Logic) │  │(Validate)│  │(Injection)│
└───────┬──┘  └──────┬──┘  └─────┬─────┘
        │            │            │
        └────────────┼────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼─────┐ ┌───▼────┐ ┌────▼──────┐
│   Models    │ │ Config │ │ Security  │
│(SQLAlchemy) │ │  Core  │ │   (JWT)   │
└───────┬─────┘ └───┬────┘ └────┬──────┘
        │           │           │
        └───────────┼───────────┘
                    │
        ┌───────────┼──────────┐
        │           │          │
┌───────▼──┐  ┌────▼───┐  ┌──▼──────┐
│ Database │  │ Redis  │  │ Gemini  │
│(PostgreSQL)  │(Cache) │  │ API     │
└──────────┘  └────────┘  └─────────┘
```

---

## 3. Technology Stack

### Backend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | FastAPI | 0.104.1 | Async web framework |
| ORM | SQLAlchemy | 2.0.23 | Database ORM |
| DB Driver | asyncpg | 0.27.0 | Async PostgreSQL driver |
| Auth | python-jose + passlib | 3.3.0 | JWT tokens & password hashing |
| Validation | Pydantic | 2.5.0 | Data validation & serialization |
| Real-time | python-socketio | 5.10.0 | WebSocket communication |
| Cache | Redis | 5.0.1 | Session & pub/sub |
| AI | google-generativeai | 0.3.2 | Gemini API integration |
| Migrations | Alembic | 1.12.1 | Database version control |
| Server | Uvicorn | 0.24.0 | ASGI server |

### Frontend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | React | 18.2.0 | UI components |
| Build Tool | Vite | 5.0.8 | Fast build & dev server |
| UI Library | Ant Design | 5.12.0 | Pre-built components |
| HTTP Client | Axios | 1.6.2 | REST API calls |
| Routing | React Router | 6.20.1 | Client-side routing |
| Real-time | Socket.IO Client | 4.6.1 | WebSocket client |
| Video | PeerJS | 1.5.2 | P2P video calls |

### Infrastructure
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Database | PostgreSQL 15 | Primary data store |
| Cache | Redis 7 | Session management & Pub/Sub |
| Containerization | Docker | Isolated environments |
| Orchestration | Docker Compose | Multi-container management |

---

## 4. Backend Architecture

### 4.1 Directory Structure

```
backend/
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
└── app/
    ├── __init__.py
    ├── main.py             # FastAPI app initialization & CORS
    │
    ├── core/               # System configuration
    │   ├── config.py       # Pydantic settings (env variables)
    │   └── security.py     # JWT utilities (to implement)
    │
    ├── db/                 # Database configuration
    │   ├── base.py         # SQLAlchemy DeclarativeBase
    │   └── session.py      # Async SQLAlchemy engine & session (to implement)
    │
    ├── models/             # SQLAlchemy ORM models
    │   ├── all_models.py   # All database models (COMPLETE)
    │   ├── user.py         # User model exports
    │   └── project.py      # Project model exports
    │
    ├── schemas/            # Pydantic validation models
    │   ├── token.py        # Token request/response
    │   └── user.py         # User request/response
    │
    ├── services/           # Business logic layer
    │   ├── ai_service.py   # Google Gemini integration
    │   └── chat_manager.py # Socket.IO chat management
    │
    ├── api/                # API endpoints
    │   ├── deps.py         # Dependency injection (auth, DB)
    │   └── v1/
    │       ├── api.py      # Main router
    │       ├── auth.py     # Authentication endpoints
    │       ├── users.py    # User management endpoints
    │       └── projects.py # Project management endpoints
    │
    └── tests/              # Unit & integration tests
        └── __init__.py
```

### 4.2 Data Model Clusters

The database is organized into **6 interconnected clusters**:

#### **1. System Identity** (Users, Access Control)
```
Role
├─ User (role_id) ──┬─> Department (dept_id)
                     └─> Role (role_id) ──> Enum: Admin, Staff, Head_Dept, Lecturer, Student
SystemSetting
AuditLog
```

#### **2. Academic Management** (Semesters, Subjects, Classes)
```
Semester ──> Subject ──> Syllabus
           └─> AcademicClass (subject_id, semester_id)
               └─> ClassEnrollment (class_id, user_id)
```

#### **3. Project Formation** (Topics & Teams)
```
Topic ──> Project (topic_id)
          └─> Team (project_id)
              └─> TeamMember (team_id, user_id)
```

#### **4. Agile Collaboration** (Sprints, Tasks, Communication)
```
Team ──> Sprint (team_id)
    │    └─> Task (sprint_id, assigned_to)
    │
    └─> Channel (team_id)
        └─> Message (channel_id, sender_id)
    
    └─> Meeting (team_id)
```

#### **5. Milestones & Submissions** (Project Progress Tracking)
```
Project ──> Milestone (project_id)
            └─> Checkpoint (milestone_id)
                └─> Submission (checkpoint_id, team_id)
```

#### **6. Evaluation & Resources** (Assessment & Learning)
```
Project ──> EvaluationCriteria (project_id)
           └─> Evaluation (project_id, evaluated_by, team_id)
               └─> EvaluationDetail (evaluation_id, criteria_id)

Team ──> PeerReview (team_id, reviewer_id, reviewed_user_id)
     └─> MentoringLog (team_id, mentor_id)
     │   ├─> ai_suggestions (Gemini API generated)
     │
     └─> Resource (team_id)
```

### 4.3 Key ORM Features (SQLAlchemy 2.0)

**Cascade Deletes**: Deleting parent records cascades to children
```python
# Example: Deleting a Team removes all:
# - TeamMembers, Sprints, Tasks, Channels, Messages, Meetings
```

**Foreign Key Naming Convention**: `{table}_{column}`
```python
team_id: Mapped[int] = mapped_column(ForeignKey("team.id", ondelete="CASCADE"))
```

**UUID vs Integer Keys**:
- **UUID**: User IDs (globally unique)
- **Integer autoincrement**: All other entities (relationships)

**Timezone-Aware Datetimes**:
```python
created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
```

### 4.4 Service-Layered Architecture (Pragmatic)

**Design Principle**: Simplicity over complexity

```
HTTP Request
    ↓
┌─────────────────────────────┐
│  Endpoint (api/v1/*.py)     │  
│  - Route handler            │  
│  - Parse request            │  
│  - Check auth               │  
│  - Call service             │  
│  - Return response          │  
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│  Service (services/*.py)    │
│  - Business logic           │
│  - Query database directly  │ ← No repository layer!
│  - External API calls       │
│  - Complex calculations     │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│  Database (AsyncSession)    │
│  - SQLAlchemy ORM queries   │
└─────────────────────────────┘
```

**Why No Repository Layer?**
- Smaller team → faster development
- SQLAlchemy abstracts data access
- Services can directly execute queries
- Focus on velocity, not architecture perfection

### 4.5 Authentication Flow

```
Client                              Backend
  │                                  │
  ├─ POST /api/v1/auth/login ───────>│
  │  (username, password)            │
  │                                  ├─ Hash password check
  │                                  ├─ Generate JWT token
  │                                  ├─ Set Redis session
  │<──── 200 OK + Token ──────────────┤
  │  {                               │
  │   "access_token": "...",         │
  │   "token_type": "bearer",        │
  │   "user": {...}                  │
  │  }                               │
  │                                  │
  │  Subsequent Requests             │
  ├─ GET /api/v1/users/me ─────────>│
  │  Header: Authorization: Bearer   │
  │<────────── User Data ────────────┤
```

**Token Details**:
- **Type**: JWT (JSON Web Token)
- **Algorithm**: HS256
- **Expiration**: 30 minutes (configurable)
- **Refresh**: Not yet implemented
- **Storage (Frontend)**: localStorage

### 4.6 API Structure

#### Versioning
```
/api/v1/
├── /auth               # Authentication
├── /users              # User management
├── /projects           # Project management
├── /teams              # Team operations
├── /sprints            # Sprint management
└── ... (more to implement)
```

#### Endpoint Pattern
```python
# Example: Get current user
@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_user)
):
    return current_user
```

#### Dependency Injection (deps.py)
```python
async def get_db() -> AsyncSession:
    """Provide database session"""

async def get_current_user(token: str) -> User:
    """Verify JWT & return authenticated user"""

async def get_current_admin(user: User) -> User:
    """Ensure user has admin role"""
```

### 4.7 Configuration Management

**Environment Variables** (loaded from `.env`):
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# AI
GOOGLE_GEMINI_API_KEY=your-api-key
```

**Settings Class** (config.py):
- Loads from `.env` using Pydantic BaseSettings
- Provides property methods for parsing complex values
- Single `settings` instance used throughout

---

## 5. Frontend Architecture

### 5.1 Directory Structure

```
frontend/
├── Dockerfile          # Container definition
├── package.json        # Dependencies & scripts
├── vite.config.js      # Vite configuration
├── index.html          # HTML entry point
│
└── src/
    ├── main.jsx        # React app entry point
    ├── App.jsx         # Root component
    │
    ├── pages/          # Full-page components (routed)
    │   ├── LoginPage.jsx
    │   ├── DashboardPage.jsx
    │   ├── ProjectsPage.jsx
    │   └── ... (more to implement)
    │
    ├── components/     # Reusable UI components
    │   ├── Navbar.jsx
    │   ├── Sidebar.jsx
    │   ├── ProjectCard.jsx
    │   └── ... (more to implement)
    │
    ├── hooks/          # Custom React hooks
    │   ├── useAuth.js
    │   ├── useApi.js
    │   └── ... (more to implement)
    │
    └── services/       # API communication & external services
        ├── api.js      # Axios instance & interceptors
        ├── authService.js
        └── ... (more to implement)
```

### 5.2 Component Hierarchy

```
App
├── Router
│   ├── LoginPage (public)
│   ├── DashboardPage (protected)
│   │   ├── Navbar
│   │   ├── Sidebar
│   │   └── MainContent
│   │       ├── ProjectsList
│   │       │   └── ProjectCard (x N)
│   │       ├── TeamsList
│   │       ├── SprintsList
│   │       └── TasksList
│   │
│   └── ... (more pages)
│
└── AuthContext (global state)
```

### 5.3 API Integration

#### Axios Configuration (services/api.js)
```javascript
// Base configuration
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
});

// Interceptors for JWT token
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 (token expired)
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

#### Example Service Call
```javascript
// authService.js
export const loginUser = async (username, password) => {
  const response = await axiosInstance.post('/api/v1/auth/login', {
    username,
    password,
  });
  localStorage.setItem('access_token', response.data.access_token);
  return response.data;
};
```

### 5.4 Real-Time Features

#### Socket.IO Client
```javascript
import io from 'socket.io-client';

const socket = io(import.meta.env.VITE_API_URL, {
  auth: {
    token: localStorage.getItem('access_token'),
  },
});

// Listen to real-time events
socket.on('message:new', (data) => {
  console.log('New message:', data);
});

// Emit events
socket.emit('message:send', { channel_id: 1, text: 'Hello' });
```

#### PeerJS for Video Calls
```javascript
import Peer from 'peerjs';

const peer = new Peer();
const call = peer.call(remotePeerId, localStream);

call.on('stream', (remoteStream) => {
  remoteVideo.srcObject = remoteStream;
});
```

### 5.5 State Management

**Current Approach**: Context API + localStorage
```javascript
// AuthContext.js
export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('access_token'));

  const login = async (username, password) => {
    const data = await loginUser(username, password);
    setUser(data.user);
    setToken(data.access_token);
  };

  return (
    <AuthContext.Provider value={{ user, token, login }}>
      {children}
    </AuthContext.Provider>
  );
};
```

**Future Enhancement**: Redux Toolkit or Zustand for more complex state

---

## 6. Database Schema Overview

### Core Tables (Simplified)

```sql
-- System
Role (id, name)                    -- Admin, Staff, Head_Dept, Lecturer, Student
User (id, username, email, password_hash, role_id)
Department (id, name)
SystemSetting (id, key, value)

-- Academic
Semester (id, name, start_date, end_date)
Subject (id, name, code)
Syllabus (id, subject_id, content)
AcademicClass (id, subject_id, lecturer_id, semester_id)
ClassEnrollment (id, class_id, user_id)

-- Projects
Topic (id, name, description)
Project (id, topic_id, class_id)
Team (id, project_id, name, join_code)
TeamMember (id, team_id, user_id, role)

-- Agile
Sprint (id, team_id, name, start_date, end_date)
Task (id, sprint_id, assigned_to, title, status)
Meeting (id, team_id, title, start_time)
Channel (id, team_id, name)
Message (id, channel_id, sender_id, content)

-- Evaluation
Milestone (id, project_id, name, deadline)
Checkpoint (id, milestone_id, description)
Submission (id, checkpoint_id, team_id, content)
EvaluationCriteria (id, project_id, name, max_score)
Evaluation (id, project_id, evaluated_by, team_id)
EvaluationDetail (id, evaluation_id, criteria_id, score)
PeerReview (id, team_id, reviewer_id, reviewed_user_id, comment)
MentoringLog (id, team_id, mentor_id, meeting_notes, ai_suggestions)
Resource (id, team_id, title, url)
```

### Relationships at a Glance

```
User  ◄─── ClassEnrollment ───► AcademicClass ◄─── Subject
│            TeamMember      │                    
│        EvaluationCriteria  │  Semester
└─────────────────────┬──────┘
                      │
                  Project ◄─── Topic
                    │  │
          Milestone  │  └─────► Team ◄─── Channel
            │        │            │         └─► Message
          Checkpoint │            ├─ Sprint
            │        │            │   └─ Task
          Submission │            │
                     │            ├─ Meeting
                     └─ Evaluation◄─┤
                        │            └─ MentoringLog
                        └─ PeerReview └─ Resource
```

---

## 7. API Endpoints (Implemented & Planned)

### Authentication (Partially Implemented)
```
POST   /api/v1/auth/login          # User login
POST   /api/v1/auth/register       # User registration (planned)
POST   /api/v1/auth/refresh        # Refresh JWT token (planned)
POST   /api/v1/auth/logout         # Logout (planned)
```

### Users (Planned)
```
GET    /api/v1/users/me            # Current user profile
GET    /api/v1/users/{user_id}     # User details
PUT    /api/v1/users/{user_id}     # Update profile
GET    /api/v1/users               # List all users (admin only)
```

### Projects (Planned)
```
GET    /api/v1/projects            # List projects
POST   /api/v1/projects            # Create project
GET    /api/v1/projects/{id}       # Project details
PUT    /api/v1/projects/{id}       # Update project
DELETE /api/v1/projects/{id}       # Delete project
```

### Teams (Planned)
```
GET    /api/v1/teams               # List teams
POST   /api/v1/teams               # Create team
GET    /api/v1/teams/{id}          # Team details
POST   /api/v1/teams/{id}/join     # Join team by code
PUT    /api/v1/teams/{id}          # Update team
DELETE /api/v1/teams/{id}          # Delete team
```

### Sprints & Tasks (Planned)
```
GET    /api/v1/sprints             # List sprints
POST   /api/v1/sprints             # Create sprint
GET    /api/v1/tasks               # List tasks
POST   /api/v1/tasks               # Create task
PATCH  /api/v1/tasks/{id}          # Update task status
```

### Channels & Messages (Planned)
```
GET    /api/v1/channels            # List channels
POST   /api/v1/channels            # Create channel
GET    /api/v1/messages            # List messages (paginated)
POST   /api/v1/messages            # Send message
```

### Evaluations (Planned)
```
POST   /api/v1/evaluations         # Create evaluation
GET    /api/v1/evaluations/{id}    # Get evaluation
PUT    /api/v1/evaluations/{id}    # Update evaluation
GET    /api/v1/peer-reviews        # List peer reviews
POST   /api/v1/peer-reviews        # Submit peer review
```

### Mentoring (Planned)
```
GET    /api/v1/mentoring-logs      # List mentoring logs
POST   /api/v1/mentoring-logs      # Create mentoring log
GET    /api/v1/mentoring-logs/{id} # Get mentoring log
```

---

## 8. Security Architecture

### Authentication & Authorization

```
┌──────────────────┐
│  User Login      │
│  (username/pwd)  │
└────────┬─────────┘
         │
    ┌────▼─────────────┐
    │  Verify Password │ (passlib)
    │  (bcrypt hash)   │
    └────┬─────────────┘
         │
    ┌────▼──────────────────┐
    │  Generate JWT Token   │ (python-jose)
    │  (HS256, 30 min exp)  │
    └────┬──────────────────┘
         │
    ┌────▼───────────────┐
    │  Store in Redis    │ (Session mgmt)
    │  localStorage      │
    └────┬───────────────┘
         │
    ┌────▼────────────────────┐
    │ Return Token to Client  │
    └─────────────────────────┘
```

### Protected Endpoints

```python
# Example: Admin-only endpoint
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check admin role
    if current_user.role.name != "Admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Delete user
    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()
```

### CORS Configuration

```python
# Allowed origins (from config.CORS_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 9. Real-Time Communication

### WebSocket Architecture (Socket.IO)

```
Frontend                Backend
   │                      │
   ├─ connect ───────────>│ (establish WS connection)
   │                      │
   ├─ emit('message:send')│ (send message)
   │         ────────────>│
   │                      ├─ Save to DB
   │                      ├─ Broadcast to team
   │<──── broadcast ──────┤
   │                      │
   └─ disconnect ────────>│
```

### Event Structure (Planned)

```javascript
// Message events
socket.on('message:new', (data) => {
  // { channel_id, sender_id, content, timestamp }
});

// Task updates
socket.on('task:updated', (data) => {
  // { task_id, status, assigned_to }
});

// Sprint notifications
socket.on('sprint:notification', (data) => {
  // { message, type: 'warning' | 'info' }
});
```

---

## 10. AI Integration

### Google Gemini API

**Use Cases**:
1. **Mentoring Suggestions** - Analyze team performance and provide feedback
2. **Task Recommendations** - Suggest tasks based on project progress
3. **Code Review Comments** - Automated code review insights
4. **Progress Analysis** - Evaluate team productivity trends

**Implementation** (ai_service.py):
```python
class AIService:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
    
    async def generate_mentoring_suggestions(
        self, 
        team_progress: dict, 
        evaluations: list
    ) -> str:
        """Generate AI-powered mentoring suggestions"""
        # Context-aware prompt construction
        # API call with error handling
        # Return suggestions as string
        pass
```

**Rate Limiting & Error Handling**:
- Retry logic with exponential backoff
- API quota monitoring
- Fallback responses if API unavailable

---

## 11. Docker & Deployment

### Docker Compose Services

```yaml
services:
  db (PostgreSQL)           # Port 5432
  redis (Redis)             # Port 6379
  backend (FastAPI)         # Port 8000
  frontend (React/Vite)     # Port 3000
```

### Service Dependencies

```
Frontend
  ├─ depends_on: Backend
  └─ healthcheck: None
  
Backend
  ├─ depends_on: DB, Redis
  └─ healthcheck: None
  
DB
  └─ healthcheck: pg_isready
  
Redis
  └─ healthcheck: redis-cli ping
```

### Volume Mounts

| Service | Mount | Purpose |
|---------|-------|---------|
| Backend | ./backend:/app | Code hot-reload |
| Frontend | ./frontend:/app | Code hot-reload |
| DB | postgres_data:/var/lib/postgresql/data | Data persistence |
| Redis | redis_data:/data | Cache persistence |

### Health Checks

```yaml
db:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U collabsphere"]
    interval: 10s
    timeout: 5s
    retries: 5

redis:
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 10s
    timeout: 5s
    retries: 5
```

### Startup Sequence

```
1. docker-compose up
   ├─ Start PostgreSQL (waits for health check)
   ├─ Start Redis (waits for health check)
   ├─ Start Backend (depends_on healthy db & redis)
   │  └─ Run migrations (Alembic - planned)
   │  └─ Start Uvicorn server
   └─ Start Frontend (depends_on backend)
      └─ Start Vite dev server
```

---

## 12. Development Workflow

### Local Development

```bash
# Clone repository
git clone <repo-url>
cd CNPM-friday

# Start all services
docker-compose up

# Services available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Database: localhost:5432
# - Redis: localhost:6379
```

### Testing Endpoints

**PowerShell Script** (test-endpoints.ps1):
- Tests auth endpoints (login, register)
- Tests CRUD operations
- Validates response schemas
- Measures performance

```powershell
# Run tests
.\test-endpoints.ps1
```

### Hot Reload

- **Backend**: Uvicorn with `--reload` flag
- **Frontend**: Vite with HMR (Hot Module Replacement)
- **Database**: Changes apply immediately
- **Redis**: Cache flushes on restart

### Environment Variables

**.env file**:
```bash
DATABASE_URL=postgresql+asyncpg://collabsphere:password@localhost:5432/collabsphere_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key-change-in-production
GOOGLE_GEMINI_API_KEY=your-api-key
```

---

## 13. Implementation Status

### Backend

| Component | Status | Notes |
|-----------|--------|-------|
| FastAPI Setup | ✅ Complete | Main app, CORS configured |
| Database Models | ✅ Complete | All 30+ models defined |
| Config Management | ✅ Complete | Pydantic settings |
| Auth Endpoints | 🟡 In Progress | Login partially implemented |
| Services Layer | 🔴 Todo | Business logic to implement |
| API Endpoints | 🔴 Todo | ~40 endpoints planned |
| Socket.IO | 🔴 Todo | Real-time features |
| Alembic Migrations | 🔴 Todo | Database versioning |

### Frontend

| Component | Status | Notes |
|-----------|--------|-------|
| Vite + React | ✅ Complete | Project structure ready |
| Ant Design | ✅ Complete | UI library installed |
| Routing | 🟡 In Progress | React Router setup needed |
| Auth Pages | 🔴 Todo | Login, register pages |
| API Client | 🟡 In Progress | Axios configured |
| Components | 🔴 Todo | Reusable components |
| Pages | 🔴 Todo | Dashboard, projects, teams |
| Socket.IO Client | 🔴 Todo | Real-time integration |

### Infrastructure

| Component | Status | Notes |
|-----------|--------|-------|
| Docker Compose | ✅ Complete | All services defined |
| PostgreSQL | ✅ Complete | Configured & running |
| Redis | ✅ Complete | Cache ready |
| Health Checks | ✅ Complete | Service dependencies checked |
| Volume Mounts | ✅ Complete | Hot reload enabled |

---

## 14. Key Architectural Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|-----------|
| **No Repository Layer** | Speed of development | Less abstraction, harder to change DB later |
| **SQLAlchemy 2.0 with async/await** | Modern, performant, type-safe | Steeper learning curve |
| **Service Layer in endpoints** | Clear separation of concerns | Not strictly layered |
| **Pydantic for validation** | Built-in FastAPI support | Duplicate models (request/response) |
| **Pragma auth (JWT + Redis)** | Simple, works at scale | Manual token refresh needed |
| **Context API (React)** | No external dependencies | Will need Redux for complex state |
| **Ant Design** | Rich components, well-maintained | Bundle size larger |
| **Socket.IO over WebSocket** | Fallback support, easier API | More overhead |
| **Cascade deletes** | Clean data consistency | Risk of accidental data loss |

---

## 15. Performance Considerations

### Backend Optimization

- **Async SQLAlchemy**: Non-blocking database operations
- **Redis Caching**: Session storage, message queues
- **Connection Pooling**: PostgreSQL connection reuse
- **Query Optimization**: Eager loading, pagination (planned)
- **Rate Limiting**: API request throttling (planned)

### Frontend Optimization

- **Code Splitting**: Vite automatically chunks routes
- **Lazy Loading**: Dynamic imports for pages
- **Asset Caching**: Static files cached in browser
- **Image Optimization**: WebP format (planned)
- **Bundle Analysis**: Monitor with Vite plugins (planned)

### Database Optimization

- **Indexes**: Foreign keys auto-indexed
- **Normalization**: Proper schema design
- **Materialized Views**: For complex queries (planned)
- **Query Monitoring**: Slow query logs (planned)

---

## 16. Scalability Path

### Short Term (Current Phase)
- Single container per service
- Local PostgreSQL & Redis
- Development-focused

### Medium Term (6-12 months)
- Multiple backend instances
- Load balancer (Nginx)
- Redis cluster for cache
- Database replication

### Long Term (12+ months)
- Kubernetes orchestration
- Horizontal scaling
- Global CDN for static assets
- Microservices decomposition

---

## 17. Gotchas & Important Notes

⚠️ **Critical Points**:

1. **Cascade Deletes**: Deleting a Team removes ALL related data permanently
   ```python
   # Deleting team cascades to:
   # - TeamMembers, Sprints, Tasks, Channels, Messages, Meetings, etc.
   ```

2. **UUID vs Integer Keys**: Don't mix them
   ```python
   # Users: UUID (user_id)
   # Everything else: Integer autoincrement
   ```

3. **Timezone Handling**: Always use UTC with timezone info
   ```python
   created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
   ```

4. **CORS Origin Mismatch**: Common cause of "No Access-Control-Allow-Origin"
   ```python
   # Frontend localhost:3000 ≠ localhost:5173 (different port)
   # Configure both in CORS_ORIGINS
   ```

5. **JWT Token Expiration**: 30 minutes - refresh logic not yet implemented
   ```python
   # Users will be logged out after 30 mins
   # TODO: Implement refresh token endpoint
   ```

6. **Environment Variables**: Override .env defaults
   ```bash
   # .env file is loaded first
   # Then docker-compose.yml overrides for containers
   ```

7. **Database Migrations**: Not yet set up with Alembic
   ```python
   # Manual schema changes currently required
   # TODO: Implement Alembic migrations
   ```

---

## 18. File Organization Philosophy

### Backend (app/ folder)

```
Organize by FEATURE, not by LAYER:

❌ BAD:
api/
├── endpoints/
│   ├── auth.py
│   ├── users.py
│   └── projects.py
models/
└── all_models.py

✅ GOOD (current):
api/v1/
├── auth.py        (includes endpoint + schema)
├── users.py       (includes endpoint + schema)
└── projects.py    (includes endpoint + schema)
```

Rationale: Related code stays together, easier to navigate

### Frontend (src/ folder)

```
Organize by PAGE, not by TYPE:

❌ BAD:
components/
├── Dashboard.jsx
├── Profile.jsx
pages/
├── DashboardPage.jsx
└── ProfilePage.jsx
services/
└── dashboardService.js

✅ GOOD (planned):
pages/
├── Dashboard/
│   ├── Dashboard.jsx
│   ├── components/ (Dashboard-specific)
│   └── hooks/      (Dashboard-specific)
└── Profile/
    ├── Profile.jsx
    ├── components/
    └── hooks/
```

---

## 19. Next Steps & Roadmap

### Phase 1: Core Authentication (In Progress)
- [ ] Complete auth endpoints (login, register, logout)
- [ ] Implement refresh token logic
- [ ] Set up password reset flow
- [ ] Create login/register UI pages

### Phase 2: User & Project Management
- [ ] CRUD endpoints for users, projects, teams
- [ ] Team join code functionality
- [ ] Project dashboard UI
- [ ] User profile pages

### Phase 3: Agile Collaboration
- [ ] Sprint & task management endpoints
- [ ] Real-time Socket.IO integration
- [ ] Chat/messaging functionality
- [ ] Notification system

### Phase 4: Evaluation & Assessment
- [ ] Evaluation endpoints
- [ ] Submission management
- [ ] Peer review system
- [ ] Grading UI

### Phase 5: AI & Mentoring
- [ ] Google Gemini integration
- [ ] Mentoring log endpoints
- [ ] AI suggestion generation
- [ ] Code review automation

### Phase 6: Polish & Deployment
- [ ] Database migrations (Alembic)
- [ ] API documentation
- [ ] Error handling & logging
- [ ] Performance optimization
- [ ] Production deployment

---

## 20. Useful Commands

```bash
# Docker
docker-compose up              # Start all services
docker-compose down            # Stop all services
docker-compose logs backend    # View backend logs
docker-compose restart backend # Restart backend

# Database
psql -h localhost -U collabsphere -d collabsphere_db
supa  cloud database

# Redis
redis-cli -h localhost PING

# Backend API
curl http://localhost:8000/health

# Frontend
npm install
npm run dev
npm run build

# Testing
.\test-endpoints.ps1           # PowerShell test script
```

---

**Document Version**: 1.0  
**Last Updated**: January 2026  
**Maintained By**: Development Team
