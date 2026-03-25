"""Handler for /scores command."""

from bot.config import config
from bot.services.lms_api import LmsApiService, LmsApiError


def handle_scores(user_input: str = "") -> str:
    """Handle the /scores command.

    Args:
        user_input: Lab identifier (e.g., "lab-04").

    Returns:
        Formatted pass rates for the specified lab.
    """
    if not user_input:
        return "Please specify a lab. Usage: /scores lab-04"
    
    try:
        api = LmsApiService(config.lms_api_base_url, config.lms_api_key)
        pass_rates = api.get_pass_rates(user_input)
        
        if not pass_rates:
            return f"No pass rate data available for {user_input}."
        
        # Format the list
        lines = [f"Pass rates for {user_input}:"]
        for task in pass_rates:
            task_name = task.get("task", "Unknown task")
            pass_rate = task.get("avg_score", 0)
            attempts = task.get("attempts", 0)
            lines.append(f"- {task_name}: {pass_rate:.1f}% ({attempts} attempts)")
        
        return "\n".join(lines)
    except LmsApiError as e:
        return f"Failed to fetch scores: {str(e)}"
