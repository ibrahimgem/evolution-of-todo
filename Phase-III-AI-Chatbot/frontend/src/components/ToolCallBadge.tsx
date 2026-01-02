'use client';

import { useState } from 'react';
import type { ToolCall } from '../types/chat';
import {
  CheckCircle,
  XCircle,
  Plus,
  List,
  Trash2,
  Edit,
  CheckSquare,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';
import { TaskList, type Task } from './TaskList';

/**
 * ToolCallBadge Component
 * T037: Complete implementation with tool execution visualization
 * T049-T050: Enhanced with TaskList rendering for list_tasks results
 *
 * Features:
 * - Visual indicators for tool success/failure
 * - Tool-specific icons (add_task, list_tasks, etc.)
 * - Expandable details showing tool results
 * - Color-coded badges based on tool type
 * - Responsive design with hover effects
 * - TaskList component for displaying task arrays
 */

/**
 * Type for list_tasks result
 */
interface ListTasksResult {
  success: boolean;
  tasks: Task[];
  total: number;
  offset: number;
  limit: number;
  error?: string;
}

/**
 * Type guard to check if result is ListTasksResult
 */
function isListTasksResult(result: unknown): result is ListTasksResult {
  return (
    typeof result === 'object' &&
    result !== null &&
    'tasks' in result &&
    Array.isArray((result as ListTasksResult).tasks)
  );
}

interface ToolCallBadgeProps {
  toolCall: ToolCall;
}

/**
 * Get icon for tool name
 */
function getToolIcon(toolName: string) {
  switch (toolName) {
    case 'add_task':
      return <Plus className="w-3 h-3" />;
    case 'list_tasks':
      return <List className="w-3 h-3" />;
    case 'complete_task':
      return <CheckSquare className="w-3 h-3" />;
    case 'delete_task':
      return <Trash2 className="w-3 h-3" />;
    case 'update_task':
      return <Edit className="w-3 h-3" />;
    case 'filter_tasks':
      return <List className="w-3 h-3" />;
    default:
      return null;
  }
}

/**
 * Get badge color scheme based on tool name
 */
function getBadgeColors(toolName: string): string {
  switch (toolName) {
    case 'add_task':
      return 'bg-gradient-to-br from-green-50 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 text-green-800 dark:text-green-200 border-green-300/50 dark:border-green-700/50';
    case 'list_tasks':
      return 'bg-gradient-to-br from-blue-50 to-cyan-100 dark:from-blue-900/30 dark:to-cyan-900/30 text-blue-800 dark:text-blue-200 border-blue-300/50 dark:border-blue-700/50';
    case 'complete_task':
      return 'bg-gradient-to-br from-purple-50 to-fuchsia-100 dark:from-purple-900/30 dark:to-fuchsia-900/30 text-purple-800 dark:text-purple-200 border-purple-300/50 dark:border-purple-700/50';
    case 'delete_task':
      return 'bg-gradient-to-br from-red-50 to-rose-100 dark:from-red-900/30 dark:to-rose-900/30 text-red-800 dark:text-red-200 border-red-300/50 dark:border-red-700/50';
    case 'update_task':
      return 'bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30 text-blue-800 dark:text-blue-200 border-blue-300/50 dark:border-blue-700/50';
    case 'filter_tasks':
      return 'bg-gradient-to-br from-sky-50 to-blue-100 dark:from-sky-900/30 dark:to-blue-900/30 text-sky-800 dark:text-sky-200 border-sky-300/50 dark:border-sky-700/50';
    default:
      return 'bg-gradient-to-br from-gray-50 to-slate-100 dark:from-gray-900/30 dark:to-slate-900/30 text-gray-800 dark:text-gray-200 border-gray-300/50 dark:border-gray-700/50';
  }
}

/**
 * Format tool name for display
 */
function formatToolName(toolName: string | undefined): string {
  if (!toolName) return 'Unknown Tool';

  return toolName
    .replace(/_/g, ' ')
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Check if tool call was successful
 */
function isToolSuccess(result: unknown): boolean {
  if (typeof result === 'object' && result !== null) {
    const typedResult = result as { success?: boolean };
    return typedResult.success === true || typedResult.success === undefined;
  }
  return true;
}

/**
 * Extract meaningful summary from tool result
 */
function getToolSummary(toolName: string, result: unknown): string {
  if (!result || typeof result !== 'object') {
    return 'No details available';
  }

  const isSuccess = isToolSuccess(result);
  const typedResult = result as Record<string, unknown>;

  if (!isSuccess && typedResult.error && typeof typedResult.error === 'string') {
    return typedResult.error;
  }

  switch (toolName) {
    case 'add_task':
      if (typedResult.task && typeof typedResult.task === 'object') {
        const task = typedResult.task as { title?: string };
        return `Created task: ${task.title || 'Untitled'}`;
      }
      return 'Task created successfully';

    case 'list_tasks':
      if (isListTasksResult(result)) {
        const count = result.tasks.length;
        const total = result.total || count;
        return `Found ${count} of ${total} task${total !== 1 ? 's' : ''}`;
      }
      return 'Tasks retrieved';

    case 'complete_task':
      if (typedResult.task && typeof typedResult.task === 'object') {
        const task = typedResult.task as { completed?: boolean };
        return `Marked as ${task.completed ? 'complete' : 'incomplete'}`;
      }
      return 'Status updated';

    case 'delete_task':
      return 'Task deleted';

    case 'update_task':
      if (typedResult.task && typeof typedResult.task === 'object') {
        const task = typedResult.task as { title?: string };
        return `Updated task: ${task.title || 'Untitled'}`;
      }
      return 'Task updated';

    case 'filter_tasks':
      if (isListTasksResult(result)) {
        const count = result.tasks.length;
        const total = result.total || count;
        return `Filtered results: ${count} of ${total} tasks`;
      }
      return 'Tasks filtered';

    default:
      return isSuccess ? 'Completed' : 'Failed';
  }
}

/**
 * Check if result contains task list data
 */
function hasTaskList(toolName: string, result: unknown): boolean {
  return (toolName === 'list_tasks' || toolName === 'filter_tasks') && isListTasksResult(result);
}

export function ToolCallBadge({ toolCall }: ToolCallBadgeProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const isSuccess = isToolSuccess(toolCall.result);
  const summary = getToolSummary(toolCall.tool_name, toolCall.result);
  const colors = getBadgeColors(toolCall.tool_name);
  const icon = getToolIcon(toolCall.tool_name);
  const displayName = formatToolName(toolCall.tool_name);
  const showTaskList = hasTaskList(toolCall.tool_name, toolCall.result);

  return (
    <div className={`inline-block rounded-xl border-2 ${colors} overflow-hidden shadow-sm hover:shadow-md transition-all duration-300`}>
      {/* Main Badge */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold hover:opacity-90 transition-all duration-200 group"
      >
        {/* Tool Icon */}
        <span className="group-hover:scale-110 transition-transform duration-200">
          {icon}
        </span>

        {/* Tool Name */}
        <span className="tracking-wide">{displayName}</span>

        {/* Success/Failure Icon */}
        {isSuccess ? (
          <CheckCircle className="w-3.5 h-3.5 group-hover:rotate-12 transition-transform duration-200" />
        ) : (
          <XCircle className="w-3.5 h-3.5 group-hover:shake transition-transform duration-200" />
        )}

        {/* Expand/Collapse Icon */}
        <span className="ml-auto">
          {isExpanded ? (
            <ChevronDown className="w-3.5 h-3.5 group-hover:translate-y-0.5 transition-transform duration-200" />
          ) : (
            <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform duration-200" />
          )}
        </span>
      </button>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="px-3.5 py-3 text-xs border-t-2 border-current/20 bg-white/60 dark:bg-black/30 backdrop-blur-sm animate-slide-down">
          <div className="font-bold mb-2 uppercase tracking-wider text-[10px] opacity-70">Result:</div>
          <div className="opacity-90 leading-relaxed">{summary}</div>

          {/* Render TaskList for list_tasks results */}
          {showTaskList && isListTasksResult(toolCall.result) && (
            <div className="mt-4 pt-4 border-t-2 border-current/20">
              <TaskList tasks={toolCall.result.tasks} total={toolCall.result.total} />
            </div>
          )}

          {/* Dev mode: raw data */}
          {process.env.NODE_ENV === 'development' && toolCall.result && !showTaskList ? (
            <details className="mt-3">
              <summary className="cursor-pointer hover:underline font-semibold text-[10px] uppercase tracking-wider opacity-60">
                Raw data (dev only)
              </summary>
              <pre className="mt-2 text-[10px] overflow-x-auto bg-black/10 dark:bg-white/10 rounded-lg p-2.5 leading-relaxed">
                {JSON.stringify(toolCall.result, null, 2)}
              </pre>
            </details>
          ) : null}
        </div>
      )}
    </div>
  );
}
