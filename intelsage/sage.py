import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from PIL import Image
import time
import os
import io
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv() 

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
    .card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #e0e0e0;
        text-align: center;
        margin-bottom: 10px;
    }
    .card h4 { color: #4F8BF9; margin: 0; padding-bottom: 10px; }
    .card p { color: #666; font-size: 0.9rem; margin: 0; }
</style>
""", unsafe_allow_html=True)

# API Configuration 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not GOOGLE_API_KEY:
    st.error(" GOOGLE_API_KEY not found. Please set it in your .env file.")

if not PINECONE_API_KEY:
    st.error(" PINECONE_API_KEY not found. Please set it in your .env file.")

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
    if os.path.exists("./my_model"):
        return SentenceTransformer("./my_model")
    else:
        st.error(" Error: 'my_model' folder is missing! Please run 'download_model.py' first.")
        st.stop()

embedder = load_model()

def extract_text_from_image(image_file):
    try:
        img = Image.open(image_file)
        vision_model = genai.GenerativeModel('gemini-1.5-flash')
        response = vision_model.generate_content(["Transcribe the text in this image exactly as it appears.", img])
        return response.text
    except Exception as e:
        st.error(f"Image processing error: {e}")
        return ""

def extract_text_preview(file):
    file_type = file.type
    
    if file_type == "application/pdf":
        reader = PdfReader(file)
        text = ""
        for page in reader.pages[:5]: 
            extracted = page.extract_text()
            if extracted:
                text += extracted.replace('\n', ' ')
        return text[:5000]
    elif file_type.startswith('image/'):
        return extract_text_from_image(file)[:5000]
    elif file_type == "text/plain":
        file.seek(0)
        return file.read().decode("utf-8")[:5000]
    else:
        return f"File format not fully supported: {file_type}"

def extract_all_text(file):
    pages = []
    file_type = file.type

    if file_type == "application/pdf":
        reader = PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text.replace('\n', ' ').strip())
            else:
                pages.append("")
    elif file_type.startswith('image/'):
        text = extract_text_from_image(file)
        if text:
            pages.append(text.strip())
    elif file_type == "text/plain":
        file.seek(0)
        text = file.read().decode("utf-8")
        if text:
            pages.append(text.strip())
            
    return pages

with st.sidebar:
    st.header("📂 Document Hub")
    
    st.warning("⚠️ Warning: Pressing Reset will permanently wipe your Pinecone database.")
    
    if st.button("🗑️ Reset Database (Delete All)", type="primary"):
        try:
            index.delete(delete_all=True)
            st.success("Database Wiped Clean!")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            if "Not Found" in str(e) or "Namespace not found" in str(e):
                 st.success("Database is already clean.")
                 time.sleep(2)
                 st.rerun()
            else:
                st.error(f"Error resetting: {e}")

    st.divider()

    uploaded_files = st.file_uploader(
        "Upload Documents (PDF, Text, or Images)", 
        type=["pdf", "txt", "png", "jpg", "jpeg"], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("⚡ Process Documents"):
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
            for file in uploaded_files:
                preview = extract_text_preview(file)
                combined_text += f"\n--- File: {file.name} ---\n{preview}\n"
            
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

# Main Chat Interface
st.markdown('<div class="main-title">🧠 IntelSage</div>', unsafe_allow_html=True)
st.caption("Advanced Document Analysis by Team Akay")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Hero Section Logic
if not st.session_state.messages:
    st.markdown("### 👋 Welcome to your Knowledge Base")
    st.markdown("Upload PDFs, Text, or Images (OCR) on the left, then ask questions below. Here is what I can do:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h4>📑 Summarize</h4>
            <p>Get quick overviews of long documents instantly.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="card">
            <h4>🔍 Search</h4>
            <p>Find specific details across multiple files.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="card">
            <h4>💡 Analyze</h4>
            <p>Extract insights and connect dots between papers.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()

# Display Chat Messages
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