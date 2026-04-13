from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.tasks import router as task_router
from app.api.users import router as user_router
from app.api.auth import router as auth_router
from app.core.db import get_db


app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is up"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database not available")


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(task_router)