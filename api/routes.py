# api/routes.py - Updated API routes with session support
import logging
from fastapi import APIRouter, HTTPException, Depends, Cookie, Response
import uuid

from api.models import (
    DocumentInput, DocumentResponse, Query, 
    ChatRequest, ChatResponse, SearchResult
)
from api.dependencies import get_document_manager, get_chatbot, validate_openai_key

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api")

@router.post("/documents", response_model=DocumentResponse)
async def add_document(
    document: DocumentInput,
    document_manager=Depends(get_document_manager)
):
    """Add a new document to the knowledge base"""
    try:
        doc_id = document_manager.add_document(
            document.content, 
            document.source,
            document.metadata
        )
        return {"id": doc_id, "message": "Document added successfully"}
    except Exception as e:
        logger.error(f"Error adding document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=list[SearchResult])
async def search_documents(
    query: Query,
    document_manager=Depends(get_document_manager)
):
    """Search for documents in the knowledge base"""
    try:
        # Currently just using the vector search from chatbot
        results = []
        # Get all documents for now (more sophisticated search would be better)
        documents = document_manager.get_all_documents()
        
        # Simple keyword search as fallback
        for doc in documents[:query.max_results]:
            results.append({
                "id": doc["id"],
                "content": doc["content"],
                "source": doc["source"],
                "score": 1.0  # Placeholder score
            })
            
        return results
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    response: Response,
    chatbot=Depends(get_chatbot),
    api_key: str = Depends(validate_openai_key),
    session_id: str = Cookie(None)
):
    """Chat with the assistant using Langchain RAG"""
    try:
        # Create or use session ID for maintaining chat context
        if not session_id:
            session_id = str(uuid.uuid4())
            response.set_cookie(key="session_id", value=session_id, httponly=True)
            logger.info(f"Created new session: {session_id}")
        
        # Generate answer using the chatbot
        answer, sources = chatbot.generate_answer(
            request.question, 
            request.chat_history, 
            session_id
        )
        
        return {"answer": answer, "sources": sources}
    except Exception as e:
        logger.error(f"Error generating chat response: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{doc_id}")
async def get_document(
    doc_id: str,
    document_manager=Depends(get_document_manager)
):
    """Get a document by ID"""
    document = document_manager.get_document(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    document_manager=Depends(get_document_manager)
):
    """Delete a document by ID"""
    success = document_manager.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found or could not be deleted")
    return {"message": "Document deleted successfully"}