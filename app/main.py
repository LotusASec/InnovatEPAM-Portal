from fastapi import FastAPI

from app.core.database import engine
from app.core.errors import APIError, api_error_handler
from app.api.routes import auth, ideas, theme
from app.models.base import Base
import app.models  # noqa: F401

app = FastAPI(title="InnovatEPAM Portal MVP")
app.add_exception_handler(APIError, api_error_handler)
app.include_router(auth.router, prefix="/api")
app.include_router(ideas.router, prefix="/api")
app.include_router(theme.router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}
