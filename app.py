# app.py - Main FastAPI application with modular structure and Mattermost integration
import os
import time
import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import configuration
import config

# Import components
from rag.embeddings import EmbeddingsManager
from rag.vector_store import QdrantStore
from core.document_manager import DocumentManager
from core.chatbot import Chatbot
from web.templates_manager import create_templates
from example_data import load_example_data

# Import routers
from api.routes import router as api_router
from web.routes import router as web_router
from api.openai_compat import router as openai_compat_router
from api.mattermost import router as mattermost_router  # New Mattermost router

# Global variables to manage application state
embeddings_manager = None
vector_store = None
document_manager = None
chatbot = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    global embeddings_manager, vector_store, document_manager, chatbot
    
    # Startup logic
    try:
        # Verify templates exist
        create_templates()
        
        # Initialize embeddings manager
        try:
            logging.info("Initializing embeddings manager...")
            embeddings_manager = EmbeddingsManager()
        except Exception as e:
            logging.error(f"Failed to initialize embeddings manager: {e}")
            raise
        
        # Initialize vector store
        try:
            logging.info("Initializing vector store...")
            vector_store = QdrantStore(embeddings_manager)
        except Exception as e:
            logging.warning(f"Standard initialization failed: {e}")
            logging.info("Attempting initialization with force reset...")
            vector_store = QdrantStore(embeddings_manager, force_reset=True)
        
        # Initialize document manager
        logging.info("Initializing document manager...")
        document_manager = DocumentManager(vector_store)
        
        # Initialize chatbot
        logging.info("Initializing chatbot with advanced RAG...")
        chatbot = Chatbot(document_manager, vector_store)
        
        # Log configuration
        logging.info(f"Using local embedding model: {config.EMBEDDING_MODEL}")
        logging.info(f"Using OpenAI chat model: {config.OPENAI_CHAT_MODEL}")
        logging.info(f"Chunk size: {config.CHUNK_SIZE}, Chunk overlap: {config.CHUNK_OVERLAP}")
        logging.info(f"Using query expansion: {config.USE_QUERY_EXPANSION}")
        logging.info(f"Using reranking: {config.USE_RERANKING}")
        
        # Check OpenAI API key
        if not config.OPENAI_API_KEY:
            logging.warning("OPENAI_API_KEY not set. Set this environment variable for chat functionality.")
        
        # Load example data
        load_example_data(document_manager)
        
        logging.info("Application started successfully")
        
        yield  # This is where the application runs
    
    finally:
        # Cleanup logic
        logging.info("Application is shutting down")

# Initialize FastAPI application with lifespan context
app = FastAPI(
    title="Economic Chatbot with Mattermost Integration",
    description="A chatbot that answers questions about the economy using advanced RAG with Langchain, OpenAI for responses, and integrations for Mattermost",
    version="1.3.0",
    debug=config.DEBUG,
    lifespan=lifespan
)

# Add CORS middleware to allow requests from Mattermost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, you might want to restrict this in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")

# Include routers - Order matters here
app.include_router(openai_compat_router)  # Add OpenAI compatibility router FIRST
app.include_router(mattermost_router)     # Add Mattermost webhook router SECOND
app.include_router(api_router)
app.include_router(web_router)

# Authentication middleware for OpenAI compatibility
@app.middleware("http")
async def validate_api_key(request: Request, call_next):
    """Middleware to validate API key for OpenAI compatibility endpoints"""
    # Check if this is an OpenAI endpoint
    is_openai_path = request.url.path.startswith("/v1/") or request.url.path == "/chat/completions"
    
    # Skip validation for Mattermost webhook endpoints
    is_mattermost_webhook = request.url.path.startswith("/webhook/mattermost")
    
    if is_openai_path and not is_mattermost_webhook:
        logging.info(f"Received request to OpenAI compatible endpoint: {request.url.path}")
        auth_header = request.headers.get("Authorization")
        
        # Skip validation in debug mode
        if config.DEBUG:
            logging.warning("DEBUG mode enabled, skipping API key validation")
            response = await call_next(request)
            return response
            
        if auth_header:
            # Extract the token from the header
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
                # Validate the token against your configured API key
                if token == config.OPENAI_API_KEY:
                    # Token is valid, process the request
                    logging.info("API key validation successful")
                else:
                    logging.warning("Invalid API key provided")
                    return JSONResponse(
                        status_code=401,
                        content={"error": {"message": "Invalid API key", "type": "invalid_request_error"}}
                    )
            else:
                logging.warning("Malformed Authorization header")
                return JSONResponse(
                    status_code=401,
                    content={"error": {"message": "Invalid Authorization header format", "type": "invalid_request_error"}}
                )
        else:
            # No Authorization header provided
            logging.warning("Missing Authorization header")
            return JSONResponse(
                status_code=401,
                content={"error": {"message": "Missing API key", "type": "invalid_request_error"}}
            )
    
    # Continue processing the request
    response = await call_next(request)
    return response

# Add a basic root endpoint
@app.get("/")
async def root():
    """Root endpoint that redirects to documentation if no UI is accessed"""
    return {
        "status": "online",
        "service": "Economic Chatbot API",
        "version": "1.3.0",
        "ui_url": "/index.html",
        "docs_url": "/docs",
        "openai_compatible": True,
        "mattermost_webhook_url": "/webhook/mattermost",
        "time": int(time.time())
    }

# Run the application
if __name__ == "__main__":
    # Configure logging before starting
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logging.info(f"Starting Economic Chatbot on {config.HOST}:{config.PORT}")
    uvicorn.run(
        "app:app", 
        host=config.HOST, 
        port=config.PORT, 
        reload=config.RELOAD,
        log_level=config.LOG_LEVEL.lower()
    )