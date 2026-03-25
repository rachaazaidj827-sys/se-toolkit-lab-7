"""Handler for /health command."""

from bot.config import config
from bot.services.lms_api import LmsApiService, LmsApiError


def handle_health(user_input: str = "") -> str:
    """Handle the /health command.

    Args:
        user_input: Optional input from user (unused for /health).

    Returns:
        Backend health status or error message.
    """
    try:
        api = LmsApiService(config.lms_api_base_url, config.lms_api_key)
        result = api.health_check()
        return f"Backend is healthy. {result['item_count']} items available."
    except LmsApiError as e:
        return f"Backend error: {str(e)}"
