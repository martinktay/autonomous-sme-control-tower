# Infrastructure Configuration

## Docker Compose Setup

This directory contains the Docker Compose configuration for local development.

## Quick Start

```bash
# From the infra directory
docker-compose up --build

# Or from the project root
docker-compose -f infra/docker-compose.yml up --build
```

## Services

### Backend (FastAPI)
- **Port**: 8000
- **Context**: `../backend`
- **Hot Reload**: Enabled via volume mount
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

### Frontend (Next.js)
- **Port**: 3000
- **Context**: `../frontend`
- **Hot Reload**: Enabled via volume mount
- **Access**: http://localhost:3000
- **Depends On**: Backend service

## Network

Services communicate via the `autonomous-sme` bridge network:
- Frontend can reach backend at `http://backend:8000`
- External access via localhost ports

## Environment Variables

Required environment variables are loaded from `../.env` file:

```bash
# Create from example
cp ../.env.example ../.env

# Edit with your AWS credentials
nano ../.env
```

## Common Commands

```bash
# Start services
docker-compose up

# Start in detached mode
docker-compose up -d

# Rebuild and start
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart a service
docker-compose restart backend

# Execute command in running container
docker-compose exec backend python -m pytest
docker-compose exec frontend npm run lint
```

## Troubleshooting

### Port Already in Use

If ports 8000 or 3000 are already in use:

```bash
# Find process using port
lsof -i :8000
lsof -i :3000

# Kill the process or change ports in docker-compose.yml
```

### Environment Variables Not Loading

Ensure `.env` file exists in project root:

```bash
ls -la ../.env
```

### Volume Mount Issues

If code changes aren't reflected:

```bash
# Rebuild containers
docker-compose up --build

# Or remove volumes and rebuild
docker-compose down -v
docker-compose up --build
```

### AWS Credentials

Verify AWS credentials are set correctly:

```bash
# Check .env file
cat ../.env | grep AWS

# Test from within container
docker-compose exec backend python -c "from app.config import get_settings; print(get_settings().aws_region)"
```

## Development Workflow

1. **Start services**: `docker-compose up`
2. **Make code changes**: Edit files in `backend/` or `frontend/`
3. **Changes auto-reload**: Both services watch for file changes
4. **View logs**: Check terminal for errors
5. **Stop services**: `Ctrl+C` or `docker-compose down`

## Production Considerations

This configuration is for **development only**. For production:

- Remove volume mounts
- Use production-grade WSGI server (gunicorn)
- Use `npm run build` and `npm start` for Next.js
- Restrict CORS origins
- Use secrets management for credentials
- Add health checks and restart policies
- Use reverse proxy (nginx)
- Enable HTTPS
