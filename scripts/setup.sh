#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=== AI-TAURON Setup ==="

# 1. Create .env if missing
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ">> Edit .env with your settings before running docker compose"
fi

# 2. Start infrastructure
echo "Starting Docker Compose services..."
docker compose up -d qdrant postgres mlflow ollama

# 3. Wait for services
echo "Waiting for services to be healthy..."
echo -n "  Qdrant: "
until curl -sf http://localhost:6333/healthz > /dev/null 2>&1; do sleep 2; echo -n "."; done
echo " OK"

echo -n "  PostgreSQL: "
until docker compose exec -T postgres pg_isready -U ai_tauron > /dev/null 2>&1; do sleep 2; echo -n "."; done
echo " OK"

echo -n "  Ollama: "
until curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; do sleep 2; echo -n "."; done
echo " OK"

# 4. Pull LLM model
echo "Pulling Mistral model in Ollama..."
docker compose exec ollama ollama pull mistral

# 5. Install Python deps
echo "Installing Python dependencies..."
pip install -e ".[dev,ui]"

echo ""
echo "=== Setup complete ==="
echo "Services:"
echo "  Qdrant:    http://localhost:6333"
echo "  PostgreSQL: localhost:5432"
echo "  MLflow:    http://localhost:5000"
echo "  Ollama:    http://localhost:11434"
echo ""
echo "Next steps:"
echo "  uvicorn src.main:app --host 0.0.0.0 --port 8000"
echo "  streamlit run src/python/dashboard.py"
