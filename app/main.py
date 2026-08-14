from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.documents import router as documents_router
from app.api.questions import router as questions_router
from app.db import initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="RAG Document Service", lifespan=lifespan)
app.include_router(documents_router)
app.include_router(questions_router)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
