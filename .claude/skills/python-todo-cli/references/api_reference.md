# TaskService API Reference

## Methods

### `add_task(title: str, description: str = "") -> Task`

Creates a new task with a unique sequential ID.

**Parameters:**
- `title` (str): Task title, 1-200 characters
- `description` (str, optional): Task description, max 1000 characters

**Returns:** `Task` - The created task object

**Raises:** `ValueError` - If title is empty or exceeds 200 characters

### `get_all_tasks() -> List[Task]`

Returns all tasks in the system.

**Returns:** `List[Task]` - List of all tasks (empty list if no tasks)

### `get_task_by_id(task_id: int) -> Optional[Task]`

Retrieves a task by its ID.

**Parameters:**
- `task_id` (int): The task ID to find

**Returns:** `Task | None` - The task if found, None otherwise

### `update_task(task_id: int, title: str = None, description: str = None) -> Task`

Updates an existing task's title and/or description.

**Parameters:**
- `task_id` (int): The task ID to update
- `title` (str, optional): New title (1-200 chars)
- `description` (str, optional): New description (max 1000 chars)

**Returns:** `Task` - The updated task object

**Raises:** `ValueError` - If task not found or validation fails

### `delete_task(task_id: int) -> bool`

Deletes a task by its ID.

**Parameters:**
- `task_id` (int): The task ID to delete

**Returns:** `bool` - True if deleted, False if not found

### `toggle_complete(task_id: int) -> Task`

Toggles a task's status between "pending" and "completed".

**Parameters:**
- `task_id` (int): The task ID to toggle

**Returns:** `Task` - The task with updated status

**Raises:** `ValueError` - If task not found

---

## Usage Example

```python
from services.task_service import TaskService

service = TaskService()

# Add a task
task = service.add_task("Buy groceries", "Milk, eggs, bread")

# View all tasks
all_tasks = service.get_all_tasks()

# Update a task
updated = service.update_task(1, title="Buy groceries and more")

# Mark complete
completed = service.toggle_complete(1)

# Delete a task
deleted = service.delete_task(1)
```
