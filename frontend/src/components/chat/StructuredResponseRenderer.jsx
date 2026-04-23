// // import React from 'react';
// // import { ShieldAlert, Trophy, GaugeCircle, Target } from 'lucide-react';
// // import ReactMarkdown from 'react-markdown';
// // import remarkGfm from 'remark-gfm';

// // function MarkdownBlock({ children }) {
// //   return (
// //     <div className="text-sm text-slate-700 leading-relaxed font-sans">
// //       <ReactMarkdown
// //         remarkPlugins={[remarkGfm]}
// //         components={{
// //           h2: ({ node, ...props }) => <h2 className="text-lg font-bold text-slate-800 mt-6 mb-3" {...props} />,
// //           h3: ({ node, ...props }) => <h3 className="text-base font-bold text-brand-700 mt-5 mb-2 flex items-center gap-1" {...props} />,
// //           h4: ({ node, ...props }) => <h4 className="text-sm font-bold text-slate-800 mt-4 mb-2" {...props} />,
// //           strong: ({ node, ...props }) => <strong className="font-bold text-brand-600 bg-brand-50 px-1 rounded" {...props} />,
// //           blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-brand-400 pl-3 py-1 my-3 text-slate-500 bg-slate-50 rounded-r-lg italic" {...props} />,
// //           ul: ({ node, ...props }) => <ul className="list-disc pl-5 space-y-1.5 my-3" {...props} />,
// //           ol: ({ node, ...props }) => <ol className="list-decimal pl-5 space-y-1.5 my-3" {...props} />,
// //           p: ({ node, ...props }) => <p className="mb-3 last:mb-0" {...props} />,
// //           table: ({ node, ...props }) => (
// //             <div className="overflow-x-auto my-4 border border-slate-200 rounded-lg shadow-sm">
// //               <table className="min-w-full divide-y divide-slate-200 text-left text-sm" {...props} />
// //             </div>
// //           ),
// //           thead: ({ node, ...props }) => <thead className="bg-slate-50" {...props} />,
// //           th: ({ node, ...props }) => <th className="px-4 py-3 font-bold text-slate-700 uppercase tracking-wider" {...props} />,
// //           tbody: ({ node, ...props }) => <tbody className="bg-white divide-y divide-slate-100" {...props} />,
// //           td: ({ node, ...props }) => <td className="px-4 py-3 text-slate-600 align-top" {...props} />,
// //           tr: ({ node, ...props }) => <tr className="hover:bg-slate-50 transition-colors" {...props} />,
// //         }}
// //       >
// //         {children || ''}
// //       </ReactMarkdown>
// //     </div>
// //   );
// // }

// // export default function StructuredResponseRenderer({ mode, content }) {
// //   if (!content) return null;

// //   if (mode === 'learning' || mode === 'student_tutor' || mode === 'project') {
// //     return (
// //       <div className="space-y-4">
// //         {content.is_refused && (
// //           <div className="bg-red-50 border border-red-200 rounded-xl p-4 shadow-sm relative overflow-hidden mb-4">
// //             <div className="absolute top-0 left-0 w-1 h-full bg-red-500"></div>
// //             <h4 className="text-red-800 font-bold mb-2 flex items-center gap-2">
// //               <ShieldAlert size={18} /> 触发教学安全护栏
// //             </h4>
// //             <p className="text-red-700 text-sm">
// //               检测到直接获取成品方案的请求。为保证项目质量与思考深度，系统已拒绝代写。请参考下方教练给出的破局思路自行推演：
// //             </p>
// //           </div>
// //         )}

// //         <MarkdownBlock>{content.reply}</MarkdownBlock>
// //       </div>
// //     );
// //   }

// //   if (mode === 'competition') {
// //     const meta = content.competition_meta || {};
// //     const summary = content.score_summary || {};
// //     const weakItems = summary.weakest_dimensions || [];

// //     return (
// //       <div className="space-y-4">
// //         {content.is_refused && (
// //           <div className="bg-red-50 border border-red-200 rounded-xl p-4 shadow-sm relative overflow-hidden mb-4">
// //             <div className="absolute top-0 left-0 w-1 h-full bg-red-500"></div>
// //             <h4 className="text-red-800 font-bold mb-2 flex items-center gap-2">
// //               <ShieldAlert size={18} /> 触发教学安全护栏
// //             </h4>
// //             <p className="text-red-700 text-sm">当前请求触发了教学安全护栏，请结合下方竞赛辅导建议继续完善。</p>
// //           </div>
// //         )}

// //         <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
// //           <div className="bg-purple-50 border border-purple-100 rounded-xl p-4">
// //             <div className="text-xs text-purple-600 mb-1 flex items-center gap-2">
// //               <Trophy size={14} /> 当前赛事模板
// //             </div>
// //             <div className="font-bold text-purple-800">{meta.template_name || '竞赛模式'}</div>
// //             <div className="text-xs text-purple-600 mt-1">{meta.matched_alias ? `识别依据：${meta.matched_alias}` : '根据对话内容自动识别'}</div>
// //           </div>

// //           <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
// //             <div className="text-xs text-blue-600 mb-1 flex items-center gap-2">
// //               <GaugeCircle size={14} /> 综合预估得分
// //             </div>
// //             <div className="font-bold text-blue-800">{summary.weighted_score_text || '—'}</div>
// //             <div className="text-xs text-blue-600 mt-1">平均单项分：{summary.average_score ?? '—'}</div>
// //           </div>

// //           <div className="bg-amber-50 border border-amber-100 rounded-xl p-4">
// //             <div className="text-xs text-amber-600 mb-1 flex items-center gap-2">
// //               <Target size={14} /> 高优先级短板
// //             </div>
// //             <div className="font-bold text-amber-800 truncate">
// //               {weakItems.length > 0 ? weakItems.map((item) => item.dimension_name).join(' / ') : '待分析'}
// //             </div>
// //             <div className="text-xs text-amber-600 mt-1">高权重低分项优先修复</div>
// //           </div>
// //         </div>

// //         <MarkdownBlock>{content.reply}</MarkdownBlock>
// //       </div>
// //     );
// //   }

// //   return <MarkdownBlock>{content.reply || ''}</MarkdownBlock>;
// // }




// import React from 'react';
// import { ShieldAlert, Trophy, GaugeCircle, Target, FileText } from 'lucide-react';
// import ReactMarkdown from 'react-markdown';
// import remarkGfm from 'remark-gfm';

// function MarkdownBlock({ children }) {
//   return (
//     <div className="text-sm text-slate-700 leading-relaxed font-sans">
//       <ReactMarkdown
//         remarkPlugins={[remarkGfm]}
//         components={{
//           h2: ({ node, ...props }) => <h2 className="text-lg font-bold text-slate-800 mt-6 mb-3" {...props} />,
//           h3: ({ node, ...props }) => <h3 className="text-base font-bold text-brand-700 mt-5 mb-2 flex items-center gap-1" {...props} />,
//           h4: ({ node, ...props }) => <h4 className="text-sm font-bold text-slate-800 mt-4 mb-2" {...props} />,
//           strong: ({ node, ...props }) => <strong className="font-bold text-brand-600 bg-brand-50 px-1 rounded" {...props} />,
//           blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-brand-400 pl-3 py-1 my-3 text-slate-500 bg-slate-50 rounded-r-lg italic" {...props} />,
//           ul: ({ node, ...props }) => <ul className="list-disc pl-5 space-y-1.5 my-3" {...props} />,
//           ol: ({ node, ...props }) => <ol className="list-decimal pl-5 space-y-1.5 my-3" {...props} />,
//           p: ({ node, ...props }) => <p className="mb-3 last:mb-0" {...props} />,
//           table: ({ node, ...props }) => (
//             <div className="overflow-x-auto my-4 border border-slate-200 rounded-lg shadow-sm">
//               <table className="min-w-full divide-y divide-slate-200 text-left text-sm" {...props} />
//             </div>
//           ),
//           thead: ({ node, ...props }) => <thead className="bg-slate-50" {...props} />,
//           th: ({ node, ...props }) => <th className="px-4 py-3 font-bold text-slate-700 uppercase tracking-wider" {...props} />,
//           tbody: ({ node, ...props }) => <tbody className="bg-white divide-y divide-slate-100" {...props} />,
//           td: ({ node, ...props }) => <td className="px-4 py-3 text-slate-600 align-top" {...props} />,
//           tr: ({ node, ...props }) => <tr className="hover:bg-slate-50 transition-colors" {...props} />,
//         }}
//       >
//         {children || ''}
//       </ReactMarkdown>
//     </div>
//   );
// }

// export default function StructuredResponseRenderer({ mode, content }) {
//   if (!content) return null;

//   if (mode === 'learning' || mode === 'student_tutor' || mode === 'project') {
//     return (
//       <div className="space-y-4">
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

//         <MarkdownBlock>{content.reply}</MarkdownBlock>
//       </div>
//     );
//   }



//   if (mode === 'project_stage_draft' || content?.stage_draft) {
//     const artifact = content?.stage_draft || content || {};
//     const highlights = Array.isArray(artifact.revision_highlights) ? artifact.revision_highlights : [];

//     return (
//       <div className="space-y-4">
//         <div className="rounded-2xl border border-amber-200 bg-amber-50/60 p-4">
//           <div className="flex items-start gap-3">
//             <div className="w-10 h-10 shrink-0 rounded-xl bg-white border border-amber-200 text-amber-600 flex items-center justify-center">
//               <FileText size={18} />
//             </div>
//             <div className="min-w-0 flex-1">
//               <div className="text-xs font-bold text-amber-600 mb-1">阶段成果整理</div>
//               <div className="text-base font-bold text-slate-800">{artifact.title || '阶段优化项目书增量稿'}</div>
//               <div className="text-xs text-slate-500 mt-1">{artifact.generation_notice || '本稿仅整理当前阶段已确认内容，请学生自行复核并与原 BP 合并。'}</div>
//             </div>
//           </div>

//           {highlights.length > 0 && (
//             <div className="mt-3 flex flex-wrap gap-2">
//               {highlights.slice(0, 4).map((item, idx) => (
//                 <span key={idx} className="px-2.5 py-1 rounded-full bg-white border border-amber-200 text-[11px] font-semibold text-amber-700">
//                   {item}
//                 </span>
//               ))}
//             </div>
//           )}
//         </div>

//         <MarkdownBlock>{artifact.content || content?.reply || ''}</MarkdownBlock>
//       </div>
//     );
//   }

//   if (mode === 'competition') {
//     const meta = content.competition_meta || {};
//     const summary = content.score_summary || {};
//     const weakItems = summary.weakest_dimensions || [];

//     return (
//       <div className="space-y-4">
//         {content.is_refused && (
//           <div className="bg-red-50 border border-red-200 rounded-xl p-4 shadow-sm relative overflow-hidden mb-4">
//             <div className="absolute top-0 left-0 w-1 h-full bg-red-500"></div>
//             <h4 className="text-red-800 font-bold mb-2 flex items-center gap-2">
//               <ShieldAlert size={18} /> 触发教学安全护栏
//             </h4>
//             <p className="text-red-700 text-sm">当前请求触发了教学安全护栏，请结合下方竞赛辅导建议继续完善。</p>
//           </div>
//         )}

//         <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
//           <div className="bg-purple-50 border border-purple-100 rounded-xl p-4">
//             <div className="text-xs text-purple-600 mb-1 flex items-center gap-2">
//               <Trophy size={14} /> 当前赛事模板
//             </div>
//             <div className="font-bold text-purple-800">{meta.template_name || '竞赛模式'}</div>
//             <div className="text-xs text-purple-600 mt-1">{meta.matched_alias ? `识别依据：${meta.matched_alias}` : '根据对话内容自动识别'}</div>
//           </div>

//           <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
//             <div className="text-xs text-blue-600 mb-1 flex items-center gap-2">
//               <GaugeCircle size={14} /> 综合预估得分
//             </div>
//             <div className="font-bold text-blue-800">{summary.weighted_score_text || '—'}</div>
//             <div className="text-xs text-blue-600 mt-1">平均单项分：{summary.average_score ?? '—'}</div>
//           </div>

//           <div className="bg-amber-50 border border-amber-100 rounded-xl p-4">
//             <div className="text-xs text-amber-600 mb-1 flex items-center gap-2">
//               <Target size={14} /> 高优先级短板
//             </div>
//             <div className="font-bold text-amber-800 truncate">
//               {weakItems.length > 0 ? weakItems.map((item) => item.dimension_name).join(' / ') : '待分析'}
//             </div>
//             <div className="text-xs text-amber-600 mt-1">高权重低分项优先修复</div>
//           </div>
//         </div>

//         <MarkdownBlock>{content.reply}</MarkdownBlock>
//       </div>
//     );
//   }

//   return <MarkdownBlock>{content.reply || ''}</MarkdownBlock>;
// }





import React from 'react';
import { ShieldAlert, Trophy, GaugeCircle, Target, FileText, AlertTriangle } from 'lucide-react';
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

function judgeToneClasses(level = '') {
  const value = String(level || '');
  if (value.includes('高压') || value.includes('极限')) {
    return 'bg-red-50 border-red-200 text-red-700';
  }
  if (value.includes('证据') || value.includes('逻辑') || value.includes('差异')) {
    return 'bg-amber-50 border-amber-200 text-amber-700';
  }
  return 'bg-slate-50 border-slate-200 text-slate-700';
}

function JudgeQuestionPreview({ judgeQuestions = [] }) {
  if (!Array.isArray(judgeQuestions) || judgeQuestions.length === 0) return null;

  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50/70 p-4">
      <div className="flex items-center gap-2 text-sm font-bold text-slate-800 mb-3">
        <AlertTriangle size={16} className="text-amber-600" /> 模拟评委席高压追问
      </div>
      <div className="space-y-3">
        {judgeQuestions.slice(0, 3).map((item, idx) => (
          <div key={`${item.question || 'judge'}-${idx}`} className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="px-2.5 py-1 rounded-full bg-purple-50 border border-purple-100 text-[11px] font-semibold text-purple-700">
                {item.expert_role || '评委'}
              </span>
              <span className="px-2.5 py-1 rounded-full bg-blue-50 border border-blue-100 text-[11px] font-semibold text-blue-700">
                {item.target_dimension_name || '关键维度'}
              </span>
              <span className={`px-2.5 py-1 rounded-full border text-[11px] font-semibold ${judgeToneClasses(item.pressure_level)}`}>
                {item.pressure_level || '高压追问'}
              </span>
            </div>
            <div className="text-sm font-semibold text-slate-800 leading-relaxed">{item.question || '请补齐该维度的关键证据。'}</div>
            <div className="mt-2 text-xs text-slate-500">盯住薄弱点：{item.attack_point || '该维度核心论证仍需补强。'}</div>
          </div>
        ))}
      </div>
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

  if (mode === 'project_stage_draft' || content?.stage_draft) {
    const artifact = content?.stage_draft || content || {};
    const highlights = Array.isArray(artifact.revision_highlights) ? artifact.revision_highlights : [];

    return (
      <div className="space-y-4">
        <div className="rounded-2xl border border-amber-200 bg-amber-50/60 p-4">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 shrink-0 rounded-xl bg-white border border-amber-200 text-amber-600 flex items-center justify-center">
              <FileText size={18} />
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-xs font-bold text-amber-600 mb-1">阶段成果整理</div>
              <div className="text-base font-bold text-slate-800">{artifact.title || '阶段优化项目书增量稿'}</div>
              <div className="text-xs text-slate-500 mt-1">{artifact.generation_notice || '本稿仅整理当前阶段已确认内容，请学生自行复核并与原 BP 合并。'}</div>
            </div>
          </div>

          {highlights.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {highlights.slice(0, 4).map((item, idx) => (
                <span key={idx} className="px-2.5 py-1 rounded-full bg-white border border-amber-200 text-[11px] font-semibold text-amber-700">
                  {item}
                </span>
              ))}
            </div>
          )}
        </div>

        <MarkdownBlock>{artifact.content || content?.reply || ''}</MarkdownBlock>
      </div>
    );
  }

  if (mode === 'competition') {
    const meta = content.competition_meta || {};
    const summary = content.score_summary || {};
    const weakItems = summary.weakest_dimensions || [];
    const judgeQuestions = content.judge_questions || [];

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

        <JudgeQuestionPreview judgeQuestions={judgeQuestions} />

        <MarkdownBlock>{content.reply}</MarkdownBlock>
      </div>
    );
  }

  return <MarkdownBlock>{content.reply || ''}</MarkdownBlock>;
}
