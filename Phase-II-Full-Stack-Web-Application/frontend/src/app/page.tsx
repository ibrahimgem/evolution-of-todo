'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '../lib/auth';
import Button from '../components/ui/Button';
import ThemeToggle from '../components/ui/ThemeToggle';

const HomePage = () => {
  const router = useRouter();
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const handleRedirect = () => {
    if (isAuthenticated()) {
      router.push('/tasks');
    } else {
      router.push('/login');
    }
  };

  const features = [
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
      ),
      title: 'Task Management',
      description: 'Create, edit, and organize your tasks with ease. Keep track of everything in one place.',
      color: 'primary',
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      ),
      title: 'Secure Authentication',
      description: 'Your data is protected with JWT authentication. Sign in securely from any device.',
      color: 'success',
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      title: 'Real-time Updates',
      description: 'Changes sync instantly across all your devices. Never lose track of your tasks.',
      color: 'warning',
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      ),
      title: 'Responsive Design',
      description: 'Beautiful interface that works seamlessly on desktop, tablet, and mobile devices.',
      color: 'danger',
    },
  ];

  const stats = [
    { value: '10K+', label: 'Tasks Created', color: 'from-indigo-500 to-indigo-600' },
    { value: '5K+', label: 'Active Users', color: 'from-emerald-500 to-emerald-600' },
    { value: '99.9%', label: 'Uptime', color: 'from-amber-500 to-amber-600' },
    { value: '4.9', label: 'Rating', color: 'from-purple-500 to-purple-600' },
  ];

  const testimonials = [
    {
      content: "This todo app has completely transformed how I manage my daily tasks. The design is stunning and functionality is top-notch.",
      author: "Sarah Chen",
      role: "Product Designer",
      avatar: "SC",
    },
    {
      content: "Finally, a task manager that looks as good as it works. The real-time sync is a game-changer for my workflow.",
      author: "Marcus Johnson",
      role: "Software Developer",
      avatar: "MJ",
    },
    {
      content: "Simple, elegant, and powerful. I've tried many todo apps, but this one stands out from the crowd.",
      author: "Emily Rodriguez",
      role: "Project Manager",
      avatar: "ER",
    },
  ];

  return (
    <div className="min-h-screen relative">
      {/* Premium Background - Light Mode */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none dark:hidden">
        {/* Premium gradient orbs */}
        <div className="absolute -top-60 -right-60 w-[600px] h-[600px] bg-gradient-to-br from-indigo-200/30 to-purple-200/20 rounded-full blur-3xl animate-float" />
        <div className="absolute -bottom-60 -left-60 w-[600px] h-[600px] bg-gradient-to-br from-amber-200/25 to-orange-200/15 rounded-full blur-3xl animate-float" style={{ animationDelay: '1.5s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-br from-emerald-200/20 to-teal-200/15 rounded-full blur-3xl animate-pulse-soft" />
        <div className="absolute top-1/4 right-1/4 w-[300px] h-[300px] bg-gradient-to-br from-rose-200/15 to-pink-200/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '2.5s' }} />

        {/* Floating particles */}
        <div className="absolute inset-0">
          {Array(25).fill(0).map((_, i) => (
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

        {/* Gradient mesh overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-white/40 to-transparent" />
      </div>

      {/* Premium Background - Dark Mode */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none hidden dark:block">
        {/* Luminous gradient orbs */}
        <div className="absolute -top-60 -right-60 w-[600px] h-[600px] bg-gradient-to-br from-indigo-600/20 to-purple-600/15 rounded-full blur-3xl animate-float" />
        <div className="absolute -bottom-60 -left-60 w-[600px] h-[600px] bg-gradient-to-br from-emerald-600/15 to-teal-600/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1.5s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-br from-amber-600/10 to-orange-600/8 rounded-full blur-3xl animate-pulse-soft" />
        <div className="absolute top-1/4 right-1/4 w-[300px] h-[300px] bg-gradient-to-br from-rose-600/10 to-pink-600/6 rounded-full blur-3xl animate-float" style={{ animationDelay: '2.5s' }} />

        {/* Floating particles with glow */}
        <div className="absolute inset-0">
          {[Array(25)].map((_, i) => (
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

        {/* Gradient mesh overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/30 to-transparent" />
      </div>

      {/* Navigation */}
      <nav className="relative z-10 px-4 sm:px-6 lg:px-8 py-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-4 group">
            <div className="relative w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-indigo-600 flex items-center justify-center shadow-xl shadow-indigo-500/30 group-hover:shadow-indigo-500/50 transform group-hover:scale-105 transition-all duration-500">
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-indigo-400/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <svg className="w-7 h-7 text-white relative" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold text-gray-900 dark:text-white transition-colors tracking-tight group-hover:text-indigo-600 dark:group-hover:text-indigo-400">Evolution of Todo</span>
              <span className="text-xs text-gray-500 dark:text-gray-400 font-medium tracking-wide">Task Management Redefined</span>
            </div>
          </Link>
          <div className="flex items-center gap-3">
            <ThemeToggle size="md" />
            <Link href="/login">
              <Button variant="ghost" size="sm">Sign In</Button>
            </Link>
            <Link href="/register">
              <Button size="sm">Get Started</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 px-4 sm:px-6 lg:px-8 pt-12 pb-20">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-4xl mx-auto">
            {/* Premium badge */}
            <div className="inline-flex items-center gap-3 px-5 py-2.5 rounded-full bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100/80 mb-10 hover:shadow-lg hover:shadow-indigo-500/10 transition-all duration-300 cursor-default backdrop-blur-sm">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400/80"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-indigo-500"></span>
              </span>
              <span className="text-sm font-medium text-indigo-700 dark:text-indigo-300 tracking-wide">✨ Premium Task Management</span>
              <div className="w-2 h-2 bg-indigo-400 rounded-full animate-pulse"></div>
            </div>

            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-gray-900 dark:text-white tracking-tighter leading-[1.1] text-balance">
              Manage your tasks with{' '}
              <span className="relative inline-block">
                <span className="bg-gradient-to-r from-indigo-600 via-purple-500 to-indigo-600 bg-clip-text text-transparent font-bold animate-gradient shadow-2xl">elegance</span>
                <svg className="absolute -bottom-4 left-0 w-full h-5 text-indigo-200/50 dark:text-indigo-500/20" viewBox="0 0 200 12" preserveAspectRatio="none">
                  <path d="M0,8 Q50,0 100,8 T200,8" stroke="currentColor" strokeWidth="3" fill="none" />
                </svg>
              </span>
            </h1>

            <p className="mt-10 text-lg sm:text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto leading-relaxed text-balance">
              A beautifully designed todo application that helps you stay organized,
              productive, and in control of your daily tasks with modern aesthetics and intuitive workflows.
            </p>

            <div className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button
                size="lg"
                onClick={handleRedirect}
                className="bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-700 hover:from-indigo-700 hover:via-purple-700 hover:to-indigo-800 shadow-xl shadow-indigo-500/30 transform hover:-translate-y-1.5 transition-all duration-500 btn-shine"
                icon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                }
              >
                {isMounted && isAuthenticated() ? 'Go to Tasks' : 'Get Started Free'}
              </Button>
              <Link href="/register">
                <Button
                  variant="secondary"
                  size="lg"
                  className="bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-700 hover:shadow-xl transform hover:-translate-y-1.5 transition-all duration-500"
                  icon={
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  }
                >
                  Create Account
                </Button>
              </Link>
            </div>

            {/* Premium trust indicators */}
            <div className="mt-10 flex flex-wrap items-center justify-center gap-8 text-sm text-gray-500 dark:text-gray-400">
              <div className="flex items-center gap-2.5">
                <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-pulse shadow-lg shadow-emerald-500/50"></div>
                <span className="font-medium">Secure & Encrypted</span>
              </div>
              <div className="w-px h-5 bg-gray-300 dark:bg-gray-600"></div>
              <div className="flex items-center gap-2.5">
                <div className="w-2.5 h-2.5 bg-indigo-500 rounded-full animate-pulse shadow-lg shadow-indigo-500/50"></div>
                <span className="font-medium">Real-time Sync</span>
              </div>
              <div className="w-px h-5 bg-gray-300 dark:bg-gray-600"></div>
              <div className="flex items-center gap-2.5">
                <div className="w-2.5 h-2.5 bg-amber-500 rounded-full animate-pulse shadow-lg shadow-amber-500/50"></div>
                <span className="font-medium">Cross-platform</span>
              </div>
            </div>
          </div>

          {/* Premium Hero Visual */}
          <div className="mt-20 relative">
            <div className="absolute inset-0 bg-gradient-to-t from-white/60 via-transparent to-transparent dark:from-black/40 z-10 pointer-events-none" />
            <div className="relative bg-gradient-to-br from-white/90 to-gray-50/90 dark:from-gray-800/90 dark:to-gray-900/90 backdrop-blur-2xl rounded-3xl shadow-2xl shadow-gray-300/50 dark:shadow-black/50 border border-white/70 dark:border-gray-700/50 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200/50 dark:border-gray-700/50 flex items-center gap-3 bg-gradient-to-r from-white/60 to-gray-50/60 dark:from-gray-800/60 dark:to-gray-900/60">
                <div className="flex gap-2">
                  <div className="w-4 h-4 rounded-full bg-gradient-to-br from-rose-400 to-rose-500 shadow-lg shadow-rose-500/20" />
                  <div className="w-4 h-4 rounded-full bg-gradient-to-br from-amber-400 to-amber-500 shadow-lg shadow-amber-500/20" />
                  <div className="w-4 h-4 rounded-full bg-gradient-to-br from-emerald-400 to-emerald-500 shadow-lg shadow-emerald-500/20" />
                </div>
                <div className="flex-1 text-center">
                  <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-gradient-to-r from-indigo-50/90 to-purple-50/90 text-sm text-gray-700 dark:text-gray-200 font-medium border border-indigo-100/50 dark:border-indigo-900/30">
                    <svg className="w-4 h-4 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    <span className="font-semibold tracking-wide">My Tasks Dashboard</span>
                  </div>
                </div>
              </div>
              <div className="p-6 space-y-4">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className="flex items-center gap-4 p-4 rounded-2xl bg-gradient-to-r from-white/70 to-gray-50/70 dark:from-gray-800/70 dark:to-gray-900/70 border border-gray-200/60 dark:border-gray-700/60 hover:from-white dark:hover:from-gray-800 hover:shadow-xl hover:shadow-gray-200/30 dark:hover:shadow-black/30 transition-all duration-500 group"
                    style={{ animationDelay: `${300 + i * 100}ms` }}
                  >
                    <div className={`relative w-6 h-6 rounded-lg border-2 flex items-center justify-center transition-all duration-300 group-hover:scale-110 ${
                      i === 1
                        ? 'bg-gradient-to-br from-emerald-500 to-emerald-600 border-emerald-500 shadow-lg shadow-emerald-500/30'
                        : i === 2
                        ? 'bg-gradient-to-br from-amber-100 to-amber-200 border-amber-300'
                        : 'border-gray-300 dark:border-gray-600 group-hover:border-indigo-400 dark:group-hover:border-indigo-400'
                    }`}>
                      {(i === 1 || i === 2) && (
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                      {i === 3 && (
                        <div className="w-2 h-2 rounded-full bg-indigo-400"></div>
                      )}
                    </div>
                    <div className="flex-1">
                      <div className={`h-4 rounded transition-all duration-300 ${
                        i === 1 ? 'w-1/2 bg-gradient-to-r from-gray-300 to-gray-400 line-through opacity-50' : i === 2 ? 'w-2/3 bg-gradient-to-r from-gray-200 to-gray-300' : 'w-3/4 bg-gradient-to-r from-gray-100 to-gray-200'
                      }`} />
                    </div>
                    <div className="flex items-center gap-2">
                      <div className={`px-3 py-1.5 rounded-full text-xs font-medium flex items-center justify-center ${
                        i === 1
                          ? 'bg-gradient-to-r from-emerald-100 to-emerald-200 text-emerald-700 border border-emerald-200/50'
                          : i === 2
                          ? 'bg-gradient-to-r from-amber-100 to-amber-200 text-amber-700 border border-amber-200/50'
                          : 'bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-700 border border-indigo-200/50'
                      }`}>
                        {i === 1 ? 'Completed' : i === 2 ? 'Today' : 'Later'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <div
                key={stat.label}
                className="group text-center p-6 rounded-3xl bg-gradient-to-br from-white/80 to-gray-50/80 dark:from-gray-800/80 dark:to-gray-900/80 backdrop-blur-sm border border-gray-200/60 dark:border-gray-700/60 hover:shadow-2xl hover:shadow-gray-200/30 dark:hover:shadow-black/30 transition-all duration-500 hover:-translate-y-2 hover:scale-105"
                style={{ animationDelay: `${600 + index * 100}ms` }}
              >
                <div className={`text-3xl sm:text-4xl font-bold bg-gradient-to-r ${stat.color} bg-clip-text text-transparent`}>
                  {stat.value}
                </div>
                <div className="mt-2 text-sm text-gray-500 dark:text-gray-400 font-medium">{stat.label}</div>
                <div className="absolute inset-0 rounded-3xl bg-gradient-to-br opacity-0 group-hover:opacity-5 transition-opacity duration-300"></div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 px-4 sm:px-6 lg:px-8 py-16">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white tracking-tight">
              Everything you need
            </h2>
            <p className="mt-4 text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Powerful features designed to help you manage your tasks efficiently and beautifully.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <div
                key={feature.title}
                className="group p-7 rounded-3xl bg-gradient-to-br from-white/80 to-gray-50/80 dark:from-gray-800/80 dark:to-gray-900/80 backdrop-blur-xl shadow-xl shadow-gray-200/50 dark:shadow-black/50 border border-gray-200/60 dark:border-gray-700/60 hover:shadow-2xl hover:shadow-gray-200/60 dark:hover:shadow-black/60 hover:-translate-y-3 hover:scale-[1.02] transition-all duration-500"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-300 group-hover:scale-110 ${
                  feature.color === 'primary'
                    ? 'bg-gradient-to-br from-indigo-100 to-purple-100 text-indigo-600 group-hover:bg-gradient-to-br group-hover:from-indigo-500 group-hover:to-purple-500 group-hover:text-white shadow-lg shadow-indigo-500/20'
                    : feature.color === 'success'
                    ? 'bg-gradient-to-br from-emerald-100 to-teal-100 text-emerald-600 group-hover:bg-gradient-to-br group-hover:from-emerald-500 group-hover:to-teal-500 group-hover:text-white shadow-lg shadow-emerald-500/20'
                    : feature.color === 'warning'
                    ? 'bg-gradient-to-br from-amber-100 to-orange-100 text-amber-600 group-hover:bg-gradient-to-br group-hover:from-amber-500 group-hover:to-orange-500 group-hover:text-white shadow-lg shadow-amber-500/20'
                    : 'bg-gradient-to-br from-rose-100 to-pink-100 text-rose-600 group-hover:bg-gradient-to-br group-hover:from-rose-500 group-hover:to-pink-500 group-hover:text-white shadow-lg shadow-rose-500/20'
                }`}>
                  {feature.icon}
                </div>
                <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-white">{feature.title}</h3>
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="relative z-10 px-4 sm:px-6 lg:px-8 py-16">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white tracking-tight">
              Loved by thousands
            </h2>
            <p className="mt-4 text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              See what our users have to say about Evolution of Todo.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {testimonials.map((testimonial, index) => (
              <div
                key={testimonial.author}
                className="group p-7 rounded-3xl bg-gradient-to-br from-white/80 to-gray-50/80 dark:from-gray-800/80 dark:to-gray-900/80 backdrop-blur-xl shadow-xl shadow-gray-200/50 dark:shadow-black/50 border border-gray-200/60 dark:border-gray-700/60 hover:shadow-2xl hover:shadow-gray-200/60 dark:hover:shadow-black/60 hover:-translate-y-3 hover:scale-[1.02] transition-all duration-500"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex items-center gap-3 mb-5 text-sm text-gray-500 dark:text-gray-400">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <svg key={star} className="w-5 h-5 text-gradient-to-r from-warning-400 to-warning-500" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed italic">"{testimonial.content}"</p>
                <div className="mt-6 flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-400 to-indigo-600 flex items-center justify-center text-white font-semibold text-lg shadow-lg shadow-indigo-500/30">
                    {testimonial.avatar}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900 dark:text-white">{testimonial.author}</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">{testimonial.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 px-4 sm:px-6 lg:px-8 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <div className="relative p-12 rounded-3xl bg-gradient-to-br from-indigo-600 via-purple-600 to-indigo-700 shadow-2xl shadow-indigo-500/30 overflow-hidden">
            {/* Decorative elements */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2" />
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full translate-y-1/2 -translate-x-1/2" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-white/5 rounded-full" />

            <div className="relative z-10">
              <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
                Ready to get organized?
              </h2>
              <p className="mt-4 text-lg text-indigo-100 max-w-xl mx-auto">
                Start managing your tasks today. It is free to get started and takes less than a minute.
              </p>
              <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link href="/register">
                  <Button
                    size="lg"
                    className="bg-white text-indigo-600 hover:bg-gray-100 hover:text-indigo-700 shadow-xl shadow-black/20 transform hover:-translate-y-1.5 transition-all duration-500"
                    icon={
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    }
                  >
                    Create Free Account
                  </Button>
                </Link>
                <Link href="/login">
                  <Button
                    variant="ghost"
                    size="lg"
                    className="border-2 border-white/30 text-white hover:bg-white/10 hover:border-white/50 transform hover:-translate-y-1.5 transition-all duration-500"
                  >
                    Already have an account?
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 px-4 sm:px-6 lg:px-8 py-8 border-t border-gray-200/50 dark:border-gray-700/50">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-600 flex items-center justify-center shadow-lg">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div className="flex flex-col">
              <span className="font-medium">Evolution of Todo</span>
              <span className="text-xs opacity-75">Task Management Redefined</span>
            </div>
          </div>
          <div className="flex items-center gap-6 text-sm text-gray-400">
            <span>Built with ❤️ using Next.js, FastAPI, and PostgreSQL</span>
          </div>
          <p className="text-sm text-gray-400">
            2025 Evolution of Todo. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
