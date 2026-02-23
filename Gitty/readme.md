# 🦊 Gitty: GitHub & GitLab to Discord Webhook 🚀

Hi there! **Gitty** is a cute but powerful bridge that tracks activity (commits, issues, merge requests...) on GitHub and GitLab and sends this data elegantly to your Discord channel.

It was designed to help you monitor your projects from a single place and stay in sync with your team (or yourself).

---

## ✨ Features

* **Dual Support:** Can fetch data from both GitHub and GitLab.
* **SQLite Database:** Tracks operations and flows with `git_flow.db`, ensuring nothing is forgotten.
* **Docker Ready:** Run it directly or containerize it with Docker.
* **Webhook Integration:** Delivers notifications instantly using the power of Discord.

---

## 📂 Project Structure

Let’s take a look at what’s cooking in Gitty’s kitchen:

```text
.
├── database/            # Database logic and SQLite file
├── src/
│   ├── main.py          # Main application entry point
│   └── services/        # GitHub, GitLab, and Webhook services
├── Dockerfile           # Containerization file
├── requirements.txt     # Required libraries
└── script/run.sh        # Quick start script
```

# 🚀 Quick Start

## 1. Configure Token Permissions
For the project to work correctly, your tokens must have the following permissions:
**GitLab (Personal Access Token)**
* `api`
* `read_api`
* `read_repository`

**GitHub (Fine-grained Personal Access Token)**
* **Repository Access: All Repositories**
* **Permissions:**
* * `Pull Requests` [readyonly]
* * `Issues` [readyonly]
* * `Contents` [readyonly]
* * `Metadata` [readyonly]

## 2. Preparation
First, clone the repo and enter the project directory:

```bash
git clone <repo-url>
cd discord-bot/Gitty
```

## 3. Configuration (.env)

```env
DB_DIR="database"
DB_NAME="git_flow.db"

GITHUB_TOKEN="ghp_your_github_token_here"
GITLAB_TOKEN="glpat-your_gitlab_token_here"

WEBHOOK_STATS="[https://discord.com/api/webhooks/.../](https://discord.com/api/webhooks/.../)"
WEBHOOK_UPDATES="[https://discord.com/api/webhooks/.../](https://discord.com/api/webhooks/.../)"
WEBHOOK_PIPELINES="[https://discord.com/api/webhooks/.../](https://discord.com/api/webhooks/.../)"
```
## 4. Install Dependencies
Create your virtual environment and install the libraries:
```bash
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 5. Run
Activate the virtual environment and run the application:
`python src/main.py`
# 🛠️ Tech Stack
* **Language:** *Python 3.13*
* *DB:** *SQLite*
* **Deployment:** *Docker & Shell Script*
