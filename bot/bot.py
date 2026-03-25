#!/usr/bin/env python3
"""LMS Telegram Bot entry point.

Usage:
    uv run bot.py              # Run as Telegram bot
    uv run bot.py --test "/start"  # Test mode: print response to stdout
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.handlers import handle_start, handle_help, handle_health, handle_labs, handle_scores
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


def run_test_mode(command: str) -> None:
    """Run a command in test mode and print the result.

    Args:
        command: The command to test (e.g., "/start", "/help").
    """
    handler = get_handler(command)
    if handler is None:
        print(f"Unknown command: {command}")
        sys.exit(1)

    # Extract arguments if present (for /scores)
    parts = command.split(maxsplit=1)
    arg = parts[1] if len(parts) > 1 else ""

    result = handler(arg)
    print(result)
    sys.exit(0)


def run_telegram_bot() -> None:
    """Run the bot as a Telegram bot."""
    try:
        from aiogram import Bot, Dispatcher, types
        from aiogram.filters import Command
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
        await message.answer(handle_start())

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

    logger.info("Bot starting...")
    dp.run_polling(bot)


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if len(sys.argv) < 3:
            print("Usage: uv run bot.py --test <command>")
            print("Example: uv run bot.py --test '/start'")
            sys.exit(1)
        command = sys.argv[2]
        run_test_mode(command)
    else:
        run_telegram_bot()


if __name__ == "__main__":
    main()
