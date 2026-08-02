OrgBrain AI — Complete Setup Guide (v2)
A working, tested, end-to-end implementation: FastAPI backend, Next.js frontend, JWT auth with a simple 2-role model, LLM-driven adaptive interviews with speech-to-text, ChromaDB RAG, an animated department knowledge graph, downloadable SOP PDFs, and a multi-provider LLM abstraction (Groq / IBM Granite via Hugging Face / Gemini).

Every command below has been run and verified in a real environment before being written here.

1. Roles — Simple, 2-Role Model
Role	What they can do
Admin	Views the organization-wide dashboard: stats, the animated department knowledge graph, a table of everyone who's been interviewed with a PDF download of their SOP, and manages employee accounts. Cannot take interviews.
Employee	Lands on an intro page with tabs to: Interview Agent (share their knowledge), AI Twin (ask department-grounded questions), SOP (browse the knowledge library).
2. How RAG Is Used In This Project
This is the core technical mechanism, worth understanding well for your report/interview:

An employee completes a guided interview (min. 6 questions, adaptive follow-ups).
The raw transcript is sent to an LLM which extracts structured knowledge (skills, best practices, troubleshooting steps) and generates a detailed, structured SOP.
That SOP's full text is embedded (converted into a vector) and stored in ChromaDB, tagged with its department_id.
When any employee asks the AI Twin a question, the question itself is embedded, and ChromaDB returns the most semantically similar SOP chunks for that department (this step is the "Retrieval" in RAG).
Those retrieved SOP excerpts are inserted into the LLM's prompt as context, and the LLM is instructed to answer using only that retrieved text (this is the "Augmented Generation" step) — it will say so honestly if nothing relevant was found, rather than guessing from general knowledge.
This is why the Twin's answers are grounded and traceable back to a real SOP, instead of being generic LLM output. See backend/routers/twin_router.py and backend/services/vector_store.py for the exact implementation.

3. What's Included vs. Stretch Goals
Fully implemented & tested:

JWT auth + 2-role RBAC (admin, employee)
Employee self-service interview: name + department form → adaptive chat (min. 6 questions, LLM-scored) → thank-you close
Speech-to-text in the interview (browser-native Web Speech API — no API key needed, works in Chrome/Edge)
Automatic knowledge extraction + detailed SOP generation the moment an interview finishes
SOP text is embedded into ChromaDB immediately — the Twin can answer from it right away
AI Twin RAG chat, answers grounded only in approved SOPs, with a confidence score
SOP Library page with search + PDF download (generated server-side with fpdf2)
Admin dashboard: KPI cards, animated department knowledge graph (custom canvas force simulation — no external graph library), interviews table with per-person PDF download, employee account management
Multi-provider LLM abstraction (Groq / Hugging Face-Granite / Gemini — one env var swap)
Clean error handling — if your LLM key is missing/invalid, you get an actionable message, not a raw crash
Implemented, optional / gracefully degrades if not configured:

Neo4j (used only for the optional /twin/experts skill-lookup endpoint — the admin dashboard's knowledge graph does not need Neo4j, it's computed directly from SQL data)
Not built (clear extension points):

Full LangGraph state-graph orchestration (current version uses an LLM-scored sequential loop with identical user-facing behavior — swap it into services/interview_agent.py if your report specifically needs the named library)
Password reset flow, email notifications
Drag-to-rearrange on the knowledge graph (currently auto-animates, not user-draggable)
4. Project Structure
orgbrain-ai/
├── backend/
│   ├── main.py                 # FastAPI app + global error handler
│   ├── models.py                # Users, Departments, Interviews, SOPs, KnowledgeSkill...
│   ├── schemas.py
│   ├── auth.py                  # JWT + RBAC (admin / employee)
│   ├── seed.py                  # creates 1 admin + 2 demo employees
│   ├── requirements.txt
│   ├── .env.example
│   ├── routers/
│   │   ├── auth_router.py
│   │   ├── admin_router.py       # interviews list, knowledge-graph, employee mgmt
│   │   ├── interview_router.py   # start/answer/auto-finalize
│   │   ├── twin_router.py        # RAG chat
│   │   └── sop_router.py         # search + PDF download
│   └── services/
│       ├── llm_provider.py       # Groq / HuggingFace-Granite / Gemini abstraction
│       ├── interview_agent.py    # adaptive question logic, min. 6 questions
│       ├── knowledge_extraction.py
│       ├── sop_generator.py
│       ├── vector_store.py       # ChromaDB (RAG)
│       └── graph_store.py        # optional Neo4j (expert lookup only)
├── frontend/
│   ├── app/
│   │   ├── login/
│   │   ├── dashboard/            # role-routed: AdminDashboard.js or EmployeeIntro.js
│   │   ├── interview/            # start form + [id] chat session
│   │   ├── twin-chat/
│   │   └── sop/
│   ├── components/
│   │   ├── Nav.js
│   │   ├── KnowledgeGraph.js     # animated canvas force-directed graph
│   │   └── SpeechTextInput.js    # mic-to-text input
│   └── lib/api.js
├── docker-compose.yml
└── README.md (this file)
5. Get Your Free API Key First
You need at least one LLM provider key.

Provider	Where to get it	Notes
Groq (recommended, default)	https://console.groq.com/keys	No card. Fast, generous free rate limits.
Hugging Face (for IBM Granite)	https://huggingface.co/settings/tokens	Use with model ibm-granite/granite-3.1-8b-instruct (already the default).
Gemini (optional fallback)	https://aistudio.google.com/apikey	No card, but rate-limited more aggressively for some accounts.
You do not need Postgres/Neo4j accounts to run this locally.

6. Run It Locally — Exact Terminal Commands
Backend
cd orgbrain-ai/backend

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Open .env and paste your GROQ_API_KEY (or HF_API_KEY) in.
# Confirm LLM_PROVIDER=groq (or huggingface) matches the key you added.

python3 seed.py

uvicorn main:app --reload --port 8000
Backend: http://localhost:8000 · Swagger docs: http://localhost:8000/docs

Frontend (new terminal)
cd orgbrain-ai/frontend

npm install

echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

npm run dev
Frontend: http://localhost:3000

Demo Accounts (from seed.py)
Role	Email	Password
Admin	admin@orgbrain.ai	Admin@123
Employee	arun@orgbrain.ai	Arun@123
Employee	priya@orgbrain.ai	Priya@123
Change these before deploying anywhere public.

Try the Full Flow
1. Log in as arun@orgbrain.ai (employee)
2. Click "Interview Agent" → confirm your name, pick "Software Development" → Begin
3. Answer the questions - type, or tap the 🎤 mic icon to speak (Chrome/Edge only)
   You'll get at least 6 questions, then a thank-you message and an auto-generated SOP
4. Click "SOP" in the top nav → find your new SOP → try "Download PDF"
5. Click "AI Twin" → select "Software Development" → ask a question related to what
   you just discussed → you'll get an answer grounded in your own SOP, with a confidence score
6. Log out, log in as admin@orgbrain.ai → see the dashboard: stats, the animated
   knowledge graph, and your interview in the table with a PDF download link
7. Docker (Optional)
cd orgbrain-ai
# Make sure backend/.env exists with your API key first
docker compose up --build
8. Deploying for Free (Live, Shareable Link)
Push to GitHub
cd orgbrain-ai
git init
git add .
git commit -m "OrgBrain AI"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/orgbrain-ai.git
git push -u origin main
Backend on Render (free)
https://render.com → New → Web Service → connect your repo, root dir backend
Build: pip install -r requirements.txt
Start: uvicorn main:app --host 0.0.0.0 --port $PORT
Env vars: JWT_SECRET, LLM_PROVIDER, GROQ_API_KEY (or HF_API_KEY), DATABASE_URL (from Neon, https://neon.tech - free permanent Postgres), FRONTEND_ORIGIN (fill in after step below)
Once live, open the Shell tab and run python3 seed.py once
Frontend on Vercel (free)
https://vercel.com → New Project → same repo, root dir frontend
Env var: NEXT_PUBLIC_API_URL = your Render backend URL
Deploy, then go back to Render and set FRONTEND_ORIGIN to your Vercel URL, redeploy
Note: Render's free tier sleeps after 15 min idle — open the link a minute before a demo.

9. Common Issues & Fixes
Problem	Fix
Answer submission returns a 502 with a message about your API key	This is the intended behavior — it means GROQ_API_KEY (or HF_API_KEY) in .env is still a placeholder or invalid. Paste a real key and restart the backend.
Mic button doesn't appear or doesn't work	Web Speech API only works in Chromium browsers (Chrome, Edge) — Firefox/Safari will just show the text input without the mic, which is expected.
Twin Chat says "I don't have any approved knowledge yet"	Expected until at least one interview has been completed for that department — SOPs publish to the Twin automatically the moment an interview finishes.
bcrypt error on seed.py	Already pinned to bcrypt==4.0.1 in requirements.txt.
CORS errors when deployed	Confirm FRONTEND_ORIGIN on Render exactly matches your Vercel URL, including https://.
10. Where to Go Next
Turn on Neo4j (fill in NEO4J_URI/NEO4J_USER/NEO4J_PASSWORD) to activate the optional /twin/experts?skill=X endpoint for "who knows X" lookups — build a small frontend page for it.
Swap the sequential interview loop in services/interview_agent.py for a literal LangGraph StateGraph if your report specifically requires showing that library.
Add drag-to-rearrange on the KnowledgeGraph.js canvas nodes for more interactivity.
