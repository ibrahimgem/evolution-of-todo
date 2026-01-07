---
name: openai-chatkit
description: Build conversational AI interfaces using OpenAI ChatKit in Next.js applications. Use when implementing chat UIs, message streaming, conversation management, or integrating ChatKit components with FastAPI backends. Covers installation, component integration, authentication flow, message handling, and UI customization.
---

# OpenAI ChatKit Integration

## Overview

Implement production-ready conversational AI interfaces using OpenAI ChatKit in Next.js applications with TypeScript. This skill covers ChatKit component integration, message streaming, conversation state management, and backend API integration.

## Quick Start

### Installation

```bash
npm install @openai/chatkit
```

### Basic ChatKit Component

```typescript
// app/chat/page.tsx
'use client';

import { ChatKit } from '@openai/chatkit';
import { useAuth } from '@/context/AuthContext';

export default function ChatPage() {
  const { token } = useAuth();

  return (
    <ChatKit
      apiUrl="/api/chat"
      authToken={token}
      placeholder="Ask me to manage your tasks..."
      theme="light"
    />
  );
}
```

## Core Integration Patterns

### 1. Authentication Flow

ChatKit requires JWT tokens from your existing auth system:

```typescript
// context/AuthContext.tsx
'use client';

import { createContext, useContext, useState, useEffect } from 'react';

interface AuthContextType {
  token: string | null;
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType>(null!);

export function AuthProvider({ children }: { children: React.Node }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Load token from localStorage on mount
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
      // Optionally validate and fetch user
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) throw new Error('Login failed');

    const data = await response.json();
    setToken(data.access_token);
    setUser(data.user);
    localStorage.setItem('token', data.access_token);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

### 2. Chat API Endpoint Integration

ChatKit communicates with your backend via POST requests:

```typescript
// app/api/chat/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const authHeader = request.headers.get('authorization');

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const token = authHeader.substring(7);
  const body = await request.json();
  const { message, conversation_id } = body;

  // Forward to FastAPI backend
  const response = await fetch(`${process.env.BACKEND_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ message, conversation_id }),
  });

  if (!response.ok) {
    return NextResponse.json(
      { error: 'Backend error' },
      { status: response.status }
    );
  }

  const data = await response.json();
  return NextResponse.json(data);
}
```

### 3. Message Streaming

Enable real-time streaming responses:

```typescript
// app/chat/page.tsx
<ChatKit
  apiUrl="/api/chat"
  authToken={token}
  streaming={true}
  onMessageStream={(chunk) => {
    // Handle streaming chunks
    console.log('Received chunk:', chunk);
  }}
/>
```

Backend streaming endpoint:

```python
# backend/src/routes/chat.py
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator

router = APIRouter()

async def generate_stream(message: str, conversation_id: str) -> AsyncGenerator[str, None]:
    """Stream AI responses chunk by chunk"""
    # Call OpenAI Agents SDK with streaming
    async for chunk in agent.stream_response(message, conversation_id):
        yield f"data: {json.dumps({'content': chunk})}\n\n"

@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    return StreamingResponse(
        generate_stream(request.message, request.conversation_id),
        media_type="text/event-stream"
    )
```

### 4. Conversation Management

Display conversation history sidebar:

```typescript
// components/ConversationList.tsx
'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';

interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export function ConversationList({ onSelect }: { onSelect: (id: string) => void }) {
  const { token } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);

  useEffect(() => {
    async function loadConversations() {
      const response = await fetch('/api/conversations', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await response.json();
      setConversations(data.conversations);
    }
    loadConversations();
  }, [token]);

  return (
    <div className="w-64 bg-gray-100 p-4">
      <h2 className="font-bold mb-4">Conversations</h2>
      {conversations.map(conv => (
        <div
          key={conv.id}
          onClick={() => onSelect(conv.id)}
          className="p-2 hover:bg-gray-200 cursor-pointer rounded"
        >
          {conv.title}
        </div>
      ))}
    </div>
  );
}
```

### 5. Tool Call Visualization

Display tool executions in the chat:

```typescript
// components/ChatMessage.tsx
interface ToolCall {
  tool: string;
  status: 'pending' | 'success' | 'error';
  result?: any;
}

export function ChatMessage({ message, toolCalls }: {
  message: string;
  toolCalls?: ToolCall[]
}) {
  return (
    <div className="message">
      <p>{message}</p>
      {toolCalls && toolCalls.length > 0 && (
        <div className="tool-calls mt-2">
          {toolCalls.map((call, idx) => (
            <div key={idx} className="tool-call flex items-center gap-2 text-sm text-gray-600">
              {call.status === 'success' && <span>✓</span>}
              {call.status === 'error' && <span>✗</span>}
              {call.status === 'pending' && <span>⏳</span>}
              <span>{call.tool}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

## UI Customization

### Theme Configuration

```typescript
<ChatKit
  theme={{
    primary: '#3b82f6',
    background: '#ffffff',
    text: '#1f2937',
    messageBubbleUser: '#3b82f6',
    messageBubbleAssistant: '#f3f4f6',
  }}
  fontFamily="Inter, sans-serif"
/>
```

### Custom Message Renderer

```typescript
<ChatKit
  renderMessage={(message) => (
    <CustomMessage
      content={message.content}
      role={message.role}
      timestamp={message.created_at}
      toolCalls={message.tool_calls}
    />
  )}
/>
```

## Error Handling

```typescript
<ChatKit
  onError={(error) => {
    console.error('ChatKit error:', error);
    // Show user-friendly error message
    toast.error('Failed to send message. Please try again.');
  }}
  retryConfig={{
    maxRetries: 3,
    retryDelay: 1000,
  }}
/>
```

## Complete Integration Example

```typescript
// app/chat/page.tsx
'use client';

import { ChatKit } from '@openai/chatkit';
import { ConversationList } from '@/components/ConversationList';
import { useAuth } from '@/context/AuthContext';
import { useState } from 'react';

export default function ChatPage() {
  const { token } = useAuth();
  const [conversationId, setConversationId] = useState<string | null>(null);

  return (
    <div className="flex h-screen">
      <ConversationList onSelect={setConversationId} />
      <div className="flex-1">
        <ChatKit
          apiUrl="/api/chat"
          authToken={token}
          conversationId={conversationId}
          streaming={true}
          placeholder="Ask me to manage your tasks..."
          theme="light"
          onError={(error) => console.error(error)}
          renderMessage={(message) => (
            <ChatMessage
              content={message.content}
              role={message.role}
              toolCalls={message.tool_calls}
            />
          )}
        />
      </div>
    </div>
  );
}
```

## Best Practices

1. **Authentication**: Always validate JWT tokens on both frontend and backend
2. **Error Boundaries**: Wrap ChatKit in React Error Boundaries for graceful failures
3. **Loading States**: Show loading indicators during message sending
4. **Optimistic Updates**: Display user messages immediately before backend confirmation
5. **Token Refresh**: Implement token refresh logic for long-running conversations
6. **Rate Limiting**: Display rate limit warnings to users proactively
7. **Accessibility**: Ensure chat interface is keyboard-navigable and screen-reader friendly

## Common Issues

**Issue**: ChatKit not authenticating
- Verify token format is `Bearer <token>`
- Check token expiration
- Confirm backend accepts the authorization header

**Issue**: Messages not streaming
- Ensure backend returns `text/event-stream` content type
- Verify `streaming={true}` prop is set
- Check network tab for SSE connection

**Issue**: Conversation not persisting
- Confirm conversation_id is passed to backend
- Verify database is storing messages correctly
- Check that conversation_id is maintained across requests
