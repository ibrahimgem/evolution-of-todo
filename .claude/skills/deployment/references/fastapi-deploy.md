# FastAPI Backend Deployment

## Docker Production Setup

Create a `Dockerfile` in your backend directory:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Environment Variables

Ensure these are set in your deployment platform:

- `DATABASE_URL`: Neon PostgreSQL connection string
- `SECRET_KEY`: JWT signing key (use a strong random value)
- `ALGORITHM`: JWT algorithm (default: `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

## Production Considerations

1. **Disable Debug Mode**: Ensure `reload=False` in production.
2. **CORS Configuration**: Whitelist only your frontend domain.
3. **Rate Limiting**: Consider adding middleware for API rate limits.
4. **Health Checks**: Add a `/health` endpoint for load balancer checks.

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```
