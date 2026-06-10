import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# We use HuggingFace free embeddings for local text vectorization
# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# -------------------------- local --------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="/app/models/all-MiniLM-L6-v2"
)

db_dir = os.getenv("CHROMA_DB_DIR", "./chroma_db")

def get_vector_store():
    return Chroma(persist_directory=db_dir, embedding_function=embeddings)

def add_document_to_store(text, metadata):
    """Splits text and adds it to the Chroma vector store."""
    if not text.strip():
        return
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100
    )
    chunks = text_splitter.split_text(text)
    metadatas = [metadata for _ in chunks]
    
    vector_store = get_vector_store()
    vector_store.add_texts(texts=chunks, metadatas=metadatas)

def search_similar_documents(query, top_k=3):
    """Retrieves relevant document chunks based on the query."""
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=top_k)
    return results

def remove_document_from_store(doc_id):
    import chromadb
    client = chromadb.PersistentClient(path=db_dir)
    
    collection = client.get_or_create_collection(name="langchain")
    
    collection.delete(where={"doc_id": doc_id})