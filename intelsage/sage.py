import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai  
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import time
import os

# Load environment variables from a .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # If python-dotenv isn't installed, environment variables must be set externally
    pass

st.set_page_config(
    page_title="IntelSage",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
<style>
    .main-title {font-size: 3rem; color: #4F8BF9; font-weight: 800;}
    .sub-title {font-size: 1.2rem; color: #555;}
    .stChatMessage {border-radius: 12px; border: 1px solid #f0f0f0; padding: 12px;}
</style>
""", unsafe_allow_html=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not GOOGLE_API_KEY:
    st.warning("GOOGLE_API_KEY not set in environment. GenAI calls may fail.")

if not PINECONE_API_KEY:
    st.warning("PINECONE_API_KEY not set in environment. Pinecone calls may fail.")

genai.configure(api_key=GOOGLE_API_KEY)

def get_working_model():
    try:
        all_models = list(genai.list_models())
        text_models = [m for m in all_models if 'generateContent' in m.supported_generation_methods]
        model_names = [m.name for m in text_models]
        
        if 'models/gemini-1.5-flash' in model_names:
            return genai.GenerativeModel('gemini-1.5-flash')
        elif 'models/gemini-pro' in model_names:
            return genai.GenerativeModel('gemini-pro')
        elif text_models:
            return genai.GenerativeModel(text_models[0].name)
        else:
            return None
    except:
        return genai.GenerativeModel('gemini-pro')

model = get_working_model()

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("sage-intel")

@st.cache_resource
def load_model():
    return SentenceTransformer("./my_model")

embedder = load_model()

def extract_text_preview(pdf_file, current_model):
    reader = PdfReader(pdf_file)
    text = ""
    
    model_name = current_model.model_name if hasattr(current_model, 'model_name') else ""
    
    if "gemini-1.5-flash" in model_name:
        pages_to_read = reader.pages
    else:
        pages_to_read = reader.pages[:10]

    for page in pages_to_read: 
        extracted = page.extract_text()
        if extracted:
            text += extracted.replace('\n', ' ')
            
    return text

def extract_all_text(pdf_file):
    reader = PdfReader(pdf_file)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text.replace('\n', ' ').strip())
        else:
            pages.append("")
    return pages

with st.sidebar:
    st.header("📂 Document Hub")
    
    st.warning("⚠️ Old files stay in memory until you delete them.")
    if st.button("🗑️ Reset Database (Delete All)", type="primary"):
        try:
            index.delete(delete_all=True)
            st.success("Database Wiped Clean! Upload new files now.")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.error(f"Error resetting: {e}")

    st.divider()
    
    uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("🚀 Process Documents"):
            progress_bar = st.progress(0)
            total_files = len(uploaded_files)
            
            for idx, uploaded_file in enumerate(uploaded_files):
                pages = extract_all_text(uploaded_file)
                for i, text in enumerate(pages):        
                    if not text.strip(): continue
                    vector = embedder.encode(text).tolist()
                    
                    summary = text[:200] + "..." 

                    index.upsert(vectors=[{
                        "id": f"{uploaded_file.name}-page{i+1}",
                        "values": vector,
                        "metadata": {"summary": summary, "full_text": text} 
                    }])
                progress_bar.progress((idx + 1) / total_files)
            st.toast("✅ IntelSage Processing Complete!")

    st.divider()

    if uploaded_files and st.button("📝 Summarize All Files"):
        with st.spinner("IntelSage is synthesizing..."):
            combined_text = ""
            for pdf in uploaded_files:
                preview = extract_text_preview(pdf, model)
                combined_text += f"\n--- File: {pdf.name} ---\n{preview}\n"
            
            try:
                response = model.generate_content(
                    f"Analyze these documents and write a detailed collective summary:\n{combined_text}"
                )
                st.info("### 📑 Collective Summary")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

st.markdown('<div class="main-title">🧠 IntelSage</div>', unsafe_allow_html=True)
st.caption("Advanced Document Analysis by Team Akay")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar_icon = "👤" if message["role"] == "user" else "🧠"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

if query := st.chat_input("Ask IntelSage about your documents..."):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user", avatar="👤"):
        st.markdown(query)

    if model:
        with st.chat_message("assistant", avatar="🧠"):
            with st.spinner("IntelSage is reading..."):
                query_vector = embedder.encode(query).tolist()
                
                results = index.query(vector=query_vector, top_k=30, include_metadata=True)
                
                context_data = []
                sources = []
                for match in results.matches:
                    text = match['metadata'].get('full_text', '')
                    doc_id = match['id']
                    context_data.append(f"Source ({doc_id}):\n{text}")
                    sources.append(doc_id)
                
                full_context = "\n\n".join(context_data) 
                
                prompt = f"""
                You are IntelSage, an expert Professor. Answer the question using the provided context notes.
                If the answer is found, explain it in detail.
                
                Context:
                {full_context}
                
                Question: {query}
                """
                
                try:
                    response = model.generate_content(prompt)
                    answer = response.text
                    
                    st.markdown(answer)
                    
                    with st.expander("📚 View Sources"):
                        for src in sources:
                            st.caption(f"• {src}")
                    
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.error("IntelSage could not connect to Google AI.")