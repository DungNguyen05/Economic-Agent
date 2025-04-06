# core/chatbot.py - Enhanced Chatbot implementation with general capability

import logging
from typing import List, Dict, Tuple, Optional
import tiktoken
from langchain_community.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

import config
from rag.retriever import AdvancedRetriever
from rag.chains import RAGChainManager

logger = logging.getLogger(__name__)

class Chatbot:
    """Enhanced economic chatbot with RAG and general capability"""
    
    def __init__(self, document_manager, vector_store):
        """Initialize the chatbot with necessary components"""
        self.document_manager = document_manager
        self.vector_store = vector_store
        self.model_name = config.OPENAI_CHAT_MODEL
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.session_histories = {}  # Store chat history by session ID
        
        # Initialize OpenAI LLM
        if not config.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set. OpenAI chat completion will not work.")
            self.llm = None
            self.rag_chain = None
            self.general_chain = None
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
                
                # Set up RAG chain manager for document-based answers
                self.rag_chain = RAGChainManager(
                    self.llm,
                    advanced_retriever.get_retriever(),
                    query_expansion_chain
                )
                
                # Create a general-purpose chain for non-document-specific answers
                general_template = """
                You are a helpful assistant that can answer a wide range of questions.
                Use your general knowledge to provide a helpful response.
                
                Chat History:
                {chat_history}
                
                Question: {question}
                
                Answer:
                """
                
                general_prompt = PromptTemplate(
                    input_variables=["chat_history", "question"],
                    template=general_template
                )
                
                self.general_chain = LLMChain(
                    llm=self.llm,
                    prompt=general_prompt
                )
                
                logger.info(f"Chatbot initialized with {self.model_name}")
                
            except Exception as e:
                logger.error(f"Error initializing chatbot: {e}")
                self.llm = None
                self.rag_chain = None
                self.general_chain = None
    
    def get_session_history(self, session_id: str = "default") -> List[Tuple[str, str]]:
        """Get chat history for a session"""
        if session_id not in self.session_histories:
            self.session_histories[session_id] = []
        return self.session_histories[session_id]
    
    def update_session_history(self, session_id: str, user_message: str, ai_message: str) -> None:
        """Update chat history for a session"""
        if session_id not in self.session_histories:
            self.session_histories[session_id] = []
        
        # Add message pair to history
        self.session_histories[session_id].append((user_message, ai_message))
        
        # Keep only the last 5 interactions to manage token usage
        if len(self.session_histories[session_id]) > 5:
            self.session_histories[session_id] = self.session_histories[session_id][-5:]
    
    def generate_answer(self, 
                        question: str, 
                        chat_history: Optional[List[Dict]] = None, 
                        session_id: str = "default") -> Tuple[str, List[Dict]]:
        """Generate an answer using either RAG or general knowledge"""
        # Format incoming chat history
        formatted_history = []
        if chat_history:
            for msg in chat_history:
                if msg["role"] == "user":
                    formatted_history.append((msg["content"], ""))
                elif msg["role"] == "assistant" and len(formatted_history) > 0:
                    # Update the last item's response
                    last_query, _ = formatted_history[-1]
                    formatted_history[-1] = (last_query, msg["content"])
        
        # Get current session history and merge with formatted history
        session_history = self.get_session_history(session_id)
        merged_history = session_history + [pair for pair in formatted_history if pair not in session_history]
        
        # Use only the most recent chat history to save tokens
        recent_history = merged_history[-5:] if len(merged_history) > 5 else merged_history
        
        try:
            # First try to answer with documents if available
            have_documents = len(self.document_manager.get_all_documents()) > 0
            
            if have_documents:
                # Use callback to track token usage
                with get_openai_callback() as cb:
                    # Get response from RAG chain
                    response = self.rag_chain.generate_response(question, recent_history)
                    
                    # Log token usage
                    logger.info(f"RAG tokens used: {cb.total_tokens} (Prompt: {cb.prompt_tokens}, Completion: {cb.completion_tokens})")
                
                # Extract answer and source documents
                answer = response.get("answer", "")
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
                
                # If we got a good answer with sources, use it
                if sources and "I don't have enough information" not in answer and "don't have specific information" not in answer:
                    # Update session history with this interaction
                    self.update_session_history(session_id, question, answer)
                    return answer, sources
            
            # If no documents or RAG didn't provide a good answer, use general knowledge
            if self.general_chain:
                # Format history for general chain
                history_text = ""
                for i, (q, a) in enumerate(recent_history):
                    history_text += f"User: {q}\nAssistant: {a}\n\n"
                
                # Use callback to track token usage
                with get_openai_callback() as cb:
                    general_response = self.general_chain.run(
                        chat_history=history_text,
                        question=question
                    )
                    
                    # Log token usage
                    logger.info(f"General tokens used: {cb.total_tokens} (Prompt: {cb.prompt_tokens}, Completion: {cb.completion_tokens})")
                
                # Update session history with this interaction
                self.update_session_history(session_id, question, general_response)
                
                return general_response, []
            
            # Fallback message if both methods fail
            fallback_message = "I'm sorry, I don't have enough information to answer that question."
            if not config.OPENAI_API_KEY:
                fallback_message = "OpenAI API key is not set. Cannot generate response."
            
            return fallback_message, []
            
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