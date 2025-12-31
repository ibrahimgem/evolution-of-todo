---
name: nextjs-frontend
description: Use when building or modifying Next.js 16+ frontend applications with App Router, TypeScript, and Tailwind CSS. Covers component patterns, API integration, authentication flow, and responsive UI implementation.
---

# Next.js Frontend

## Overview

This skill provides guidance for building modern Next.js 16+ frontend applications using the App Router, TypeScript, and Tailwind CSS. Use when creating new pages, components, API integrations, or modifying the todo app frontend.

## Quick Start

```typescript
// Basic page structure with App Router
import { NextPage } from 'next'

const TasksPage: NextPage = () => {
  return (
    <main className="p-4">
      <h1 className="text-2xl font-bold">My Tasks</h1>
    </main>
  )
}

export default TasksPage
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── page.tsx            # Home page
│   │   ├── layout.tsx          # Root layout
│   │   ├── globals.css         # Global styles
│   │   └── tasks/              # Tasks feature
│   │       ├── page.tsx        # Tasks list
│   │       ├── new/            # Create task
│   │       └── [id]/           # Task details
│   ├── components/
│   │   ├── ui/                 # Reusable UI components
│   │   └── tasks/              # Task-specific components
│   └── lib/
│       ├── api.ts              # API client
│       └── auth.ts             # Auth utilities
├── package.json
└── tailwind.config.ts
```

## Component Patterns

### Client Component (with interactivity)

```typescript
// components/TaskList.tsx
'use client'

import { useState, useEffect } from 'react'

interface Task {
  id: number
  title: string
  completed: boolean
}

export default function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([])

  useEffect(() => {
    fetchTasks()
  }, [])

  async function fetchTasks() {
    const res = await fetch('/api/tasks')
    const data = await res.json()
    setTasks(data)
  }

  async function toggleComplete(id: number) {
    await fetch(`/api/tasks/${id}/complete`, { method: 'PATCH' })
    fetchTasks()
  }

  return (
    <ul>
      {tasks.map(task => (
        <li key={task.id} className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={task.completed}
            onChange={() => toggleComplete(task.id)}
          />
          <span className={task.completed ? 'line-through' : ''}>
            {task.title}
          </span>
        </li>
      ))}
    </ul>
  )
}
```

### Server Component (data fetching)

```typescript
// app/tasks/page.tsx
import { api } from '@/lib/api'
import TaskList from '@/components/TaskList'

export default async function TasksPage() {
  const tasks = await api.getTasks()

  return (
    <main className="max-w-2xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">My Tasks</h1>
      <TaskList initialTasks={tasks} />
    </main>
  )
}
```

## API Client Pattern

```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem('auth_token')

  const res = await fetch(`${API_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  })

  if (!res.ok) {
    throw new Error('API request failed')
  }

  return res.json()
}

export const api = {
  getTasks: () => fetchWithAuth('/api/tasks'),
  createTask: (data: { title: string; description?: string }) =>
    fetchWithAuth('/api/tasks', { method: 'POST', body: JSON.stringify(data) }),
  updateTask: (id: number, data: Partial<{ title: string; description: string }>) =>
    fetchWithAuth(`/api/tasks/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteTask: (id: number) =>
    fetchWithAuth(`/api/tasks/${id}`, { method: 'DELETE' }),
  toggleComplete: (id: number) =>
    fetchWithAuth(`/api/tasks/${id}/complete`, { method: 'PATCH' }),
}
```

## Tailwind CSS Patterns

### Responsive Layout

```typescript
// Responsive container
<div className="container mx-auto px-4">
  {/* Mobile: stack vertically, tablet+: side by side */}
  <div className="flex flex-col md:flex-row gap-4">
    <div className="w-full md:w-1/3">Sidebar</div>
    <div className="w-full md:w-2/3">Main content</div>
  </div>
</div>

// Responsive typography
<h1 className="text-2xl md:text-3xl lg:text-4xl font-bold">
  Responsive Title
</h1>

// Mobile-first spacing
<div className="p-4 md:p-6 lg:p-8">
  Responsive padding
</div>
```

### Task UI Component

```typescript
// components/TaskItem.tsx
interface TaskItemProps {
  task: {
    id: number
    title: string
    description?: string
    completed: boolean
  }
  onToggle: (id: number) => void
  onEdit: (id: number) => void
  onDelete: (id: number) => void
}

export function TaskItem({ task, onToggle, onEdit, onDelete }: TaskItemProps) {
  return (
    <div className={`
      border rounded-lg p-4 mb-2
      ${task.completed ? 'bg-gray-50' : 'bg-white'}
      hover:shadow-md transition-shadow
    `}>
      <div className="flex items-center gap-3">
        <input
          type="checkbox"
          checked={task.completed}
          onChange={() => onToggle(task.id)}
          className="h-5 w-5 rounded"
        />
        <div className="flex-1">
          <h3 className={`font-medium ${task.completed ? 'line-through text-gray-500' : ''}`}>
            {task.title}
          </h3>
          {task.description && (
            <p className="text-sm text-gray-600 mt-1">{task.description}</p>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onEdit(task.id)}
            className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
          >
            Edit
          </button>
          <button
            onClick={() => onDelete(task.id)}
            className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  )
}
```

## Form Patterns

```typescript
// components/TaskForm.tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function TaskForm() {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState('')
  const router = useRouter()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')

    if (!title.trim()) {
      setError('Title is required')
      return
    }

    try {
      await api.createTask({ title, description })
      router.refresh()
      setTitle('')
      setDescription('')
    } catch (err) {
      setError('Failed to create task')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <p className="text-red-500 text-sm">{error}</p>}

      <div>
        <label htmlFor="title" className="block text-sm font-medium mb-1">
          Title
        </label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={e => setTitle(e.target.value)}
          className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
          placeholder="Enter task title"
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium mb-1">
          Description (optional)
        </label>
        <textarea
          id="description"
          value={description}
          onChange={e => setDescription(e.target.value)}
          className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
          rows={3}
          placeholder="Enter description"
        />
      </div>

      <button
        type="submit"
        className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors"
      >
        Add Task
      </button>
    </form>
  )
}
```

## Resources

### references/

- `nextjs-docs.md` - Next.js 16 App Router documentation reference

### scripts/

- `create-page.sh` - Generate new page with boilerplate
- `create-component.sh` - Generate component with TypeScript types
