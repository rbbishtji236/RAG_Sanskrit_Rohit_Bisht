import os
from pathlib import Path
from dotenv import load_dotenv
from docx import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
#from langchain.prompts import PromptTemplate
from sentence_transformers import SentenceTransformer
import chromadb

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DOCS_PATH = Path(__file__).parent.parent / "data" / "Rag-docs.docx"
DB_PATH = Path(__file__).parent.parent / "data" / "vector_db"

EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
LLM_MODEL = "gemini-3-flash-preview"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 3

class SimpleRAG:
    def __init__(self):
        if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_api_key_here":
            raise ValueError(
                "Please add your correct Google API key "
                
            )
        self.embedding_model = None
        self.llm = None
        self.vector_db = None
        self.collection = None
    
    def load_document(self):

        if not DOCS_PATH.exists():
            raise FileNotFoundError(f"Document not found: {DOCS_PATH}")
        
        doc = Document(DOCS_PATH)
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text.strip())
        
        text = "\n\n".join(full_text)
        
        print(f"Loaded {len(text)} characters")
        return text
    def split_text(self, text):
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", "।", "॥", " "]
        )
        chunks = splitter.split_text(text)
        print(f"Created {len(chunks)} chunks")
        return chunks
    
    def setup_embeddings(self):
        
        if self.embedding_model is None:
            print(f"\nLoading embedding model...")
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    
    def create_embeddings(self, chunks):

        self.setup_embeddings()
        embeddings = self.embedding_model.encode(chunks, show_progress_bar=True)
        
        return embeddings
   
    def setup_database(self):
        
        os.makedirs(DB_PATH, exist_ok=True)
        
        self.vector_db = chromadb.PersistentClient(path=str(DB_PATH))
        try:
            self.collection = self.vector_db.get_collection("sanskrit_docs")
            print(f"Loaded existing database ({self.collection.count()} docs)")
        except:
            self.collection = self.vector_db.create_collection("sanskrit_docs")
            print(f"Created new database")
    
    def store_embeddings(self, chunks, embeddings):
        print(f"\nStoring in database...")
        
        self.setup_database()
        
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        self.collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings.tolist()
        )
        
        print(f"Stored {len(chunks)} chunks")
    
    def index_documents(self):
        print("\nINDEXING DOCUMENTS")
        
        self.setup_database()
        if self.collection.count() > 0:
            print(f"\nAlready indexed ({self.collection.count()} chunks)")
            return
        
        text = self.load_document()           
        chunks = self.split_text(text)      
        embeddings = self.create_embeddings(chunks)  
        self.store_embeddings(chunks, embeddings)    
       
    def search(self, question):
        print(f"\nSearching for: {question}")
        
        self.setup_database()
        self.setup_embeddings()
        
        question_embedding = self.embedding_model.encode(question)
        
        results = self.collection.query(
            query_embeddings=[question_embedding.tolist()],
            n_results=TOP_K
        )
        
        chunks = results['documents'][0] if results['documents'] else []
        
        print(f"Found {len(chunks)} relevant chunks")
        return chunks
    
    def setup_llm(self):
        if self.llm is None:
            self.llm = ChatGoogleGenerativeAI(
                model=LLM_MODEL,
                google_api_key=GOOGLE_API_KEY,
                temperature=0.7
            )
            print(f"Gemini ready")
    
    def generate_answer(self, question, context_chunks):
        print(f"\nGenerating answer..")
        
        self.setup_llm()
        
        context = "\n\n".join([f"Context {i+1}:\n{chunk}" 
                              for i, chunk in enumerate(context_chunks)])
        
#         prompt = f"""You are a helpful assistant for Sanskrit documents.
# Use the context below to answer the question. If you cannot answer from the context, say so.

# Context:
# {context}

# Question: {question}

# Answer:"""
        
        prompt = f"""You are an expert in Sanskrit literature and stories.

Below are relevant excerpts from Sanskrit documents. Read them carefully and answer the question in a natural, flowing way.

IMPORTANT INSTRUCTIONS:
- Synthesize information from all excerpts into ONE coherent answer
- Do NOT mention "Context 1", "Context 2", etc. in your answer
- Write as if you naturally know this information
- Provide answer in Sanskrit first , then English translation in parentheses
- if not find answer from the context then directly tell "answer is not found in the provided context ". don't guess assuptions.

Relevant excerpts:
{context}

Question: {question}

Answer naturally:"""
        
        response = self.llm.invoke(prompt)
        answer = response.text
        
        
        return answer
    
    def query(self, question):
        
        context_chunks = self.search(question)
        
        answer = self.generate_answer(question, context_chunks)
        
        return {
            'question': question,
            'answer': answer,
            'context_chunks': context_chunks
        }

def main():
    
    rag = SimpleRAG()
    rag.index_documents()

    question = "कालीदासः कः आसीत्?"
    result = rag.query(question)
    
    print(f"\nAnswer:\n{result['answer']}")


if __name__ == "__main__":
    main()