"""Handler for /labs command."""

from bot.config import config
from bot.services.lms_api import LmsApiService, LmsApiError


def handle_labs(user_input: str = "") -> str:
    """Handle the /labs command.

    Args:
        user_input: Optional input from user (unused for /labs).

    Returns:
        Formatted list of available labs.
    """
    try:
        api = LmsApiService(config.lms_api_base_url, config.lms_api_key)
        items = api.get_items()
        
        # Filter for labs only (type == "lab")
        labs = [item for item in items if item.get("type") == "lab"]
        
        if not labs:
            return "No labs available."
        
        # Format the list
        lines = ["Available labs:"]
        for lab in labs:
            title = lab.get("title", "Unknown").strip()
            lines.append(f"- {title}")
        
        return "\n".join(lines)
    except LmsApiError as e:
        return f"Failed to fetch labs: {str(e)}"
