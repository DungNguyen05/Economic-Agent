# core/chatbot.py - Chatbot implementation using Langchain RAG
import logging
from typing import List, Dict, Tuple, Optional
import tiktoken
from langchain_community.chat_models import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI

import config
from rag.retriever import AdvancedRetriever
from rag.chains import RAGChainManager

logger = logging.getLogger(__name__)



class Chatbot:
    """Economic chatbot with advanced RAG"""
    
    def __init__(self, document_manager, vector_store):
        """Initialize the chatbot with necessary components"""
        self.document_manager = document_manager
        self.vector_store = vector_store
        self.model_name = config.OPENAI_CHAT_MODEL
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Initialize OpenAI LLM
        if not config.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set. OpenAI chat completion will not work.")
            self.llm = None
            self.rag_chain = None
        else:
            try:
                # Initialize LLM
                self.llm = ChatOpenAI(
                    model_name=self.model_name,
                    temperature=config.TEMPERATURE,
                    openai_api_key=config.OPENAI_API_KEY,
                    max_tokens=config.MAX_TOKENS_RESPONSE
                )
                
                # Get base retriever from vector store
                base_retriever = self.vector_store.get_retriever()
                
                # Set up advanced retriever
                advanced_retriever = AdvancedRetriever(self.llm, base_retriever)
                
                # Get query expansion chain if enabled
                query_expansion_chain = advanced_retriever.get_query_expansion_chain()
                
                # Set up RAG chain manager
                self.rag_chain = RAGChainManager(
                    self.llm,
                    advanced_retriever.get_retriever(),
                    query_expansion_chain
                )
                
                logger.info(f"Chatbot initialized with {self.model_name}")
                
            except Exception as e:
                logger.error(f"Error initializing chatbot: {e}")
                self.llm = None
                self.rag_chain = None
    
    def generate_answer(self, question: str, chat_history: Optional[List[Dict]] = None) -> Tuple[str, List[Dict]]:
        """Generate an answer using RAG"""
        # Check if we have documents
        if not self.document_manager.get_all_documents():
            return (
                "I don't have any economic data to answer your question. Please add some relevant documents first.",
                []
            )
        
        # Check if RAG chain is initialized
        if self.rag_chain is None:
            if not config.OPENAI_API_KEY:
                return "OpenAI API key is not set. Cannot generate response.", []
            else:
                return "Error initializing RAG components. Check logs for details.", []
        
        # Format chat history for the RAG chain
        formatted_history = []
        if chat_history:
            for msg in chat_history:
                if msg["role"] == "user":
                    formatted_history.append((msg["content"], ""))
                elif msg["role"] == "assistant" and len(formatted_history) > 0:
                    # Update the last item's response
                    last_query, _ = formatted_history[-1]
                    formatted_history[-1] = (last_query, msg["content"])
        
        # Use only the most recent chat history to save tokens
        recent_history = formatted_history[-3:] if len(formatted_history) > 3 else formatted_history
        
        try:
            # Use callback to track token usage
            with get_openai_callback() as cb:
                # Get response from RAG chain
                response = self.rag_chain.generate_response(question, recent_history)
                
                # Log token usage
                logger.info(f"Tokens used: {cb.total_tokens} (Prompt: {cb.prompt_tokens}, Completion: {cb.completion_tokens})")
            
            # Extract answer and source documents
            answer = response.get("answer", "I couldn't find an answer based on the available information.")
            source_docs = response.get("source_documents", [])
            
            # Extract source information from documents
            sources = []
            seen_doc_ids = set()
            
            for doc in source_docs:
                doc_id = doc.metadata.get("doc_id", "unknown")
                source = doc.metadata.get("source", "Unknown Source")
                
                # De-duplicate sources
                if doc_id not in seen_doc_ids:
                    seen_doc_ids.add(doc_id)
                    sources.append({
                        "id": doc_id,
                        "source": source
                    })
            
            return answer, sources
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
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