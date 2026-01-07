"""Entry point for the Todo application."""

from src.cli import TodoCLI


def main() -> None:
    """Run the Todo CLI application."""
    cli = TodoCLI()
    try:
        cli.run()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")


if __name__ == "__main__":
    main()
