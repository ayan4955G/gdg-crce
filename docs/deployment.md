# Re:Learn — Deployment Guide

## Local Development

### Backend
```bash
pip install -r requirements.txt
python ml/scripts/generate_dataset.py
python ml/scripts/split_dataset.py
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev    # Vite dev server on http://localhost:5173
```

The Vite dev server proxies `/api` requests to `http://127.0.0.1:8000`.

## Docker Deployment

### Build & Run
```bash
docker-compose up --build
```

### Services
| Service | Port | Description |
|---|---|---|
| `backend` | 8000 | FastAPI + ML inference |
| `frontend` | 3000 | Nginx serving React build |

### Volumes
- `ml/data/` — Dataset files
- `ml/saved_models/` — Trained model artifacts

## Production Considerations
- Replace in-memory learner profiles with PostgreSQL persistence
- Add Redis for session caching and rate limiting
- Deploy code sandbox as isolated container with `--network=none`
- Set `PYTHONUNBUFFERED=1` for proper log streaming
- Add health check endpoints (`/health`, `/ready`)
- Configure CORS origins to specific frontend domain
