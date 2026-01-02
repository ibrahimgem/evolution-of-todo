/**
 * TypeScript type definitions for chat functionality
 * T020: Complete types aligned with API contract (specs/003-ai-chatbot/contracts/chat-api.yaml)
 */

/**
 * Message role types matching backend enum
 */
export type MessageRole = 'user' | 'assistant' | 'system';

/**
 * Message status during processing (client-side only)
 */
export type MessageStatus = 'sending' | 'sent' | 'error';

/**
 * Tool call information
 * Represents MCP tool invocations and results
 */
export interface ToolCall {
  tool_name: string;
  result: unknown;
}

/**
 * Message interface matching backend schema
 */
export interface Message {
  id: string;
  conversation_id: string;
  role: MessageRole;
  content: string | null;
  tool_calls: Record<string, unknown> | null;
  created_at: string;
}

/**
 * Chat message interface (client-side with additional UI state)
 */
export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  status?: MessageStatus;
  toolCalls?: ToolCall[];
}

/**
 * Conversation metadata matching backend schema
 */
export interface Conversation {
  id: string;
  user_id: number;
  title: string;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, unknown>;
}

/**
 * Chat API request payload
 */
export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

/**
 * Chat API response payload
 */
export interface ChatResponse {
  response: string;
  conversation_id: string;
  tool_calls: ToolCall[];
}

/**
 * API error response
 */
export interface ApiErrorResponse {
  error: string;
  message: string;
  code: string;
  details?: Record<string, unknown>;
}
