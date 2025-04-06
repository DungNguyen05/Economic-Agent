# rag/chains.py - Enhanced LLM chains for RAG with better context handling
import logging
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate 

import config

logger = logging.getLogger(__name__)

class RAGChainManager:
    """Manages RAG chains for conversational retrieval with improved context handling"""
    
    def __init__(self, llm, retriever, query_expansion_chain=None):
        """Initialize the RAG chain manager"""
        self.llm = llm
        self.retriever = retriever
        self.query_expansion_chain = query_expansion_chain
        
        # Create the QA chain
        self.qa_chain = self._create_qa_chain()
        
        # Create the final conversational retrieval chain
        self.conversation_chain = self._create_conversation_chain()
        
        logger.info("RAG chains initialized successfully")
    
    def _create_qa_chain(self):
        """Create an enhanced question answering chain with better prompting"""
        qa_template = """
        You are a helpful assistant that can answer a wide range of questions, with special knowledge about economics.
        
        Use the following pieces of retrieved context to answer the question. The context contains economic information from various sources.
        If you don't find enough information in the context, feel free to use your general knowledge to provide a helpful response.
        
        When using information from the context, cite sources by their numbers [1], [2], etc. If using general knowledge, there's no need to cite.
        
        Context:
        {context}
        
        Chat History:
        {chat_history}
        
        Question: {question}
        
        Answer:
        """
        
        qa_prompt = PromptTemplate(
            input_variables=["context", "chat_history", "question"],
            template=qa_template
        )
        
        return load_qa_chain(
            llm=self.llm,
            chain_type="stuff",
            prompt=qa_prompt
        )
    
    def _create_conversation_chain(self):
        """Create an improved conversational retrieval chain"""
        return ConversationalRetrievalChain(
            retriever=self.retriever,
            combine_docs_chain=self.qa_chain,
            question_generator=self.query_expansion_chain,
            return_source_documents=True,
            verbose=config.DEBUG,
            # Increase max token limit for context to allow more flexible responses
            max_tokens_limit=config.MAX_CONTEXT_LENGTH
        )
    
    def _format_chat_history(self, history):
        """Format chat history pairs into a readable string for context"""
        if not history:
            return ""
            
        formatted_history = ""
        for i, (question, answer) in enumerate(history):
            if question and answer:
                formatted_history += f"User: {question}\nAssistant: {answer}\n\n"
            elif question:
                formatted_history += f"User: {question}\n\n"
                
        return formatted_history.strip()
    
    def generate_response(self, question, chat_history=None):
        """Generate a response using the conversational retrieval chain with improved context handling"""
        if chat_history is None:
            chat_history = []
            
        try:
            # Prepare chat history for the chain
            formatted_history = self._format_chat_history(chat_history)
            
            # Get response from conversation chain
            response = self.conversation_chain({
                "question": question,
                "chat_history": formatted_history
            })
            
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise