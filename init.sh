#!/bin/bash

# init.sh — WT2 Project setup script

echo "🔵 Setting up Python environment..."

# 1. Create venv in project root if not exists
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# 2. Activate venv
source .venv/bin/activate

# 3. Install backend/pipeline requirements
echo "🔵 Installing Python requirements..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# 4. Check MongoDB via Docker
echo "🔵 Starting MongoDB container via docker-compose..."
docker compose up -d

# 5. Check if MongoDB is running
sleep 5
if ! docker ps | grep -q "wt2-mongo"; then
  echo "❌ MongoDB did not start correctly. Please check Docker."
  exit 1
fi

# 6. Info about seeding (only manual if needed)
echo "✅ MongoDB is up. If the database is empty, run:"
echo "   source .venv/bin/activate && python3 pipeline/seed_mongodb.py"

# 7. Reminder about env file
if [ ! -f backend/.env ]; then
  echo "❗ No .env file detected in backend/. Please create one based on .env.example!"
fi

# 8. Start backend in development mode
echo "🔵 Starting FastAPI backend (dev mode)..."
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# 9. Start frontend in development mode
echo "🔵 Installing frontend dependencies and starting Vite dev server..."
cd frontend
npm install --legacy-peer-deps
npm run dev -- --host 0.0.0.0 --port 3000 &
FRONTEND_PID=$!
cd ..

# 10. Final info
echo "✅ Project initialized."
echo "🔵 Backend running on http://localhost:8000"
echo "🔵 Frontend running on http://localhost:3000"
echo "ℹ️ Press Ctrl+C to stop manually. (PIDs: Backend $BACKEND_PID, Frontend $FRONTEND_PID)"
