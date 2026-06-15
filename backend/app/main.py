from fastapi import FastAPI
from app.database import create_db
from app.routers import users, pins
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Pinterest Clone API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(users.router)

app.include_router(pins.router)

@app.on_event("startup")
def on_startup():
    create_db()


@app.get("/")
def root():
    return {
        "message": "Pinterest Clone API funcionando"
    }
