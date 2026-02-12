# 📚 Study Buddy AI

An interactive **quiz generation** app powered by **LLMs** (Groq or Ollama) with a Streamlit UI.
You choose a topic + difficulty + question type, attempt the quiz, then view results and download them as CSV.

## 🌟 Features

- **Two quiz types**: Multiple Choice Questions (MCQ) + Fill-in-the-Blank
- **Provider toggle**: Groq (cloud) **or** Ollama (local)
- **Streamlit UI** with stable session-state flow (Generate → Attempt → Submit → Results)
- **Export results** as CSV (download in-memory; optional server-side save)
- **Docker + Kubernetes ready** (Streamlit on port **8501**)

## 🛠️ Tech Stack

- **Language**: Python **3.12+**
- **UI**: Streamlit
- **LLM orchestration**: LangChain
- **Providers**: Groq (`langchain-groq`) / Ollama (`langchain-ollama`)
- **Data**: pandas (results)
- **Packaging**: `setup.py` + `pyproject.toml`

## 📁 Project Structure

```
Study Buddy AI/
├── application.py              # Streamlit app entry point
├── src/
│   ├── generator/
│   │   └── question_generator.py  # LLM calls + parsing
│   ├── prompts/
│   │   └── templates.py           # Prompt templates
│   ├── models/
│   │   └── question_schemas.py    # Pydantic schemas for parsing
│   ├── llm/                       # Groq/Ollama client factory
│   ├── config/
│   │   └── settings.py            # Environment-based config
│   └── utils/
│       └── helpers.py             # QuizManager (UI helpers, results)
├── manifests/
│   ├── deployment.yaml         # Kubernetes Deployment (Streamlit 8501)
│   └── service.yaml            # Kubernetes Service (NodePort -> 8501)
├── requirements.in             # Top-level deps (edit this)
├── requirements.txt            # Compiled/pinned deps (used for Docker)
├── Dockerfile
└── README.md
```

## 🔧 Configuration

The app reads settings from environment variables (optionally from a local `.env`).

### Provider toggle

- **Groq mode (cloud)**:
  - `USE_OLLAMA=false`
  - `GROQ_API_KEY=...` (**required**)

- **Ollama mode (local)**:
  - `USE_OLLAMA=true`
  - `OLLAMA_BASE_URL=http://localhost:11434` (default; must be reachable)

### Common environment variables

- `USE_OLLAMA`: `"true"` or `"false"`
- `GROQ_API_KEY`: required when `USE_OLLAMA=false`
- `OLLAMA_BASE_URL`: default `"http://localhost:11434"`

## 🚀 Getting Started (Local Dev)

### Prerequisites

- Python **3.12+**
- `uv` installed

### Install (dev)

Create and activate a virtual environment:

```powershell
uv venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies + editable install:

```powershell
uv pip sync requirements.txt
uv pip install -e .
```

### Run (Streamlit)

```powershell
streamlit run application.py
```

Open `http://localhost:8501`.

### Smoke test (keep existing command)

```powershell
python -c "import study_buddy_ai; print(study_buddy_ai.__version__)"
```

## 🐳 Docker

### Build

```bash
docker build -t study-buddy-ai:latest .
```

### Run (Groq mode)

```bash
docker run --rm -p 8501:8501 \
  -e USE_OLLAMA=false \
  -e GROQ_API_KEY=YOUR_GROQ_API_KEY \
  study-buddy-ai:latest
```

### Run (Ollama mode)

If your Ollama server is running on your machine, the container must be able to reach it.
On Windows/Mac, you typically set `OLLAMA_BASE_URL` to the host address reachable from Docker.

```bash
docker run --rm -p 8501:8501 \
  -e USE_OLLAMA=true \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  study-buddy-ai:latest
```

## ☸️ Kubernetes (manifests/)

Your manifests expose Streamlit on **8501** and use:
- Deployment name: `llmops-app`
- Service name: `llmops-service`
- Secret name: `groq-api-secret` (key: `GROQ_API_KEY`)

### 1) Create secret (Groq)

```bash
kubectl create secret generic groq-api-secret --from-literal=GROQ_API_KEY=YOUR_GROQ_API_KEY
```

### 2) Update the image

Edit `manifests/deployment.yaml` and set:

```yaml
image: <your-registry>/study-buddy-ai:<tag>
```

### 3) Apply

```bash
kubectl apply -f manifests/deployment.yaml
kubectl apply -f manifests/service.yaml
```

### 4) Access (NodePort)

```bash
kubectl get svc llmops-service
```

Then open `http://<NODE_IP>:<NODE_PORT>`.

## 🔄 CI/CD (Jenkins + Argo CD)

This repo includes a `Jenkinsfile` that implements a simple GitOps-style flow:

- **Jenkins**:
  - checks out `main`
  - builds + pushes a Docker image to Docker Hub (`dataguru97/studybuddy:v<BUILD_NUMBER>`)
  - updates `manifests/deployment.yaml` with the new image tag
  - commits + pushes the manifest change back to `main`
  - logs into **Argo CD** and triggers `argocd app sync`

- **Argo CD**:
  - watches the repo/manifests and applies the updated image tag to the cluster

### Jenkins credentials required

Create these credentials in Jenkins (IDs must match):

- `github-token` (**Username with password**)
  - username: your GitHub username
  - password: a GitHub **PAT** with repo write permission
- `dockerhub-token` (Docker Hub credentials/token)
- `kubeconfig` (Kubeconfig credential for your cluster)

### Jenkinsfile environment values to verify

At the top of `Jenkinsfile`, confirm these match your environment:

- `GIT_REPO_URL` (this repo)
- `GIT_BRANCH` (usually `main`)
- `KUBE_SERVER_URL` (Kubernetes API server URL)
- `ARGOCD_SERVER` (Argo CD server address)
- `ARGOCD_APP_NAME` (your Argo CD application name; currently `study`)

## 🔁 Dependency Management (important)

- **Edit**: `requirements.in` (top-level deps)
- **Compile**: `requirements.txt` (pinned, reproducible; used in Docker builds)

Update dependencies:

```powershell
uv pip compile requirements.in -o requirements.txt
uv pip sync requirements.txt
```

## 🧯 Troubleshooting

- **Missing `GROQ_API_KEY` error**:
  - Set `USE_OLLAMA=false` and provide `GROQ_API_KEY`, or set `USE_OLLAMA=true` for Ollama.
- **Ollama connection issues in Docker**:
  - Use `OLLAMA_BASE_URL=http://host.docker.internal:11434` (common on Windows/Mac).
- **Don’t commit secrets**:
  - `.env` is ignored by git; keep keys out of the repo.
