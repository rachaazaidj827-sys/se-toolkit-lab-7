"""Handler for /start command."""

from bot.config import config


def handle_start(user_input: str = "") -> str:
    """Handle the /start command.

    Args:
        user_input: Optional input from user (unused for /start).

    Returns:
        Welcome message with bot name.
    """
    return "Welcome to the LMS Bot! Use /help to see available commands."
