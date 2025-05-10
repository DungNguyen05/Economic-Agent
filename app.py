import os
import time
import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
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
from api.mattermost import router as mattermost_router

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
    title="Economic Chatbot with Advanced RAG",
    description="A chatbot that answers questions about the economy using advanced RAG with Langchain, local embeddings and OpenAI for responses",
    version="1.1.0",
    debug=config.DEBUG,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, you might want to restrict this in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")

# Include routers
app.include_router(mattermost_router)
app.include_router(api_router)
app.include_router(web_router)

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "app:app", 
        host=config.HOST, 
        port=config.PORT, 
        reload=config.RELOAD
    )