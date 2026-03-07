import streamlit as st
import sys
import os
import tempfile

# Tambahkan src ke path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

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

# ─── HELPER FUNCTIONS ──────────────────────────────────
def save_uploaded_file(uploaded_file):
    """
    Simpan file sementara di memory menggunakan tempfile.
    Tidak simpan ke disk permanen → cocok untuk HuggingFace deployment.
    File temporary otomatis terhapus setelah tidak dipakai.
    """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.write(uploaded_file.getbuffer())
    tmp.close()
    return tmp.name

def process_document(file_path):
    """
    Load, chunk, embed dokumen.
    VectorDB disimpan di memory (persist_directory=None)
    → tidak tersimpan ke disk → cocok untuk HuggingFace deployment.
    """
    with st.spinner("📖 Loading document..."):
        docs = load_document(file_path)
        st.sidebar.caption(f"✅ Loaded {len(docs)} pages")

    with st.spinner("✂️ Chunking document..."):
        chunks = chunk_documents(docs)
        st.sidebar.caption(f"✅ Created {len(chunks)} chunks")

    with st.spinner("🔢 Embedding & building VectorDB..."):
        # persist_directory=None → simpan di memory saja
        vectorstore = create_vectorstore(chunks, persist_directory=None)
        st.sidebar.caption(f"✅ VectorDB ready!")

    return vectorstore

def cleanup_temp_file(file_path):
    """
    Hapus file temporary setelah selesai diproses.
    Penting untuk menjaga memory tetap bersih.
    """
    try:
        os.unlink(file_path)
    except Exception:
        pass

# ─── SESSION STATE ─────────────────────────────────────
# Session state = memory Streamlit selama user membuka app
# Tanpa ini semua variable reset setiap kali user interaksi

if "messages" not in st.session_state:
    st.session_state.messages = []        # riwayat chat

if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None     # RAG chain object

if "retriever" not in st.session_state:
    st.session_state.retriever = None     # retriever object

if "document_processed" not in st.session_state:
    st.session_state.document_processed = False  # status dokumen

if "current_filename" not in st.session_state:
    st.session_state.current_filename = None  # nama file aktif

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
        # Cek apakah file berbeda dari sebelumnya
        is_new_file = uploaded_file.name != st.session_state.current_filename

        if is_new_file:
            st.info(f"📄 New file detected: {uploaded_file.name}")

        if st.button("🚀 Process Document", use_container_width=True):
            try:
                # Step 1: Simpan ke tempfile
                file_path = save_uploaded_file(uploaded_file)

                # Step 2: Proses dokumen
                vectorstore = process_document(file_path)

                # Step 3: Buat RAG chain
                with st.spinner("🤖 Setting up AI..."):
                    rag_chain, retriever = create_rag_chain(vectorstore)

                    # Simpan ke session state
                    st.session_state.rag_chain = rag_chain
                    st.session_state.retriever = retriever
                    st.session_state.document_processed = True
                    st.session_state.current_filename = uploaded_file.name
                    st.session_state.messages = []  # reset chat history

                # Step 4: Cleanup tempfile
                cleanup_temp_file(file_path)

                st.success("✅ Document processed successfully!")

            except Exception as e:
                st.error(f"❌ Error processing document: {str(e)}")

    st.markdown("---")

    # Status indicator
    if st.session_state.document_processed:
        st.success("🟢 AI is ready!")
        st.info(f"📄 Active file:\n{st.session_state.current_filename}")

        # Tombol reset
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
    # Welcome screen
    st.markdown("""
    ### 👋 Welcome to AI Document Assistant!
    
    **How to use:**
    1. 📁 Upload a PDF document from the sidebar on the left
    2. 🚀 Click **"Process Document"** and wait for processing
    3. 💬 Start asking questions about your document!
    
    **Notes:**
    - 📌 Only PDF files are supported
    - ⚡ Processing time depends on document size
    - 🔄 Upload a new document anytime by clicking Reset
    
    **Powered by:**
    - 🦜 LangChain
    - ⚡ Groq (Llama 3.1)
    - 🗄️ ChromaDB
    - 🤗 HuggingFace Embeddings
    """)

else:
    # Tampilkan riwayat chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["role"] == "assistant":
                st.caption(f"📄 Sources: pages {message['sources']}")

    # Chat input
    if prompt := st.chat_input("Ask a question about your document..."):

        # Tampilkan pesan user
        with st.chat_message("user"):
            st.markdown(prompt)

        # Simpan ke history
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        # Generate jawaban
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

                    # Simpan ke history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

                except Exception as e:
                    error_msg = f"❌ Error generating answer: {str(e)}"
                    st.error(error_msg)

