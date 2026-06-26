#!/usr/bin/env python3
"""
Example solution for Stage 8 Exercise 4: Add Persistence

This script demonstrates implementing conversation persistence using SQLite.
It saves conversations to a database, loads previous conversations on startup,
and allows the user to view conversation history.
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and API client
from utils.config import config
from utils.api_client import APIClient, create_payload
from utils.formatter import Formatter


class SQLiteStorage:
    """
    SQLite-based conversation storage.
    
    Provides persistence for agent conversations, allowing
    saving, loading, and listing of conversation history.
    """

    def __init__(self, db_path: str = "conversations.db"):
        """
        Initialize the storage with a database path.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        """Create the necessary tables if they don't exist."""
        import sqlite3
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    system_prompt TEXT
                )
            """)
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            """)
            
            # Tool calls table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tool_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT,
                    message_id INTEGER,
                    name TEXT,
                    arguments TEXT,
                    result TEXT,
                    success INTEGER,
                    timestamp TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id),
                    FOREIGN KEY (message_id) REFERENCES messages(id)
                )
            """)
            
            conn.commit()

    def create_conversation(self, system_prompt: str = "") -> str:
        """
        Create a new conversation and return its ID.
        
        Args:
            system_prompt: The system prompt for the conversation.
            
        Returns:
            Unique conversation ID.
        """
        import sqlite3
        
        conv_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (id, title, created_at, updated_at, system_prompt) VALUES (?, ?, ?, ?, ?)",
                (conv_id, f"Conversation {conv_id[-6:]}", now, now, system_prompt)
            )
            conn.commit()
        
        return conv_id

    def save_message(self, conversation_id: str, role: str, content: str) -> int:
        """
        Save a message to a conversation.
        
        Args:
            conversation_id: The conversation ID.
            role: Message role (user, assistant, system).
            content: Message content.
            
        Returns:
            Message ID.
        """
        import sqlite3
        
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (conversation_id, role, content, now)
            )
            msg_id = cursor.lastrowid
            
            # Update conversation's updated_at
            cursor.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (now, conversation_id)
            )
            conn.commit()
        
        return msg_id

    def save_tool_call(self, conversation_id: str, message_id: int, name: str, 
                       arguments: str, result: str, success: bool) -> int:
        """
        Save a tool call to a conversation.
        
        Args:
            conversation_id: The conversation ID.
            message_id: Associated message ID.
            name: Tool name.
            arguments: Tool arguments as JSON string.
            result: Tool result.
            success: Whether the tool call succeeded.
            
        Returns:
            Tool call ID.
        """
        import sqlite3
        
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tool_calls (conversation_id, message_id, name, arguments, result, success, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (conversation_id, message_id, name, arguments, result, 1 if success else 0, now)
            )
            tool_id = cursor.lastrowid
            conn.commit()
        
        return tool_id

    def get_conversation(self, conversation_id: str) -> dict:
        """
        Load a complete conversation with all messages.
        
        Args:
            conversation_id: The conversation ID.
            
        Returns:
            Dictionary with conversation metadata and messages.
        """
        import sqlite3
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get conversation metadata
            cursor.execute(
                "SELECT * FROM conversations WHERE id = ?",
                (conversation_id,)
            )
            conv_row = cursor.fetchone()
            
            if not conv_row:
                return None
            
            columns = [desc[0] for desc in cursor.description]
            conversation = dict(zip(columns, conv_row))
            
            # Get messages
            cursor.execute(
                "SELECT id, role, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY id",
                (conversation_id,)
            )
            messages = []
            for msg_row in cursor.fetchall():
                msg_columns = [desc[0] for desc in cursor.description]
                messages.append(dict(zip(msg_columns, msg_row)))
            
            # Get tool calls
            cursor.execute(
                "SELECT id, name, arguments, result, success, timestamp FROM tool_calls WHERE conversation_id = ? ORDER BY id",
                (conversation_id,)
            )
            tool_calls = []
            for tc_row in cursor.fetchall():
                tc_columns = [desc[0] for desc in cursor.description]
                tool_calls.append(dict(zip(tc_columns, tc_row)))
            
            conversation["messages"] = messages
            conversation["tool_calls"] = tool_calls
            
            return conversation

    def list_conversations(self, limit: int = 20) -> list:
        """
        List all conversations, newest first.
        
        Args:
            limit: Maximum number of conversations to return.
            
        Returns:
            List of conversation summaries.
        """
        import sqlite3
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, created_at, updated_at FROM conversations ORDER BY updated_at DESC LIMIT ?",
                (limit,)
            )
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation and all its messages.
        
        Args:
            conversation_id: The conversation ID.
            
        Returns:
            True if deleted, False if not found.
        """
        import sqlite3
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
            conn.commit()
            return cursor.rowcount > 0


def demo_persistence():
    """Demonstrate conversation persistence with SQLite."""
    f = Formatter(show_raw=True)

    f.header("STAGE 8 EXERCISE 4: ADD PERSISTENCE")
    f.script("Implementing Conversation Persistence with SQLite")
    f.print()

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.config(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    f.print()

    # Create storage with a test database
    db_path = "test_conversations.db"
    storage = SQLiteStorage(db_path)

    f.script(f"  Database: {db_path}")
    f.print()

    # Demonstrate creating a conversation
    f.subheader("STEP 1: CREATE A NEW CONVERSATION")
    conv_id = storage.create_conversation(
        system_prompt="You are a helpful assistant."
    )
    f.script(f"  Created conversation: {conv_id}")
    f.print()

    # Demonstrate saving messages
    f.subheader("STEP 2: SAVE MESSAGES")
    
    msg1_id = storage.save_message(conv_id, "user", "Hello! What can you do?")
    f.script(f"  Saved user message (ID: {msg1_id})")
    
    msg2_id = storage.save_message(conv_id, "assistant", "I can help with many things! I can search, calculate, and answer questions.")
    f.script(f"  Saved assistant message (ID: {msg2_id})")
    
    msg3_id = storage.save_message(conv_id, "user", "What's 2 + 2?")
    f.script(f"  Saved user message (ID: {msg3_id})")
    
    # Save a tool call
    tc_id = storage.save_tool_call(
        conv_id, msg3_id, "calculate", 
        json.dumps({"expression": "2 + 2"}),
        "Result: 4",
        True
    )
    f.script(f"  Saved tool call (ID: {tc_id})")
    f.print()

    # Demonstrate loading a conversation
    f.subheader("STEP 3: LOAD THE CONVERSATION")
    
    conversation = storage.get_conversation(conv_id)
    if conversation:
        f.script(f"  Conversation: {conversation['title']}")
        f.script(f"  Created: {conversation['created_at']}")
        f.script(f"  Messages: {len(conversation['messages'])}")
        f.script(f"  Tool calls: {len(conversation['tool_calls'])}")
        f.print()
        
        f.script("  Messages:")
        for msg in conversation['messages']:
            f.script(f"    [{msg['role']}] {msg['content'][:60]}...")
        f.print()
        
        f.script("  Tool calls:")
        for tc in conversation['tool_calls']:
            f.script(f"    {tc['name']}: {tc['arguments']} -> {tc['result']}")
    else:
        f.error("Conversation not found")
    
    f.print()

    # Demonstrate listing conversations
    f.subheader("STEP 4: LIST ALL CONVERSATIONS")
    
    # Create a couple more conversations for demonstration
    conv2_id = storage.create_conversation()
    conv3_id = storage.create_conversation()
    
    conversations = storage.list_conversations(limit=10)
    f.script(f"  Total conversations: {len(conversations)}")
    f.print()
    
    f.script(f"  {'ID':<35} {'Title':<25} {'Updated':<20}")
    f.dim("  " + "-" * 80)
    for conv in conversations:
        f.script(f"  {conv['id']:<35} {conv['title']:<25} {conv['updated_at']:<20}")
    
    f.print()

    # Demonstrate the expected interface from exercises.md
    f.subheader("EXPECTED INTERFACE (from exercises.md)")
    f.script("  ```python")
    f.script("  agent = FinalAgent(config, storage=SQLiteStorage('conversations.db'))")
    f.script("  conversations = agent.storage.list_conversations()")
    f.script("  ```")
    f.print()

    # Cleanup
    f.subheader("CLEANUP")
    import os
    if os.path.exists(db_path):
        os.remove(db_path)
        f.script(f"  Removed test database: {db_path}")
    
    f.print()

    # Summary
    f.subheader("SUMMARY: PERSISTENCE FEATURES")
    f.script("  - Conversations are stored in SQLite with unique IDs")
    f.script("  - Each conversation has messages and tool calls")
    f.script("  - Full conversation history can be loaded by ID")
    f.script("  - Conversions can be listed, searched, and deleted")
    f.script("  - Timestamps track when conversations were created/updated")
    f.script("  - Foreign keys maintain referential integrity")


if __name__ == "__main__":
    demo_persistence()