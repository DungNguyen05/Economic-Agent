# Economic Chatbot with Memory and Mattermost Integration

A Python-based economic chatbot that remembers conversation history and uses Retrieval-Augmented Generation (RAG) to answer questions accurately. This system maintains conversational context across interactions while efficiently retrieving relevant information from your knowledge base. Now with Mattermost integration!

## Key Features

- **Conversation Memory** - Maintains chat history across sessions with server-side and client-side persistence
- **Smart Retrieval** - Selectively uses document retrieval only when necessary, based on query complexity
- **Token Optimization** - Minimizes token usage while maintaining high-quality responses
- **Hybrid Knowledge** - Seamlessly switches between document-based and general knowledge responses
- **User-Friendly Interface** - Clean UI with typing indicators and session management
- **Persistent Storage** - Multi-layer storage with cookies, localStorage, and server-side session management
- **Mattermost Integration** - Connect to Mattermost via outgoing webhooks

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
   
4. **Mattermost Integration**
   - Webhook-based integration with Mattermost
   - Maintains conversation context per Mattermost user
   - Supports trigger words for bot activation
   - Formats responses according to Mattermost requirements

## Getting Started

### Prerequisites

- Python 3.10+
- OpenAI API key (the only external dependency)
- Everything else runs locally

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
   # Edit .env to add your OpenAI API key (OPENAI_API_KEY=your_key_here)
   ```

5. Run the application locally:
   ```
   python app.py
   ```

6. Access the web interface at [http://localhost:8000](http://localhost:8000)

The application uses:
- Local embedding models with sentence-transformers
- Local vector database (Qdrant) stored in the data directory
- Local file storage for documents
- OpenAI API (the only external service) for generating responses

## Mattermost Integration

### Setting Up Mattermost Outgoing Webhooks

1. In your Mattermost instance, go to **System Console** > **Integrations** > **Outgoing Webhooks**
2. Click **Add Outgoing Webhook**
3. Configure the webhook:
   - **Title**: Economic Assistant
   - **Description**: AI-powered economic assistant
   - **Content Type**: application/x-www-form-urlencoded
   - **Channel**: Choose the channel where the bot should respond (or leave blank for all channels)
   - **Trigger Words**: Add trigger words like @econ-bot
   - **Trigger When**: Start With A Trigger Word
   - **Callback URLs**: http://your-server-address:8000/webhook/mattermost
   - **Response Username**: Economic Bot (or your preferred name)
   - **Response Icon**: (Optional) URL to a bot avatar
4. Save the configuration

### Testing the Integration

You can use the included test script to verify the integration:

```
python test_mattermost_webhook.py --url http://your-server-address:8000
```

### Interacting with the Bot in Mattermost

Once configured, you can interact with the bot in Mattermost by using the trigger word:

```
@econ-bot What is inflation?
```

The bot will respond in the same channel with the answer.

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

## Storage Implementation

The application uses several local storage mechanisms:

### 1. In-Memory Session Storage
- Conversation histories are stored in Python dictionaries within the server process
- Located in `core/chatbot.py` as `self.session_histories` dictionary
- This memory persists only while the server is running
- No database required for this storage

### 2. Document Storage
- Document metadata is stored in a local JSON file (`data/documents.json`)
- Document content is stored in the local vector database
- Managed by the `DocumentManager` class in `core/document_manager.py`
- All files are saved in your local file system

### 3. Vector Database Storage
- Uses Qdrant vector database running in local mode (no separate server)
- Vector database files stored in `data/qdrant_storage/`
- Embeddings generated locally using sentence-transformers
- Completely self-contained with no external database connections

### 4. Client-Side Storage
- Browser localStorage stores conversation history as backup
- HTTP cookies track the session ID between page loads
- All client storage happens in your browser

When you run the application, all data remains on your machine. The "server" in this context is just the local Python application running on your computer - there is no remote server involved except when generating responses via OpenAI's API.

### RAG Optimization

The system uses an intelligent approach to RAG, with all retrieval happening locally:

1. Evaluates query complexity to determine if RAG is needed
2. Only retrieves documents for domain-specific questions from local vector store
3. Uses general knowledge for common questions
4. Falls back to general knowledge if local documents don't provide a good answer

The vector embeddings are generated locally using sentence-transformers, and 
document storage is handled by a local Qdrant instance that runs within the application.

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
├── app.py                    # Main FastAPI application (runs locally)
├── config.py                 # Configuration settings
├── ALGORITHM.md              # Algorithm documentation
│
├── core/                     # Core application logic
│   ├── chatbot.py            # Main chatbot with memory (local storage)
│   ├── document_manager.py   # Document handling (local files)
│   └── utils.py              # Utility functions
│
├── rag/                      # Local RAG components
│   ├── chains.py             # LLM chains for RAG
│   ├── embeddings.py         # Local embedding models
│   ├── retriever.py          # Local retrieval strategies
│   └── vector_store.py       # Local vector database
│
├── api/                      # Local API endpoints
│   ├── models.py             # API data models
│   ├── routes.py             # API route handlers
│   ├── openai_compat.py      # OpenAI compatibility API
│   ├── mattermost.py         # Mattermost webhook handler
│   └── dependencies.py       # FastAPI dependencies
│
├── static/                   # Static files (served locally)
│   ├── chat.js               # Chat functionality
│   └── styles.css            # CSS styles
│
├── templates/                # HTML templates (rendered locally)
│   └── index.html            # Main interface
│
├── test_mattermost_webhook.py  # Test script for Mattermost integration
│
└── data/                     # Local data storage
    ├── qdrant_storage/       # Local vector database files
    ├── documents.json        # Local document metadata storage
    └── transformers_cache/   # Local model cache for embeddings
```

All components run locally on your machine, with the only external dependency being 
the OpenAI API for generating the final text responses.

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

4. **Mattermost integration issues**
   - Check the server logs for webhook processing details
   - Verify the webhook URL is correctly configured in Mattermost
   - Ensure network connectivity between Mattermost and your server
   - Run the test_mattermost_webhook.py script to verify the endpoint

## License

This project is licensed under the MIT License.