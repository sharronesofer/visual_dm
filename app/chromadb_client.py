"""
ChromaDB client with comprehensive logging and monitoring.
"""

import logging
import time
from typing import Optional, Dict, Any, List
import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.api.types import EmbeddingFunction

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChromaDBClient:
    """ChromaDB client with enhanced logging and monitoring."""
    
    def __init__(self, path: str = "./chroma_db"):
        """Initialize ChromaDB client with logging."""
        self.start_time = time.time()
        logger.info(f"Initializing ChromaDB client at path: {path}")
        
        try:
            self.client = chromadb.PersistentClient(path=path)
            logger.info("ChromaDB client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {str(e)}")
            raise
        
        self.short_term_collection = self._initialize_collection("short_term_memory")
        self.long_term_collection = self._initialize_collection("long_term_memory")
        
        logger.info(f"ChromaDB setup completed in {time.time() - self.start_time:.2f} seconds")
    
    def _initialize_collection(self, name: str) -> Optional[Collection]:
        """Initialize a collection with error handling and logging."""
        logger.info(f"Initializing collection: {name}")
        
        try:
            collection = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Collection '{name}' initialized successfully")
            return collection
        except Exception as e:
            logger.warning(f"Error initializing collection '{name}': {str(e)}")
            logger.info(f"Attempting to recreate collection '{name}'")
            
            try:
                self.client.delete_collection(name)
                collection = self.client.create_collection(
                    name=name,
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info(f"Collection '{name}' recreated successfully")
                return collection
            except Exception as e:
                logger.error(f"Failed to recreate collection '{name}': {str(e)}")
                return None
    
    def add_documents(self, collection: Collection, documents: List[str], 
                     metadatas: Optional[List[Dict[str, Any]]] = None,
                     ids: Optional[List[str]] = None) -> bool:
        """Add documents to a collection with logging."""
        try:
            start_time = time.time()
            logger.info(f"Adding {len(documents)} documents to collection '{collection.name}'")
            
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            duration = time.time() - start_time
            logger.info(f"Successfully added documents in {duration:.2f} seconds")
            return True
        except Exception as e:
            logger.error(f"Failed to add documents to collection '{collection.name}': {str(e)}")
            return False
    
    def query(self, collection: Collection, query_texts: List[str],
              n_results: int = 10) -> Optional[Dict[str, Any]]:
        """Query a collection with logging."""
        try:
            start_time = time.time()
            logger.info(f"Querying collection '{collection.name}' with {len(query_texts)} queries")
            
            results = collection.query(
                query_texts=query_texts,
                n_results=n_results
            )
            
            duration = time.time() - start_time
            logger.info(f"Query completed in {duration:.2f} seconds")
            return results
        except Exception as e:
            logger.error(f"Failed to query collection '{collection.name}': {str(e)}")
            return None
    
    def get_collection_stats(self, collection: Collection) -> Dict[str, Any]:
        """Get collection statistics with logging."""
        try:
            stats = {
                "name": collection.name,
                "count": collection.count(),
                "metadata": collection.metadata
            }
            logger.info(f"Retrieved stats for collection '{collection.name}': {stats}")
            return stats
        except Exception as e:
            logger.error(f"Failed to get stats for collection '{collection.name}': {str(e)}")
            return {}

# Initialize the client
client = ChromaDBClient()

# Export collections for direct import
short_term_collection = client.short_term_collection
long_term_collection = client.long_term_collection
