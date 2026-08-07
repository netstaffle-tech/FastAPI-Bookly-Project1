from importlib.metadata import version
from fastapi import FastAPI
from src.books.routes import book_router
from src.auth.routers import auth_router
from contextlib import asynccontextmanager
from src.db.main import init_db

@asynccontextmanager
async def lifespan(app:FastAPI):
    print(f"Server is starting...")
    await init_db()
    yield
    print(f"Server is shutting down...")

version = "v1"

#app = FastAPI(title="Bookly",description="A REST API for Book review web service.",version=version,lifespan=lifespan)

app = FastAPI(title="Bookly",description="A REST API for Book review web service.",version=version)

app.include_router(book_router,prefix=f"/api/{version}/books",tags=["Books"])

app.include_router(auth_router,prefix=f"/api/{version}/auth",tags=["Users"])