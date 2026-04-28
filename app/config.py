import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_index: str = os.getenv("PINECONE_INDEX", "codesentinel")
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    webhook_secret: str = os.getenv("WEBHOOK_SECRET", "secret")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")


settings = Settings()