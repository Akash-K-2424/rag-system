"""
Kiro Agent Orchestration Layer for RAG System.
Coordinates the complete RAG pipeline with explicit tool calls.
Domain: Academic & Research Documents (AI & ML PDFs)
"""

import os
from typing import List, Dict, Any
from ingest import ingest_document, DocumentChunk
from retriever import VectorRetriever
from generator import AnswerGenerator
from memory import ConversationMemory
from schemas import ChatResponse, Citation


class RAGAgent:
    """
    Orchestrates the complete RAG pipeline with conversation memory:
    Query → Memory → Retrieval → Re-ranking → Generation → Citations
    """
    
    def __init__(self):
        """Initialize RAG agent with all components including memory."""
        self.retriever = VectorRetriever(
            db_path=os.getenv("CHROMA_DB_PATH", "./chroma_db"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "tfidf")
        )
        self.generator = AnswerGenerator(
            confidence_threshold=float(os.getenv("CONFIDENCE_THRESHOLD", "0.2"))
        )
        self.memory = ConversationMemory(
            max_short_term=10,
            max_long_term=100,
            storage_path="./conversation_history.json"
        )
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "400"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "80"))
        self.top_k = int(os.getenv("TOP_K_RETRIEVAL", "5"))
        self.default_conversation_id = "default"
    
    def tool_ingest_documents(self, file_path: str, document_name: str) -> Dict[str, Any]:
        """
        TOOL 1: Ingest and chunk documents.
        
        Pipeline step: Document Ingestion
        - Extract text from PDF
        - Split into overlapping chunks (400 tokens, 80-token overlap)
        - Create metadata (document_name, page_number, chunk_id)
        
        Args:
            file_path: Path to PDF file
            document_name: Name to store in metadata
            
        Returns:
            Dictionary with ingestion results
        """
        print(f"[AGENT] Tool: ingest_documents({document_name})")
        
        try:
            chunks = ingest_document(
                file_path=file_path,
                document_name=document_name,
                chunk_size=self.chunk_size,
                overlap=self.chunk_overlap
            )
            
            total_tokens = sum(chunk.token_count for chunk in chunks)
            
            return {
                "status": "success",
                "document_name": document_name,
                "chunks_created": len(chunks),
                "total_tokens": total_tokens,
                "chunks": chunks
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def tool_embed_chunks(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """
        TOOL 2: Generate embeddings and store in vector database.
        
        Pipeline step: Embedding Generation & Storage
        - Convert chunks to embeddings using SentenceTransformers
        - Store in ChromaDB with metadata
        
        Args:
            chunks: List of DocumentChunk objects
            
        Returns:
            Dictionary with embedding results
        """
        print(f"[AGENT] Tool: embed_chunks({len(chunks)} chunks)")
        
        try:
            self.retriever.add_chunks(chunks)
            
            return {
                "status": "success",
                "chunks_embedded": len(chunks),
                "vector_db": "ChromaDB"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def tool_vector_search(self, query: str) -> Dict[str, Any]:
        """
        TOOL 3: Retrieve top-k similar chunks using vector similarity.
        
        Pipeline step: Vector Database Search
        - Embed user query
        - Search ChromaDB for top-5 similar chunks
        - Return with similarity scores
        
        Args:
            query: User question
            
        Returns:
            Dictionary with retrieved chunks
        """
        print(f"[AGENT] Tool: vector_search(query='{query[:50]}...')")
        
        try:
            retrieved = self.retriever.search(query, top_k=self.top_k)
            
            return {
                "status": "success",
                "query": query,
                "retrieved_count": len(retrieved),
                "chunks": retrieved
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def tool_rerank_context(self, query: str, retrieved_chunks: List) -> Dict[str, Any]:
        """
        TOOL 4: Re-rank retrieved chunks using MMR (Maximal Marginal Relevance).
        
        Pipeline step: Context Re-ranking
        - Apply MMR algorithm to balance relevance and diversity
        - Reduce redundancy in retrieved context
        
        Args:
            query: User question
            retrieved_chunks: List of (text, metadata, similarity) tuples
            
        Returns:
            Dictionary with re-ranked chunks
        """
        print(f"[AGENT] Tool: rerank_context({len(retrieved_chunks)} chunks)")
        
        try:
            reranked = self.retriever.rerank_mmr(query, retrieved_chunks)
            
            return {
                "status": "success",
                "reranked_count": len(reranked),
                "chunks": reranked
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def tool_generate_answer_with_citations(self, query: str, reranked_chunks: List,
                                            conversation_history: str = "") -> Dict[str, Any]:
        """
        TOOL 5: Generate answer using LLM with conversation context.
        
        Args:
            query: User question
            reranked_chunks: List of (text, metadata, similarity) tuples
            conversation_history: Previous conversation context
            
        Returns:
            Dictionary with answer and citations
        """
        print(f"[AGENT] Tool: generate_answer_with_citations()")
        
        try:
            result = self.generator.generate_answer(query, reranked_chunks, conversation_history)
            
            return {
                "status": "success",
                "answer": result["answer"],
                "citations": result["citations"],
                "confidence": result["confidence"],
                "retrieved_chunks": result["retrieved_chunks"]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def process_query(self, query: str, conversation_id: str = None) -> ChatResponse:
        """
        ORCHESTRATION: Execute complete RAG pipeline with memory.
        
        Pipeline:
        1. Get conversation history from memory
        2. Vector Database Search (top-5)
        3. Context Re-ranking (MMR)
        4. Answer Generation with history context
        5. Store messages in memory
        
        Args:
            query: User question
            conversation_id: Optional conversation ID for memory
            
        Returns:
            ChatResponse with answer and citations
        """
        conv_id = conversation_id or self.default_conversation_id
        print(f"\n[AGENT] Processing query: '{query}' (conversation: {conv_id})")
        
        # Step 1: Get conversation history
        conversation_history = self.memory.get_conversation_summary(conv_id)
        if conversation_history:
            print(f"[AGENT] Found conversation history ({len(conversation_history)} chars)")
        
        # Store user message in memory
        self.memory.add_message(conv_id, "user", query)
        
        # Step 2: Vector search
        search_result = self.tool_vector_search(query)
        if search_result["status"] != "success":
            error_response = ChatResponse(
                answer="Error retrieving documents",
                citations=[],
                confidence=0.0,
                retrieved_chunks=0
            )
            self.memory.add_message(conv_id, "assistant", error_response.answer)
            return error_response
        
        retrieved_chunks = search_result["chunks"]
        
        # Step 3: Re-rank context
        rerank_result = self.tool_rerank_context(query, retrieved_chunks)
        reranked_chunks = rerank_result.get("chunks", retrieved_chunks)
        
        # Step 4: Generate answer with conversation history
        gen_result = self.tool_generate_answer_with_citations(
            query, reranked_chunks, conversation_history
        )
        
        if gen_result["status"] != "success":
            error_response = ChatResponse(
                answer="Error generating answer",
                citations=[],
                confidence=0.0,
                retrieved_chunks=len(reranked_chunks)
            )
            self.memory.add_message(conv_id, "assistant", error_response.answer)
            return error_response
        
        # Build response
        response = ChatResponse(
            answer=gen_result["answer"],
            citations=gen_result["citations"],
            confidence=gen_result["confidence"],
            retrieved_chunks=gen_result["retrieved_chunks"]
        )
        
        # Store assistant response in memory
        self.memory.add_message(conv_id, "assistant", response.answer, {
            "confidence": response.confidence,
            "citations": len(response.citations)
        })
        
        print(f"[AGENT] Pipeline complete. Confidence: {response.confidence:.2f}")
        return response
    
    def ingest_and_store(self, file_path: str, document_name: str, clear_existing: bool = True) -> Dict[str, Any]:
        """
        ORCHESTRATION: Complete ingestion pipeline.
        
        Args:
            file_path: Path to PDF file
            document_name: Name to store in metadata
            clear_existing: Whether to clear existing documents before adding new ones
            
        Returns:
            Dictionary with ingestion results
        """
        print(f"\n[AGENT] Starting ingestion pipeline for: {document_name}")
        
        # Clear existing documents if requested
        if clear_existing:
            print("[AGENT] Clearing existing documents...")
            self.retriever.clear_collection()
        
        # Step 1: Ingest documents
        ingest_result = self.tool_ingest_documents(file_path, document_name)
        if ingest_result["status"] != "success":
            return ingest_result
        
        chunks = ingest_result["chunks"]
        
        # Step 2: Embed and store
        embed_result = self.tool_embed_chunks(chunks)
        if embed_result["status"] != "success":
            return embed_result
        
        print(f"[AGENT] Ingestion complete. Chunks: {ingest_result['chunks_created']}")
        
        return {
            "status": "success",
            "document_name": document_name,
            "chunks_created": ingest_result["chunks_created"],
            "total_tokens": ingest_result["total_tokens"]
        }
