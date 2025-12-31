'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import ThemeToggle from '../../components/ui/ThemeToggle';
import { authAPI } from '../../lib/api';
import { setAuthToken } from '../../lib/auth';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await authAPI.login({
        email,
        password,
      });

      // Store the token
      setAuthToken(response.access_token);

      // Redirect to tasks page
      router.push('/tasks');
      router.refresh();
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Premium Background - Light Mode */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none dark:hidden">
        <div className="absolute -top-60 -right-60 w-[600px] h-[600px] bg-gradient-to-br from-indigo-200/30 to-purple-200/20 rounded-full blur-3xl animate-float" />
        <div className="absolute -bottom-60 -left-60 w-[600px] h-[600px] bg-gradient-to-br from-violet-200/25 to-fuchsia-200/15 rounded-full blur-3xl animate-float" style={{ animationDelay: '1.5s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-br from-blue-200/20 to-cyan-200/15 rounded-full blur-3xl animate-pulse-soft" />

        {/* Floating particles */}
        <div className="absolute inset-0">
          {Array(20).fill(0).map((_, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-indigo-400/25 rounded-full animate-float"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 5}s`,
                animationDuration: `${4 + Math.random() * 3}s`,
              }}
            />
          ))}
        </div>
      </div>

      {/* Premium Background - Dark Mode */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none hidden dark:block">
        <div className="absolute -top-60 -right-60 w-[600px] h-[600px] bg-gradient-to-br from-indigo-600/20 to-purple-600/15 rounded-full blur-3xl animate-float" />
        <div className="absolute -bottom-60 -left-60 w-[600px] h-[600px] bg-gradient-to-br from-violet-600/15 to-fuchsia-600/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1.5s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-br from-blue-600/10 to-cyan-600/8 rounded-full blur-3xl animate-pulse-soft" />

        {/* Floating particles with glow */}
        <div className="absolute inset-0">
          {Array(20).fill(0).map((_, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-indigo-400/40 rounded-full animate-float shadow-lg"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 5}s`,
                animationDuration: `${4 + Math.random() * 3}s`,
              }}
            />
          ))}
        </div>
      </div>

      <div className="relative w-full max-w-md">
        {/* Theme Toggle */}
        <div className="absolute top-0 right-0 animate-fadeIn">
          <ThemeToggle />
        </div>

        {/* Back to home */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors mb-8 animate-fadeIn"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to home
        </Link>

        {/* Logo/Brand */}
        <div className="text-center mb-8 animate-fadeIn">
          <Link href="/" className="inline-block group">
            <div className="relative w-20 h-20 rounded-3xl bg-gradient-to-br from-indigo-500 via-purple-500 to-indigo-600 shadow-2xl shadow-indigo-500/40 flex items-center justify-center mx-auto mb-5 transform hover:scale-105 transition-all duration-500 group-hover:shadow-indigo-500/60">
              <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-indigo-400/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <svg
                className="w-10 h-10 text-white relative z-10"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                />
              </svg>
            </div>
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white tracking-tight mb-2">
            Welcome back
          </h1>
          <p className="text-base text-gray-600 dark:text-gray-300">Sign in to continue to your tasks</p>
        </div>

        {/* Login Card - Premium Glassmorphism */}
        <div className="relative group animate-slideUp">
          <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500 rounded-3xl blur opacity-20 group-hover:opacity-30 transition duration-1000 group-hover:duration-200" />
          <div className="relative bg-white/90 dark:bg-gray-800/90 backdrop-blur-2xl rounded-3xl shadow-2xl shadow-gray-300/50 dark:shadow-black/50 border border-white/70 dark:border-gray-700/50 p-8">
          {/* Error Alert - Premium */}
          {error && (
            <div className="mb-6 p-5 bg-gradient-to-br from-rose-50 to-rose-100 dark:from-rose-900/30 dark:to-rose-950/20 backdrop-blur-sm border border-rose-200/60 dark:border-rose-800/60 rounded-2xl text-rose-700 dark:text-rose-300 animate-slideDown shadow-lg shadow-rose-200/30 dark:shadow-rose-950/30">
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
                <div className="flex-1">
                  <p className="font-semibold text-sm">Authentication Error</p>
                  <p className="text-sm mt-0.5 opacity-90">{error}</p>
                </div>
              </div>
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit}>
            <div className="animate-slideUp" style={{ animationDelay: '100ms' }}>
              <Input
                label="Email address"
                id="email"
                type="email"
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                icon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"
                    />
                  </svg>
                }
              />
            </div>

            <div className="animate-slideUp" style={{ animationDelay: '150ms' }}>
              <div className="mb-1.5">
                <label
                  htmlFor="password"
                  className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
                >
                  Password <span className="text-danger-500">*</span>
                </label>
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-400">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                    />
                  </svg>
                </div>
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full px-4 py-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl text-gray-800 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 transition-all duration-200 ease-out appearance-none pl-11 pr-11 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 hover:border-gray-300 dark:hover:border-gray-500"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 transition-colors"
                >
                  {showPassword ? (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between animate-slideUp" style={{ animationDelay: '175ms' }}>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  className="w-4 h-4 rounded border-gray-300 dark:border-gray-600 text-primary-600 focus:ring-primary-500 cursor-pointer bg-white dark:bg-gray-700"
                />
                <span className="text-sm text-gray-600 dark:text-gray-400">Remember me</span>
              </label>
              <Link href="/forgot-password" className="text-sm font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 transition-colors">
                Forgot password?
              </Link>
            </div>

            <div className="animate-slideUp" style={{ animationDelay: '200ms' }}>
              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-700 hover:from-indigo-700 hover:via-purple-700 hover:to-indigo-800 shadow-xl shadow-indigo-500/30 hover:shadow-indigo-500/50 transform hover:-translate-y-0.5 transition-all duration-500 btn-shine"
                size="lg"
                loading={loading}
              >
                {loading ? 'Signing in...' : 'Sign in'}
              </Button>
            </div>
          </form>

          {/* Divider - Premium */}
          <div className="relative my-8 animate-fadeIn" style={{ animationDelay: '250ms' }}>
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gradient-to-r from-transparent via-gray-300 dark:via-gray-600 to-transparent" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white/90 dark:bg-gray-800/90 text-gray-500 dark:text-gray-400 font-medium">or</span>
            </div>
          </div>

          {/* Register Link - Premium */}
          <div className="text-center animate-fadeIn" style={{ animationDelay: '300ms' }}>
            <p className="text-gray-600 dark:text-gray-300">
              Do not have an account?{' '}
              <Link
                href="/register"
                className="font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 transition-all duration-200"
              >
                Sign up
              </Link>
            </p>
          </div>
          </div>
        </div>

        {/* Footer - Premium */}
        <p className="mt-10 text-center text-sm text-gray-500 dark:text-gray-400 animate-fadeIn">
          By signing in, you agree to our{' '}
          <a href="#" className="font-semibold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 transition-all">
            Terms of Service
          </a>{' '}
          and{' '}
          <a href="#" className="font-semibold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 transition-all">
            Privacy Policy
          </a>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
