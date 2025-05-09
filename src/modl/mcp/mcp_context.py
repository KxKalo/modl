"""
Model Context Protocol (MCP) core implementation for modl.
Defines the structured context format for LLM interactions.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Tool(BaseModel):
    """Represents a tool available to the model."""
    name: str
    description: str
    args: List[str] = Field(default_factory=list)


class RetrievedDocument(BaseModel):
    """Represents a document retrieved for context."""
    source: str
    query: str
    results: List[Dict[str, Any]] = Field(default_factory=list)


class ChatMessage(BaseModel):
    """Represents a message in the chat history."""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class UserProfile(BaseModel):
    """Represents user profile information."""
    name: Optional[str] = None
    style: List[str] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    past_interactions: List[Dict[str, Any]] = Field(default_factory=list)


class Memory(BaseModel):
    """Represents both long-term and short-term memory."""
    long_term: Dict[str, Any] = Field(default_factory=dict)
    short_term: Dict[str, Any] = Field(default_factory=dict)


class MCPContext(BaseModel):
    """
    The core Model Context Protocol context object.
    Defines the structured format for all context information passed to LLMs.
    """
    system_instruction: str
    user_goal: str
    user_profile: UserProfile = Field(default_factory=UserProfile)
    retrieved_documents: List[RetrievedDocument] = Field(default_factory=list)
    tools: List[Tool] = Field(default_factory=list)
    chat_history: List[ChatMessage] = Field(default_factory=list)
    memory: Memory = Field(default_factory=Memory)

    def to_prompt(self) -> str:
        """
        Converts the structured context into a prompt string for the LLM.
        This is where the MCP interpreter logic lives.
        """
        prompt_parts = [
            f"System: {self.system_instruction}\n",
            f"User Goal: {self.user_goal}\n"
        ]

        if self.user_profile.name:
            prompt_parts.append(f"User Profile: {self.user_profile.name}\n")
            if self.user_profile.style:
                prompt_parts.append(f"Style Preferences: {', '.join(self.user_profile.style)}\n")

        if self.retrieved_documents:
            prompt_parts.append("\nRetrieved Information:")
            for doc in self.retrieved_documents:
                prompt_parts.append(f"\nFrom {doc.source}:")
                for result in doc.results:
                    prompt_parts.append(f"- {result.get('name', 'Unknown')}: {result.get('description', '')}")

        if self.tools:
            prompt_parts.append("\nAvailable Tools:")
            for tool in self.tools:
                prompt_parts.append(f"- {tool.name}: {tool.description}")

        if self.chat_history:
            prompt_parts.append("\nChat History:")
            for msg in self.chat_history:
                prompt_parts.append(f"{msg.role.capitalize()}: {msg.content}")

        return "\n".join(prompt_parts)

    def update_memory(self, key: str, value: Any, memory_type: str = "short_term"):
        """Updates either long-term or short-term memory."""
        if memory_type == "long_term":
            self.memory.long_term[key] = value
        else:
            self.memory.short_term[key] = value

    def add_chat_message(self, role: str, content: str):
        """Adds a new message to the chat history."""
        self.chat_history.append(ChatMessage(role=role, content=content))

    def add_retrieved_document(self, source: str, query: str, results: List[Dict[str, Any]]):
        """Adds a new retrieved document to the context."""
        self.retrieved_documents.append(
            RetrievedDocument(source=source, query=query, results=results)
        ) 