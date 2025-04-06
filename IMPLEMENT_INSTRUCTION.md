# Implementation Instructions

Follow these steps to implement the enhanced chatbot with general question-answering abilities and better memory management:

## 1. File Updates

### Core Changes

1. **Replace `core/chatbot.py` with the enhanced version**
   - This is the main change that implements the hybrid RAG/general capability
   - The new implementation maintains session history and handles both document-based and general questions

2. **Replace `rag/chains.py` with the updated version**
   - This enhances the RAG chains with improved prompting
   - The updated prompts guide the model to use general knowledge when documents are insufficient

3. **Update `api/routes.py` with the session-aware version**
   - This adds session cookie handling for persistent conversations
   - The new routes maintain user session context across requests

### Frontend Changes

4. **Create a new file `static/chat.js`**
   - Copy the content from the "Updated Frontend JavaScript for Chat History" artifact
   - This separates the chat logic from the HTML template for better organization

5. **Update `templates/index.html`**
   - Replace with the updated HTML version
   - The updated template references the new external JS file and adds a clear chat button

6. **Update `static/styles.css`**
   - Replace with the enhanced CSS version
   - This adds styling for new UI elements like the typing indicator and clear button

## 2. Implementation Steps

### Backend Setup

1. **Update Python Files:**
   ```bash
   # Replace core files
   cp your-download-path/enhanced-chatbot.py core/chatbot.py
   cp your-download-path/updated-rag-chains.py rag/chains.py
   cp your-download-path/modified-api-routes.py api/routes.py
   ```

2. **Create the Algorithm Documentation:**
   ```bash
   cp your-download-path/ALGORITHM.md ./
   ```

### Frontend Setup

3. **Create JavaScript File:**
   ```bash
   # Create new JS file
   cp your-download-path/updated-web-js.js static/chat.js
   ```

4. **Update HTML and CSS:**
   ```bash
   # Update HTML template
   cp your-download-path/updated-html.html templates/index.html
   
   # Update CSS
   cp your-download-path/updated-css.css static/styles.css
   ```

## 3. Testing

After implementation, test these key functionalities:

1. **Economic Questions**
   - Add some economic documents
   - Ask questions directly related to the documents
   - Verify that answers include source citations

2. **General Questions**
   - Ask questions unrelated to economics (e.g., "How do I bake a cake?")
   - Verify the chatbot responds using its general knowledge

3. **Mixed Conversations**
   - Have a conversation that mixes economic and general questions
   - Verify the chatbot maintains context across question types

4. **Persistent Sessions**
   - Ask a question, reload the page, and refer to previous answers
   - Verify the chatbot understands the references

## 4. Advanced Configuration

To fine-tune the implementation, you can adjust these parameters in `config.py`:

- `MAX_TOKENS_RESPONSE`: Adjust token limit for responses
- `TEMPERATURE`: Adjust for more deterministic (lower) or creative (higher) responses
- `MAX_CONTEXT_LENGTH`: Adjust token limit for context window

Example:
```python
# More concise, focused responses
MAX_TOKENS_RESPONSE = 300
TEMPERATURE = 0.2

# More detailed, creative responses
MAX_TOKENS_RESPONSE = 700
TEMPERATURE = 0.7
```

## 5. Troubleshooting

If you encounter issues:

1. **Session Issues**
   - Check browser cookie storage for session_id
   - Verify the cookie is being correctly set and read by the API

2. **Memory Problems**
   - Check server logs for "history" related errors
   - Review session management implementation in chatbot.py

3. **General Response Quality**
   - Try adjusting the temperature parameter
   - Check the prompts in the rag_chains.py file