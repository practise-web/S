from fastapi import APIRouter, status, HTTPException, Depends, Request
from app.services.docling_pdf import runPDF
from app.core.security import get_current_user
from app.schemas.doc_schema import ParseRequest
from fastapi.responses import JSONResponse
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
async def parse(request: Request, doc: ParseRequest, user=Depends(get_current_user)):
    req_id = getattr(request.state, "request_id", "-")
    try:
        logger.info(
            f"[{req_id}] Starting to parse document: {doc.path} for user: {user.get('sub')}"
        )
        runPDF(doc.path)
        logger.info(f"[{req_id}] Successfully parsed document: {doc.path}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Doc parsed successfully"},
        )
    except Exception as e:
        logger.error(f"[{req_id}] Error parsing document: {doc.path} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing Doc: {str(e)}",
        )
