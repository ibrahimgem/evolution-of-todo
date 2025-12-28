# Quickstart Guide for Phase I - In-Memory Python Console Todo App

## Prerequisites
- Python 3.13 or higher
- pip (Python package installer)

## Setup
1. Clone the repository
2. Navigate to the project directory
3. The application uses only Python standard library, so no additional installation is required

## Running the Application
1. Navigate to the project root directory
2. Run the application: `python src/todo_app.py`
3. The interactive menu will be displayed

## Basic Usage
1. When the application starts, you'll see a menu with options:
   - 1. Add Task
   - 2. View Tasks
   - 3. Update Task
   - 4. Delete Task
   - 5. Mark Task Complete/Incomplete
   - 6. Exit
2. Enter the number of the option you want to perform
3. Follow the prompts to complete your task

## Example Workflow
1. Select "1. Add Task" to create a new task
2. Enter the task title when prompted
3. Optionally enter a description
4. The task will be added to your list
5. Select "2. View Tasks" to see all your tasks
6. Use other options to manage your tasks

## Testing
To run the unit tests:
1. Navigate to the project root directory
2. Run: `python -m pytest tests/`