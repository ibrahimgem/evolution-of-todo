---
name: python-todo-cli
description: Implements a console-based todo application in Python with task CRUD operations (Add, View, Update, Delete, Mark Complete). Use when building an interactive command-line todo manager with in-memory storage, input validation, and error handling.
---

# Python Todo CLI

## Overview

This skill enables building a Python console todo application with complete task management capabilities. The application features an interactive menu system, in-memory data storage, comprehensive input validation, and follows PEP 8 coding standards.

## Quick Start

```python
# Basic task structure
class Task:
    def __init__(self, id: int, title: str, description: str = "", status: str = "pending"):
        self.id = id
        self.title = title
        self.description = description
        self.status = status  # "pending" or "completed"
```

## Core Operations

### Task CRUD Operations

1. **Add Task** - Create new tasks with title and optional description
2. **View Tasks** - Display all tasks with status indicators
3. **Update Task** - Modify task title or description by ID
4. **Delete Task** - Remove task by ID
5. **Mark Complete** - Toggle task status between pending/completed

### Implementation Pattern

```python
# Task model with validation
class Task:
    def __init__(self, id: int, title: str, description: str = "", status: str = "pending"):
        self.id = id
        self.title = title
        self.description = description
        self.status = status

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        if not 1 <= len(value) <= 200:
            raise ValueError("Title must be 1-200 characters")
        self._title = value
```

### Service Layer Pattern

```python
class TaskService:
    def __init__(self):
        self.tasks = []
        self.next_id = 1

    def add_task(self, title: str, description: str = "") -> Task:
        task = Task(self.next_id, title, description)
        self.tasks.append(task)
        self.next_id += 1
        return task

    def get_all_tasks(self) -> List[Task]:
        return self.tasks

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(self, task_id: int, title: str = None, description: str = None) -> Task:
        task = self.get_task_by_id(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        return task

    def delete_task(self, task_id: int) -> bool:
        task = self.get_task_by_id(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False

    def toggle_complete(self, task_id: int) -> Task:
        task = self.get_task_by_id(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        task.status = "completed" if task.status == "pending" else "pending"
        return task
```

### CLI Menu Pattern

```python
class TodoMenu:
    def __init__(self, task_service: TaskService):
        self.service = task_service

    def display_main_menu(self):
        print("\n=== Todo Menu ===")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Update Task")
        print("4. Delete Task")
        print("5. Mark Complete/Incomplete")
        print("6. Exit")

    def get_user_choice(self) -> int:
        while True:
            try:
                choice = int(input("\nEnter choice (1-6): "))
                if 1 <= choice <= 6:
                    return choice
                print("Please enter a number between 1 and 6")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def run(self):
        while True:
            self.display_main_menu()
            choice = self.get_user_choice()
            if choice == 6:
                print("Goodbye!")
                break
            self.handle_choice(choice)

    def handle_choice(self, choice: int):
        handlers = {
            1: self.add_task,
            2: self.view_tasks,
            3: self.update_task,
            4: self.delete_task,
            5: self.toggle_complete
        }
        handler = handlers.get(choice)
        if handler:
            handler()
```

## Error Handling

```python
def validate_task_id(task_id: int, tasks: List[Task]) -> bool:
    if task_id < 1:
        print("Error: Task ID must be a positive number")
        return False
    exists = any(t.id == task_id for t in tasks)
    if not exists:
        print(f"Error: Task {task_id} not found")
        return False
    return True

def get_validated_input(prompt: str, field_name: str, max_length: int = 200) -> str:
    while True:
        value = input(prompt).strip()
        if not value:
            print(f"Error: {field_name} cannot be empty")
            continue
        if len(value) > max_length:
            print(f"Error: {field_name} must be {max_length} characters or less")
            continue
        return value
```

## Project Structure

```
src/
├── todo_app.py          # Main application entry point
├── models/
│   └── task.py          # Task data model
├── services/
│   └── task_service.py  # Business logic
└── cli/
    └── menu.py          # Console menu interface

tests/
├── unit/
│   ├── test_task.py
│   └── test_task_service.py
└── integration/
    └── test_todo_app.py
```

## Key Entities

- **Task**: Represents a todo item with ID, title, description, and status
- **TaskService**: Manages task operations and in-memory storage
- **TodoMenu**: Handles user interaction via console menu

## Resources

### scripts/

Utility scripts for task operations that can be executed directly.

### references/

- **api_reference.md**: Complete API documentation for TaskService methods

### assets/

Example templates or boilerplate code for the todo application structure.