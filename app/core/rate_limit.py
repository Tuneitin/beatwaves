from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.lock = asyncio.Lock()

    async def check_rate_limit(self, client_id: str) -> bool:
        async with self.lock:
            now = datetime.now()
            window_start = now - timedelta(seconds=self.window_seconds)
            
            # Clean old requests
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if req_time > window_start
            ]
            
            if len(self.requests[client_id]) >= self.max_requests:
                return False
            
            self.requests[client_id].append(now)
            return True


def get_client_ip(request: Request) -> str:
    """Extract client IP from request, considering proxies."""
    if request.headers.get("x-forwarded-for"):
        return request.headers["x-forwarded-for"].split(",")[0].strip()
    return request.client.host if request.client else "unknown"
