from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.cases import router as cases_router
from app.api.modules import router as modules_router
from app.database import create_db

create_db()

app = FastAPI(
    title="Nexus OSINT",
    description="Community OSINT investigation platform for small businesses.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cases_router, prefix="/api")
app.include_router(modules_router, prefix="/api")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": "0.1.0"}
