
# NL2SQL Assistant

**Convert Natural Language Questions to SQL Queries** and execute them on your database using LLMs like OpenAI's GPT.

---

## Features

* 🔍 Converts user questions to SQL using GPT-4o
* 📊 Executes SQL queries on a live Postgres
* 📂 Extracts schema context dynamically (with caching)
* ⚡ Caches LLM outputs and query results for speed
* 🔐 Validates SQL for safety (prevents risky modifications)
* 📈 Logs token usage, queries, and performance

---

## 🏗️ Project Structure


nl2sql-assistant/

├── app/                        # FastAPI Backend
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           └── query.py         # Endpoints for /generate-sql and /run-sql
│   ├── core/                        # App settings and logger
│   ├── db/                          # DB session and schema reflection
│   ├── llm/                         # Prompt templates and OpenAI calls
│   ├── models/                      # Pydantic schemas
│   ├── services/                    # SQL validation and execution logic
│   ├── utils/                       # Helpers for formatting, caching, etc.
│   └── main.py                      # FastAPI app entrypoint
│
├── frontend/
│   └── streamlit_app.py             # Streamlit UI
│
├── scripts/
│   └── setup_db.py                  # Initial DB setup
│
├── tests/                           # Unit and integration tests
│
├── docker/
│   └── docker-compose.yml          # Combined stack setup
│
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables (API keys, DB URL)
└── README.md                        # Project documentation

---

## ⚙️ Tech Stack

* **Backend** : FastAPI, SQLAlchemy (async)
* **LLM** : OpenAI GPT-4o
* **Cache** : diskcache (local), Redis (optional for prod)
* **Database** : PostgreSQL 
* **Container** : Docker + Docker Compose
* **Extras** : Loguru,Pydantic, Uvicorn

---

## 📦 Installation

### 1. Clone the Repo

https://github.com/devendraghormare/AI-projects.git

### 2. Set up `.env`

<code class="whitespace-pre! language-env"><span>OPENAI_API_KEY=your-openai-api-key
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
</span></code></div></div></pre>

### 3. Install Dependencies

<code class="whitespace-pre! language-bash"><span><span>pip install -r requirements.txt
</span></span></code></div></div></pre>

### 4. Run the Server

cd app

uvicorn main:app --reload

---

## 🐳 Docker Deployment

<code class="whitespace-pre! language-bash"><span><span>docker-compose up --build
</span></span></code></div></div></pre>

Make sure your `.env` is configured. Example `docker-compose.yml` supports:

* FastAPI app
* PostgreSQL with volume
* Redis (optional for caching)

---

## 📬 API Endpoints

* `POST /v1/query`: Accepts natural language and returns SQL + results

### Example Request

<code class="whitespace-pre! language-json"><span><span>{</span><span>
  </span><span>"question"</span><span>:</span><span></span><span>"Show me the top 5 products by sales"</span><span>,</span><span>
  </span><span>"allow_modifications"</span><span>:</span><span></span><span>false</span><span>
</span><span>}</span><span>
</span></span></code></div></div></pre>

---

## 📈 Logging & Caching

* **Diskcache** stores:
  * Schema for 1 hour
  * LLM outputs for 10 minutes
  * SELECT query results for 5 minutes
* Logs are written using Loguru with daily rotation.
