// import axios from 'axios';

// const API_BASE_URL = 'http://121.14.82.109:8061/api/v1';

// const api = axios.create({
//   baseURL: API_BASE_URL,
// });

// export const runAgent = async (userInput, currentMode, threadId, files = []) => {
//   const formData = new FormData();
//   formData.append('user_input', userInput);
//   formData.append('current_mode', currentMode);
//   if (threadId) formData.append('thread_id', threadId);

//   files.forEach(file => {
//     formData.append('files', file.raw);
//   });

//   try {
//     const response = await api.post('/agent/run', formData, {
//       headers: { 'Content-Type': 'multipart/form-data' }
//     });
//     return response.data;
//   } catch (error) {
//     console.error('Agent调用失败:', error);
//     throw error;
//   }
// };

// export const runAgentStream = async (
//   userInput,
//   currentMode,
//   threadId,
//   files = [],
//   onEvent,
// ) => {
//   const formData = new FormData();
//   formData.append('user_input', userInput);
//   formData.append('current_mode', currentMode);
//   if (threadId) formData.append('thread_id', threadId);

//   files.forEach(file => {
//     formData.append('files', file.raw ?? file);
//   });

//   const response = await fetch(`${API_BASE_URL}/agent/run/stream`, {
//     method: 'POST',
//     body: formData,
//   });

//   if (!response.ok) {
//     const errorText = await response.text();
//     throw new Error(errorText || 'Agent 流式调用失败');
//   }

//   if (!response.body) {
//     throw new Error('当前浏览器不支持流式响应');
//   }

//   const reader = response.body.getReader();
//   const decoder = new TextDecoder('utf-8');
//   let buffer = '';
//   let finalData = null;
//   let streamError = null;

//   const processBuffer = (textChunk = '') => {
//     buffer += textChunk;
//     const blocks = buffer.split('\n\n');
//     buffer = blocks.pop() || '';

//     for (const block of blocks) {
//       const dataLine = block
//         .split('\n')
//         .find(line => line.startsWith('data: '));

//       if (!dataLine) continue;

//       try {
//         const event = JSON.parse(dataLine.slice(6));
//         if (typeof onEvent === 'function') {
//           onEvent(event);
//         }
//         if (event.type === 'final') {
//           finalData = event.data;
//         }
//         if (event.type === 'error') {
//           streamError = new Error(event.message || 'Agent 执行失败');
//         }
//       } catch (e) {
//         console.error('流式事件解析失败:', e, block);
//       }
//     }
//   };

//   while (true) {
//     const { value, done } = await reader.read();
//     if (done) break;
//     processBuffer(decoder.decode(value, { stream: true }));
//   }

//   processBuffer(decoder.decode());
//   if (buffer.trim()) {
//     processBuffer('\n\n');
//   }

//   if (streamError) {
//     throw streamError;
//   }

//   return finalData;
// };

// export const fetchProjects = async (studentId) => {
//   try {
//     const response = await api.get('/projects/', {
//       params: { student_id: studentId }
//     });
//     return response.data;
//   } catch (error) {
//     console.error('拉取项目列表失败:', error);
//     throw error;
//   }
// };

// export const createProject = async (name, studentId, file, content = '') => {
//   const formData = new FormData();
//   formData.append('name', name);
//   formData.append('student_id', studentId);
//   if (file) formData.append('file', file);
//   if (content) formData.append('content', content);

//   try {
//     const response = await api.post('/projects/', formData, {
//       headers: { 'Content-Type': 'multipart/form-data' }
//     });
//     return response.data;
//   } catch (error) {
//     console.error('创建项目失败:', error);
//     throw error;
//   }
// };

// export const fetchAllProjects = async () => {
//   try {
//     const response = await api.get('/projects/');
//     return response.data;
//   } catch (error) {
//     console.error('教师拉取全班项目失败:', error);
//     throw error;
//   }
// };

// export const syncProjectChat = async (projectId, chatHistoryArray) => {
//   try {
//     const response = await api.put(`/projects/${projectId}/chat`, {
//       chat_history: JSON.stringify(chatHistoryArray)
//     });
//     return response.data;
//   } catch (error) {
//     console.error('同步聊天记录失败:', error);
//     throw error;
//   }
// };

// export const loginUser = async (username, password) => {
//   try {
//     const response = await api.post('/auth/login', { username, password });
//     return response.data;
//   } catch (error) {
//     console.error('登录失败:', error);
//     throw error.response?.data?.detail || '登录失败，请检查账号密码';
//   }
// };

// export const registerUser = async (userData) => {
//   try {
//     const response = await api.post('/auth/register', userData);
//     return response.data;
//   } catch (error) {
//     console.error('注册失败:', error);
//     throw error.response?.data?.detail || '注册失败，请更换账号名重试';
//   }
// };


import axios from 'axios';

const API_BASE_URL = 'http://121.14.82.109:8061/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const runAgent = async (
  userInput,
  currentMode,
  threadId,
  files = [],
  conversationId = ''
) => {
  const formData = new FormData();
  formData.append('user_input', userInput);
  formData.append('current_mode', currentMode);
  if (threadId) formData.append('thread_id', threadId);
  if (conversationId) formData.append('conversation_id', conversationId);

  files.forEach((file) => {
    formData.append('files', file.raw ?? file);
  });

  try {
    const response = await api.post('/agent/run', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    console.error('Agent调用失败:', error);
    throw error;
  }
};

export const runAgentStream = async (
  userInput,
  currentMode,
  threadId,
  files = [],
  onEvent,
  conversationId = ''
) => {
  const formData = new FormData();
  formData.append('user_input', userInput);
  formData.append('current_mode', currentMode);
  if (threadId) formData.append('thread_id', threadId);
  if (conversationId) formData.append('conversation_id', conversationId);

  files.forEach((file) => {
    formData.append('files', file.raw ?? file);
  });

  const response = await fetch(`${API_BASE_URL}/agent/run/stream`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || 'Agent 流式调用失败');
  }

  if (!response.body) {
    throw new Error('当前浏览器不支持流式响应');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';
  let finalData = null;
  let streamError = null;

  const processBuffer = async (textChunk = '') => {
    buffer += textChunk;
    const blocks = buffer.split('\n\n');
    buffer = blocks.pop() || '';

    for (const block of blocks) {
      const dataLine = block
        .split('\n')
        .find((line) => line.startsWith('data: '));

      if (!dataLine) continue;

      try {
        const event = JSON.parse(dataLine.slice(6));
        if (typeof onEvent === 'function') {
          await onEvent(event);
        }
        if (event.type === 'final') {
          finalData = event.data;
        }
        if (event.type === 'error') {
          streamError = new Error(event.message || 'Agent 执行失败');
        }
      } catch (e) {
        console.error('流式事件解析失败:', e, block);
      }
    }
  };

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    await processBuffer(decoder.decode(value, { stream: true }));
  }

  await processBuffer(decoder.decode());
  if (buffer.trim()) {
    await processBuffer('\n\n');
  }

  if (streamError) {
    throw streamError;
  }

  return finalData;
};

/* =========================
   Conversation APIs
========================= */

export const fetchConversations = async (studentId) => {
  try {
    const response = await api.get('/conversations/', {
      params: { student_id: studentId },
    });
    return response.data;
  } catch (error) {
    console.error('拉取会话列表失败:', error);
    throw error;
  }
};

export const createConversation = async (studentId, title = '新对话') => {
  try {
    const response = await api.post('/conversations/', {
      student_id: studentId,
      title,
    });
    return response.data;
  } catch (error) {
    console.error('创建会话失败:', error);
    throw error;
  }
};

export const fetchConversationDetail = async (conversationId) => {
  try {
    const response = await api.get(`/conversations/${conversationId}`);
    return response.data;
  } catch (error) {
    console.error('拉取会话详情失败:', error);
    throw error;
  }
};

export const bindConversationFile = async (conversationId, file) => {
  const formData = new FormData();
  formData.append('file', file.raw ?? file);

  try {
    const response = await api.put(`/conversations/${conversationId}/bind-file`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    console.error('绑定会话文档失败:', error);
    throw error;
  }
};

export const syncConversationState = async (
  conversationId,
  chatHistoryArray,
  analysisSnapshot = null,
  title = null,
  lastMode = null
) => {
  const payload = {
    chat_history: JSON.stringify(chatHistoryArray),
  };

  if (analysisSnapshot !== null) {
    payload.analysis_snapshot =
      typeof analysisSnapshot === 'string'
        ? analysisSnapshot
        : JSON.stringify(analysisSnapshot);
  }

  if (title !== null) payload.title = title;
  if (lastMode !== null) payload.last_mode = lastMode;

  try {
    const response = await api.put(`/conversations/${conversationId}/state`, payload);
    return response.data;
  } catch (error) {
    console.error('同步会话状态失败:', error);
    throw error;
  }
};

/* =========================
   Legacy Project APIs
========================= */

export const fetchProjects = async (studentId) => {
  try {
    const response = await api.get('/projects/', {
      params: { student_id: studentId },
    });
    return response.data;
  } catch (error) {
    console.error('拉取项目列表失败:', error);
    throw error;
  }
};

export const createProject = async (name, studentId, file, content = '') => {
  const formData = new FormData();
  formData.append('name', name);
  formData.append('student_id', studentId);
  if (file) formData.append('file', file);
  if (content) formData.append('content', content);

  try {
    const response = await api.post('/projects/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    console.error('创建项目失败:', error);
    throw error;
  }
};

export const fetchAllProjects = async () => {
  try {
    const response = await api.get('/projects/');
    return response.data;
  } catch (error) {
    console.error('教师拉取全班项目失败:', error);
    throw error;
  }
};

export const syncProjectChat = async (projectId, chatHistoryArray) => {
  try {
    const response = await api.put(`/projects/${projectId}/chat`, {
      chat_history: JSON.stringify(chatHistoryArray),
    });
    return response.data;
  } catch (error) {
    console.error('同步聊天记录失败:', error);
    throw error;
  }
};

export const loginUser = async (username, password) => {
  try {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  } catch (error) {
    console.error('登录失败:', error);
    throw error.response?.data?.detail || '登录失败，请检查账号密码';
  }
};

export const registerUser = async (userData) => {
  try {
    const response = await api.post('/auth/register', userData);
    return response.data;
  } catch (error) {
    console.error('注册失败:', error);
    throw error.response?.data?.detail || '注册失败，请更换账号名重试';
  }
};

/* =========================
   Admin Portal APIs
========================= */
export const fetchAdminUsers = async () => {
  const response = await api.get('/admin/users');
  return response.data;
};

export const batchRegisterUsers = async (usersData) => {
  const response = await api.post('/admin/users/batch', { users: usersData });
  return response.data;
};

export const deleteUser = async (userId) => {
  const response = await api.delete(`/admin/users/${userId}`);
  return response.data;
};

export const resetUserPassword = async (userId, newPassword) => {
  const response = await api.put(`/admin/users/${userId}/password`, { new_password: newPassword });
  return response.data;
};

export const updateUserRole = async (userId, role) => {
  const response = await api.put(`/admin/users/${userId}/role`, { role });
  return response.data;
};

export const fetchAdminStats = async () => {
  const response = await api.get('/admin/stats');
  return response.data;
};