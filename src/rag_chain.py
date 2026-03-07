from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os 

load_dotenv()

def get_llm():
    """Membuat object LLM menggunakan Groq(gratis)"""
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
        max_tokens=1024
    )
    return llm

def get_prompt_template():
    """Membuat template prompt untuk RAG"""

    template = """
    You are a helpful assistant that answers questions based on the provided context.
    Use ONLY the information from the context below to answer the question.
    If the answer is not in the context, say "I cannot find the answer in the document."
    Important instructions:
    - Pay close attention to numbers and figures mentioned in the context
    - Do not modify, combine, or assume numbers from different parts of the context
    - Answer in the same language as the question (Indonesian or English)
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:
    """

    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )
    return prompt

def format_docs(docs):
    """Menggabungkan semua chunks menjadi satu string context"""
    return "\n\n".join(doc.page_content for doc in docs)

def create_rag_chain(vectorestore):
    """Menggabungkan VectorDB + Prompt + LLM menjadi RAG chain"""

    llm = get_llm()
    prompt = get_prompt_template()
    retriever = vectorestore.as_retriever(search_type="similarity", search_kwargs={"k":3})

    rag_chain = (
        {
            "context":retriever | format_docs,
            "question":RunnablePassthrough()
        }
        | prompt
        | llm 
        | StrOutputParser()
    ) 
    return rag_chain, retriever

def ask_question(rag_chain, retriever, question):
    """Mengirim pertanyaan ke RAG chain dan mengembalikan jawaban ke LLM"""
    answer = rag_chain.invoke(question)
    #Ambil halaman sumber
    source_docs = retriever.invoke(question)
    sources = []
    for doc in source_docs:
        page = doc.metadata.get("page","unknown")
        if page not in sources:
            sources.append(page)
    return answer, sources

if __name__ == "__main__":
    from embedder import load_vectorstore
    #Load vectorstore yang sudah ada
    print("Load vectorstore...")
    vectorstore = load_vectorstore()

    #Buat RAG Chain dahulu
    print("Creating RAG chain...")
    rag_chain, retriever =  create_rag_chain(vectorstore)

    # Test tanya jawab
    questions = [
        "What is the offside rule?",
        "What is the NBA rules?",                 # Negative testing  
        "Tell me everything about football",      # Edge case testing
        "What is handball in football?",          
        "List all offences in football"           # Boundary Test
    ]
    
    for question in questions:
        print(f"\n{'='*50}")
        print(f"Question: {question}")
        print(f"{'='*50}")
        answer, sources = ask_question(rag_chain, retriever, question)
        print(f"Answer: {answer}")
        print(f"Sources (pages): {sources}")
