"""CLI interface for the Todo application using Rich library."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box

from src.storage import TaskStorage, TaskNotFoundError
from src.models import ValidationError


class TodoCLI:
    """Command-line interface for the Todo application.

    Provides a menu-driven interface for managing tasks with
    Rich-formatted output.
    """

    def __init__(self) -> None:
        """Initialize the CLI with a console and storage."""
        self.console = Console()
        self.storage = TaskStorage()

    def display_menu(self) -> None:
        """Display the main menu."""
        menu_text = (
            "[bold cyan]1.[/] Add Task\n"
            "[bold cyan]2.[/] View All Tasks\n"
            "[bold cyan]3.[/] Update Task\n"
            "[bold cyan]4.[/] Delete Task\n"
            "[bold cyan]5.[/] Mark Complete/Incomplete\n"
            "[bold cyan]6.[/] Exit"
        )
        self.console.print(Panel(menu_text, title="Todo App Menu", box=box.ROUNDED))

    def add_task(self) -> None:
        """Handle the add task flow."""
        self.console.print("\n[bold]Add New Task[/bold]\n")

        title = Prompt.ask("[cyan]Enter task title[/cyan]")
        description = Prompt.ask(
            "[cyan]Enter description (optional)[/cyan]", default=""
        )

        try:
            task = self.storage.add_task(title, description)
            self.console.print(
                f"\n[green]Task created successfully![/green] ID: [bold]{task.id[:8]}...[/bold]\n"
            )
        except ValidationError as e:
            self.console.print(f"\n[red]Error:[/red] {e}\n")

    def view_tasks(self) -> None:
        """Display all tasks in a formatted table."""
        tasks = self.storage.get_all_tasks()

        if not tasks:
            self.console.print(
                "\n[yellow]No tasks found. Add a task to get started![/yellow]\n"
            )
            return

        table = Table(title="All Tasks", box=box.ROUNDED)
        table.add_column("ID", style="dim", width=12)
        table.add_column("Title", style="cyan", min_width=20)
        table.add_column("Status", justify="center", width=12)
        table.add_column("Description", max_width=30)

        for task in tasks:
            task_id = f"{task.id[:8]}..."
            status = "[green]Complete[/green]" if task.completed else "[yellow]Incomplete[/yellow]"
            desc = task.description[:27] + "..." if len(task.description) > 30 else task.description

            table.add_row(task_id, task.title, status, desc)

        self.console.print()
        self.console.print(table)
        self.console.print()

    def update_task(self) -> None:
        """Handle the update task flow."""
        self.console.print("\n[bold]Update Task[/bold]\n")

        task_id = Prompt.ask("[cyan]Enter task ID[/cyan]")

        task = self.storage.get_task_by_id(task_id)
        if task is None:
            self.console.print(f"\n[red]Error:[/red] Task with ID {task_id} not found\n")
            return

        self.console.print(f"\nCurrent title: [bold]{task.title}[/bold]")
        self.console.print(f"Current description: {task.description or '(none)'}\n")

        new_title = Prompt.ask(
            "[cyan]New title (press Enter to keep current)[/cyan]", default=""
        )
        new_description = Prompt.ask(
            "[cyan]New description (press Enter to keep current)[/cyan]", default=""
        )

        try:
            self.storage.update_task(
                task_id,
                title=new_title if new_title else None,
                description=new_description if new_description else None,
            )
            self.console.print("\n[green]Task updated successfully![/green]\n")
        except ValidationError as e:
            self.console.print(f"\n[red]Error:[/red] {e}\n")

    def delete_task(self) -> None:
        """Handle the delete task flow with confirmation."""
        self.console.print("\n[bold]Delete Task[/bold]\n")

        task_id = Prompt.ask("[cyan]Enter task ID[/cyan]")

        task = self.storage.get_task_by_id(task_id)
        if task is None:
            self.console.print(f"\n[red]Error:[/red] Task with ID {task_id} not found\n")
            return

        self.console.print(f"\nTask to delete: [bold]{task.title}[/bold]")
        self.console.print(f"Description: {task.description or '(none)'}\n")

        if Confirm.ask("[yellow]Are you sure you want to delete this task?[/yellow]"):
            self.storage.delete_task(task_id)
            self.console.print("\n[green]Task deleted successfully![/green]\n")
        else:
            self.console.print("\n[dim]Deletion cancelled.[/dim]\n")

    def toggle_complete(self) -> None:
        """Handle the mark complete/incomplete flow."""
        self.console.print("\n[bold]Mark Complete/Incomplete[/bold]\n")

        task_id = Prompt.ask("[cyan]Enter task ID[/cyan]")

        try:
            task = self.storage.toggle_complete(task_id)
            status = "complete" if task.completed else "incomplete"
            self.console.print(
                f"\n[green]Task marked as {status}![/green] - {task.title}\n"
            )
        except TaskNotFoundError:
            self.console.print(f"\n[red]Error:[/red] Task with ID {task_id} not found\n")

    def run(self) -> None:
        """Run the main application loop."""
        self.console.print("\n[bold blue]Welcome to Todo App![/bold blue]\n")

        while True:
            self.display_menu()
            choice = Prompt.ask("\n[bold]Enter choice[/bold]", choices=["1", "2", "3", "4", "5", "6"], show_choices=False)

            match choice:
                case "1":
                    self.add_task()
                case "2":
                    self.view_tasks()
                case "3":
                    self.update_task()
                case "4":
                    self.delete_task()
                case "5":
                    self.toggle_complete()
                case "6":
                    self.console.print("\n[bold blue]Goodbye![/bold blue]\n")
                    break
