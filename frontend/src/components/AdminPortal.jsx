import React, { useState, useEffect } from 'react';
import { Shield, Users, Activity, Trash2, KeyRound, CheckCircle, AlertTriangle, UserCog, UploadCloud } from 'lucide-react';
import { fetchAdminUsers, deleteUser, resetUserPassword, updateUserRole, fetchAdminStats, batchRegisterUsers } from '../api';

export default function AdminPortal() {
  const [activeTab, setActiveTab] = useState('users');
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  
  // 批量注册相关的状态
  const [batchInput, setBatchInput] = useState('');
  
  // 获取初始数据
  useEffect(() => {
    loadUsers();
    loadStats();
  }, []);

  const loadUsers = async () => {
    try {
      const data = await fetchAdminUsers();
      setUsers(data);
    } catch (e) {
      console.error("加载用户失败", e);
    }
  };

  const loadStats = async () => {
    try {
      const data = await fetchAdminStats();
      setStats(data);
    } catch (e) {
      console.error("加载统计失败", e);
    }
  };

  const handleDelete = async (userId) => {
    if (!window.confirm("确定要永久删除该账号及关联数据吗？")) return;
    try {
      await deleteUser(userId);
      loadUsers();
      loadStats();
    } catch (e) {
      alert("删除失败");
    }
  };

  const handleResetPassword = async (userId) => {
    const newPwd = window.prompt("请输入新的初始密码 (至少6位):", "123456");
    if (!newPwd) return;
    try {
      await resetUserPassword(userId, newPwd);
      alert("密码重置成功！");
    } catch (e) {
      alert("密码重置失败");
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      await updateUserRole(userId, newRole);
      loadUsers();
    } catch (e) {
      alert("角色修改失败");
    }
  };

  const handleBatchRegister = async () => {
    if (!batchInput.trim()) return;
    try {
      // 简单解析 CSV 格式: username,password,real_name,class_name,role
      const lines = batchInput.split('\n').filter(line => line.trim() !== '');
      const parsedUsers = lines.map(line => {
        const [username, password, real_name, class_name, role] = line.split(',');
        return { 
          username: username.trim(), 
          password: password.trim(), 
          real_name: real_name.trim(), 
          class_name: class_name ? class_name.trim() : null, 
          role: role ? role.trim() : 'student' 
        };
      });
      
      const res = await batchRegisterUsers(parsedUsers);
      alert(res.message);
      setBatchInput('');
      loadUsers();
      loadStats();
    } catch (e) {
      alert("批量注册失败，请检查格式是否为: 账号,密码,姓名,班级,角色");
    }
  };

  return (
    <div className="flex h-[calc(100vh-64px)] bg-slate-50 overflow-hidden w-full">
      {/* 侧边栏 */}
      <div className="w-64 bg-slate-900 flex flex-col shrink-0 z-20 shadow-xl">
        <div className="p-6 border-b border-slate-800">
          <h2 className="text-white font-bold flex items-center gap-2">
            <Shield size={20} className="text-red-400" />
            教务管理系统
          </h2>
          <p className="text-slate-400 text-xs mt-1">全局数据与权限中心</p>
        </div>
        <div className="flex flex-col p-4 gap-2">
          <button onClick={() => setActiveTab('users')} className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-medium ${activeTab === 'users' ? 'bg-red-600 text-white shadow-md' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}>
            <UserCog size={18} /> 用户与权限隔离
          </button>
          <button onClick={() => setActiveTab('stats')} className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-medium ${activeTab === 'stats' ? 'bg-red-600 text-white shadow-md' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}>
            <Activity size={18} /> 全局数据监控
          </button>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="flex-1 overflow-y-auto p-8">
        
        {/* ================= 用户与权限隔离 Tab ================= */}
        {activeTab === 'users' && (
          <div className="space-y-6">
            <div className="flex justify-between items-end mb-6">
              <div>
                <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
                  <Users size={24} className="text-red-500"/> 用户与角色分配
                </h1>
                <p className="text-slate-500 mt-1">负责全校账号增删改查及系统角色控制</p>
              </div>
            </div>

            {/* 批量注册区块 */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-3">
                <UploadCloud size={18} className="text-slate-500"/> 批量注册账号
              </h3>
              <p className="text-xs text-slate-500 mb-2">每行一条数据，格式：<code className="bg-slate-100 px-1 rounded">账号,密码,真实姓名,班级(选填),角色(student/teacher/admin)</code></p>
              <textarea 
                value={batchInput}
                onChange={e => setBatchInput(e.target.value)}
                placeholder="例如：&#10;stu001,123456,张三,1班,student&#10;teach01,password,李四,,teacher"
                className="w-full border border-slate-300 rounded-lg p-3 text-sm focus:ring-2 focus:ring-red-500 outline-none mb-3 bg-slate-50 font-mono"
                rows={3}
              />
              <button onClick={handleBatchRegister} disabled={!batchInput} className="bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2">
                执行批量建档
              </button>
            </div>

            {/* 用户列表 */}
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-600">
                  <tr>
                    <th className="p-4 font-bold">真实姓名</th>
                    <th className="p-4 font-bold">登录账号</th>
                    <th className="p-4 font-bold">班级</th>
                    <th className="p-4 font-bold">当前角色</th>
                    <th className="p-4 font-bold text-right">安全操作</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {users.map(u => (
                    <tr key={u.id} className="hover:bg-slate-50">
                      <td className="p-4 font-medium text-slate-800">{u.real_name}</td>
                      <td className="p-4 text-slate-500 font-mono text-xs">{u.username}</td>
                      <td className="p-4 text-slate-600">{u.class_name || '-'}</td>
                      <td className="p-4">
                        <select 
                          value={u.role} 
                          onChange={(e) => handleRoleChange(u.id, e.target.value)}
                          className={`px-2 py-1 rounded text-xs font-bold outline-none border ${
                            u.role === 'admin' ? 'bg-red-100 text-red-700 border-red-200' : 
                            u.role === 'teacher' ? 'bg-orange-100 text-orange-700 border-orange-200' : 
                            'bg-blue-100 text-blue-700 border-blue-200'
                          }`}
                        >
                          <option value="student">Student</option>
                          <option value="teacher">Teacher</option>
                          <option value="admin">Admin (System)</option>
                        </select>
                      </td>
                      <td className="p-4 text-right flex justify-end gap-2">
                        <button onClick={() => handleResetPassword(u.id)} className="text-slate-400 hover:text-brand-600 transition-colors p-1" title="重置密码"><KeyRound size={16} /></button>
                        <button onClick={() => handleDelete(u.id)} className="text-slate-400 hover:text-red-600 transition-colors p-1" title="彻底删除"><Trash2 size={16} /></button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ================= 全局数据监控 Tab ================= */}
        {activeTab === 'stats' && stats && (
          <div className="space-y-6 animate-in fade-in">
            <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2 mb-6">
              <Activity size={24} className="text-red-500"/> 宏观统计与全校健康度看板
            </h1>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm border-t-4 border-t-blue-500">
                <div className="text-slate-500 text-sm font-bold mb-1">注册总人数</div>
                <div className="text-3xl font-extrabold text-slate-800">{stats.total_users}</div>
              </div>
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm border-t-4 border-t-emerald-500">
                <div className="text-slate-500 text-sm font-bold mb-1">平台项目数</div>
                <div className="text-3xl font-extrabold text-slate-800">{stats.total_projects}</div>
              </div>
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm border-t-4 border-t-purple-500">
                <div className="text-slate-500 text-sm font-bold mb-1">累计对话流</div>
                <div className="text-3xl font-extrabold text-slate-800">{stats.total_conversations}</div>
              </div>
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm border-t-4 border-t-red-500">
                <div className="text-slate-500 text-sm font-bold mb-1">全局模型健康度</div>
                <div className="text-3xl font-extrabold text-red-600">{stats.overall_health_score}/100</div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm mt-6">
              <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-4">
                <AlertTriangle size={18} className="text-red-500"/> 全校高频触发 Top 3 业务漏洞
              </h3>
              <div className="space-y-3">
                {stats.top_flaws.map((flaw, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 bg-slate-50 border border-slate-100 rounded-xl">
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-1 rounded text-xs font-bold ${flaw.severity === 'Critical' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'}`}>
                        Top {idx + 1}
                      </span>
                      <span className="font-medium text-slate-700">{flaw.name}</span>
                    </div>
                    <div className="text-sm font-mono font-bold text-slate-500 bg-white px-3 py-1 rounded border border-slate-200">
                      波及率: {flaw.frequency}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}