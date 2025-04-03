# api/routes.py - API routes for the economic chatbot
import logging
from fastapi import APIRouter, HTTPException, Depends

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
    chatbot=Depends(get_chatbot),
    api_key: str = Depends(validate_openai_key)
):
    """Chat with the economic assistant using Langchain RAG"""
    try:
        answer, sources = chatbot.generate_answer(request.question, request.chat_history)
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