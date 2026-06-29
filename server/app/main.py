# --------------------------------------------------------
# File: server/app/main.py
# Purpose: FastAPI Main Entry Point & Configuration
# Responsibilities: Initializes the FastAPI application, sets up middleware
#                   (CORS), handles the database lifespan, and registers API routers.
# Author: Srihan Raj Guduru
# --------------------------------------------------------

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.debt import router as debt_router
from app.api.expense import router as expense_router
from app.api.goal import router as goal_router
from app.api.notification import chat_router
from app.api.notification import router as notification_router
from app.api.prediction import router as prediction_router
from app.api.reward import router as reward_router
from app.api.transaction import router as transaction_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifespan events of the FastAPI application.
    Useful for initializing and shutting down connections.
    """
    yield


app = FastAPI(title="FinBro API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(transaction_router)
app.include_router(goal_router)
app.include_router(debt_router)
app.include_router(expense_router)
app.include_router(prediction_router)
app.include_router(reward_router)
app.include_router(notification_router)
app.include_router(chat_router)


@app.get("/health")
async def health():
    """
    Liveness and readiness check endpoint.
    """
    return {"status": "ok"}
