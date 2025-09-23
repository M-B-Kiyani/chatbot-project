import os, glob
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.config import Settings
import openai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create ephemeral Chroma client
chroma_client = chromadb.PersistentClient(
    path="./chroma_test_store",
    settings=Settings(anonymized_telemetry=False)
)

files = glob.glob("knowledge_base/Company_Info/*")[:2]  # First 2 files
texts=[]
for f in files:
    try:
        texts.append(open(f,"r",encoding="utf-8",errors="ignore").read())
    except:
        continue

splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)
chunks=[]
for t in texts:
    chunks.extend(splitter.split_text(t)[:3])  # First 3 chunks per file

col = chroma_client.get_or_create_collection(name="kb_test")

# Generate embeddings using OpenAI client
embs = []
for chunk in chunks:
    try:
        response = client.embeddings.create(model="text-embedding-3-small", input=chunk)
        embs.append(response.data[0].embedding)
    except Exception as e:
        print(f"Error generating embedding: {e}")
        continue

col.add(ids=[f"t{i}" for i in range(len(embs))],documents=chunks[:len(embs)],embeddings=embs)
print("indexed_chunks", len(embs))