import streamlit as st
import sys
import os
import tempfile

# Path langsung ke src (tanpa app/ folder)
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from document_loader import load_document
from chunker import chunk_documents
from embedder import create_vectorstore
from rag_chain import create_rag_chain, ask_question

# ─── PAGE CONFIG ───────────────────────────────────────
st.set_page_config(
    page_title="AI Document Assistant",
    page_icon="📄",
    layout="wide"
)

def save_uploaded_file(uploaded_file):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.write(uploaded_file.getbuffer())
    tmp.close()
    return tmp.name

def process_document(file_path):
    with st.spinner("📖 Loading document..."):
        docs = load_document(file_path)
        st.sidebar.caption(f"✅ Loaded {len(docs)} pages")
    with st.spinner("✂️ Chunking document..."):
        chunks = chunk_documents(docs)
        st.sidebar.caption(f"✅ Created {len(chunks)} chunks")
    with st.spinner("🔢 Embedding & building VectorDB..."):
        vectorstore = create_vectorstore(chunks, persist_directory=None)
        st.sidebar.caption(f"✅ VectorDB ready!")
    return vectorstore

def cleanup_temp_file(file_path):
    try:
        os.unlink(file_path)
    except Exception:
        pass

# ─── SESSION STATE ─────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None
if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "document_processed" not in st.session_state:
    st.session_state.document_processed = False
if "current_filename" not in st.session_state:
    st.session_state.current_filename = None

# ─── SIDEBAR ───────────────────────────────────────────
with st.sidebar:
    st.title("📄 AI Document Assistant")
    st.markdown("---")
    st.subheader("📁 Upload Document")
    uploaded_file = st.file_uploader(
        "Upload a PDF file",
        type=["pdf"],
        help="Upload a PDF document to start chatting"
    )

    if uploaded_file is not None:
        is_new_file = uploaded_file.name != st.session_state.current_filename
        if is_new_file:
            st.info(f"📄 New file detected: {uploaded_file.name}")

        if st.button("🚀 Process Document", use_container_width=True):
            try:
                file_path = save_uploaded_file(uploaded_file)
                vectorstore = process_document(file_path)
                with st.spinner("🤖 Setting up AI..."):
                    rag_chain, retriever = create_rag_chain(vectorstore)
                    st.session_state.rag_chain = rag_chain
                    st.session_state.retriever = retriever
                    st.session_state.document_processed = True
                    st.session_state.current_filename = uploaded_file.name
                    st.session_state.messages = []
                cleanup_temp_file(file_path)
                st.success("✅ Document processed successfully!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    st.markdown("---")
    if st.session_state.document_processed:
        st.success("🟢 AI is ready!")
        st.info(f"📄 Active file:\n{st.session_state.current_filename}")
        if st.button("🔄 Reset / New Document", use_container_width=True):
            st.session_state.messages = []
            st.session_state.rag_chain = None
            st.session_state.retriever = None
            st.session_state.document_processed = False
            st.session_state.current_filename = None
            st.rerun()
    else:
        st.warning("🟡 Please upload a document first")

    st.markdown("---")
    st.caption("Built with LangChain + Groq + ChromaDB + Streamlit")

# ─── MAIN CHAT AREA ────────────────────────────────────
st.title("💬 Chat with your Document")

if not st.session_state.document_processed:
    st.markdown("""
    ### 👋 Welcome to AI Document Assistant!
    
    **How to use:**
    1. 📁 Upload a PDF document from the sidebar
    2. 🚀 Click **"Process Document"**
    3. 💬 Start asking questions!
    
    **Powered by:**
    - 🦜 LangChain
    - ⚡ Groq (Llama 3.1)
    - 🗄️ ChromaDB
    - 🤗 HuggingFace Embeddings
    """)
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["role"] == "assistant":
                st.caption(f"📄 Sources: pages {message['sources']}")

    if prompt := st.chat_input("Ask a question about your document..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    answer, sources = ask_question(
                        st.session_state.rag_chain,
                        st.session_state.retriever,
                        prompt
                    )
                    st.markdown(answer)
                    st.caption(f"📄 Sources: pages {sources}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")