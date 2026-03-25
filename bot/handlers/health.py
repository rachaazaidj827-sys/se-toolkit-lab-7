"""Handler for /health command."""


def handle_health(user_input: str = "") -> str:
    """Handle the /health command.

    Args:
        user_input: Optional input from user (unused for /health).

    Returns:
        Backend health status.
    """
    return "Backend status: OK (placeholder)"
