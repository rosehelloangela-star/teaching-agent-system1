import React, { useState, useEffect, useRef } from 'react';
import { Shield, Users, Activity, Trash2, KeyRound, AlertTriangle, UserCog, UploadCloud, BookOpen, Settings, PlusCircle, FileSpreadsheet, Download } from 'lucide-react';
import { fetchAdminUsers, deleteUser, resetUserPassword, updateUserRole, fetchAdminStats, batchRegisterUsers, assignTeacherClasses, fetchClassStats } from '../api';

export default function AdminPortal() {
  const [activeTab, setActiveTab] = useState('users');
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [classStats, setClassStats] = useState([]);
  
  // 动态班级列表状态
  const [customClasses, setCustomClasses] = useState([]);
  const baseClasses = Array.from({ length: 10 }, (_, i) => `${i + 1}班`);
  // 合并默认1-10班与管理员新建的班级
  const AVAILABLE_CLASSES = [...baseClasses, ...customClasses];

  // 控制分配班级的弹窗
  const [assignModal, setAssignModal] = useState({ isOpen: false, user: null, selectedClasses: [] });
  const fileInputRef = useRef(null);

  useEffect(() => {
    loadUsers();
    loadStats();
    loadClassStats();
  }, []);

  const loadUsers = async () => {
    try { setUsers(await fetchAdminUsers()); } catch (e) { console.error(e); }
  };
  const loadStats = async () => {
    try { setStats(await fetchAdminStats()); } catch (e) { console.error(e); }
  };
  const loadClassStats = async () => {
    try { setClassStats(await fetchClassStats()); } catch (e) { console.error(e); }
  };

  const handleDelete = async (userId) => {
    if (!window.confirm("确定要永久删除该账号吗？")) return;
    try { await deleteUser(userId); loadUsers(); loadStats(); loadClassStats(); } catch (e) { alert("删除失败"); }
  };

  const handleResetPassword = async (userId) => {
    const newPwd = window.prompt("请输入新的初始密码:", "123456");
    if (!newPwd) return;
    try { await resetUserPassword(userId, newPwd); alert("密码重置成功！"); } catch (e) { alert("重置失败"); }
  };

  const handleRoleChange = async (userId, newRole) => {
    try { await updateUserRole(userId, newRole); loadUsers(); } catch (e) { alert("角色修改失败"); }
  };

  // 打开弹窗（兼容斜杠和逗号分隔符）
  const openAssignModal = (user) => {
    const currentClasses = user.class_name ? user.class_name.split(/[,/|]/).map(c => c.trim()).filter(Boolean) : [];
    setAssignModal({ isOpen: true, user: user, selectedClasses: currentClasses });
  };

  // 点击班级时触发：根据角色决定单选还是多选
  const toggleClassSelection = (className) => {
    setAssignModal(prev => {
      const isStudent = prev.user?.role === 'student';
      
      if (isStudent) {
        // 学生：单选逻辑（直接替换选中的班级，或者再次点击取消）
        const isSelected = prev.selectedClasses.includes(className);
        return { ...prev, selectedClasses: isSelected ? [] : [className] };
      } else {
        // 导师：多选逻辑
        const isSelected = prev.selectedClasses.includes(className);
        const newSelection = isSelected 
          ? prev.selectedClasses.filter(c => c !== className) // 取消勾选
          : [...prev.selectedClasses, className]; // 增加勾选
        return { ...prev, selectedClasses: newSelection };
      }
    });
  };

  // 提交班级分配（统一用逗号存入数据库）
  const submitClassAssignment = async () => {
    try {
      const classesString = assignModal.selectedClasses.join(',');
      await assignTeacherClasses(assignModal.user.id, classesString);
      setAssignModal({ isOpen: false, user: null, selectedClasses: [] });
      loadUsers(); // 刷新列表
    } catch (e) {
      alert("分配班级失败");
    }
  };

  // 新建班级逻辑
  const handleCreateClass = () => {
    const newClass = window.prompt("请输入新建班级的名称（例如：11班，卓越创新班）：");
    if (newClass && newClass.trim() !== '') {
      const trimmedClass = newClass.trim();
      if (!AVAILABLE_CLASSES.includes(trimmedClass)) {
        setCustomClasses(prev => [...prev, trimmedClass]);
        alert(`班级【${trimmedClass}】创建成功！现在可以将其分配给导师或学生。`);
      } else {
        alert("该班级已存在！");
      }
    }
  };

  // 严格拦截版：读取并解析 CSV 文件
  const handleCSVUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (event) => {
      try {
        const text = event.target.result;
        const lines = text.split('\n').map(line => line.trim()).filter(line => line !== '');
        
        // 剔除表头
        if (lines[0].includes('账号') || lines[0].includes('username')) {
          lines.shift();
        }

        const parsedUsers = [];
        const errorLogs = []; // 用于记录被拦截的错误信息

        lines.forEach((line) => {
          const parts = line.split(',');
          const username = parts[0]?.trim() || '';
          const password = parts[1]?.trim() || '';
          const real_name = parts[2]?.trim() || '未命名';
          const class_name = parts[3]?.trim() || null;
          let role = parts[4]?.trim().toLowerCase();
          
          if (!['student', 'teacher', 'admin'].includes(role)) {
              role = 'student';
          }

          // 必须有账号和密码
          if (!username || !password) return; 

          // 🚨 核心逻辑：拦截学生班级异常 🚨
          if (role === 'student') {
            // 1. 学生没填班级
            if (!class_name) {
              errorLogs.push(`❌ [${username}]: 学生必须填写班级`);
              return; // 放弃这条数据，跳出当前循环
            }
            // 2. 学生填了多个班级 (判断是否包含了分隔符 / 、 等)
            if (class_name.includes('/') || class_name.includes('、') || class_name.includes(',') || class_name.includes('&')) {
              errorLogs.push(`❌ [${username}]: 学生只能归属1个班级，不能填多个`);
              return; // 放弃这条数据
            }
          }

          // 校验通过，加入合法列表
          parsedUsers.push({ username, password, real_name, class_name, role });
        });

        // 极端情况：所有数据都不合格
        if (parsedUsers.length === 0) {
          alert(`CSV数据无合法导入项！\n\n拦截原因：\n${errorLogs.join('\n')}`);
          if (fileInputRef.current) fileInputRef.current.value = '';
          return;
        }

        // 部分数据被拦截，弹出警告让管理员确认是否继续导入合法的
        if (errorLogs.length > 0) {
          const confirmProceed = window.confirm(
            `注意！发现 ${errorLogs.length} 条不合规数据已被自动剔除。\n` +
            `(规定：学生必须有班级，且只能有1个班级)\n\n` +
            `拦截明细：\n${errorLogs.slice(0, 5).join('\n')}${errorLogs.length > 5 ? '\n...' : ''}\n\n` +
            `是否继续导入剩余 ${parsedUsers.length} 条合法数据？`
          );
          
          if (!confirmProceed) {
            if (fileInputRef.current) fileInputRef.current.value = '';
            return;
          }
        }

        // 发送后端请求
        const res = await batchRegisterUsers(parsedUsers);
        alert(res.message || `成功导入了 ${parsedUsers.length} 条账号数据！`);
        loadUsers(); loadStats(); loadClassStats();
      } catch (err) {
        alert("批量注册失败，请检查CSV格式。");
      }
      
      if (fileInputRef.current) fileInputRef.current.value = '';
    };
    reader.readAsText(file, 'utf-8');
  };

  // 生成并下载预置的 CSV 模板（含 BOM 头，防止 Excel 乱码）
  const handleDownloadTemplate = () => {
    const csvContent = 
      "账号,密码,真实姓名,班级(老师可多班用/隔开_学生必须且只能填1个),角色(student/teacher/admin)\n" +
      "admin02,123456,王管理,,admin\n" +
      "tea01,123456,张老师,1班/2班,teacher\n" +
      "stu01,123456,李学生,1班,student\n";
    
    // 添加 UTF-8 BOM，解决 Excel 直接打开中文乱码的问题
    const blob = new Blob([new Uint8Array([0xEF, 0xBB, 0xBF]), csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "批量建档标准模板.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex h-[calc(100vh-64px)] bg-slate-50 overflow-hidden w-full relative">
      {/* 侧边栏 */}
      <div className="w-64 bg-slate-900 flex flex-col shrink-0 z-20 shadow-xl">
        <div className="p-6 border-b border-slate-800">
          <h2 className="text-white font-bold flex items-center gap-2"><Shield size={20} className="text-red-400" /> 教务管理系统</h2>
        </div>
        <div className="flex flex-col p-4 gap-2">
          <button onClick={() => setActiveTab('users')} className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-medium ${activeTab === 'users' ? 'bg-red-600 text-white shadow-md' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}>
            <UserCog size={18} /> 用户与权限隔离
          </button>
          <button onClick={() => setActiveTab('classes')} className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-medium ${activeTab === 'classes' ? 'bg-red-600 text-white shadow-md' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}>
            <BookOpen size={18} /> 班级学情监控
          </button>
          <button onClick={() => setActiveTab('stats')} className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-medium ${activeTab === 'stats' ? 'bg-red-600 text-white shadow-md' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}>
            <Activity size={18} /> 全局漏洞与数据
          </button>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="flex-1 overflow-y-auto p-8">
        
        {/* ================= 1. 用户与权限隔离 Tab ================= */}
        {activeTab === 'users' && (
          <div className="space-y-6 animate-in fade-in">
            <div className="flex items-center justify-between mb-6">
              <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2"><Users size={24} className="text-red-500"/> 用户与角色分配</h1>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between gap-4 flex-wrap">
              <div>
                <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-1"><FileSpreadsheet size={18} className="text-emerald-600"/> 通过 CSV 批量建档</h3>
                <p className="text-xs text-slate-500 leading-relaxed">
                  请上传 `.csv` 文本文件。每行一条数据，用英文逗号隔开。<br/>
                  <span className="text-red-500 font-bold">规则限制：</span>学生必须填写班级，且只能归属1个班级；教师可分配多个班级。<br/>
                  如果不确定格式，请先 <button onClick={handleDownloadTemplate} className="text-brand-600 hover:text-brand-700 font-bold underline underline-offset-2">下载 CSV 模板</button>，修改后再上传。
                </p>
              </div>
              <div className="flex items-center gap-3 shrink-0">
                <button onClick={handleDownloadTemplate} className="bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 px-4 py-2.5 rounded-xl text-sm font-bold flex items-center gap-2 transition-colors">
                  <Download size={18}/> 下载模板
                </button>
                <input 
                  type="file" 
                  accept=".csv" 
                  className="hidden" 
                  ref={fileInputRef} 
                  onChange={handleCSVUpload} 
                />
                <button onClick={() => fileInputRef.current?.click()} className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2.5 rounded-xl text-sm font-bold flex items-center gap-2 transition-colors">
                  <UploadCloud size={18}/> 上传 CSV 导入
                </button>
              </div>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-600">
                  <tr>
                    <th className="p-4 font-bold">真实姓名</th>
                    <th className="p-4 font-bold">登录账号</th>
                    <th className="p-4 font-bold">所属/管理班级</th>
                    <th className="p-4 font-bold">当前角色</th>
                    <th className="p-4 font-bold text-right">操作</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {users.map(u => (
                    <tr key={u.id} className="hover:bg-slate-50">
                      <td className="p-4 font-medium text-slate-800">{u.real_name}</td>
                      <td className="p-4 text-slate-500 font-mono text-xs">{u.username}</td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <span className="text-slate-600">{u.class_name ? u.class_name.replace(/,/g, ' / ') : '-'}</span>
                          {/* 无论是老师还是学生，都可以分配/修改班级 */}
                          {['teacher', 'student'].includes(u.role) && (
                            <button onClick={() => openAssignModal(u)} className="text-blue-500 hover:text-blue-700 text-xs flex items-center gap-1 bg-blue-50 px-2 py-1 rounded">
                              <Settings size={12}/> 分配
                            </button>
                          )}
                        </div>
                      </td>
                      <td className="p-4">
                        <select value={u.role} onChange={(e) => handleRoleChange(u.id, e.target.value)} className={`px-2 py-1 rounded text-xs font-bold outline-none border ${u.role === 'admin' ? 'bg-red-100 text-red-700 border-red-200' : u.role === 'teacher' ? 'bg-orange-100 text-orange-700 border-orange-200' : 'bg-blue-100 text-blue-700 border-blue-200'}`}>
                          <option value="student">Student</option>
                          <option value="teacher">Teacher</option>
                          <option value="admin">Admin (System)</option>
                        </select>
                      </td>
                      <td className="p-4 text-right flex justify-end gap-2">
                        <button onClick={() => handleResetPassword(u.id)} className="text-slate-400 hover:text-brand-600 p-1" title="重置密码"><KeyRound size={16} /></button>
                        <button onClick={() => handleDelete(u.id)} className="text-slate-400 hover:text-red-600 p-1" title="彻底删除"><Trash2 size={16} /></button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ================= 2. 班级学情监控 Tab ================= */}
        {activeTab === 'classes' && (
          <div className="space-y-6 animate-in fade-in">
            <div className="flex items-center justify-between mb-6">
              <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2"><BookOpen size={24} className="text-red-500"/> 各班级学情概况</h1>
              <button onClick={handleCreateClass} className="bg-blue-50 text-blue-600 border border-blue-200 hover:bg-blue-100 px-4 py-2 rounded-xl text-sm font-bold flex items-center gap-2 transition-colors">
                <PlusCircle size={16}/> 新建管理班级
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {classStats.length === 0 ? (
                <div className="col-span-3 text-center text-slate-400 py-10">暂无具有学生的班级数据</div>
              ) : (
                classStats.map((c, idx) => (
                  <div key={idx} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                    <h3 className="text-xl font-extrabold text-slate-800 mb-4 border-b border-slate-100 pb-3">{c.class_name}</h3>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-slate-500">学生总数</span>
                      <span className="font-bold text-blue-600">{c.student_count} 人</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-500">已建档真实项目数</span>
                      <span className="font-bold text-emerald-600">{c.project_count} 个</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* ================= 3. 全局数据监控 Tab ================= */}
        {activeTab === 'stats' && (
          <div className="space-y-6 animate-in fade-in">
            <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2 mb-6">
              <Activity size={24} className="text-red-500"/> 宏观统计与全校漏洞看板
            </h1>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white p-5 rounded-2xl border-t-4 border-t-blue-500 shadow-sm">
                <div className="text-slate-500 text-sm font-bold mb-1">注册总人数</div>
                <div className="text-3xl font-extrabold text-slate-800">{stats?.total_users || 0}</div>
              </div>
              <div className="bg-white p-5 rounded-2xl border-t-4 border-t-emerald-500 shadow-sm">
                <div className="text-slate-500 text-sm font-bold mb-1">有效建档项目数</div>
                <div className="text-3xl font-extrabold text-slate-800">{stats?.total_projects || 0}</div>
              </div>
              <div className="bg-white p-5 rounded-2xl border-t-4 border-t-purple-500 shadow-sm">
                <div className="text-slate-500 text-sm font-bold mb-1">累计对话流</div>
                <div className="text-3xl font-extrabold text-slate-800">{stats?.total_conversations || 0}</div>
              </div>
              <div className="bg-white p-5 rounded-2xl border-t-4 border-t-red-500 shadow-sm">
                <div className="text-slate-500 text-sm font-bold mb-1">全局模型健康度</div>
                <div className="text-3xl font-extrabold text-red-600">{stats?.overall_health_score ?? '--'}/100</div>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm mt-6">
              <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-4">
                <AlertTriangle size={18} className="text-red-500"/> 全校超图规则触发排行 (20项全景看板)
              </h3>
              
              <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
                {(!stats || (stats?.top_flaws || []).length === 0) ? (
                  <div className="text-center text-slate-400 py-10 text-sm">暂无统计数据或数据加载中...</div>
                ) : (
                  (stats?.top_flaws || []).map((flaw, idx) => (
                    <div key={idx} className="flex items-center justify-between p-4 bg-slate-50 border border-slate-100 rounded-xl hover:shadow-sm transition-shadow">
                      <div className="flex items-center gap-3">
                        <span className={`px-2 py-1 rounded text-xs font-bold ${
                          flaw.severity === 'Critical' ? 'bg-red-100 text-red-700' : 
                          flaw.severity === 'High' ? 'bg-orange-100 text-orange-700' : 
                          'bg-slate-200 text-slate-700'
                        }`}>
                          {flaw.rule}
                        </span>
                        <span className="font-medium text-slate-700">{flaw.name}</span>
                      </div>
                      
                      <div className="flex items-center gap-4">
                        <span className={`text-xs font-bold ${
                          flaw.severity === 'Critical' ? 'text-red-600' : 
                          flaw.severity === 'High' ? 'text-orange-600' : 
                          'text-slate-500'
                        }`}>
                          {flaw.severity}
                        </span>
                        <div className="text-sm font-mono font-bold text-slate-500 bg-white px-3 py-1 rounded border border-slate-200 min-w-[110px] text-center">
                          波及率: {flaw.frequency}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 分配班级弹窗 Modal */}
      {assignModal.isOpen && (
        <div className="fixed inset-0 bg-slate-900/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="p-5 border-b border-slate-100 bg-slate-50 flex justify-between items-center">
              <div>
                <h3 className="font-bold text-slate-800 text-lg">
                  为{assignModal.user?.role === 'student' ? '学生' : '导师'}【{assignModal.user?.real_name}】分配班级
                </h3>
                <p className="text-xs text-slate-500 mt-1">
                  {assignModal.user?.role === 'student' ? '请为该学生指定归属班级（仅限单选）。' : '勾选该导师负责管理的班级，可多选。'}
                </p>
              </div>
              <button onClick={handleCreateClass} title="找不到班级？点击新建" className="text-blue-500 hover:text-blue-700 p-2 bg-blue-50 rounded-full transition-colors">
                <PlusCircle size={20}/>
              </button>
            </div>
            
            <div className="p-5 max-h-64 overflow-y-auto">
              <div className="grid grid-cols-2 gap-3">
                {AVAILABLE_CLASSES.map(cls => (
                  <label key={cls} className="flex items-center gap-2 p-2 border border-slate-200 rounded-lg cursor-pointer hover:bg-slate-50 transition-colors">
                    <input 
                      // 动态输入框类型：学生用单选框，老师用复选框
                      type={assignModal.user?.role === 'student' ? "radio" : "checkbox"} 
                      name="class_selection"
                      className={`w-4 h-4 text-blue-600 focus:ring-blue-500 ${assignModal.user?.role === 'student' ? 'rounded-full' : 'rounded'}`}
                      checked={assignModal.selectedClasses.includes(cls)}
                      onChange={() => toggleClassSelection(cls)}
                    />
                    <span className="text-sm font-medium text-slate-700 truncate">{cls}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="p-4 border-t border-slate-100 bg-slate-50 flex justify-end gap-3">
              <button onClick={() => setAssignModal({ isOpen: false, user: null, selectedClasses: [] })} className="px-4 py-2 text-sm font-bold text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-100">取消</button>
              <button onClick={submitClassAssignment} className="px-4 py-2 text-sm font-bold text-white bg-blue-600 rounded-lg hover:bg-blue-700">确认分配</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// import React, { useState, useEffect } from 'react';
// import { Shield, Users, Activity, Trash2, KeyRound, AlertTriangle, UserCog, UploadCloud, BookOpen, Settings } from 'lucide-react';
// import { fetchAdminUsers, deleteUser, resetUserPassword, updateUserRole, fetchAdminStats, batchRegisterUsers, assignTeacherClasses, fetchClassStats } from '../api';

// export default function AdminPortal() {
//   const [activeTab, setActiveTab] = useState('users');
//   const [users, setUsers] = useState([]);
//   const [stats, setStats] = useState(null);
//   const [classStats, setClassStats] = useState([]);
//   const [batchInput, setBatchInput] = useState('');

//   // 控制分配班级的弹窗
//   const [assignModal, setAssignModal] = useState({ isOpen: false, user: null, selectedClasses: [] });
//   // 定义标准班级列表 (1班 - 10班)
//   const AVAILABLE_CLASSES = Array.from({ length: 10 }, (_, i) => `${i + 1}班`);

//   useEffect(() => {
//     loadUsers();
//     loadStats();
//     loadClassStats();
//   }, []);

//   const loadUsers = async () => {
//     try { setUsers(await fetchAdminUsers()); } catch (e) { console.error(e); }
//   };
//   const loadStats = async () => {
//     try { setStats(await fetchAdminStats()); } catch (e) { console.error(e); }
//   };
//   const loadClassStats = async () => {
//     try { setClassStats(await fetchClassStats()); } catch (e) { console.error(e); }
//   };

//   const handleDelete = async (userId) => {
//     if (!window.confirm("确定要永久删除该账号吗？")) return;
//     try { await deleteUser(userId); loadUsers(); loadStats(); loadClassStats(); } catch (e) { alert("删除失败"); }
//   };

//   const handleResetPassword = async (userId) => {
//     const newPwd = window.prompt("请输入新的初始密码:", "123456");
//     if (!newPwd) return;
//     try { await resetUserPassword(userId, newPwd); alert("密码重置成功！"); } catch (e) { alert("重置失败"); }
//   };

//   const handleRoleChange = async (userId, newRole) => {
//     try { await updateUserRole(userId, newRole); loadUsers(); } catch (e) { alert("角色修改失败"); }
//   };

//   // 1. 打开弹窗
//   const openAssignModal = (user) => {
//     const currentClasses = user.class_name ? user.class_name.split(',').map(c => c.trim()) : [];
//     setAssignModal({ isOpen: true, user: user, selectedClasses: currentClasses });
//   };

//   // 2. 点击复选框时触发
//   const toggleClassSelection = (className) => {
//     setAssignModal(prev => {
//       const isSelected = prev.selectedClasses.includes(className);
//       const newSelection = isSelected 
//         ? prev.selectedClasses.filter(c => c !== className) // 取消勾选
//         : [...prev.selectedClasses, className]; // 增加勾选
//       return { ...prev, selectedClasses: newSelection };
//     });
//   };

//   // 3. 点击保存时触发，拼成英文逗号字符串发给后端
//   const submitClassAssignment = async () => {
//     try {
//       const classesString = assignModal.selectedClasses.join(',');
//       await assignTeacherClasses(assignModal.user.id, classesString);
//       setAssignModal({ isOpen: false, user: null, selectedClasses: [] });
//       loadUsers(); // 刷新列表
//     } catch (e) {
//       alert("分配班级失败");
//     }
//   };

//   const handleBatchRegister = async () => {
//     if (!batchInput.trim()) return;
//     try {
//       const lines = batchInput.split('\n').filter(line => line.trim() !== '');
//       const parsedUsers = lines.map(line => {
//         const [username, password, real_name, class_name, role] = line.split(',');
//         return { 
//           username: username.trim(), password: password.trim(), real_name: real_name.trim(), 
//           class_name: class_name ? class_name.trim() : null, role: role ? role.trim() : 'student' 
//         };
//       });
//       const res = await batchRegisterUsers(parsedUsers);
//       alert(res.message);
//       setBatchInput('');
//       loadUsers(); loadStats(); loadClassStats();
//     } catch (e) {
//       alert("批量注册失败，格式：账号,密码,姓名,班级,角色");
//     }
//   };

//   return (
//     <div className="flex h-[calc(100vh-64px)] bg-slate-50 overflow-hidden w-full relative">
//       {/* 侧边栏 */}
//       <div className="w-64 bg-slate-900 flex flex-col shrink-0 z-20 shadow-xl">
//         <div className="p-6 border-b border-slate-800">
//           <h2 className="text-white font-bold flex items-center gap-2"><Shield size={20} className="text-red-400" /> 教务管理系统</h2>
//         </div>
//         <div className="flex flex-col p-4 gap-2">
//           <button onClick={() => setActiveTab('users')} className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-medium ${activeTab === 'users' ? 'bg-red-600 text-white shadow-md' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}>
//             <UserCog size={18} /> 用户与权限隔离
//           </button>
//           <button onClick={() => setActiveTab('classes')} className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-medium ${activeTab === 'classes' ? 'bg-red-600 text-white shadow-md' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}>
//             <BookOpen size={18} /> 班级学情监控
//           </button>
//           <button onClick={() => setActiveTab('stats')} className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-medium ${activeTab === 'stats' ? 'bg-red-600 text-white shadow-md' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}>
//             <Activity size={18} /> 全局漏洞与数据
//           </button>
//         </div>
//       </div>

//       {/* 主内容区 */}
//       <div className="flex-1 overflow-y-auto p-8">
        
//         {/* ================= 1. 用户与权限隔离 Tab ================= */}
//         {activeTab === 'users' && (
//           <div className="space-y-6">
//             <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2"><Users size={24} className="text-red-500"/> 用户与角色分配</h1>

//             <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
//               <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-3"><UploadCloud size={18} className="text-slate-500"/> 批量注册账号</h3>
//               <p className="text-xs text-slate-500 mb-2">每行一条数据，格式：<code className="bg-slate-100 px-1 rounded">账号,密码,真实姓名,班级(选填),角色(student/teacher/admin)</code></p>
//               <textarea value={batchInput} onChange={e => setBatchInput(e.target.value)} placeholder="例如：&#10;stu001,123456,张三,1班,student&#10;tech01,123456,李四,1班,teacher" className="w-full border border-slate-300 rounded-lg p-3 text-sm focus:ring-2 focus:ring-red-500 outline-none mb-3 bg-slate-50 font-mono" rows={3}/>
//               <button onClick={handleBatchRegister} disabled={!batchInput} className="bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2">执行批量建档</button>
//             </div>

//             <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
//               <table className="w-full text-left text-sm">
//                 <thead className="bg-slate-50 border-b border-slate-200 text-slate-600">
//                   <tr>
//                     <th className="p-4 font-bold">真实姓名</th>
//                     <th className="p-4 font-bold">登录账号</th>
//                     <th className="p-4 font-bold">所属/管理班级</th>
//                     <th className="p-4 font-bold">当前角色</th>
//                     <th className="p-4 font-bold text-right">操作</th>
//                   </tr>
//                 </thead>
//                 <tbody className="divide-y divide-slate-100">
//                   {users.map(u => (
//                     <tr key={u.id} className="hover:bg-slate-50">
//                       <td className="p-4 font-medium text-slate-800">{u.real_name}</td>
//                       <td className="p-4 text-slate-500 font-mono text-xs">{u.username}</td>
//                       <td className="p-4">
//                         <div className="flex items-center gap-2">
//                           <span className="text-slate-600">{u.class_name || '-'}</span>
//                           {/* 如果是老师，显示分配班级按钮 */}
//                           {u.role === 'teacher' && (
//                             <button onClick={() => openAssignModal(u)} className="text-blue-500 hover:text-blue-700 text-xs flex items-center gap-1 bg-blue-50 px-2 py-1 rounded">
//                               <Settings size={12}/> 分配
//                             </button>
//                           )}
//                         </div>
//                       </td>
//                       <td className="p-4">
//                         <select value={u.role} onChange={(e) => handleRoleChange(u.id, e.target.value)} className={`px-2 py-1 rounded text-xs font-bold outline-none border ${u.role === 'admin' ? 'bg-red-100 text-red-700 border-red-200' : u.role === 'teacher' ? 'bg-orange-100 text-orange-700 border-orange-200' : 'bg-blue-100 text-blue-700 border-blue-200'}`}>
//                           <option value="student">Student</option>
//                           <option value="teacher">Teacher</option>
//                           <option value="admin">Admin (System)</option>
//                         </select>
//                       </td>
//                       <td className="p-4 text-right flex justify-end gap-2">
//                         <button onClick={() => handleResetPassword(u.id)} className="text-slate-400 hover:text-brand-600 p-1" title="重置密码"><KeyRound size={16} /></button>
//                         <button onClick={() => handleDelete(u.id)} className="text-slate-400 hover:text-red-600 p-1" title="彻底删除"><Trash2 size={16} /></button>
//                       </td>
//                     </tr>
//                   ))}
//                 </tbody>
//               </table>
//             </div>
//           </div>
//         )}

//         {/* ================= 2. 班级学情监控 Tab ================= */}
//         {activeTab === 'classes' && (
//           <div className="space-y-6 animate-in fade-in">
//             <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2 mb-6"><BookOpen size={24} className="text-red-500"/> 各班级学情概况</h1>
//             <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
//               {classStats.length === 0 ? (
//                 <div className="col-span-3 text-center text-slate-400 py-10">暂无班级数据</div>
//               ) : (
//                 classStats.map((c, idx) => (
//                   <div key={idx} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
//                     <h3 className="text-xl font-extrabold text-slate-800 mb-4 border-b border-slate-100 pb-3">{c.class_name}</h3>
//                     <div className="flex justify-between items-center mb-2">
//                       <span className="text-sm text-slate-500">学生总数</span>
//                       <span className="font-bold text-blue-600">{c.student_count} 人</span>
//                     </div>
//                     <div className="flex justify-between items-center">
//                       <span className="text-sm text-slate-500">已建档真实项目数</span>
//                       <span className="font-bold text-emerald-600">{c.project_count} 个</span>
//                     </div>
//                   </div>
//                 ))
//               )}
//             </div>
//           </div>
//         )}

//         {/* ================= 3. 全局数据监控 Tab ================= */}
//         {activeTab === 'stats' && (
//           <div className="space-y-6 animate-in fade-in">
//             <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2 mb-6">
//               <Activity size={24} className="text-red-500"/> 宏观统计与全校漏洞看板
//             </h1>
            
//             {/* 数据卡片区：使用 ?. 和 || 0 进行安全渲染 */}
//             <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
//               <div className="bg-white p-5 rounded-2xl border-t-4 border-t-blue-500 shadow-sm">
//                 <div className="text-slate-500 text-sm font-bold mb-1">注册总人数</div>
//                 <div className="text-3xl font-extrabold text-slate-800">{stats?.total_users || 0}</div>
//               </div>
//               <div className="bg-white p-5 rounded-2xl border-t-4 border-t-emerald-500 shadow-sm">
//                 <div className="text-slate-500 text-sm font-bold mb-1">有效建档项目数</div>
//                 <div className="text-3xl font-extrabold text-slate-800">{stats?.total_projects || 0}</div>
//               </div>
//               <div className="bg-white p-5 rounded-2xl border-t-4 border-t-purple-500 shadow-sm">
//                 <div className="text-slate-500 text-sm font-bold mb-1">累计对话流</div>
//                 <div className="text-3xl font-extrabold text-slate-800">{stats?.total_conversations || 0}</div>
//               </div>
//               <div className="bg-white p-5 rounded-2xl border-t-4 border-t-red-500 shadow-sm">
//                 <div className="text-slate-500 text-sm font-bold mb-1">全局模型健康度</div>
//                 <div className="text-3xl font-extrabold text-red-600">{stats?.overall_health_score ?? '--'}/100</div>
//               </div>
//             </div>
            
//             {/* 20 项全景排行榜区 */}
//             <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm mt-6">
//               <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-4">
//                 <AlertTriangle size={18} className="text-red-500"/> 全校超图规则触发排行 (20项全景看板)
//               </h3>
              
//               <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
//                 {(!stats || (stats?.top_flaws || []).length === 0) ? (
//                   <div className="text-center text-slate-400 py-10 text-sm">暂无统计数据或数据加载中...</div>
//                 ) : (
//                   (stats?.top_flaws || []).map((flaw, idx) => (
//                     <div key={idx} className="flex items-center justify-between p-4 bg-slate-50 border border-slate-100 rounded-xl hover:shadow-sm transition-shadow">
//                       <div className="flex items-center gap-3">
//                         <span className={`px-2 py-1 rounded text-xs font-bold ${
//                           flaw.severity === 'Critical' ? 'bg-red-100 text-red-700' : 
//                           flaw.severity === 'High' ? 'bg-orange-100 text-orange-700' : 
//                           'bg-slate-200 text-slate-700'
//                         }`}>
//                           {flaw.rule}
//                         </span>
//                         <span className="font-medium text-slate-700">{flaw.name}</span>
//                       </div>
                      
//                       <div className="flex items-center gap-4">
//                         <span className={`text-xs font-bold ${
//                           flaw.severity === 'Critical' ? 'text-red-600' : 
//                           flaw.severity === 'High' ? 'text-orange-600' : 
//                           'text-slate-500'
//                         }`}>
//                           {flaw.severity}
//                         </span>
//                         <div className="text-sm font-mono font-bold text-slate-500 bg-white px-3 py-1 rounded border border-slate-200 min-w-[110px] text-center">
//                           波及率: {flaw.frequency}
//                         </div>
//                       </div>
//                     </div>
//                   ))
//                 )}
//               </div>
//             </div>
//           </div>
//         )}
//       </div>

//       {/* 分配班级弹窗 Modal */}
//       {assignModal.isOpen && (
//         <div className="fixed inset-0 bg-slate-900/40 z-50 flex items-center justify-center p-4">
//           <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-200">
//             <div className="p-5 border-b border-slate-100 bg-slate-50">
//               <h3 className="font-bold text-slate-800 text-lg">为导师【{assignModal.user?.real_name}】分配班级</h3>
//               <p className="text-xs text-slate-500 mt-1">勾选该导师负责管理的班级，可多选。</p>
//             </div>
            
//             <div className="p-5">
//               <div className="grid grid-cols-2 gap-3">
//                 {AVAILABLE_CLASSES.map(cls => (
//                   <label key={cls} className="flex items-center gap-2 p-2 border border-slate-200 rounded-lg cursor-pointer hover:bg-slate-50 transition-colors">
//                     <input 
//                       type="checkbox" 
//                       className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
//                       checked={assignModal.selectedClasses.includes(cls)}
//                       onChange={() => toggleClassSelection(cls)}
//                     />
//                     <span className="text-sm font-medium text-slate-700">{cls}</span>
//                   </label>
//                 ))}
//               </div>
//             </div>

//             <div className="p-4 border-t border-slate-100 bg-slate-50 flex justify-end gap-3">
//               <button onClick={() => setAssignModal({ isOpen: false, user: null, selectedClasses: [] })} className="px-4 py-2 text-sm font-bold text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-100">取消</button>
//               <button onClick={submitClassAssignment} className="px-4 py-2 text-sm font-bold text-white bg-blue-600 rounded-lg hover:bg-blue-700">确认分配</button>
//             </div>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// }