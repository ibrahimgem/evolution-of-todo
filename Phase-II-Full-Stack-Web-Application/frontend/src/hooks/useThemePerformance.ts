'use client';

import { useEffect, useRef, useCallback, useState, useMemo } from 'react';

/**
 * Performance optimization hook for theme switching
 * Handles lazy loading, memoization, and performance monitoring
 */
export function useThemePerformance() {
  const transitionTimerRef = useRef<NodeJS.Timeout | null>(null);
  const frameIdRef = useRef<number | null>(null);

  // Debounce theme changes to prevent rapid switching
  const debounceThemeChange = useCallback((callback: () => void, delay: number = 100) => {
    if (transitionTimerRef.current) {
      clearTimeout(transitionTimerRef.current);
    }

    transitionTimerRef.current = setTimeout(() => {
      callback();
    }, delay);
  }, []);

  // Request animation frame for smooth transitions
  const scheduleThemeTransition = useCallback((callback: () => void) => {
    if (frameIdRef.current) {
      cancelAnimationFrame(frameIdRef.current);
    }

    frameIdRef.current = requestAnimationFrame(() => {
      callback();
    });
  }, []);

  // Optimize CSS custom properties updates
  const optimizeThemeUpdates = useCallback(() => {
    // Force hardware acceleration for better performance
    const root = document.documentElement;

    // Use requestAnimationFrame to batch DOM updates
    scheduleThemeTransition(() => {
      // Trigger GPU acceleration
      root.style.transform = 'translateZ(0)';
      root.style.willChange = 'background-color, color, border-color';

      // Remove will-change after transition
      setTimeout(() => {
        root.style.willChange = 'auto';
      }, 350);
    });
  }, [scheduleThemeTransition]);

  // Cleanup timers on unmount
  useEffect(() => {
    return () => {
      if (transitionTimerRef.current) {
        clearTimeout(transitionTimerRef.current);
      }
      if (frameIdRef.current) {
        cancelAnimationFrame(frameIdRef.current);
      }
    };
  }, []);

  return {
    debounceThemeChange,
    scheduleThemeTransition,
    optimizeThemeUpdates,
  };
}

/**
 * Hook for monitoring theme performance
 */
export function useThemePerformanceMonitor() {
  const performanceRef = useRef<{
    transitionStart: number;
    transitionEnd: number;
    isTransitioning: boolean;
  }>({
    transitionStart: 0,
    transitionEnd: 0,
    isTransitioning: false,
  });

  const startTransition = useCallback(() => {
    performanceRef.current.transitionStart = performance.now();
    performanceRef.current.isTransitioning = true;
  }, []);

  const endTransition = useCallback(() => {
    performanceRef.current.transitionEnd = performance.now();
    performanceRef.current.isTransitioning = false;

    const duration = performanceRef.current.transitionEnd - performanceRef.current.transitionStart;

    // Log performance metrics
    if (duration > 350) {
      console.warn(`Theme transition took ${duration.toFixed(2)}ms, consider optimizing`);
    } else {
      console.log(`Theme transition completed in ${duration.toFixed(2)}ms`);
    }
  }, []);

  const getPerformanceMetrics = useCallback(() => {
    const { transitionStart, transitionEnd, isTransitioning } = performanceRef.current;
    const duration = transitionEnd - transitionStart;

    return {
      isTransitioning,
      duration,
      isOptimal: duration <= 300,
    };
  }, []);

  return {
    startTransition,
    endTransition,
    getPerformanceMetrics,
  };
}

/**
 * Hook for lazy loading theme-dependent resources
 */
export function useThemeLazyLoading() {
  const loadedThemesRef = useRef<Set<string>>(new Set());

  const loadThemeResources = useCallback((theme: string) => {
    if (loadedThemesRef.current.has(theme)) {
      return Promise.resolve();
    }

    return new Promise<void>((resolve) => {
      // Simulate lazy loading of theme-specific resources
      setTimeout(() => {
        loadedThemesRef.current.add(theme);
        resolve();
      }, 50);
    });
  }, []);

  return {
    loadThemeResources,
    isThemeLoaded: (theme: string) => loadedThemesRef.current.has(theme),
  };
}

/**
 * Hook for virtualizing long lists in theme context
 */
export function useThemeVirtualization(items: any[], itemHeight: number = 50) {
  const [visibleRange, setVisibleRange] = useState({ start: 0, end: Math.min(items.length, 20) });

  const handleScroll = useCallback((scrollTop: number, containerHeight: number) => {
    const start = Math.floor(scrollTop / itemHeight);
    const visibleCount = Math.ceil(containerHeight / itemHeight);
    const end = Math.min(start + visibleCount + 5, items.length); // +5 for buffer

    setVisibleRange({ start: Math.max(0, start - 2), end }); // -2 for buffer
  }, [itemHeight, items.length]);

  const virtualizedItems = useMemo(() => {
    return items.slice(visibleRange.start, visibleRange.end).map((item, index) => ({
      ...item,
      virtualIndex: visibleRange.start + index,
      style: {
        position: 'absolute',
        top: (visibleRange.start + index) * itemHeight,
        height: itemHeight,
        left: 0,
        right: 0,
      },
    }));
  }, [items, visibleRange, itemHeight]);

  return {
    virtualizedItems,
    handleScroll,
    totalHeight: items.length * itemHeight,
  };
}