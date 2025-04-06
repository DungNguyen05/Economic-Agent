# Enhanced Chatbot Algorithm

This document explains the key algorithms and approaches used in the enhanced chatbot implementation.

## 1. Core Algorithm: Hybrid RAG + General Knowledge

The enhanced chatbot uses a hybrid approach that combines Retrieval-Augmented Generation (RAG) with general language model capabilities:

```
ALGORITHM: Hybrid Response Generation
Input: User question, Chat history, Session ID
Output: Answer with optional sources

1. Get session history from memory or initialize new history
2. Format and merge provided chat history with session history
3. IF document repository has documents THEN
   a. Perform RAG retrieval to find relevant documents
   b. Generate answer using RAG with retrieved documents and history context
   c. Extract source references from retrieved documents
   d. IF answer contains sources AND doesn't indicate insufficient information THEN
      i. Update session history
      ii. RETURN answer with sources
4. Generate general answer using language model with chat history context
5. Update session history with new interaction
6. RETURN general answer without sources
```

This algorithm allows the chatbot to:
- Use document knowledge when relevant
- Fall back to general capabilities when documents don't have the answer
- Maintain contextual awareness across multiple messages

## 2. Session Management

The chatbot maintains persistent sessions to track conversation context:

```
ALGORITHM: Session Management
Input: Session ID (or null), user message, assistant message
Output: Updated session history

1. IF session ID not in session store THEN
   a. Create new empty session history
2. Append (user message, assistant message) pair to session history
3. Truncate history to last 5 interactions to manage token usage
4. RETURN updated session history
```

Benefits:
- Preserves context across multiple messages
- Manages token usage by limiting history size
- Implements cookie-based session tracking in the API

## 3. RAG Implementation with Improved Prompting

The chatbot uses an enhanced RAG implementation with better prompting:

```
ALGORITHM: Enhanced RAG Prompting
Input: Question, Context documents, Chat history
Output: Coherent answer with source citations

1. Format chat history into readable format for context
2. Construct prompt that:
   a. Identifies the assistant's role (helpful with economics knowledge)
   b. Provides retrieved context documents
   c. Includes formatted chat history
   d. States the current question
   e. Instructs on citation format for information from sources
   f. Allows use of general knowledge when sources insufficient
3. Submit prompt to language model
4. Process and return response
```

## 4. Context Handling and Token Optimization

To optimize token usage while maintaining quality:

```
ALGORITHM: Context Optimization
Input: Chat history, Retrieved documents
Output: Optimized context for LLM

1. Limit chat history to 5 most recent interactions
2. Format chat history in compact user/assistant format
3. Use query expansion to improve document retrieval only when needed
4. Apply contextual compression to focus on relevant document sections
5. Track token usage for both RAG and general responses
6. Return optimized context within token constraints
```

## 5. Frontend Implementation with Persistent State

The frontend uses localStorage to maintain chat persistence:

```
ALGORITHM: Frontend State Management
Input: User interactions, Server responses
Output: Persistent chat interface

1. ON PAGE LOAD:
   a. Try to load chat history from localStorage
   b. IF history exists THEN render messages
   c. ELSE display welcome message
2. ON NEW MESSAGE:
   a. Display user message
   b. Show typing indicator
   c. Send message with history context to server
   d. Remove typing indicator and display response
   e. Save updated history to localStorage
3. ON CLEAR CHAT:
   a. Clear chat display
   b. Reset chat history array
   c. Remove history from localStorage
   d. Display new welcome message
```

## Technical Implementation Details

### Document Processing

- Documents are chunked using RecursiveCharacterTextSplitter with semantic awareness
- Chunk size (1000) and overlap (200) balance context preservation and retrieval precision
- Each chunk maintains metadata including source information and document ID

### Vector Retrieval

- Uses sentence-transformers with efficient "all-MiniLM-L6-v2" model
- Performs similarity search with adjustable parameters
- Documents are stored in Qdrant vector database for efficient retrieval

### Answer Generation

- The chatbot uses a two-stage approach:
  1. First attempt: RAG with document context
  2. Fallback: General LLM response

### Conversation Management

- The server maintains session state using cookies and in-memory storage
- The client provides conversation history with each request
- Both sides implement truncation strategies to keep within token limits