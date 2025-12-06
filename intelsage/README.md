# intel_doc_sage_console

Quick setup
 - Copy `../.env.example` to `../.env` (one directory up from this README) and fill in your own API keys.
 - Do NOT commit `../.env` — this file is already ignored by `.gitignore`.

Example (PowerShell):

```powershell
Set-Location -Path "d:\Project"
Copy-Item -Path .env.example -Destination .env -Force
notepad .env  # edit with your API keys
```

If you are contributing or running the project from a clone
 - Create your own `.env` from `.env.example` and populate values.
 - Use provider consoles (Google Cloud, Pinecone) to obtain keys and keep them private.

CI / GitHub
 - For GitHub Actions, store secrets in the repository settings (`Settings -> Secrets and variables -> Actions`) and reference them in the workflow.

If a secret was committed accidentally
 - Immediately rotate/regenerate the exposed keys in their provider consoles.
 - Remove the secret from the repo history (if the repository has already been initialized and pushed). Two common approaches:

 1) Remove from current commit and stop tracking:

 ```powershell
 Set-Location -Path "C:\path\to\repo"
 git rm --cached .env
 git commit -m "Remove .env from repository"
 git push
 ```

 2) Purge from history (more thorough) — recommended if the secret was pushed to a remote. Use `git filter-repo` or the BFG Repo-Cleaner. Example with BFG:

 ```powershell
 # install BFG (Java required) then run locally
 bfg --delete-files .env
 git reflog expire --expire=now --all
 git gc --prune=now --aggressive
 git push --force
 ```

Notes
 - `.env.example` contains only variable names and is safe to commit.
 - Always rotate (regenerate) secrets that have been exposed in a repo — deletion from git history is not a substitute for rotation.
 - If you want, I can add a `CONTRIBUTING.md` snippet, a setup script, or automate environment checks.
