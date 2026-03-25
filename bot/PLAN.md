# Bot Development Plan

## Overview

This document outlines the implementation plan for the LMS Telegram Bot across four tasks. The bot provides students with access to their learning management system data through a Telegram interface, including lab information, scores, and backend health status.

## Architecture

The bot follows a **separation of concerns** pattern with three layers:

1. **Handlers** (`bot/handlers/`) - Pure functions that take input and return text. They have no dependency on Telegram, making them testable in isolation and reusable across different interfaces.

2. **Services** (`bot/services/`) - External API clients for the LMS backend and LLM. These handle HTTP requests, authentication, and error handling.

3. **Transport** (`bot/bot.py`) - The Telegram bot client that receives messages and routes them to handlers. Also provides `--test` mode for offline testing.

## Task 1: Scaffold (Current)

- Create project structure with `pyproject.toml`
- Implement handler interface with placeholder responses
- Add `--test` mode for CLI testing without Telegram
- Create configuration loading from `.env.bot.secret`

## Task 2: Backend Integration

- Implement `LmsApiService` for HTTP requests to the LMS backend
- Add Bearer token authentication using `LMS_API_KEY`
- Update handlers to fetch real data:
  - `/health` - GET `/health` endpoint
  - `/labs` - GET `/items/` filtered by type=lab
  - `/scores` - GET `/scores/` with user identification

## Task 3: Intent Routing with LLM

- Implement `LlmService` for LLM API calls
- Add tool descriptions for each handler
- Create intent router that uses the LLM to determine which tool to call
- Handle natural language queries like "what labs are available" or "show my scores for lab 4"

## Task 4: Deployment

- Dockerize the bot
- Configure Docker networking to reach backend and LLM services
- Set up health checks and restart policies
- Deploy to VM alongside backend and Qwen Code API

## Testing Strategy

- Unit tests for handlers (pure functions)
- Integration tests for services (mock HTTP)
- Manual testing via `--test` mode
- End-to-end testing in Telegram

## Environment Variables

| Variable | Description | Source |
|----------|-------------|--------|
| `BOT_TOKEN` | Telegram bot token | BotFather |
| `LMS_API_BASE_URL` | Backend API URL | VM deployment |
| `LMS_API_KEY` | Backend API key | `.env.docker.secret` |
| `LLM_API_KEY` | LLM API key | Qwen Code API |
| `LLM_API_BASE_URL` | LLM API URL | VM deployment |
| `LLM_API_MODEL` | Model name | Qwen Code API |
