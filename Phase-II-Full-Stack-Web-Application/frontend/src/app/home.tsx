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
    { value: '10K+', label: 'Tasks Created', color: 'from-primary-500 to-primary-600' },
    { value: '5K+', label: 'Active Users', color: 'from-success-500 to-success-600' },
    { value: '99.9%', label: 'Uptime', color: 'from-warning-500 to-warning-600' },
    { value: '4.9', label: 'Rating', color: 'from-purple-500 to-purple-600' },
  ];

  const testimonials = [
    {
      content: "This todo app has completely transformed how I manage my daily tasks. The design is stunning and the functionality is top-notch.",
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
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-950 dark:via-gray-900 dark:to-gray-800">
      {/* Background decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-[500px] h-[500px] bg-gradient-to-br from-primary-400/10 to-primary-600/5 rounded-full blur-3xl animate-float" />
        <div className="absolute -bottom-40 -left-40 w-[500px] h-[500px] bg-gradient-to-br from-success-400/10 to-success-600/5 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/3 left-1/3 w-[400px] h-[400px] bg-gradient-to-br from-warning-400/10 to-warning-600/5 rounded-full blur-3xl animate-pulse-soft" />
        <div className="absolute bottom-1/4 right-1/4 w-[300px] h-[300px] bg-gradient-to-br from-purple-400/10 to-purple-600/5 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }} />

        {/* Floating particles */}
        <div className="absolute inset-0">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-primary-400/20 rounded-full animate-float"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 5}s`,
                animationDuration: `${3 + Math.random() * 4}s`,
              }}
            />
          ))}
        </div>
      </div>

      {/* Navigation */}
      <nav className="relative z-10 px-4 sm:px-6 lg:px-8 py-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-4 group">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-lg shadow-primary-500/30 group-hover:shadow-primary-500/40 transform group-hover:scale-105 transition-all duration-300">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold text-gray-900 dark:text-white transition-colors group-hover:text-primary-600">Evolution of Todo</span>
              <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">Task Management Redefined</span>
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
      <section className="relative z-10 px-4 sm:px-6 lg:px-8 pt-8 pb-16">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-3 px-6 py-3 rounded-full bg-gradient-to-r from-primary-50 to-primary-100 border border-primary-100/50 mb-8 hover:shadow-md transition-all duration-300 cursor-default backdrop-blur-sm">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400/70"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-primary-500"></span>
              </span>
              <span className="text-sm font-medium text-primary-700">✨ Modern Task Management</span>
              <div className="w-2 h-2 bg-primary-400 rounded-full animate-pulse"></div>
            </div>

            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-gray-900 dark:text-white tracking-tight leading-[1.1] text-balance">
              Manage your tasks with{' '}
              <span className="relative inline-block">
                <span className="bg-gradient-to-r from-primary-600 via-primary-500 to-primary-600 bg-clip-text text-transparent font-bold animate-gradient">elegance</span>
                <svg className="absolute -bottom-3 left-0 w-full h-4 text-primary-200/50" viewBox="0 0 200 12" preserveAspectRatio="none">
                  <path d="M0,8 Q50,0 100,8 T200,8" stroke="url(#gradient-underline)" strokeWidth="3" fill="none" />
                  <defs>
                    <linearGradient id="gradient-underline" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#60a5fa" />
                      <stop offset="50%" stopColor="#3b82f6" />
                      <stop offset="100%" stopColor="#2563eb" />
                    </linearGradient>
                  </defs>
                </svg>
              </span>
            </h1>

            <p className="mt-8 text-lg sm:text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto leading-relaxed text-balance">
              A beautifully designed todo application that helps you stay organized,
              productive, and in control of your daily tasks with modern aesthetics and intuitive workflows.
            </p>

            <div className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button
                size="lg"
                onClick={handleRedirect}
                className="bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300"
                icon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                }
              >
                {isAuthenticated() ? 'Go to Tasks' : 'Get Started Free'}
              </Button>
              <Link href="/register">
                <Button
                  variant="secondary"
                  size="lg"
                  className="bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-700 hover:shadow-lg transform hover:-translate-y-1 transition-all duration-300"
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

            {/* Trust indicators */}
            <div className="mt-8 flex items-center justify-center gap-6 text-sm text-gray-500 dark:text-gray-400">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
                <span>Secure & Encrypted</span>
              </div>
              <div className="w-px h-4 bg-gray-300 dark:bg-gray-600"></div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse"></div>
                <span>Real-time Sync</span>
              </div>
              <div className="w-px h-4 bg-gray-300 dark:bg-gray-600"></div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-warning-500 rounded-full animate-pulse"></div>
                <span>Cross-platform</span>
              </div>
            </div>
          </div>

          {/* Hero Visual */}
          <div className="mt-16 relative">
            <div className="absolute inset-0 bg-gradient-to-t from-white/50 via-transparent to-transparent dark:from-gray-900/50 z-10 pointer-events-none" />
            <div className="relative bg-gradient-to-br from-white/80 to-gray-50/80 dark:from-gray-800/80 dark:to-gray-900/80 backdrop-blur-xl rounded-3xl shadow-2xl shadow-gray-200/50 dark:shadow-gray-900/50 border border-white/60 dark:border-gray-700/60 overflow-hidden">
              <div className="px-6 py-4 border-b border-white/60 dark:border-gray-700/60 flex items-center gap-3 bg-gradient-to-r from-white/50 to-gray-50/50 dark:from-gray-800/50 dark:to-gray-900/50">
                <div className="flex gap-2">
                  <div className="w-3.5 h-3.5 rounded-full bg-danger-400/80 ring-4 ring-danger-400/20" />
                  <div className="w-3.5 h-3.5 rounded-full bg-warning-400/80 ring-4 ring-warning-400/20" />
                  <div className="w-3.5 h-3.5 rounded-full bg-success-400/80 ring-4 ring-success-400/20" />
                </div>
                <div className="flex-1 text-center">
                  <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-gradient-to-r from-primary-50/80 to-primary-100/80 text-sm text-gray-700 dark:text-gray-200 font-medium border border-primary-100/50">
                    <svg className="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    <span className="font-semibold">My Tasks Dashboard</span>
                  </div>
                </div>
              </div>
              <div className="p-6 space-y-4">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className="flex items-center gap-4 p-4 rounded-xl bg-white/60 dark:bg-gray-800/60 border border-white/40 dark:border-gray-700/40 hover:bg-white/80 dark:hover:bg-gray-800 hover:shadow-lg hover:shadow-gray-200/30 dark:hover:shadow-gray-900/30 transition-all duration-300 group"
                    style={{ animationDelay: `${300 + i * 100}ms` }}
                  >
                    <div className={`relative w-6 h-6 rounded-lg border-2 flex items-center justify-center transition-all duration-300 group-hover:scale-110 ${
                      i === 1
                        ? 'bg-gradient-to-br from-success-500 to-success-600 border-success-500 shadow-lg shadow-success-500/30'
                        : i === 2
                        ? 'bg-gradient-to-br from-warning-100 to-warning-200 border-warning-300'
                        : 'border-gray-300 dark:border-gray-600 group-hover:border-primary-400 dark:group-hover:border-primary-400'
                    }`}>
                      {(i === 1 || i === 2) && (
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                      {i === 3 && (
                        <div className="w-2 h-2 rounded-full bg-primary-400"></div>
                      )}
                    </div>
                    <div className="flex-1">
                      <div className={`h-4 rounded transition-all duration-300 ${
                        i === 1 ? 'w-1/2 bg-gradient-to-r from-gray-300 to-gray-400 line-through opacity-60' : i === 2 ? 'w-2/3 bg-gradient-to-r from-gray-200 to-gray-300' : 'w-3/4 bg-gradient-to-r from-gray-100 to-gray-200'
                      }`} />
                    </div>
                    <div className="flex items-center gap-2">
                      <div className={`px-3 py-1.5 rounded-full text-xs font-medium flex items-center justify-center ${
                        i === 1
                          ? 'bg-gradient-to-r from-success-100 to-success-200 text-success-700 border border-success-200/50'
                          : i === 2
                          ? 'bg-gradient-to-r from-warning-100 to-warning-200 text-warning-700 border border-warning-200/50'
                          : 'bg-gradient-to-r from-primary-100 to-primary-200 text-primary-700 border border-primary-200/50'
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
                className="group text-center p-6 rounded-2xl bg-gradient-to-br from-white/80 to-gray-50/80 dark:from-gray-800/80 dark:to-gray-900/80 backdrop-blur-sm border border-white/60 dark:border-gray-700/60 hover:shadow-xl hover:shadow-gray-200/30 dark:hover:shadow-gray-900/30 transition-all duration-300 hover:-translate-y-1"
                style={{ animationDelay: `${600 + index * 100}ms` }}
              >
                <div className={`text-3xl sm:text-4xl font-bold bg-gradient-to-r ${stat.color} bg-clip-text text-transparent`}>
                  {stat.value}
                </div>
                <div className="mt-2 text-sm text-gray-500 dark:text-gray-400 font-medium">{stat.label}</div>
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br opacity-0 group-hover:opacity-5 transition-opacity duration-300"></div>
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
                className="group p-6 rounded-2xl bg-gradient-to-br from-white/80 to-gray-50/80 dark:from-gray-800/80 dark:to-gray-900/80 backdrop-blur-xl shadow-lg shadow-gray-200/50 dark:shadow-gray-900/50 border border-white/60 dark:border-gray-700/60 hover:shadow-xl hover:shadow-gray-200/60 dark:hover:shadow-gray-900/60 hover:-translate-y-2 transition-all duration-300 group"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-300 group-hover:scale-110 ${
                  feature.color === 'primary'
                    ? 'bg-gradient-to-br from-primary-100 to-primary-200 text-primary-600 group-hover:bg-gradient-to-br group-hover:from-primary-500 group-hover:to-primary-600 group-hover:text-white shadow-lg shadow-primary-500/20'
                    : feature.color === 'success'
                    ? 'bg-gradient-to-br from-success-100 to-success-200 text-success-600 group-hover:bg-gradient-to-br group-hover:from-success-500 group-hover:to-success-600 group-hover:text-white shadow-lg shadow-success-500/20'
                    : feature.color === 'warning'
                    ? 'bg-gradient-to-br from-warning-100 to-warning-200 text-warning-600 group-hover:bg-gradient-to-br group-hover:from-warning-500 group-hover:to-warning-600 group-hover:text-white shadow-lg shadow-warning-500/20'
                    : 'bg-gradient-to-br from-danger-100 to-danger-200 text-danger-600 group-hover:bg-gradient-to-br group-hover:from-danger-500 group-hover:to-danger-600 group-hover:text-white shadow-lg shadow-danger-500/20'
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
                className="group p-6 rounded-2xl bg-gradient-to-br from-white/80 to-gray-50/80 dark:from-gray-800/80 dark:to-gray-900/80 backdrop-blur-xl shadow-lg shadow-gray-200/50 dark:shadow-gray-900/50 border border-white/60 dark:border-gray-700/60 hover:shadow-xl hover:shadow-gray-200/60 dark:hover:shadow-gray-900/60 hover:-translate-y-2 transition-all duration-300"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex items-center gap-2 mb-4">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <svg key={star} className="w-5 h-5 text-gradient-to-r from-warning-400 to-warning-500" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed italic">"{testimonial.content}"</p>
                <div className="mt-6 flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-semibold text-lg shadow-lg shadow-primary-500/30">
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
      <section className="relative z-10 px-4 sm:px-6 lg:px-8 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <div className="relative p-8 rounded-3xl bg-gradient-to-br from-primary-600 via-primary-600 to-primary-700 shadow-2xl shadow-primary-500/30 overflow-hidden">
            {/* Decorative elements */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2" />
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full translate-y-1/2 -translate-x-1/2" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-white/5 rounded-full" />

            <div className="relative z-10">
              <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
                Ready to get organized?
              </h2>
              <p className="mt-4 text-lg text-primary-100 max-w-xl mx-auto">
                Start managing your tasks today. It is free to get started and takes less than a minute.
              </p>
              <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link href="/register">
                  <Button
                    size="lg"
                    className="bg-white text-primary-600 hover:bg-gray-100 hover:text-primary-700 shadow-xl shadow-black/20 transform hover:-translate-y-1 transition-all duration-300"
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
                    className="border-2 border-white/30 text-white hover:bg-white/10 hover:border-white/50 transform hover:-translate-y-1 transition-all duration-300"
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
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-lg">
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