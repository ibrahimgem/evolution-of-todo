# Data Model for Phase I - In-Memory Python Console Todo App

## Task Entity

### Fields
- **id**: Integer (required) - Unique identifier for the task
- **title**: String (required) - Title of the task (1-200 characters)
- **description**: String (optional) - Detailed description of the task (max 1000 characters)
- **status**: String (required) - Status of the task ("pending" or "completed")
- **created_at**: DateTime (required) - Timestamp when task was created

### Validation Rules
- Title must be 1-200 characters long
- Description, if provided, must be 1-1000 characters long
- Status must be either "pending" or "completed"
- ID must be unique within the application session

### State Transitions
- A task can transition from "pending" to "completed" state
- A task can transition from "completed" back to "pending" state

## Task List Container

### Fields
- **tasks**: List of Task objects - Collection of all tasks in memory
- **next_id**: Integer - Counter for generating unique task IDs

### Operations
- Add a new task to the list
- Remove a task from the list by ID
- Update a task in the list by ID
- Find a task by ID
- Get all tasks
- Get tasks by status