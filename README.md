# Economic Chatbot with Memory

A Python-based economic chatbot that remembers conversation history and uses Retrieval-Augmented Generation (RAG) to answer questions accurately. This system maintains conversational context across interactions while efficiently retrieving relevant information from your knowledge base.

## Key Features

- **Conversation Memory** - Maintains chat history across sessions with server-side and client-side persistence
- **Smart Retrieval** - Selectively uses document retrieval only when necessary, based on query complexity
- **Token Optimization** - Minimizes token usage while maintaining high-quality responses
- **Hybrid Knowledge** - Seamlessly switches between document-based and general knowledge responses
- **User-Friendly Interface** - Clean UI with typing indicators and session management
- **Persistent Storage** - Multi-layer storage with cookies, localStorage, and server-side session management

## System Architecture

This chatbot uses a sophisticated hybrid architecture:

1. **Memory Management**
   - Server-side session tracking with unique session IDs
   - Client-side localStorage for persistence across page reloads
   - Cookie-based session synchronization
   - Sliding window history truncation for token efficiency

2. **RAG Implementation**
   - Query complexity evaluation to determine when to use RAG
   - Context-aware document retrieval with conversation history
   - Source citation and formatting
   - Fallback to general knowledge when documents are insufficient

3. **Token Optimization**
   - Selective RAG usage based on query type
   - History truncation to manage context window
   - Efficient prompt formatting
   - Token usage tracking and analysis

## Getting Started

### Prerequisites

- Python 3.10+
- OpenAI API key
- Vector database support (Qdrant)

### Installation

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

4. Configure your environment:
   ```
   cp .env.example .env
   # Edit .env to add your OpenAI API key
   ```

5. Run the application:
   ```
   python app.py
   ```

6. Access the web interface at [http://localhost:8000](http://localhost:8000)

## Usage

### Adding Economic Data

1. Navigate to the web interface
2. Use the "Add Document" tab to add economic data
3. Provide a source and content for the document

### Asking Questions

1. Type your question in the chat input
2. The chatbot will:
   - Remember previous conversation context
   - Retrieve relevant information using RAG when needed
   - Use general knowledge for questions outside its document base
   - Provide source citations for information from your documents

### Managing Sessions

- Your conversation history persists between page reloads
- Use the "Clear Chat" button to reset the conversation
- Sessions are automatically maintained with cookies

## Implementation Details

### Memory Management

The chatbot uses a multi-layered approach to memory:

```
Server-side session storage
↓
HTTP cookie tracking
↓
Client-side localStorage backup
```

This ensures robust persistence across different scenarios:
- Browser refreshes
- Tab closures
- Server restarts

### RAG Optimization

The system uses an intelligent approach to RAG:

1. Evaluates query complexity to determine if RAG is needed
2. Only retrieves documents for domain-specific questions
3. Uses general knowledge for common questions
4. Falls back to general knowledge if documents don't provide a good answer

### Token Efficiency

Several strategies minimize token usage:

1. Limited history context (last 5 interactions)
2. Selective RAG usage
3. Efficient prompt formatting
4. Context compression

## Configuration Options

Key configuration settings in `config.py`:

```python
# Memory settings
MAX_TOKENS_RESPONSE = 500    # Maximum tokens in responses
TEMPERATURE = 0.3            # Response creativity (0.0-1.0)
MAX_CONTEXT_LENGTH = 4000    # Maximum context window size
```

## Project Structure

```
economic_chatbot/
│
├── app.py                    # Main FastAPI application
├── config.py                 # Configuration settings
├── ALGORITHM.md              # Algorithm documentation
│
├── core/                     # Core application logic
│   ├── chatbot.py            # Main chatbot with memory
│   ├── document_manager.py   # Document handling
│   └── utils.py              # Utility functions
│
├── rag/                      # RAG components
│   ├── chains.py             # LLM chains for RAG
│   ├── embeddings.py         # Embedding models
│   ├── retriever.py          # Retrieval strategies
│   └── vector_store.py       # Vector database
│
├── api/                      # API endpoints
│   ├── models.py             # API data models
│   ├── routes.py             # API route handlers
│   └── dependencies.py       # FastAPI dependencies
│
├── static/                   # Static files
│   ├── chat.js               # Chat functionality
│   └── styles.css            # CSS styles
│
├── templates/                # HTML templates
│   └── index.html            # Main interface
│
└── data/                     # Data storage
    └── qdrant_storage/       # Vector database files
```

## Troubleshooting

### Common Issues

1. **Memory not persisting**
   - Check browser cookies and localStorage
   - Verify server logs for session creation
   - Ensure session_id cookie is being set

2. **RAG not retrieving relevant documents**
   - Add more diverse economic data
   - Check logs for "Using RAG for this query" messages
   - Verify documents are properly added to the vector store

3. **High token usage**
   - Reduce MAX_CONTEXT_LENGTH in config.py
   - Decrease conversation history length in chatbot.py
   - Use more focused, shorter documents

## License

This project is licensed under the MIT License.