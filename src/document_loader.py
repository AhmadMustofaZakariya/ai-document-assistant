from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import CSVLoader
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.document_loaders import Docx2txtLoader
import os 

def load_document(file_path):
    if os.path.splitext(file_path)[1] == ".pdf":
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return documents
    elif os.path.splitext(file_path)[1] == ".csv":
        loader = CSVLoader(file_path)    
        documents = loader.load()
        return documents
    elif os.path.splitext(file_path)[1] == ".docx":
        loader = Docx2txtLoader(file_path)    
        documents = loader.load()
        return documents
    elif os.path.splitext(file_path)[1] == ".xlsx":
        loader = UnstructuredExcelLoader(file_path)    
        documents = loader.load()
        return documents
    else:
        print("Unsuported Format File, please choose another file that match the format")
    return None

if __name__ == "__main__":
    docs = load_document("./data/documents/Laws-of-the-Game-2024_25.pdf")

    print("Total pages: ", len(docs))
    print("\nFirst page content preview:\n")
    print(docs[0].page_content[:500])
    print(docs[0].metadata)