#!/usr/bin/env python3
"""LMS Telegram Bot entry point.

Usage:
    uv run bot.py              # Run as Telegram bot
    uv run bot.py --test "what labs are available"  # Test mode: print response to stdout
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_intent,
)
from bot.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_handler(command: str):
    """Get the handler function for a command.

    Args:
        command: The command string (e.g., "/start", "/help").

    Returns:
        The handler function for the command, or None if not found.
    """
    handlers = {
        "/start": handle_start,
        "/help": handle_help,
        "/health": handle_health,
        "/labs": handle_labs,
        "/scores": handle_scores,
    }
    # Extract command without arguments for routing
    cmd = command.split()[0] if command else ""
    return handlers.get(cmd)


def run_test_mode(user_input: str) -> None:
    """Run a command or natural language query in test mode.

    Args:
        user_input: The command or natural language query to test.
    """
    # Check if it's a slash command
    if user_input.startswith("/"):
        handler = get_handler(user_input)
        if handler is None:
            print(f"Unknown command: {user_input}. Use /help to see available commands.")
            sys.exit(0)

        # Extract arguments if present (for /scores)
        parts = user_input.split(maxsplit=1)
        arg = parts[1] if len(parts) > 1 else ""

        result = handler(arg)
        print(result)
    else:
        # Natural language query - use intent router
        result = handle_intent(user_input)
        print(result)

    sys.exit(0)


def run_telegram_bot() -> None:
    """Run the bot as a Telegram bot."""
    try:
        from aiogram import Bot, Dispatcher, types
        from aiogram.filters import Command
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    except ImportError:
        logger.error("aiogram not installed. Run: uv sync")
        sys.exit(1)

    if not config.bot_token:
        logger.error("BOT_TOKEN not set in .env.bot.secret")
        sys.exit(1)

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        """Handle /start with inline keyboard buttons."""
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📚 Available Labs", callback_data="labs"
                    ),
                    InlineKeyboardButton(
                        text="🏥 Health Check", callback_data="health"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="📊 My Scores", callback_data="scores_help"
                    ),
                    InlineKeyboardButton(
                        text="❓ Help", callback_data="help"
                    ),
                ],
            ]
        )
        await message.answer(handle_start(), reply_markup=keyboard)

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        await message.answer(handle_help())

    @dp.message(Command("health"))
    async def cmd_health(message: types.Message):
        await message.answer(handle_health())

    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message):
        await message.answer(handle_labs())

    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message):
        # Get the argument after /scores
        arg = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
        await message.answer(handle_scores(arg))

    @dp.message()
    async def handle_message(message: types.Message):
        """Handle natural language messages with intent routing."""
        user_text = message.text or ""
        if user_text.startswith("/"):
            return  # Let command handlers deal with this

        # Use intent router for natural language
        response = handle_intent(user_text)
        await message.answer(response)

    @dp.callback_query()
    async def handle_callback(callback: types.CallbackQuery):
        """Handle inline keyboard button clicks."""
        data = callback.data

        if data == "labs":
            await callback.message.answer(handle_labs())
        elif data == "health":
            await callback.message.answer(handle_health())
        elif data == "help":
            await callback.message.answer(handle_help())
        elif data == "scores_help":
            await callback.message.answer(
                "To view your scores, use:\n/scores lab-04\n\nReplace 'lab-04' with the lab number you want to check."
            )

        await callback.answer()

    logger.info("Bot starting...")
    dp.run_polling(bot)


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if len(sys.argv) < 3:
            print("Usage: uv run bot.py --test <query>")
            print("Examples:")
            print("  uv run bot.py --test '/start'")
            print('  uv run bot.py --test "what labs are available"')
            sys.exit(1)
        user_input = sys.argv[2]
        run_test_mode(user_input)
    else:
        run_telegram_bot()


if __name__ == "__main__":
    main()
