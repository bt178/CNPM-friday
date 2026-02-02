# 📋 TASK_ASSIGNMENT_PHASE3 - Chi tiết kỹ thuật

## 🔌 Socket.IO Architecture (BE1)

### Cấu trúc Socket Events

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
├─────────────────────────────────────────────────────────┤
│  socket.emit('message:send', { channel_id, content })   │
│  socket.on('message:new', (data) => {...})              │
│  socket.emit('typing:start', { channel_id })            │
│  socket.on('typing:indicator', (data) => {...})         │
└────────────────────────┬────────────────────────────────┘
                         │ WebSocket
┌────────────────────────▼────────────────────────────────┐
│              BACKEND (FastAPI + Socket.IO)               │
├─────────────────────────────────────────────────────────┤
│  @sio.on('message:send')                                │
│  async def handle_message(sid, data):                   │
│      # Save to DB                                       │
│      # Broadcast to channel members                     │
│      await sio.emit('message:new', msg, room=channel)   │
└────────────────────────┬────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │  Redis  │  ← Pub/Sub for multi-instance
                    └─────────┘
```

### Socket.IO Setup (main.py)

```python
import socketio
from app.core.config import settings

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=settings.CORS_ORIGINS
)

# Wrap FastAPI app
socket_app = socketio.ASGIApp(sio, app)

# Event handlers
@sio.event
async def connect(sid, environ, auth):
    """Authenticate socket connection"""
    token = auth.get('token')
    user = verify_token(token)
    if not user:
        raise ConnectionRefusedError('authentication failed')
    # Store user in session
    await sio.save_session(sid, {'user_id': user.id})
    
@sio.event
async def disconnect(sid):
    """Handle disconnect"""
    session = await sio.get_session(sid)
    print(f"User {session['user_id']} disconnected")

@sio.on('message:send')
async def handle_message(sid, data):
    """Handle new message"""
    session = await sio.get_session(sid)
    # Save message to DB
    message = await save_message(
        sender_id=session['user_id'],
        channel_id=data['channel_id'],
        content=data['content']
    )
    # Broadcast to channel
    await sio.emit('message:new', message.dict(), room=f"channel:{data['channel_id']}")

@sio.on('join:channel')
async def join_channel(sid, data):
    """Join a channel room"""
    sio.enter_room(sid, f"channel:{data['channel_id']}")

@sio.on('typing:start')
async def typing_start(sid, data):
    """Broadcast typing indicator"""
    session = await sio.get_session(sid)
    await sio.emit('typing:indicator', {
        'user_id': session['user_id'],
        'channel_id': data['channel_id']
    }, room=f"channel:{data['channel_id']}", skip_sid=sid)
```

---

## 💬 Channels & Messages API (BE2)

### Schema: channel.py

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ChannelCreate(BaseModel):
    team_id: int
    name: str
    description: Optional[str] = None
    is_private: bool = False

class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ChannelResponse(BaseModel):
    id: int
    team_id: int
    name: str
    description: Optional[str]
    is_private: bool
    created_at: datetime
    member_count: int
    last_message_at: Optional[datetime]
    
    class Config:
        from_attributes = True
```

### Schema: message.py

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class MessageCreate(BaseModel):
    channel_id: int
    content: str
    reply_to_id: Optional[int] = None  # For threading

class MessageUpdate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    channel_id: int
    sender_id: UUID
    sender_name: str
    sender_avatar: Optional[str]
    content: str
    created_at: datetime
    updated_at: Optional[datetime]
    is_edited: bool = False
    reply_to_id: Optional[int]
    
    class Config:
        from_attributes = True

class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int
    has_more: bool
```

### Endpoints: channels.py

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.deps import get_db, get_current_user
from app.models.all_models import Channel, TeamMember, User
from app.schemas.channel import ChannelCreate, ChannelUpdate, ChannelResponse

router = APIRouter()

@router.post("/", response_model=ChannelResponse, status_code=201)
async def create_channel(
    channel_data: ChannelCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new channel in a team"""
    # Verify user is team member
    member = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == channel_data.team_id,
            TeamMember.user_id == current_user.id
        )
    )
    if not member.scalar():
        raise HTTPException(403, "Must be team member to create channel")
    
    channel = Channel(**channel_data.dict())
    db.add(channel)
    await db.commit()
    await db.refresh(channel)
    return channel

@router.get("/", response_model=List[ChannelResponse])
async def list_channels(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all channels in a team"""
    # Verify user is team member
    # ... (same check as above)
    
    result = await db.execute(
        select(Channel).where(Channel.team_id == team_id)
    )
    return result.scalars().all()

@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get channel details"""
    channel = await db.get(Channel, channel_id)
    if not channel:
        raise HTTPException(404, "Channel not found")
    return channel

@router.delete("/{channel_id}", status_code=204)
async def delete_channel(
    channel_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a channel (team lead only)"""
    channel = await db.get(Channel, channel_id)
    if not channel:
        raise HTTPException(404, "Channel not found")
    
    await db.delete(channel)
    await db.commit()
```

### Endpoints: messages.py

```python
@router.post("/", response_model=MessageResponse, status_code=201)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message to a channel"""
    message = Message(
        channel_id=message_data.channel_id,
        sender_id=current_user.id,
        content=message_data.content,
        reply_to_id=message_data.reply_to_id
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    
    # Emit socket event
    # await sio.emit('message:new', message.dict(), room=f"channel:{message.channel_id}")
    
    return message

@router.get("/", response_model=MessageListResponse)
async def list_messages(
    channel_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List messages in a channel (paginated)"""
    # Get messages ordered by created_at DESC
    result = await db.execute(
        select(Message)
        .where(Message.channel_id == channel_id)
        .order_by(Message.created_at.desc())
        .offset(skip)
        .limit(limit + 1)  # +1 to check if has_more
    )
    messages = result.scalars().all()
    
    has_more = len(messages) > limit
    if has_more:
        messages = messages[:limit]
    
    # Reverse for chronological order in response
    messages.reverse()
    
    # Get total count
    count_result = await db.execute(
        select(func.count()).where(Message.channel_id == channel_id)
    )
    total = count_result.scalar()
    
    return MessageListResponse(
        messages=messages,
        total=total,
        has_more=has_more
    )

@router.patch("/{message_id}", response_model=MessageResponse)
async def edit_message(
    message_id: int,
    update_data: MessageUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Edit a message (sender only)"""
    message = await db.get(Message, message_id)
    if not message:
        raise HTTPException(404, "Message not found")
    if message.sender_id != current_user.id:
        raise HTTPException(403, "Can only edit your own messages")
    
    message.content = update_data.content
    message.is_edited = True
    message.updated_at = datetime.utcnow()
    
    await db.commit()
    return message

@router.delete("/{message_id}", status_code=204)
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a message (sender or team lead)"""
    message = await db.get(Message, message_id)
    if not message:
        raise HTTPException(404, "Message not found")
    
    await db.delete(message)
    await db.commit()
```

---

## 📅 Meetings API (BE3)

### Schema: meeting.py

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum

class MeetingStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MeetingCreate(BaseModel):
    team_id: int
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None  # "daily", "weekly", etc.

class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[MeetingStatus] = None

class MeetingResponse(BaseModel):
    id: int
    team_id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    status: MeetingStatus
    meeting_link: str  # PeerJS room ID
    created_by: UUID
    created_by_name: str
    attendees_count: int
    
    class Config:
        from_attributes = True

class MeetingJoinResponse(BaseModel):
    meeting_id: int
    room_id: str  # PeerJS room ID
    participants: List[dict]  # [{user_id, name, peer_id}]
```

---

## 🖥️ Frontend Services (FE1, FE2)

### chatService.js

```javascript
import apiClient from './apiClient';

export const channelService = {
  // Channels
  createChannel: (teamId, data) => 
    apiClient.post('/channels', { team_id: teamId, ...data }),
  
  listChannels: (teamId) => 
    apiClient.get(`/channels?team_id=${teamId}`),
  
  getChannel: (channelId) => 
    apiClient.get(`/channels/${channelId}`),
  
  deleteChannel: (channelId) => 
    apiClient.delete(`/channels/${channelId}`),
};

export const messageService = {
  // Messages
  sendMessage: (channelId, content, replyToId = null) => 
    apiClient.post('/messages', { channel_id: channelId, content, reply_to_id: replyToId }),
  
  listMessages: (channelId, skip = 0, limit = 50) => 
    apiClient.get(`/messages?channel_id=${channelId}&skip=${skip}&limit=${limit}`),
  
  editMessage: (messageId, content) => 
    apiClient.patch(`/messages/${messageId}`, { content }),
  
  deleteMessage: (messageId) => 
    apiClient.delete(`/messages/${messageId}`),
};
```

### socketService.js

```javascript
import io from 'socket.io-client';

const SOCKET_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class SocketService {
  constructor() {
    this.socket = null;
    this.listeners = new Map();
  }

  connect(token) {
    if (this.socket?.connected) return;
    
    this.socket = io(SOCKET_URL, {
      auth: { token },
      transports: ['websocket'],
    });

    this.socket.on('connect', () => {
      console.log('Socket connected:', this.socket.id);
    });

    this.socket.on('disconnect', (reason) => {
      console.log('Socket disconnected:', reason);
    });

    this.socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  // Channel operations
  joinChannel(channelId) {
    this.socket?.emit('join:channel', { channel_id: channelId });
  }

  leaveChannel(channelId) {
    this.socket?.emit('leave:channel', { channel_id: channelId });
  }

  // Message operations
  sendMessage(channelId, content) {
    this.socket?.emit('message:send', { channel_id: channelId, content });
  }

  onNewMessage(callback) {
    this.socket?.on('message:new', callback);
  }

  // Typing indicators
  startTyping(channelId) {
    this.socket?.emit('typing:start', { channel_id: channelId });
  }

  stopTyping(channelId) {
    this.socket?.emit('typing:stop', { channel_id: channelId });
  }

  onTypingIndicator(callback) {
    this.socket?.on('typing:indicator', callback);
  }

  // Cleanup
  removeAllListeners() {
    this.socket?.removeAllListeners();
  }
}

export default new SocketService();
```

### meetingService.js

```javascript
import apiClient from './apiClient';

export const meetingService = {
  scheduleMeeting: (data) => 
    apiClient.post('/meetings', data),
  
  listMeetings: (teamId) => 
    apiClient.get(`/meetings?team_id=${teamId}`),
  
  getMeeting: (meetingId) => 
    apiClient.get(`/meetings/${meetingId}`),
  
  updateMeeting: (meetingId, data) => 
    apiClient.put(`/meetings/${meetingId}`, data),
  
  cancelMeeting: (meetingId) => 
    apiClient.delete(`/meetings/${meetingId}`),
  
  joinMeeting: (meetingId) => 
    apiClient.post(`/meetings/${meetingId}/join`),
};
```

### peerService.js

```javascript
import Peer from 'peerjs';

class PeerService {
  constructor() {
    this.peer = null;
    this.localStream = null;
    this.connections = new Map(); // peerId -> { call, stream }
  }

  async init(userId) {
    return new Promise((resolve, reject) => {
      this.peer = new Peer(userId, {
        // Use default PeerJS cloud server or configure your own
        // host: 'your-peerjs-server.com',
        // port: 9000,
        // path: '/peerjs',
      });

      this.peer.on('open', (id) => {
        console.log('PeerJS connected with ID:', id);
        resolve(id);
      });

      this.peer.on('error', (err) => {
        console.error('PeerJS error:', err);
        reject(err);
      });
    });
  }

  async getLocalStream() {
    if (this.localStream) return this.localStream;
    
    this.localStream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true,
    });
    return this.localStream;
  }

  async callPeer(remotePeerId) {
    const localStream = await this.getLocalStream();
    const call = this.peer.call(remotePeerId, localStream);
    
    return new Promise((resolve) => {
      call.on('stream', (remoteStream) => {
        this.connections.set(remotePeerId, { call, stream: remoteStream });
        resolve(remoteStream);
      });
    });
  }

  onIncomingCall(callback) {
    this.peer.on('call', async (call) => {
      const localStream = await this.getLocalStream();
      call.answer(localStream);
      
      call.on('stream', (remoteStream) => {
        this.connections.set(call.peer, { call, stream: remoteStream });
        callback(call.peer, remoteStream);
      });
    });
  }

  toggleAudio(enabled) {
    if (this.localStream) {
      this.localStream.getAudioTracks().forEach((track) => {
        track.enabled = enabled;
      });
    }
  }

  toggleVideo(enabled) {
    if (this.localStream) {
      this.localStream.getVideoTracks().forEach((track) => {
        track.enabled = enabled;
      });
    }
  }

  disconnect() {
    // Close all connections
    this.connections.forEach(({ call }) => call.close());
    this.connections.clear();
    
    // Stop local stream
    if (this.localStream) {
      this.localStream.getTracks().forEach((track) => track.stop());
      this.localStream = null;
    }
    
    // Destroy peer
    if (this.peer) {
      this.peer.destroy();
      this.peer = null;
    }
  }
}

export default new PeerService();
```

---

## 📦 Dependencies to Install

### Backend
```bash
pip install python-socketio aioredis
```

### Frontend
```bash
npm install socket.io-client peerjs
```

---

## 🧪 Test Commands

### Test Channels
```bash
# Create channel
curl -X POST http://localhost:8000/api/v1/channels \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"team_id": 1, "name": "general"}'

# List channels
curl http://localhost:8000/api/v1/channels?team_id=1 \
  -H "Authorization: Bearer $TOKEN"
```

### Test Messages
```bash
# Send message
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"channel_id": 1, "content": "Hello team!"}'

# List messages
curl "http://localhost:8000/api/v1/messages?channel_id=1&limit=50" \
  -H "Authorization: Bearer $TOKEN"
```

### Test Socket.IO
```javascript
// In browser console
const socket = io('http://localhost:8000', {
  auth: { token: localStorage.getItem('access_token') }
});

socket.on('connect', () => console.log('Connected!'));
socket.emit('join:channel', { channel_id: 1 });
socket.on('message:new', (msg) => console.log('New message:', msg));
```
