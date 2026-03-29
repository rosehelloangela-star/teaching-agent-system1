import React, { useState } from 'react';
import { BarChart3, AlertTriangle, Lightbulb, Loader2, Send, Users } from 'lucide-react';
import { runAgent } from '../api';


export default function ClassInsightsView() {
  const [selectedClass, setSelectedClass] = useState('');
  const [insightsLoading, setInsightsLoading] = useState(false);
  const [hasInsights, setHasInsights] = useState(false);
  
  const [interventionLoading, setInterventionLoading] = useState(false);
  const [interventionResult, setInterventionResult] = useState('');

  // 模拟从后端获取汇总数据
  const handleGenerateInsights = () => {
    if (!selectedClass) return;
    setInsightsLoading(true);
    setTimeout(() => {
      setHasInsights(true);
      setInsightsLoading(false);
    }, 1500);
  };

  // 核心：调用 instructor 智能体生成干预方案
  const handleGenerateIntervention = async () => {
    setInterventionLoading(true);
    try {
      const summaryText = "当前班级40%团队缺乏对巨头竞争的防御策略，财务测算掌握率仅20%。请结合共性错误，输出具体的、可落地的下周教学干预方案与课表安排。";
      const data = await runAgent(summaryText, 'instructor', 'class_summary_thread');
      setInterventionResult(data.generated_content.teaching_suggestions || JSON.stringify(data.generated_content));
    } catch (e) {
      setInterventionResult("生成失败，请检查后端服务。");
    } finally {
      setInterventionLoading(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-8">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">📊 班级学情洞察 (Class Insights)</h1>
          <p className="text-slate-500 mt-1">汇总班级项目数据，识别共性短板与高危项目</p>
        </div>
        <div className="flex gap-2">
          <select 
            value={selectedClass} 
            onChange={e => setSelectedClass(e.target.value)}
            className="border border-slate-300 rounded-lg px-4 py-2 bg-white text-sm outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="">-- 选择班级 --</option>
            <option value="class_1">2023级 计算机创新创业班 (导入D001-D004)</option>
          </select>
          <button 
            onClick={handleGenerateInsights}
            disabled={!selectedClass || insightsLoading}
            className="bg-slate-800 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-slate-900 disabled:opacity-50 flex items-center gap-2"
          >
            {insightsLoading && <Loader2 size={16} className="animate-spin" />}
            运行汇总分析
          </button>
        </div>
      </div>

      {hasInsights ? (
        <div className="space-y-6 animate-in fade-in duration-300">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 看板1：知识覆盖率 */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <h3 className="font-bold text-slate-700 flex items-center gap-2 mb-4">
                <BarChart3 size={18} className="text-blue-500"/> Knowledge Coverage Summary
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between text-sm"><span className="text-slate-600">精益创业概念掌握率</span><span className="font-bold text-emerald-600">80%</span></div>
                <div className="w-full bg-slate-100 rounded-full h-2"><div className="bg-emerald-500 h-2 rounded-full" style={{width: '80%'}}></div></div>
                <div className="flex justify-between text-sm mt-2"><span className="text-slate-600">财务测算/单位经济掌握率</span><span className="font-bold text-red-500">20%</span></div>
                <div className="w-full bg-slate-100 rounded-full h-2"><div className="bg-red-400 h-2 rounded-full" style={{width: '20%'}}></div></div>
              </div>
            </div>

            {/* 看板2：共性错误 Top 5 */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <h3 className="font-bold text-slate-700 flex items-center gap-2 mb-4">
                <AlertTriangle size={18} className="text-orange-500"/> Top 5 Common Mistakes
              </h3>
              <ul className="space-y-2 text-sm text-slate-600">
                <li className="flex gap-2 items-start"><span className="bg-orange-100 text-orange-700 px-2 rounded text-xs font-bold">Top 1</span> 40%团队普遍缺乏对巨头竞争的防御策略</li>
                <li className="flex gap-2 items-start"><span className="bg-orange-100 text-orange-700 px-2 rounded text-xs font-bold">Top 2</span> TAM/SOM 口径混淆，大数幻觉严重</li>
                <li className="flex gap-2 items-start"><span className="bg-slate-100 text-slate-600 px-2 rounded text-xs font-bold">Top 3</span> 获客渠道(Channel)与用户画像不匹配</li>
                <li className="flex gap-2 items-start"><span className="bg-slate-100 text-slate-600 px-2 rounded text-xs font-bold">Top 4</span> 缺乏验证支付意愿的真实证据</li>
              </ul>
            </div>

            {/* 看板3：高风险名单 */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <h3 className="font-bold text-slate-700 flex items-center gap-2 mb-4">
                <AlertTriangle size={18} className="text-red-500"/> High-risk Projects List
              </h3>
              <div className="space-y-3">
                <div className="border border-red-100 bg-red-50 p-3 rounded-lg">
                  <div className="flex justify-between mb-1"><span className="font-bold text-sm text-red-900">DroneFarm (D001)</span><span className="text-xs font-bold bg-red-200 text-red-800 px-2 rounded">高风险</span></div>
                  <p className="text-xs text-red-700">原因：单位经济严重不成立，CAC估算存在致命缺陷。</p>
                </div>
                <div className="border border-orange-100 bg-orange-50 p-3 rounded-lg">
                  <div className="flex justify-between mb-1"><span className="font-bold text-sm text-orange-900">OrientBox (D002)</span><span className="text-xs font-bold bg-orange-200 text-orange-800 px-2 rounded">中风险</span></div>
                  <p className="text-xs text-orange-700">原因：存在合规授权风险及落地资源脱节。</p>
                </div>
              </div>
            </div>
          </div>

          {/* 一键干预方案生成区 */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-slate-800 flex items-center gap-2">
                <Lightbulb size={20} className="text-brand-500"/> Suggested Teaching Interventions (教学干预方案)
              </h3>
              <button 
                onClick={handleGenerateIntervention}
                disabled={interventionLoading}
                className="bg-brand-600 hover:bg-brand-700 text-white px-5 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition-colors disabled:opacity-50"
              >
                {interventionLoading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                一键生成下周教学课表
              </button>
            </div>
            
            <div className="flex-1 bg-slate-50 border border-slate-200 rounded-xl p-5 min-h-[150px]">
              {!interventionResult && !interventionLoading && (
                <div className="h-full flex flex-col items-center justify-center text-slate-400">
                  <Lightbulb size={32} className="opacity-20 mb-2" />
                  <p className="text-sm">点击右上角，AI 将根据共性错误自动编排教学计划</p>
                </div>
              )}
              {interventionResult && (
                <pre className="text-sm text-slate-700 whitespace-pre-wrap font-sans leading-relaxed">
                  {interventionResult}
                </pre>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="h-64 flex flex-col items-center justify-center border-2 border-dashed border-slate-300 rounded-2xl bg-white text-slate-400">
          <Users size={48} className="opacity-20 mb-4" />
          <p>请在右上角选择班级并运行分析，以获取全局洞察。</p>
        </div>
      )}
    </div>
  );
}