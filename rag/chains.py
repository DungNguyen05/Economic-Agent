# rag/chains.py - LLM chains for RAG
import logging
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

import config

logger = logging.getLogger(__name__)

class RAGChainManager:
    """Manages RAG chains for conversational retrieval"""
    
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
        """Create the question answering chain"""
        qa_template = """
        You are an economic assistant that helps with questions about the economy.
        Use the following pieces of retrieved context to answer the question. If you don't know the 
        answer based on the context, say you don't have enough information, but still try to be helpful.
        
        Use the sources to provide an informed response. Cite sources by their numbers [1], [2], etc. when you use information from them.
        
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
        """Create the conversational retrieval chain"""
        return ConversationalRetrievalChain(
            retriever=self.retriever,
            combine_docs_chain=self.qa_chain,
            question_generator=self.query_expansion_chain,
            return_source_documents=True,
            verbose=config.DEBUG
        )
    
    def generate_response(self, question, chat_history=None):
        """Generate a response using the conversational retrieval chain"""
        if chat_history is None:
            chat_history = []
            
        try:
            response = self.conversation_chain({
                "question": question,
                "chat_history": chat_history
            })
            
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise