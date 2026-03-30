// import React, { useState } from 'react';
// import { MessageSquare, FolderGit2 } from 'lucide-react';
// import FreeChatView from './FreeChatView';
// import ProjectWorkspaceView from './ProjectWorkspaceView';

// export default function StudentWorkspace({ currentUser }) { 
//   const [activeNav, setActiveNav] = useState('chat');

//   return (
//     <div className="flex h-[calc(100vh-64px)] bg-white overflow-hidden">
//       {/* 最左侧：一级导航栏 */}
//       <div className="w-20 bg-slate-900 flex flex-col items-center py-6 gap-6 shrink-0 z-20">
//         <button 
//           onClick={() => setActiveNav('chat')}
//           className={`flex flex-col items-center gap-1 p-3 rounded-xl transition-all ${
//             activeNav === 'chat' ? 'bg-brand-600 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'
//           }`}
//         >
//           <MessageSquare size={24} />
//           <span className="text-[10px] font-bold">自由对话</span>
//         </button>
//         <button 
//           onClick={() => setActiveNav('workspace')}
//           className={`flex flex-col items-center gap-1 p-3 rounded-xl transition-all ${
//             activeNav === 'workspace' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'
//           }`}
//         >
//           <FolderGit2 size={24} />
//           <span className="text-[10px] font-bold">工作台</span>
//         </button>
//       </div>

//       {/* 右侧：内容区切换 */}
//       <div className="flex-1 flex overflow-hidden relative">
//         <div className={`w-full h-full ${activeNav === 'chat' ? 'flex' : 'hidden'}`}>
//           <FreeChatView />
//         </div>
        
//         <div className={`w-full h-full ${activeNav === 'workspace' ? 'flex' : 'hidden'}`}>
//           {/* 2. 在这里把包裹接着往下传！ */}
//           <ProjectWorkspaceView currentUser={currentUser} /> 
//         </div>
//       </div>
//     </div>
//   );
// }

// import React from 'react';
// import FreeChatView from './FreeChatView';

// export default function StudentWorkspace({ currentUser }) {
//   return (
//     <div className="h-[calc(100vh-64px)] bg-white overflow-hidden">
//       <FreeChatView currentUser={currentUser} />
//     </div>
//   );
// }

import React from 'react';
// 注意这里变成了 ./chat/FreeChatView
import FreeChatView from './chat/FreeChatView'; 

export default function StudentWorkspace({ currentUser }) {
  return (
    <div className="h-[calc(100vh-64px)] min-h-0 bg-white overflow-hidden">
      <FreeChatView currentUser={currentUser} />
    </div>
  );
}