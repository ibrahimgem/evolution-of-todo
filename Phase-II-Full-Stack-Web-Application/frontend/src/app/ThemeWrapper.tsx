'use client';

import { useTheme } from '@/context/ThemeContext';

export default function ThemeWrapper({ children }: { children: React.ReactNode }) {
  const { theme, isTransitioning } = useTheme();

  return (
    <body className={`antialiased font-sans ${isTransitioning ? 'theme-transitioning' : ''}`}>
      {children}
    </body>
  );
}