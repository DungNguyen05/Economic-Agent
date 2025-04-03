# rag/retriever.py - Advanced retrieval strategies
import logging
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

import config

logger = logging.getLogger(__name__)

class AdvancedRetriever:
    """Implements advanced retrieval strategies for RAG"""
    
    def __init__(self, llm, base_retriever):
        """Initialize the advanced retriever with components"""
        self.llm = llm
        self.base_retriever = base_retriever
        
        # Set up different retrieval strategies
        if config.USE_QUERY_EXPANSION and config.USE_RERANKING:
            logger.info("Initializing retriever with query expansion and reranking")
            self.retriever = self._create_full_retriever()
        elif config.USE_QUERY_EXPANSION:
            logger.info("Initializing retriever with query expansion only")
            self.retriever = self._create_query_expansion_retriever()
        elif config.USE_RERANKING:
            logger.info("Initializing retriever with reranking only")
            self.retriever = self._create_reranking_retriever()
        else:
            logger.info("Initializing base retriever without enhancements")
            self.retriever = base_retriever
    
    def _create_query_expansion_chain(self):
        """Create a query expansion chain for better retrieval"""
        query_expansion_template = """
        You are an AI assistant helping to generate better search queries for an economic knowledge base.
        Given the user's question, create an improved search query that will help find the most relevant information.
        Make the query more specific, include synonyms, and focus on the key economic concepts.
        
        Original question: {question}
        
        Improved search query:
        """
        
        query_expansion_prompt = PromptTemplate(
            input_variables=["question"],
            template=query_expansion_template
        )
        
        return LLMChain(
            llm=self.llm,
            prompt=query_expansion_prompt
        )
    
    def _create_reranking_retriever(self):
        """Create a retriever with context compression for reranking"""
        compressor = LLMChainExtractor.from_llm(self.llm)
        
        return ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=self.base_retriever
        )
    
    def _create_query_expansion_retriever(self):
        """Create a retriever with query expansion"""
        # Base retriever is used, but the query will be expanded
        # The expansion happens at the chain level, not the retriever level
        return self.base_retriever
    
    def _create_full_retriever(self):
        """Create a retriever with both query expansion and reranking"""
        # Query expansion happens at the chain level
        # Here we just add the reranking/compression
        compressor = LLMChainExtractor.from_llm(self.llm)
        
        return ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=self.base_retriever
        )
    
    def get_retriever(self):
        """Return the configured retriever"""
        return self.retriever
    
    def get_query_expansion_chain(self):
        """Return the query expansion chain if enabled, or None"""
        if config.USE_QUERY_EXPANSION:
            return self._create_query_expansion_chain()
        return None