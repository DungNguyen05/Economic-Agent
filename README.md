# Economic Chatbot with Hybrid RAG

This is a Python-based economic chatbot that uses a hybrid Retrieval-Augmented Generation (RAG) approach to answer questions about economics. The system uses local embeddings to efficiently store documents and OpenAI's language models for high-quality responses.

## Features

- **Hybrid RAG Implementation**: Local embeddings for storage + OpenAI for responses
- **Token Optimization**: Significantly reduces OpenAI API usage by only using tokens for responses
- **Vector Search**: Uses Qdrant for efficient similarity search (scale to thousands of documents)
- **Document Management**: Add, view, and search economic documents
- **Web Interface**: User-friendly chat interface with document management
- **REST API**: Complete API for integration with other applications
- **Environment-based Configuration**: Easy configuration through environment variables

## Advantages of Hybrid Approach

This application uses a cost-effective hybrid architecture:

1. **Local Embeddings** (Sentence Transformers)
   - Document vectorization runs locally without API calls
   - Saves tokens for each document you add
   - Uses the efficient "all-MiniLM-L6-v2" model by default

2. **OpenAI Responses**
   - High-quality, nuanced answers from GPT models
   - Only uses tokens when generating responses
   - Properly formats prompts with retrieved context

3. **Token Savings**:
   - Eliminate token usage for document storage/embedding
   - Pay only for tokens used in actual chat responses
   - For large knowledge bases, savings can be substantial

## Why Qdrant?

Qdrant is an excellent vector database choice for this economic chatbot, especially when handling thousands of economic articles:

1. **Easy to Install**: Simple pip installation, no complex C++ dependencies like FAISS
2. **High Performance**: Efficiently handles thousands to millions of vectors
3. **Persistence**: Built-in storage management with automatic persistence
4. **Filtering**: Advanced metadata filtering beyond simple vector similarity
5. **Production Ready**: Runs in-memory for development or can be deployed as a service
6. **Active Development**: Well-maintained with regular updates and improvements

## Project Structure

```
economic_chatbot/
│
├── app.py                    # Main FastAPI application
├── config.py                 # Configuration with environment variables
├── models.py                 # API data models
├── vector_store.py           # Vector database using Qdrant
├── chatbot.py                # Chat functionality using OpenAI
├── utils.py                  # Utility functions
├── example_data.py           # Example economic data
├── templates_manager.py      # Templates verification
│
├── templates/                # HTML templates
│   └── index.html            # Main interface template
│
├── static/                   # Static files
│   └── styles.css            # CSS styles
│
├── data/                     # Data storage (auto-created)
│   ├── qdrant_storage/       # Qdrant vector database files
│   └── documents.json        # Document metadata
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

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up configuration:
   ```
   # Create a .env file with your OpenAI API key
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
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

## Usage

### Adding Economic Data

1. Navigate to the web interface
2. Use the "Add Document" tab to add economic data
3. Provide a source and content for the document

### Adding Thousands of Articles

For bulk loading thousands of economic articles, you can use the API:

```python
import requests
import json

def add_article(content, source, metadata=None):
    response = requests.post(
        "http://localhost:8000/api/documents",
        json={
            "content": content,
            "source": source,
            "metadata": metadata or {}
        }
    )
    return response.json()

# Example batch processing from a large dataset
with open("economic_articles.json", "r") as f:
    articles = json.load(f)
    
for article in articles:
    add_article(
        content=article["text"],
        source=article["source"],
        metadata={
            "date": article["date"],
            "author": article["author"],
            "category": article["category"]
        }
    )
```

### Asking Questions

1. Type your economic question in the chat input
2. The chatbot will retrieve relevant information using local embeddings
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
2. **Deployment Options**:
   - Docker Compose for simple deployments
   - Kubernetes for large-scale deployments with multiple replicas
3. **Optimizations**:
   - Configure Qdrant for disk-based storage for very large collections
   - Implement batched indexing for initial bulk loading
   - Consider sharding for collections over 10 million vectors

## License

This project is licensed under the MIT License.