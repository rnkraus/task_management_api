from fastapi import FastAPI
from app.api.tasks import router as task_router
from app.core.db import Base, engine

app = FastAPI()

#Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "API läuft"}

app.include_router(task_router)