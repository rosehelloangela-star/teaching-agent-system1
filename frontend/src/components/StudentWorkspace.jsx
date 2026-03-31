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