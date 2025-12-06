from huggingface_hub import snapshot_download
print("Downloading model manually...")
# Download model to a specific local folder "my_model"
model_path = snapshot_download(
    repo_id="sentence-transformers/all-MiniLM-L6-v2",
    local_dir="my_model",
    local_dir_use_symlinks=False  
)
print(f" Model successfully downloaded to: {model_path}")   