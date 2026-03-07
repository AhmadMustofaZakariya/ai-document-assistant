from langchain_community.document_loaders import PyPDFLoader

def load_document(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents

if __name__ == "__main__":
    docs = load_document("./data/documents/Laws-of-the-Game-2024_25.pdf")

    print("Total pages: ", len(docs))
    print("\nFirst page content preview:\n")
    print(docs[0].page_content[:500])
    print(docs[0].metadata)