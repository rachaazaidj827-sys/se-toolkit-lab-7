"""Handler for /help command."""


def handle_help(user_input: str = "") -> str:
    """Handle the /help command.

    Args:
        user_input: Optional input from user (unused for /help).

    Returns:
        List of available commands.
    """
    return """Available commands:
/start - Welcome message
/help - Show this help message
/health - Check backend status
/labs - List available labs
/scores - View your scores"""
