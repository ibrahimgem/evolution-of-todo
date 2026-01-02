'use client';

import React, { createContext, useContext } from 'react';

/**
 * ChatContext - Configuration for OpenAI ChatKit Web Component
 * Phase 1: Shell structure with configuration
 * Full implementation in Phase 3 (US1) with ChatKit web component integration
 *
 * Note: @openai/chatkit is a Web Component (custom element), not a React component.
 * It will be used directly in the chat page as <openai-chatkit> element.
 */

interface ChatConfig {
  apiUrl: string;
  streamingEnabled: boolean;
}

interface ChatContextType {
  config: ChatConfig;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const config: ChatConfig = {
    apiUrl: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
    streamingEnabled: true,
  };

  return (
    <ChatContext.Provider value={{ config }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChatConfig() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChatConfig must be used within a ChatProvider');
  }
  return context;
}

export default ChatProvider;
