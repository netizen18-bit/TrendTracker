import time
import httpx
from typing import Optional, Tuple, Dict, Any
from app.config import settings

HEADERS = {
    "User-Agent": settings.USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/rss+xml,application/atom+xml,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

async def fetch_url(
    url: str,
    timeout: float = settings.REQUEST_TIMEOUT_SECONDS,
    follow_redirects: bool = True,
    headers: Optional[Dict[str, str]] = None
) -> Tuple[Optional[str], Optional[httpx.Response], float, Optional[str]]:
    """
    Fetches a URL asynchronously with latency measurement and error handling.
    Returns: (content, response_obj, response_time_ms, error_message)
    """
    req_headers = HEADERS.copy()
    if headers:
        req_headers.update(headers)

    start_time = time.perf_counter()
    try:
        async with httpx.AsyncClient(
            verify=False,
            follow_redirects=follow_redirects,
            timeout=httpx.Timeout(timeout, connect=timeout / 2)
        ) as client:
            resp = await client.get(url, headers=req_headers)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            
            if resp.status_code >= 400:
                return None, resp, elapsed_ms, f"HTTP Status {resp.status_code}: {resp.reason_phrase}"
            
            return resp.text, resp, elapsed_ms, None
    except httpx.TimeoutException:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return None, None, elapsed_ms, f"Request timed out after {timeout}s"
    except httpx.ConnectError as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return None, None, elapsed_ms, f"Connection error: {str(e)}"
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return None, None, elapsed_ms, f"Fetch error: {str(e)}"
