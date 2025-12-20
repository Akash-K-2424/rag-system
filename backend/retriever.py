"""
Retrieval and re-ranking module for RAG system.
Implements vector search and MMR (Maximal Marginal Relevance) re-ranking.
Domain: Academic & Research Documents (AI & ML PDFs)
"""

from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings


class VectorRetriever:
    """
    Handles vector similarity search and re-ranking.
    Uses ChromaDB for vector storage and SentenceTransformers for embeddings.
    """
    
    def __init__(self, db_path: str = "./chroma_db", embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize retriever with embedding model and vector database.
        
        Args:
            db_path: Path to ChromaDB storage
            embedding_model: HuggingFace model name for embeddings
        """
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Use EphemeralClient (in-memory) to avoid blocking issues on Apple Silicon
        # This is faster and doesn't require disk persistence
        try:
            self.client = chromadb.EphemeralClient()
            print("✓ Using ChromaDB EphemeralClient (in-memory)")
        except Exception as e:
            print(f"Warning: ChromaDB init issue: {e}")
            self.client = chromadb.Client()
        
        # Get or create collection for documents
        self.collection = self.client.get_or_create_collection(
            name="academic_documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        try:
            self.client.delete_collection("academic_documents")
            self.collection = self.client.get_or_create_collection(
                name="academic_documents",
                metadata={"hnsw:space": "cosine"}
            )
            print("✓ Collection cleared successfully")
        except Exception as e:
            print(f"Warning: Could not clear collection: {e}")
    
    def add_chunks(self, chunks: List) -> None:
        """
        Add document chunks to vector database.
        
        Args:
            chunks: List of DocumentChunk objects from ingest.py
        """
        if not chunks:
            return
        
        # Extract texts and metadata
        texts = [chunk.text for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        ids = [chunk.chunk_id for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        
        # Add to ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            documents=texts
        )
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, dict, float]]:
        """
        Retrieve top-k most similar chunks using vector similarity.
        
        Args:
            query: User question
            top_k: Number of results to retrieve
            
        Returns:
            List of (text, metadata, similarity_score) tuples
        """
        # Embed query
        query_embedding = self.embedding_model.encode(query, convert_to_numpy=True)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        
        # Format results
        retrieved = []
        if results and results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i]
                # Convert distance to similarity (cosine distance to similarity)
                similarity = 1 - distance
                retrieved.append((doc, metadata, similarity))
        
        return retrieved
    
    def rerank_mmr(self, query: str, retrieved_chunks: List[Tuple[str, dict, float]], 
                   lambda_param: float = 0.5) -> List[Tuple[str, dict, float]]:
        """
        Re-rank retrieved chunks using Maximal Marginal Relevance (MMR).
        Balances relevance to query with diversity among results.
        
        Args:
            query: User question
            retrieved_chunks: List of (text, metadata, similarity) from search()
            lambda_param: Balance between relevance (1.0) and diversity (0.0)
            
        Returns:
            Re-ranked list of (text, metadata, similarity) tuples
        """
        if len(retrieved_chunks) <= 1:
            return retrieved_chunks
        
        # Embed query and all chunks
        query_embedding = self.embedding_model.encode(query, convert_to_numpy=True)
        chunk_texts = [chunk[0] for chunk in retrieved_chunks]
        chunk_embeddings = self.embedding_model.encode(chunk_texts, convert_to_numpy=True)
        
        # Calculate query relevance scores
        query_scores = np.dot(chunk_embeddings, query_embedding) / (
            np.linalg.norm(chunk_embeddings, axis=1) * np.linalg.norm(query_embedding) + 1e-8
        )
        
        # MMR selection
        selected_indices = []
        remaining_indices = list(range(len(retrieved_chunks)))
        
        # Select first chunk (highest relevance)
        first_idx = np.argmax(query_scores)
        selected_indices.append(first_idx)
        remaining_indices.remove(first_idx)
        
        # Iteratively select chunks that maximize MMR
        while remaining_indices:
            mmr_scores = []
            
            for idx in remaining_indices:
                # Relevance to query
                relevance = query_scores[idx]
                
                # Diversity: minimum similarity to already selected chunks
                diversity = 0
                for selected_idx in selected_indices:
                    similarity = np.dot(chunk_embeddings[idx], chunk_embeddings[selected_idx]) / (
                        np.linalg.norm(chunk_embeddings[idx]) * np.linalg.norm(chunk_embeddings[selected_idx]) + 1e-8
                    )
                    diversity = max(diversity, similarity)
                
                # MMR score
                mmr = lambda_param * relevance - (1 - lambda_param) * diversity
                mmr_scores.append(mmr)
            
            # Select chunk with highest MMR
            best_idx = remaining_indices[np.argmax(mmr_scores)]
            selected_indices.append(best_idx)
            remaining_indices.remove(best_idx)
        
        # Return re-ranked chunks
        return [retrieved_chunks[i] for i in selected_indices]
    
    def retrieve_and_rerank(self, query: str, top_k: int = 5) -> List[Tuple[str, dict, float]]:
        """
        Complete retrieval pipeline: search → re-rank.
        
        Args:
            query: User question
            top_k: Number of results to retrieve
            
        Returns:
            Re-ranked list of (text, metadata, similarity) tuples
        """
        # Step 1: Vector similarity search
        retrieved = self.search(query, top_k=top_k)
        
        # Step 2: MMR re-ranking for diversity
        reranked = self.rerank_mmr(query, retrieved)
        
        return reranked
