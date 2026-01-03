from fastapi import FastAPI,HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List,Annotated
from sqlalchemy import text
from app.db.database import Base, engine
from app.routes import userRoutes
from app.routes import oauthRoutes
from app.models import userModel
from app.models import oauthAccountModel
from app.core.config import settings  

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://localhost:19006",
        "http://127.0.0.1:19006",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def _startup() -> None:
    Base.metadata.create_all(bind=engine)

app.include_router(userRoutes.router)
app.include_router(oauthRoutes.router)

@app.get("/debug-env")
def debug_env():
    return {"GITHUB_REDIRECT_URI": settings.GITHUB_REDIRECT_URI}