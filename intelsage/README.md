# IntelDoc Sage Console

IntelDoc Sage Console (IntelSage) is a lightweight Streamlit app for ingesting PDFs, text files, and images, embedding their content using a local SentenceTransformer model, storing vectors in Pinecone, and querying them with Google Generative AI (Gemini) to produce detailed answers and summaries.

**Quick Start**
- Prerequisites: Python 3.8+ and Git.
- Clone the repo, create a virtual environment, install dependencies, populate your `.env`, download the local embedding model, and run the Streamlit app.

PowerShell example (copy-paste):

```powershell
Set-Location -Path "d:\Project"
# Create (or activate) a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install runtime dependencies
pip install --upgrade pip
pip install streamlit PyPDF2 google-generative-ai pinecone-client sentence-transformers pillow python-dotenv huggingface-hub

# Create a local .env from the example and edit it with your keys
Copy-Item -Path .env.example -Destination .env -Force
notepad .env

# Download the local sentence-transformers model used by the app
python intelsage/download_model.py

# Run the Streamlit app
streamlit run intelsage/sage.py
```

If you prefer `requirements.txt`, you can freeze the installed packages after installing and commit the file for your environment.

**Environment variables**
Create a file named `.env` in the project root (we include `.env.example` with the required keys). The app reads these variables using `python-dotenv`.

- `GOOGLE_API_KEY` — Google Generative AI API key (Gemini)
- `PINECONE_API_KEY` — Pinecone API key

Do NOT commit your `.env` file to source control. This repository already includes `.gitignore` configured to ignore `.env`.

**What the app does**
- Upload PDFs, text files, or images (OCR) through the Streamlit UI.
- Extracts text (PDF via PyPDF2, images via Google Vision/model-based OCR fallback).
- Encodes document text using a local SentenceTransformer model (downloaded to `./my_model`).
- Stores vectors in a Pinecone index named `sage-intel`.
- Answers user queries by retrieving relevant vectors and passing context to Google Generative AI.

**Download model**
The repo includes `intelsage/download_model.py` which uses `huggingface_hub.snapshot_download` to fetch `sentence-transformers/all-MiniLM-L6-v2` into `./my_model`. Run:

```powershell
python intelsage/download_model.py
```

If you prefer a different model, update `repo_id` in that script.

**CI / GitHub Actions**
- For running this project in CI or on GitHub Pages/Cloud, store sensitive values (API keys) as repository secrets in `Settings -> Secrets and variables -> Actions` and reference them in workflows. Do not embed secrets in YAML or commit them to the repo.

**If a secret was committed accidentally**
1. Immediately rotate/regenerate the exposed keys from their provider consoles (Google Cloud, Pinecone).
2. Remove the file from the latest commit and stop tracking it:

```powershell
Set-Location -Path "C:\path\to\repo"
git rm --cached .env
git commit -m "Remove .env from repository"
git push
```

3. If the secret was pushed to a remote and you need to purge it from history, use a history-cleaning tool such as `git filter-repo` or the BFG Repo-Cleaner and then force-push. Example (BFG):

```powershell
# Install BFG (requires Java). Then:
bfg --delete-files .env
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

Note: Deleting from history does NOT replace the secret — you must rotate/regenerate compromised keys.

**Troubleshooting**
- If the app shows an error: `Error: 'my_model' folder is missing! Please run 'download_model.py' first.` — run the `download_model.py` script.
- If `GOOGLE_API_KEY` or `PINECONE_API_KEY` are missing, set them in your local `.env`.
- If Pinecone index operations fail, verify your Pinecone key and index name in the Pinecone console.

**Development & Contribution**
- Keep `.env` out of commits. Prefer `.env.example` to document required variables.
- Add tests or CI workflow snippets under `.github/workflows/` if you want to automate checks.
- If you want, submit a PR to add a `requirements.txt` or `pyproject.toml` for reproducible installs.

**Files of interest**
- `intelsage/sage.py` — Streamlit app (main project UI and logic).
- `intelsage/download_model.py` — script to fetch the local embedding model.
- `.env.example` — template for environment variables.

**License**
This repository does not include a license file. Add a `LICENSE` if you want to make usage terms explicit.

---

If you'd like, I can also:
- Add a `requirements.txt` generated from the environment I used to test the app.
- Add a small PowerShell `setup.ps1` to automate virtualenv creation, `.env` creation from `.env.example`, model download, and dependency installation.
