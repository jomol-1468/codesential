from pinecone import Pinecone, ServerlessSpec
from app.config import settings

pc = Pinecone(api_key=settings.pinecone_api_key)


def create_index():
    existing = pc.list_indexes().names()
    if settings.pinecone_index not in existing:
        pc.create_index(
            name=settings.pinecone_index,
            dimension=384,  # all-MiniLM-L6-v2 dimension
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws", region="us-east-1"
            ),
        )
    return pc.Index(settings.pinecone_index)