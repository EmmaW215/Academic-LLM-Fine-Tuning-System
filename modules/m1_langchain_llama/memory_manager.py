# modules/m1_langchain_llama/memory_manager.py
"""Conversation memory management."""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ConversationTurn:
    """Single conversation turn."""
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


class MemoryManager:
    """Manages conversation history and context."""
    
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.history: List[ConversationTurn] = []
        
    def add_turn(self, role: str, content: str):
        """Add a conversation turn."""
        turn = ConversationTurn(role=role, content=content)
        self.history.append(turn)
        
        # Trim if exceeds max
        if len(self.history) > self.max_turns * 2:  # *2 for user+assistant pairs
            self.history = self.history[-self.max_turns * 2:]
    
    def get_context_string(self) -> str:
        """Get conversation history as formatted string."""
        context_parts = []
        for turn in self.history:
            prefix = "User" if turn.role == "user" else "Assistant"
            context_parts.append(f"{prefix}: {turn.content}")
        return "\n".join(context_parts)
    
    def get_langchain_memory(self):
        """Get memory as list of messages (compatible with LangChain)."""
        # Return a simple list format that can be used with LangChain
        messages = []
        for turn in self.history[-self.max_turns * 2:]:
            from langchain_core.messages import HumanMessage, AIMessage
            if turn.role == "user":
                messages.append(HumanMessage(content=turn.content))
            else:
                messages.append(AIMessage(content=turn.content))
        return messages
    
    def clear(self):
        """Clear all history."""
        self.history = []
    
    def to_dict(self) -> List[Dict]:
        """Export history as list of dicts."""
        return [
            {"role": t.role, "content": t.content, "timestamp": t.timestamp.isoformat()}
            for t in self.history
        ]

