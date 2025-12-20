import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rag_pipeline import SimpleRAG

st.set_page_config(
    page_title="Sanskrit RAG",
    layout="wide"
)

st.markdown("""
<style>
.big-title {
    font-size: 3rem;
    color: #FF6B35;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)
@st.cache_resource
def get_rag_system():
    try:
        rag = SimpleRAG()
        return rag, None
    except Exception as e:
        return None, str(e)
def main():
    
    st.markdown('<h1 class="big-title">Sanskrit RAG System</h1>', 
                unsafe_allow_html=True)
    
    rag, error = get_rag_system()
    
    if error:
        st.error(f"Error: {error}")

    rag.setup_database()
    doc_count = rag.collection.count()
    
    if doc_count == 0:
        st.warning("Documents not indexed yet")
        
        if st.button("Index Documents Now", type="primary"):
            with st.spinner("Indexing... Please wait..."):
                rag.index_documents()
            st.success("Indexing complete")
            st.rerun()
        return
    
    st.success(f"System ready ({doc_count} chunks indexed)")
    
    st.subheader("Ask Your Question")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        question = st.text_input(
            "Question",
            placeholder="e.g., कालीदासः कः आसीत्?",
            label_visibility="collapsed"
        )
    
    with col2:
        search_btn = st.button("Search", type="primary", use_container_width=True)
   
    if search_btn and question:
        with st.spinner("generating answer..."):
            try:
                result = rag.query(question)
                
                st.subheader("Answer")
                st.markdown(f'{result["answer"]}', 
                           unsafe_allow_html=True)
                
                with st.expander("View Context Used"):
                    for i, chunk in enumerate(result['context_chunks'], 1):
                        st.markdown(f"**Context {i}:**")
                        st.text(chunk[:300] + "...")
                        st.markdown("")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    elif search_btn:
        st.warning("Please enter a question")

if __name__ == "__main__":
    main()