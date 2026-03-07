from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os 

def get_embeddings():
    """Membuat object embedding model dari HuggingFace"""
    embeddings = HuggingFaceEmbeddings(
        model_name ="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs = {"device":"cpu"},
        encode_kwargs = {"normalize_embeddings":"True"}
    )
    return embeddings

def create_vectorstore(chunks, persist_directory=None):
    """Menyimpan Vector ke VectorDB disini menggunakan Chroma"""
    embeddings = get_embeddings()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )

    print(f"Vectorstore created! Total Vectors: {vectorstore._collection.count()}")
    return vectorstore

def load_vectorstore(persist_directory="./data/vectorstore"):
    """Load data yang sudah di vector, jadi tidak perlu embed ulang"""
    embeddings=get_embeddings()

    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    return vectorstore

if __name__ == "__main__":
    from document_loader import load_document
    from chunker import chunk_documents

    #Step 1: Load
    print("Loading document...")
    docs = load_document("./data/documents/Laws-of-the-Game-2024_25.pdf")

    #Step 2: Chunk
    print("Chunking document...")
    chunks = chunk_documents(docs)
    print(f"Total chunks : {len(chunks)}")

    #Step 3: Embed dan simpan ke VectorDB (Chroma)
    vectorstore = create_vectorstore(chunks)

    # Test similarity search
    print("\nTest similarity search:")
    query = "What is offside rule?"
    results = vectorstore.similarity_search(query, k=3)
    
    for i, doc in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(doc.page_content[:300])
        print(f"Source: page {doc.metadata.get('page', 'unknown')}")


