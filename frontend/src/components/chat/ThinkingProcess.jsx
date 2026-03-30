import React, { useState } from 'react';
import { Brain, Sparkles, Loader2, ChevronDown, ChevronUp } from 'lucide-react';

export default function ThinkingProcess({ thinking }) {
  const [isOpen, setIsOpen] = useState(false);
  if (!thinking) return null;

  const logs = Array.isArray(thinking.logs) ? thinking.logs : [];
  const status = thinking.status || 'done';
  const isThinking = status === 'thinking';
  const isError = status === 'error';

  return (
    <div className="mb-4 bg-slate-50 border border-slate-200 rounded-xl overflow-hidden transition-all duration-300">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3 text-sm text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Brain size={16} className="text-brand-500" />
          <span className="font-medium">{isThinking ? 'Agent 正在思考中...' : 'Agent 思考过程'}</span>
          {isThinking && <Loader2 size={14} className="animate-spin text-brand-500" />}
        </div>
        <div className="flex items-center gap-2">
          {isError && <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-100 text-red-600">失败</span>}
          {isThinking && <span className="text-[10px] px-2 py-0.5 rounded-full bg-brand-100 text-brand-600">进行中</span>}
          {!isThinking && !isError && <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-600">已完成</span>}
          {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </button>

      {isOpen && (
        <div className="p-4 border-t border-slate-200 text-xs text-slate-600 space-y-4 bg-slate-100/50">
          {logs.length === 0 && <div className="text-slate-400">正在等待后端返回执行日志...</div>}
          
          {logs.length > 0 && (
            <div>
              <span className="font-bold text-slate-700 flex items-center gap-1 mb-2">
                <Brain size={12} /> 实时执行日志
              </span>
              <div className="space-y-2 bg-white p-3 rounded border border-slate-200">
                {logs.map((log, idx) => (
                  <div key={`${log.timestamp || 't'}-${idx}`} className="flex items-start gap-2 leading-relaxed">
                    <span className="text-[10px] text-slate-400 font-mono shrink-0 mt-0.5">{log.timestamp || '--:--:--'}</span>
                    <span className="px-1.5 py-0.5 bg-slate-100 text-slate-600 rounded font-mono text-[10px] shrink-0">
                      {log.node || 'agent'}
                    </span>
                    <span className={log.level === 'error' ? 'text-red-600' : log.level === 'warning' ? 'text-orange-600' : 'text-slate-700'}>
                      {log.message}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {thinking.role && (
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-700">调用角色：</span>
              <span className="px-2 py-0.5 bg-slate-200 text-slate-700 rounded-full font-mono">{thinking.role}</span>
            </div>
          )}

          {thinking.diagnosis && (
            <div>
              <span className="font-bold text-slate-700 flex items-center gap-1 mb-1">
                <Brain size={12} /> 结构化诊断
              </span>
              <pre className="whitespace-pre-wrap font-sans bg-white p-2 rounded border border-slate-200 leading-relaxed text-[11px]">
                {thinking.diagnosis}
              </pre>
            </div>
          )}

          {thinking.tasks && thinking.tasks.length > 0 && (
            <div>
              <span className="font-bold text-slate-700 flex items-center gap-1 mb-1">
                <Sparkles size={12} /> 任务规划
              </span>
              <ul className="list-decimal list-inside space-y-1 bg-white p-2 rounded border border-slate-200 text-[11px]">
                {thinking.tasks.map((t, i) => (
                  <li key={i}>
                    {t.task_desc} <span className="text-slate-400 font-mono ml-1">(Pri: {t.priority})</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}