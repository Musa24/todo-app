from fastapi import FastAPI

from app import models  # noqa: F401
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
