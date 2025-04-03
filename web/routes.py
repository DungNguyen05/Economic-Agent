# web/routes.py - Web interface routes
import logging
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import config
from api.dependencies import get_document_manager

logger = logging.getLogger(__name__)

# Set up templates
templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))

# Create router
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def get_interface(request: Request):
    """Render the chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/upload", response_class=HTMLResponse)
async def upload_document(
    request: Request,
    content: str = Form(...),
    source: str = Form(...),
    document_manager=Depends(get_document_manager)
):
    """Upload a document from the web interface"""
    try:
        doc_id = document_manager.add_document(content, source)
        return templates.TemplateResponse(
            "index.html", 
            {"request": request, "message": f"Document added successfully with ID: {doc_id}"}
        )
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        return templates.TemplateResponse(
            "index.html", 
            {"request": request, "error": str(e)}
        )