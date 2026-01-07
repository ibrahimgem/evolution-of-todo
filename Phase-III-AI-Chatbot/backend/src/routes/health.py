"""
Backend health check router for Kubernetes liveness/readiness probes
[Task]: T020
[From]: specs/004-local-k8s-deployment/spec.md §US1, plan.md §DD-006
"""

from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes probes.
    Returns 200 OK if the service is healthy.
    Does not depend on database connectivity for basic liveness.
    """
    return {
        "status": "healthy",
        "service": "todo-chatbot-backend",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
