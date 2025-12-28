# Phase I: In-Memory Python Console Todo App

A console-based todo application built with Python 3.13+ using only the standard library.

## Features

- Add new tasks with title and description
- View all tasks with status indicators
- Mark tasks as complete/incomplete
- Update task details
- Delete tasks

## Running the Application

```bash
python src/todo_app.py
```

## Project Structure

```
src/
├── todo_app.py      # Main application entry point
├── models/
│   └── task.py      # Task data model
├── services/
│   └── task_service.py  # Task management service
└── cli/
    └── menu.py      # Console menu interface

tests/
├── unit/
│   ├── test_task.py
│   └── test_task_service.py
└── integration/
    └── test_todo_app.py
```

## Requirements

- Python 3.13+
- No external dependencies
