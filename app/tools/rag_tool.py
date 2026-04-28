from langchain.tools import tool


@tool
def search_codebase_context(query: str) -> str:
    """
    Search the indexed codebase for code patterns relevant
    to a query. Use this before reviewing new code to find
    how similar patterns are handled in the existing project,
    detect convention violations, and understand project style.
    Returns the top 5 most relevant code chunks with file paths.
    """
    try:
        from app.rag.indexer import create_index
        from langchain_huggingface import HuggingFaceEmbeddings

        embedder = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        index = create_index()
        vec = embedder.embed_query(query)
        res = index.query(
            vector=vec, top_k=5, include_metadata=True
        )
        if not res.matches:
            return "No relevant codebase context found."
        return "\n\n".join([
            f"[{m.metadata['file']}]\n{m.metadata['chunk']}"
            for m in res.matches
        ])
    except Exception as e:
        return f"Codebase search unavailable: {str(e)}"