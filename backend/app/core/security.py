from fastapi import Request, Response
from starlette.middleware.cors import CORSMiddleware
from app.core.context import request_id_ctx
import uuid
import logging
import time


logger = logging.getLogger("app.middleware")
REQUEST_ID_HEADER = "X-Request-ID"

def setup_middlewares(app):
    # -------------------------
    # CORS middleware
    # -------------------------

    origins = [
        "*",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,       # which origins can access
        allow_credentials=True,      # allow cookies/auth headers
        allow_methods=["*"],         # GET, POST, PUT, etc.
        allow_headers=["*"],         # allow custom headers
    )

    # -------------------------
    # Request ID middleware
    # -------------------------


    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        """Attach a unique request id to each request and response."""
        req_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        # Attach to scope so later code can access
        request.state.request_id = req_id
        request_id_ctx.set(req_id)

        response: Response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = req_id
        return response

    # -------------------------
    # Logging middleware
    # -------------------------

    @app.middleware("http")
    async def logger_middleware(request: Request, call_next):
        """Attach a unique request id to each request and response."""
        start_time = time.time()
        response: Response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"{request.method} {request.url.path} completed in {process_time:.5f} ms with status {response.status_code}"
        )
        return response


