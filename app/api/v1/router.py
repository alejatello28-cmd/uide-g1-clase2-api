from fastapi import APIRouter
from app.api.v1.endpoints import crypto

api_router = APIRouter()
api_router.include_router(crypto.router, prefix="")
