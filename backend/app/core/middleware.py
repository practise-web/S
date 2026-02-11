from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from app.core.context import request_id_ctx
from app.core.config import kcsettings
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.core import database as db
import json
import uuid
import logging
import time
import httpx
import jwt

logger = logging.getLogger("app.core.middleware")

class PhantomTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Priority: Check Cookie first
        phantom_token = request.cookies.get("session_id")
        # If not in cookie, check Authorization header
        if not phantom_token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                phantom_token = auth_header.split(" ")[1]

        # We let the route handler decide if it needs auth (returns 401 or 403 later)
        if not phantom_token:
            return await call_next(request)

        try:
            data_json = await db.redis_client.get(f"session:{phantom_token}")
            
            if not data_json:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Session expired or revoked"}
                )
            session_data = json.loads(data_json)
            session_data = await self.validate_session_data(session_data, phantom_token)
            
            if session_data is None:
                await db.redis_client.delete(f"session:{phantom_token}")
                response = JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Session expired fully"}
                )
                response.delete_cookie("session_id")
                return response

            # INJECT REAL JWT
            headers = dict(request.scope["headers"])
            headers[b"authorization"] = f"Bearer {session_data['access_token']}".encode("latin-1")
            request.scope["headers"] = list(headers.items())

        except Exception as e:
            print(f"Redis Error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )

        response = await call_next(request)
        return response
    
    async def validate_session_data(self, session_data, phantom_token):
        try:
            payload = jwt.decode(session_data['access_token'], options={"verify_signature": False})
            is_expired = False
            # Check if current time > exp time
            import time
            if time.time() > payload["exp"]:
                is_expired = True
        except:
            is_expired = True
        
        if(is_expired):
            refresh_response = await self.refresh_keycloak_token(session_data['refresh_token'])
            if refresh_response.status_code != 200:
                logger.error(f"Keycloak refresh failed: {refresh_response.text}")
                return None # could not refresh, session is invalid
            refresh_response = refresh_response.json()
            session_data['access_token'] = refresh_response['access_token']
            session_data['refresh_token'] = refresh_response.get('refresh_token', session_data['refresh_token'])
            await db.redis_client.setex(f"session:{phantom_token}", refresh_response.get("refresh_expires_in", 1800), json.dumps(session_data))
        return session_data

    async def refresh_keycloak_token(self, refresh_token):
        payload = {
            "client_id": kcsettings.KEYCLOAK_CLIENT_ID,
            "client_secret": kcsettings.KEYCLOAK_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        async with httpx.AsyncClient() as client:
            return await client.post(kcsettings.KEYCLOAK_TOKEN_URL, data=payload)

class RequestIdMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """Attach a unique request id to each request and response."""
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = req_id
        request_id_ctx.set(req_id)
        
        response: Response = await call_next(request)
        
        response.headers["X-Request-ID"] = req_id
        return response
    

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        log_message = (
            f"{request.method} {request.url.path} "
            f"completed in {process_time:.2f}ms "
            f"status {response.status_code}"
        )
        logger.info(log_message)
        return response
