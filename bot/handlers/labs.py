"""Handler for /labs command."""


def handle_labs(user_input: str = "") -> str:
    """Handle the /labs command.

    Args:
        user_input: Optional input from user (unused for /labs).

    Returns:
        List of available labs.
    """
    return "Available labs: Lab 01, Lab 02, Lab 03, Lab 04 (placeholder)"
