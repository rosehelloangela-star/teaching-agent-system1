import React, { useEffect, useMemo, useState } from 'react';
import { Activity, Bot, CheckCircle, Loader2, Send, ShieldAlert, User, UserCog, Search, FileText, CheckSquare, Clock } from 'lucide-react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar as RechartsRadar,
  ResponsiveContainer,
} from 'recharts';
import {
  fetchTeacherProjectConversations, 
  fetchTeacherConversationDetail,
  runAgent,
  syncConversationState,
  saveConversationEvaluation // <--- 新增
} from '../api';

function safeParseJSON(raw, fallback) {
  if (!raw) return fallback;
  if (typeof raw === 'object') return raw;
  try {
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

export default function StudentProfileView({ currentUser }) {
  const [students, setStudents] = useState([]);
  const [loadingList, setLoadingList] = useState(true);
  const [search, setSearch] = useState('');

  const [activeStudentId, setActiveStudentId] = useState('');
  const [selectedConvId, setSelectedConvId] = useState('');
  
  const [detail, setDetail] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const [interventionType, setInterventionType] = useState('rule');
  const [interventionRule, setInterventionRule] = useState('');
  const [ruleInjected, setRuleInjected] = useState(false);

  const [evalLoading, setEvalLoading] = useState(false);
  const [evalReport, setEvalReport] = useState(null);

  const activeStudent = useMemo(() => students.find(s => s.student_id === activeStudentId), [students, activeStudentId]);
  const messages = useMemo(() => safeParseJSON(detail?.chat_history, []), [detail?.chat_history]);
  const snapshot = useMemo(() => safeParseJSON(detail?.analysis_snapshot, {}), [detail?.analysis_snapshot]);
  const interventions = snapshot.teacher_interventions || [];

  useEffect(() => {
    async function loadList() {
      if (!currentUser?.id) return;
      setLoadingList(true);
      try {
        const rawData = await fetchTeacherProjectConversations(currentUser.id, search);
        const studentMap = {};
        rawData.forEach(conv => {
          if (!studentMap[conv.student_id]) {
            studentMap[conv.student_id] = {
              student_id: conv.student_id,
              student_name: conv.student_name,
              class_name: conv.class_name,
              completed_conversations: [],
              ongoing_conversations: []
            };
          }
          const snap = safeParseJSON(conv.analysis_snapshot, {});
          const isCompleted = snap?.project?.overall_status === 'completed' || (snap?.project?.stage_flow?.current_stage_index >= 3);
          if (isCompleted) {
            studentMap[conv.student_id].completed_conversations.push(conv);
          } else {
            studentMap[conv.student_id].ongoing_conversations.push(conv);
          }
        });
        const groupedStudents = Object.values(studentMap);
        setStudents(groupedStudents);
        if (!activeStudentId && groupedStudents.length > 0) setActiveStudentId(groupedStudents[0].student_id);
      } catch (error) {
        console.error('加载项目列表失败', error);
      } finally {
        setLoadingList(false);
      }
    }
    loadList();
  }, [currentUser?.id, search]);

  useEffect(() => {
    if (activeStudent) {
      const allConvs = [...activeStudent.completed_conversations, ...activeStudent.ongoing_conversations];
      const stillValid = allConvs.some(c => c.id === selectedConvId);
      if (!stillValid) {
        setSelectedConvId(allConvs[0]?.id || '');
        if(!allConvs[0]) setDetail(null);
        setEvalReport(null);
      }
    }
  }, [activeStudent, selectedConvId]);

  useEffect(() => {
    async function loadDetail() {
      if (!selectedConvId || !currentUser?.id) return;
      setLoadingDetail(true);
      try {
        const data = await fetchTeacherConversationDetail(selectedConvId, currentUser.id);
        setDetail(data);
        // 【修改点】：如果有已保存的报告，直接反序列化显示
        if (data.evaluation_report) {
          setEvalReport(safeParseJSON(data.evaluation_report, null));
        } else {
          setEvalReport(null);
        }
      } catch (error) {
        console.error('加载会话详情失败', error);
      } finally {
        setLoadingDetail(false);
      }
    }
    loadDetail();
  }, [selectedConvId, currentUser?.id]);

  const persistFullConversation = async (nextMessages, nextSnapshot) => {
    if (!detail?.id) return;
    const updated = await syncConversationState(detail.id, nextMessages, nextSnapshot, detail.title, detail.last_mode || 'project');
    setDetail(prev => ({ ...prev, chat_history: updated.chat_history, analysis_snapshot: updated.analysis_snapshot }));
  };

  const handleInjectRule = async () => {
    if (!detail?.id || !interventionRule.trim()) return;
    const intervention = {
      id: `intervention-${Date.now()}`, type: interventionType, content: interventionRule.trim(), created_at: new Date().toISOString(), active: true,
    };
    const teacherMessage = {
      id: `teacher-intervention-${Date.now()}`, role: 'teacher', mode: 'teacher_intervention', 
      text: `【教师${interventionType === 'case' ? '案例注入' : '干预规则'}】${interventionRule.trim()}`, unreadByStudent: true,
    };
    const nextSnapshot = { ...snapshot, teacher_interventions: [...interventions, intervention] };
    await persistFullConversation([...messages, teacherMessage], nextSnapshot);
    setRuleInjected(true);
    setTimeout(() => setRuleInjected(false), 3000);
    setInterventionRule('');
  };

  const handleGenerateProcessEval = async () => {
    if (!detail?.id || messages.length === 0) return;
    setEvalLoading(true);
    try {
      const rawLogText = messages.map(m => `${m.role}: ${m.text || JSON.stringify(m.content || {})}`).join('\n');
      const prompt = `请分析以下学生历史日志，生成完整的教学建议和表现报告：\n${rawLogText}`;
      
      const data = await runAgent(prompt, 'profile_evaluator', `eval_thread_${detail.id}`, [], detail.id);
      setEvalReport(data.generated_content);

      // 【修改点】：生成成功后，静默保存到数据库
      await saveConversationEvaluation(detail.id, data.generated_content);
      
    } catch (error) {
      console.error(error);
      alert('评估报告生成失败，请检查网络或后端 Agent 日志。');
    } finally {
      setEvalLoading(false);
    }
  };
  const isCurrentConvCompleted = activeStudent?.completed_conversations.some(c => c.id === selectedConvId);

  return (
    <div className="flex-1 min-h-0 flex overflow-hidden">
      <div className="w-80 shrink-0 border-r border-slate-200 bg-white flex flex-col">
        <div className="p-5 border-b border-slate-200">
          <h1 className="text-xl font-bold text-slate-800">👤 交互画像与反向干预</h1>
          <div className="mt-4 relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="检索学生姓名..." className="w-full pl-9 pr-3 py-2 rounded-xl border border-slate-300 text-sm outline-none focus:ring-2 focus:ring-brand-500"/>
          </div>
        </div>
        <div className="flex-1 min-h-0 overflow-y-auto p-3 space-y-2">
          {loadingList ? (
            <div className="p-4 text-center text-sm text-slate-500"><Loader2 className="animate-spin inline mr-2"/> 加载中...</div>
          ) : students.map((student) => (
            <button key={student.student_id} onClick={() => setActiveStudentId(student.student_id)}
              className={`w-full text-left rounded-xl p-4 transition-all border ${activeStudentId === student.student_id ? 'border-brand-400 bg-brand-50 shadow-sm' : 'border-slate-100 bg-white hover:border-brand-200'}`}>
              <div className="font-bold text-slate-800">{student.student_name}</div>
              <div className="text-xs text-slate-500 mt-1">{student.class_name}</div>
              <div className="flex gap-2 mt-3 text-xs">
                <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded-full flex items-center gap-1"><CheckSquare size={12}/> {student.completed_conversations.length} 可评估</span>
                <span className="bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full flex items-center gap-1"><Clock size={12}/> {student.ongoing_conversations.length} 冲关中</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 min-h-0 flex flex-col bg-slate-50">
        {activeStudent ? (
          <>
            <div className="bg-white p-4 border-b border-slate-200 flex items-center gap-4 shrink-0">
              <span className="text-sm font-bold text-slate-700">当前学生会话：</span>
              <select value={selectedConvId} onChange={(e) => setSelectedConvId(e.target.value)} className="border border-slate-300 rounded-lg p-2 text-sm focus:ring-2 focus:ring-brand-500 outline-none w-96 bg-slate-50">
                <optgroup label="✅ 可评估（到达三阶或通关）">
                  {activeStudent.completed_conversations.map(c => <option key={c.id} value={c.id}>{c.title || '未命名项目'}</option>)}
                </optgroup>
                <optgroup label="⏳ 冲关中（一、二阶段）">
                  {activeStudent.ongoing_conversations.map(c => <option key={c.id} value={c.id}>{c.title || '未命名项目'}</option>)}
                </optgroup>
              </select>
            </div>

            <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-2 gap-0">
              {/* 核心修改点：左侧这整个容器自带 overflow-y-auto，内容变长即可整栏滑动 */}
              <div className="min-h-0 p-6 border-r border-slate-200 overflow-y-auto flex flex-col gap-6">
                <div>
                  <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-2"><Activity size={18} className="text-blue-500" /> 真实交互日志记录</h3>
                  {/* 把高度由 h-64 改为了 h-[550px]，让聊天框大幅变长 */}
                  <div className="bg-white border border-slate-200 rounded-xl p-4 h-[350px] overflow-y-auto text-xs space-y-4 font-mono shadow-inner">
                    {loadingDetail ? <Loader2 className="animate-spin text-slate-400 mx-auto mt-10" /> : messages.map((msg, i) => (
                      <div key={i} className={`flex gap-2 p-2 rounded ${msg.mode === 'teacher_intervention' ? 'bg-red-50 border border-red-200' : msg.role === 'teacher' ? 'bg-emerald-50' : 'bg-slate-50'}`}>
                        {msg.role === 'user' ? <User size={14} className="text-brand-600 shrink-0 mt-0.5" /> : 
                         msg.mode === 'teacher_intervention' ? <ShieldAlert size={14} className="text-red-600 shrink-0 mt-0.5" /> :
                         msg.role === 'teacher' ? <UserCog size={14} className="text-emerald-700 shrink-0 mt-0.5" /> : <Bot size={14} className="text-slate-800 shrink-0 mt-0.5" />}
                        <span className={`break-all ${msg.mode === 'teacher_intervention' ? 'font-bold text-red-700' : ''}`}>{msg.text || JSON.stringify(msg.content)}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-5">
                  <div>
                    <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-3"><ShieldAlert size={18} className="text-red-500" /> 强制教学干预注入</h3>
                    <div className="flex gap-2">
                      <select value={interventionType} onChange={(e) => setInterventionType(e.target.value)} className="border border-slate-300 rounded-lg p-2 text-sm bg-white outline-none">
                        <option value="rule">规则</option><option value="case">案例</option>
                      </select>
                      <input value={interventionRule} onChange={(e) => setInterventionRule(e.target.value)} placeholder="要求学生先回答单位经济..." className="flex-1 border border-slate-300 rounded-lg p-2 text-sm outline-none bg-red-50/20"/>
                      <button onClick={handleInjectRule} disabled={!interventionRule.trim()} className="bg-red-500 hover:bg-red-600 text-white px-4 rounded-lg text-sm font-bold flex items-center gap-2 disabled:opacity-50 transition-colors">
                        {ruleInjected ? <CheckCircle size={16} /> : <Send size={16} />}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div className="min-h-0 p-6 overflow-y-auto">
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm min-h-full">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="font-bold text-slate-800 flex items-center gap-2">
                      <FileText size={18} className="text-purple-500" /> 交互溯源与诊断画像
                    </h3>
                    <button onClick={handleGenerateProcessEval} disabled={!selectedConvId || !isCurrentConvCompleted || evalLoading} className="bg-slate-800 hover:bg-slate-900 disabled:opacity-40 text-white px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition-all">
                      {evalLoading && <Loader2 size={16} className="animate-spin" />} 生成画像报告
                    </button>
                  </div>

                  {!isCurrentConvCompleted && !evalReport && (
                    <div className="bg-orange-50 text-orange-700 p-4 rounded-lg text-sm border border-orange-200 mb-4 flex gap-2">
                      <span className="text-xl">⚠️</span>
                      <div><strong>画像生成已锁定</strong><br/>当前选择的会话较浅。画像评估需基于有一定深度记录（进入第三阶段或带✅）的项目生成。</div>
                    </div>
                  )}

                  {evalReport && evalReport.capabilities ? (
                    <div className="space-y-6">
                      
                      {/* 1. 核心能力量化打分（加入雷达图） */}
                      <div>
                        <h4 className="text-sm font-bold text-slate-800 mb-3 border-b pb-2">📊 核心能力量化打分</h4>
                        
                        {evalReport.capabilities.length > 0 && (
                          <div className="bg-slate-50 border border-slate-100 rounded-xl p-4 mb-4 h-64 shadow-inner flex justify-center items-center">
                            <ResponsiveContainer width="100%" height="100%">
                              <RadarChart cx="50%" cy="50%" outerRadius="75%" data={evalReport.capabilities}>
                                <PolarGrid stroke="#cbd5e1" />
                                <PolarAngleAxis dataKey="dimension" tick={{ fill: '#475569', fontSize: 11, fontWeight: 'bold' }} />
                                <PolarRadiusAxis angle={30} domain={[0, 5]} tick={{ fill: '#94a3b8', fontSize: 10 }} tickCount={6} />
                                <RechartsRadar name="能力得分" dataKey="score" stroke="#3b82f6" fill="#60a5fa" fillOpacity={0.4} />
                              </RadarChart>
                            </ResponsiveContainer>
                          </div>
                        )}

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {evalReport.capabilities.map((cap, idx) => (
                            <div key={idx} className="bg-white border border-slate-200 rounded-lg p-3 shadow-sm">
                              <div className="flex justify-between items-center mb-1">
                                <span className="font-bold text-slate-700">{cap.dimension}</span>
                                <span className="text-blue-600 font-bold text-lg">{cap.score} <span className="text-xs text-slate-400 font-normal">/ 5</span></span>
                              </div>
                              <div className="text-xs text-slate-500">{cap.reason}</div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* 2. 三轮对话行为诊断 */}
                      <div>
                        <h4 className="text-sm font-bold text-slate-800 mb-3 border-b pb-2">🧠 阶段对话行为诊断</h4>
                        <div className="space-y-3">
                          {(evalReport.stage_diagnoses || []).map((stage, idx) => (
                            <div key={idx} className="bg-blue-50/50 p-3 rounded-lg border border-blue-100">
                              <div className="font-bold text-blue-900 text-sm mb-1">{stage.stage_name}</div>
                              <div className="text-sm text-blue-800 leading-relaxed">{stage.performance}</div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* 3. 核心证据溯源 */}
                      <div>
                        <h4 className="text-sm font-bold text-slate-800 mb-3 border-b pb-2">🔎 核心证据溯源</h4>
                        <div className="space-y-3">
                          {(evalReport.evidences || []).map((ev, idx) => (
                            <div key={idx} className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-sm">
                              <div className="text-slate-600 mb-2">
                                <span className="font-bold text-slate-700 mr-2">学生原话:</span>
                                <span className="italic bg-amber-50 px-1 rounded">"{ev.student_quote}"</span>
                              </div>
                              <div className="text-slate-700">
                                <span className="font-bold text-slate-700 mr-2">能力映射:</span>
                                {ev.implication}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center h-48 text-slate-400">
                      <Bot size={32} className="mb-2 opacity-50" />
                      <p className="text-sm">点击上方按钮，AI 将根据项目多轮对话日志生成深度评估报告</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-slate-400">请在左侧选择学生</div>
        )}
      </div>
    </div>
  );
}