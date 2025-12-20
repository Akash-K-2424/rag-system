"""
Conversation memory module for RAG system.
Implements short-term and long-term memory for chat context.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from collections import deque


class ConversationMemory:
    """
    Manages conversation history with short-term and long-term memory.
    - Short-term: Recent messages in current session (kept in memory)
    - Long-term: Persisted to disk for retrieval across sessions
    """
    
    def __init__(self, 
                 max_short_term: int = 10,
                 max_long_term: int = 100,
                 storage_path: str = "./conversation_history.json"):
        """
        Initialize memory system.
        
        Args:
            max_short_term: Max messages to keep in short-term memory
            max_long_term: Max messages to persist in long-term storage
            storage_path: Path to JSON file for long-term storage
        """
        self.max_short_term = max_short_term
        self.max_long_term = max_long_term
        self.storage_path = storage_path
        
        # Short-term memory (current session)
        self.short_term: Dict[str, deque] = {}
        
        # Load long-term memory from disk
        self.long_term: Dict[str, List[Dict]] = self._load_long_term()
        
        print(f"✓ Memory initialized (short-term: {max_short_term}, long-term: {max_long_term})")
    
    def _load_long_term(self) -> Dict[str, List[Dict]]:
        """Load long-term memory from disk."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    print(f"✓ Loaded {sum(len(v) for v in data.values())} messages from long-term memory")
                    return data
            except Exception as e:
                print(f"Warning: Could not load memory: {e}")
        return {}
    
    def _save_long_term(self):
        """Save long-term memory to disk."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.long_term, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save memory: {e}")
    
    def add_message(self, conversation_id: str, role: str, content: str, 
                    metadata: Optional[Dict] = None):
        """
        Add a message to memory.
        
        Args:
            conversation_id: Unique conversation identifier
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional metadata (citations, confidence, etc.)
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Add to short-term memory
        if conversation_id not in self.short_term:
            self.short_term[conversation_id] = deque(maxlen=self.max_short_term)
        self.short_term[conversation_id].append(message)
        
        # Add to long-term memory
        if conversation_id not in self.long_term:
            self.long_term[conversation_id] = []
        self.long_term[conversation_id].append(message)
        
        # Trim long-term memory if needed
        if len(self.long_term[conversation_id]) > self.max_long_term:
            self.long_term[conversation_id] = self.long_term[conversation_id][-self.max_long_term:]
        
        # Persist to disk
        self._save_long_term()
    
    def get_context(self, conversation_id: str, max_messages: int = 6) -> List[Dict]:
        """
        Get recent conversation context for the LLM.
        
        Args:
            conversation_id: Conversation identifier
            max_messages: Maximum messages to return
            
        Returns:
            List of recent messages
        """
        # First check short-term memory
        if conversation_id in self.short_term:
            messages = list(self.short_term[conversation_id])
            return messages[-max_messages:]
        
        # Fall back to long-term memory
        if conversation_id in self.long_term:
            return self.long_term[conversation_id][-max_messages:]
        
        return []
    
    def get_conversation_summary(self, conversation_id: str) -> str:
        """
        Generate a summary of the conversation for context.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Summary string
        """
        messages = self.get_context(conversation_id, max_messages=10)
        if not messages:
            return ""
        
        summary_parts = []
        for msg in messages[-6:]:  # Last 6 messages
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"]
            summary_parts.append(f"{role}: {content}")
        
        return "\n".join(summary_parts)
    
    def clear_conversation(self, conversation_id: str):
        """Clear a specific conversation from memory."""
        if conversation_id in self.short_term:
            del self.short_term[conversation_id]
        if conversation_id in self.long_term:
            del self.long_term[conversation_id]
            self._save_long_term()
    
    def get_all_conversations(self) -> List[str]:
        """Get list of all conversation IDs."""
        all_ids = set(self.short_term.keys()) | set(self.long_term.keys())
        return list(all_ids)


# Global memory instance
memory = ConversationMemory()
