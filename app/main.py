"""FastAPI app 실행파일.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
import os
import sys

from api.api_v1.api import api_router
from core.logger import make_logger
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

logger = make_logger(__name__)

sys.path.append(
    os.path.join(os.path.dirname(os.getcwd()), "app"),  # noqa: PTH118, PTH120, PTH109
)


app = FastAPI(docs_url=None, redoc_url=None)
origins = ["*"]

app.include_router(api_router, prefix="/api/v1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> HTMLResponse:
    """Offline swagger가 될 수 있도록 하는 함수."""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,  # type: ignore[arg-type]
        title=app.title + " - Swagger UI",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )
