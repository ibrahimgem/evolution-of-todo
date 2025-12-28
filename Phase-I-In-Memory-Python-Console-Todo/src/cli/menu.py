"""Console menu interface for the todo application."""

from services.task_service import TaskService


class TodoMenu:
    """Interactive console menu for todo task management."""

    def __init__(self, task_service: TaskService):
        """Initialize the menu with a TaskService instance.

        Args:
            task_service: The TaskService for managing tasks
        """
        self.service = task_service

    def display_main_menu(self) -> None:
        """Display the main menu options."""
        print("\n=== Todo Menu ===")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Mark Complete/Incomplete")
        print("4. Update Task")
        print("5. Delete Task")
        print("6. Exit")

    def get_user_choice(self) -> int:
        """Get and validate user menu choice.

        Returns:
            The validated menu choice (1-6)
        """
        while True:
            try:
                choice = int(input("\nEnter choice (1-6): "))
                if 1 <= choice <= 6:
                    return choice
                print("Please enter a number between 1 and 6")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def get_validated_input(
        self, prompt: str, field_name: str, max_length: int = 200
    ) -> str:
        """Get validated text input from user.

        Args:
            prompt: The input prompt to display
            field_name: Name of the field for error messages
            max_length: Maximum allowed characters

        Returns:
            The validated input string
        """
        while True:
            value = input(prompt).strip()
            if not value:
                print(f"Error: {field_name} cannot be empty")
                continue
            if len(value) > max_length:
                print(f"Error: {field_name} must be {max_length} characters or less")
                continue
            return value

    def add_task(self) -> None:
        """Handle adding a new task."""
        print("\n--- Add New Task ---")
        title = self.get_validated_input("Enter task title: ", "Title", 200)
        description = input("Enter task description (optional): ").strip()
        task = self.service.add_task(title, description or "")
        print(f"Task added successfully! (ID: {task.id})")

    def view_tasks(self) -> None:
        """Display all tasks."""
        print("\n--- All Tasks ---")
        tasks = self.service.get_all_tasks()
        if not tasks:
            print("No tasks found. Add some tasks to get started!")
            return

        for i, task in enumerate(tasks, 1):
            status_icon = "[X]" if task.status == "completed" else "[ ]"
            print(f"{i}. {status_icon} {task.title}")
            if task.description:
                print(f"   Description: {task.description}")
            print(f"   ID: {task.id} | Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}")
            print()

    def mark_complete(self) -> None:
        """Handle marking a task as complete/incomplete."""
        print("\n--- Mark Complete/Incomplete ---")
        tasks = self.service.get_all_tasks()
        if not tasks:
            print("No tasks found. Add some tasks first!")
            return

        self.view_tasks()
        try:
            task_id = int(input("Enter task ID to toggle: "))
            task = self.service.toggle_complete(task_id)
            status = "completed" if task.status == "completed" else "pending"
            print(f"Task marked as {status}!")
        except ValueError as e:
            print(f"Error: {e}")
        except ValueError:
            print("Error: Invalid task ID")

    def update_task(self) -> None:
        """Handle updating a task."""
        print("\n--- Update Task ---")
        tasks = self.service.get_all_tasks()
        if not tasks:
            print("No tasks found. Add some tasks first!")
            return

        self.view_tasks()
        try:
            task_id = int(input("Enter task ID to update: "))
            task = self.service.get_task_by_id(task_id)
            if task is None:
                print(f"Error: Task {task_id} not found")
                return

            print(f"Current title: {task.title}")
            print(f"Current description: {task.description}")

            new_title = input("Enter new title (leave empty to keep): ").strip()
            new_desc = input("Enter new description (leave empty to keep): ").strip()

            updated_task = self.service.update_task(
                task_id,
                title=new_title if new_title else None,
                description=new_desc if new_desc else None,
            )
            print("Task updated successfully!")
        except ValueError as e:
            print(f"Error: {e}")

    def delete_task(self) -> None:
        """Handle deleting a task."""
        print("\n--- Delete Task ---")
        tasks = self.service.get_all_tasks()
        if not tasks:
            print("No tasks found. Add some tasks first!")
            return

        self.view_tasks()
        try:
            task_id = int(input("Enter task ID to delete: "))
            confirm = input(f"Delete task {task_id}? (y/n): ").strip().lower()
            if confirm == "y":
                if self.service.delete_task(task_id):
                    print("Task deleted successfully!")
                else:
                    print(f"Error: Task {task_id} not found")
            else:
                print("Deletion cancelled.")
        except ValueError:
            print("Error: Invalid task ID")

    def handle_choice(self, choice: int) -> None:
        """Handle a menu choice.

        Args:
            choice: The menu choice number
        """
        handlers = {
            1: self.add_task,
            2: self.view_tasks,
            3: self.mark_complete,
            4: self.update_task,
            5: self.delete_task,
        }
        handler = handlers.get(choice)
        if handler:
            handler()

    def run(self) -> None:
        """Run the main menu loop."""
        print("Welcome to Todo App!")
        while True:
            self.display_main_menu()
            choice = self.get_user_choice()
            if choice == 6:
                print("Goodbye!")
                break
            self.handle_choice(choice)
