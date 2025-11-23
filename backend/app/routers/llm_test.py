from fastapi import APIRouter
from app.llm_client import LLMClient

router = APIRouter(prefix="/api/v1/llm", tags=["llm"])

@router.get("/test")
async def test_llm():
    client = LLMClient()
    result = await client.ask("Say hello in one sentence.")
    return {"reply": result}
