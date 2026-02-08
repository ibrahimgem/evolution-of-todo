'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useAuth } from '../../context/AuthContext';
import { apiClient, TaskRead, TaskPriority } from '../../lib/api-client';

// Sort options
type SortField = 'created_at' | 'priority' | 'category' | 'title';
type SortDirection = 'asc' | 'desc';

const SORT_OPTIONS: { value: SortField; label: string }[] = [
  { value: 'created_at', label: 'Date Created' },
  { value: 'priority', label: 'Priority' },
  { value: 'category', label: 'Category' },
  { value: 'title', label: 'Title' },
];

const PRIORITY_ORDER: Record<TaskPriority, number> = {
  high: 3,
  medium: 2,
  low: 1,
};
import TaskForm from '../../components/tasks/TaskForm';
import TaskListView from '../../components/tasks/TaskListView';
import {
  CheckSquare,
  Plus,
  Loader2,
  MessageSquare,
  X,
  AlertCircle,
  LogOut,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
} from 'lucide-react';
import Link from 'next/link';

/**
 * Tasks Page - Traditional task management interface
 * Provides CRUD operations for tasks with a clean, modern UI
 */
export default function TasksPage() {
  const { token, isAuthenticated, isLoading: authLoading, user, logout } = useAuth();
  const [tasks, setTasks] = useState<TaskRead[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<TaskRead | null>(null);
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  /**
   * Load all tasks for the current user
   */
  // Get numeric user ID (AuthContext stores it as string)
  const userId = user?.id ? parseInt(user.id, 10) : null;

  const loadTasks = useCallback(async () => {
    if (!userId) return;

    setIsLoading(true);
    setError(null);
    try {
      const fetchedTasks = await apiClient.getTasks(userId);
      setTasks(fetchedTasks);
    } catch (err) {
      console.error('Failed to load tasks:', err);
      setError('Failed to load tasks. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  /**
   * Load tasks when component mounts
   */
  useEffect(() => {
    if (token && isAuthenticated && user) {
      apiClient.setToken(token);
      loadTasks();
    }
  }, [token, isAuthenticated, user, loadTasks]);

  /**
   * Sort tasks based on current sort field and direction
   */
  const sortedTasks = useMemo(() => {
    const sorted = [...tasks].sort((a, b) => {
      let comparison = 0;

      switch (sortField) {
        case 'priority':
          const priorityA = PRIORITY_ORDER[a.priority] || 0;
          const priorityB = PRIORITY_ORDER[b.priority] || 0;
          comparison = priorityA - priorityB;
          break;
        case 'category':
          const catA = a.category || '';
          const catB = b.category || '';
          comparison = catA.localeCompare(catB);
          break;
        case 'title':
          comparison = a.title.localeCompare(b.title);
          break;
        case 'created_at':
        default:
          comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
          break;
      }

      return sortDirection === 'asc' ? comparison : -comparison;
    });

    return sorted;
  }, [tasks, sortField, sortDirection]);

  /**
   * Toggle sort direction or change sort field
   */
  const handleSortChange = (field: SortField) => {
    if (field === sortField) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection(field === 'priority' ? 'desc' : 'asc');
    }
  };

  /**
   * Create a new task
   */
  const handleCreateTask = async (taskData: { title: string; description?: string; priority?: string; category?: string }) => {
    if (!userId) return;

    setError(null);
    try {
      await apiClient.createTask(userId, taskData);
      await loadTasks();
      setShowForm(false);
    } catch (err) {
      console.error('Failed to create task:', err);
      setError('Failed to create task. Please try again.');
    }
  };

  /**
   * Update an existing task
   */
  const handleUpdateTask = async (taskData: { title: string; description?: string; priority?: string; category?: string }) => {
    if (!userId || !editingTask) return;

    setError(null);
    try {
      await apiClient.updateTask(userId, editingTask.id, taskData);
      await loadTasks();
      setEditingTask(null);
    } catch (err) {
      console.error('Failed to update task:', err);
      setError('Failed to update task. Please try again.');
    }
  };

  /**
   * Toggle task completion status
   */
  const handleToggleComplete = async (task: TaskRead) => {
    if (!userId) return;

    setError(null);
    try {
      await apiClient.toggleTaskComplete(userId, task.id);
      await loadTasks();
    } catch (err) {
      console.error('Failed to toggle task:', err);
      setError('Failed to update task. Please try again.');
    }
  };

  /**
   * Delete a task
   */
  const handleDeleteTask = async (task: TaskRead) => {
    if (!userId) return;
    if (!confirm('Are you sure you want to delete this task?')) return;

    setError(null);
    try {
      await apiClient.deleteTask(userId, task.id);
      await loadTasks();
    } catch (err) {
      console.error('Failed to delete task:', err);
      setError('Failed to delete task. Please try again.');
    }
  };

  /**
   * Start editing a task
   */
  const handleEditTask = (task: TaskRead) => {
    setEditingTask(task);
    setShowForm(false);
  };

  /**
   * Cancel form/editing
   */
  const handleCancelForm = () => {
    setShowForm(false);
    setEditingTask(null);
    setError(null);
  };

  /**
   * Handle logout
   */
  const handleLogout = () => {
    logout();
  };

  /**
   * Show loading state while auth initializes
   */
  if (authLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  /**
   * Redirect to login if not authenticated
   */
  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50 dark:bg-gray-900">
        <div className="text-center max-w-md px-4">
          <CheckSquare className="w-16 h-16 mx-auto mb-4 text-gray-400" />
          <h2 className="text-2xl font-semibold mb-2 text-gray-900 dark:text-white">
            Authentication Required
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Please log in to manage your tasks.
          </p>
          <a
            href="/auth"
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
          >
            Go to Login
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-slate-900 dark:to-purple-900">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -right-1/2 w-full h-full bg-gradient-to-br from-blue-400/20 to-purple-400/20 dark:from-blue-600/10 dark:to-purple-600/10 rounded-full blur-3xl animate-pulse" />
        <div
          className="absolute -bottom-1/2 -left-1/2 w-full h-full bg-gradient-to-tr from-purple-400/20 to-pink-400/20 dark:from-purple-600/10 dark:to-pink-600/10 rounded-full blur-3xl animate-pulse"
          style={{ animationDelay: '1s' }}
        />
      </div>

      {/* Header */}
      <header className="relative z-10 bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
                <CheckSquare className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Task Manager</h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Organize your work efficiently
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Link
                href="/chat"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors shadow-sm"
              >
                <MessageSquare className="w-5 h-5" />
                <span className="hidden sm:inline">AI Chat</span>
              </Link>
              <button
                onClick={handleLogout}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Logout"
              >
                <LogOut className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Display */}
        {error && (
          <div className="mb-6 animate-fade-in" role="alert">
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
              <p className="text-sm text-red-800 dark:text-red-200 flex-1">{error}</p>
              <button
                onClick={() => setError(null)}
                className="text-red-800/50 hover:text-red-800"
                aria-label="Dismiss error"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Create Task Button / Form */}
        {!showForm && !editingTask && (
          <div className="mb-8 animate-slide-up">
            <button
              onClick={() => setShowForm(true)}
              className="w-full p-6 rounded-2xl bg-white/60 dark:bg-gray-800/60 backdrop-blur-lg border-2 border-dashed border-gray-300 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-500 transition-all duration-300 group hover:shadow-xl"
            >
              <div className="flex items-center justify-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                  <Plus className="w-6 h-6 text-white" />
                </div>
                <span className="text-lg font-semibold text-gray-700 dark:text-gray-300 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                  Create New Task
                </span>
              </div>
            </button>
          </div>
        )}

        {/* Task Form (Create or Edit) */}
        {(showForm || editingTask) && (
          <div className="mb-8 p-6 rounded-2xl bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg border border-gray-200 dark:border-gray-700 shadow-xl animate-slide-up">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                {editingTask ? (
                  <>
                    <CheckSquare className="w-6 h-6 text-blue-600" />
                    Edit Task
                  </>
                ) : (
                  <>
                    <Plus className="w-6 h-6 text-blue-600" />
                    New Task
                  </>
                )}
              </h2>
              <button
                onClick={handleCancelForm}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
                aria-label="Cancel"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <TaskForm
              onSubmit={editingTask ? handleUpdateTask : handleCreateTask}
              initialData={editingTask || undefined}
              submitText={editingTask ? 'Update Task' : 'Create Task'}
              onCancel={handleCancelForm}
              showCancel={true}
            />
          </div>
        )}

        {/* Task List */}
        <div className="rounded-2xl bg-white/60 dark:bg-gray-800/60 backdrop-blur-lg border border-gray-200 dark:border-gray-700 shadow-lg p-6">
          {/* Sorting Controls */}
          {tasks.length > 0 && (
            <div className="mb-6 flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <ArrowUpDown className="w-4 h-4" />
                <span className="font-medium">Sort by:</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {SORT_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleSortChange(option.value)}
                    className={`
                      inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200
                      ${sortField === option.value
                        ? 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 border-2 border-blue-300 dark:border-blue-700'
                        : 'bg-gray-100 dark:bg-gray-700/50 text-gray-600 dark:text-gray-400 border-2 border-transparent hover:bg-gray-200 dark:hover:bg-gray-700'
                      }
                    `}
                  >
                    {option.label}
                    {sortField === option.value && (
                      sortDirection === 'asc' ? (
                        <ArrowUp className="w-3.5 h-3.5" />
                      ) : (
                        <ArrowDown className="w-3.5 h-3.5" />
                      )
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}

          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20" role="status">
              <Loader2 className="w-10 h-10 animate-spin text-blue-600 mb-4" />
              <p className="text-gray-500 font-medium">Loading your tasks...</p>
            </div>
          ) : (
            <TaskListView
              tasks={sortedTasks}
              onToggleComplete={handleToggleComplete}
              onEdit={handleEditTask}
              onDelete={handleDeleteTask}
            />
          )}
        </div>
      </main>
    </div>
  );
}
