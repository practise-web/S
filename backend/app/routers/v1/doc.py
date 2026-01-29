from fastapi import APIRouter, status, HTTPException, Depends, Request, File, UploadFile
from app.services.docling_service import parse_pdf
from app.core.security import get_current_user
from app.schemas.doc_schema import ParseRequest
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
import logging
import shutil
import tempfile
import os

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
async def parse_url(request: Request, doc: ParseRequest, user=Depends(get_current_user)):
    req_id = getattr(request.state, "request_id", "-")
    logger.info(
        f"[{req_id}] Starting to parse document: {doc.path} for user: {user.get('sub')}"
    )
    try:
        await run_in_threadpool(parse_pdf, doc.path)
        logger.info(f"[{req_id}] Successfully parsed document: {doc.path}")
        return JSONResponse(status_code=status.HTTP_200_OK,content={"message": "Doc parsed successfully"},)
    except Exception as e:
        logger.error(f"[{req_id}] Error parsing document: {doc.path} - {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error parsing Doc: {str(e)}",)


@router.post(
    "/upload",
    status_code=status.HTTP_200_OK,
    tags=["Documents"],
    summary="Upload a PDF Document",
    description="""
                Uploads a PDF file to the server for parsing.
                    """,)
async def parse_upload(request: Request, file: UploadFile = File(...), user=Depends(get_current_user)):
    req_id = getattr(request.state, "request_id", "-")

    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF files are allowed")
    
    logger.info(
        f"[{req_id}] Starting to upload document: {file.filename} for user: {user.get('sub')}"
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    try:
        await run_in_threadpool(parse_pdf, tmp_path)
        logger.info(f"[{req_id}] Successfully uploaded and parsed document: {file.filename}")
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "File uploaded and parsed successfully"},)
    except Exception as e:
        logger.error(f"[{req_id}] Error uploading document: {file.filename} - {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error uploading Doc: {str(e)}",)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)