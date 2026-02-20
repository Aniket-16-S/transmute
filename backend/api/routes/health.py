from fastapi import APIRouter, HTTPException
from core import get_settings
import sqlite3
import os

router = APIRouter(prefix="/health", tags=["health"])

settings = get_settings()
DB_PATH = settings.db_path
UPLOAD_DIR = settings.upload_dir


@router.get(
        "/info", 
        summary="Get application metadata", 
        responses={
            200: {
                "description": "Application metadata",
                "content": {
                    "application/json": {
                        "example": {
                            "name": "Transmute",
                            "version": "v1.0.0"
                        }
                    }
                }
            }
        }
)
def app_info():
    """Return application metadata"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
    }


@router.get(
        "/live", 
        summary="Liveness check", 
        responses={
            200: {
                "description": "Liveness status",
                "content": {
                    "application/json": {
                        "example": {
                            "status": "alive"
                        }
                    }
                }
            }
        }
)
def liveness():
    """Simple liveness check to confirm the server is running"""
    return {"status": "alive"}


@router.get(
        "/ready", 
        summary="Readiness check", 
        responses={
            200: {
                "description": "Readiness status",
                "content": {
                    "application/json": {
                        "example": {
                            "status": "ready",
                            "checks": {
                                "database": "ok",
                                "storage": "ok"
                            }
                        }
                    }
                }
            },
            503: {
                "description": "Not ready with details on failed checks",
                "content": {
                    "application/json": {
                        "example": {
                            "status": "not_ready",
                            "checks": {
                                "database": "error: unable to connect",
                                "storage": "ok"
                            }
                        }
                    }
                }
            }
        }
)
def readiness():
    """Readiness check to confirm the server is ready to handle requests"""
    checks = {}
    # SQLite check
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        conn.close()
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"

    # Filesystem check
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        test_path = os.path.join(UPLOAD_DIR, ".healthcheck")
        with open(test_path, "w") as f:
            f.write("ok")
        os.remove(test_path)
        checks["storage"] = "ok"
    except Exception as e:
        checks["storage"] = f"error: {e}"

    # Determine overall status
    if all(v == "ok" for v in checks.values()):
        return {"status": "ready", "checks": checks}

    raise HTTPException(status_code=503, detail={"status": "not_ready", "checks": checks})