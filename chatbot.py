# chatbot.py - Chatbot implementation using OpenAI LLM for responses and local embeddings for RAG
import logging
from typing import List, Dict, Tuple, Optional
import openai
import tiktoken

import config
from utils import count_tokens, format_context, format_chat_history
from vector_store import VectorStore

class Chatbot:
    """Chatbot using OpenAI LLM and RAG with local embeddings"""
    
    def __init__(self, vector_store: VectorStore):
        """Initialize the chatbot"""
        self.vector_store = vector_store
        self.model = config.OPENAI_CHAT_MODEL
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Configure OpenAI client
        try:
            # Set API key directly (old style)
            openai.api_key = config.OPENAI_API_KEY
            self.client = openai
            logging.info("OpenAI client initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing OpenAI client: {str(e)}")
            logging.error(f"API Key length: {len(config.OPENAI_API_KEY) if config.OPENAI_API_KEY else 0}")
            self.client = None
        
        if not config.OPENAI_API_KEY:
            logging.warning("OPENAI_API_KEY not set. OpenAI chat completion will not work.")
        else:
            logging.info(f"Using OpenAI chat model: {self.model}")
    
    def generate_answer(self, question: str, chat_history: Optional[List[Dict]] = None) -> Tuple[str, List[Dict]]:
        """Generate an answer using RAG with local embeddings and OpenAI's chat completion"""
        # Step 1: Retrieve relevant documents using local embeddings
        relevant_docs = self.vector_store.search(question, top_k=config.MAX_SEARCH_RESULTS)
        
        if not relevant_docs:
            return (
                "I don't have any economic data to answer your question. Please add some relevant documents first.",
                []
            )
        
        # Step 2: Create context from retrieved documents
        context = format_context(relevant_docs)
        
        # Step 3: Count tokens to ensure we're within limits
        context_tokens = count_tokens(context)
        question_tokens = count_tokens(question)
        history_tokens = 0
        
        # Format and count chat history tokens if provided
        formatted_history = []
        if chat_history:
            formatted_history = format_chat_history(chat_history)
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in formatted_history])
            history_tokens = count_tokens(history_text)
        
        total_tokens = context_tokens + question_tokens + history_tokens
        logging.info(f"Total input tokens: {total_tokens}")
        
        # Step 4: Create the prompt with context and question
        system_prompt = f"""You are an economic assistant that helps with questions about the economy.
Answer the question based on the provided context information. If you cannot answer from the context, say you don't have enough information.

Use the sources to provide an informed response. Cite sources by their numbers [1], [2], etc. when you use information from them.

Context information:
{context}
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add chat history if provided (limited to save tokens)
        if formatted_history:
            # Only use the most recent messages to save tokens
            recent_history = formatted_history[-3:] if len(formatted_history) > 3 else formatted_history
            messages.extend(recent_history)
            
        # Add the current question
        messages.append({"role": "user", "content": question})
        
        # Step 5: Generate response from OpenAI for high-quality answers
        try:
            if not config.OPENAI_API_KEY:
                raise ValueError("OpenAI API key is not set. Cannot generate response.")
            
            if self.client is None:
                raise ValueError("OpenAI client is not initialized properly.")
            
            # Use the OpenAI client to generate a response (old style)
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=config.TEMPERATURE,
                max_tokens=config.MAX_TOKENS_RESPONSE
            )
            
            answer = response['choices'][0]['message']['content']
            
            # Return the answer and sources
            sources = [{"id": doc["id"], "source": doc["source"]} for doc in relevant_docs]
            return answer, sources
            
        except Exception as e:
            logging.error(f"Error generating answer: {e}")
            return f"I'm sorry, there was an error processing your request: {str(e)}", []
    
    def process_feedback(self, question: str, answer: str, feedback: str, relevant_docs: List[Dict]) -> None:
        """Process user feedback on answers (for future improvement)"""
        # This could be expanded to log feedback, retrain models, or adjust relevance scores
        logging.info(f"Received feedback: {feedback}")
        # For now, just log the feedback
        feedback_log = {
            "question": question,
            "answer": answer,
            "feedback": feedback,
            "sources": [doc["id"] for doc in relevant_docs]
        }
        logging.info(f"Feedback log: {feedback_log}")