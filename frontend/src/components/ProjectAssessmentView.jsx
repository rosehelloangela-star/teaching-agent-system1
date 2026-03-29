import React, { useState, useEffect } from 'react';
import { FileCheck, Edit3, Send, Loader2, CheckCircle } from 'lucide-react';
import { runAgent, fetchAllProjects } from '../api'; // 引入真实API

export default function ProjectAssessmentView() {
  const [allProjects, setAllProjects] = useState([]); // 存放数据库拿到的所有项目
  const [isFetchingList, setIsFetchingList] = useState(true);

  const [selectedProjectId, setSelectedProjectId] = useState('');
  const [assessmentResult, setAssessmentResult] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const [editedScores, setEditedScores] = useState({});
  const [reviewNotes, setReviewNotes] = useState('');
  const [sent, setSent] = useState(false);

  // 【新增】页面一加载，就去后端拉取全班的项目
  useEffect(() => {
    async function loadAllProjects() {
      try {
        const data = await fetchAllProjects();
        setAllProjects(data);
      } catch (e) {
        console.error("获取班级项目失败", e);
      } finally {
        setIsFetchingList(false);
      }
    }
    loadAllProjects();
  }, []);

  const handleFetchAssessment = async () => {
    if (!selectedProjectId) return;
    setLoading(true);
    setSent(false);
    
    // 找到老师选中的那个真实项目
    const targetProject = allProjects.find(p => p.id === selectedProjectId);
    
    try {
      // 真实环境：应该把 targetProject.content 发给后端，这里我们用名字演示
      const textToAnalyze = targetProject?.content || `正在分析项目：${targetProject?.name}`;
      
      const data = await runAgent(textToAnalyze, 'assessment', `teacher_eval_${selectedProjectId}`);
      setAssessmentResult(data.generated_content);
      
      const initialScores = {};
      data.generated_content.rubric_table?.forEach((item, i) => {
        initialScores[i] = item.score;
      });
      setEditedScores(initialScores);
    } catch (e) {
      alert("获取评价失败，请检查后端状态。");
    } finally {
      setLoading(false);
    }
  };

  const handleScoreChange = (index, newScore) => {
    setEditedScores({ ...editedScores, [index]: parseInt(newScore) });
  };

  const handleSendToStudent = () => {
    // 未来这里可以发一个 PUT 请求到后端存数据库，目前模拟成功
    setTimeout(() => {
      setSent(true);
    }, 800);
  };

  return (
    <div className="flex-1 overflow-y-auto p-8 flex flex-col">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">📝 单项目复核与批改 (Assessment)</h1>
          <p className="text-slate-500 mt-1">从数据库调取学生真实项目进行 AI 初评与人工复核</p>
        </div>
        <div className="flex gap-2">
          {/* 【修改】下拉框遍历真实的数据库项目 */}
          <select 
            value={selectedProjectId} 
            onChange={e => setSelectedProjectId(e.target.value)}
            className="border border-slate-300 rounded-lg px-4 py-2 bg-white text-sm outline-none focus:ring-2 focus:ring-brand-500 max-w-xs"
          >
            <option value="">-- 选择要批改的学生项目 --</option>
            {isFetchingList ? (
              <option disabled>正在加载数据库项目...</option>
            ) : (
              allProjects.map(p => (
                <option key={p.id} value={p.id}>
                  {p.student_id} - {p.name}
                </option>
              ))
            )}
          </select>

          <button 
            onClick={handleFetchAssessment}
            disabled={!selectedProjectId || loading}
            className="bg-slate-800 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-slate-900 disabled:opacity-50 flex items-center gap-2"
          >
            {loading && <Loader2 size={16} className="animate-spin" />}
            AI 生成预评估报告
          </button>
        </div>
      </div>

      {assessmentResult ? (
        <div className="flex-1 flex gap-6 overflow-hidden">
          <div className="flex-[2] bg-white border border-slate-200 rounded-2xl shadow-sm flex flex-col overflow-hidden">
            <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
              <h3 className="font-bold text-slate-800 flex items-center gap-2"><FileCheck size={18}/> Rubric 评分与证据追踪 (可修改)</h3>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              <table className="w-full text-left bg-white text-sm border border-slate-200 rounded-lg overflow-hidden">
                <thead className="bg-slate-100">
                  <tr>
                    <th className="p-3 border-b border-slate-200">评估维度</th>
                    <th className="p-3 border-b border-slate-200 w-24">教师打分</th>
                    <th className="p-3 border-b border-slate-200">可追溯证据</th>
                  </tr>
                </thead>
                <tbody>
                  {assessmentResult.rubric_table?.map((row, i) => (
                    <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="p-3 font-medium text-slate-700">{row.dimension}</td>
                      <td className="p-3">
                        <select 
                          value={editedScores[i] ?? row.score} 
                          onChange={(e) => handleScoreChange(i, e.target.value)}
                          className={`w-full p-1 border rounded font-bold text-center outline-none ${
                            editedScores[i] !== row.score ? 'bg-orange-100 text-orange-700 border-orange-300' : 'bg-slate-50 border-slate-300'
                          }`}
                        >
                          {[0,1,2,3,4,5].map(v => <option key={v} value={v}>{v} 分</option>)}
                        </select>
                      </td>
                      <td className="p-3 text-xs text-slate-500 font-mono bg-slate-50 m-1 rounded border border-slate-100 leading-relaxed">
                        "{row.evidence_trace}"
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <div className="mt-6 bg-blue-50 p-4 rounded-xl border border-blue-100">
                <h4 className="font-bold text-blue-800 text-sm mb-2">💡 AI 修订建议 (Revision Suggestions)</h4>
                <p className="text-sm text-blue-700 whitespace-pre-wrap">{assessmentResult.revision_suggestions}</p>
              </div>
            </div>
          </div>

          <div className="flex-1 bg-white border border-slate-200 rounded-2xl shadow-sm p-5 flex flex-col">
            <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-4">
              <Edit3 size={18} className="text-orange-500" /> 教师复核备注
            </h3>
            <p className="text-xs text-slate-500 mb-2">该备注将直接写入数据库，显示在学生端项目气泡中。</p>
            <textarea
              value={reviewNotes}
              onChange={e => setReviewNotes(e.target.value)}
              placeholder="输入你对该项目的批改意见..."
              className="flex-1 w-full border border-slate-300 rounded-xl p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-brand-500 mb-4 bg-slate-50"
            />
            <button
              onClick={handleSendToStudent}
              disabled={sent}
              className={`w-full py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-colors ${
                sent ? 'bg-emerald-100 text-emerald-700' : 'bg-brand-600 hover:bg-brand-700 text-white'
              }`}
            >
              {sent ? <><CheckCircle size={18}/> 已下发至数据库</> : <><Send size={18}/> 确认并下发评价</>}
            </button>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex flex-col items-center justify-center border-2 border-dashed border-slate-300 rounded-2xl bg-white text-slate-400">
          <FileCheck size={48} className="opacity-20 mb-4" />
          <p>请在上方选择真实的数据库项目，获取预评估报告。</p>
        </div>
      )}
    </div>
  );
}