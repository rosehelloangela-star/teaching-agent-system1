import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, User, Bot, ArrowLeft, CheckCircle, FolderGit2, Paperclip, UploadCloud, FileText, X } from 'lucide-react';
import { runAgentStream, fetchProjects, createProject, syncProjectChat } from '../api';
// 【修改点】：分别从各自的独立文件中默认导入
import StructuredResponseRenderer from './chat/StructuredResponseRenderer';
import ThinkingProcess from './chat/ThinkingProcess';

export default function ProjectWorkspaceView({ currentUser }) {
  const [projects, setProjects] = useState([]);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [activeProjectId, setActiveProjectId] = useState(null);
  const [newProjectFile, setNewProjectFile] = useState(null);
  const [newProjectName, setNewProjectName] = useState('');
  const [projectInput, setProjectInput] = useState('');
  const [projectLoading, setProjectLoading] = useState(false);

  const chatEndRef = useRef(null);
  const projectFileInputRef = useRef(null);

  const activeProject = projects.find(p => p.id === activeProjectId);
  const currentStudentId = currentUser?.id;

  useEffect(() => {
    async function loadMyProjects() {
      if (!currentStudentId) {
        setIsInitialLoading(false);
        return;
      }
      try {
        const data = await fetchProjects(currentStudentId);
        const formattedProjects = data.map(p => ({
          id: p.id,
          name: p.name,
          date: new Date(p.created_at).toISOString().split('T')[0],
          status: p.status,
          instructorNotes: p.instructor_notes,
          messages: p.chat_history ? JSON.parse(p.chat_history) : [],
        }));
        setProjects(formattedProjects);
      } catch (e) {
        console.error('数据拉取失败', e);
      } finally {
        setIsInitialLoading(false);
      }
    }
    loadMyProjects();
  }, [currentStudentId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [projects, projectLoading]);

  const handleNewProjectFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setNewProjectFile(file);
      const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '');
      setNewProjectName(nameWithoutExt);
    }
  };

  const handleClearNewProject = () => {
    setNewProjectFile(null);
    setNewProjectName('');
    if (projectFileInputRef.current) projectFileInputRef.current.value = '';
  };

  const handleCreateProject = async () => {
    if (!newProjectName.trim() || !newProjectFile || !currentStudentId) return;
    const isDuplicate = projects.some(p => p.name === newProjectName);
    if (isDuplicate) {
      alert('⚠️ 该项目名称已存在！请修改名称，或者在左侧列表中选中该项目后继续交流。');
      return;
    }

    setProjectLoading(true);
    try {
      const newP = await createProject(newProjectName, currentStudentId, newProjectFile, '');

      const newFrontendProject = {
        id: newP.id,
        name: newP.name,
        date: new Date(newP.created_at).toISOString().split('T')[0],
        status: newP.status,
        instructorNotes: newP.instructor_notes,
        messages: [{
          role: 'assistant',
          text: `✅ 系统已成功读取你的初始项目计划书附件《${newProjectFile.name}》。项目已成功存入数据库建档！\n\n你可以随时针对该附件内容向我提问，或者在底部继续上传新的补充材料。`
        }]
      };

      setProjects([newFrontendProject, ...projects]);
      handleClearNewProject();
      setActiveProjectId(newFrontendProject.id);
    } catch (e) {
      alert('创建项目失败，请确保 FastAPI 后端已启动并正常运行。');
    } finally {
      setProjectLoading(false);
    }
  };

  const updateProjectAssistantMessage = (projectId, messageId, updater) => {
    setProjects(prev => prev.map(project => {
      if (project.id !== projectId) return project;
      return {
        ...project,
        messages: project.messages.map(msg => (
          msg.id === messageId ? updater(msg) : msg
        )),
      };
    }));
  };

  const appendThinkingLog = (projectId, messageId, event) => {
    updateProjectAssistantMessage(projectId, messageId, msg => ({
      ...msg,
      thinking: {
        ...(msg.thinking || {}),
        status: 'thinking',
        logs: [...(msg.thinking?.logs || []), event],
      },
    }));
  };

  const handleSubmitProjectChat = async () => {
    if (!projectInput.trim()) return;

    const targetProjectId = activeProjectId;
    const assistantMessageId = `assistant-${Date.now()}`;

    const userMsg = { id: `user-${Date.now()}`, role: 'user', text: projectInput };
    const pendingAssistantMessage = {
      id: assistantMessageId,
      role: 'assistant',
      mode: 'project',
      content: null,
      thinking: {
        role: '',
        diagnosis: '',
        tasks: [],
        logs: [],
        status: 'thinking',
      },
    };

    setProjects(prev => prev.map(project => project.id === targetProjectId ? {
      ...project,
      messages: [...project.messages, userMsg, pendingAssistantMessage],
    } : project));

    setProjectInput('');
    setProjectLoading(true);

    try {
      const data = await runAgentStream(
        userMsg.text,
        'project',
        String(targetProjectId),
        [],
        (event) => {
          if (event.type === 'log') {
            appendThinkingLog(targetProjectId, assistantMessageId, event);
            return;
          }

          if (event.type === 'final') {
            const finalData = event.data;
            updateProjectAssistantMessage(targetProjectId, assistantMessageId, msg => ({
              ...msg,
              mode: 'project',
              content: finalData.generated_content,
              thinking: {
                ...(msg.thinking || {}),
                role: finalData.selected_role,
                diagnosis: finalData.critic_diagnosis?.raw_analysis || '',
                tasks: finalData.planned_tasks || [],
                logs: msg.thinking?.logs || [],
                status: 'done',
              },
            }));
            return;
          }

          if (event.type === 'error') {
            updateProjectAssistantMessage(targetProjectId, assistantMessageId, msg => ({
              ...msg,
              isError: true,
              text: event.message || '项目模式调用失败，请稍后重试。',
              thinking: {
                ...(msg.thinking || {}),
                status: 'error',
                logs: msg.thinking?.logs || [],
              },
            }));
          }
        }
      );

      if (!data) {
        throw new Error('未收到最终结果');
      }

      setProjects(prev => prev.map(project => {
        if (project.id !== targetProjectId) return project;

        const messagesForDB = project.messages.map(msg => {
          const { thinking, id, ...rest } = msg;
          return rest;
        });

        syncProjectChat(targetProjectId, messagesForDB).catch(e => console.error(e));
        return project;
      }));
    } catch (e) {
      updateProjectAssistantMessage(targetProjectId, assistantMessageId, msg => ({
        ...msg,
        isError: true,
        text: e.message || '项目模式调用失败，请稍后重试。',
        thinking: {
          ...(msg.thinking || {}),
          status: 'error',
          logs: msg.thinking?.logs || [],
        },
      }));
    } finally {
      setProjectLoading(false);
    }
  };

  return (
    <div className="flex-1 flex bg-slate-50 relative overflow-hidden">
      <div className={`${activeProjectId ? 'w-80 border-r border-slate-200 hidden md:flex flex-col bg-slate-50 shrink-0' : 'w-full max-w-4xl mx-auto p-8 flex flex-col'}`}>
        {!activeProjectId && (
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-slate-800">🗂️ 我的项目库</h1>
            <p className="text-slate-500 text-sm mt-1">请上传你的商业计划书 (BP) 附件，系统将自动建档供导师查阅及后续深度评估。</p>
          </div>
        )}

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm mb-6 shrink-0 transition-all">
          <label className="text-sm font-bold text-slate-700 mb-3 block">上传计划书建立项目</label>
          <input type="file" ref={projectFileInputRef} onChange={handleNewProjectFileChange} className="hidden" accept=".pdf,.doc,.docx,.txt" />
          {!newProjectFile ? (
            <div onClick={() => projectFileInputRef.current?.click()} className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center bg-slate-50 hover:bg-slate-100 hover:border-emerald-400 transition-colors cursor-pointer group">
              <UploadCloud size={28} className="mx-auto text-slate-400 group-hover:text-emerald-500 mb-2 transition-colors" />
              <p className="text-sm font-medium text-slate-600 group-hover:text-emerald-600">点击上传 BP 附件</p>
            </div>
          ) : (
            <div className="space-y-3 animate-in fade-in duration-200">
              <div className="flex items-center justify-between bg-emerald-50 border border-emerald-100 p-3 rounded-lg">
                <div className="flex items-center gap-2 overflow-hidden">
                  <FileText size={16} className="text-emerald-600 shrink-0" />
                  <span className="text-xs text-emerald-800 font-medium truncate">{newProjectFile.name}</span>
                </div>
                <button onClick={handleClearNewProject} className="text-emerald-400 hover:text-emerald-700 p-1 shrink-0"><X size={14} /></button>
              </div>
              <div className="flex gap-2">
                <input value={newProjectName} onChange={e => setNewProjectName(e.target.value)} placeholder="确认或修改项目名称..." className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500 outline-none" />
                <button onClick={handleCreateProject} disabled={!newProjectName.trim() || projectLoading} className="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-emerald-700 disabled:opacity-50 transition-colors shrink-0">
                  {projectLoading ? <Loader2 size={16} className="animate-spin" /> : '确认建档'}
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="flex-1 overflow-y-auto space-y-3 pr-2">
          <label className="text-xs font-bold text-slate-500 block px-1 flex items-center gap-2">
            已建档项目
            {isInitialLoading && <Loader2 size={12} className="animate-spin text-emerald-500" />}
          </label>

          {!isInitialLoading && projects.length === 0 && (
            <div className="text-center py-8 text-slate-400 text-sm">暂无项目，请先上传附件建档</div>
          )}
          {projects.map(p => (
            <div key={p.id} onClick={() => setActiveProjectId(p.id)} className={`p-4 rounded-xl border cursor-pointer transition-all ${activeProjectId === p.id ? 'bg-emerald-50 border-emerald-500 shadow-sm' : 'bg-white border-slate-200 hover:border-emerald-300'}`}>
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-bold text-slate-800 text-sm">{p.name}</h3>
                {p.instructorNotes && <span className="bg-orange-100 text-orange-700 px-2 py-0.5 rounded text-[10px] font-bold shrink-0">有批注</span>}
              </div>
              <div className="flex items-center text-xs text-slate-500 gap-4">
                <span>{p.date}</span>
                <span className="flex items-center gap-1"><CheckCircle size={12} className="text-emerald-500" /> 已入库</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {activeProjectId && activeProject && (
        <div className="flex-1 flex flex-col bg-white animate-in slide-in-from-right-8 duration-200 relative border-l border-slate-200">
          <div className="h-14 border-b border-slate-200 flex items-center px-4 bg-white shrink-0 gap-3">
            <button onClick={() => setActiveProjectId(null)} className="md:hidden p-2 text-slate-500 hover:bg-slate-100 rounded-lg"><ArrowLeft size={18} /></button>
            <FolderGit2 size={20} className="text-emerald-600" />
            <h2 className="font-bold text-slate-800">{activeProject.name}</h2>
          </div>
          <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 bg-slate-50/50">
            {activeProject.instructorNotes && (
              <div className="bg-orange-50 border border-orange-200 rounded-2xl p-5 shadow-sm relative mt-2 max-w-3xl mx-auto">
                <div className="absolute -top-3 left-6 bg-orange-500 text-white text-[10px] font-bold px-2 py-1 rounded-full flex items-center gap-1 shadow-sm">
                  <User size={12} /> 来自导师的最新反馈
                </div>
                <p className="text-sm text-orange-900 font-medium leading-relaxed mt-1">
                  {activeProject.instructorNotes}
                </p>
              </div>
            )}
            {activeProject.messages.map((msg, i) => (
              <div key={msg.id || i} className={`flex gap-4 max-w-3xl mx-auto ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 ${msg.role === 'user' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-800 text-white'}`}>
                  {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                </div>
                <div className={`flex flex-col gap-2 max-w-[85%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                  {msg.role === 'user' ? (
                    <div className="bg-emerald-600 text-white px-4 py-2.5 rounded-2xl rounded-tr-sm text-sm whitespace-pre-wrap">{msg.text}</div>
                  ) : (
                    <div className="bg-white border border-slate-200 p-4 rounded-2xl rounded-tl-sm shadow-sm w-full">
                      {msg.isError ? (
                        <>
                          <ThinkingProcess thinking={msg.thinking} />
                          <p className="text-red-500 text-sm whitespace-pre-wrap">{msg.text}</p>
                        </>
                      ) : (
                        <>
                          <ThinkingProcess thinking={msg.thinking} />
                          {msg.mode && msg.content ? <StructuredResponseRenderer mode={msg.mode} content={msg.content} /> : msg.text ? <p className="text-sm text-slate-700 whitespace-pre-wrap">{msg.text}</p> : null}
                        </>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          <div className="p-4 border-t border-slate-200 bg-white shrink-0">
            <div className="max-w-3xl mx-auto flex items-end bg-slate-50 border border-slate-300 rounded-xl overflow-hidden focus-within:ring-2 focus-within:ring-emerald-500">
              <button className="p-3 text-slate-400 hover:text-emerald-600 transition-colors"><Paperclip size={18} /></button>
              <textarea value={projectInput} onChange={e => setProjectInput(e.target.value)} onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmitProjectChat(); } }} placeholder="针对该项目提问，或发送更新材料..." className="flex-1 p-3 resize-none bg-transparent focus:outline-none text-sm max-h-32" rows={1} />
              <button onClick={handleSubmitProjectChat} disabled={projectLoading || !projectInput.trim()} className="m-2 p-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50">
                {projectLoading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
