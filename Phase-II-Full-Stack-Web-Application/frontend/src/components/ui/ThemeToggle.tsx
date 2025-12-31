'use client';

import React, { useState, useEffect } from 'react';
import { useTheme } from '@/context/ThemeContext';
import { useThemeAccessibility, useThemeKeyboardNavigation, useHighContrastSupport, useReducedMotionSupport } from '@/hooks/useThemeAccessibility';

const SunIcon = ({ className = "w-5 h-5" }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
    />
  </svg>
);

const MoonIcon = ({ className = "w-5 h-5" }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
    />
  </svg>
);

const SystemIcon = ({ className = "w-5 h-5" }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
    />
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
    />
  </svg>
);


interface ThemeToggleProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

type ThemePreference = 'light' | 'dark' | 'system';

const ThemeToggle: React.FC<ThemeToggleProps> = ({
  className = '',
  size = 'md',
}) => {
  const { theme, preference, setPreference, isTransitioning } = useTheme();
  const [isAnimating, setIsAnimating] = useState(false);

  // Accessibility hooks
  const { getAriaLabel, getThemeDescription } = useThemeAccessibility();
  useThemeKeyboardNavigation();
  useHighContrastSupport();
  useReducedMotionSupport();

  const cycleTheme = () => {
    setIsAnimating(true);

    // Cycle through themes: light -> dark -> system -> light ...
    const themes: ThemePreference[] = ['light', 'dark', 'system'];
    const currentIndex = themes.indexOf(preference);
    const nextIndex = (currentIndex + 1) % themes.length;
    setPreference(themes[nextIndex]);

    setTimeout(() => setIsAnimating(false), 400);
  };

  const buttonSizeClasses = {
    sm: 'p-2',
    md: 'p-2.5',
    lg: 'p-3',
  };

  const iconSizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  const isDark = theme === 'dark';
  const isSystem = preference === 'system';

  // Determine which icon to show based on current preference
  const showSunIcon = preference === 'light';
  const showMoonIcon = preference === 'dark';
  const showSystemIcon = preference === 'system';

  return (
    <button
      onClick={cycleTheme}
      className={`
        relative inline-flex items-center justify-center
        rounded-xl ${buttonSizeClasses[size]}
        bg-white dark:bg-gray-800
        text-gray-700 dark:text-gray-200
        shadow-lg shadow-gray-200/50 dark:shadow-gray-900/50
        border border-gray-200 dark:border-gray-700
        hover:shadow-xl hover:scale-105
        active:scale-95
        transition-all duration-300 ease-out
        focus:outline-none focus:ring-2 focus:ring-primary-500/50
        ${isAnimating ? 'animate-spin' : ''} ${isTransitioning ? 'pointer-events-none' : ''}
        ${className}
      `}
      aria-label={getAriaLabel(theme, preference)}
      aria-describedby="theme-status"
      title={getThemeDescription(theme, preference)}
      disabled={isTransitioning}
      data-theme-toggle
    >
      {/* Sun glow effect */}
      <div className={`absolute inset-0 rounded-xl bg-gradient-to-br from-yellow-100/20 to-transparent pointer-events-none transition-all duration-500 ${showSunIcon ? 'opacity-100 scale-100' : 'opacity-0 scale-0'}`} />

      {/* Moon glow effect */}
      <div className={`absolute inset-0 rounded-xl bg-gradient-to-br from-indigo-900/20 to-transparent pointer-events-none transition-all duration-500 ${showMoonIcon ? 'opacity-100 scale-100' : 'opacity-0 scale-0'}`} />

      {/* System glow effect */}
      <div className={`absolute inset-0 rounded-xl bg-gradient-to-br from-blue-100/20 to-transparent pointer-events-none transition-all duration-500 ${showSystemIcon ? 'opacity-100 scale-100' : 'opacity-0 scale-0'}`} />

      {/* Sun Icon */}
      <span
        className={`
          relative flex items-center justify-center
          ${iconSizeClasses[size]}
          transition-all duration-500 ease-out
          ${showSunIcon ? 'opacity-100 scale-100 rotate-0' : 'opacity-0 scale-90 rotate-12'}
        `}
      >
        <SunIcon className={iconSizeClasses[size]} />
      </span>

      {/* Moon Icon */}
      <span
        className={`
          absolute flex items-center justify-center
          ${iconSizeClasses[size]}
          transition-all duration-500 ease-out
          ${showMoonIcon ? 'opacity-100 scale-100 rotate-0' : 'opacity-0 scale-90 -rotate-12'}
        `}
      >
        <MoonIcon className={iconSizeClasses[size]} />
      </span>

      {/* System Icon */}
      <span
        className={`
          absolute flex items-center justify-center
          ${iconSizeClasses[size]}
          transition-all duration-500 ease-out
          ${showSystemIcon ? 'opacity-100 scale-100 rotate-0' : 'opacity-0 scale-90 rotate-12'}
        `}
      >
        <SystemIcon className={iconSizeClasses[size]} />
      </span>

      {/* System indicator ring */}
      {isSystem && (
        <div className={`
          absolute inset-0 rounded-xl
          border-2 border-primary-400/50
          animate-pulse-soft
          pointer-events-none
        `} />
      )}
    </button>
  );
};

export default ThemeToggle;
