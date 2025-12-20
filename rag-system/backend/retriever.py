"""
Retrieval and re-ranking module for RAG system.
Uses TF-IDF for fast, lightweight text similarity (no heavy ML models).
Domain: Academic & Research Documents (AI & ML PDFs)
"""

from typing import List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class VectorRetriever:
    """
    Handles text similarity search and re-ranking using TF-IDF.
    Lightweight alternative to embedding models - works great on Apple Silicon.
    """
    
    def __init__(self, db_path: str = "./chroma_db", embedding_model: str = "tfidf"):
        """
        Initialize retriever with TF-IDF vectorizer.
        
        Args:
            db_path: Not used (kept for API compatibility)
            embedding_model: Not used (kept for API compatibility)
        """
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.chunks = []  # Store chunks in memory
        self.chunk_vectors = None
        self.is_fitted = False
        print("✓ Vector store ready")
    
    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        self.chunks = []
        self.chunk_vectors = None
        self.is_fitted = False
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        print("✓ Collection cleared successfully")
    
    def add_chunks(self, chunks: List) -> None:
        """
        Add document chunks to the store.
        
        Args:
            chunks: List of DocumentChunk objects from ingest.py
        """
        if not chunks:
            return
        
        # Store chunks
        for chunk in chunks:
            self.chunks.append({
                'text': chunk.text,
                'metadata': chunk.metadata,
                'chunk_id': chunk.chunk_id
            })
        
        # Rebuild TF-IDF vectors
        texts = [c['text'] for c in self.chunks]
        self.chunk_vectors = self.vectorizer.fit_transform(texts)
        self.is_fitted = True
        print(f"✓ Added {len(chunks)} chunks, total: {len(self.chunks)}")
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, dict, float]]:
        """
        Retrieve top-k most similar chunks using TF-IDF similarity.
        
        Args:
            query: User question
            top_k: Number of results to retrieve
            
        Returns:
            List of (text, metadata, similarity_score) tuples
        """
        if not self.is_fitted or len(self.chunks) == 0:
            return []
        
        # Transform query using fitted vectorizer
        query_vector = self.vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.chunk_vectors)[0]
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Format results
        retrieved = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only include if there's some similarity
                chunk = self.chunks[idx]
                retrieved.append((chunk['text'], chunk['metadata'], float(similarities[idx])))
        
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
        
        # Get texts
        chunk_texts = [chunk[0] for chunk in retrieved_chunks]
        
        # Create TF-IDF vectors for chunks and query
        all_texts = [query] + chunk_texts
        tfidf_matrix = TfidfVectorizer(stop_words='english').fit_transform(all_texts)
        
        query_vector = tfidf_matrix[0:1]
        chunk_vectors = tfidf_matrix[1:]
        
        # Calculate query relevance scores
        query_scores = cosine_similarity(chunk_vectors, query_vector).flatten()
        
        # Calculate chunk-to-chunk similarities
        chunk_similarities = cosine_similarity(chunk_vectors)
        
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
                
                # Diversity: max similarity to already selected chunks
                diversity = max(chunk_similarities[idx][sel_idx] for sel_idx in selected_indices)
                
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
        # Step 1: TF-IDF similarity search
        retrieved = self.search(query, top_k=top_k)
        
        # Step 2: MMR re-ranking for diversity
        reranked = self.rerank_mmr(query, retrieved)
        
        return reranked
