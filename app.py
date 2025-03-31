# app.py - Main application file
import os
import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import project modules
import config
import openai
from models import (
    DocumentInput, DocumentResponse, Query, ChatRequest, 
    ChatResponse, SearchResult
)
from vector_store import VectorStore
from chatbot import Chatbot
from example_data import load_example_data
from templates_manager import create_templates
from utils import generate_id, truncate_text

# Global variables to manage application state
vector_store = None
chatbot = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    global vector_store, chatbot
    
    # Startup logic
    try:
        # Verify templates exist
        create_templates()
        
        # Initialize vector store
        try:
            vector_store = VectorStore()
        except Exception as e:
            logging.warning(f"Standard initialization failed: {e}")
            logging.info("Attempting initialization with force reset...")
            vector_store = VectorStore(force_reset=True)
        
        # Initialize chatbot
        chatbot = Chatbot(vector_store)
        
        # Log model configuration
        logging.info(f"Using local embedding model: {config.EMBEDDING_MODEL}")
        logging.info(f"Using OpenAI chat model: {config.OPENAI_CHAT_MODEL}")
        
        # Check OpenAI API key
        if not config.OPENAI_API_KEY:
            logging.warning("OPENAI_API_KEY not set. Set this environment variable for chat functionality.")
        
        # Load example data
        load_example_data(vector_store)
        
        logging.info("Application started successfully")
        
        yield  # This is where the application runs
    
    finally:
        # Optional cleanup logic can go here
        logging.info("Application is shutting down")

# Initialize FastAPI application with lifespan context
app = FastAPI(
    title="Economic Chatbot",
    description="A chatbot that answers questions about the economy using RAG with local embeddings and OpenAI for responses",
    version="1.0.0",
    debug=config.DEBUG,
    lifespan=lifespan
)

# Set up templates and static files
templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")

# Dependency for OpenAI API Key validation
def validate_openai_key():
    if not config.OPENAI_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="OpenAI API key not configured. Set the OPENAI_API_KEY environment variable."
        )
    return config.OPENAI_API_KEY

# API Routes
@app.post("/api/documents", response_model=DocumentResponse)
async def add_document(document: DocumentInput):
    """Add a new document to the knowledge base"""
    try:
        doc_id = vector_store.add_document(
            document.content, 
            document.source,
            document.metadata
        )
        return {"id": doc_id, "message": "Document added successfully"}
    except Exception as e:
        logging.error(f"Error adding document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search", response_model=list[SearchResult])
async def search_documents(query: Query):
    """Search for documents in the knowledge base"""
    try:
        results = vector_store.search(query.question, query.max_results)
        return results
    except Exception as e:
        logging.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, api_key: str = Depends(validate_openai_key)):
    """Chat with the economic assistant using OpenAI for responses"""
    try:
        answer, sources = chatbot.generate_answer(request.question, request.chat_history)
        return {"answer": answer, "sources": sources}
    except Exception as e:
        logging.error(f"Error generating chat response: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Web Interface Routes
@app.get("/", response_class=HTMLResponse)
async def get_interface(request: Request):
    """Render the chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
async def upload_document(
    request: Request,
    content: str = Form(...),
    source: str = Form(...)
):
    """Upload a document from the web interface"""
    try:
        doc_id = vector_store.add_document(content, source)
        return templates.TemplateResponse(
            "index.html", 
            {"request": request, "message": f"Document added successfully with ID: {doc_id}"}
        )
    except Exception as e:
        logging.error(f"Error uploading document: {e}")
        return templates.TemplateResponse(
            "index.html", 
            {"request": request, "error": str(e)}
        )

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "app:app", 
        host=config.HOST, 
        port=config.PORT, 
        reload=config.RELOAD
    )