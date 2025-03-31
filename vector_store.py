# vector_store.py - Vector database for document storage and retrieval using Qdrant
import os
import shutil
import numpy as np
import logging
from typing import List, Dict, Any, Optional
import tiktoken
import torch
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

import config
from utils import generate_id, get_current_timestamp, save_json, load_json, count_tokens

# Import sentence-transformers for embeddings
from sentence_transformers import SentenceTransformer

class VectorStore:
    """Vector store for document embeddings and retrieval using Qdrant"""
    
    def __init__(self, force_reset: bool = False):
        """Initialize the vector store with Qdrant"""
        self.embedding_model_name = config.EMBEDDING_MODEL
        self.collection_name = "economic_documents"
        self.documents = []
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Initialize the embedding model
        logging.info(f"Loading embedding model: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        
        # Get embedding dimension
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        logging.info(f"Embedding dimension: {self.dimension}")
        
        # Initialize Qdrant client with more robust configuration
        self.qdrant_path = os.path.join(config.DATA_DIR, "qdrant_storage")
        
        # Optional force reset of the vector store
        if force_reset and os.path.exists(self.qdrant_path):
            logging.warning("Force resetting Qdrant storage...")
            try:
                shutil.rmtree(self.qdrant_path)
            except Exception as e:
                logging.error(f"Error removing Qdrant storage: {e}")
        
        # Ensure directory exists
        os.makedirs(self.qdrant_path, exist_ok=True)
        
        try:
            logging.info(f"Initializing Qdrant with local storage at: {self.qdrant_path}")
            self.client = QdrantClient(
                path=self.qdrant_path,
                force_disable_check_same_thread=True  # Add this to mitigate thread-related issues
            )
            
            # Create collection if it doesn't exist
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            if self.collection_name not in collection_names:
                logging.info(f"Creating new collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qdrant_models.VectorParams(
                        size=self.dimension,
                        distance=qdrant_models.Distance.COSINE
                    )
                )
            
        except Exception as e:
            logging.error(f"Error initializing Qdrant: {e}")
            logging.info("Attempting to resolve by resetting Qdrant storage...")
            
            # Attempt to reset storage if initialization fails
            try:
                shutil.rmtree(self.qdrant_path)
                os.makedirs(self.qdrant_path, exist_ok=True)
                self.client = QdrantClient(
                    path=self.qdrant_path,
                    force_disable_check_same_thread=True
                )
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qdrant_models.VectorParams(
                        size=self.dimension,
                        distance=qdrant_models.Distance.COSINE
                    )
                )
            except Exception as reset_error:
                logging.critical(f"Could not initialize or reset Qdrant: {reset_error}")
                raise RuntimeError("Unable to initialize vector store") from reset_error
        
        # Load existing documents if available
        self.load_data()
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Get vector embedding using Sentence-Transformers"""
        # Count tokens for monitoring
        token_count = count_tokens(text)
        logging.info(f"Getting embedding for {token_count} tokens")
        
        # Generate embedding using sentence-transformers
        with torch.no_grad():
            embedding = self.embedding_model.encode(text)
            
        # Ensure the embedding is the correct shape and type
        return np.array(embedding).astype(np.float32)
    
    def add_document(self, content: str, source: str, metadata: Optional[Dict] = None) -> str:
        """Add a document to the vector store"""
        # Generate document ID and timestamp
        doc_id = generate_id()
        date_added = get_current_timestamp()
        
        # Create document record
        doc = {
            "id": doc_id,
            "content": content,
            "source": source,
            "date_added": date_added,
            "metadata": metadata or {}
        }
        
        # Get embedding
        embedding = self.get_embedding(content)
        
        # Add to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                qdrant_models.PointStruct(
                    id=doc_id,
                    vector=embedding.tolist(),
                    payload={
                        "content": content,
                        "source": source,
                        "date_added": date_added,
                        **(metadata or {})
                    }
                )
            ]
        )
        
        # Store in our documents list
        self.documents.append(doc)
        
        # Save updated documents to JSON
        self.save_data()
        
        return doc_id
    
    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """Search for similar documents"""
        # Use configured default if not specified
        if top_k is None:
            top_k = config.MAX_SEARCH_RESULTS
            
        # Handle empty collection case
        if len(self.documents) == 0:
            return []
            
        # Get query embedding
        query_embedding = self.get_embedding(query)
        
        # Search the collection
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),
            limit=top_k
        )
        
        # Format results
        results = []
        for scored_point in search_result:
            doc_id = scored_point.id
            score = scored_point.score
            payload = scored_point.payload
            
            results.append({
                "id": doc_id,
                "content": payload["content"],
                "source": payload["source"],
                "score": float(score),
            })
        
        return results
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Get a document by ID"""
        for doc in self.documents:
            if doc["id"] == doc_id:
                return doc
        return None
    
    def save_data(self) -> None:
        """Save documents metadata to disk"""
        # Save the documents to JSON
        save_json(self.documents, str(config.DOCUMENTS_FILE))
        logging.info(f"Saved {len(self.documents)} document metadata to disk")
    
    def load_data(self) -> None:
        """Load documents metadata from disk"""
        try:
            # Load documents if exists
            documents = load_json(str(config.DOCUMENTS_FILE))
            if documents:
                self.documents = documents
                logging.info(f"Loaded {len(self.documents)} document metadata from disk")
                
                # Verify documents exist in Qdrant
                doc_count = self.client.count(
                    collection_name=self.collection_name
                ).count
                
                logging.info(f"Qdrant contains {doc_count} vectors")
                
                if doc_count != len(self.documents):
                    logging.warning(f"Document count mismatch: {len(self.documents)} in JSON vs {doc_count} in Qdrant")
                
        except Exception as e:
            logging.error(f"Error loading data: {e}")
            # Initialize with empty data
            self.documents = []
    
    def bulk_add_documents(self, documents: List[Dict]) -> List[str]:
        """Add multiple documents at once (more efficient)"""
        if not documents:
            return []
            
        doc_ids = []
        points = []
        
        for doc in documents:
            # Generate document ID and timestamp
            doc_id = generate_id()
            date_added = get_current_timestamp()
            
            # Store document info
            new_doc = {
                "id": doc_id,
                "content": doc["content"],
                "source": doc["source"],
                "date_added": date_added,
                "metadata": doc.get("metadata", {})
            }
            
            # Get embedding
            embedding = self.get_embedding(doc["content"])
            
            # Add to batch
            points.append(
                qdrant_models.PointStruct(
                    id=doc_id,
                    vector=embedding.tolist(),
                    payload={
                        "content": doc["content"],
                        "source": doc["source"],
                        "date_added": date_added,
                        **(doc.get("metadata", {}))
                    }
                )
            )
            
            # Add to our documents list
            self.documents.append(new_doc)
            doc_ids.append(doc_id)
        
        # Batch add to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        # Save updated documents to JSON
        self.save_data()
        
        return doc_ids
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID"""
        # Find document index
        doc_index = None
        for i, doc in enumerate(self.documents):
            if doc["id"] == doc_id:
                doc_index = i
                break
                
        if doc_index is None:
            return False
        
        # Delete from Qdrant
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=qdrant_models.PointIdsList(
                    points=[doc_id]
                )
            )
        except Exception as e:
            logging.error(f"Error deleting document from Qdrant: {e}")
            return False
            
        # Remove document from list
        self.documents.pop(doc_index)
        
        # Save updated documents
        self.save_data()
        
        return True