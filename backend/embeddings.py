from langchain_openai import OpenAIEmbeddings
import os

def get_embeddings():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    return OpenAIEmbeddings(openai_api_key=api_key)
