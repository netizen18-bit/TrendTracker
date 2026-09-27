from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from app.analyzers.website_analyzer import WebsiteAnalyzer

router = APIRouter(prefix="/analysis", tags=["Website Analyzer"])

class InspectRequest(BaseModel):
    url: str

@router.post("/inspect")
async def inspect_website(payload: InspectRequest):
    """
    Autonomous investigation of a website URL.
    Probes RSS, Sitemaps, robots.txt, Blog sections, and article structure,
    returning a detailed capabilities matrix and recommended monitoring strategy.
    """
    if not payload.url or len(payload.url.strip()) < 3:
        raise HTTPException(status_code=400, detail="Invalid target URL")

    result = await WebsiteAnalyzer.analyze(payload.url.strip())
    return result
