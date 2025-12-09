IntelDoc Sage Console — Final Evaluation README
This README is prepared for the Dev_Or_Die final evaluation. It documents the project purpose, features, architecture, setup, AI/ML integrations, error handling, team responsibilities, and future improvements. Use it as the primary reference for your evaluation.
Project Overview
	•	Name: IntelDoc Sage Console (IntelSage)
	•	Short description: A Streamlit web app that ingests PDFs, text files and images (OCR), embeds document content with a local SentenceTransformer model, stores vectors in Pinecone, and uses Google Generative AI (Gemini) to synthesize answers and summaries from retrieved context.
Problem Statement (PS Number)
	•	PS Number: 4
	•	Problem: Quickly extract, search and summarize information from large document sets (PDFs, images, text) to support knowledge discovery and question answering.
Features implemented
	•	Upload multiple documents: PDFs, text, and images.
	•	Text extraction from PDFs (PyPDF2) and images (model-assisted OCR via Google Generative AI).
	•	Local embedding with  sentence-transformers  (model downloaded to  ./my_model ).
	•	Vector storage and retrieval using Pinecone ( sage-intel  index).
	•	Contextual retrieval + LLM-based answer generation using Google Generative AI (Gemini).
	•	Simple UI with Streamlit: file upload, process documents, summarize, and chat-like Q&A.
	•	Pinecone index management: reset/clear database from UI.
Tech Stack used
	•	Python 3.8+
	•	Streamlit (UI)
	•	PyPDF2 (PDF parsing)
	•	Pillow (image handling)
	•	google-generative-ai (Gemini integration)
	•	Pinecone client (vector DB)
	•	sentence-transformers (local embedding model)
	•	huggingface-hub (model download)
	•	python-dotenv (read  .env )
System Architecture / High-level design
	•	User (browser) -> Streamlit UI ( intelsage/sage.py )
	•	Uploaded files -> Extraction layer (PDF/text/image) -> raw text
	•	Embedding layer -> local SentenceTransformer (in  ./my_model ) -> vectors
	•	Vector store -> Pinecone index  sage-intel 
	•	Retrieval -> nearest neighbors -> assemble context
	•	LLM layer -> Google Generative AI (Gemini) with context -> final response
Diagram (textual):
User -> Streamlit UI -> Extraction -> Embedding -> Pinecone -> Retrieval -> Gemini -> User
API documentation (where applicable)
	•	Google Generative AI: configured from environment variable  GOOGLE_API_KEY . The app calls  genai.list_models()  and  model.generate_content() .
	•	Pinecone: configured from  PINECONE_API_KEY . The app uses  Pinecone(api_key=...) ,  pc.Index("sage-intel") ,  index.upsert()  and  index.query() .
	•	SentenceTransformer: local model loaded via  SentenceTransformer("./my_model") . If missing, the app stops and prompts to run  download_model.py .
Key code entry points
	•	 intelsage/sage.py  — main Streamlit app. Responsible for UI, file upload, extraction, embedding, Pinecone ops, and LLM calls.
	•	 intelsage/download_model.py  — downloads  sentence-transformers/all-MiniLM-L6-v2  to local  ./my_model .
Setup Instructions (how to run the project locally)
	1.	Clone the repository:
git clone https://github.com/anantmani13/intel_doc_sage_console
Set-Location -Path "d:\Project"  # adjust path as needed
2.	Create and activate a virtual environment (PowerShell):
python -m venv .venv
.\.venv\Scripts\Activate.ps1
	3.	Install dependencies:
pip install --upgrade pip
pip install streamlit PyPDF2 google-generative-ai pinecone-client sentence-transformers pillow python-dotenv huggingface-hub
	4.	Create a  .env  from  .env.example  and fill values (DO NOT commit  .env ):
Copy-Item -Path .env.example -Destination .env -Force
notepad .env
Required variables in  .env :
	•	 GOOGLE_API_KEY  — API key for Google Generative AI
	•	 PINECONE_API_KEY  — Pinecone API key
	5.	Download the local embedding model:
python intelsage/download_model.py
	6.	Run the Streamlit app:
  streamlit run intelsage/sage.py
Open the printed local URL (usually  http://localhost:8501 ) to use the app.
Deployment Link
	•	Local deployment only. Run  streamlit run intelsage/sage.py  to automatically start the app at  http://localhost:8501 . No public deployment required for this Python-based Streamlit project.
Error Handling & Reliability considerations
	•	Missing API Keys: The app checks for  GOOGLE_API_KEY  and  PINECONE_API_KEY  and shows Streamlit errors if missing.
	•	Missing local model:  load_model()  checks for  ./my_model  and stops the app with an error instructing to run  download_model.py .
	•	Pinecone exceptions: UI wraps index delete/upsert/query in try/except and shows descriptive errors.
	•	Rate limits & timeouts: LLM and Pinecone calls can fail on rate limits. Add exponential backoff and retries for production.
	•	Data privacy:  .env  is ignored by  .gitignore . Never commit secrets; rotate compromised keys immediately.
AI/ML Integration details
	•	Embeddings:  sentence-transformers/all-MiniLM-L6-v2  (local) is used to create dense vectors for text passages.
	•	Vector DB: Pinecone used to store and query vectors ( sage-intel  index).
	•	LLM: Google Generative AI (Gemini) used to generate summaries and answers from assembled context.
	•	Workflow: Documents -> text extraction -> chunking (per page) -> embedding -> upsert to Pinecone -> query -> assemble context -> LLM prompt -> answer.
Team members and responsibilities
	•	Anant Mani Dubey — Team Lead, Important inputs and functionality contributions
	•	Karan Patel — Important inputs and functionality contributions
	•	Yogesh Soni — Important inputs and functionality contributions
	•	Adarsh Patel — Important inputs and functionality contributions
Future Improvements
	•	Add chunking and paging strategies for better retrieval (overlap, dynamic sizes).
	•	Add retries/backoff and monitoring for LLM and Pinecone calls.
	•	Add automated tests and CI workflows.
	•	Add Dockerfile for consistent deployment.
	•	Add role-based access and authenticated UI for shared deployments.
Evaluation mapping (how this README addresses evaluation criteria)
	•	UI/UX: Streamlit UI with upload, progress bar, summarize and chat features.
	•	Code quality: Modular  sage.py  functions for extraction, embedding, and LLM calls — documented in this README.
	•	Folder structure:  intelsage/  contains app and helpers; model in  ./my_model .
	•	Functionality & feature completeness: Document ingestion, embedding, storage, retrieval, summarization, and chat.
	•	API usage & integrations: Google Generative AI, Pinecone, HuggingFace model download — documented here.
	•	Deployment: Steps to run locally; add deployment link when available.
	•	Error handling: App-level checks and try/except handling described above.
	•	Git hygiene:  .env  ignored;  .env.example  included; guidelines to remove secrets provided.
Git push troubleshooting (if you cannot push  README.md ) Common reasons you might be unable to push:
	•	Not a git repository in the current path — make sure you are in the repo root (where  .git  is). Check:
Set-Location -Path "d:\Project"
git status
git rev-parse --show-toplevel
	•	No remote configured or wrong remote URL. Check:
git remote -v
•	Authentication failure: you may need to use a GitHub Personal Access Token (PAT) when using HTTPS, or configure SSH keys.
	•	For HTTPS push with PAT (recommended for automation):
git remote set-url origin https://<username>:<PAT>@github.com/<owner>/<repo>.git
git push origin main
•	For SSH, ensure your public key is added to GitHub and remote uses  git@github.com:owner/repo.git .
	•	Branch protection or required reviews: GitHub may block direct pushes to  main . Either create a feature branch, open a Pull Request, and get required approvals, or adjust branch protection in repository settings.
	•	Merge conflicts: If remote changed since your last pull, pull/rebase first:
git pull --rebase origin main
git push origin main
