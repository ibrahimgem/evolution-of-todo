"""Main entry point for the Todo application."""

from cli.menu import TodoMenu
from services.task_service import TaskService


def main() -> None:
    """Initialize and run the todo application."""
    service = TaskService()
    menu = TodoMenu(service)
    menu.run()


if __name__ == "__main__":
    main()
