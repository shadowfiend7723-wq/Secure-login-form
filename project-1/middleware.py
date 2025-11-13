from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from typing import Dict
from fastapi import APIRouter


router= APIRouter()

class AdvancedMiddleware(BaseHTTPMiddleware):
    def __init__(self,app):
        super().__init__(app)
        self.rate_limit_records: Dict[str, float] = defaultdict(float)

    async def log_message(self, message:str):
        print(message)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        # Skip middleware for docs, openapi, redoc, login page, static assets and auth endpoints
        skip_prefixes = ("/docs", "/openapi", "/redoc", "/login", "/static", "/auth")
        if any(path.startswith(p) for p in skip_prefixes):
            return await call_next(request)

        # Determine client IP (may be None in some test environments)
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        # Bypass rate limiting for local requests (useful for browser/testing on localhost)
        is_local = client_ip in ("127.0.0.1", "::1", "localhost")

        if not is_local:
            # enforce a simple 1-second rate limit per IP
            if current_time - self.rate_limit_records[client_ip] < 1:
                return Response(content="Rate limit exceeded", status_code=429)

            self.rate_limit_records[client_ip] = current_time

        await self.log_message(f"Request to {path} from {client_ip}")

        start_time = time.time()
        response = await call_next(request)
        process_time= time.time() - start_time

        custom_headers = {"X-Process-Time": str(process_time)}
        # MutableHeaders behave like a dict; assign headers via indexing
        for header, value in custom_headers.items():
            response.headers[header] = value

        await self.log_message(f"Response for {path} took {process_time} seconds")

        return response
 
@router.get("/")
async def main():
    return {"message": "Hello, world"}
