from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.core.init_db import create_db_and_tables
from modules.hero.api import router as hero_router

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(hero_router)

@app.get("/")
async def root():
    return {"message": "Hero API is up and running!"}
