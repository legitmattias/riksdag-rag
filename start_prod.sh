#!/bin/bash

# start_prod.sh — WT2 Project production start script

# 1. Activate Python venv
source .venv/bin/activate

# 2. Start MongoDB if not already running
docker compose up -d

# 3. Start FastAPI backend without reload
cd backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# 4. Start built frontend
cd frontend
nohup node build > frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "Production servers started."
echo "Backend (FastAPI) on port 8000 (PID $BACKEND_PID)"
echo "Frontend (SvelteKit) on port 3000 (PID $FRONTEND_PID)"
