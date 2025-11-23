

import uvicorn
from fastapi import FastAPI

from .config import settings
from .database import Base, engine
from .routers import batches
from .routers import llm_test  # import your LLM test router
from dotenv import load_dotenv

load_dotenv()


app = FastAPI(title=settings.PROJECT_NAME)


# include routers
app.include_router(
    batches.router,
    prefix=settings.API_V1_PREFIX,
)

# LLM test endpoint
app.include_router(
    llm_test.router,          # uses prefix from llm_test.py ("/api/v1/llm")
)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
    }


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def on_startup():
    await init_db()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
