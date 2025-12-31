'use client';

import React, { useEffect, useState, useMemo } from 'react';
import { useTheme } from '@/context/ThemeContext';

/**
 * Visual feedback component for theme transitions
 * Provides smooth loading states and visual indicators during theme switching
 */
const ThemeTransitionOverlay: React.FC = () => {
  const { isTransitioning, theme } = useTheme();
  const [isVisible, setIsVisible] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (isTransitioning) {
      setIsVisible(true);
      setProgress(0);

      // Animate progress bar
      const interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            return 100;
          }
          return prev + 10;
        });
      }, 15);

      return () => clearInterval(interval);
    } else {
      // Fade out when transition completes
      const timeout = setTimeout(() => {
        setIsVisible(false);
        setProgress(0);
      }, 200);

      return () => clearTimeout(timeout);
    }
  }, [isTransitioning]);

  if (!isVisible) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 pointer-events-none">
      {/* Radial gradient overlay */}
      <div
        className={`
          absolute inset-0 bg-gradient-radial from-transparent via-white/10 to-white/20
          dark:from-transparent dark:via-gray-900/30 dark:to-gray-900/50
          transition-all duration-300 ease-out
          ${isTransitioning ? 'opacity-100 scale-100' : 'opacity-0 scale-95'}
        `}
      />

      {/* Animated background shimmer */}
      <div
        className={`
          absolute inset-0 bg-gradient-to-r
          ${theme === 'light'
            ? 'from-primary-500/10 via-success-500/10 to-warning-500/10'
            : 'from-primary-400/20 via-success-400/20 to-warning-400/20'
          }
          animate-shimmer
          transition-all duration-500 ease-out
        `}
      />

      {/* Progress bar */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 w-64">
        <div className="bg-white/20 dark:bg-gray-800/50 backdrop-blur-sm rounded-full p-1">
          <div
            className={`
              h-2 rounded-full bg-gradient-to-r
              ${theme === 'light'
                ? 'from-primary-500 to-primary-600'
                : 'from-primary-400 to-primary-500'
              }
              transition-all duration-150 ease-out
              shadow-lg shadow-primary-500/30
            `}
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="text-center mt-2 text-sm font-medium text-white/80">
          {progress < 100 ? 'Switching theme...' : 'Theme applied'}
        </div>
      </div>

      {/* Floating particles */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(8)].map((_, i) => (
          <div
            key={i}
            className={`
              absolute w-2 h-2 rounded-full
              ${theme === 'light'
                ? 'bg-primary-400/30'
                : 'bg-primary-300/40'
              }
              animate-float
              shadow-lg shadow-primary-500/20
            `}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 2}s`,
              animationDuration: `${3 + Math.random() * 2}s`,
            }}
          />
        ))}
      </div>

      {/* Center ripple effect */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
        <div
          className={`
            w-32 h-32 rounded-full border-4 border-white/30 dark:border-gray-700/30
            animate-ripple
            ${isTransitioning ? 'scale-0 opacity-100' : 'scale-100 opacity-0'}
            transition-all duration-300 ease-out
          `}
        />
        <div
          className={`
            absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2
            w-16 h-16 rounded-full bg-white/20 dark:bg-gray-700/20
            animate-pulse-soft
            ${isTransitioning ? 'scale-100 opacity-100' : 'scale-0 opacity-0'}
            transition-all duration-300 ease-out
          `}
        />
      </div>
    </div>
  );
};

/**
 * Theme transition notification component
 */
const ThemeTransitionNotification: React.FC = () => {
  const { isTransitioning, theme, preference } = useTheme();
  const [showNotification, setShowNotification] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');

  useEffect(() => {
    if (isTransitioning) {
      const themeLabel = theme === 'light' ? 'Light mode' : 'Dark mode';
      const preferenceLabel = preference === 'system' ? 'system preference' : preference;
      setNotificationMessage(`Applying ${themeLabel} (${preferenceLabel})...`);
      setShowNotification(true);
    } else {
      const timeout = setTimeout(() => {
        setShowNotification(false);
      }, 1000);
      return () => clearTimeout(timeout);
    }
  }, [isTransitioning, theme, preference]);

  if (!showNotification) {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 z-50 animate-slideIn">
      <div className={`
        flex items-center gap-3 px-4 py-3 rounded-xl
        bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm
        shadow-xl shadow-gray-200/30 dark:shadow-gray-900/40
        border border-gray-200/50 dark:border-gray-700/50
      `}>
        <div className="relative">
          <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse" />
          <div className="absolute inset-0 w-2 h-2 bg-primary-400 rounded-full animate-ping opacity-75" />
        </div>
        <div className="text-sm font-medium text-gray-700 dark:text-gray-200">
          {notificationMessage}
        </div>
        <div className="w-4 h-4">
          <div className="w-2 h-2 bg-primary-500 rounded-full mx-auto animate-bounce" />
        </div>
      </div>
    </div>
  );
};

/**
 * Loading spinner for theme operations
 */
const ThemeLoadingSpinner: React.FC<{ isVisible: boolean }> = ({ isVisible }) => {
  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm">
      <div className="text-center">
        <div className="inline-flex items-center gap-4 bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-2xl">
          <div className="relative">
            <div className="w-12 h-12 border-4 border-primary-200/50 border-t-primary-500 rounded-full animate-spin" />
            <div className="absolute inset-0 w-12 h-12 border-4 border-success-200/50 border-r-success-500 rounded-full animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }} />
            <div className="absolute inset-2 w-8 h-8 border-4 border-warning-200/50 border-b-warning-500 rounded-full animate-spin" style={{ animationDuration: '2s' }} />
          </div>
          <div>
            <div className="text-lg font-semibold text-gray-800 dark:text-white mb-2">Applying theme</div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Please wait...</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export { ThemeTransitionOverlay, ThemeTransitionNotification, ThemeLoadingSpinner };