'use client';

import React from 'react';
import TaskItem from './TaskItem';
import type { TaskRead } from '../../lib/api-client';

interface TaskListViewProps {
  tasks: TaskRead[];
  onToggleComplete: (task: TaskRead) => void;
  onEdit: (task: TaskRead) => void;
  onDelete: (task: TaskRead) => void;
}

const TaskListView: React.FC<TaskListViewProps> = ({
  tasks,
  onToggleComplete,
  onEdit,
  onDelete,
}) => {
  if (tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 px-6 animate-fade-in">
        {/* Floating animation container */}
        <div className="relative mb-8">
          {/* Glowing background orb */}
          <div className="absolute inset-0 w-32 h-32 bg-gradient-to-br from-blue-500/20 via-purple-500/20 to-blue-500/20 rounded-full blur-2xl animate-pulse" />

          {/* Icon container with gradient */}
          <div className="relative w-28 h-28 rounded-3xl bg-gradient-to-br from-blue-500 via-purple-500 to-blue-600 flex items-center justify-center shadow-2xl shadow-blue-500/40 animate-float">
            <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-white/20 to-transparent" />
            <svg
              className="w-14 h-14 text-white relative z-10"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
              />
            </svg>
          </div>

          {/* Decorative floating elements */}
          <div className="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-lg shadow-lg animate-float opacity-80" />
          <div
            className="absolute -bottom-2 -left-2 w-5 h-5 bg-gradient-to-br from-amber-400 to-orange-500 rounded-lg shadow-lg animate-float opacity-80"
            style={{ animationDelay: '0.5s' }}
          />
        </div>

        <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-3 text-center bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          No tasks yet
        </h3>
        <p className="text-gray-500 dark:text-gray-400 text-center max-w-sm leading-relaxed mb-6">
          Your task list is empty. Create your first task to start organizing your day and boost
          your productivity!
        </p>

        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-blue-50 via-purple-50 to-blue-50 dark:from-blue-900/30 dark:via-purple-900/30 dark:to-blue-900/30 border border-blue-200/60 dark:border-blue-700/50 shadow-sm">
          <svg
            className="w-5 h-5 text-blue-600 dark:text-blue-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
            Add your first task above
          </span>
        </div>
      </div>
    );
  }

  // Separate completed and pending tasks
  const pendingTasks = tasks.filter((t) => !t.completed);
  const completedTasks = tasks.filter((t) => t.completed);

  return (
    <div className="space-y-8">
      {/* Pending Tasks Section */}
      {pendingTasks.length > 0 && (
        <div className="animate-fade-in">
          <div className="flex items-center gap-3 mb-5">
            <div className="relative">
              <div className="w-3 h-3 rounded-full bg-gradient-to-r from-blue-500 to-blue-600 shadow-lg shadow-blue-500/50" />
              <div className="absolute inset-0 w-3 h-3 rounded-full bg-gradient-to-r from-blue-500 to-blue-600 animate-pulse opacity-60" />
            </div>
            <h3 className="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
              Pending Tasks
            </h3>
            <span className="px-2.5 py-0.5 rounded-full bg-gradient-to-br from-blue-100 to-blue-50 dark:from-blue-900/40 dark:to-blue-950/30 border border-blue-200/60 dark:border-blue-700/50 text-xs font-semibold text-blue-700 dark:text-blue-300">
              {pendingTasks.length}
            </span>
          </div>
          <div className="space-y-4">
            {pendingTasks.map((task, index) => (
              <div
                key={task.id}
                className="animate-slide-up"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <TaskItem
                  task={task}
                  onToggleComplete={onToggleComplete}
                  onEdit={onEdit}
                  onDelete={onDelete}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Completed Tasks Section */}
      {completedTasks.length > 0 && (
        <div className="animate-fade-in">
          <div className="flex items-center gap-3 mb-5">
            <div className="relative">
              <div className="w-3 h-3 rounded-full bg-gradient-to-r from-green-500 to-emerald-600 shadow-lg shadow-green-500/50" />
              <div className="absolute inset-0 w-3 h-3 rounded-full bg-gradient-to-r from-green-500 to-emerald-600 animate-pulse opacity-60" />
            </div>
            <h3 className="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
              Completed Tasks
            </h3>
            <span className="px-2.5 py-0.5 rounded-full bg-gradient-to-br from-green-100 to-emerald-50 dark:from-green-900/40 dark:to-emerald-950/30 border border-green-200/60 dark:border-green-700/50 text-xs font-semibold text-green-700 dark:text-green-300">
              {completedTasks.length}
            </span>
          </div>
          <div className="space-y-4">
            {completedTasks.map((task, index) => (
              <div
                key={task.id}
                className="animate-slide-up"
                style={{ animationDelay: `${(pendingTasks.length + index) * 50}ms` }}
              >
                <TaskItem
                  task={task}
                  onToggleComplete={onToggleComplete}
                  onEdit={onEdit}
                  onDelete={onDelete}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TaskListView;
