'use client';

import React, { useEffect, useRef } from 'react';
import Button from './Button';

interface DeleteConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  taskTitle: string;
  loading?: boolean;
}

const DeleteConfirmDialog: React.FC<DeleteConfirmDialogProps> = ({
  isOpen,
  onClose,
  onConfirm,
  taskTitle,
  loading = false,
}) => {
  const dialogRef = useRef<HTMLDivElement>(null);
  const cancelRef = useRef<HTMLButtonElement>(null);

  // Handle escape key and focus trap
  useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    // Focus trap: move focus within the dialog
    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      const focusableElements = dialogRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      if (!focusableElements || focusableElements.length === 0) return;

      const firstElement = focusableElements[0] as HTMLElement;
      const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

      if (e.shiftKey) {
        // Shift + Tab: moving backward
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        }
      } else {
        // Tab: moving forward
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    };

    // Focus the cancel button when dialog opens
    cancelRef.current?.focus();

    document.addEventListener('keydown', handleEscape);
    document.addEventListener('keydown', handleTab);
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.removeEventListener('keydown', handleTab);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop with glassmorphism */}
      <div
        className="fixed inset-0 bg-gray-900/40 backdrop-blur-xl transition-all duration-300 animate-fadeIn"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Dialog container with scale animation */}
      <div
        ref={dialogRef}
        className={`
          relative w-full max-w-md
          bg-white/90 dark:bg-gray-800/90
          backdrop-blur-3xl
          rounded-3xl
          shadow-2xl shadow-gray-900/30 dark:shadow-gray-950/50
          border border-white/30 dark:border-gray-700/30
          transform transition-all duration-300 ease-out
          animate-scaleIn
        `}
        role="dialog"
        aria-modal="true"
        aria-labelledby="delete-title"
        aria-describedby="delete-description"
      >
        {/* Decorative gradient background */}
        <div className="absolute inset-0 overflow-hidden rounded-3xl pointer-events-none">
          <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-danger-100/50 to-danger-50/30 dark:from-danger-900/20 dark:to-transparent rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 animate-float-slow" />
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-gradient-to-tr from-rose-100/30 to-transparent dark:from-rose-900/10 rounded-full blur-3xl translate-y-1/3 -translate-x-1/3 animate-float-medium" />
        </div>

        {/* Content */}
        <div className="relative p-8">
          {/* Warning Icon with gradient and glow */}
          <div className="flex justify-center mb-6">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-danger-400 to-rose-600 rounded-full blur-lg opacity-50 animate-pulse-glow" />
              <div className="relative w-20 h-20 rounded-full bg-gradient-to-br from-danger-400 to-rose-600 flex items-center justify-center shadow-lg shadow-danger-500/40">
                <svg
                  className="w-10 h-10 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2.5}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
            </div>
          </div>

          {/* Title */}
          <h2
            id="delete-title"
            className="text-2xl font-bold text-gray-900 dark:text-white text-center mb-3 tracking-tight"
          >
            Delete Task?
          </h2>

          {/* Message with proper ARIA description */}
          <p
            id="delete-description"
            className="text-center text-gray-600 dark:text-gray-300 mb-8 leading-relaxed"
          >
            Are you sure you want to delete{' '}
            <span className="font-semibold text-gray-900 dark:text-white">"{taskTitle}"</span>?
            <br />
            <span className="text-sm text-gray-500 dark:text-gray-400 mt-2 inline-block">
              This action cannot be undone.
            </span>
          </p>

          {/* Buttons */}
          <div className="flex flex-row items-center justify-center gap-4 w-full">
            {/* Cancel Button - focused by default */}
            <Button
              ref={cancelRef}
              variant="ghost"
              onClick={onClose}
              disabled={loading}
              className="flex-1 min-w-[120px] flex-shrink-0 group hover:bg-gray-100 dark:hover:bg-gray-700/50 text-gray-700 dark:text-gray-300"
            >
              <span className="group-hover:translate-x-0 translate-x-1 transition-transform duration-200">
                Cancel
              </span>
            </Button>

            {/* Delete Button */}
            <Button
              variant="danger"
              onClick={onConfirm}
              loading={loading}
              disabled={loading}
              className="flex-1 min-w-[120px] flex-shrink-0 group shadow-lg shadow-danger-500/30 hover:shadow-danger-500/50 hover:-translate-y-0.5 hover:scale-105 transition-all duration-200"
            >
              <span className="flex items-center gap-2">
                <svg
                  className="w-4 h-4 group-hover:animate-shake"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
                Delete
              </span>
            </Button>
          </div>
        </div>

        {/* Bottom gradient highlight */}
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-danger-400 via-rose-500 to-danger-400 rounded-b-3xl" />
      </div>
    </div>
  );
};

export default DeleteConfirmDialog;
