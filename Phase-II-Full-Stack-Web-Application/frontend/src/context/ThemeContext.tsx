'use client';

import React, { createContext, useContext, useEffect, useState, useCallback, useMemo } from 'react';
import { ThemeTransitionOverlay, ThemeTransitionNotification } from '@/components/ui/ThemeTransitionOverlay';

export type Theme = 'light' | 'dark';
export type ThemePreference = Theme | 'system';

interface ThemeContextType {
  theme: Theme;
  preference: ThemePreference;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
  setPreference: (preference: ThemePreference) => void;
  isTransitioning: boolean;
}

const defaultContext: ThemeContextType = {
  theme: 'light',
  preference: 'system',
  toggleTheme: () => {},
  setTheme: () => {},
  setPreference: () => {},
  isTransitioning: false,
};

const ThemeContext = createContext<ThemeContextType>(defaultContext);

// Utility functions
const getSystemTheme = (): Theme => {
  if (typeof window === 'undefined') return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

const applyThemeToDOM = (theme: Theme) => {
  // Use CSS custom properties for smoother transitions
  const root = document.documentElement;

  if (theme === 'dark') {
    root.classList.add('dark');
    root.style.setProperty('--theme-background', 'var(--gray-900)');
    root.style.setProperty('--theme-background-secondary', 'var(--gray-800)');
    root.style.setProperty('--theme-text', 'var(--gray-100)');
    root.style.setProperty('--theme-text-secondary', 'var(--gray-300)');
    root.style.setProperty('--theme-border', 'var(--gray-700)');
  } else {
    root.classList.remove('dark');
    root.style.setProperty('--theme-background', 'var(--gray-50)');
    root.style.setProperty('--theme-background-secondary', 'var(--gray-100)');
    root.style.setProperty('--theme-text', 'var(--gray-800)');
    root.style.setProperty('--theme-text-secondary', 'var(--gray-600)');
    root.style.setProperty('--theme-border', 'var(--gray-200)');
  }
};

// Enhanced Theme Provider
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>('light');
  const [preference, setPreferenceState] = useState<ThemePreference>('system');
  const [mounted, setMounted] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);

  // Load initial state from localStorage
  useEffect(() => {
    try {
      const storedPreference = localStorage.getItem('theme-preference') as ThemePreference | null;
      const storedTheme = localStorage.getItem('theme') as Theme | null;

      // Set preference from localStorage first
      if (storedPreference) {
        setPreferenceState(storedPreference);
      } else {
        setPreferenceState('system');
      }

      // Determine initial theme based on preference
      let initialTheme: Theme;
      if (storedPreference === 'system') {
        initialTheme = getSystemTheme();
      } else if (storedPreference && (storedPreference === 'light' || storedPreference === 'dark')) {
        initialTheme = storedPreference;
      } else if (storedTheme && (storedTheme === 'light' || storedTheme === 'dark')) {
        initialTheme = storedTheme;
      } else {
        initialTheme = getSystemTheme();
      }

      setThemeState(initialTheme);
      setMounted(true);

      // Apply theme immediately for smooth hydration
      applyThemeToDOM(initialTheme);

      // Listen for system theme changes
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleSystemThemeChange = (e: MediaQueryListEvent) => {
        const currentPref = localStorage.getItem('theme-preference') as ThemePreference | null;
        if (currentPref === 'system') {
          const newSystemTheme = e.matches ? 'dark' : 'light';
          setIsTransitioning(true);
          setThemeState(newSystemTheme);
          applyThemeToDOM(newSystemTheme);
          setTimeout(() => setIsTransitioning(false), 300);
        }
      };

      // Add event listener for system theme changes
      if (mediaQuery.addEventListener) {
        mediaQuery.addEventListener('change', handleSystemThemeChange);
      } else {
        // Fallback for older browsers
        mediaQuery.addListener(handleSystemThemeChange);
      }

      return () => {
        if (mediaQuery.removeEventListener) {
          mediaQuery.removeEventListener('change', handleSystemThemeChange);
        } else {
          mediaQuery.removeListener(handleSystemThemeChange);
        }
      };
    } catch (error) {
      console.warn('Error loading theme preferences:', error);
      setMounted(true);
      applyThemeToDOM('light');
    }
  }, []);

  const setTheme = useCallback((newTheme: Theme) => {
    setIsTransitioning(true);

    // If user explicitly sets a theme, update preference to that theme
    if (preference === 'system') {
      setPreferenceState(newTheme);
      localStorage.setItem('theme-preference', newTheme);
    }

    setThemeState(newTheme);
    localStorage.setItem('theme', newTheme);

    applyThemeToDOM(newTheme);

    // Remove transition lock after animation completes
    setTimeout(() => setIsTransitioning(false), 300);
  }, [preference]);

  const setPreference = useCallback((newPreference: ThemePreference) => {
    setPreferenceState(newPreference);
    localStorage.setItem('theme-preference', newPreference);

    if (newPreference === 'system') {
      const systemTheme = getSystemTheme();
      if (systemTheme !== theme) {
        setIsTransitioning(true);
        setThemeState(systemTheme);
        applyThemeToDOM(systemTheme);
        setTimeout(() => setIsTransitioning(false), 300);
      }
    } else {
      if (newPreference !== theme) {
        setIsTransitioning(true);
        setThemeState(newPreference);
        applyThemeToDOM(newPreference);
        setTimeout(() => setIsTransitioning(false), 300);
      }
    }
  }, [theme]);

  const toggleTheme = useCallback(() => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
  }, [theme, setTheme]);

  // Memoize context value to prevent unnecessary re-renders
  const contextValue = useMemo<ThemeContextType>(() => ({
    theme: mounted ? theme : 'light',
    preference,
    toggleTheme,
    setTheme,
    setPreference,
    isTransitioning,
  }), [theme, preference, mounted, toggleTheme, setTheme, setPreference, isTransitioning]);

  return (
    <ThemeContext.Provider value={contextValue}>
      <div
        className={`
          min-h-screen
          transition-colors duration-300 ease-out
          bg-theme-background
          text-theme-text
          ${isTransitioning ? 'theme-transitioning' : ''}
        `}
        style={{
          // Add subtle transition for better performance
          transitionProperty: 'background-color, color, border-color',
        }}
      >
        {children}
        <ThemeTransitionOverlay />
        <ThemeTransitionNotification />
      </div>
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
