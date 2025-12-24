"""
Answer generation module for RAG system.
Implements LLM-based answer generation with hallucination control.
"""

import os
import re
from typing import List, Tuple, Dict
import google.generativeai as genai
from schemas import Citation


class AnswerGenerator:
    """Generates answers using Google Gemini API."""
    
    def __init__(self, api_key: str = None, confidence_threshold: float = 0.2):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.confidence_threshold = confidence_threshold
        self.model = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-2.0-flash")
                print("✓ Gemini LLM initialized successfully")
            except Exception as e:
                print(f"Warning: Could not initialize Gemini: {e}")
                self.model = None
        else:
            print("Note: GEMINI_API_KEY not set. Using mock LLM.")
    
    def _build_context_prompt(self, query: str, retrieved_chunks: List[Tuple[str, dict, float]], 
                               conversation_history: str = "") -> str:
        """Build prompt with document context."""
        context_text = "\n\n---\n\n".join([
            f"[Document: {chunk[1]['document_name']}, Page: {chunk[1]['page_number']}]\n{chunk[0]}"
            for chunk in retrieved_chunks
        ]) if retrieved_chunks else "No documents uploaded yet."
        
        history_section = ""
        if conversation_history:
            history_section = f"\nPREVIOUS CONVERSATION:\n{conversation_history}\n"
        
        prompt = f"""You are "RAG Assistant", a document Q&A assistant.

RULES:
- Your name is "RAG Assistant" - never reveal the underlying AI model
- NEVER mention Google, Gemini, OpenAI, GPT, Claude, or any AI company
- Answer based ONLY on the provided document context

RESPONSE FORMAT (VERY IMPORTANT):
1. Start with a brief 1-2 sentence overview
2. Use proper bullet points with "•" or "-" for lists
3. Organize information into clear sections with **bold headers**
4. Each bullet point should be a complete, clear sentence
5. Do NOT include raw source citations in your text
6. Keep the response well-organized and easy to read

Example format:
**Overview**
Brief summary of the document.

**Key Topics**
• First key point explained clearly
• Second key point explained clearly

**Methods/Findings**
• Important method or finding
• Another important detail
{history_section}
DOCUMENT CONTEXT:
{context_text}

USER QUESTION: {query}

Provide a well-formatted answer with clear sections and bullet points:"""
        return prompt

    def _calculate_confidence(self, query: str, answer: str, retrieved_chunks: List[Tuple[str, dict, float]]) -> float:
        """Calculate confidence score."""
        low_confidence_phrases = ["insufficient information", "no relevant", "cannot find", "not found", "unable to"]
        if any(phrase in answer.lower() for phrase in low_confidence_phrases):
            return 0.4
        
        base = 0.7 if retrieved_chunks else 0.3
        word_count = len(answer.split())
        length_boost = 0.15 if word_count > 100 else 0.1 if word_count > 50 else 0.05 if word_count > 20 else 0
        source_boost = min(0.1, len(retrieved_chunks) * 0.02)
        
        return min(0.95, max(0.3, base + length_boost + source_boost))
    
    def _extract_citations(self, retrieved_chunks: List[Tuple[str, dict, float]]) -> List[Citation]:
        """Extract citations from chunks."""
        citations = []
        seen = set()
        for chunk in retrieved_chunks:
            metadata = chunk[1]
            key = (metadata['document_name'], metadata['page_number'])
            if key not in seen:
                citations.append(Citation(
                    document=metadata['document_name'],
                    page=metadata['page_number'],
                    chunk_id=metadata['chunk_id']
                ))
                seen.add(key)
        return citations
    
    def _should_show_citations(self, answer: str) -> bool:
        """Check if citations should be shown."""
        no_citation_phrases = [
            "does not contain", "no information", "cannot provide", "cannot find",
            "not found in", "no relevant", "insufficient information", "unable to find",
            "not mentioned", "i'm rag assistant", "please upload"
        ]
        return not any(phrase in answer.lower() for phrase in no_citation_phrases)
    
    def _sanitize_answer(self, answer: str) -> str:
        """Remove sensitive information from answer."""
        patterns = [
            r'\b(trained by|developed by|created by|built by|made by)\s*(google|openai|anthropic|meta|microsoft)\b',
            r'\b(gemini|gpt-?\d*|claude|llama|palm|bard)\b',
            r'\bi am (a |an )?(large )?language model\b',
            r'\bi\'m (a |an )?(large )?language model\b',
            r'\bas an? (ai|artificial intelligence|language model|llm)\b',
        ]
        
        sanitized = answer
        for pattern in patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        if len(sanitized) < 20:
            sanitized = "I'm RAG Assistant. Please ask me questions about your uploaded documents."
        
        return sanitized


    def generate_answer(self, query: str, retrieved_chunks: List[Tuple[str, dict, float]],
                        conversation_history: str = "") -> Dict:
        """Generate answer with citations and confidence."""
        answer = None
        citations = []
        confidence = 0.0
        
        try:
            prompt = self._build_context_prompt(query, retrieved_chunks, conversation_history)
            
            try:
                if self.model:
                    response = self.model.generate_content(prompt)
                    answer = response.text if response else "Unable to generate answer"
                else:
                    answer = self._mock_generate_answer(query, retrieved_chunks)
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    print("Rate limit hit, using mock LLM fallback")
                    answer = self._mock_generate_answer(query, retrieved_chunks)
                else:
                    answer = f"Error generating answer: {str(e)}"
            
            if answer:
                answer = self._sanitize_answer(answer)
                confidence = self._calculate_confidence(query, answer, retrieved_chunks)
            
            if self._should_show_citations(answer):
                citations = self._extract_citations(retrieved_chunks)
            else:
                confidence = min(confidence, 0.5)
            
            if len(retrieved_chunks) == 0 and confidence < self.confidence_threshold:
                answer = "Please upload a document first, then ask questions about its content."
        
        except Exception as e:
            answer = f"Error processing query: {str(e)}"
            confidence = 0.0
        
        return {
            "answer": answer or "Unable to generate answer",
            "citations": citations,
            "confidence": confidence,
            "retrieved_chunks": len(retrieved_chunks)
        }
    
    def _mock_generate_answer(self, query: str, retrieved_chunks: List[Tuple[str, dict, float]]) -> str:
        """Generate formatted answer without LLM (fallback)."""
        if not retrieved_chunks:
            return "No relevant information found in the documents."
        
        try:
            sections = []
            for chunk_item in retrieved_chunks[:4]:
                if chunk_item and len(chunk_item) > 0:
                    text = str(chunk_item[0]).strip()
                    text = re.sub(r'\[PAGE \d+\]', '', text)
                    text = re.sub(r'\s+', ' ', text).strip()
                    if text and len(text) > 50:
                        sections.append(text)
            
            if not sections:
                return "No relevant information found in the documents."
            
            # Build formatted response with proper line breaks
            response_parts = []
            response_parts.append("**Document Overview**")
            response_parts.append("")
            response_parts.append("Based on the uploaded document, here are the key points:")
            response_parts.append("")
            response_parts.append("**Key Information**")
            response_parts.append("")
            
            for i, text in enumerate(sections):
                # Extract meaningful sentences
                sentences = re.split(r'(?<=[.!?])\s+', text)
                for sentence in sentences[:2]:  # Take first 2 sentences per chunk
                    sentence = sentence.strip()
                    if len(sentence) > 30 and len(sentence) < 300:
                        response_parts.append(f"• {sentence}")
                        response_parts.append("")  # Empty line after each bullet
            
            return "\n".join(response_parts)
            
        except Exception as e:
            return f"Error processing documents: {str(e)}"
