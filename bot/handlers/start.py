"""Handler for /start command."""


def handle_start(user_input: str = "") -> str:
    """Handle the /start command.

    Args:
        user_input: Optional input from user (unused for /start).

    Returns:
        Welcome message.
    """
    return "Welcome to the LMS Bot! Use /help to see available commands."
