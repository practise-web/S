from app.services.docling_pdf import runPDF
from app.schemas.doc_schema import ParseRequest
from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/doc", tags=["Document_Parsing"])


@router.post(
    "/parse",
    status_code=status.HTTP_200_OK,
    tags=["Document_Parsing"],
    summary="Parse a PDF Document",
    description="""
              Takes a PDF file path or URL as input and parses the document to extract its content.
                """,
)
async def parse(doc: ParseRequest):
    try:
        runPDF(doc.path)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "PDF parsed successfully"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing PDF: {str(e)}",
        )
