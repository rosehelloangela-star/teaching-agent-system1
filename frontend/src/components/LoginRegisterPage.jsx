import React, { useState } from 'react';
import { GraduationCap, User, Lock, BookOpen, Users, Loader2 } from 'lucide-react';
import { loginUser, registerUser } from '../api';

export default function LoginRegisterPage({ onLoginSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 表单状态
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [realName, setRealName] = useState('');
  const [className, setClassName] = useState('');
  const [role, setRole] = useState('student'); // 默认注册为学生

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        // 执行登录
        const user = await loginUser(username, password);
        onLoginSuccess(user); // 登录成功，把用户信息传给 App.jsx
      } else {
        // 执行注册
        const userData = { username, password, real_name: realName, class_name: className, role };
        const user = await registerUser(userData);
        onLoginSuccess(user); // 注册成功直接登录
      }
    } catch (err) {
      setError(typeof err === 'string' ? err : '操作失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center items-center p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden">
        {/* 顶部 Logo 区 */}
        <div className="bg-slate-900 p-8 text-center">
          <GraduationCap size={48} className="text-brand-500 mx-auto mb-3" />
          <h1 className="text-2xl font-bold text-white tracking-tight">创新创业教学智能体</h1>
          <p className="text-slate-400 text-sm mt-2">AI-Powered Entrepreneurship Platform</p>
        </div>

        {/* 表单区 */}
        <div className="p-8">
          <h2 className="text-xl font-bold text-slate-800 mb-6 text-center">
            {isLogin ? '欢迎回来，请登录' : '创建你的账号'}
          </h2>

          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-4 text-center border border-red-100">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* 登录账号 & 密码 (共用) */}
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">登录账号</label>
              <div className="relative">
                <User size={16} className="absolute left-3 top-3 text-slate-400" />
                <input 
                  required value={username} onChange={e => setUsername(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-brand-500 outline-none text-sm" 
                  placeholder="请输入英文字母或数字"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">登录密码</label>
              <div className="relative">
                <Lock size={16} className="absolute left-3 top-3 text-slate-400" />
                <input 
                  required type="password" value={password} onChange={e => setPassword(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-brand-500 outline-none text-sm" 
                  placeholder="请输入密码"
                />
              </div>
            </div>

            {/* 注册专属字段 */}
            {!isLogin && (
              <div className="space-y-4 pt-2 border-t border-slate-100 mt-2">
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 text-sm cursor-pointer">
                    <input type="radio" name="role" value="student" checked={role === 'student'} onChange={() => setRole('student')} className="text-brand-600 focus:ring-brand-500" />
                    <span>👨‍🎓 我是学生</span>
                  </label>
                  <label className="flex items-center gap-2 text-sm cursor-pointer">
                    <input type="radio" name="role" value="teacher" checked={role === 'teacher'} onChange={() => setRole('teacher')} className="text-brand-600 focus:ring-brand-500" />
                    <span>👨‍🏫 我是导师</span>
                  </label>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-600 mb-1">真实姓名 (必填)</label>
                  <input required value={realName} onChange={e => setRealName(e.target.value)} className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-brand-500 outline-none text-sm" placeholder="如：张三" />
                </div>

                {role === 'student' && (
                  <div>
                    <label className="block text-xs font-bold text-slate-600 mb-1">所属班级 (学生必填)</label>
                    {/* 将 input 替换为 select 下拉框 */}
                    <select 
                      required 
                      value={className} 
                      onChange={e => setClassName(e.target.value)} 
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-brand-500 outline-none text-sm bg-white" 
                    >
                      <option value="" disabled>请选择班级 (1-10班)</option>
                      {[...Array(10)].map((_, i) => (
                        <option key={i+1} value={`${i+1}班`}>{`${i+1}班`}</option>
                      ))}
                    </select>
                  </div>
                )}
              </div>
            )}

            <button disabled={loading} type="submit" className="w-full bg-brand-600 text-white font-bold py-3 rounded-xl mt-6 hover:bg-brand-700 transition-colors flex justify-center items-center gap-2 disabled:opacity-50">
              {loading && <Loader2 size={18} className="animate-spin" />}
              {isLogin ? '登 录' : '注 册 并 登 录'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button onClick={() => { setIsLogin(!isLogin); setError(''); }} className="text-sm text-brand-600 hover:text-brand-800 font-medium">
              {isLogin ? '没有账号？点击注册新账号 →' : '已有账号？返回登录 ←'}
            </button>
          {/* 👇 === 新增这部分：助教测试提示 === 👇 */}
            <div className="mt-4 pt-4 border-t border-slate-100 text-xs text-slate-400">
              <p>💡 提示：</p>
              <p className="mt-1">
                管理员账号：<code className="bg-slate-100 text-slate-600 px-1 py-0.5 rounded font-mono">admin</code> / 
                密码：<code className="bg-slate-100 text-slate-600 px-1 py-0.5 rounded font-mono">123456</code>
              </p>
            </div>
            {/* 👆 === 新增结束 === 👆 */}
          </div>
          </div>
        </div>
      </div>
  );
}