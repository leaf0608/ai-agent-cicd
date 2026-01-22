from typing import List, Dict, Any
from chromadb import Collection

class ChromaDBRepository:
    def __init__(self, collection: Collection):
        self.collection = collection

    def add_documents(self, ids: List[str], documents: List[str], embeddings: List[List[float]], metadatas: List[Dict]):
        # 벡터 저장소에 문서와 임베딩 데이터를 추가합니다 [cite: 631, 634-639]
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def query(self, query_embeddings: List[List[float]], n_results: int = 5):
        # 질문 임베딩과 가장 유사한 문서를 검색합니다 [cite: 632, 640-642]
        return self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )