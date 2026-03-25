"""Handler for /scores command."""


def handle_scores(user_input: str = "") -> str:
    """Handle the /scores command.

    Args:
        user_input: Optional lab identifier (e.g., "lab-04").

    Returns:
        User's scores for the specified lab.
    """
    if user_input:
        return f"Scores for {user_input}: (placeholder - will fetch from backend)"
    return "Your scores: (placeholder - will fetch from backend)"
