// import React from 'react';
// import { ShieldAlert } from 'lucide-react';
// import ReactMarkdown from 'react-markdown';
// import remarkGfm from 'remark-gfm'; // 【新增】引入 GFM 插件支持表格

// export default function StructuredResponseRenderer({ mode, content }) {
//   if (!content) return null;

//   // 【学习模式 和 项目模式：使用 ReactMarkdown 渲染精美排版】
//   if (mode === 'learning' || mode === 'student_tutor' || mode === 'project') {
//     return (
//       <div className="space-y-4">
//         {/* 触发护栏时的红色警告框 */}
//         {content.is_refused && (
//           <div className="bg-red-50 border border-red-200 rounded-xl p-4 shadow-sm relative overflow-hidden mb-4">
//             <div className="absolute top-0 left-0 w-1 h-full bg-red-500"></div>
//             <h4 className="text-red-800 font-bold mb-2 flex items-center gap-2">
//               <ShieldAlert size={18} /> 触发教学安全护栏
//             </h4>
//             <p className="text-red-700 text-sm">
//               检测到直接获取成品方案的请求。为保证项目质量与思考深度，系统已拒绝代写。请参考下方教练给出的破局思路自行推演：
//             </p>
//           </div>
//         )}

//         {/* 核心改变：Markdown 富文本渲染，加入 remarkGfm 和 表格样式 */}
//         <div className="text-sm text-slate-700 leading-relaxed font-sans">
//           <ReactMarkdown
//             remarkPlugins={[remarkGfm]} // 【新增】启用表格等 GFM 语法
//             components={{
//               h3: ({node, ...props}) => <h3 className="text-base font-bold text-brand-700 mt-5 mb-2 flex items-center gap-1" {...props} />,
//               h4: ({node, ...props}) => <h4 className="text-sm font-bold text-slate-800 mt-4 mb-2" {...props} />,
//               strong: ({node, ...props}) => <strong className="font-bold text-brand-600 bg-brand-50 px-1 rounded" {...props} />,
//               blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-brand-400 pl-3 py-1 my-3 text-slate-500 bg-slate-50 rounded-r-lg italic" {...props} />,
//               ul: ({node, ...props}) => <ul className="list-disc pl-5 space-y-1.5 my-3" {...props} />,
//               ol: ({node, ...props}) => <ol className="list-decimal pl-5 space-y-1.5 my-3" {...props} />,
//               p: ({node, ...props}) => <p className="mb-3 last:mb-0" {...props} />,
              
//               // 【新增】为 Markdown 表格定制的精美 Tailwind 样式
//               table: ({node, ...props}) => (
//                 <div className="overflow-x-auto my-4 border border-slate-200 rounded-lg shadow-sm">
//                   <table className="min-w-full divide-y divide-slate-200 text-left text-sm" {...props} />
//                 </div>
//               ),
//               thead: ({node, ...props}) => <thead className="bg-slate-50" {...props} />,
//               th: ({node, ...props}) => <th className="px-4 py-3 font-bold text-slate-700 uppercase tracking-wider" {...props} />,
//               tbody: ({node, ...props}) => <tbody className="bg-white divide-y divide-slate-100" {...props} />,
//               td: ({node, ...props}) => <td className="px-4 py-3 text-slate-600 align-top" {...props} />,
//               tr: ({node, ...props}) => <tr className="hover:bg-slate-50 transition-colors" {...props} />
//             }}
//           >
//             {content.reply}
//           </ReactMarkdown>
//         </div>
//       </div>
//     );
//   }

//   // --- 竞赛模式 (保持原样) ---
//   if (mode === 'competition') {
//     return (
//       <div className="space-y-4">
//         <div>
//           <h4 className="font-bold text-slate-800 text-sm mb-1">📊 Rubric 对标评分</h4>
//           <p className="text-sm text-slate-600 whitespace-pre-wrap">{content.rubric_scores}</p>
//         </div>
//         <div className="bg-red-50 p-3 rounded-lg border border-red-100">
//           <h4 className="font-bold text-red-800 text-sm mb-1">📉 扣分点证据追踪</h4>
//           <p className="text-sm text-red-700 whitespace-pre-wrap">{content.deduction_evidence}</p>
//         </div>
//         <div>
//           <h4 className="font-bold text-slate-800 text-sm mb-2">🚀 高性价比提分策略 (Top Tasks)</h4>
//           <div className="space-y-2">
//             {content.top_tasks?.map((task, i) => (
//               <div key={i} className="bg-slate-50 border border-slate-200 p-3 rounded-lg">
//                 <p className="font-bold text-sm text-purple-700 mb-1">{task.task_desc}</p>
//                 <p className="text-xs text-slate-500 mb-2">
//                   ⏱ {task.timeframe} | 💡 {task.roi_reason}
//                 </p>
//                 <div className="bg-white p-2 rounded border border-slate-100 text-xs text-slate-600">
//                   {task.template_example}
//                 </div>
//               </div>
//             ))}
//           </div>
//         </div>
//       </div>
//     );
//   }

//   return <pre className="text-xs text-slate-600 whitespace-pre-wrap">{JSON.stringify(content, null, 2)}</pre>;
// }


import React from 'react';
import { ShieldAlert, Trophy, GaugeCircle, Target } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

function MarkdownBlock({ children }) {
  return (
    <div className="text-sm text-slate-700 leading-relaxed font-sans">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h2: ({ node, ...props }) => <h2 className="text-lg font-bold text-slate-800 mt-6 mb-3" {...props} />,
          h3: ({ node, ...props }) => <h3 className="text-base font-bold text-brand-700 mt-5 mb-2 flex items-center gap-1" {...props} />,
          h4: ({ node, ...props }) => <h4 className="text-sm font-bold text-slate-800 mt-4 mb-2" {...props} />,
          strong: ({ node, ...props }) => <strong className="font-bold text-brand-600 bg-brand-50 px-1 rounded" {...props} />,
          blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-brand-400 pl-3 py-1 my-3 text-slate-500 bg-slate-50 rounded-r-lg italic" {...props} />,
          ul: ({ node, ...props }) => <ul className="list-disc pl-5 space-y-1.5 my-3" {...props} />,
          ol: ({ node, ...props }) => <ol className="list-decimal pl-5 space-y-1.5 my-3" {...props} />,
          p: ({ node, ...props }) => <p className="mb-3 last:mb-0" {...props} />,
          table: ({ node, ...props }) => (
            <div className="overflow-x-auto my-4 border border-slate-200 rounded-lg shadow-sm">
              <table className="min-w-full divide-y divide-slate-200 text-left text-sm" {...props} />
            </div>
          ),
          thead: ({ node, ...props }) => <thead className="bg-slate-50" {...props} />,
          th: ({ node, ...props }) => <th className="px-4 py-3 font-bold text-slate-700 uppercase tracking-wider" {...props} />,
          tbody: ({ node, ...props }) => <tbody className="bg-white divide-y divide-slate-100" {...props} />,
          td: ({ node, ...props }) => <td className="px-4 py-3 text-slate-600 align-top" {...props} />,
          tr: ({ node, ...props }) => <tr className="hover:bg-slate-50 transition-colors" {...props} />,
        }}
      >
        {children || ''}
      </ReactMarkdown>
    </div>
  );
}

export default function StructuredResponseRenderer({ mode, content }) {
  if (!content) return null;

  if (mode === 'learning' || mode === 'student_tutor' || mode === 'project') {
    return (
      <div className="space-y-4">
        {content.is_refused && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 shadow-sm relative overflow-hidden mb-4">
            <div className="absolute top-0 left-0 w-1 h-full bg-red-500"></div>
            <h4 className="text-red-800 font-bold mb-2 flex items-center gap-2">
              <ShieldAlert size={18} /> 触发教学安全护栏
            </h4>
            <p className="text-red-700 text-sm">
              检测到直接获取成品方案的请求。为保证项目质量与思考深度，系统已拒绝代写。请参考下方教练给出的破局思路自行推演：
            </p>
          </div>
        )}

        <MarkdownBlock>{content.reply}</MarkdownBlock>
      </div>
    );
  }

  if (mode === 'competition') {
    const meta = content.competition_meta || {};
    const summary = content.score_summary || {};
    const weakItems = summary.weakest_dimensions || [];

    return (
      <div className="space-y-4">
        {content.is_refused && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 shadow-sm relative overflow-hidden mb-4">
            <div className="absolute top-0 left-0 w-1 h-full bg-red-500"></div>
            <h4 className="text-red-800 font-bold mb-2 flex items-center gap-2">
              <ShieldAlert size={18} /> 触发教学安全护栏
            </h4>
            <p className="text-red-700 text-sm">当前请求触发了教学安全护栏，请结合下方竞赛辅导建议继续完善。</p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="bg-purple-50 border border-purple-100 rounded-xl p-4">
            <div className="text-xs text-purple-600 mb-1 flex items-center gap-2">
              <Trophy size={14} /> 当前赛事模板
            </div>
            <div className="font-bold text-purple-800">{meta.template_name || '竞赛模式'}</div>
            <div className="text-xs text-purple-600 mt-1">{meta.matched_alias ? `识别依据：${meta.matched_alias}` : '根据对话内容自动识别'}</div>
          </div>

          <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
            <div className="text-xs text-blue-600 mb-1 flex items-center gap-2">
              <GaugeCircle size={14} /> 综合预估得分
            </div>
            <div className="font-bold text-blue-800">{summary.weighted_score_text || '—'}</div>
            <div className="text-xs text-blue-600 mt-1">平均单项分：{summary.average_score ?? '—'}</div>
          </div>

          <div className="bg-amber-50 border border-amber-100 rounded-xl p-4">
            <div className="text-xs text-amber-600 mb-1 flex items-center gap-2">
              <Target size={14} /> 高优先级短板
            </div>
            <div className="font-bold text-amber-800 truncate">
              {weakItems.length > 0 ? weakItems.map((item) => item.dimension_name).join(' / ') : '待分析'}
            </div>
            <div className="text-xs text-amber-600 mt-1">高权重低分项优先修复</div>
          </div>
        </div>

        <MarkdownBlock>{content.reply}</MarkdownBlock>
      </div>
    );
  }

  return <MarkdownBlock>{content.reply || ''}</MarkdownBlock>;
}
