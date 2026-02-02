# 🎯 GIAO_VIEC_3 - Phase 3 (Real-time Features & Chat)

**Ngày bắt đầu:** Feb 8, 2026  
**Deadline:** Feb 14, 2026  
**Mục tiêu:** Chat real-time, Channels, Messages, Meetings, Notifications live

---

## � TIẾN ĐỘ PHASE 3

| Thành viên | Task | Status |
|------------|------|--------|
| **BE1** | Socket.IO Infrastructure | ✅ **HOÀN THÀNH** |
| BE2 | Channels & Messages | 🔄 Chưa bắt đầu |
| BE3 | Meetings Module | 🔄 Chưa bắt đầu |
| BE4 | Semesters + Cleanup | 🔄 Chưa bắt đầu |
| FE1 | Chat UI | 🔄 Chưa bắt đầu |
| FE2 | Meetings + Video UI | 🔄 Chưa bắt đầu |
| FE3 | Notifications UI | 🔄 Chưa bắt đầu |

### ✅ BE1 Đã hoàn thành (các thành viên khác có thể sử dụng):

**Files đã tạo:**
- `backend/app/services/socket_manager.py` - Socket.IO server với ConnectionManager
- `backend/app/services/notification_service.py` - NotificationService class

**Cách sử dụng Socket.IO cho BE2, BE3:**
```python
from app.services.socket_manager import manager

# Broadcast message tới channel
await manager.broadcast_message(channel_id, message_data)

# Broadcast task update tới team
await manager.broadcast_task_update(team_id, task_data)

# Gửi notification cho user
await manager.send_notification(user_id, notification_data)
```

**Cách sử dụng NotificationService cho BE2, BE3, BE4:**
```python
from app.services.notification_service import NotificationService

# Tạo và gửi notification
await NotificationService.create_and_send(db, user_id, "Tiêu đề", "Nội dung", "task")

# Thông báo cho cả team
await NotificationService.send_to_team(db, team_id, "title", "content", "meeting")
```

---

## �📊 Tình trạng API hiện tại

### ✅ Đã hoàn thành (Phase 1 + 2):
| Module | Endpoints | Status |
|--------|-----------|--------|
| Auth | login, register | ✅ Done |
| Users | /me, profile | ✅ Done |
| Topics | CRUD, approve, reject, evaluations | ✅ Done (7 endpoints) |
| Teams | CRUD, join, leave, finalize, select-project | ✅ Done (7 endpoints) |
| Tasks | CRUD, sprints, status, assign | ✅ Done (10 endpoints) |
| Projects | CRUD, claim | ✅ Done (4 endpoints) |
| Academic Classes | CRUD | ✅ Done (5 endpoints) |
| Enrollments | CRUD, bulk | ✅ Done (6 endpoints) |
| Subjects | CRUD | ✅ Done (5 endpoints) |
| Syllabuses | CRUD | ✅ Done (5 endpoints) |
| Departments | CRUD | ✅ Done (5 endpoints) |
| Semesters | create | ⚠️ Partial (1 endpoint) |
| Notifications | CRUD | ✅ Done (6 endpoints) |

**Tổng: ~60 endpoints đã có**

### 🔴 Cần làm Phase 3:
| Module | Endpoints cần | Priority |
|--------|--------------|----------|
| Channels | CRUD (4) | HIGH |
| Messages | CRUD + Real-time (5) | HIGH |
| Meetings | CRUD (4) | MEDIUM |
| Socket.IO Events | 5+ events | HIGH |
| Semesters | GET, PUT, DELETE (3) | LOW |

---

## 👥 Phân công Phase 3

### 🔴 BE1 (Backend Lead - Real-time Architecture) ✅ HOÀN THÀNH
**Mục tiêu:** Set up Socket.IO infrastructure

**Công việc:**
- [x] Configure Socket.IO server in FastAPI
- [x] Create `app/services/socket_manager.py`
- [x] Set up Redis pub/sub for multi-instance support
- [x] Define socket events:
  - `message:new` - New message received
  - `message:typing` - User is typing
  - `task:updated` - Task status changed
  - `notification:new` - New notification
  - `team:member_joined` - Team member update
- [x] Create authentication middleware for sockets
- [x] Test with frontend Socket.IO client

**Success criteria:**
- ✅ Socket connection established from frontend
- ✅ Messages broadcast to correct channels
- ✅ Events reach correct users only

**Files đã tạo:**
```
backend/app/services/
├── socket_manager.py      # ✅ Socket.IO event handlers (~300 lines)
├── chat_manager.py        # (existing) 
└── notification_service.py # ✅ Real-time notifications (~200 lines)
```

**Ghi chú BE1 (Hoàn thành ngày: Feb 2026):**
- Socket.IO được mount tại `/socket.io` path trong main.py
- Thêm `verify_token()` vào `app/core/security.py` để xác thực socket
- Sử dụng `python-socketio==5.11.0` với async mode
- ConnectionManager class quản lý user connections và rooms
- Tất cả events đều có JWT authentication

**Tài liệu tham khảo:**
- PHASE3_PLAN.md (real-time section)
- python-socketio documentation

---

### 🟡 BE2 (Channels & Messages Module)
**Mục tiêu:** Implement chat channels and messages

**Công việc:**
- [ ] Create schemas: `app/schemas/channel.py`, `app/schemas/message.py`
- [ ] Create endpoints: `app/api/v1/channels.py`
- [ ] Create endpoints: `app/api/v1/messages.py`
- [ ] Register routes in `api.py`
- [ ] Implement endpoints:
  - `POST /api/v1/channels` (create channel in team)
  - `GET /api/v1/channels?team_id={id}` (list team channels)
  - `GET /api/v1/channels/{id}` (channel details)
  - `DELETE /api/v1/channels/{id}` (delete channel)
  - `POST /api/v1/messages` (send message)
  - `GET /api/v1/messages?channel_id={id}` (list messages, paginated)
  - `GET /api/v1/messages/{id}` (message details)
  - `DELETE /api/v1/messages/{id}` (delete message)
  - `PATCH /api/v1/messages/{id}` (edit message)
- [ ] Add socket events for real-time messages
- [ ] Test with Postman/curl

**Success criteria:**
- All 9 endpoints working
- Messages paginated (limit 50 per request)
- Only team members can access channels
- Socket events trigger on new messages

**Schema examples:**
```python
# channel.py
class ChannelCreate(BaseModel):
    team_id: int
    name: str
    description: Optional[str] = None

class ChannelResponse(BaseModel):
    id: int
    team_id: int
    name: str
    created_at: datetime

# message.py
class MessageCreate(BaseModel):
    channel_id: int
    content: str

class MessageResponse(BaseModel):
    id: int
    channel_id: int
    sender_id: UUID
    sender_name: str
    content: str
    created_at: datetime
```

---

### 🟠 BE3 (Meetings Module)
**Mục tiêu:** Implement meeting scheduling

**Công việc:**
- [ ] Create schema: `app/schemas/meeting.py`
- [ ] Create endpoints: `app/api/v1/meetings.py`
- [ ] Register routes in `api.py`
- [ ] Implement endpoints:
  - `POST /api/v1/meetings` (schedule meeting)
  - `GET /api/v1/meetings?team_id={id}` (list team meetings)
  - `GET /api/v1/meetings/{id}` (meeting details)
  - `PUT /api/v1/meetings/{id}` (update meeting)
  - `DELETE /api/v1/meetings/{id}` (cancel meeting)
  - `POST /api/v1/meetings/{id}/join` (join meeting - get PeerJS room)
- [ ] Integrate with notification system (remind before meeting)
- [ ] Test meeting creation and listing

**Success criteria:**
- All 6 endpoints working
- Meeting notifications sent 15 min before
- Team members can join via PeerJS room ID

**Schema examples:**
```python
class MeetingCreate(BaseModel):
    team_id: int
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    meeting_link: Optional[str] = None  # PeerJS room ID

class MeetingResponse(BaseModel):
    id: int
    team_id: int
    title: str
    start_time: datetime
    end_time: datetime
    meeting_link: Optional[str]
    created_by: UUID
```

---

### 🟠 BE4 (Semesters + Cleanup)
**Mục tiêu:** Complete semesters module + fix remaining issues

**Công việc:**
- [ ] Complete `app/api/v1/semesters.py`:
  - `GET /api/v1/semesters` (list all)
  - `GET /api/v1/semesters/{id}` (details)
  - `PUT /api/v1/semesters/{id}` (update)
  - `DELETE /api/v1/semesters/{id}` (delete)
- [ ] Add semester status (active, upcoming, completed)
- [ ] Create utility endpoint: `GET /api/v1/semesters/current` (get active semester)
- [ ] Fix any remaining 422/500 errors from Phase 1-2
- [ ] Add comprehensive error messages
- [ ] Update OpenAPI documentation (Swagger descriptions)

**Success criteria:**
- Semesters CRUD complete (5 endpoints)
- Current semester endpoint working
- All API errors have clear messages
- Swagger docs updated

---

### 🟢 FE1 (Frontend - Chat UI)
**Mục tiêu:** Build chat interface with real-time updates

**Công việc:**
- [ ] Create `frontend/src/services/chatService.js`
- [ ] Create `frontend/src/services/socketService.js`
- [ ] Create components:
  - [ ] `ChatSidebar.jsx` (list channels)
  - [ ] `ChatWindow.jsx` (message list)
  - [ ] `MessageInput.jsx` (send message)
  - [ ] `MessageItem.jsx` (single message)
  - [ ] `TypingIndicator.jsx` (user is typing)
- [ ] Create page: `frontend/src/pages/TeamChat.jsx`
- [ ] Integrate Socket.IO client:
  - Connect on page load
  - Listen to `message:new`
  - Emit `message:send`
  - Show typing indicator
- [ ] Add to team navigation menu
- [ ] Style with Ant Design

**Success criteria:**
- Real-time messages appear without refresh
- Typing indicator shows when others type
- Message history loads on scroll (pagination)
- Mobile responsive

**Socket.IO integration:**
```javascript
// socketService.js
import io from 'socket.io-client';

const socket = io(import.meta.env.VITE_API_URL, {
  auth: { token: localStorage.getItem('access_token') }
});

export const subscribeToMessages = (channelId, callback) => {
  socket.on(`channel:${channelId}:message`, callback);
};

export const sendMessage = (channelId, content) => {
  socket.emit('message:send', { channel_id: channelId, content });
};
```

---

### 🔵 FE2 (Frontend - Meetings + Video)
**Mục tiêu:** Build meeting UI with video call support

**Công việc:**
- [ ] Create `frontend/src/services/meetingService.js`
- [ ] Create `frontend/src/services/peerService.js` (PeerJS wrapper)
- [ ] Create components:
  - [ ] `MeetingsList.jsx` (upcoming meetings)
  - [ ] `MeetingCard.jsx` (single meeting)
  - [ ] `ScheduleMeetingModal.jsx` (create meeting)
  - [ ] `VideoCall.jsx` (PeerJS video interface)
  - [ ] `VideoGrid.jsx` (multiple video streams)
- [ ] Create page: `frontend/src/pages/TeamMeetings.jsx`
- [ ] Integrate PeerJS:
  - Initialize Peer on join
  - Handle call/answer events
  - Display local + remote video streams
- [ ] Add calendar view for meetings (Ant Design Calendar)
- [ ] Add to team navigation menu

**Success criteria:**
- Can schedule new meetings
- Calendar shows upcoming meetings
- Video call works between 2+ users
- Audio/video controls working

**PeerJS integration:**
```javascript
// peerService.js
import Peer from 'peerjs';

let peer = null;

export const initPeer = (userId) => {
  peer = new Peer(userId);
  return peer;
};

export const callPeer = (remotePeerId, localStream) => {
  return peer.call(remotePeerId, localStream);
};
```

---

## 🧪 Testing Checklist Phase 3

### Real-time Chat Test
```
1. User A opens TeamChat page
2. User B opens same team's chat
3. User A sends message
4. User B sees message appear instantly (no refresh)
5. User A sees typing indicator when B types
```

### Video Call Test
```
1. User A schedules meeting
2. User B sees meeting in calendar
3. Both users click "Join Meeting"
4. Video/audio streams connect
5. Can mute/unmute, turn camera on/off
```

### Notification Test
```
1. User A sends message in channel
2. User B (not in chat) receives notification
3. Notification shows message preview
4. Click notification goes to chat
```

---

## ⏰ Timeline Phase 3

| Ngày | Milestone | Owner |
|-----|-----------|-------|
| Feb 8-9 | Socket.IO setup + Channels/Messages BE | BE1, BE2 |
| Feb 10-11 | Meetings BE + Semesters + FE Chat UI | BE3, BE4, FE1 |
| Feb 12-13 | FE Meetings + Video integration | FE2 |
| Feb 14 | Full integration test + bug fixes | All |

---

## 🚨 Common Issues Phase 3

**Issue:** Socket connection fails  
→ Check CORS settings include WebSocket origins  
→ Verify token is sent in socket auth

**Issue:** Messages not real-time  
→ Check Redis pub/sub is running  
→ Verify socket event names match

**Issue:** Video call fails to connect  
→ Check STUN/TURN server configuration  
→ Verify PeerJS server is accessible

**Issue:** Meeting notifications not received  
→ Check notification service is triggered  
→ Verify user subscription settings

---

## ✅ Khi xong Phase 3

Sau khi real-time chat + meetings + video working:

1. Run integration tests (Chat, Video, Notifications)
2. Check performance (message latency < 100ms)
3. Document socket events in API docs
4. Mở file `Giao_Viec_4/giao_viec.md`
5. Bắt đầu Phase 4 (AI Features + Advanced Evaluation)

---

**Chúc bạn làm việc vui vẻ! 🚀**  
*Phase 3 là giai đoạn thú vị nhất - real-time features make the app feel alive! 💬📹*
