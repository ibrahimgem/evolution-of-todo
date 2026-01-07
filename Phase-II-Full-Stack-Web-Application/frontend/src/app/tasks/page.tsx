'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import TaskList from '../../components/tasks/TaskList';
import Button from '../../components/ui/Button';
import Modal from '../../components/ui/Modal';
import ThemeToggle from '../../components/ui/ThemeToggle';
import TaskForm from '../../components/tasks/TaskForm';
import { tasksAPI, TaskRead, ApiRequestError } from '../../lib/api';
import { isAuthenticated, removeAuthToken, getCurrentUserId } from '../../lib/auth';

const TasksPage = () => {
  const [tasks, setTasks] = useState<TaskRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [userId, setUserId] = useState<number | null>(null);
  const router = useRouter();

  // Check authentication after component mounts
  useEffect(() => {
    const checkAuth = () => {
      if (!isAuthenticated()) {
        router.push('/login');
        return;
      }
      const currentUserId = getCurrentUserId();
      setUserId(currentUserId);
      setIsCheckingAuth(false);
    };
    checkAuth();
  }, [router]);

  useEffect(() => {
    if (isCheckingAuth || !userId) {
      return;
    }

    const controller = new AbortController();
    const fetchTasks = async () => {
      try {
        const data = await tasksAPI.getAll(userId, controller.signal);
        setTasks(data);
        setError('');
      } catch (err: any) {
        if (err.name === 'AbortError') return;

        console.error('Error fetching tasks:', err);
        if (err instanceof ApiRequestError) {
          setError(err.data.message || 'Failed to load tasks.');
        } else {
          setError('An unexpected error occurred. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
    return () => controller.abort();
  }, [userId, isCheckingAuth]);

  if (isCheckingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="relative">
          <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
          <div className="absolute inset-0 w-12 h-12 border-4 border-transparent border-t-primary-400 rounded-full animate-spin-slow opacity-50" />
        </div>
      </div>
    );
  }

  const handleToggleComplete = async (task: TaskRead) => {
    if (!userId) return;

    try {
      const updatedTask = await tasksAPI.toggleComplete(userId, task.id);
      setTasks(tasks.map(t => t.id === task.id ? updatedTask : t));
    } catch (err: any) {
      console.error('Error toggling task completion:', err);
      if (err instanceof ApiRequestError) {
        setError(err.data.message);
      } else {
        setError('Failed to update task.');
      }
    }
  };

  const handleEdit = (task: TaskRead) => {
    router.push(`/tasks/${task.id}/edit`);
  };

  const handleDelete = async (task: TaskRead) => {
    if (!userId) return;

    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      await tasksAPI.delete(userId, task.id);
      setTasks(tasks.filter(t => t.id !== task.id));
    } catch (err: any) {
      console.error('Error deleting task:', err);
      if (err instanceof ApiRequestError) {
        setError(err.data.message);
      } else {
        setError('Failed to delete task.');
      }
    }
  };

  const handleCreateTask = async (taskData: { title: string; description?: string }) => {
    if (!userId) return;

    try {
      const newTask = await tasksAPI.create(userId, taskData);
      setTasks([newTask, ...tasks]);
      setShowCreateModal(false);
      setError('');
    } catch (err: any) {
      console.error('Error creating task:', err);
      if (err instanceof ApiRequestError) {
        setError(err.data.message);
      } else {
        setError('Failed to create task.');
      }
    }
  };

  const handleLogout = () => {
    removeAuthToken();
    router.push('/login');
  };

  const completedCount = tasks.filter(t => t.completed).length;
  const pendingCount = tasks.length - completedCount;
  const progressPercentage = tasks.length > 0 ? Math.round((completedCount / tasks.length) * 100) : 0;

  if (loading) {
    return (
      <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto mb-12 animate-slideDown">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <div className="h-12 w-64 bg-gradient-to-r from-gray-200 to-gray-100 rounded-2xl skeleton animate-shimmer-slow mb-3" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      <div className="relative z-10 py-10 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          {/* Header Section */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-12 gap-6 animate-slideDown">
            <div className="flex-1">
              <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white tracking-tight mb-3 gradient-text">
                My Tasks
              </h1>
              <p className="text-base text-gray-600 dark:text-gray-400 leading-relaxed max-w-lg">
                {tasks.length > 0
                  ? `You have ${pendingCount} pending task${pendingCount !== 1 ? 's' : ''} remaining.`
                  : 'Ready to be productive? Create your first task.'
                }
              </p>
            </div>

            <div className="flex items-center gap-3 flex-wrap">
              <ThemeToggle />
              <Button variant="ghost" size="md" onClick={() => setShowCreateModal(true)}>
                Create Task
              </Button>
              <Button variant="secondary" size="md" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mb-8 p-5 bg-gradient-to-br from-rose-50 to-rose-100 dark:from-rose-900/30 dark:to-rose-950/20 backdrop-blur-sm border border-rose-200 dark:border-rose-800 rounded-2xl text-rose-700 dark:text-rose-300 animate-slideDown shadow-lg">
              <div className="flex items-start gap-3">
                <div className="flex-1">
                  <p className="font-semibold mb-1">Error</p>
                  <p className="text-sm opacity-90">{error}</p>
                </div>
                <button onClick={() => setError('')} className="flex-shrink-0 p-1">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          )}

          {/* Task List Card */}
          <div className="relative p-8 rounded-3xl bg-white/95 dark:bg-gray-800/95 backdrop-blur-3xl shadow-2xl border border-gray-200 dark:border-gray-700">
            <TaskList
              tasks={tasks}
              onToggleComplete={handleToggleComplete}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          </div>
        </div>
      </div>

      <Modal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} title="Create New Task">
        <TaskForm onSubmit={handleCreateTask} submitText="Create Task" showCancel onCancel={() => setShowCreateModal(false)} />
      </Modal>
    </div>
  );
};

export default TasksPage;
