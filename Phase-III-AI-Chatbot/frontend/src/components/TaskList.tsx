'use client';

import { CheckCircle, Circle, Calendar, FileText, Clock, Sparkles } from 'lucide-react';

/**
 * TaskList Component - Enhanced with stunning visuals
 *
 * Features:
 * - Modern card design with gradients
 * - Enhanced visual hierarchy
 * - Smooth animations
 * - Better status indicators
 * - Beautiful empty states
 */

/**
 * Task interface matching MCP tool output schema
 */
export interface Task {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  due_date: string | null;
  created_at: string;
  updated_at: string;
}

interface TaskListProps {
  tasks: Task[];
  total?: number;
}

/**
 * Format date for display with relative time
 */
function formatDate(dateStr: string): { display: string; isOverdue: boolean; isDueSoon: boolean } {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = date.getTime() - now.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

  const isOverdue = diffMs < 0;
  const isDueSoon = diffHours > 0 && diffHours <= 24;

  // Format for display
  const dateDisplay = date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
  });

  const timeDisplay = date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });

  if (isOverdue) {
    if (Math.abs(diffDays) === 0) {
      return { display: `Overdue (today at ${timeDisplay})`, isOverdue, isDueSoon: false };
    } else if (Math.abs(diffDays) === 1) {
      return { display: `Overdue (yesterday)`, isOverdue, isDueSoon: false };
    } else {
      return { display: `Overdue (${Math.abs(diffDays)} days ago)`, isOverdue, isDueSoon: false };
    }
  }

  if (diffDays === 0) {
    return { display: `Today at ${timeDisplay}`, isOverdue: false, isDueSoon };
  } else if (diffDays === 1) {
    return { display: `Tomorrow at ${timeDisplay}`, isOverdue: false, isDueSoon };
  } else if (diffDays <= 7) {
    const dayName = date.toLocaleDateString('en-US', { weekday: 'long' });
    return { display: `${dayName} at ${timeDisplay}`, isOverdue: false, isDueSoon };
  } else {
    return { display: `${dateDisplay} at ${timeDisplay}`, isOverdue: false, isDueSoon: false };
  }
}

/**
 * Individual task card component
 */
function TaskCard({ task, index }: { task: Task; index: number }) {
  const dueDateInfo = task.due_date ? formatDate(task.due_date) : null;

  return (
    <div
      className={`group border-2 rounded-xl p-5 transition-all duration-300 hover-lift animate-slide-up ${
        task.completed
          ? 'bg-gradient-to-br from-gray-50 to-slate-100 dark:from-gray-800/50 dark:to-slate-800/50 border-gray-300 dark:border-gray-700 opacity-75 hover:opacity-90'
          : 'bg-gradient-to-br from-white to-blue-50/30 dark:from-gray-800 dark:to-blue-900/10 border-blue-200/50 dark:border-blue-700/30 hover:border-blue-300 dark:hover:border-blue-600 shadow-sm'
      }`}
      style={{ animationDelay: `${index * 50}ms` }}
    >
      <div className="flex items-start gap-4 mb-3">
        {/* Status Icon */}
        <div className="flex-shrink-0 mt-1">
          {task.completed ? (
            <div className="relative">
              <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
              <div className="absolute inset-0 blur-lg bg-green-500/30 animate-pulse-slow" />
            </div>
          ) : (
            <Circle className="w-6 h-6 text-blue-500 dark:text-blue-400 group-hover:scale-110 transition-transform duration-300" />
          )}
        </div>

        {/* Title and ID */}
        <div className="flex-1 min-w-0">
          <h3
            className={`font-bold text-base mb-1 ${
              task.completed
                ? 'line-through text-gray-600 dark:text-gray-400'
                : 'text-gray-900 dark:text-white group-hover:text-blue-900 dark:group-hover:text-blue-100'
            }`}
          >
            {task.title}
          </h3>
          <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-[10px] font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
            <span className="w-1 h-1 rounded-full bg-gray-400" />
            ID {task.id}
          </div>
        </div>

        {/* Completion Badge */}
        <div
          className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-bold shadow-sm ${
            task.completed
              ? 'bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 text-green-800 dark:text-green-200 ring-2 ring-green-300/50 dark:ring-green-700/50'
              : 'bg-gradient-to-r from-blue-100 to-cyan-100 dark:from-blue-900/30 dark:to-cyan-900/30 text-blue-800 dark:text-blue-200 ring-2 ring-blue-300/50 dark:ring-blue-700/50'
          }`}
        >
          {task.completed ? 'Complete' : 'Active'}
        </div>
      </div>

      {/* Description */}
      {task.description && (
        <div className="flex items-start gap-3 mb-3 ml-10 p-3 rounded-lg bg-white/60 dark:bg-gray-700/30 border border-gray-200/50 dark:border-gray-600/50">
          <FileText className="w-4 h-4 text-blue-500 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
            {task.description}
          </p>
        </div>
      )}

      {/* Due Date */}
      {dueDateInfo && (
        <div className="flex items-center gap-2 ml-10 mt-3">
          <Calendar
            className={`w-4 h-4 flex-shrink-0 ${
              dueDateInfo.isOverdue
                ? 'text-red-500 dark:text-red-400'
                : dueDateInfo.isDueSoon
                ? 'text-yellow-500 dark:text-yellow-400'
                : 'text-blue-500 dark:text-blue-400'
            }`}
          />
          <span
            className={`text-xs font-semibold px-2 py-1 rounded-full ${
              dueDateInfo.isOverdue
                ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
                : dueDateInfo.isDueSoon
                ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300'
                : 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
            }`}
          >
            {dueDateInfo.display}
          </span>
        </div>
      )}

      {/* Created At (small timestamp) */}
      <div className="flex items-center gap-2 ml-10 mt-3 text-xs text-gray-400 dark:text-gray-500">
        <Clock className="w-3 h-3" />
        <span>
          Created {new Date(task.created_at).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
          })}
        </span>
      </div>
    </div>
  );
}

/**
 * Main TaskList component
 */
export function TaskList({ tasks, total }: TaskListProps) {
  // Empty state
  if (!tasks || tasks.length === 0) {
    return (
      <div className="text-center py-12 px-4 animate-fade-in">
        <div className="relative inline-block mb-4">
          <Circle className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600" />
          <div className="absolute inset-0 blur-2xl bg-blue-400/20 dark:bg-blue-600/20 animate-pulse-slow" />
        </div>
        <p className="text-base font-semibold text-gray-600 dark:text-gray-400 mb-2">No tasks found</p>
        <p className="text-sm text-gray-500 dark:text-gray-500">Create your first task to get started</p>
      </div>
    );
  }

  // Separate completed and incomplete tasks
  const incompleteTasks = tasks.filter((t) => !t.completed);
  const completedTasks = tasks.filter((t) => t.completed);

  return (
    <div className="space-y-6">
      {/* Summary Header */}
      <div className="flex items-center justify-between px-1 pb-4 border-b-2 border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Sparkles className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            <div className="absolute inset-0 blur-xl bg-blue-500/30 animate-pulse-slow" />
          </div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-white">
            Your Tasks {total !== undefined && <span className="text-blue-600 dark:text-blue-400">({total})</span>}
          </h3>
        </div>
        <div className="flex items-center gap-4 text-xs font-semibold">
          <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200">
            <Circle className="w-3 h-3" />
            {incompleteTasks.length} active
          </span>
          <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200">
            <CheckCircle className="w-3 h-3" />
            {completedTasks.length} done
          </span>
        </div>
      </div>

      {/* Incomplete Tasks */}
      {incompleteTasks.length > 0 && (
        <div className="space-y-3">
          {incompleteTasks.map((task, index) => (
            <TaskCard key={task.id} task={task} index={index} />
          ))}
        </div>
      )}

      {/* Completed Tasks */}
      {completedTasks.length > 0 && (
        <div className="space-y-3 mt-8">
          {incompleteTasks.length > 0 && (
            <div className="flex items-center gap-3 px-1 mb-4">
              <div className="h-0.5 flex-1 bg-gradient-to-r from-transparent via-gray-300 dark:via-gray-600 to-transparent"></div>
              <span className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider px-3 py-1 rounded-full bg-gray-100 dark:bg-gray-800">
                Completed
              </span>
              <div className="h-0.5 flex-1 bg-gradient-to-r from-transparent via-gray-300 dark:via-gray-600 to-transparent"></div>
            </div>
          )}
          {completedTasks.map((task, index) => (
            <TaskCard key={task.id} task={task} index={index} />
          ))}
        </div>
      )}
    </div>
  );
}
