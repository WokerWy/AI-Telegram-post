# AI Telegram Scheduler Bot

A production-ready backend service for **parsing news, generating AI-powered posts**, and **scheduling Telegram messages** for delivery at a specified time.

Designed with reliability, atomic execution, and future scalability in mind.

---

## 📜 License

This project is licensed under a **Proprietary Non-Commercial License**.

You are allowed to view and evaluate the source code for personal
or educational purposes only.

❌ Commercial use, redistribution, or reuse of the core logic
without explicit written permission is strictly prohibited.

© 2026 Arslonbek Erkinov. All rights reserved.


---

## 🚀 Features

- 📰 **News parsing from external sources**
- 🤖 **AI-powered post generation**
- ✍️ Automatic content preparation for Telegram
- 📆 Schedule Telegram messages for a specific datetime (UTC-based)
- 🔒 Atomic database locking (no duplicate delivery)
- 🔁 Jobs survive application restarts
- 🧠 Clear job lifecycle: scheduled → sent / failed
- 🗄 SQLite database with WAL mode enabled
- 📜 Structured logging for observability
- ⚙️ Clean architecture (API / Services / Repositories / Scheduler)

---

## 🧠 Core Capabilities

### 📰 News Parsing
The system can fetch and parse news data from external sources (RSS / APIs / scrapers), normalize content, and prepare it for further processing.

Parsed data is stored and can be:
- reviewed
- enriched
- passed to AI for generation

---

### 🤖 AI Post Generation
An integrated AI layer is used to generate Telegram-ready posts:

- Headline rewriting
- Summary generation
- Tone adaptation (news / neutral / promotional)
- Emoji & formatting optimization
- Language-agnostic (model-based)

AI generation is **decoupled** from scheduling logic and can be extended independently.

---

### 📆 Smart Scheduling
Generated (or manual) posts can be scheduled for future delivery with:

- Timezone-safe UTC normalization
- Validation against past timestamps
- Automatic job recovery after restart

---

## 🏗 Architecture Overview
```
API (FastAPI)
│
├── News Parser
│
├── AI Content Generator
│
▼
Scheduler Service
│
▼
SQLite Database (WAL, Atomic Lock)
│
▼
APScheduler
│
▼
Telegram Bot API
```

## 🧠 Key Design Decisions

### Atomic Execution
Each scheduled post is protected by an **atomic database lock**, ensuring:

- No duplicate sends
- Safe concurrent execution
- Idempotent job processing
- Protection against race conditions

This design mirrors **row-level locking patterns** used in PostgreSQL.

---

### SQLite + WAL
SQLite was intentionally chosen for the first stage:
- Reliable for single-instance schedulers
- WAL mode allows concurrent reads/writes
- Easy migration to PostgreSQL in the future

### APScheduler
- Precise job execution
- Jobs persist in memory and survive restarts
- Clean integration with Python services

---

## 📦 Tech Stack

- **Python 3.11+**
- **FastAPI**
- **APScheduler**
- **SQLAlchemy**
- **SQLite (WAL mode)**
- **Aiogram (Telegram Bot API)**
- **AI provider (OpenAI / local LLM ready)**


## 📂 Project Structure 
```
app/
├── api/            # HTTP API endpoints
├── services/       # Business logic
├── scheduler/      # APScheduler jobs & tasks
├── repositories/   # DB access layer
├── models/         # SQLAlchemy models
├── database.py     # DB engine & session
├── config.py       # Settings (.env)
├── telegram/       # Telegram client
├── main.py         # FastAPI entrypoint
logs/
```


---

## 🔌 API Example

### Schedule a message

**POST** `/api/schedule`

```json
{
  "text": "Hello from the scheduler 🚀",
  "publish_at": "2026-01-06T18:00:00+03:00"
}
```
## Response
```
{
  "status": "scheduled",
  "publish_at": "2026-01-06T15:00:00+00:00"
}

```

## 🧪 Reliability Guarantees
- A message is sent only once
- If execution fails:
- Status is marked as failed
- Error is stored in DB
- Duplicate execution attempts are automatically blocked

## 🛠 Future Improvements (Planned)

The following enhancements are intentionally prepared but not enabled yet:
- 🐘 PostgreSQL support (row-level locking, job store)
- 🐳 Docker & Docker Compose
- 🔴 Redis (distributed locks & queues)
- 📊 Admin dashboard
- 🔁 Retry backoff strategies
- ☁️ Horizontal scaling
