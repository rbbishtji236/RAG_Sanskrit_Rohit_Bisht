
# Sanskrit RAG System

A Retrieval-Augmented Generation system for Sanskrit documents.

---

## Project Structure

```
RAG_Sanskrit/
│
├── code/
│   ├── rag_pipeline.py    #  ALL RAG logic 
│   └── streamlit.py           # Streamlit web interface
│
├── data/
│   ├── Rag-docs.docx    # Sanskrit document (INPUT)
│   └── vector_db/       # Database (created after indexing)
│
├── .env                 # Your API key here
└── requirements.txt     # Dependencies
```

## Quick Start

### Step 1: Install
```bash
pip install -r requirements.txt
```

### Step 2: Add API Key
Edit `.env` file:
```
GOOGLE_API_KEY=your_actual_key_here
```
Get free key: https://makersuite.google.com/app/apikey

### Step 3: Run
```bash
cd code
streamlit run streamlit.py
```

---

## How It Works

### The `rag_pipeline.py` file has everything:

1. **Load** → Read Rag-docs.docx from docs folder
2. **Split** → Break into chunks
3. **Embed** → Convert to numbers (multilingual-e5-small)
4. **Store** → Save in ChromaDB
5. **Search** → Find relevant chunks
6. **Generate** → Create answer (Gemini)

### Simple Functions:
```python
rag = SimpleRAG()              # Create system
rag.index_documents()          # Index once
result = rag.query("question") # Ask questions
```

---

## Understanding rag_system.py

### Configuration (Top of file):
```python
DOCS_PATH = "docs/Rag-docs.docx"  # Document location
CHUNK_SIZE = 500                   # Size of chunks
TOP_K = 3                          # Results to retrieve
```

### Main Functions:
```python
load_document()       # Reads DOCX file
split_text()          # Makes chunks
create_embeddings()   # Converts to numbers
store_embeddings()    # Saves in database
search()              # Finds relevant chunks
generate_answer()     # Creates answer
query()               # Does everything!
```

### All in Order!
Each function does ONE thing clearly.

---

## Using the Web Interface

```bash
streamlit run streamlit.py
```

---
