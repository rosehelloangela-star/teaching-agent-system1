import React, { useState, useEffect } from 'react';
import { UserCog, ShieldAlert, Activity, Send, CheckCircle, Loader2, Bot, User } from 'lucide-react';
import { runAgent, fetchAllProjects } from '../api'; // 引入API

export default function StudentProfileView() {
  const [allProjects, setAllProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState('');
  
  const [interventionRule, setInterventionRule] = useState('');
  const [ruleInjected, setRuleInjected] = useState(false);
  
  const [evalLoading, setEvalLoading] = useState(false);
  const [processReport, setProcessReport] = useState('');

  // 1. 初始化拉取所有项目
  useEffect(() => {
    async function loadAllProjects() {
      const data = await fetchAllProjects();
      setAllProjects(data);
    }
    loadAllProjects();
  }, []);

  const activeProject = allProjects.find(p => p.id === selectedProjectId);
  // 解析存储在后端的 JSON 聊天记录
  const projectMessages = activeProject?.chat_history ? JSON.parse(activeProject.chat_history) : [];

  const handleInjectRule = () => {
    if (!interventionRule.trim()) return;
    setRuleInjected(true);
    setTimeout(() => setRuleInjected(false), 3000);
    setInterventionRule('');
  };

  const handleGenerateProcessEval = async () => {
    if (projectMessages.length === 0) {
      alert("该项目暂无有效的交互对话记录，无法生成评估。");
      return;
    }
    setEvalLoading(true);
    try {
      // 2. 把真实聊天记录喂给 AI 生成报告
      const rawLogText = projectMessages.map(m => `${m.role === 'user' ? '学生' : 'AI'}: ${m.text || JSON.stringify(m.content)}`).join('\n');
      
      const prompt = `请根据以下真实对话记录，生成对话过程评估报告，包含：1. 核心能力打分(逻辑、商业等) 2. 行为诊断表现 3. 证据引用。\n记录如下：\n${rawLogText}`;
      
      const data = await runAgent(prompt, 'instructor', `eval_thread_${selectedProjectId}`);
      setProcessReport(data.generated_content.teaching_suggestions || JSON.stringify(data.generated_content));
    } catch(e) {
      setProcessReport("评估报告生成失败。");
    } finally {
      setEvalLoading(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-8">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">👤 交互画像与反向干预 (Learning Profile)</h1>
          <p className="text-slate-500 mt-1">查看学生在项目工作台中的真实对话记录，并生成过程性评价</p>
        </div>
        <select 
          value={selectedProjectId} 
          onChange={e => { setSelectedProjectId(e.target.value); setProcessReport(''); }}
          className="border border-slate-300 rounded-lg px-4 py-2 bg-white text-sm outline-none focus:ring-2 focus:ring-brand-500"
        >
          <option value="">-- 选择目标学生项目 --</option>
          {allProjects.map(p => (
            <option key={p.id} value={p.id}>{p.student_id} - {p.name}</option>
          ))}
        </select>
      </div>

      {activeProject ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="flex flex-col gap-6">
            
            {/* 真实交互日志查阅 */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex-1 flex flex-col">
              <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-4">
                <Activity size={18} className="text-blue-500"/> 真实交互日志记录
              </h3>
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 flex-1 max-h-96 overflow-y-auto text-xs text-slate-600 space-y-4 font-mono">
                {projectMessages.length === 0 ? (
                  <p className="text-slate-400 text-center mt-10">暂无对话记录</p>
                ) : (
                  projectMessages.map((msg, i) => (
                    <div key={i} className={`flex gap-2 ${msg.role === 'user' ? '' : 'bg-white p-2 border border-slate-100 rounded'}`}>
                      {msg.role === 'user' ? <User size={14} className="text-brand-600 shrink-0 mt-0.5"/> : <Bot size={14} className="text-slate-800 shrink-0 mt-0.5"/>}
                      <span className="leading-relaxed break-all">
                        {msg.text || JSON.stringify(msg.content)}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* 干预注入保留... */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-3">
                <ShieldAlert size={18} className="text-red-500"/> 强制教学干预注入
              </h3>
              <textarea
                value={interventionRule}
                onChange={e => setInterventionRule(e.target.value)}
                placeholder="在此输入干预规则..."
                className="w-full border border-slate-300 rounded-xl p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-red-500 mb-3 bg-red-50/30"
                rows={2}
              />
              <button
                onClick={handleInjectRule}
                disabled={!interventionRule.trim()}
                className="w-full bg-red-500 hover:bg-red-600 disabled:bg-slate-300 text-white py-2.5 rounded-xl text-sm font-bold flex items-center justify-center gap-2 transition-colors"
              >
                {ruleInjected ? <><CheckCircle size={16}/> 规则已生效</> : <><Send size={16}/> 注入规则</>}
              </button>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-slate-800 flex items-center gap-2">
                <UserCog size={18} className="text-purple-500"/> 真实过程评估报告 (基于日志)
              </h3>
              <button
                onClick={handleGenerateProcessEval}
                disabled={evalLoading || projectMessages.length === 0}
                className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2"
              >
                {evalLoading ? <Loader2 size={16} className="animate-spin"/> : '基于日志生成画像'}
              </button>
            </div>
            
            <div className="flex-1 bg-purple-50/30 border border-purple-100 rounded-xl p-5 overflow-y-auto">
              {!processReport && !evalLoading && (
                <div className="h-full flex flex-col items-center justify-center text-slate-400">
                  <UserCog size={32} className="opacity-20 mb-2"/>
                  <p className="text-sm">点击按钮，读取学生的历史对话记录进行分析打分</p>
                </div>
              )}
              {processReport && (
                <pre className="text-sm text-slate-700 whitespace-pre-wrap font-sans leading-relaxed">
                  {processReport}
                </pre>
              )}
            </div>
          </div>
          
        </div>
      ) : (
        <div className="h-64 flex flex-col items-center justify-center border-2 border-dashed border-slate-300 rounded-2xl bg-white text-slate-400">
          <UserCog size={48} className="opacity-20 mb-4" />
          <p>请选择一个真实的学生项目以查看交互画像。</p>
        </div>
      )}
    </div>
  );
}