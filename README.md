# Economic Chatbot with Advanced RAG

A Python-based economic chatbot that uses advanced Retrieval-Augmented Generation (RAG) techniques powered by Langchain to answer questions about economics. The system uses local embeddings to efficiently store documents and OpenAI's language models for high-quality responses.

## Features

- **Advanced RAG Implementation**: Document chunking, query expansion, and contextual compression
- **Token Optimization**: Significantly reduces OpenAI API usage by only using tokens for responses
- **Vector Search**: Uses Qdrant with Langchain for efficient similarity search (scale to thousands of documents)
- **Document Management**: Add, view, and search economic documents
- **Web Interface**: User-friendly chat interface with document management
- **REST API**: Complete API for integration with other applications
- **Environment-based Configuration**: Easy configuration through environment variables

## Architecture

This application uses a sophisticated hybrid architecture:

1. **Local Embeddings** (Sentence Transformers)
   - Document vectorization runs locally without API calls
   - Saves tokens for each document you add
   - Uses the efficient "all-MiniLM-L6-v2" model by default
   - Configurable with different embedding models

2. **OpenAI Responses**
   - High-quality, nuanced answers from GPT models
   - Only uses tokens when generating responses
   - Properly formats prompts with retrieved context

3. **Advanced RAG Techniques**
   - Semantic document chunking for better context preservation
   - Query expansion to bridge vocabulary gaps
   - Context compression to focus on relevant information
   - Conversation history awareness for better continuity

## Project Structure

```
economic_chatbot/
│
├── app.py                    # Main FastAPI application
├── config.py                 # Configuration with environment variables
├── example_data.py           # Example economic data
│
├── rag/                      # RAG components 
│   ├── __init__.py           # Package initialization
│   ├── embeddings.py         # Manages embedding models
│   ├── vector_store.py       # Qdrant vector storage
│   ├── retriever.py          # Advanced retrieval strategies
│   └── chains.py             # LLM chains for RAG
│
├── core/                     # Core application logic
│   ├── __init__.py           # Package initialization
│   ├── chatbot.py            # Main chatbot implementation
│   ├── document_manager.py   # Document handling
│   └── utils.py              # Utility functions
│
├── api/                      # API endpoints
│   ├── __init__.py           # Package initialization
│   ├── models.py             # API data models
│   ├── routes.py             # API route handlers
│   └── dependencies.py       # FastAPI dependencies
│
├── web/                      # Web interface
│   ├── __init__.py           # Package initialization
│   ├── routes.py             # Web routes
│   └── templates_manager.py  # Templates verification
│
├── templates/                # HTML templates
│   └── index.html            # Main interface template
│
├── static/                   # Static files
│   └── styles.css            # CSS styles
│
├── .env.example              # Example environment variables
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose setup
└── requirements.txt          # Project dependencies
```

## Installation

### Local Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/economic-chatbot.git
   cd economic-chatbot
   ```

2. Create a virtual environment with Python 3.11:
   ```
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up configuration:
   ```
   # Create a .env file with your OpenAI API key
   cp .env.example .env
   # Edit the .env file and add your OpenAI API key
   ```

5. Run the application:
   ```
   python app.py
   ```

6. Access the web interface at [http://localhost:8000](http://localhost:8000)

### Docker Installation

1. Set your OpenAI API key:
   ```
   export OPENAI_API_KEY=your_api_key_here
   ```

2. Run with Docker Compose:
   ```
   docker-compose up -d
   ```
   
   This will:
   - Build the Docker image
   - Start the container
   - Mount the data directory for persistence
   - Pass your OpenAI API key to the container

3. Access the web interface at [http://localhost:8000](http://localhost:8000)

## Configuration Options

The application is highly configurable through environment variables:

### Embedding Model Selection

```
# Options:
# - all-MiniLM-L6-v2 (fast, good quality, default)
# - multi-qa-mpnet-base-dot-v1 (better quality, more resource intensive)
# - all-mpnet-base-v2 (best quality, more resource intensive)
# - paraphrase-multilingual-mpnet-base-v2 (for multilingual support)
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### RAG Settings

```
# Document chunking
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Advanced RAG features
USE_QUERY_EXPANSION=true
USE_RERANKING=true
```

### OpenAI Settings

```
OPENAI_API_KEY=your_api_key_here
OPENAI_CHAT_MODEL=gpt-3.5-turbo
MAX_TOKENS_RESPONSE=500
TEMPERATURE=0.3
```

## Usage

### Adding Economic Data

1. Navigate to the web interface
2. Use the "Add Document" tab to add economic data
3. Provide a source and content for the document

### Asking Questions

1. Type your economic question in the chat input
2. The chatbot will retrieve relevant information using advanced RAG techniques
3. OpenAI will generate a high-quality response based on the retrieved documents
4. Sources used to answer the question will be displayed with the response

### Using the API

Example of using the chat API with curl:

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What was the inflation rate in 2023?",
    "chat_history": []
  }'
```

## Scaling to Production

For production environments with thousands of articles:

1. **Resource Consideration**: Ensure sufficient memory for embeddings (approximately 1GB per 50,000 articles)
2. **Model Selection**: Choose the embedding model based on your quality/performance needs
3. **Chunking Strategy**: Adjust chunk size and overlap based on your document types
4. **Deployment Options**:
   - Docker Compose for simple deployments
   - Kubernetes for large-scale deployments

## Advanced RAG Techniques

This implementation includes several advanced RAG techniques:

1. **Semantic Document Chunking**
   - Documents are intelligently split using RecursiveCharacterTextSplitter
   - Preserves semantic relationships between text sections
   - Configurable chunk size and overlap

2. **Query Transformation**
   - Transforms user questions into more effective search queries
   - Bridges vocabulary gaps between questions and documents
   - Uses LLM to identify key economic concepts

3. **Context Compression**
   - Extracts the most relevant passages from retrieved documents
   - Removes redundant or irrelevant information
   - Focuses the context provided to the LLM

4. **Conversational Context**
   - Maintains chat history for better continuity
   - Incorporates previous exchanges into retrieval process
   - Automatically manages token usage by limiting history length

## License

This project is licensed under the MIT License.