from fastapi import FastAPI,HTTPException, Depends
from pydantic import BaseModel
from typing import List,Annotated
from sqlalchemy import text
from app.db.database import Base, engine
from app.routes import userRoutes
from app.routes import oauthRoutes
from app.models import userModel
from app.models import oauthAccountModel

app = FastAPI()

@app.on_event("startup")
def _startup() -> None:
    Base.metadata.create_all(bind=engine)

app.include_router(userRoutes.router)
app.include_router(oauthRoutes.router)