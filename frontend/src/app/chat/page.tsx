'use client';

import { useState } from 'react';
import { ChatKit } from '@/components/ChatKit';

export default function ChatPage() {
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a0a2e 50%, #0a0a0a 100%)'
    }}>
      <ChatKit 
        conversationId={conversationId}
        onConversationChange={setConversationId}
      />
    </div>
  );
}
