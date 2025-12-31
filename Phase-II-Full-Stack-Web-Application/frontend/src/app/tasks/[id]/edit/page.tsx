'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import TaskForm from '../../../../components/tasks/TaskForm';
import Button from '../../../../components/ui/Button';
import ThemeToggle from '../../../../components/ui/ThemeToggle';
import { tasksAPI } from '../../../../lib/api';
import { isAuthenticated, getCurrentUserId } from '../../../../lib/auth';

// Define TaskRead type locally since it's not exported
interface TaskRead {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at?: string;
}

const EditTaskPage = () => {
  const [task, setTask] = useState<TaskRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();
  const { id } = useParams();
  const userId = getCurrentUserId();

  // Redirect to login if not authenticated
  if (!isAuthenticated()) {
    router.push('/login');
    return null; // Render nothing while redirecting
  }

  useEffect(() => {
    if (!userId || !id) {
      setError('User not authenticated or invalid task ID');
      setLoading(false);
      return;
    }

    const fetchTask = async () => {
      try {
        // Note: For the actual API, we need to get the specific task
        // For now, we'll get all tasks and find the one with the matching ID
        const allTasks = await tasksAPI.getAll(userId);
        const foundTask = allTasks.find(t => t.id === parseInt(id as string));

        if (!foundTask) {
          setError('Task not found');
          return;
        }

        setTask(foundTask);
      } catch (err: any) {
        console.error('Error fetching task:', err);
        setError(err.message || 'Failed to load task. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
  }, [id, userId]);

  const handleSubmit = async (taskData: { title: string; description?: string }) => {
    if (!userId || !task) return;

    try {
      const updatedTask = await tasksAPI.update(userId, task.id, {
        ...taskData,
        completed: task.completed // Keep the completion status
      });

      // Redirect to tasks list
      router.push('/tasks');
      router.refresh();
    } catch (err: any) {
      console.error('Error updating task:', err);
      setError(err.message || 'Failed to update task. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
        <div className="relative max-w-2xl mx-auto">
          <div className="animate-slideDown">
            <div className="h-8 w-48 bg-gray-200 dark:bg-gray-700 rounded-lg skeleton animate-shimmer" />
            <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded mt-2 skeleton animate-shimmer" />
          </div>
          <div className="mt-8 h-64 bg-gray-200 dark:bg-gray-700 rounded-2xl skeleton animate-shimmer" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
        <div className="relative max-w-2xl mx-auto animate-fadeIn">
          <div className="flex items-center gap-3 mb-6">
            <Link
              href="/tasks"
              className="flex items-center gap-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="text-sm font-medium">Back to Tasks</span>
            </Link>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Error Loading Task</h1>
          <div className="mb-4 p-4 bg-danger-50 dark:bg-danger-900/30 border border-danger-100 dark:border-danger-800 rounded-xl text-danger-700 dark:text-danger-300">
            {error}
          </div>
          <Link href="/tasks">
            <Button variant="secondary">Back to Tasks</Button>
          </Link>
        </div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
        <div className="relative max-w-2xl mx-auto animate-fadeIn">
          <div className="flex items-center gap-3 mb-6">
            <Link
              href="/tasks"
              className="flex items-center gap-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="text-sm font-medium">Back to Tasks</span>
            </Link>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Task Not Found</h1>
          <Link href="/tasks">
            <Button variant="secondary">Back to Tasks</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Premium Background - Light Mode */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none dark:hidden">
        <div className="absolute -top-60 top-0 right-0 w-[600px] h-[600px] bg-gradient-to-br from-violet-200/30 to-purple-200/20 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-gradient-to-br from-fuchsia-200/25 to-pink-200/15 rounded-full blur-3xl animate-float" style={{ animationDelay: '1.5s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-gradient-to-br from-indigo-200/20 to-blue-200/15 rounded-full blur-3xl animate-pulse-soft" />
      </div>

      {/* Premium Background - Dark Mode */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none hidden dark:block">
        <div className="absolute -top-60 top-0 right-0 w-[600px] h-[600px] bg-gradient-to-br from-violet-600/20 to-purple-600/15 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-gradient-to-br from-fuchsia-600/15 to-pink-600/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1.5s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-gradient-to-br from-indigo-600/10 to-blue-600/8 rounded-full blur-3xl animate-pulse-soft" />
      </div>

      <div className="relative max-w-2xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8 gap-4 animate-slideDown">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Link
                href="/tasks"
                className="flex items-center gap-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                <span className="text-sm font-medium">Back to Tasks</span>
              </Link>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white tracking-tight">Edit Task</h1>
            <p className="mt-1 text-gray-500 dark:text-gray-400">Update your task details</p>
          </div>
          <ThemeToggle />
        </div>

        {/* Error Alert - Premium */}
        {error && (
          <div className="mb-6 p-5 bg-gradient-to-br from-rose-50 to-rose-100 dark:from-rose-900/30 dark:to-rose-950/20 backdrop-blur-sm border border-rose-200/60 dark:border-rose-800/60 rounded-2xl text-rose-700 dark:text-rose-300 animate-slideDown shadow-lg shadow-rose-200/30 dark:shadow-rose-950/30">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div className="flex-1">
                <p className="font-semibold text-sm">Update Error</p>
                <p className="text-sm mt-0.5 opacity-90">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Form Card - Premium Glassmorphism */}
        <div className="relative group animate-slideUp">
          <div className="absolute -inset-0.5 bg-gradient-to-r from-violet-500 via-purple-500 to-violet-500 rounded-3xl blur opacity-20 group-hover:opacity-30 transition duration-1000 group-hover:duration-200" />
          <div className="relative bg-white/90 dark:bg-gray-800/90 backdrop-blur-2xl rounded-3xl shadow-2xl shadow-gray-300/50 dark:shadow-black/50 border border-white/70 dark:border-gray-700/50 p-8">
          <TaskForm
            onSubmit={handleSubmit}
            initialData={{ title: task.title, description: task.description || '' }}
            submitText="Update Task"
            showCancel
            onCancel={() => router.push('/tasks')}
          />
          </div>
        </div>
      </div>
    </div>
  );
};

export default EditTaskPage;
