"""Handler for /help command."""


def handle_help(user_input: str = "") -> str:
    """Handle the /help command.

    Args:
        user_input: Optional input from user (unused for /help).

    Returns:
        List of available commands with descriptions.
    """
    return """Available commands:
/start - Welcome message
/help - Show this help message
/health - Check backend status
/labs - List available labs
/scores <lab> - View scores for a specific lab (e.g., /scores lab-04)"""
