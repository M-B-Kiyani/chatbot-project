import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings

# Load environment variables from .env file
load_dotenv()

# Embedding model - fixed environment variable name
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

def load_documents(folder_path="knowledge_base"):
    """Load documents from knowledge base directory and all subdirectories."""
    docs = []
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print(f"Warning: Knowledge base directory {folder_path} does not exist")
        return docs
    
    # Supported file extensions
    supported_extensions = {'.txt', '.md', '.pdf', '.docx'}
    
    # Recursively find all supported files
    for file_path in folder_path.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            try:
                print(f"Loading: {file_path.relative_to(folder_path)}")
                
                if file_path.suffix.lower() in ['.txt', '.md']:
                    docs.extend(TextLoader(str(file_path)).load())
                elif file_path.suffix.lower() == '.pdf':
                    docs.extend(PyPDFLoader(str(file_path)).load())
                elif file_path.suffix.lower() == '.docx':
                    docs.extend(Docx2txtLoader(str(file_path)).load())
                    
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue
    
    print(f"Loaded {len(docs)} documents from {folder_path}")
    return docs

def chunk_documents(docs):
    """Split documents into chunks for better retrieval."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Increased for better context
        chunk_overlap=200,  # Increased overlap for better continuity
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    print(f"Created {len(chunks)} chunks from {len(docs)} documents")
    return chunks

def create_vectorstore(docs):
    """Create vector store from documents."""
    connection_string = os.getenv("DATABASE_URL")
    
    if not connection_string:
        print("Warning: DATABASE_URL not set. Using ChromaDB as fallback.")
        # Fallback to ChromaDB if no PostgreSQL connection
        from langchain_community.vectorstores import Chroma
        return Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory="./knowledge_base/embeddings/chroma_db"
        )
    
    try:
        return PGVector.from_documents(
            documents=docs,
            embedding=embeddings,
            connection_string=connection_string,
            collection_name="knowledge_base"
        )
    except Exception as e:
        print(f"Error creating PGVector: {e}")
        print("Falling back to ChromaDB...")
        from langchain_community.vectorstores import Chroma
        return Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory="./knowledge_base/embeddings/chroma_db"
        )

def search_vectorstore(query, k=5):
    """Search the vector store for relevant documents."""
    connection_string = os.getenv("DATABASE_URL")
    
    if not connection_string:
        # Use ChromaDB if no PostgreSQL connection
        from langchain_community.vectorstores import Chroma
        db = Chroma(
            persist_directory="./knowledge_base/embeddings/chroma_db",
            embedding_function=embeddings
        )
    else:
        try:
            db = PGVector(
                connection_string=connection_string,
                embedding_function=embeddings,
                collection_name="knowledge_base"
            )
        except Exception as e:
            print(f"Error connecting to PGVector: {e}")
            print("Falling back to ChromaDB...")
            from langchain_community.vectorstores import Chroma
            db = Chroma(
                persist_directory="./knowledge_base/embeddings/chroma_db",
                embedding_function=embeddings
            )
    
    return db.similarity_search_with_score(query, k=k)

def generate_answer(query, docs, session_context=None):
    """Generate an answer using retrieved documents."""
    if not docs:
        return "Sorry, I don't have enough information to answer that yet."

    # Extract content and scores from documents
    content_with_scores = []
    for doc, score in docs:
        content_with_scores.append(f"[Relevance: {score:.2f}] {doc.page_content}")
    
    combined = "\n\n".join(content_with_scores)
    
    # Use OpenAI to generate a proper answer
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context from a knowledge base. Use the retrieved documents to provide accurate, relevant answers."},
                {"role": "user", "content": f"Question: {query}\n\nContext from knowledge base:\n{combined}\n\nPlease provide a comprehensive answer based on the above context."}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error generating answer with OpenAI: {e}")
        # Fallback to simple concatenation
        return f"Based on the knowledge base:\n\n{combined[:1000]}..."
