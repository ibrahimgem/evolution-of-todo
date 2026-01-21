'use client';

import React, { useState } from 'react';
import Input from '../ui/Input';
import Button from '../ui/Button';
import type { TaskRead } from '../../lib/api-client';

interface TaskFormProps {
  onSubmit: (taskData: { title: string; description?: string }) => Promise<void>;
  initialData?: Partial<TaskRead>;
  submitText?: string;
  onCancel?: () => void;
  showCancel?: boolean;
}

const TaskForm: React.FC<TaskFormProps> = ({
  onSubmit,
  initialData,
  submitText = 'Create Task',
  onCancel,
  showCancel = false,
}) => {
  const [title, setTitle] = useState(initialData?.title || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [errors, setErrors] = useState<{ title?: string; description?: string }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const newErrors: { title?: string; description?: string } = {};

    if (!title.trim()) {
      newErrors.title = 'Title is required';
    } else if (title.length > 200) {
      newErrors.title = 'Title must be 200 characters or less';
    }

    if (description && description.length > 1000) {
      newErrors.description = 'Description must be 1000 characters or less';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    setIsSubmitting(true);
    try {
      await onSubmit({ title: title.trim(), description: description.trim() || undefined });
      // Reset form after successful submission (only if not editing)
      if (!initialData?.title) {
        setTitle('');
        setDescription('');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5 animate-fade-in">
      <div className="animate-slide-up">
        <Input
          label="Task Title"
          id="task-title"
          type="text"
          placeholder="What needs to be done?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          error={errors.title}
          required
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
          }
        />
      </div>

      <div className="animate-slide-up" style={{ animationDelay: '100ms' }}>
        <Input
          label="Description"
          id="task-description"
          type="text"
          placeholder="Add more details (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          error={errors.description}
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h7"
              />
            </svg>
          }
        />
      </div>

      <div
        className="flex items-center gap-3 pt-2 animate-slide-up"
        style={{ animationDelay: '150ms' }}
      >
        <Button
          type="submit"
          disabled={isSubmitting}
          loading={isSubmitting}
          size="lg"
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
          }
        >
          {submitText}
        </Button>

        {showCancel && onCancel && (
          <Button
            type="button"
            variant="ghost"
            onClick={onCancel}
            disabled={isSubmitting}
            size="lg"
          >
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
};

export default TaskForm;
