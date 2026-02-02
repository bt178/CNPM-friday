/**
 * Chat Service - Phase 3
 * Copy file này vào: frontend/src/services/chatService.js
 * 
 * Quản lý các API calls cho Channels và Messages
 */

import api from './api';

// ============ CHANNELS ============

/**
 * Tạo channel mới cho team
 * @param {number} teamId - ID của team
 * @param {object} channelData - { name: string, description?: string }
 */
export const createChannel = async (teamId, channelData) => {
  const response = await api.post('/channels/', {
    team_id: teamId,
    ...channelData
  });
  return response.data;
};

/**
 * Lấy danh sách channels của team
 * @param {number} teamId - ID của team
 */
export const getTeamChannels = async (teamId) => {
  const response = await api.get('/channels/', {
    params: { team_id: teamId }
  });
  return response.data;
};

/**
 * Lấy chi tiết channel
 * @param {number} channelId - ID của channel
 */
export const getChannel = async (channelId) => {
  const response = await api.get(`/channels/${channelId}`);
  return response.data;
};

/**
 * Cập nhật channel
 * @param {number} channelId - ID của channel
 * @param {object} updateData - { name?: string, description?: string }
 */
export const updateChannel = async (channelId, updateData) => {
  const response = await api.put(`/channels/${channelId}`, updateData);
  return response.data;
};

/**
 * Xóa channel
 * @param {number} channelId - ID của channel
 */
export const deleteChannel = async (channelId) => {
  await api.delete(`/channels/${channelId}`);
};


// ============ MESSAGES ============

/**
 * Gửi tin nhắn trong channel
 * @param {number} channelId - ID của channel
 * @param {string} content - Nội dung tin nhắn
 */
export const sendMessage = async (channelId, content) => {
  const response = await api.post('/messages/', {
    channel_id: channelId,
    content
  });
  return response.data;
};

/**
 * Lấy tin nhắn trong channel (có phân trang)
 * @param {number} channelId - ID của channel
 * @param {object} options - { page?: number, limit?: number }
 */
export const getChannelMessages = async (channelId, options = {}) => {
  const { page = 1, limit = 50 } = options;
  const response = await api.get('/messages/', {
    params: { 
      channel_id: channelId,
      page,
      limit
    }
  });
  return response.data;
};

/**
 * Lấy chi tiết tin nhắn
 * @param {number} messageId - ID của message
 */
export const getMessage = async (messageId) => {
  const response = await api.get(`/messages/${messageId}`);
  return response.data;
};

/**
 * Cập nhật tin nhắn
 * @param {number} messageId - ID của message
 * @param {string} content - Nội dung mới
 */
export const updateMessage = async (messageId, content) => {
  const response = await api.patch(`/messages/${messageId}`, { content });
  return response.data;
};

/**
 * Xóa tin nhắn
 * @param {number} messageId - ID của message
 */
export const deleteMessage = async (messageId) => {
  await api.delete(`/messages/${messageId}`);
};


// ============ UTILITY FUNCTIONS ============

/**
 * Format thời gian hiển thị tin nhắn
 * @param {string} dateString - ISO date string
 */
export const formatMessageTime = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now - date;
  
  // Trong vòng 1 phút
  if (diff < 60000) {
    return 'Vừa xong';
  }
  
  // Trong vòng 1 giờ
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000);
    return `${minutes} phút trước`;
  }
  
  // Trong vòng 24 giờ
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000);
    return `${hours} giờ trước`;
  }
  
  // Khác - hiển thị ngày
  return date.toLocaleDateString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * Nhóm tin nhắn theo ngày
 * @param {array} messages - Danh sách tin nhắn
 */
export const groupMessagesByDate = (messages) => {
  const groups = {};
  
  messages.forEach(msg => {
    const date = new Date(msg.sent_at).toLocaleDateString('vi-VN');
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(msg);
  });
  
  return groups;
};

export default {
  createChannel,
  getTeamChannels,
  getChannel,
  updateChannel,
  deleteChannel,
  sendMessage,
  getChannelMessages,
  getMessage,
  updateMessage,
  deleteMessage,
  formatMessageTime,
  groupMessagesByDate
};
