// import React, { useEffect, useMemo, useRef, useState } from 'react';
// import {
//   Plus, MessageSquare, Send, FileText, BookOpen, Briefcase, Trophy,
//   Bot, User, Sparkles, ChevronDown, ChevronUp, Loader2, Paperclip, AlertCircle, RefreshCcw
// } from 'lucide-react';
// import {
//   bindConversationFile, createConversation, fetchConversations,
//   runAgentStream, syncConversationState
// } from '../../api';

// // 【导入拆分出来的组件】确保这三个文件和 FreeChatView.jsx 在同一个目录下
// import SnapshotOverlay from './SnapshotOverlay';
// import ThinkingProcess from './ThinkingProcess';
// import StructuredResponseRenderer from './StructuredResponseRenderer';

// // --- 工具函数区 ---
// function safeParseJSON(raw, fallback) {
//   if (!raw) return fallback;
//   try {
//     return JSON.parse(raw);
//   } catch {
//     return fallback;
//   }
// }

// function formatDateTime(raw) {
//   if (!raw) return '未知时间';
//   const date = new Date(raw);
//   if (Number.isNaN(date.getTime())) return raw;
//   return date.toLocaleString('zh-CN', {
//     year: 'numeric',
//     month: '2-digit',
//     day: '2-digit',
//     hour: '2-digit',
//     minute: '2-digit',
//   });
// }

// function deriveConversationTitle(text) {
//   const cleaned = (text || '').trim();
//   if (!cleaned) return '新对话';
//   return cleaned.length > 18 ? `${cleaned.slice(0, 18)}...` : cleaned;
// }

// function mapConversationFromApi(item) {
//   return {
//     id: item.id,
//     studentId: item.student_id,
//     title: item.title || '新对话',
//     messages: safeParseJSON(item.chat_history, []),
//     documentStatus: item.document_status || 'none',
//     boundFileName: item.bound_file_name || '',
//     boundFileUploadedAt: item.bound_file_uploaded_at || '',
//     analysisSnapshot: safeParseJSON(item.analysis_snapshot, {}),
//     lastMode: item.last_mode || 'learning',
//     createdAt: item.created_at || '',
//     updatedAt: item.updated_at || '',
//     threadId: item.id,
//   };
// }

// // function sanitizeMessagesForSave(messages = []) {
// //   return messages.map((msg) => ({
// //     id: msg.id,
// //     role: msg.role,
// //     text: msg.text || '',
// //     mode: msg.mode || '',
// //     content: msg.content ?? null,
// //     isError: !!msg.isError,
// //     thinking: msg.thinking
// //       ? {
// //         role: msg.thinking.role || '',
// //         diagnosis: msg.thinking.diagnosis || '',
// //         tasks: Array.isArray(msg.thinking.tasks) ? msg.thinking.tasks : [],
// //         logs: Array.isArray(msg.thinking.logs) ? msg.thinking.logs : [],
// //         status: msg.thinking.status || 'done',
// //       }
// //       : null,
// //   }));
// // }

// function sanitizeMessagesForSave(messages = []) {
//   return messages.map((msg) => ({
//     ...msg,
//     id: msg.id,
//     role: msg.role,
//     text: msg.text || '',
//     mode: msg.mode || '',
//     content: msg.content ?? null,
//     isError: !!msg.isError,
//     thinking: msg.thinking
//       ? {
//           role: msg.thinking.role || '',
//           diagnosis: msg.thinking.diagnosis || '',
//           tasks: Array.isArray(msg.thinking.tasks) ? msg.thinking.tasks : [],
//           logs: Array.isArray(msg.thinking.logs) ? msg.thinking.logs : [],
//           status: msg.thinking.status || 'done',
//         }
//       : null,
//   }));
// }

// function hasUnreadTeacherMessages(messages = []) {
//   return messages.some((msg) => msg.role === 'teacher' && msg.unreadByStudent);
// }

// function getMessagePreview(msg) {
//   if (!msg) return '暂无文本';
//   if (msg.text) return msg.text;
//   if (msg.content?.reply) return msg.content.reply;
//   return '暂无文本';
// }

// // --- 工具函数区结束 ---

// const modes = [
//   { id: 'learning', name: '学习模式', icon: <BookOpen size={18} />, color: 'text-blue-600', bg: 'bg-blue-50' },
//   { id: 'project', name: '项目模式', icon: <Briefcase size={18} />, color: 'text-orange-600', bg: 'bg-orange-50' },
//   { id: 'competition', name: '竞赛模式', icon: <Trophy size={18} />, color: 'text-purple-600', bg: 'bg-purple-50' },
// ];

// const suggestedPrompts = [
//   '我不清楚什么是 TAM（目标可达市场），请结合实际例子给我讲一下？',
//   '能给我一个标准的大学生双创项目商业计划书（BP）的结构示例吗？',
//   '路演答辩时，评委最喜欢问的 3 个致命问题是什么？该怎么准备？',
//   '我的项目是关于校园跑腿外卖的，我应该如何进行竞品分析？',
// ];

// export default function FreeChatView({ currentUser }) {
//   const [conversations, setConversations] = useState([]);
//   const conversationsRef = useRef([]);
//   const [activeConversationId, setActiveConversationId] = useState(null);

//   const [input, setInput] = useState('');
//   const [activeMode, setActiveMode] = useState('learning');

//   const [loadingConversations, setLoadingConversations] = useState(true);
//   const [creatingConversation, setCreatingConversation] = useState(false);
//   const [bindingFile, setBindingFile] = useState(false);
//   const [loadingReply, setLoadingReply] = useState(false);
//   const [snapshotOpen, setSnapshotOpen] = useState(false);

//   const fileInputRef = useRef(null);
//   const chatEndRef = useRef(null);

//   useEffect(() => {
//     conversationsRef.current = conversations;
//   }, [conversations]);

//   const activeConversation = useMemo(
//     () => conversations.find((item) => item.id === activeConversationId) || null,
//     [conversations, activeConversationId]
//   );

//   const hasBoundDocument = activeConversation?.documentStatus === 'bound';
//   useEffect(() => {
//     if (!activeConversationId || !activeConversation) return;
//     if (!hasUnreadTeacherMessages(activeConversation.messages || [])) return;
    
//     const nextConversation = applyConversationUpdate(activeConversationId, (conv) => ({
//       ...conv,
//       messages: conv.messages.map((msg) =>
//         msg.role === 'teacher' && msg.unreadByStudent ? { ...msg, unreadByStudent: false } : msg
//       ),
//     }));
    
//     if (nextConversation) {
//       persistConversation(
//         nextConversation.id,
//         nextConversation.messages,
//         nextConversation.analysisSnapshot || {},
//         nextConversation.title,
//         nextConversation.lastMode || activeMode
//       );
//     }
//   }, [activeConversationId, activeConversation]);

//   const applyConversationUpdate = (conversationId, updater) => {
//     const nextList = conversationsRef.current.map((conv) => {
//       if (conv.id !== conversationId) return conv;
//       return updater(conv);
//     });
//     conversationsRef.current = nextList;
//     setConversations(nextList);
//     return nextList.find((conv) => conv.id === conversationId) || null;
//   };

//   useEffect(() => {
//     async function loadConversationList() {
//       if (!currentUser?.id) {
//         setLoadingConversations(false);
//         return;
//       }

//       try {
//         const data = await fetchConversations(currentUser.id);
//         const mapped = data.map(mapConversationFromApi);
//         conversationsRef.current = mapped;
//         setConversations(mapped);
//         if (mapped.length > 0) {
//           setActiveConversationId(mapped[0].id);
//         }
//       } catch (e) {
//         console.error('会话初始化失败', e);
//       } finally {
//         setLoadingConversations(false);
//       }
//     }

//     loadConversationList();
//   }, [currentUser?.id]);

//   useEffect(() => {
//     if (!hasBoundDocument && activeMode !== 'learning') {
//       setActiveMode('learning');
//     }
//   }, [hasBoundDocument, activeMode]);

//   useEffect(() => {
//     chatEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
//   }, [conversations, loadingReply]);

//   const ensureConversation = async () => {
//     if (activeConversationId) return activeConversationId;

//     setCreatingConversation(true);
//     try {
//       const created = await createConversation(currentUser.id, '新对话');
//       const mapped = mapConversationFromApi(created);
//       const nextList = [mapped, ...conversationsRef.current];
//       conversationsRef.current = nextList;
//       setConversations(nextList);
//       setActiveConversationId(mapped.id);
//       return mapped.id;
//     } finally {
//       setCreatingConversation(false);
//     }
//   };

//   const handleNewConversation = async () => {
//     if (!currentUser?.id) return;

//     setCreatingConversation(true);
//     try {
//       const created = await createConversation(currentUser.id, '新对话');
//       const mapped = mapConversationFromApi(created);
//       const nextList = [mapped, ...conversationsRef.current];
//       conversationsRef.current = nextList;
//       setConversations(nextList);
//       setActiveConversationId(mapped.id);
//       setInput('');
//       setActiveMode('learning');
//       setSnapshotOpen(false);
//     } catch (e) {
//       alert(e?.response?.data?.detail || e.message || '创建新对话失败');
//     } finally {
//       setCreatingConversation(false);
//     }
//   };

//   const persistConversation = async (
//     conversationId,
//     messages,
//     analysisSnapshot,
//     title,
//     lastMode
//   ) => {
//     try {
//       await syncConversationState(
//         conversationId,
//         sanitizeMessagesForSave(messages),
//         analysisSnapshot,
//         title,
//         lastMode
//       );
//     } catch (e) {
//       console.error('会话持久化失败:', e);
//     }
//   };

//   const handleBindFileChange = async (e) => {
//     const file = e.target.files?.[0];
//     e.target.value = '';
//     if (!file) return;

//     try {
//       const conversationId = await ensureConversation();
//       setBindingFile(true);

//       const response = await bindConversationFile(conversationId, file);

//       const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
//         ...conv,
//         documentStatus: response.document_status || 'bound',
//         boundFileName: response.bound_file_name || '',
//         boundFileUploadedAt: response.bound_file_uploaded_at || '',
//         analysisSnapshot: safeParseJSON(response.analysis_snapshot, conv.analysisSnapshot || {}),
//         messages: [
//           ...conv.messages,
//           {
//             id: `assistant-bind-${Date.now()}`,
//             role: 'assistant',
//             text: `✅ 已成功绑定文档《${response.bound_file_name}》。从现在起，这个聊天框内的项目模式和竞赛模式都会默认基于该文档内容进行分析。`,
//           },
//         ],
//       }));

//       if (updatedConversation) {
//         await persistConversation(
//           conversationId,
//           updatedConversation.messages,
//           updatedConversation.analysisSnapshot,
//           updatedConversation.title,
//           'learning'
//         );
//       }

//       setActiveConversationId(conversationId);
//       setActiveMode('project');
//     } catch (e) {
//       alert(e?.response?.data?.detail || e.message || '绑定文档失败');
//     } finally {
//       setBindingFile(false);
//     }
//   };

//   const updateAssistantMessage = (conversationId, messageId, updater) => {
//     applyConversationUpdate(conversationId, (conv) => ({
//       ...conv,
//       messages: conv.messages.map((msg) => (msg.id === messageId ? updater(msg) : msg)),
//     }));
//   };

//   const appendThinkingLog = (conversationId, messageId, event) => {
//     updateAssistantMessage(conversationId, messageId, (msg) => ({
//       ...msg,
//       thinking: {
//         ...(msg.thinking || {}),
//         status: 'thinking',
//         logs: [...(msg.thinking?.logs || []), event],
//       },
//     }));
//   };

//   const handleSubmit = async (presetText = null) => {
//     const textToProcess = typeof presetText === 'string' ? presetText : input;
//     if (!textToProcess.trim()) return;

//     if ((activeMode === 'project' || activeMode === 'competition') && !hasBoundDocument) {
//       alert('请先在当前聊天框绑定商业计划书文档，再使用项目模式或竞赛模式。');
//       return;
//     }

//     const conversationId = await ensureConversation();
//     const currentConv =
//       conversationsRef.current.find((conv) => conv.id === conversationId) || null;
//     const activeTeacherInterventions = (currentConv?.analysisSnapshot?.teacher_interventions || [])
//       .filter((item) => item && item.active !== false);
//     const interventionPrefix = activeTeacherInterventions.length > 0
//       ? [
//           '【教师反向干预要求】（请在本轮回答中优先执行）',
//           ...activeTeacherInterventions.map((item, idx) => `- 干预${idx + 1}：${item.content}`),
//           '',
//         ].join('\n')
//       : '';

//     const assistantMessageId = `assistant-${Date.now()}`;
//     const userMessage = {
//       id: `user-${Date.now()}`,
//       role: 'user',
//       text: textToProcess,
//       mode: activeMode,
//     };

//     const pendingAssistantMessage = {
//       id: assistantMessageId,
//       role: 'assistant',
//       mode: activeMode,
//       content: null,
//       thinking: {
//         role: '',
//         diagnosis: '',
//         tasks: [],
//         logs: [],
//         status: 'thinking',
//       },
//     };

//     const nextTitle =
//       currentConv && currentConv.messages.length > 0
//         ? currentConv.title
//         : deriveConversationTitle(textToProcess);

//     const draftConversation = applyConversationUpdate(conversationId, (conv) => ({
//       ...conv,
//       title: nextTitle,
//       lastMode: activeMode,
//       messages: [...conv.messages, userMessage, pendingAssistantMessage],
//     }));

//     if (draftConversation) {
//       await persistConversation(
//         conversationId,
//         draftConversation.messages,
//         draftConversation.analysisSnapshot || {},
//         draftConversation.title,
//         activeMode
//       );
//     }

//     setInput('');
//     setLoadingReply(true);

//     try {
//       const data = await runAgentStream(
//         interventionPrefix
//           ? `${interventionPrefix}\n【学生本轮真实问题】\n${userMessage.text}`
//           : userMessage.text,
//         // userMessage.text,
//         activeMode,
//         currentConv?.threadId || conversationId,
//         [],
//         async (event) => {
//           if (event.type === 'log') {
//             appendThinkingLog(conversationId, assistantMessageId, event);
//             return;
//           }

//           if (event.type === 'final') {
//             const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
//               ...conv,
//               documentStatus: event.data.document_status || conv.documentStatus,
//               boundFileName: event.data.bound_file_name || conv.boundFileName,
//               boundFileUploadedAt: event.data.bound_file_uploaded_at || conv.boundFileUploadedAt,
//               analysisSnapshot: event.data.analysis_snapshot || conv.analysisSnapshot,
//               lastMode: activeMode,
//               threadId: event.data.thread_id || conv.threadId,
//               messages: conv.messages.map((msg) =>
//                 msg.id === assistantMessageId
//                   ? {
//                     ...msg,
//                     mode: activeMode,
//                     content: event.data.generated_content,
//                     thinking: {
//                       ...(msg.thinking || {}),
//                       role: event.data.selected_role,
//                       diagnosis: event.data.critic_diagnosis?.raw_analysis || '',
//                       tasks: event.data.planned_tasks || [],
//                       logs: msg.thinking?.logs || [],
//                       status: 'done',
//                     },
//                   }
//                   : msg
//               ),
//             }));

//             if (updatedConversation) {
//               await persistConversation(
//                 conversationId,
//                 updatedConversation.messages,
//                 updatedConversation.analysisSnapshot,
//                 updatedConversation.title,
//                 activeMode
//               );
//             }
//             if (activeMode === 'project' || activeMode === 'competition') {
//               setSnapshotOpen(true);
//             }
//             return;
//           }

//           if (event.type === 'error') {
//             const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
//               ...conv,
//               messages: conv.messages.map((msg) =>
//                 msg.id === assistantMessageId
//                   ? {
//                     ...msg,
//                     isError: true,
//                     text: event.message || '网络请求失败，请检查后端是否运行。',
//                     thinking: {
//                       ...(msg.thinking || {}),
//                       status: 'error',
//                       logs: msg.thinking?.logs || [],
//                     },
//                   }
//                   : msg
//               ),
//             }));

//             if (updatedConversation) {
//               await persistConversation(
//                 conversationId,
//                 updatedConversation.messages,
//                 updatedConversation.analysisSnapshot || {},
//                 updatedConversation.title,
//                 activeMode
//               );
//             }
//           }
//         },
//         conversationId
//       );

//       if (!data) {
//         throw new Error('未收到最终结果');
//       }
//     } catch (e) {
//       const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
//         ...conv,
//         messages: conv.messages.map((msg) =>
//           msg.id === assistantMessageId
//             ? {
//               ...msg,
//               isError: true,
//               text: e.message || '网络请求失败，请检查后端是否运行。',
//               thinking: {
//                 ...(msg.thinking || {}),
//                 status: 'error',
//                 logs: msg.thinking?.logs || [],
//               },
//             }
//             : msg
//         ),
//       }));

//       if (updatedConversation) {
//         await persistConversation(
//           conversationId,
//           updatedConversation.messages,
//           updatedConversation.analysisSnapshot || {},
//           updatedConversation.title,
//           activeMode
//         );
//       }
//     } finally {
//       setLoadingReply(false);
//     }
//   };

//   const renderModeButton = (mode) => {
//     const disabled = !hasBoundDocument && (mode.id === 'project' || mode.id === 'competition');

//     return (
//       <button
//         key={mode.id}
//         onClick={() => {
//           if (!disabled) setActiveMode(mode.id);
//         }}
//         disabled={disabled}
//         className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 border ${activeMode === mode.id && !disabled
//             ? `${mode.bg} ${mode.color} shadow-sm`
//             : disabled
//               ? 'text-slate-300 bg-slate-100 border-slate-200 cursor-not-allowed'
//               : 'text-slate-500 hover:bg-slate-100 border-transparent'
//           }`}
//       >
//         {mode.icon}
//         {mode.name}
//       </button>
//     );
//   };

//   return (
//     <div className="h-full min-h-0 flex overflow-hidden bg-white">
//       <div className="w-72 shrink-0 h-full min-h-0 bg-slate-50 border-r border-slate-200 flex flex-col">
//         <div className="p-4 shrink-0 border-b border-slate-200 space-y-3">
//           <button
//             onClick={handleNewConversation}
//             disabled={creatingConversation}
//             className="w-full flex items-center justify-center gap-2 bg-white border border-slate-200 hover:border-brand-500 hover:text-brand-600 text-slate-700 font-medium py-2.5 px-4 rounded-xl shadow-sm transition-all disabled:opacity-60"
//           >
//             {creatingConversation ? <Loader2 size={18} className="animate-spin" /> : <Plus size={18} />}
//             新建对话
//           </button>

//           <button
//             onClick={() => fileInputRef.current?.click()}
//             disabled={bindingFile || creatingConversation}
//             className="w-full flex items-center justify-center gap-2 bg-brand-600 hover:bg-brand-700 text-white font-medium py-2.5 px-4 rounded-xl transition-colors disabled:opacity-60"
//           >
//             {bindingFile ? <Loader2 size={18} className="animate-spin" /> : <Paperclip size={18} />}
//             上传 / 更新绑定文档
//           </button>

//           <input
//             ref={fileInputRef}
//             type="file"
//             className="hidden"
//             accept=".pdf,.doc,.docx,.txt,.md"
//             onChange={handleBindFileChange}
//           />
//         </div>

//         <div className="flex-1 min-h-0 overflow-y-auto px-3 py-4 space-y-2">
//           <div className="text-xs font-bold text-slate-400 px-2">我的对话</div>

//           {loadingConversations && (
//             <div className="flex items-center gap-2 text-sm text-slate-500 px-2 py-3">
//               <Loader2 size={16} className="animate-spin" />
//               正在加载会话...
//             </div>
//           )}

//           {!loadingConversations && conversations.length === 0 && (
//             <div className="px-3 py-8 text-sm text-slate-400 text-center">
//               还没有会话。点击上方“新建对话”开始使用。
//             </div>
//           )}

//           {conversations.map((conversation) => (
//             <button
//               key={conversation.id}
//               onClick={() => {
//                 setActiveConversationId(conversation.id);
//                 setSnapshotOpen(false);
//               }}
//               className={`w-full text-left px-3 py-3 rounded-xl transition-all border ${activeConversationId === conversation.id
//                   ? 'bg-brand-50 border-brand-200'
//                   : 'bg-white border-slate-200 hover:border-brand-200'
//                 }`}
//             >
//               <div className="flex items-start justify-between gap-2 mb-1">
//                 <div className="flex items-center gap-2 min-w-0">
//                   <MessageSquare
//                     size={15}
//                     className={
//                       activeConversationId === conversation.id ? 'text-brand-500' : 'text-slate-400'
//                     }
//                   />
//                   <span className="text-sm font-medium text-slate-700 truncate">
//                     {conversation.title}
//                   </span>
//                 </div>
//                 <div className="flex items-center gap-1 shrink-0">
//                   {hasUnreadTeacherMessages(conversation.messages || []) && (
//                     <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700">
//                       教师新消息
//                     </span>
//                   )}
//                   {conversation.documentStatus === 'bound' && (
//                     <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-100 text-red-700 shrink-0">
//                       已绑文档
//                     </span>
//                   )}
//                 </div>
                
//               </div>

//               <div className="text-xs text-slate-400 truncate">
//                 {conversation.boundFileName
//                   ? conversation.boundFileName
//                   : conversation.messages.length > 0
//                     // ? conversation.messages[conversation.messages.length - 1]?.text || '暂无文本'
//                     ? getMessagePreview(conversation.messages[conversation.messages.length - 1])
//                     : '未绑定文档'}
//               </div>
//             </button>
//           ))}
//         </div>
//       </div>

//       <div className="flex-1 min-w-0 h-full min-h-0 flex flex-col overflow-hidden bg-white">
//         {!activeConversation ? (
//           <div className="flex-1 min-h-0 flex flex-col items-center justify-center text-center px-6">
//             <div className="w-16 h-16 bg-gradient-to-tr from-brand-100 to-brand-50 rounded-2xl flex items-center justify-center shadow-sm border border-brand-100 mb-5">
//               <Bot size={36} className="text-brand-600" />
//             </div>
//             <h2 className="text-2xl font-semibold tracking-tight text-slate-800 mb-2">
//               欢迎使用创新创业教学智能体
//             </h2>
//             <p className="text-slate-500 text-sm max-w-xl leading-relaxed">
//               新建一个对话后，你可以先用学习模式提问；也可以给这个对话绑定一份 BP，让它升级为围绕该文档持续分析的工作会话。
//             </p>
//           </div>
//         ) : (
//           <>
//             <div className="relative shrink-0 border-b border-slate-200 bg-white">
//               <div className="px-5 py-3 border-b border-slate-100">
//                 <div className="flex items-center justify-between gap-3">
//                   <div className="min-w-0">
//                     <div className="text-[11px] font-bold text-slate-400 mb-0.5">当前对话</div>
//                     <div className="text-lg font-bold text-slate-800 truncate">
//                       {activeConversation.title}
//                     </div>
//                   </div>

//                   <button
//                     onClick={() => fileInputRef.current?.click()}
//                     disabled={bindingFile}
//                     className="inline-flex items-center gap-2 px-3 py-2 rounded-xl border border-slate-200 bg-white hover:border-brand-300 hover:text-brand-600 text-slate-600 transition-colors disabled:opacity-60 shrink-0"
//                   >
//                     {bindingFile ? <Loader2 size={16} className="animate-spin" /> : <RefreshCcw size={16} />}
//                     {activeConversation.documentStatus === 'bound' ? '更新文档' : '绑定文档'}
//                   </button>
//                 </div>
//               </div>

//               <div className="px-5 py-2 bg-red-50 border-b border-red-100">
//                 {hasBoundDocument ? (
//                   <div className="flex items-center justify-between gap-3">
//                     <div className="min-w-0 flex items-center gap-2">
//                       <FileText size={15} className="text-red-600 shrink-0" />
//                       <span className="text-sm text-red-800 truncate font-medium">
//                         {activeConversation.boundFileName}
//                       </span>
//                       <span className="text-xs text-red-500 shrink-0">
//                         {formatDateTime(activeConversation.boundFileUploadedAt)}
//                       </span>
//                     </div>

//                     <button
//                       onClick={() => setSnapshotOpen((v) => !v)}
//                       className="shrink-0 inline-flex items-center gap-1 text-xs text-amber-700 bg-white border border-amber-200 rounded-full px-3 py-1 hover:bg-amber-50"
//                     >
//                       文档分析面板
//                       {snapshotOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
//                     </button>
//                   </div>
//                 ) : (
//                   <div className="flex items-center justify-between gap-3">
//                     <div className="flex items-center gap-2 min-w-0">
//                       <AlertCircle size={15} className="text-red-500 shrink-0" />
//                       <span className="text-sm text-red-700 truncate">
//                         当前对话尚未绑定商业计划书，仅学习模式可用
//                       </span>
//                     </div>

//                     <button
//                       onClick={() => fileInputRef.current?.click()}
//                       className="shrink-0 text-xs text-red-700 bg-white border border-red-200 rounded-full px-3 py-1 hover:bg-red-50"
//                     >
//                       去绑定
//                     </button>
//                   </div>
//                 )}
//               </div>
//               {(activeConversation.analysisSnapshot?.assessment_review?.status === 'sent' ||
//                 (activeConversation.analysisSnapshot?.teacher_interventions || []).length > 0) && (
//                 <div className="px-5 py-2 bg-emerald-50 border-b border-emerald-100 flex items-center justify-between gap-3">
//                   <div className="text-sm text-emerald-700 truncate">
//                     {activeConversation.analysisSnapshot?.assessment_review?.status === 'sent'
//                       ? '该项目已收到教师复核意见，请及时查看并根据要求修改。'
//                       : `当前会话已有 ${(activeConversation.analysisSnapshot?.teacher_interventions || []).length} 条教师干预规则正在生效。`}
//                   </div>
//                 </div>
//               )}
//               <SnapshotOverlay open={snapshotOpen} snapshot={activeConversation.analysisSnapshot} />
//             </div>

//             <div className="flex-1 min-h-0 overflow-y-auto p-4 md:p-6 bg-slate-50/50">
//               <div className="max-w-4xl mx-auto space-y-6">
//                 {activeConversation.messages.length === 0 ? (
//                   <div className="min-h-full flex flex-col items-center justify-center text-slate-700 space-y-8 px-4">
//                     <div className="flex flex-col items-center space-y-4 text-center">
//                       <div className="w-16 h-16 bg-gradient-to-tr from-brand-100 to-brand-50 rounded-2xl flex items-center justify-center shadow-sm border border-brand-100">
//                         <Bot size={36} className="text-brand-600" />
//                       </div>
//                       <h2 className="text-2xl font-semibold tracking-tight">
//                         {hasBoundDocument
//                           ? '文档已绑定，可以开始基于 BP 深度分析'
//                           : '先学习概念，或先绑定一份商业计划书'}
//                       </h2>
//                       <p className="text-slate-500 text-sm text-center max-w-2xl">
//                         {hasBoundDocument
//                           ? '现在你可以在项目模式和竞赛模式之间切换，系统会持续基于当前绑定文档进行诊断与迭代。'
//                           : '你可以先用学习模式提问基础概念；准备好后再给这个对话绑定一份 BP。'}
//                       </p>
//                     </div>

//                     {!hasBoundDocument && (
//                       <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-3xl">
//                         {suggestedPrompts.map((prompt, index) => (
//                           <button
//                             key={index}
//                             onClick={() => handleSubmit(prompt)}
//                             className="text-left bg-white border border-slate-200 hover:border-brand-400 hover:shadow-md transition-all p-4 rounded-xl flex items-start gap-3 group"
//                           >
//                             <Sparkles
//                               size={18}
//                               className="text-brand-400 group-hover:text-brand-500 shrink-0 mt-0.5"
//                             />
//                             <span className="text-sm text-slate-600 group-hover:text-slate-800 leading-relaxed">
//                               {prompt}
//                             </span>
//                           </button>
//                         ))}
//                       </div>
//                     )}
//                   </div>
//                 ) : (
                  
//                   activeConversation.messages.map((msg, index) => {
//                     const isUser = msg.role === 'user';
//                     const isTeacher = msg.role === 'teacher';
//                     const isAssistant = !isUser && !isTeacher;
//                     return (
//                       <div
//                         key={msg.id || index}
//                         className={`flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}
//                       >
//                         <div
//                           className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 ${
//                             isUser
//                               ? 'bg-brand-100 text-brand-600'
//                               : isTeacher
//                                 ? 'bg-emerald-100 text-emerald-700'
//                                 : 'bg-slate-800 text-white'
//                           }`}
//                         >
//                           {isUser ? <User size={18} /> : isTeacher ? <MessageSquare size={18} /> : <Bot size={18} />}
//                         </div>
//                         <div
//                           className={`flex flex-col gap-2 max-w-[82%] ${isUser ? 'items-end' : 'items-start'}`}
//                         >
//                           {isUser ? (
//                             <div className={`px-5 py-3 rounded-2xl rounded-tr-sm shadow-sm whitespace-pre-wrap ${msg.teacherHighlight ? 'bg-yellow-100 text-slate-800 ring-2 ring-yellow-300' : 'bg-brand-600 text-white'}`}>
//                               {msg.text}
//                             </div>
//                           ) : isTeacher ? (
//                             <div className="bg-emerald-50 border border-emerald-200 px-5 py-4 rounded-2xl rounded-tl-sm shadow-sm w-full">
//                               {msg.quote && (
//                                 <div className="mb-3 bg-white/80 border border-emerald-100 rounded-xl p-3 text-xs text-emerald-800">
//                                   <div className="font-bold mb-1">引用批注</div>
//                                   <div className="opacity-80">{msg.quote.sourceRoleLabel}：</div>
//                                   <div className="mt-1 whitespace-pre-wrap">“{msg.quote.text}”</div>
//                                 </div>
//                               )}
//                               {msg.text && (
//                                 <p className="text-slate-700 whitespace-pre-wrap leading-relaxed">{msg.text}</p>
//                               )}
//                               {Array.isArray(msg.attachments) && msg.attachments.length > 0 && (
//                                 <div className="mt-3 flex flex-wrap gap-2">
//                                   {msg.attachments.map((file, idx) => (
//                                     <span key={idx} className="text-xs px-2 py-1 rounded-full bg-white border border-emerald-200 text-emerald-700">
//                                       附件：{file.name}
//                                     </span>
//                                   ))}
//                                 </div>
//                               )}
//                             </div>
//                           ) : (
//                             <div className={`bg-white border px-5 py-4 rounded-2xl rounded-tl-sm shadow-sm w-full ${msg.teacherHighlight ? 'border-yellow-300 ring-2 ring-yellow-100' : 'border-slate-200'}`}>
//                               {msg.isError ? (
//                                 <>
//                                   <ThinkingProcess thinking={msg.thinking} />
//                                   <p className="text-red-500 whitespace-pre-wrap">{msg.text}</p>
//                                 </>
//                               ) : (
//                                 <>
//                                   <ThinkingProcess thinking={msg.thinking} />
//                                   {msg.mode && msg.content ? (
//                                     <StructuredResponseRenderer mode={msg.mode} content={msg.content} />
//                                   ) : msg.text ? (
//                                     <p className="text-slate-700 whitespace-pre-wrap">{msg.text}</p>
//                                   ) : null}
//                                 </>
//                               )}
//                             </div>
//                           )}
//                         </div>
//                       </div>
//                     );
//                   })

//                 )}

//                 <div ref={chatEndRef} />
//               </div>
//             </div>

//             <div className="shrink-0 bg-white border-t border-slate-200 p-4">
//               <div className="max-w-4xl mx-auto">
//                 <div className="flex items-center justify-between mb-3 gap-4 flex-wrap">
//                   <div className="flex gap-3 flex-wrap">{modes.map(renderModeButton)}</div>

//                   {!hasBoundDocument && (
//                     <div className="text-xs text-amber-600 bg-amber-50 border border-amber-200 px-3 py-1.5 rounded-full">
//                       当前仅学习模式可用
//                     </div>
//                   )}
//                 </div>

//                 <div className="relative flex items-end bg-white border border-slate-300 focus-within:border-brand-500 focus-within:ring-1 focus-within:ring-brand-500 rounded-xl shadow-sm transition-all overflow-hidden">
//                   <button
//                     onClick={() => fileInputRef.current?.click()}
//                     className="p-3 text-slate-400 hover:text-brand-500 transition-colors"
//                     title="上传并绑定文档"
//                   >
//                     <Paperclip size={20} />
//                   </button>

//                   <textarea
//                     value={input}
//                     onChange={(e) => setInput(e.target.value)}
//                     onKeyDown={(e) => {
//                       if (e.key === 'Enter' && !e.shiftKey) {
//                         e.preventDefault();
//                         handleSubmit();
//                       }
//                     }}
//                     placeholder={
//                       hasBoundDocument
//                         ? '在此继续基于当前绑定文档提问，按 Enter 发送（Shift+Enter 换行）...'
//                         : '先用学习模式提问，或点击左上 / 顶部按钮绑定商业计划书文档...'
//                     }
//                     className="flex-1 max-h-40 p-3 bg-transparent resize-none focus:outline-none text-slate-700 text-sm"
//                     rows={1}
//                     style={{ minHeight: '52px' }}
//                   />

//                   <button
//                     onClick={() => handleSubmit()}
//                     disabled={loadingReply || !input.trim()}
//                     className="m-2 p-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 disabled:hover:bg-brand-600 transition-colors"
//                   >
//                     {loadingReply ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
//                   </button>
//                 </div>

//                 <p className="text-center text-xs text-slate-400 mt-2">
//                   AI 输出仅作为教学辅助，请结合指导教师意见使用。
//                 </p>
//               </div>
//             </div>
//           </>
//         )}
//       </div>
//     </div>
//   );
// }


import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  Plus, MessageSquare, Send, FileText, BookOpen, Briefcase, Trophy,
  Bot, User, Sparkles, ChevronDown, ChevronUp, Loader2, Paperclip, AlertCircle, RefreshCcw
} from 'lucide-react';
import {
  API_BASE_URL, bindConversationFile, createConversation, fetchConversations,
  runAgentStream, syncConversationState
} from '../../api';

// 【导入拆分出来的组件】确保这三个文件和 FreeChatView.jsx 在同一个目录下
import SnapshotOverlay from './SnapshotOverlay';
import ThinkingProcess from './ThinkingProcess';
import StructuredResponseRenderer from './StructuredResponseRenderer';

// --- 工具函数区 ---
function safeParseJSON(raw, fallback) {
  if (!raw) return fallback;
  try {
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

function formatDateTime(raw) {
  if (!raw) return '未知时间';
  const date = new Date(raw);
  if (Number.isNaN(date.getTime())) return raw;
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function deriveConversationTitle(text) {
  const cleaned = (text || '').trim();
  if (!cleaned) return '新对话';
  return cleaned.length > 18 ? `${cleaned.slice(0, 18)}...` : cleaned;
}

function mapConversationFromApi(item) {
  return {
    id: item.id,
    studentId: item.student_id,
    title: item.title || '新对话',
    messages: safeParseJSON(item.chat_history, []),
    documentStatus: item.document_status || 'none',
    boundFileName: item.bound_file_name || '',
    boundFileUploadedAt: item.bound_file_uploaded_at || '',
    analysisSnapshot: safeParseJSON(item.analysis_snapshot, {}),
    lastMode: item.last_mode || 'learning',
    createdAt: item.created_at || '',
    updatedAt: item.updated_at || '',
    threadId: item.id,
  };
}


function sanitizeMessagesForSave(messages = []) {
  return messages.map((msg) => ({
    ...msg,
    id: msg.id,
    role: msg.role,
    text: msg.text || '',
    mode: msg.mode || '',
    content: msg.content ?? null,
    isError: !!msg.isError,
    thinking: msg.thinking
      ? {
          role: msg.thinking.role || '',
          diagnosis: msg.thinking.diagnosis || '',
          tasks: Array.isArray(msg.thinking.tasks) ? msg.thinking.tasks : [],
          logs: Array.isArray(msg.thinking.logs) ? msg.thinking.logs : [],
          status: msg.thinking.status || 'done',
        }
      : null,
  }));
}

function hasUnreadTeacherMessages(messages = []) {
  return messages.some((msg) => msg.role === 'teacher' && msg.unreadByStudent);
}

function getMessagePreview(msg) {
  if (!msg) return '暂无文本';
  if (msg.kind === 'assessment_report') return '老师下发了评估复核报告';
  if (msg.text) return msg.text;
  if (msg.content?.reply) return msg.content.reply;
  return '暂无文本';
}

function buildAttachmentDownloadUrl(file) {
  if (!file) return '#';
  if (file.download_url?.startsWith('http')) return file.download_url;
  return `${API_BASE_URL.replace(/\/api\/v1$/, '')}${file.download_url || ''}`;
}

// --- 工具函数区结束 ---

const modes = [
  { id: 'learning', name: '学习模式', icon: <BookOpen size={18} />, color: 'text-blue-600', bg: 'bg-blue-50' },
  { id: 'project', name: '项目模式', icon: <Briefcase size={18} />, color: 'text-orange-600', bg: 'bg-orange-50' },
  { id: 'competition', name: '竞赛模式', icon: <Trophy size={18} />, color: 'text-purple-600', bg: 'bg-purple-50' },
];

const suggestedPrompts = [
  '我不清楚什么是 TAM（目标可达市场），请结合实际例子给我讲一下？',
  '能给我一个标准的大学生双创项目商业计划书（BP）的结构示例吗？',
  '路演答辩时，评委最喜欢问的 3 个致命问题是什么？该怎么准备？',
  '我的项目是关于校园跑腿外卖的，我应该如何进行竞品分析？',
];


function TeacherAssessmentMessageCard({ msg }) {
  const report = msg?.report || {};
  const items = report.rubric_table || [];
  return (
    <div className="rounded-2xl border border-emerald-200 bg-white overflow-hidden shadow-sm w-full">
      <div className="px-4 py-3 bg-emerald-50 border-b border-emerald-100 flex items-center gap-2 text-emerald-800 font-bold text-sm">
        <Sparkles size={16} /> 教师复核评估报告
      </div>
      <div className="p-4 space-y-4">
        {msg.text ? (
          <div className="rounded-xl bg-slate-50 border border-slate-200 p-3 text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">
            {msg.text}
          </div>
        ) : null}
        <div className="rounded-xl border border-slate-200 overflow-hidden">
          <div className="px-3 py-2 bg-slate-50 border-b border-slate-200 font-bold text-slate-800 text-sm">Rubric Table</div>
          <div className="divide-y divide-slate-100">
            {items.map((row, idx) => (
              <div key={idx} className="p-3 space-y-2">
                <div className="flex items-center justify-between gap-3">
                  <div className="font-semibold text-slate-800 text-sm">{row.dimension}</div>
                  <div className="text-xs rounded-full px-2 py-1 bg-emerald-100 text-emerald-700 font-bold">
                    教师评分 {row.teacher_score ?? row.score ?? 0} 分
                  </div>
                </div>
                {row.evidence_trace ? (
                  <div className="text-xs text-slate-600 bg-blue-50 border border-blue-100 rounded-lg p-3 leading-relaxed">
                    <strong>Evidence Trace：</strong> {row.evidence_trace}
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        </div>
        {report.revision_suggestions ? (
          <div className="rounded-xl bg-blue-50 border border-blue-100 p-3">
            <div className="font-bold text-blue-800 text-sm mb-2">Revision Suggestions</div>
            <div className="text-sm text-blue-700 whitespace-pre-wrap leading-relaxed">{report.revision_suggestions}</div>
          </div>
        ) : null}
        {report.instructor_review_notes ? (
          <div className="rounded-xl bg-slate-50 border border-slate-200 p-3">
            <div className="font-bold text-slate-800 text-sm mb-2">Instructor Review Notes</div>
            <div className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">{report.instructor_review_notes}</div>
          </div>
        ) : null}
        {Array.isArray(msg.attachments) && msg.attachments.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {msg.attachments.map((file, idx) => (
              <a
                key={idx}
                href={buildAttachmentDownloadUrl(file)}
                target="_blank"
                rel="noreferrer"
                className="text-xs px-2 py-1 rounded-full bg-white border border-emerald-200 text-emerald-700 inline-flex items-center gap-1 hover:bg-emerald-50"
              >
                <Paperclip size={12} /> {file.name}
              </a>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default function FreeChatView({ currentUser }) {
  const [conversations, setConversations] = useState([]);
  const conversationsRef = useRef([]);
  const [activeConversationId, setActiveConversationId] = useState(null);

  const [input, setInput] = useState('');
  const [activeMode, setActiveMode] = useState('learning');

  const [loadingConversations, setLoadingConversations] = useState(true);
  const [creatingConversation, setCreatingConversation] = useState(false);
  const [bindingFile, setBindingFile] = useState(false);
  const [loadingReply, setLoadingReply] = useState(false);
  const [snapshotOpen, setSnapshotOpen] = useState(false);

  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    conversationsRef.current = conversations;
  }, [conversations]);

  const activeConversation = useMemo(
    () => conversations.find((item) => item.id === activeConversationId) || null,
    [conversations, activeConversationId]
  );

  const hasBoundDocument = activeConversation?.documentStatus === 'bound';

  const applyConversationUpdate = (conversationId, updater) => {
    const nextList = conversationsRef.current.map((conv) => {
      if (conv.id !== conversationId) return conv;
      return updater(conv);
    });
    conversationsRef.current = nextList;
    setConversations(nextList);
    return nextList.find((conv) => conv.id === conversationId) || null;
  };

  const markConversationTeacherMessagesRead = async (conversationId) => {
    const targetConversation = conversationsRef.current.find((conv) => conv.id === conversationId);
    if (!targetConversation || !hasUnreadTeacherMessages(targetConversation.messages || [])) return;

    const nextConversation = applyConversationUpdate(conversationId, (conv) => ({
      ...conv,
      messages: conv.messages.map((msg) =>
        msg.role === 'teacher' && msg.unreadByStudent ? { ...msg, unreadByStudent: false } : msg
      ),
    }));

    if (nextConversation) {
      await persistConversation(
        nextConversation.id,
        nextConversation.messages,
        nextConversation.analysisSnapshot || {},
        nextConversation.title,
        nextConversation.lastMode || activeMode
      );
    }
  };

  const handleSelectConversation = async (conversationId) => {
    setActiveConversationId(conversationId);
    setSnapshotOpen(false);
    await markConversationTeacherMessagesRead(conversationId);
  };

  useEffect(() => {
    async function loadConversationList() {
      if (!currentUser?.id) {
        setLoadingConversations(false);
        return;
      }

      try {
        const data = await fetchConversations(currentUser.id);
        const mapped = data.map(mapConversationFromApi);
        conversationsRef.current = mapped;
        setConversations(mapped);
        if (mapped.length > 0) {
          setActiveConversationId(mapped[0].id);
        }
      } catch (e) {
        console.error('会话初始化失败', e);
      } finally {
        setLoadingConversations(false);
      }
    }

    loadConversationList();
  }, [currentUser?.id]);

  useEffect(() => {
    if (!hasBoundDocument && activeMode !== 'learning') {
      setActiveMode('learning');
    }
  }, [hasBoundDocument, activeMode]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [conversations, loadingReply]);

  const ensureConversation = async () => {
    if (activeConversationId) return activeConversationId;

    setCreatingConversation(true);
    try {
      const created = await createConversation(currentUser.id, '新对话');
      const mapped = mapConversationFromApi(created);
      const nextList = [mapped, ...conversationsRef.current];
      conversationsRef.current = nextList;
      setConversations(nextList);
      setActiveConversationId(mapped.id);
      return mapped.id;
    } finally {
      setCreatingConversation(false);
    }
  };

  const handleNewConversation = async () => {
    if (!currentUser?.id) return;

    setCreatingConversation(true);
    try {
      const created = await createConversation(currentUser.id, '新对话');
      const mapped = mapConversationFromApi(created);
      const nextList = [mapped, ...conversationsRef.current];
      conversationsRef.current = nextList;
      setConversations(nextList);
      setActiveConversationId(mapped.id);
      setInput('');
      setActiveMode('learning');
      setSnapshotOpen(false);
    } catch (e) {
      alert(e?.response?.data?.detail || e.message || '创建新对话失败');
    } finally {
      setCreatingConversation(false);
    }
  };

  const persistConversation = async (
    conversationId,
    messages,
    analysisSnapshot,
    title,
    lastMode
  ) => {
    try {
      await syncConversationState(
        conversationId,
        sanitizeMessagesForSave(messages),
        analysisSnapshot,
        title,
        lastMode
      );
    } catch (e) {
      console.error('会话持久化失败:', e);
    }
  };

  const handleBindFileChange = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;

    try {
      const conversationId = await ensureConversation();
      setBindingFile(true);

      const response = await bindConversationFile(conversationId, file);

      const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
        ...conv,
        documentStatus: response.document_status || 'bound',
        boundFileName: response.bound_file_name || '',
        boundFileUploadedAt: response.bound_file_uploaded_at || '',
        analysisSnapshot: safeParseJSON(response.analysis_snapshot, conv.analysisSnapshot || {}),
        messages: [
          ...conv.messages,
          {
            id: `assistant-bind-${Date.now()}`,
            role: 'assistant',
            text: `✅ 已成功绑定文档《${response.bound_file_name}》。从现在起，这个聊天框内的项目模式和竞赛模式都会默认基于该文档内容进行分析。`,
          },
        ],
      }));

      if (updatedConversation) {
        await persistConversation(
          conversationId,
          updatedConversation.messages,
          updatedConversation.analysisSnapshot,
          updatedConversation.title,
          'learning'
        );
      }

      setActiveConversationId(conversationId);
      setActiveMode('project');
    } catch (e) {
      alert(e?.response?.data?.detail || e.message || '绑定文档失败');
    } finally {
      setBindingFile(false);
    }
  };

  const updateAssistantMessage = (conversationId, messageId, updater) => {
    applyConversationUpdate(conversationId, (conv) => ({
      ...conv,
      messages: conv.messages.map((msg) => (msg.id === messageId ? updater(msg) : msg)),
    }));
  };

  const appendThinkingLog = (conversationId, messageId, event) => {
    updateAssistantMessage(conversationId, messageId, (msg) => ({
      ...msg,
      thinking: {
        ...(msg.thinking || {}),
        status: 'thinking',
        logs: [...(msg.thinking?.logs || []), event],
      },
    }));
  };

  const handleSubmit = async (presetText = null) => {
    const textToProcess = typeof presetText === 'string' ? presetText : input;
    if (!textToProcess.trim()) return;

    if ((activeMode === 'project' || activeMode === 'competition') && !hasBoundDocument) {
      alert('请先在当前聊天框绑定商业计划书文档，再使用项目模式或竞赛模式。');
      return;
    }

    const conversationId = await ensureConversation();
    const currentConv =
      conversationsRef.current.find((conv) => conv.id === conversationId) || null;
    const activeTeacherInterventions = (currentConv?.analysisSnapshot?.teacher_interventions || [])
      .filter((item) => item && item.active !== false);
    const interventionPrefix = activeTeacherInterventions.length > 0
      ? [
          '【教师反向干预要求】（请在本轮回答中优先执行）',
          ...activeTeacherInterventions.map((item, idx) => `- 干预${idx + 1}：${item.content}`),
          '',
        ].join('\n')
      : '';

    const assistantMessageId = `assistant-${Date.now()}`;
    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      text: textToProcess,
      mode: activeMode,
    };

    const pendingAssistantMessage = {
      id: assistantMessageId,
      role: 'assistant',
      mode: activeMode,
      content: null,
      thinking: {
        role: '',
        diagnosis: '',
        tasks: [],
        logs: [],
        status: 'thinking',
      },
    };

    const nextTitle =
      currentConv && currentConv.messages.length > 0
        ? currentConv.title
        : deriveConversationTitle(textToProcess);

    const draftConversation = applyConversationUpdate(conversationId, (conv) => ({
      ...conv,
      title: nextTitle,
      lastMode: activeMode,
      messages: [...conv.messages, userMessage, pendingAssistantMessage],
    }));

    if (draftConversation) {
      await persistConversation(
        conversationId,
        draftConversation.messages,
        draftConversation.analysisSnapshot || {},
        draftConversation.title,
        activeMode
      );
    }

    setInput('');
    setLoadingReply(true);

    try {
      const data = await runAgentStream(
        interventionPrefix
          ? `${interventionPrefix}\n【学生本轮真实问题】\n${userMessage.text}`
          : userMessage.text,
        // userMessage.text,
        activeMode,
        currentConv?.threadId || conversationId,
        [],
        async (event) => {
          if (event.type === 'log') {
            appendThinkingLog(conversationId, assistantMessageId, event);
            return;
          }

          if (event.type === 'final') {
            const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
              ...conv,
              documentStatus: event.data.document_status || conv.documentStatus,
              boundFileName: event.data.bound_file_name || conv.boundFileName,
              boundFileUploadedAt: event.data.bound_file_uploaded_at || conv.boundFileUploadedAt,
              analysisSnapshot: event.data.analysis_snapshot || conv.analysisSnapshot,
              lastMode: activeMode,
              threadId: event.data.thread_id || conv.threadId,
              messages: conv.messages.map((msg) =>
                msg.id === assistantMessageId
                  ? {
                    ...msg,
                    mode: activeMode,
                    content: event.data.generated_content,
                    thinking: {
                      ...(msg.thinking || {}),
                      role: event.data.selected_role,
                      diagnosis: event.data.critic_diagnosis?.raw_analysis || '',
                      tasks: event.data.planned_tasks || [],
                      logs: msg.thinking?.logs || [],
                      status: 'done',
                    },
                  }
                  : msg
              ),
            }));

            if (updatedConversation) {
              await persistConversation(
                conversationId,
                updatedConversation.messages,
                updatedConversation.analysisSnapshot,
                updatedConversation.title,
                activeMode
              );
            }
            if (activeMode === 'project' || activeMode === 'competition') {
              setSnapshotOpen(true);
            }
            return;
          }

          if (event.type === 'error') {
            const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
              ...conv,
              messages: conv.messages.map((msg) =>
                msg.id === assistantMessageId
                  ? {
                    ...msg,
                    isError: true,
                    text: event.message || '网络请求失败，请检查后端是否运行。',
                    thinking: {
                      ...(msg.thinking || {}),
                      status: 'error',
                      logs: msg.thinking?.logs || [],
                    },
                  }
                  : msg
              ),
            }));

            if (updatedConversation) {
              await persistConversation(
                conversationId,
                updatedConversation.messages,
                updatedConversation.analysisSnapshot || {},
                updatedConversation.title,
                activeMode
              );
            }
          }
        },
        conversationId
      );

      if (!data) {
        throw new Error('未收到最终结果');
      }
    } catch (e) {
      const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
        ...conv,
        messages: conv.messages.map((msg) =>
          msg.id === assistantMessageId
            ? {
              ...msg,
              isError: true,
              text: e.message || '网络请求失败，请检查后端是否运行。',
              thinking: {
                ...(msg.thinking || {}),
                status: 'error',
                logs: msg.thinking?.logs || [],
              },
            }
            : msg
        ),
      }));

      if (updatedConversation) {
        await persistConversation(
          conversationId,
          updatedConversation.messages,
          updatedConversation.analysisSnapshot || {},
          updatedConversation.title,
          activeMode
        );
      }
    } finally {
      setLoadingReply(false);
    }
  };

  const renderModeButton = (mode) => {
    const disabled = !hasBoundDocument && (mode.id === 'project' || mode.id === 'competition');

    return (
      <button
        key={mode.id}
        onClick={() => {
          if (!disabled) setActiveMode(mode.id);
        }}
        disabled={disabled}
        className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 border ${activeMode === mode.id && !disabled
            ? `${mode.bg} ${mode.color} shadow-sm`
            : disabled
              ? 'text-slate-300 bg-slate-100 border-slate-200 cursor-not-allowed'
              : 'text-slate-500 hover:bg-slate-100 border-transparent'
          }`}
      >
        {mode.icon}
        {mode.name}
      </button>
    );
  };

  return (
    <div className="h-full min-h-0 flex overflow-hidden bg-white">
      <div className="w-72 shrink-0 h-full min-h-0 bg-slate-50 border-r border-slate-200 flex flex-col">
        <div className="p-4 shrink-0 border-b border-slate-200 space-y-3">
          <button
            onClick={handleNewConversation}
            disabled={creatingConversation}
            className="w-full flex items-center justify-center gap-2 bg-white border border-slate-200 hover:border-brand-500 hover:text-brand-600 text-slate-700 font-medium py-2.5 px-4 rounded-xl shadow-sm transition-all disabled:opacity-60"
          >
            {creatingConversation ? <Loader2 size={18} className="animate-spin" /> : <Plus size={18} />}
            新建对话
          </button>

          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={bindingFile || creatingConversation}
            className="w-full flex items-center justify-center gap-2 bg-brand-600 hover:bg-brand-700 text-white font-medium py-2.5 px-4 rounded-xl transition-colors disabled:opacity-60"
          >
            {bindingFile ? <Loader2 size={18} className="animate-spin" /> : <Paperclip size={18} />}
            上传 / 更新绑定文档
          </button>

          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept=".pdf,.doc,.docx,.txt,.md"
            onChange={handleBindFileChange}
          />
        </div>

        <div className="flex-1 min-h-0 overflow-y-auto px-3 py-4 space-y-2">
          <div className="text-xs font-bold text-slate-400 px-2">我的对话</div>

          {loadingConversations && (
            <div className="flex items-center gap-2 text-sm text-slate-500 px-2 py-3">
              <Loader2 size={16} className="animate-spin" />
              正在加载会话...
            </div>
          )}

          {!loadingConversations && conversations.length === 0 && (
            <div className="px-3 py-8 text-sm text-slate-400 text-center">
              还没有会话。点击上方“新建对话”开始使用。
            </div>
          )}

          {conversations.map((conversation) => (
            <button
              key={conversation.id}
              onClick={() => {
                void handleSelectConversation(conversation.id);
              }}
              className={`w-full text-left px-3 py-3 rounded-xl transition-all border ${activeConversationId === conversation.id
                  ? 'bg-brand-50 border-brand-200'
                  : 'bg-white border-slate-200 hover:border-brand-200'
                }`}
            >
              <div className="flex items-start justify-between gap-2 mb-1">
                <div className="flex items-center gap-2 min-w-0">
                  <MessageSquare
                    size={15}
                    className={
                      activeConversationId === conversation.id ? 'text-brand-500' : 'text-slate-400'
                    }
                  />
                  <span className="text-sm font-medium text-slate-700 truncate">
                    {conversation.title}
                  </span>
                </div>
                <div className="flex items-center gap-1 shrink-0">
                  {hasUnreadTeacherMessages(conversation.messages || []) && (
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700">
                      教师新消息
                    </span>
                  )}
                  {conversation.documentStatus === 'bound' && (
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-100 text-red-700 shrink-0">
                      已绑文档
                    </span>
                  )}
                </div>
                
              </div>

              <div className="text-xs text-slate-400 truncate">
                {conversation.boundFileName
                  ? conversation.boundFileName
                  : conversation.messages.length > 0
                    // ? conversation.messages[conversation.messages.length - 1]?.text || '暂无文本'
                    ? getMessagePreview(conversation.messages[conversation.messages.length - 1])
                    : '未绑定文档'}
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 min-w-0 h-full min-h-0 flex flex-col overflow-hidden bg-white">
        {!activeConversation ? (
          <div className="flex-1 min-h-0 flex flex-col items-center justify-center text-center px-6">
            <div className="w-16 h-16 bg-gradient-to-tr from-brand-100 to-brand-50 rounded-2xl flex items-center justify-center shadow-sm border border-brand-100 mb-5">
              <Bot size={36} className="text-brand-600" />
            </div>
            <h2 className="text-2xl font-semibold tracking-tight text-slate-800 mb-2">
              欢迎使用创新创业教学智能体
            </h2>
            <p className="text-slate-500 text-sm max-w-xl leading-relaxed">
              新建一个对话后，你可以先用学习模式提问；也可以给这个对话绑定一份 BP，让它升级为围绕该文档持续分析的工作会话。
            </p>
          </div>
        ) : (
          <>
            <div className="relative shrink-0 border-b border-slate-200 bg-white">
              <div className="px-5 py-3 border-b border-slate-100">
                <div className="flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="text-[11px] font-bold text-slate-400 mb-0.5">当前对话</div>
                    <div className="text-lg font-bold text-slate-800 truncate">
                      {activeConversation.title}
                    </div>
                  </div>

                  <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={bindingFile}
                    className="inline-flex items-center gap-2 px-3 py-2 rounded-xl border border-slate-200 bg-white hover:border-brand-300 hover:text-brand-600 text-slate-600 transition-colors disabled:opacity-60 shrink-0"
                  >
                    {bindingFile ? <Loader2 size={16} className="animate-spin" /> : <RefreshCcw size={16} />}
                    {activeConversation.documentStatus === 'bound' ? '更新文档' : '绑定文档'}
                  </button>
                </div>
              </div>

              <div className="px-5 py-2 bg-red-50 border-b border-red-100">
                {hasBoundDocument ? (
                  <div className="flex items-center justify-between gap-3">
                    <div className="min-w-0 flex items-center gap-2">
                      <FileText size={15} className="text-red-600 shrink-0" />
                      <span className="text-sm text-red-800 truncate font-medium">
                        {activeConversation.boundFileName}
                      </span>
                      <span className="text-xs text-red-500 shrink-0">
                        {formatDateTime(activeConversation.boundFileUploadedAt)}
                      </span>
                    </div>

                    <button
                      onClick={() => setSnapshotOpen((v) => !v)}
                      className="shrink-0 inline-flex items-center gap-1 text-xs text-amber-700 bg-white border border-amber-200 rounded-full px-3 py-1 hover:bg-amber-50"
                    >
                      文档分析面板
                      {snapshotOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </button>
                  </div>
                ) : (
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2 min-w-0">
                      <AlertCircle size={15} className="text-red-500 shrink-0" />
                      <span className="text-sm text-red-700 truncate">
                        当前对话尚未绑定商业计划书，仅学习模式可用
                      </span>
                    </div>

                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="shrink-0 text-xs text-red-700 bg-white border border-red-200 rounded-full px-3 py-1 hover:bg-red-50"
                    >
                      去绑定
                    </button>
                  </div>
                )}
              </div>
              {(activeConversation.analysisSnapshot?.assessment_review?.status === 'sent' ||
                (activeConversation.analysisSnapshot?.teacher_interventions || []).length > 0) && (
                <div className="px-5 py-2 bg-emerald-50 border-b border-emerald-100 flex items-center justify-between gap-3">
                  <div className="text-sm text-emerald-700 truncate">
                    {activeConversation.analysisSnapshot?.assessment_review?.status === 'sent'
                      ? '该项目已收到教师复核意见，请及时查看并根据要求修改。'
                      : `当前会话已有 ${(activeConversation.analysisSnapshot?.teacher_interventions || []).length} 条教师干预规则正在生效。`}
                  </div>
                </div>
              )}
              <SnapshotOverlay open={snapshotOpen} snapshot={activeConversation.analysisSnapshot} />
            </div>

            <div className="flex-1 min-h-0 overflow-y-auto p-4 md:p-6 bg-slate-50/50">
              <div className="max-w-4xl mx-auto space-y-6">
                {activeConversation.messages.length === 0 ? (
                  <div className="min-h-full flex flex-col items-center justify-center text-slate-700 space-y-8 px-4">
                    <div className="flex flex-col items-center space-y-4 text-center">
                      <div className="w-16 h-16 bg-gradient-to-tr from-brand-100 to-brand-50 rounded-2xl flex items-center justify-center shadow-sm border border-brand-100">
                        <Bot size={36} className="text-brand-600" />
                      </div>
                      <h2 className="text-2xl font-semibold tracking-tight">
                        {hasBoundDocument
                          ? '文档已绑定，可以开始基于 BP 深度分析'
                          : '先学习概念，或先绑定一份商业计划书'}
                      </h2>
                      <p className="text-slate-500 text-sm text-center max-w-2xl">
                        {hasBoundDocument
                          ? '现在你可以在项目模式和竞赛模式之间切换，系统会持续基于当前绑定文档进行诊断与迭代。'
                          : '你可以先用学习模式提问基础概念；准备好后再给这个对话绑定一份 BP。'}
                      </p>
                    </div>

                    {!hasBoundDocument && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-3xl">
                        {suggestedPrompts.map((prompt, index) => (
                          <button
                            key={index}
                            onClick={() => handleSubmit(prompt)}
                            className="text-left bg-white border border-slate-200 hover:border-brand-400 hover:shadow-md transition-all p-4 rounded-xl flex items-start gap-3 group"
                          >
                            <Sparkles
                              size={18}
                              className="text-brand-400 group-hover:text-brand-500 shrink-0 mt-0.5"
                            />
                            <span className="text-sm text-slate-600 group-hover:text-slate-800 leading-relaxed">
                              {prompt}
                            </span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  
                  activeConversation.messages.map((msg, index) => {
                    const isUser = msg.role === 'user';
                    const isTeacher = msg.role === 'teacher';
                    const isAssistant = !isUser && !isTeacher;
                    return (
                      <div
                        key={msg.id || index}
                        className={`flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}
                      >
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 ${
                            isUser
                              ? 'bg-brand-100 text-brand-600'
                              : isTeacher
                                ? 'bg-emerald-100 text-emerald-700'
                                : 'bg-slate-800 text-white'
                          }`}
                        >
                          {isUser ? <User size={18} /> : isTeacher ? <MessageSquare size={18} /> : <Bot size={18} />}
                        </div>
                        <div
                          className={`flex flex-col gap-2 max-w-[82%] ${isUser ? 'items-end' : 'items-start'}`}
                        >
                          {isUser ? (
                            <div className={`px-5 py-3 rounded-2xl rounded-tr-sm shadow-sm whitespace-pre-wrap ${msg.teacherHighlight ? 'bg-yellow-100 text-slate-800 ring-2 ring-yellow-300' : 'bg-brand-600 text-white'}`}>
                              {msg.text}
                            </div>
                          ) : isTeacher ? (
                            msg.kind === 'assessment_report' ? (
                              <div className="w-full max-w-3xl">
                                <TeacherAssessmentMessageCard msg={msg} />
                              </div>
                            ) : (
                              <div className="bg-emerald-50 border border-emerald-200 px-5 py-4 rounded-2xl rounded-tl-sm shadow-sm w-full max-w-3xl">
                                {msg.quote && (
                                  <div className="mb-3 bg-white/80 border border-emerald-100 rounded-xl p-3 text-xs text-emerald-800">
                                    <div className="font-bold mb-1">引用批注</div>
                                    <div className="opacity-80">{msg.quote.sourceRoleLabel}：</div>
                                    <div className="mt-1 whitespace-pre-wrap">“{msg.quote.text}”</div>
                                  </div>
                                )}
                                {msg.text && (
                                  <p className="text-slate-700 whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                                )}
                                {Array.isArray(msg.attachments) && msg.attachments.length > 0 && (
                                  <div className="mt-3 flex flex-wrap gap-2">
                                    {msg.attachments.map((file, idx) => (
                                      <a
                                        key={idx}
                                        href={buildAttachmentDownloadUrl(file)}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="text-xs px-2 py-1 rounded-full bg-white border border-emerald-200 text-emerald-700 inline-flex items-center gap-1 hover:bg-emerald-50"
                                      >
                                        <Paperclip size={12} /> {file.name}
                                      </a>
                                    ))}
                                  </div>
                                )}
                              </div>
                            )
                          ) : (
                            <div className={`bg-white border px-5 py-4 rounded-2xl rounded-tl-sm shadow-sm w-full ${msg.teacherHighlight ? 'border-yellow-300 ring-2 ring-yellow-100' : 'border-slate-200'}`}>
                              {msg.isError ? (
                                <>
                                  <ThinkingProcess thinking={msg.thinking} />
                                  <p className="text-red-500 whitespace-pre-wrap">{msg.text}</p>
                                </>
                              ) : (
                                <>
                                  <ThinkingProcess thinking={msg.thinking} />
                                  {msg.mode && msg.content ? (
                                    <StructuredResponseRenderer mode={msg.mode} content={msg.content} />
                                  ) : msg.text ? (
                                    <p className="text-slate-700 whitespace-pre-wrap">{msg.text}</p>
                                  ) : null}
                                </>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })

                )}

                <div ref={chatEndRef} />
              </div>
            </div>

            <div className="shrink-0 bg-white border-t border-slate-200 p-4">
              <div className="max-w-4xl mx-auto">
                <div className="flex items-center justify-between mb-3 gap-4 flex-wrap">
                  <div className="flex gap-3 flex-wrap">{modes.map(renderModeButton)}</div>

                  {!hasBoundDocument && (
                    <div className="text-xs text-amber-600 bg-amber-50 border border-amber-200 px-3 py-1.5 rounded-full">
                      当前仅学习模式可用
                    </div>
                  )}
                </div>

                <div className="relative flex items-end bg-white border border-slate-300 focus-within:border-brand-500 focus-within:ring-1 focus-within:ring-brand-500 rounded-xl shadow-sm transition-all overflow-hidden">
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="p-3 text-slate-400 hover:text-brand-500 transition-colors"
                    title="上传并绑定文档"
                  >
                    <Paperclip size={20} />
                  </button>

                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmit();
                      }
                    }}
                    placeholder={
                      hasBoundDocument
                        ? '在此继续基于当前绑定文档提问，按 Enter 发送（Shift+Enter 换行）...'
                        : '先用学习模式提问，或点击左上 / 顶部按钮绑定商业计划书文档...'
                    }
                    className="flex-1 max-h-40 p-3 bg-transparent resize-none focus:outline-none text-slate-700 text-sm"
                    rows={1}
                    style={{ minHeight: '52px' }}
                  />

                  <button
                    onClick={() => handleSubmit()}
                    disabled={loadingReply || !input.trim()}
                    className="m-2 p-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 disabled:hover:bg-brand-600 transition-colors"
                  >
                    {loadingReply ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                  </button>
                </div>

                <p className="text-center text-xs text-slate-400 mt-2">
                  AI 输出仅作为教学辅助，请结合指导教师意见使用。
                </p>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
