import chromadb
import os
from dotenv import load_dotenv

load_dotenv()

class ChromaDBConfig:
    def __init__(self):
        # 환경 변수에서 접속 정보를 읽어옵니다 [cite: 591-594]
        self.host = os.getenv("CHROMA_HOST", "localhost")
        self.port = int(os.getenv("CHROMA_PORT", "8000"))
        self.collection_name = os.getenv("CHROMA_COLLECTION_NAME", "upstage_embeddings")

def get_chroma_client():
    config = ChromaDBConfig()
    # HTTP 방식으로 별도 컨테이너인 ChromaDB 서버에 연결 [cite: 600]
    return chromadb.HttpClient(host=config.host, port=config.port)

def get_chroma_collection(name: str = None):
    config = ChromaDBConfig()
    client = get_chroma_client()
    collection_name = name or config.collection_name
    # 컬렉션이 없으면 생성하고, 있으면 가져옵니다 [cite: 630]
    return client.get_or_create_collection(name=collection_name)