'use client';

import { useEffect } from 'react';
import { useTheme } from '@/context/ThemeContext';

/**
 * Accessibility hook for theme switching
 * Ensures proper ARIA labels, screen reader announcements, and focus management
 */
export function useThemeAccessibility() {
  const { theme, preference, isTransitioning } = useTheme();

  useEffect(() => {
    // Announce theme changes to screen readers
    if (!isTransitioning) {
      const announcement = createThemeAnnouncement(theme, preference);
      announceToScreenReader(announcement);
    }

    // Update meta theme-color for mobile browsers
    updateThemeColor(theme);

    // Update document title with current theme
    updateDocumentTitle(theme, preference);

    // Ensure proper focus management during transitions
    if (isTransitioning) {
      disablePointerEventsDuringTransition();
    }
  }, [theme, preference, isTransitioning]);

  return {
    getAriaLabel: (currentTheme: string, currentPreference: string) =>
      `Switch to ${getTargetThemeLabel(currentTheme)} mode (${currentPreference === 'system' ? 'System' : currentPreference} setting)`,
    getThemeDescription: (currentTheme: string, currentPreference: string) =>
      `Currently using ${currentTheme} theme with ${currentPreference} preference`,
  };
}

function createThemeAnnouncement(theme: string, preference: string): string {
  const themeLabel = theme === 'light' ? 'Light mode' : 'Dark mode';
  const preferenceLabel = preference === 'system' ? 'system preference' : preference;

  return `Theme changed to ${themeLabel}. Using ${preferenceLabel}.`;
}

function announceToScreenReader(message: string) {
  // Create a live region for announcements
  let liveRegion = document.getElementById('theme-announcements');

  if (!liveRegion) {
    liveRegion = document.createElement('div');
    liveRegion.id = 'theme-announcements';
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.style.position = 'absolute';
    liveRegion.style.left = '-10000px';
    liveRegion.style.width = '1px';
    liveRegion.style.height = '1px';
    liveRegion.style.overflow = 'hidden';
    document.body.appendChild(liveRegion);
  }

  // Clear and set new message
  liveRegion.textContent = '';
  setTimeout(() => {
    liveRegion!.textContent = message;
  }, 100);
}

function updateThemeColor(theme: string) {
  const metaThemeColor = document.querySelector('meta[name="theme-color"]') as HTMLMetaElement;
  const metaThemeColorMobile = document.querySelector('meta[name="apple-mobile-web-app-status-bar-style"]') as HTMLMetaElement;

  const color = theme === 'light' ? '#ffffff' : '#0f172a';

  if (metaThemeColor) {
    metaThemeColor.content = color;
  }

  if (metaThemeColorMobile) {
    metaThemeColorMobile.content = color;
  }
}

function updateDocumentTitle(theme: string, preference: string) {
  const themeEmoji = theme === 'light' ? '☀️' : '🌙';
  const preferenceText = preference === 'system' ? 'System' : preference;

  document.title = `${themeEmoji} Evolution of Todo | ${preferenceText} Mode`;
}

function disablePointerEventsDuringTransition() {
  // Add pointer-events-none to prevent interactions during transition
  const body = document.body;
  body.style.pointerEvents = 'none';

  setTimeout(() => {
    body.style.pointerEvents = '';
  }, 300);
}

function getTargetThemeLabel(currentTheme: string): string {
  return currentTheme === 'light' ? 'Dark' : 'Light';
}

/**
 * Hook for managing keyboard navigation for theme switching
 */
export function useThemeKeyboardNavigation() {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Alt + T for theme toggle
      if (e.altKey && e.key.toLowerCase() === 't') {
        e.preventDefault();
        const themeToggle = document.querySelector('[data-theme-toggle]') as HTMLElement;
        if (themeToggle) {
          themeToggle.click();
        }
      }

      // Ctrl/Cmd + Shift + T for opening theme dropdown
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 't') {
        e.preventDefault();
        const themeDropdown = document.querySelector('[data-theme-dropdown]') as HTMLElement;
        if (themeDropdown) {
          themeDropdown.click();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);
}

/**
 * Hook for high contrast mode detection and support
 */
export function useHighContrastSupport() {
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-contrast: high)');

    const handleContrastChange = (e: MediaQueryListEvent) => {
      if (e.matches) {
        document.documentElement.classList.add('high-contrast');
      } else {
        document.documentElement.classList.remove('high-contrast');
      }
    };

    // Initial check
    if (mediaQuery.matches) {
      document.documentElement.classList.add('high-contrast');
    }

    mediaQuery.addEventListener('change', handleContrastChange);
    return () => mediaQuery.removeEventListener('change', handleContrastChange);
  }, []);
}

/**
 * Hook for reduced motion support
 */
export function useReducedMotionSupport() {
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    const handleMotionChange = (e: MediaQueryListEvent) => {
      if (e.matches) {
        document.documentElement.classList.add('reduced-motion');
      } else {
        document.documentElement.classList.remove('reduced-motion');
      }
    };

    // Initial check
    if (mediaQuery.matches) {
      document.documentElement.classList.add('reduced-motion');
    }

    mediaQuery.addEventListener('change', handleMotionChange);
    return () => mediaQuery.removeEventListener('change', handleMotionChange);
  }, []);
}

/**
 * Hook for color vision deficiency support
 */
export function useColorVisionSupport() {
  useEffect(() => {
    // Add class for color vision support
    document.documentElement.classList.add('color-vision-support');

    // Monitor for user preferences
    const checkColorPreferences = () => {
      // Check for any color vision related preferences
      const prefersNoColor = window.matchMedia('(prefers-color-scheme: no-preference)').matches;
      const prefersHighContrast = window.matchMedia('(prefers-contrast: high)').matches;

      if (prefersNoColor || prefersHighContrast) {
        document.documentElement.classList.add('enhanced-color-support');
      } else {
        document.documentElement.classList.remove('enhanced-color-support');
      }
    };

    checkColorPreferences();

    // Monitor changes
    const mediaQueries = [
      window.matchMedia('(prefers-color-scheme: no-preference)'),
      window.matchMedia('(prefers-contrast: high)')
    ];

    mediaQueries.forEach(mq => {
      mq.addEventListener('change', checkColorPreferences);
    });

    return () => {
      mediaQueries.forEach(mq => {
        mq.removeEventListener('change', checkColorPreferences);
      });
    };
  }, []);
}