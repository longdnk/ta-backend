## FastAPI User Authentication and Management
This FastAPI project focuses on creating a robust user authentication and management system. The core features include user registration, login, and token management. The application leverages JWT for secure user authentication and encryption for password handling, developed with Python 3.11.

## Available features
- [x] Login with user_name/email.
- [x] JWT auth.
- [x] Run with Docker.
- [x] Combine with proxy (Nginx).
- [x] MySQL DB connect.
- [x] Run with custom params meter parser.
- [x] Multi channel run.
- [ ] Validation by user token.
- [ ] Validate router.
- [ ] Run with SSL cert.

## Installation
**With Conda:**
```bash
conda create --name ta-backend python=3.11
```

**Install:**
```bash
pip install -r requirements.txt
```

## Run
**Local with single channel:**
```bash
python main.py --host=127.0.0.1 --port=9999 --reload=1 --workers=1 --backlog=5000 --log_level=info --use_colors=1 --limit_concurrency=10000 --limit_max_requests=1000
```

**Local with multi channel:**
```bash
python main.py --host=0.0.0.0 --port=5555 --reload=0 --workers=4 --backlog=5000 --log_level=info --use_colors=1 --limit_concurrency=10000 --limit_max_requests=1000
```

## Run with docker
**Docker:**
```bash 
docker build -t backend .
```
```bash 
docker run -d --name backend -p 5555:5555 my-backend
```

**Docker compose:**
```bash 
docker-compose up -d --build
```