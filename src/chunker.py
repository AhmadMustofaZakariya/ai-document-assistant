from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_documents(documents, chunk_size=1000, chunk_overlap=100):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators= ["\n\n", "\n", " ", ""]
    )

    chunks = text_splitter.split_documents(documents)
    chunks = [chunk for chunk in chunks if len(chunk.page_content.strip()) >50]
    return chunks

if __name__ == "__main__":
    from document_loader import load_document

    docs = load_document("./data/documents/Laws-of-the-Game-2024_25.pdf")
    chunks = chunk_documents(docs)

    print(f"Total documents (pages): {len(docs)}")
    print(f"Total chunks: {len(chunks)}")
    print(f"\nContoh chunk pertama:")
    print(chunks[0].page_content)
    print(f"\nContoh chunk kedua:")
    print(chunks[1].page_content)
    print(f"\nMetadata chunk: {chunks[0].metadata}")