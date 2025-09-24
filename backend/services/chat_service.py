"""
Chat Service for processing messages and generating responses
"""

import os
import sys
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

from knowledge_base.processors.document_processor import DocumentProcessor

class ChatService:
    """Service for handling chat operations."""

    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.document_processor = DocumentProcessor(
            documents_dir=str(Path(__file__).parent.parent.parent / "knowledge_base")
        )

    async def process_message(self, message: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user message and generate a response using RAG.

        Args:
            message: The user's message
            user_id: Optional user identifier

        Returns:
            Dictionary containing the response and metadata
        """
        try:
            # Search for relevant documents
            docs = self.document_processor.search_similar_documents(message, n_results=5)

            # Generate answer using OpenAI
            answer = self._generate_answer(message, docs)

            return {
                "response": answer,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "success",
                "documents_used": len(docs)
            }
        except Exception as e:
            return {
                "response": f"Sorry, I encountered an error processing your message: {str(e)}",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error"
            }

    async def search_knowledge_base(self, query: str) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant information.

        Args:
            query: Search query

        Returns:
            List of relevant documents
        """
        from backend.db.database import SessionLocal
        db = SessionLocal()
        try:
            return self.document_processor.search_similar_documents(query, n_results=5, db=db)
        finally:
            db.close()

    def _generate_answer(self, query: str, docs: List[Dict[str, Any]]) -> str:
        """Generate an answer using retrieved documents and OpenAI."""
        if not docs:
            return "I couldn't find any relevant information to answer your question."

        # Prepare context from documents
        context_parts = []
        for doc in docs:
            context_parts.append(f"Content: {doc['content'][:500]}...")  # Limit content length
        context = "\n\n".join(context_parts)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context. Be concise but informative."},
                    {"role": "user", "content": f"Question: {query}\n\nContext:\n{context}\n\nPlease provide a helpful answer based on the context above."}
                ],
                max_tokens=500,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error generating answer: {str(e)}")
            return f"Based on the knowledge base: {context[:500]}..."

