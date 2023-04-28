"""APIRouter 설정.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com.
"""

from api.api_v1.endpoints import dashboard, detail, fdc, setting_client, test, trend
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(
    setting_client.router,
    prefix="/setting-client",
    tags=["setting_client"],
)
api_router.include_router(
    fdc.router,
    prefix="/fdc",
    tags=["fdc"],
)


api_router.include_router(detail.router, prefix="/data/detail", tags=["front-end"])
api_router.include_router(trend.router, prefix="/data/trend", tags=["front-end"])
api_router.include_router(
    dashboard.router,
    prefix="/data/dashboard",
    tags=["front-end"],
)
api_router.include_router(test.router, prefix="/test", tags=["test"])
