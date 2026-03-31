import React, { useState, useEffect } from 'react';
// 确保这里的引入路径和你实际的文件名一致
import StudentWorkspace from './components/StudentWorkspace';
import TeacherDashboard from './components/TeacherDashboard';
import LoginRegisterPage from './components/LoginRegisterPage';
import AdminPortal from './components/AdminPortal';
import { GraduationCap, LogOut, User } from 'lucide-react';

function App() {
  // 1. 核心状态：当前登录的用户
  const [currentUser, setCurrentUser] = useState(null);
  const [isChecking, setIsChecking] = useState(true);

  // 2. 页面加载时，检查本地缓存是否已经登录过
  useEffect(() => {
    const savedUser = localStorage.getItem('teaching_agent_user');
    if (savedUser) {
      setCurrentUser(JSON.parse(savedUser));
    }
    setIsChecking(false);
  }, []);

  // 3. 处理登录成功
  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    localStorage.setItem('teaching_agent_user', JSON.stringify(user));
  };

  // 4. 处理退出登录
  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('teaching_agent_user');
  };

  // 如果还在检查缓存，防止页面闪烁
  if (isChecking) return <div className="min-h-screen bg-slate-50 flex items-center justify-center">加载中...</div>;

  // ================= 没登录：展示登录注册页 =================
  if (!currentUser) {
    return <LoginRegisterPage onLoginSuccess={handleLoginSuccess} />;
  }

  // ================= 登录成功：展示主界面 =================
  return (
    <div className="min-h-screen flex flex-col font-sans">
      {/* 顶部导航栏 */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 text-brand-600">
            <GraduationCap size={28} />
            <span className="text-xl font-extrabold tracking-tight">Teaching Agent UI</span>
          </div>
          
          {/* 右上角：原来是切换按钮，现在变成了【当前用户信息 + 退出按钮】 */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 bg-slate-100 px-3 py-1.5 rounded-full text-sm font-medium text-slate-600">
              <User size={16} className="text-brand-500" />
              <span>{currentUser.real_name}</span>
              {/* 根据角色显示不同的颜色标签 */}
              <span className={`px-1.5 py-0.5 rounded text-[10px] uppercase font-bold ${
                currentUser.role === 'teacher' ? 'bg-orange-200 text-orange-800' : 'bg-blue-200 text-blue-800'
              }`}>
                {currentUser.role === 'teacher' ? '导师' : '学生'}
              </span>
            </div>
            
            <button
              onClick={handleLogout}
              className="text-slate-400 hover:text-red-500 transition-colors flex items-center gap-1 text-sm font-bold"
            >
              <LogOut size={16} /> 退出
            </button>
          </div>
        </div>
      </header>

      {/* 主体内容区：根据角色自动路由 */}
      <main className="flex-1 bg-slate-50/50">
        <div className="max-w-7xl mx-auto h-full">
          {/* 把 currentUser 当作 props 传给子组件，这样里面就能用到真实的 user ID 了 */}
          {currentUser.role === 'student' && <StudentWorkspace currentUser={currentUser} />}
          {currentUser.role === 'teacher' && <TeacherDashboard currentUser={currentUser} />}
          {currentUser.role === 'admin' && <AdminPortal />}
        </div>
      </main>
    </div>
  );
}

export default App;