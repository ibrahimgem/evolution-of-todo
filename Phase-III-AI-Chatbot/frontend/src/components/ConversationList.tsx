'use client';

import { useState } from 'react';
import type { Conversation } from '../types/chat';
import { Plus, MessageCircle, Calendar, MoreVertical, Trash2, Sparkles } from 'lucide-react';

/**
 * ConversationList Component - Enhanced with modern styling
 *
 * Features:
 * - Beautiful gradient hover effects
 * - Smooth animations and transitions
 * - Glass morphism styling
 * - Enhanced visual hierarchy
 * - Micro-interactions
 */
interface ConversationListProps {
  conversations?: Conversation[];
  selectedId?: string;
  onSelect?: (id: string) => void;
  onNew?: () => void;
  onDelete?: (id: string) => void;
}

export function ConversationList({
  conversations = [],
  selectedId,
  onSelect,
  onNew,
  onDelete,
}: ConversationListProps) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [menuOpenId, setMenuOpenId] = useState<string | null>(null);

  /**
   * Format date for display
   */
  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return 'Today';
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else {
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
      });
    }
  };

  /**
   * Truncate conversation title
   */
  const truncateTitle = (title: string, maxLength: number = 50): string => {
    if (title.length <= maxLength) return title;
    return title.substring(0, maxLength) + '...';
  };

  /**
   * Handle conversation selection
   */
  const handleSelect = (id: string) => {
    onSelect?.(id);
    setMenuOpenId(null);
  };

  /**
   * Handle delete conversation
   */
  const handleDelete = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this conversation?')) {
      onDelete?.(id);
      setMenuOpenId(null);
    }
  };

  /**
   * Toggle menu for conversation
   */
  const toggleMenu = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setMenuOpenId(menuOpenId === id ? null : id);
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-white to-gray-50 dark:from-gray-800 dark:to-gray-900">
      {/* Header with New Conversation Button */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
        <button
          onClick={onNew}
          className="group w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 px-4 rounded-xl
                   transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed
                   flex items-center justify-center gap-2 shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98]"
          disabled={!onNew}
        >
          <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform duration-300" />
          <span>New Chat</span>
          <Sparkles className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <div className="p-6 text-center animate-fade-in">
            <div className="relative mb-4 inline-block">
              <MessageCircle className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600" />
              <div className="absolute inset-0 blur-xl bg-blue-400/20 dark:bg-blue-600/20 animate-pulse-slow" />
            </div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              No conversations yet
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500">
              Start chatting to create your first conversation
            </p>
          </div>
        ) : (
          <ul className="p-2 space-y-1.5">
            {conversations.map((conv, index) => (
              <li
                key={conv.id}
                onMouseEnter={() => setHoveredId(conv.id)}
                onMouseLeave={() => setHoveredId(null)}
                className="relative animate-slide-in-right"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <button
                  onClick={() => handleSelect(conv.id)}
                  className={`w-full text-left p-3 rounded-xl transition-all duration-300 group ${
                    selectedId === conv.id
                      ? 'bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/30 dark:to-purple-900/30 border-l-4 border-blue-600 shadow-md scale-[1.02]'
                      : 'hover:bg-gray-100 dark:hover:bg-gray-700/50 border-l-4 border-transparent hover:border-gray-300 dark:hover:border-gray-600 hover:scale-[1.01]'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      {/* Conversation Title */}
                      <div
                        className={`font-semibold text-sm truncate mb-1 ${
                          selectedId === conv.id
                            ? 'text-blue-900 dark:text-blue-100'
                            : 'text-gray-900 dark:text-gray-100 group-hover:text-blue-900 dark:group-hover:text-blue-100'
                        }`}
                        title={conv.title}
                      >
                        {truncateTitle(conv.title)}
                      </div>

                      {/* Conversation Date */}
                      <div className="flex items-center gap-1.5">
                        <Calendar className="w-3 h-3 text-gray-400 dark:text-gray-500" />
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {formatDate(conv.updated_at || conv.created_at)}
                        </span>
                      </div>
                    </div>

                    {/* More Actions Button (appears on hover) */}
                    {(hoveredId === conv.id || menuOpenId === conv.id) && onDelete && (
                      <div className="relative flex-shrink-0">
                        <button
                          onClick={(e) => toggleMenu(e, conv.id)}
                          className="p-1.5 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                          aria-label="More options"
                        >
                          <MoreVertical className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                        </button>

                        {/* Dropdown Menu */}
                        {menuOpenId === conv.id && (
                          <div className="absolute right-0 top-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-xl z-20 min-w-[140px] animate-scale-in">
                            <button
                              onClick={(e) => handleDelete(e, conv.id)}
                              className="w-full text-left px-4 py-2.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl flex items-center gap-2 font-medium transition-colors"
                            >
                              <Trash2 className="w-4 h-4" />
                              <span>Delete</span>
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Footer with Conversation Count */}
      {conversations.length > 0 && (
        <div className="p-3 border-t border-gray-200 dark:border-gray-700 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
          <div className="flex items-center justify-center gap-2 text-xs text-gray-500 dark:text-gray-400">
            <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
            <span className="font-medium">
              {conversations.length} conversation{conversations.length !== 1 ? 's' : ''}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
