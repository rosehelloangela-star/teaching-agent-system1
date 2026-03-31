import React, { useState } from 'react';
import { Users, FileCheck, UserCog, LayoutDashboard } from 'lucide-react';
import ClassInsightsView from './ClassInsightsView';
import ProjectAssessmentView from './ProjectAssessmentView';
import StudentProfileView from './StudentProfileView';

export default function TeacherDashboard({ currentUser }) {
  const [activeTab, setActiveTab] = useState('insights');

  return (
    <div className="flex h-[calc(100vh-64px)] bg-slate-50 overflow-hidden">
      {/* 教师端专属左侧导航 */}
      <div className="w-64 bg-slate-900 flex flex-col shrink-0 z-20 shadow-xl">
        <div className="p-6 border-b border-slate-800">
          <h2 className="text-white font-bold flex items-center gap-2">
            <LayoutDashboard size={20} className="text-brand-400" />
            教师管理看板
          </h2>
          <p className="text-slate-400 text-xs mt-1">教学干预与数据分析中心</p>
        </div>
        
        <div className="flex flex-col p-4 gap-2">
          <button 
            onClick={() => setActiveTab('insights')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-medium ${
              activeTab === 'insights' ? 'bg-brand-600 text-white shadow-md' : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <Users size={18} /> 班级学情洞察
          </button>
          
          <button 
            onClick={() => setActiveTab('assessment')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-medium ${
              activeTab === 'assessment' ? 'bg-brand-600 text-white shadow-md' : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <FileCheck size={18} /> 单项目复核批改
          </button>

          <button 
            onClick={() => setActiveTab('profile')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-medium ${
              activeTab === 'profile' ? 'bg-brand-600 text-white shadow-md' : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <UserCog size={18} /> 交互画像与干预
          </button>
        </div>
      </div>

      {/* 右侧内容区 */}
      <div className="flex-1 flex overflow-hidden bg-slate-50">
        {activeTab === 'insights' && <ClassInsightsView currentUser={currentUser} />} {/* <-- 这里加上 currentUser */}
        {activeTab === 'assessment' && <ProjectAssessmentView />}
        {activeTab === 'profile' && <StudentProfileView />}
      </div>
    </div>
  );
}