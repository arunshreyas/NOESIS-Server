from fastapi import FastAPI,HTTPException, Depends
from pydantic import BaseModel
from typing import List,Annotated
from sqlalchemy import text
from app.db.database import engine

app = FastAPI()

