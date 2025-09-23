"""
RAG (Retrieval-Augmented Generation) Service
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import openai
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the knowledge_base directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent / "knowledge_base"))

from processors.document_processor import DocumentProcessor

class RAGService:
    """Service for Retrieval-Augmented Generation."""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.document_processor = DocumentProcessor(
            documents_dir=str(Path(__file__).parent.parent.parent / "knowledge_base"),
            embeddings_dir=str(Path(__file__).parent.parent.parent / "knowledge_base" / "embeddings")
        )
    
    def search_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents in the knowledge base.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant documents with metadata and scores
        """
        return self.document_processor.search_similar_documents(query, n_results)
    
    def generate_answer(self, query: str, docs: List[Dict[str, Any]], session_context: Optional[str] = None, relevance_threshold: float = 0.7) -> Dict[str, Any]:
        """
        Generate an answer using retrieved documents and context.
        
        Args:
            query: User's question
            docs: Retrieved documents from search
            session_context: Optional session context
            relevance_threshold: Minimum relevance score to consider documents relevant
            
        Returns:
            Dictionary containing answer, confidence, and metadata
        """
        if not docs:
            self._log_unanswered_query(query, "No documents found")
            return {
                "answer": "I couldn't find any relevant information to answer your question. Please try rephrasing your query or check if the knowledge base has been populated.",
                "confidence": "low",
                "reason": "no_documents_found",
                "documents_used": []
            }
        
        # Filter documents by relevance threshold
        relevant_docs = [doc for doc in docs if doc.get('relevance_score', 0) >= relevance_threshold]
        
        if not relevant_docs:
            self._log_unanswered_query(query, f"No documents above relevance threshold {relevance_threshold}")
            return {
                "answer": f"I found some documents but they don't seem highly relevant to your question (relevance below {relevance_threshold}). Please try rephrasing your query or ask a more specific question.",
                "confidence": "low",
                "reason": "low_relevance",
                "documents_used": docs[:2]  # Show top 2 for reference
            }
        
        # Prepare context from relevant documents
        context_parts = []
        for i, doc in enumerate(relevant_docs, 1):
            context_parts.append(f"Document {i} (Relevance: {doc['relevance_score']:.2f}):\n{doc['content']}\n")
        
        context = "\n".join(context_parts)
        
        # Prepare the prompt
        system_prompt = """You are a helpful assistant that answers questions based on the provided context from a knowledge base. 
        Use the retrieved documents to provide accurate, relevant answers. If the context doesn't contain enough information 
        to fully answer the question, say so and provide what information you can find.
        
        Guidelines:
        - Base your answer primarily on the provided context
        - If multiple documents are relevant, synthesize information from all of them
        - Be concise but comprehensive
        - If you're uncertain about something, express that uncertainty
        - Cite which document(s) your answer is based on when relevant
        - If the context doesn't fully answer the question, acknowledge this limitation"""
        
        user_prompt = f"""Question: {query}

Context from knowledge base:
{context}

Please provide a comprehensive answer based on the above context."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            # Determine confidence based on relevance scores
            avg_relevance = sum(doc.get('relevance_score', 0) for doc in relevant_docs) / len(relevant_docs)
            if avg_relevance >= 0.8:
                confidence = "high"
            elif avg_relevance >= 0.6:
                confidence = "medium"
            else:
                confidence = "low"
            
            return {
                "answer": answer,
                "confidence": confidence,
                "reason": "success",
                "documents_used": relevant_docs,
                "avg_relevance": avg_relevance
            }
            
        except Exception as e:
            print(f"Error generating answer: {str(e)}")
            self._log_unanswered_query(query, f"Error: {str(e)}")
            return {
                "answer": f"I encountered an error while generating an answer: {str(e)}",
                "confidence": "low",
                "reason": "error",
                "documents_used": []
            }
    
    def _log_unanswered_query(self, query: str, reason: str):
        """Log unanswered queries for later knowledge base updates."""
        log_entry = {
            "query": query,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # In a production system, you might want to log to a database or file
        print(f"UNANSWERED QUERY LOG: {log_entry}")
        
        # Optionally save to a file for later analysis
        log_file = Path(__file__).parent.parent.parent / "knowledge_base" / "unanswered_queries.json"
        try:
            import json
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(log_entry)
            
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"Could not save unanswered query log: {e}")
    
    def process_knowledge_base(self):
        """Process all documents in the knowledge base."""
        return self.document_processor.process_all_documents()
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        try:
            # Get collection info
            collection = self.document_processor.collection
            count = collection.count()
            
            return {
                "total_chunks": count,
                "collection_name": collection.name,
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "total_chunks": 0
            }
