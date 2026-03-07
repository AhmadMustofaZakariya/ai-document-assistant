---
title: AI Document Assistant
emoji: 📄
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 📄 AI Document Assistant

An intelligent document assistant powered by RAG (Retrieval-Augmented Generation) that allows you to upload PDF documents and ask questions about their content in natural language.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![LangChain](https://img.shields.io/badge/LangChain-latest-green)
![Streamlit](https://img.shields.io/badge/Streamlit-latest-red)
![Groq](https://img.shields.io/badge/Groq-Llama3.1-orange)

## 🚀 Live Demo
[▶️ Try it on Streamlit Cloud](https://ai-document-assistant-de4l28z4ihph4zdwj8fr3x.streamlit.app)

---

## ✨ Features
- 📁 Upload any PDF document
- 💬 Chat with your document in natural language
- 🔍 Accurate answers based strictly on document content
- 📄 Source page references for every answer
- 🌐 Supports both English and Indonesian questions
- 🔄 Switch documents anytime without refreshing

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **Framework** | LangChain |
| **LLM** | Groq (Llama 3.1 8B) - Free |
| **Embedding** | HuggingFace `all-MiniLM-L6-v2` |
| **Vector DB** | ChromaDB |
| **UI** | Streamlit |
| **PDF Parsing** | PyPDF |

---

## 🔄 RAG Pipeline

```
📄 PDF Upload
     ↓
📥 Document Loader (PyPDF)
     ↓
✂️ Text Chunking (chunk_size=1000, overlap=100)
     ↓
🔢 Embedding (HuggingFace sentence-transformers)
     ↓
🗄️ Vector Store (ChromaDB)
     ↓
❓ User Query → Similarity Search → Top 3 Chunks
     ↓
🤖 LLM (Groq/Llama3.1) → Answer + Sources
```

---

## 📁 Project Structure

```
ai-document-assistant/
│
├── app.py                  # Main Streamlit UI
├── requirements.txt        # Dependencies
├── .env                    # API Keys (not committed)
├── .gitignore
│
└── src/
    ├── document_loader.py  # PDF loading
    ├── chunker.py          # Text chunking
    ├── embedder.py         # Embedding + VectorDB
    └── rag_chain.py        # RAG pipeline + LLM
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-document-assistant.git
cd ai-document-assistant
```

### 2. Create virtual environment
```bash
conda create -n rag_env python=3.11
conda activate rag_env
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup environment variables
Create a `.env` file in the root directory:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get your free Groq API key at [groq.com](https://groq.com)

### 5. Run the app
```bash
streamlit run app.py
```

---

## 🧪 Testing Results

| Test Type | Question | Result |
|---|---|---|
| ✅ Positive | "What is the offside rule?" | Accurate answer with sources |
| ✅ Positive | "How many players in a football team?" | "Maximum 11 players" |
| ✅ Negative | "What is the NBA rules?" | "Cannot find answer in document" |
| ✅ Edge Case | "Tell me everything about football" | General summary from context |
| ✅ Boundary | "List all offences in football" | Partial list with honest disclaimer |

---

## 🔑 Key Design Decisions

- **Chunk size 1000, overlap 100** → optimal for legal/rule documents
- **k=3 retrieval** → balance between context and token efficiency  
- **Temperature 0.2** → low temperature for factual accuracy
- **In-memory VectorDB** → no persistence needed for demo deployment
- **Prompt engineering** → strict instruction to not hallucinate beyond context

---

## 📝 Lessons Learned

- RAG accuracy heavily depends on chunk size and overlap configuration
- PDF parsing can introduce artifacts (headers, footers) that affect chunk quality
- Filtering chunks shorter than 50 characters significantly improves retrieval quality
- LLM temperature should be low (0.1-0.3) for document Q&A tasks

---

## 👨‍💻 Author
**Ahmad Mustofa Z**  
Hacktiv8 Data Science Bootcamp - Phase 1 Project