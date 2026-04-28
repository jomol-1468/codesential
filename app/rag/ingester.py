import os
from langchain.text_splitter import (
    Language, RecursiveCharacterTextSplitter
)
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.rag.indexer import create_index

# Free local model — no API key needed
# dimension=384 for all-MiniLM-L6-v2
embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=800,
    chunk_overlap=100,
)
SKIP = ["__pycache__", ".egg", "venv"]


def index_repo(repo_path: str) -> int:
    index = create_index()
    batch = []
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs
                   if not any(s in d for s in SKIP)]
        for fname in files:
            if not fname.endswith(".py"):
                continue
            path = os.path.join(root, fname)
            try:
                chunks = splitter.split_text(
                    open(path, encoding="utf-8").read()
                )
                if not chunks:
                    continue
                vecs = embedder.embed_documents(chunks)
                batch += [
                    {
                        "id": f"{path}:{i}",
                        "values": v,
                        "metadata": {
                            "file": path,
                            "chunk": chunks[i]
                        },
                    }
                    for i, v in enumerate(vecs)
                ]
            except Exception as e:
                print(f"Skipping {path}: {e}")
    if batch:
        index.upsert(vectors=batch)
    return len(batch)