'use client';

import React, { forwardRef } from 'react';

interface InputProps {
  label?: string;
  id?: string;
  type?: string;
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (e: React.FocusEvent<HTMLInputElement>) => void;
  error?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  helperText?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      id,
      type = 'text',
      placeholder,
      value,
      onChange,
      onBlur,
      error,
      required = false,
      disabled = false,
      className = '',
      icon,
      iconPosition = 'left',
      helperText,
    },
    ref
  ) => {
    return (
      <div className="mb-5">
        {label && (
          <label
            htmlFor={id}
            className={`
            block text-sm font-medium mb-1.5
            transition-colors duration-200
            ${error ? 'text-red-600 dark:text-red-400' : 'text-gray-700 dark:text-gray-300'}
          `}
          >
            {label}
            {required && <span className="text-red-500 dark:text-red-400 ml-0.5">*</span>}
          </label>
        )}
        <div className="relative">
          {icon && iconPosition === 'left' && (
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-400 dark:text-gray-500 group-focus-within:text-blue-500 dark:group-focus-within:text-blue-400 transition-colors">
              {icon}
            </div>
          )}
          <input
            ref={ref}
            id={id}
            type={type}
            placeholder={placeholder}
            value={value}
            onChange={onChange}
            onBlur={onBlur}
            required={required}
            disabled={disabled}
            className={`
            w-full px-4 py-3
            bg-white dark:bg-gray-800/60
            border rounded-xl
            text-gray-800 dark:text-gray-100
            placeholder-gray-400 dark:placeholder-gray-500
            transition-all duration-200 ease-out
            appearance-none
            ${icon && iconPosition === 'left' ? 'pl-11' : ''}
            ${icon && iconPosition === 'right' ? 'pr-11' : ''}
            ${
              error
                ? 'border-red-300 dark:border-red-500 focus:ring-red-500/20 focus:border-red-500 dark:focus:border-red-400 hover:border-red-400 dark:hover:border-red-400'
                : 'border-gray-200 dark:border-gray-700 focus:ring-blue-500/20 focus:border-blue-500 dark:focus:border-blue-400 hover:border-gray-300 dark:hover:border-gray-600'
            }
            focus:outline-none focus:ring-2
            disabled:bg-gray-50 dark:disabled:bg-gray-900 disabled:text-gray-500 dark:disabled:text-gray-600 disabled:cursor-not-allowed
            ${className}
          `}
          />
          {icon && iconPosition === 'right' && (
            <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none text-gray-400 dark:text-gray-500 group-focus-within:text-blue-500 dark:group-focus-within:text-blue-400 transition-colors">
              {icon}
            </div>
          )}
        </div>
        {error && (
          <p className="mt-1.5 text-sm text-red-600 dark:text-red-400 animate-slide-up">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1.5 text-sm text-gray-500 dark:text-gray-400">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
