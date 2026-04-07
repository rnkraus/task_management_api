from fastapi import FastAPI
from app.api.tasks import router as task_router
from app.api.users import router as user_router
from app.core.db import Base, engine
from app.api.auth import router as auth_router


app = FastAPI()

#Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "API läuft"}

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(task_router)