\# 🤖 Email Agent — Autonomous Job Email Handler



An AI-powered email triage agent that automatically identifies, classifies, and takes

user-approved actions on job-related emails. Built with Python, Claude AI, and the Gmail API.



> \*\*Privacy-first · Human-in-the-loop · Conservative by default\*\*

> The agent never sends, deletes, or modifies emails without your explicit approval.



\---



\## ✨ Features



| Capability | Description |

|---|---|

| 🎯 \*\*Priority Classification\*\* | Classifies emails as HIGH / NORMAL / LOW using a rule engine + Claude AI |

| 🏷️ \*\*Auto-labelling\*\* | Assigns Gmail labels (`Job/Important`, `Job/Normal`, `Job/Low`) automatically |

| 🚩 \*\*Auto-flagging\*\* | Flags high-priority emails (interview invites, offers, deadlines) instantly |

| 📝 \*\*Draft Reply Templates\*\* | Generates reply drafts for approval — never sends without you |

| ⏰ \*\*Deadline Reminders\*\* | Detects deadlines and queues calendar reminders |

| 📋 \*\*Email Summaries\*\* | Condenses long emails into 3-bullet summaries via Claude |

| 🔁 \*\*Learning Loop\*\* | Improves classification accuracy from your approve/reject feedback |

| 🔐 \*\*Full Audit Log\*\* | Every decision and action is logged with timestamp and undo support |



\---



\## 🏗️ Architecture
Gmail / IMAP

│

▼

┌─────────────────┐

│  Privacy Gate   │  ← PII scrub, body truncation, HTML sanitization

└────────┬────────┘

│

▼

┌─────────────────┐     ┌──────────────────┐

│  Rule Engine    │────▶│  Claude Classifier│  (fallback for unmatched)

└────────┬────────┘     └────────┬─────────┘

└──────────┬────────────┘

▼

┌─────────────────┐

│  Action Planner │  ← maps priority → candidate actions

└────────┬────────┘

│

┌─────────┴──────────┐

▼                    ▼

Auto-execute          Review Queue

(flag, label)    (draft reply, send, delete)

│

▼

Review Console

(approve / reject)
---



\## 🛠️ Tech Stack



| Layer | Technology | Reason |

|---|---|---|

| Language | Python 3.11+ | Async support, rich ecosystem |

| AI | Claude Sonnet 4 (Anthropic) | Best accuracy for email classification |

| Email I/O | Gmail API + `imapclient` | OAuth2 secure, supports labels |

| Scheduler | APScheduler | Lightweight in-process polling |

| API Server | FastAPI + Uvicorn | Review console backend |

| CLI Output | Rich | Coloured Windows-compatible terminal |

| Config | Pydantic Settings | Type-safe `.env` loading |

| Packaging | uv | Fast, modern Python package manager |



\---



\## 📁 Project Structure
email-agent/

├── src/

│   ├── config.py          # Settings loaded from .env

│   ├── main.py            # Entry point + scheduler

│   ├── ingestion/         # Gmail/IMAP polling

│   ├── classifier/        # Rule engine + Claude classifier

│   ├── planner/           # Action planning + guardrails

│   ├── executor/          # Safe action execution

│   ├── console/           # FastAPI review console

│   └── storage/           # SQLite + audit log

├── tests/                 # Pytest test suite

├── .env.example           # Template — copy to .env and fill in

├── credentials.json       # ⚠️ NOT committed — download from Google Cloud

├── pyproject.toml         # Project metadata + dependencies

└── README.md
---



\## ⚡ Quick Start



\### Prerequisites



\- Python 3.11+

\- \[uv](https://astral.sh/uv) package manager

\- A Gmail account

\- An \[Anthropic API key](https://console.anthropic.com)



\### 1. Clone the repo



```bash

git clone https://github.com/YOUR\_USERNAME/email-agent.git

cd email-agent

```



\### 2. Install dependencies



```bash

uv pip install -e .

```



\### 3. Set up environment variables



```bash

copy .env.example .env

notepad .env        # fill in your keys

```



\### 4. Set up Gmail OAuth2



1\. Go to \[Google Cloud Console](https://console.cloud.google.com)

2\. Create a project → Enable \*\*Gmail API\*\*

3\. Configure \*\*OAuth consent screen\*\* → External → add your email as test user

4\. Create credentials → \*\*OAuth client ID\*\* → Desktop app

5\. Download JSON → rename to `credentials.json` → place in project root



\### 5. Authenticate with Gmail (one-time)



```bash

python -c "

from google\_auth\_oauthlib.flow import InstalledAppFlow

from pathlib import Path

flow = InstalledAppFlow.from\_client\_secrets\_file(

&#x20;   'credentials.json',

&#x20;   scopes=\['https://www.googleapis.com/auth/gmail.modify']

)

creds = flow.run\_local\_server(port=0)

Path('token.json').write\_text(creds.to\_json())

print('Done! token.json saved.')

"

```



\### 6. Run the agent



```bash

\# Activate virtual environment (Windows)

.venv\\Scripts\\activate



\# Start the agent

python src\\main.py

```



\---



\## 🔐 Safety \& Privacy



| Guardrail | Detail |

|---|---|

| \*\*No auto-send\*\* | `ALLOW\_AUTO\_SEND=false` by default — requires explicit opt-in |

| \*\*Minimal scopes\*\* | OAuth2 requests only `gmail.modify` — no full account access |

| \*\*PII scrubbing\*\* | Email bodies are truncated and PII-scrubbed before any LLM call |

| \*\*Local storage\*\* | All data stored locally — nothing sent to third parties except Anthropic API |

| \*\*Audit log\*\* | Every action logged with timestamp, reversible within 24 h |

| \*\*Data retention\*\* | Emails and summaries auto-purged after `RETENTION\_DAYS` (default 30) |

| \*\*Credentials\*\* | `credentials.json` and `token.json` are in `.gitignore` — never committed |



\---



\## 📋 Classification Rules



The rule engine catches common patterns instantly (no LLM cost):



```yaml

HIGH priority  → interview invites, job offers, deadlines <72h,

&#x20;                background checks, hiring manager emails

NORMAL priority → recruiter outreach, application confirmations,

&#x20;                 networking, salary threads

LOW priority   → newsletters, automated job alerts, rejections

```



Claude AI handles anything the rule engine doesn't match, with a conservative

bias (prefers HIGH over LOW when uncertain).



\---



\## 🗺️ Roadmap



\- \[x] Project scaffold + config system

\- \[x] Entry point + scheduler

\- \[ ] Gmail ingestion module (`src/ingestion/gmail.py`)

\- \[ ] Rule engine + Claude classifier (`src/classifier/engine.py`)

\- \[ ] Action planner + guardrails (`src/planner/actions.py`)

\- \[ ] Executor (`src/executor/actions.py`)

\- \[ ] SQLite audit log (`src/storage/`)

\- \[ ] FastAPI review console (`src/console/`)

\- \[ ] React frontend dashboard

\- \[ ] Outlook / Microsoft Graph support

\- \[ ] Desktop tray icon + system notifications

\- \[ ] Learning loop from feedback



\---



\## 🧪 Running Tests



```bash

uv add --dev pytest pytest-asyncio

python -m pytest tests/ -v

```



\---



\## 🤝 Contributing



1\. Fork the repo

2\. Create a feature branch: `git checkout -b feature/gmail-ingestion`

3\. Commit your changes: `git commit -m "feat: add Gmail ingestion module"`

4\. Push: `git push origin feature/gmail-ingestion`

5\. Open a Pull Request



\---



\## 📄 License



MIT License — see \[LICENSE](LICENSE) for details.



\---



\## ⚠️ Disclaimer



This project is for personal productivity use. Always review AI-generated

reply drafts before sending. The author is not responsible for any

unintended email actions.

