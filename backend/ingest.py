"""
Document ingestion pipeline for RAG system.
Handles PDF parsing, chunking, and metadata extraction.
Domain: Academic & Research Documents (AI & ML PDFs)
"""

import os
from typing import List, Tuple
from PyPDF2 import PdfReader
import re


class DocumentChunk:
    """Represents a single chunk of a document."""
    
    def __init__(self, chunk_id: str, text: str, document_name: str, page_number: int, token_count: int):
        self.chunk_id = chunk_id
        self.text = text
        self.document_name = document_name
        self.page_number = page_number
        self.token_count = token_count
        self.metadata = {
            "document_name": document_name,
            "page_number": page_number,
            "chunk_id": chunk_id,
            "token_count": token_count
        }


def estimate_tokens(text: str) -> int:
    """
    Estimate token count using simple word-based heuristic.
    Approximation: 1 token ≈ 1.3 words (OpenAI standard)
    """
    words = len(text.split())
    return max(1, int(words / 1.3))


def extract_text_from_pdf(file_path: str) -> Tuple[str, int]:
    """
    Extract text from PDF file with page tracking.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Tuple of (full_text, total_pages)
    """
    try:
        reader = PdfReader(file_path)
        full_text = ""
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            # Add page marker for tracking
            full_text += f"\n[PAGE {page_num + 1}]\n{text}\n"
        
        return full_text, len(reader.pages)
    except Exception as e:
        raise ValueError(f"Failed to extract PDF: {str(e)}")


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> List[str]:
    """
    Split text into overlapping chunks based on token count.
    
    Args:
        text: Full document text
        chunk_size: Target tokens per chunk
        overlap: Overlap tokens between chunks
        
    Returns:
        List of text chunks
    """
    # Split by sentences for better semantic boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    current_tokens = 0
    
    for sentence in sentences:
        sentence_tokens = estimate_tokens(sentence)
        
        # If adding this sentence exceeds chunk_size, save current chunk
        if current_tokens + sentence_tokens > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Start new chunk with overlap
            current_chunk = current_chunk[-int(chunk_size * overlap / 100):] + " " + sentence
            current_tokens = estimate_tokens(current_chunk)
        else:
            current_chunk += " " + sentence
            current_tokens += sentence_tokens
    
    # Add final chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


def extract_page_number(chunk_text: str) -> int:
    """
    Extract page number from chunk text (marked during PDF extraction).
    
    Args:
        chunk_text: Text chunk with page markers
        
    Returns:
        Page number (1-indexed)
    """
    match = re.search(r'\[PAGE (\d+)\]', chunk_text)
    if match:
        return int(match.group(1))
    return 1


def ingest_document(file_path: str, document_name: str, chunk_size: int = 400, overlap: int = 80) -> List[DocumentChunk]:
    """
    Complete ingestion pipeline: extract → chunk → create metadata.
    
    Args:
        file_path: Path to PDF file
        document_name: Name to store in metadata
        chunk_size: Target tokens per chunk
        overlap: Overlap tokens between chunks
        
    Returns:
        List of DocumentChunk objects
    """
    # Extract text from PDF
    full_text, total_pages = extract_text_from_pdf(file_path)
    
    # Split into chunks using chunk_text function
    text_chunks = chunk_text(full_text, chunk_size, overlap)
    
    # Create DocumentChunk objects with metadata
    document_chunks = []
    for idx, text_content in enumerate(text_chunks):
        page_num = extract_page_number(text_content)
        token_count = estimate_tokens(text_content)
        
        chunk = DocumentChunk(
            chunk_id=f"{document_name}_{idx}",
            text=text_content,
            document_name=document_name,
            page_number=page_num,
            token_count=token_count
        )
        document_chunks.append(chunk)
    
    return document_chunks
