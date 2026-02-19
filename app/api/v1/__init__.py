from fastapi import APIRouter
from app.api.v1 import auth, sars, users, analytics, alerts

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(sars.router, prefix="/sars", tags=["SARs"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
