'use client';

import type { ChatMessage as ChatMessageType } from '@/types/chat';
import { ToolCallBadge } from './ToolCallBadge';
import { User, Bot, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

/**
 * ChatMessage Component - Enhanced with stunning visuals
 *
 * Features:
 * - Modern bubble design with gradients
 * - Smooth animations and transitions
 * - Enhanced avatars with gradient backgrounds
 * - Better status indicators
 * - Glass morphism effects
 * - Micro-interactions on hover
 */
interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  // Format timestamp
  const timeStr = message.timestamp.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });

  /**
   * Render status indicator for user messages
   */
  const renderStatus = () => {
    if (!message.status || !isUser) return null;

    switch (message.status) {
      case 'sending':
        return (
          <div className="flex items-center gap-1.5 text-xs text-white/80 mt-2">
            <Clock className="w-3.5 h-3.5 animate-pulse" />
            <span>Sending...</span>
          </div>
        );
      case 'sent':
        return (
          <div className="flex items-center gap-1.5 text-xs text-white/80 mt-2">
            <CheckCircle className="w-3.5 h-3.5" />
            <span>Delivered</span>
          </div>
        );
      case 'error':
        return (
          <div className="flex items-center gap-1.5 text-xs text-red-200 mt-2">
            <XCircle className="w-3.5 h-3.5" />
            <span>Failed to send</span>
          </div>
        );
      default:
        return null;
    }
  };

  // System messages (rare, but possible for admin notices)
  if (isSystem) {
    return (
      <div className="flex justify-center mb-6 animate-slide-down">
        <div className="glass dark:glass-dark rounded-2xl px-5 py-3 max-w-md border border-yellow-200/50 dark:border-yellow-700/50 shadow-lg">
          <div className="flex items-center gap-2 mb-1">
            <AlertCircle className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
            <span className="text-xs font-semibold text-yellow-800 dark:text-yellow-200 uppercase tracking-wider">
              System Notice
            </span>
          </div>
          <p className="text-sm text-yellow-900 dark:text-yellow-100 text-center leading-relaxed">
            {message.content}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-8 group animate-slide-up`}>
      <div className="flex gap-3 max-w-[85%] md:max-w-[75%]">
        {/* Avatar (only for assistant) */}
        {!isUser && (
          <div className="flex-shrink-0">
            <div className="relative w-10 h-10 rounded-2xl bg-gradient-to-br from-purple-500 via-blue-600 to-cyan-500 flex items-center justify-center shadow-lg ring-2 ring-white/20 dark:ring-gray-800/50 group-hover:scale-110 transition-transform duration-300">
              <Bot className="w-6 h-6 text-white drop-shadow-lg" />
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-purple-400 to-cyan-400 opacity-0 group-hover:opacity-30 blur-xl transition-opacity duration-300" />
            </div>
          </div>
        )}

        {/* Message Content */}
        <div className="flex-1 min-w-0">
          {/* Message Bubble */}
          <div
            className={`rounded-2xl px-5 py-3.5 shadow-md transition-all duration-300 ${
              isUser
                ? 'bg-gradient-to-br from-blue-600 to-purple-600 text-white shadow-blue-500/20 group-hover:shadow-lg group-hover:shadow-blue-500/30'
                : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-700 shadow-gray-200/50 dark:shadow-gray-900/50 group-hover:shadow-lg group-hover:border-gray-300 dark:group-hover:border-gray-600'
            }`}
          >
            {/* Message Text */}
            <div className="text-sm md:text-base whitespace-pre-wrap break-words leading-relaxed">
              {message.content}
            </div>

            {/* Status Indicator (for user messages) */}
            {renderStatus()}

            {/* Tool Calls (for assistant messages) */}
            {message.toolCalls && message.toolCalls.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-200/50 dark:border-gray-600/50">
                <div className="flex items-center gap-2 text-xs font-semibold mb-3 text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
                  Actions Performed
                </div>
                <div className="flex flex-wrap gap-2">
                  {message.toolCalls.map((toolCall, index) => (
                    <ToolCallBadge key={index} toolCall={toolCall} />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Timestamp */}
          <div
            className={`text-xs text-gray-500 dark:text-gray-400 mt-2 px-1 ${
              isUser ? 'text-right' : 'text-left'
            }`}
          >
            {timeStr}
          </div>
        </div>

        {/* Avatar (only for user) */}
        {isUser && (
          <div className="flex-shrink-0">
            <div className="relative w-10 h-10 rounded-2xl bg-gradient-to-br from-blue-500 via-cyan-600 to-teal-500 flex items-center justify-center shadow-lg ring-2 ring-white/20 dark:ring-gray-800/50 group-hover:scale-110 transition-transform duration-300">
              <User className="w-6 h-6 text-white drop-shadow-lg" />
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-blue-400 to-teal-400 opacity-0 group-hover:opacity-30 blur-xl transition-opacity duration-300" />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
