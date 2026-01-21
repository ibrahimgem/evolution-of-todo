'use client';

import React, { useState } from 'react';
import Button from '../ui/Button';
import type { TaskRead } from '../../lib/api-client';

interface TaskItemProps {
  task: TaskRead;
  onToggleComplete: (task: TaskRead) => void;
  onEdit: (task: TaskRead) => void;
  onDelete: (task: TaskRead) => void;
}

const TaskItem: React.FC<TaskItemProps> = ({ task, onToggleComplete, onEdit, onDelete }) => {
  const [isDeleting, setIsDeleting] = useState(false);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) {
      return 'Today';
    } else if (days === 1) {
      return 'Yesterday';
    } else if (days < 7) {
      return `${days} days ago`;
    } else {
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      });
    }
  };

  const handleToggleComplete = () => {
    onToggleComplete(task);
  };

  const handleEdit = () => {
    onEdit(task);
  };

  const handleDelete = () => {
    setIsDeleting(true);
    setTimeout(() => {
      onDelete(task);
    }, 200);
  };

  return (
    <div
      className={`
        group relative overflow-hidden rounded-3xl border-2 transition-all duration-500 ease-out
        hover:shadow-xl hover:shadow-gray-200/40 dark:hover:shadow-gray-900/40 hover:-translate-y-1 hover:scale-[1.01]
        ${
          isDeleting
            ? 'opacity-0 translate-y-4'
            : task.completed
            ? 'bg-gradient-to-br from-gray-50/80 to-gray-100/60 dark:from-gray-800/60 dark:to-gray-900/40 border-gray-200/60 dark:border-gray-700/50 opacity-90'
            : 'bg-gradient-to-br from-white/90 to-gray-50/90 dark:from-gray-800/90 dark:to-gray-900/90 border-gray-200/70 dark:border-gray-700/60 shadow-lg shadow-gray-200/30 dark:shadow-gray-900/30'
        }
      `}
    >
      {/* Animated gradient border on hover */}
      <div
        className={`absolute inset-0 rounded-3xl bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-blue-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300`}
      />

      {/* Decorative shimmer effect */}
      <div
        className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-500/5 via-purple-500/5 to-blue-500/5 rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500`}
      />

      <div className="relative p-6">
        <div className="flex items-start gap-4">
          {/* Premium Custom Checkbox */}
          <div className="relative flex-shrink-0 flex items-center justify-center w-9 h-9">
            <input
              type="checkbox"
              checked={task.completed}
              onChange={handleToggleComplete}
              className={`
                peer w-8 h-8 rounded-xl border-2 cursor-pointer appearance-none
                transition-all duration-300 ease-out
                ${
                  task.completed
                    ? 'bg-gradient-to-br from-green-500 to-emerald-600 border-green-500 shadow-lg shadow-green-500/30'
                    : 'border-gray-300 dark:border-gray-600 hover:border-blue-400 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-650 shadow-sm'
                }
              `}
            />
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <svg
                className={`
                  w-5 h-5 text-white
                  transition-all duration-300
                  ${task.completed ? 'opacity-100 scale-110' : 'opacity-0 scale-75'}
                `}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={3.5}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
          </div>

          {/* Task Content */}
          <div className="flex-1 min-w-0">
            <h3
              className={`
                text-xl font-bold tracking-tight transition-all duration-300 ease-out
                ${
                  task.completed
                    ? 'text-gray-400 dark:text-gray-500 line-through opacity-80'
                    : 'text-gray-900 dark:text-white'
                }
              `}
            >
              {task.title}
            </h3>
            {task.description && (
              <p
                className={`
                  mt-2.5 text-base leading-relaxed transition-all duration-300 ease-out
                  ${
                    task.completed
                      ? 'text-gray-400 dark:text-gray-500 line-through opacity-80'
                      : 'text-gray-600 dark:text-gray-400'
                  }
                `}
              >
                {task.description}
              </p>
            )}

            {/* Meta info with premium styling */}
            <div className="mt-4 flex items-center gap-4">
              <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-gradient-to-br from-gray-100 to-gray-50 dark:from-gray-700/50 dark:to-gray-800/50 border border-gray-200/60 dark:border-gray-700/50 text-xs font-medium text-gray-500 dark:text-gray-400 shadow-sm">
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                {formatDate(task.created_at)}
              </span>

              {task.updated_at !== task.created_at && (
                <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-gradient-to-br from-blue-50 to-blue-100/50 dark:from-blue-900/20 dark:to-blue-800/20 border border-blue-200/60 dark:border-blue-700/50 text-xs font-medium text-blue-600 dark:text-blue-400 shadow-sm">
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                    />
                  </svg>
                  Updated
                </span>
              )}

              {task.completed && (
                <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200/60 dark:border-green-800/50 text-xs font-semibold text-green-700 dark:text-green-400 shadow-sm shadow-green-500/20">
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Completed
                </span>
              )}
            </div>
          </div>

          {/* Actions - Premium Hover Reveal */}
          <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-all duration-300 translate-x-2 group-hover:translate-x-0">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleEdit}
              className="!bg-transparent !border-1.5 !border-gray-200/60 dark:!border-gray-700/60 !text-gray-500 hover:!bg-blue-50 hover:!text-blue-600 hover:!border-blue-300 dark:hover:!bg-blue-900/20 dark:hover:!text-blue-400 dark:hover:!border-blue-700/50 hover:shadow-lg hover:shadow-blue-500/20 transition-all duration-200 hover:-translate-y-0.5"
              icon={
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
              }
            >
              Edit
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDelete}
              className="!bg-transparent !border-1.5 !border-gray-200/60 dark:!border-gray-700/60 !text-gray-500 hover:!bg-red-50 hover:!text-red-600 hover:!border-red-300 dark:hover:!bg-red-900/20 dark:hover:!text-red-400 dark:hover:!border-red-700/50 hover:shadow-lg hover:shadow-red-500/20 transition-all duration-200 hover:-translate-y-0.5"
              icon={
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              }
            >
              Delete
            </Button>
          </div>
        </div>
      </div>

      {/* Bottom highlight bar */}
      <div
        className={`absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-blue-500 transition-all duration-300 ${
          task.completed ? 'opacity-0' : 'opacity-0 group-hover:opacity-100'
        }`}
      />
    </div>
  );
};

export default TaskItem;
