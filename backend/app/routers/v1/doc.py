from fastapi import APIRouter, status, Depends, Request, File, UploadFile
from app.services.keycloak_service import kc_admin
from app.schemas.doc_schema import ParseRequest
import logging

logger = logging.getLogger("app.routers.doc")
router = APIRouter(prefix="/doc", tags=["Documents"])


@router.post(
    "/parse",
    status_code=status.HTTP_200_OK,
    tags=["Documents"],
    summary="Parse a PDF Document",
    description="""
              Takes a PDF file path or URL as input and parses the document to extract its content.
                """,
)
async def parse_url(
    request: Request, doc: ParseRequest, user=Depends(kc_admin.get_current_user)
):
    req_id = getattr(request.state, "request_id", "-")
    logger.info(
        f"Received request to parse document {doc.url} for user {user.get('sub')}",
        extra={"request_id": req_id},
    )
    return {"detail": f"Received request to parse documents for user {user.get('sub')}"}


@router.post(
    "/upload",
    status_code=status.HTTP_200_OK,
    tags=["Documents"],
    summary="Upload a PDF Document",
    description="""
                Uploads a PDF file to the server for parsing.
                    """,
)
async def parse_upload(
    request: Request,
    file: UploadFile = File(...),
    user=Depends(kc_admin.get_current_user),
):
    req_id = getattr(request.state, "request_id", "-")
    logger.info(
        f"Received request to upload document {file.filename} for user {user.get('sub')}",
        extra={"request_id": req_id},
    )
    return {
        "detail": f"Received request to upload document {file.filename} for user {user.get('sub')}"
    }
