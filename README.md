# Lab 7 — Build a Client with an AI Coding Agent

[Sync your fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork#syncing-a-fork-branch-from-the-command-line) regularly — the lab gets updated.

## Product brief

> Build a Telegram bot that lets users interact with the LMS backend through chat. Users should be able to check system health, browse labs and scores, and ask questions in plain language. The bot should use an LLM to understand what the user wants and fetch the right data. Deploy it alongside the existing backend on the VM.

This is what a customer might tell you. Your job is to turn it into a working product using an AI coding agent (Qwen Code) as your development partner.

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────┐   │
│  │  Telegram    │────▶│  Your Bot                        │   │
│  │  User        │◀────│  (aiogram / python-telegram-bot) │   │
│  └──────────────┘     └──────┬───────────────────────────┘   │
│                              │                               │
│                              │ slash commands + plain text    │
│                              ├───────▶ /start, /help         │
│                              ├───────▶ /health, /labs        │
│                              ├───────▶ intent router ──▶ LLM │
│                              │                    │          │
│                              │                    ▼          │
│  ┌──────────────┐     ┌──────┴───────┐    tools/actions      │
│  │  Docker      │     │  LMS Backend │◀───── GET /items      │
│  │  Compose     │     │  (FastAPI)   │◀───── GET /analytics  │
│  │              │     │  + PostgreSQL│◀───── POST /sync      │
│  └──────────────┘     └──────────────┘                       │
└──────────────────────────────────────────────────────────────┘
```

## Requirements

### P0 — Must have

1. Testable handler architecture — handlers work without Telegram
2. CLI test mode: `cd bot && uv run bot.py --test "/command"` prints response to stdout
3. `/start` — welcome message
4. `/help` — lists all available commands
5. `/health` — calls backend, reports up/down status
6. `/labs` — lists available labs
7. `/scores <lab>` — per-task pass rates
8. Error handling — backend down produces a friendly message, not a crash

### P1 — Should have

1. Natural language intent routing — plain text interpreted by LLM
2. All 9 backend endpoints wrapped as LLM tools
3. Inline keyboard buttons for common actions
4. Multi-step reasoning (LLM chains multiple API calls)

### P2 — Nice to have

1. Rich formatting (tables, charts as images)
2. Response caching
3. Conversation context (multi-turn)

### P3 — Deployment

1. Bot containerized with Dockerfile
2. Added as service in `docker-compose.yml`
3. Deployed and running on VM
4. README documents deployment

## Learning advice

Notice the progression above: **product brief** (vague customer ask) → **prioritized requirements** (structured) → **task specifications** (precise deliverables + acceptance criteria). This is how engineering work flows.

You are not following step-by-step instructions — you are building a product with an AI coding agent. The learning comes from planning, building, testing, and debugging iteratively.

## Learning outcomes

By the end of this lab, you should be able to say:

1. I turned a vague product brief into a working Telegram bot.
2. I can ask it questions in plain language and it fetches the right data.
3. I used an AI coding agent to plan and build the whole thing.

## Tasks

### Prerequisites

1. Complete the [lab setup](./lab/setup/setup-simple.md#lab-setup)

> **Note**: First time in this course? Do the [full setup](./lab/setup/setup-full.md#lab-setup) instead.

### Required

1. [Plan and Scaffold](./lab/tasks/required/task-1.md) — P0: project structure + `--test` mode
2. [Backend Integration](./lab/tasks/required/task-2.md) — P0: slash commands + real data
3. [Intent-Based Natural Language Routing](./lab/tasks/required/task-3.md) — P1: LLM tool use
4. [Containerize and Document](./lab/tasks/required/task-4.md) — P3: containerize + deploy

## Deploy

This section explains how to deploy the Telegram bot alongside the LMS backend on your VM.

### Prerequisites

Before deploying, ensure you have:

1. **VM access** — SSH access to your university VM
2. **Telegram bot token** — Get from [@BotFather](https://t.me/BotFather) with `/newbot`
3. **LLM API access** — Qwen Code API running on your VM (see setup step 1.9)
4. **Environment files** — `.env.docker.secret` with all required variables

### Environment variables

The bot requires these variables in `.env.docker.secret`:

```text
# Telegram Bot
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyz

# LMS API (inside Docker, use service name not localhost)
LMS_API_BASE_URL=http://backend:8000
LMS_API_KEY=my-secret-api-key

# LLM API (use host.docker.internal for cross-network access)
LLM_API_KEY=my-qwen-api-key
LLM_API_BASE_URL=http://host.docker.internal:42005/v1
LLM_API_MODEL=coder-model
```

> **Important**: Inside Docker, `localhost` refers to the container itself. Use `http://backend:8000` to reach the backend service, and `host.docker.internal` to reach services on the VM host (like the Qwen Code API).

### Deploy steps

1. **Clone your fork on the VM** (if not already done):
   ```terminal
   git clone https://github.com/YOUR_USERNAME/se-toolkit-lab-7 ~/se-toolkit-lab-7
   cd ~/se-toolkit-lab-7
   ```

2. **Create environment files**:
   ```terminal
   cp .env.docker.example .env.docker.secret
   nano .env.docker.secret  # Fill in all values
   ```

3. **Start all services with Docker Compose**:
   ```terminal
   docker compose --env-file .env.docker.secret up --build -d
   ```

4. **Verify services are running**:
   ```terminal
   docker compose --env-file .env.docker.secret ps
   ```
   
   You should see:
   ```
   NAME                STATUS
   backend             Up
   bot                 Up
   caddy               Up
   postgres            Up (healthy)
   pgadmin             Up
   ```

5. **Populate the database** (if not already done):
   ```terminal
   curl -X POST http://localhost:42002/pipeline/sync \
     -H "Authorization: Bearer my-secret-api-key" \
     -H "Content-Type: application/json" \
     -d '{}'
   ```

### Verify deployment

1. **Check bot container logs**:
   ```terminal
   docker compose --env-file .env.docker.secret logs bot --tail 20
   ```
   
   Look for:
   - "Application started" — bot connected to Telegram
   - "HTTP Request: POST .../getUpdates" — bot is polling

2. **Test in Telegram**:
   - Send `/start` — should see welcome message with inline buttons
   - Send `/health` — should see backend status
   - Send "what labs are available?" — should list labs from backend
   - Send "which lab has the lowest pass rate?" — should analyze and respond

3. **Check backend is healthy**:
   ```terminal
   curl -sf http://localhost:42002/docs
   ```

### Troubleshooting

| Symptom | Solution |
|---------|----------|
| Bot container keeps restarting | Check logs: `docker compose logs bot`. Usually missing env var or import error. |
| `/health` fails in container | `LMS_API_BASE_URL` must be `http://backend:8000` (not `localhost:42002`). |
| LLM queries fail | `LLM_API_BASE_URL` must use `host.docker.internal` (not `localhost`). |
| "BOT_TOKEN is required" | Ensure `BOT_TOKEN` is set in `.env.docker.secret`. |
| Build fails at `uv sync` | Ensure `uv.lock` is copied in Dockerfile. |

### Stop and restart

```terminal
# Stop all services
docker compose --env-file .env.docker.secret down

# Restart bot only
docker compose --env-file .env.docker.secret restart bot

# Rebuild and restart after code changes
docker compose --env-file .env.docker.secret up --build -d
```
