'use client';

import React, { forwardRef } from 'react';
import { useTheme } from '@/context/ThemeContext';

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'success';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  fullWidth?: boolean;
  icon?: React.ReactNode;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(({
  children,
  onClick,
  type = 'button',
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  className = '',
  fullWidth = false,
  icon,
}, ref) => {
  const { isTransitioning } = useTheme();

  const baseClasses = 'relative inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-200 ease-out focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]';

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm gap-1.5',
    md: 'px-5 py-2.5 text-sm gap-2',
    lg: 'px-7 py-3.5 text-base gap-2.5',
  };

  const variantClasses = {
    primary: `
      bg-gradient-to-r from-primary-600 to-primary-500
      text-white shadow-lg shadow-primary-500/25
      hover:from-primary-700 hover:to-primary-600
      hover:shadow-xl hover:shadow-primary-500/30
      hover:-translate-y-0.5
      focus:ring-primary-500/50
    `,
    secondary: `
      bg-theme-background-secondary border border-theme-border
      text-theme-text shadow-sm
      hover:bg-theme-background hover:border-theme-text-secondary
      hover:text-theme-text hover:shadow-md hover:-translate-y-0.5
      focus:ring-primary-500/20
    `,
    danger: `
      bg-gradient-to-r from-danger-600 to-danger-500
      text-white shadow-lg shadow-danger-500/25
      hover:from-danger-700 hover:to-danger-600
      hover:shadow-xl hover:shadow-danger-500/30
      hover:-translate-y-0.5
      focus:ring-danger-500/50
    `,
    success: `
      bg-gradient-to-r from-success-600 to-success-500
      text-white shadow-lg shadow-success-500/25
      hover:from-success-700 hover:to-success-600
      hover:shadow-xl hover:shadow-success-500/30
      hover:-translate-y-0.5
      focus:ring-success-500/50
    `,
    ghost: `
      bg-transparent
      text-theme-text-secondary dark:text-gray-400
      hover:bg-theme-background-secondary hover:text-theme-text
      focus:ring-primary-500/20
    `,
  };

  const widthClass = fullWidth ? 'w-full' : '';

  const classes = `${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${widthClass} ${className}`;

  return (
    <button
      ref={ref}
      type={type}
      onClick={onClick}
      disabled={disabled || loading || isTransitioning}
      className={classes}
    >
      {loading ? (
        <>
          <svg
            className="animate-spin h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <span>Loading...</span>
        </>
      ) : (
        <>
          {icon && <span className="flex-shrink-0">{icon}</span>}
          {children}
        </>
      )}
    </button>
  );
});

Button.displayName = 'Button';

export default Button;
