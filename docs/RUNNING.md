# Running Mail Risk Intelligence

## Choose an inference path

| Path | Install Ollama? | API key? | Where email content is processed |
| --- | --- | --- | --- |
| Default: Ollama / qwen3.5:4b | Yes; download the model | No | Your local Ollama server |
| Optional: Groq / openai/gpt-oss-120b | No | Yes, a Groq key | Groq's hosted API |

Both paths run the same backend and frontend. Groq is the evaluated supervised-demo recommendation; local Qwen supports no-key/offline inference after the initial downloads. No paid key is required. This integration is **Groq**, not xAI Grok. The frontend never receives a provider key. See [evaluation results](../evaluations/EXPANDED_COMPARISON_2026-10-06.md) for quality and quota limitations.

## 1. Install prerequisites and obtain the project

Install Python 3.11+, [uv](https://docs.astral.sh/uv/getting-started/installation/), and [Node.js](https://nodejs.org/en/download) 22.12+ with npm. Use the supplied local checkout or extract the submission ZIP; no remote repository URL is required. Open a terminal in the directory containing README.md, backend/ and frontend/. Confirm tools:

```sh
python3 --version
uv --version
node --version
npm --version
```

Commands below use a macOS/Linux shell. On Windows, use equivalent directory/copy commands in your terminal; the Python/npm commands are the same. Dependency installation and model download require internet access. Local inference does not require internet after setup. Hardware, free memory and disk capacity affect Ollama performance; the repository does not bundle model weights.

## 2A. Prepare Ollama for the default local path

Download the installer for your OS from [Ollama downloads](https://ollama.com/download) and follow the [official local setup](https://docs.ollama.com/quickstart). Open the installed Ollama app. If its service is not already running, keep this command running in a separate terminal:

```sh
ollama serve
```

Do not launch a second server if the desktop app already owns port 11434. From another terminal, download and verify the selected model:

```sh
ollama pull qwen3.5:4b
ollama list
curl http://127.0.0.1:11434/api/tags
```

The list should contain qwen3.5:4b. Optional direct inference smoke check:

```sh
ollama run qwen3.5:4b "Reply with the word ready."
```

The first inference may include model loading. Successful smoke output establishes connectivity, not email-analysis accuracy. Local Ollama requires **no Ollama or Groq API key**; Ollama cloud is not the selected integration. Skip section 2B if using this path.

## 2B. Prepare Groq instead of Ollama

Create/sign in to an account at the [Groq console](https://console.groq.com/) and create a key in [API Keys](https://console.groq.com/keys), following the [official quickstart](https://console.groq.com/docs/quickstart). Check model access and eligible free-tier limits in your account. Hosted access is not guaranteed for every key; do not enable a paid-only dependency to run this submission.

If a reviewer needs a temporary demo key, **the project author can provide their Groq API key on request, with a 30-day expiration as stated by the author**. Confirm the actual expiry when it is issued/shared. This describes the author's offer, not a guarantee that all Groq keys expire in 30 days. Reviewers can use their own key or the no-key Ollama path instead. Request/share credentials privately; do not put them in Git, screenshots, evaluation reports or frontend variables.

Ollama installation and model download can be skipped for Groq. Email and attachment text will be sent to Groq. Network access and quotas remain required at inference time.

## 3. Install and configure the backend

From the repository root:

```sh
cd backend
uv sync --locked
test -f .env || cp .env.example .env
```

On PowerShell, the non-overwriting copy equivalent is:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Edit backend/.env. For local inference, confirm:

```dotenv
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:4b
OLLAMA_NUM_CTX=8192
OLLAMA_THINK=false
LLM_TIMEOUT_SECONDS=180
LLM_MAX_RETRIES=1
GROQ_API_KEY=
```

For Groq, use:

```dotenv
LLM_PROVIDER=groq
GROQ_MODEL=openai/gpt-oss-120b
GROQ_API_KEY=replace-with-your-private-key
LLM_TIMEOUT_SECONDS=180
LLM_MAX_RETRIES=1
```

Retain all other copied variables, including prompt paths, risk catalog path, database path and CORS origins. Never commit .env; .env.example intentionally contains no key. Existing shell environment variables override .env, and existing .env overrides Settings defaults. Copying the example only when absent will not change an older private provider/model selection. Keep exactly one active assignment for each variable. No frontend .env is needed for the development proxy.

## 4. Start backend — terminal A

From backend/:

```sh
uv run uvicorn mailrisk.api:app --host 127.0.0.1 --port 8000
```

Keep this terminal open. Run one backend process and no extra Uvicorn workers. Optional development hot reload adds --reload; model/provider changes require a restart. SQLite is created under backend/data/; a new database imports and queues ten seed emails. Existing messages/results are retained and failures are not automatically rerun on startup.

From another terminal:

```sh
curl http://127.0.0.1:8000/health
```

Expect status ok with your selected provider/model. Health checks configuration/process availability, not provider readiness; a real analysis is the end-to-end check. API docs: http://127.0.0.1:8000/docs.

## 5. Start frontend — terminal B

From the repository root in a new terminal:

```sh
cd frontend
npm ci
npm run dev -- --port 5173 --strictPort
```

Open http://127.0.0.1:5173. The development server proxies /api to the backend on port 8000. Port 5173 matches configured CORS origins. If the port is occupied, stop the conflicting development instance or deliberately change the port and CORS_ORIGINS; do not silently use a second UI/server pair. Changing backend port also requires changing frontend/vite.config.ts proxy target.

npm run build verifies TypeScript and produces a frontend build. npm run preview alone does not provide the configured development API proxy; use npm run dev for the documented complete local application. Production serving/proxy configuration is outside this take-home setup.

## 6. Verify the complete flow

1. Check that the inbox contains the seed emails and shows processing states, then results or visible errors. With an existing evaluation database, additional synthetic emails may also appear.
2. Open a completed message: inspect original text, extracted facts, risk rationale, entities and relationships with source evidence.
3. Add a pasted email or supported TXT/PDF/EML file. PDFs require readable text layers. It follows the same two-stage analysis pipeline.
4. Open Knowledge graph: pan/zoom, select a node, inspect connections and navigate to its source email. Only selected successful analyses contribute.
5. For a failed analysis, check the displayed error and retained extraction; fix provider configuration and retry. Failures do not mean risk none. A failed reanalysis preserves previous successful results.

Local analysis can take minutes. A run can spend up to four 180-second calls plus backoff, excluding queue wait. Groq can return rate-limit errors even when a model is accessible. The latest evaluation used external pacing that the running application does not implement. Do not interpret valid JSON or an accepted risk badge as independently verified truth.

## 7. Troubleshooting, stopping and restarting

| Symptom | Action |
| --- | --- |
| Ollama unreachable | Open its app/start its server; check /api/tags and OLLAMA_BASE_URL. |
| Model not found | Download the exact OLLAMA_MODEL tag or verify GROQ_MODEL access. |
| Groq key missing/authentication failure | Set private GROQ_API_KEY, check expiry/access and restart backend. |
| Groq rate limit | Wait for quota recovery; retry explicitly. Do not repeatedly submit duplicate work. |
| Invalid model output | Inspect safe error and bounded repair history; retry or explicitly change model. Longer timeouts do not fix semantic errors. |
| UI cannot reach API | Check backend port, Vite proxy and startup terminal; frontend must run through Vite. |
| Old provider/model remains selected | Check existing .env and shell overrides; restart backend. |
| Uploaded PDF rejected | Use an unencrypted PDF with readable text; OCR is not implemented. |

Press Ctrl+C in the frontend and backend terminals to stop those processes. Stop a manually started ollama serve with Ctrl+C, or quit its desktop app when no longer needed. SQLite persists; restarting backend marks unfinished analyses interrupted, then allows manual retry. No database deletion is necessary to restart or switch provider.

For tests, commands, coverage and tracked reports, see [Testing](TESTING.md).
