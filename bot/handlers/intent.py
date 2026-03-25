"""Intent-based natural language router using LLM."""

import sys
from bot.config import config
from bot.services.llm import LlmService, LlmError


# Tool schemas for the LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all labs and tasks available in the system",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of enrolled learners and their groups",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submission timeline (submissions per day) for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group performance and student counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top learners to return (default: 5)",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL pipeline to refresh data from autochecker",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# System prompt for the LLM
SYSTEM_PROMPT = """You are an LMS (Learning Management System) assistant. You help students understand their progress, lab performance, and course analytics.

You have access to tools that fetch real data from the backend. When a user asks a question:
1. Think about what data you need to answer
2. Call the appropriate tools to get that data
3. Analyze the results
4. Provide a clear, helpful answer based on the actual data

Available tools:
- get_items: List all labs and tasks
- get_learners: List enrolled students
- get_scores: Score distribution for a lab
- get_pass_rates: Per-task pass rates for a lab
- get_timeline: Submission timeline for a lab
- get_groups: Per-group performance
- get_top_learners: Top students for a lab
- get_completion_rate: Completion percentage for a lab
- trigger_sync: Refresh data from autochecker

For questions about specific labs, use the lab identifier format "lab-XX" (e.g., "lab-01", "lab-04").

If the user asks a greeting or simple question that doesn't need data, respond naturally without calling tools.

If you don't understand the question, ask for clarification or suggest what you can help with.

Always base your answers on the actual data returned by tools - don't make up numbers."""


def handle_intent(user_input: str = "") -> str:
    """Handle natural language intent routing.

    Args:
        user_input: User's natural language query.

    Returns:
        LLM-generated response based on tool results.
    """
    # Check for simple greetings or fallback cases
    lower_input = user_input.lower().strip()

    # Simple greetings - respond without LLM
    if lower_input in ["hello", "hi", "hey", "start"]:
        return "Hello! I'm your LMS assistant. I can help you with:\n- What labs are available\n- Show scores for a lab\n- Which lab has the lowest pass rate\n- Top students in a lab\n- And more! Just ask me anything about your course progress."

    # Gibberish or too short - helpful fallback
    if len(lower_input) < 3 or (lower_input.isalpha() and len(lower_input) < 5):
        return "I didn't quite understand that. Here's what I can help you with:\n- 'what labs are available?'\n- 'show me scores for lab 4'\n- 'which lab has the lowest pass rate?'\n- 'who are the top students?'\n\nTry asking about labs, scores, or student performance!"

    # Ambiguous lab reference
    if lower_input.startswith("lab ") and len(lower_input.split()) <= 3:
        lab_num = lower_input.replace("lab ", "").strip()
        return f"You mentioned lab {lab_num}. What would you like to know about it? I can show you:\n- Pass rates for each task\n- Score distribution\n- Top students\n- Group performance\n- Completion rate\n\nJust ask, for example: 'show me scores for lab {lab_num}'"

    try:
        llm = LlmService(
            config.llm_api_key, config.llm_api_base_url, config.llm_api_model
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ]

        response = llm.chat_with_tools(messages, TOOLS)

        # Debug output to stderr
        print(f"[response] LLM returned answer", file=sys.stderr)

        return response

    except LlmError as e:
        return f"LLM error: {str(e)}"
    except Exception as e:
        return f"Error processing your question: {str(e)}"
