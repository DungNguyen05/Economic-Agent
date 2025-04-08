# api/routes.py - Updated API routes with robust session support
import logging
from fastapi import APIRouter, HTTPException, Depends, Cookie, Response
import uuid
from typing import Optional

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
    session_id: Optional[str] = Cookie(None)
):
    """Chat with the assistant using Langchain RAG with session management"""
    try:
        # Create or use session ID for maintaining chat context
        if not session_id:
            session_id = str(uuid.uuid4())
            response.set_cookie(
                key="session_id", 
                value=session_id, 
                httponly=True,
                max_age=3600*24*7,  # 7 day cookie
                samesite="lax"
            )
            logger.info(f"Created new session: {session_id}")
        else:
            logger.info(f"Using existing session: {session_id}")
        
        # Generate answer using the chatbot with session context
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

@router.get("/session")
async def get_session_info(
    session_id: Optional[str] = Cookie(None),
    chatbot=Depends(get_chatbot)
):
    """Get information about the current session"""
    if not session_id:
        return {"has_session": False, "message": "No active session"}
    
    # Get session history
    history = chatbot.get_session_history(session_id)
    message_count = len(history)
    
    return {
        "has_session": True,
        "session_id": session_id,
        "message_count": message_count
    }

@router.delete("/session")
async def clear_session(
    response: Response,
    session_id: Optional[str] = Cookie(None),
    chatbot=Depends(get_chatbot)
):
    """Clear the current session history"""
    if session_id and session_id in chatbot.session_histories:
        # Clear the session history
        chatbot.session_histories[session_id] = []
        logger.info(f"Cleared session history for {session_id}")
        
    # Clear the cookie
    response.delete_cookie(key="session_id")
    
    return {"message": "Session cleared successfully"}