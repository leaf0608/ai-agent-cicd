from typing import List, Dict, Any
from app.repository.vector_repo import ChromaDBRepository
from app.service.embedding_service import EmbeddingService

class VectorService:
    def __init__(self, vector_repository: ChromaDBRepository, embedding_service: EmbeddingService):
        self.vector_repository = vector_repository
        self.embedding_service = embedding_service

    def save_knowledge(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        # 지식을 임베딩하여 DB에 저장합니다 (Indexing 과정) [cite: 654, 658]
        embeddings = self.embedding_service.create_embeddings(documents)
        self.vector_repository.add_documents(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        # 질문을 임베딩하고 가장 유사한 지식을 검색합니다 (Retrieval 과정) [cite: 532, 728]
        query_embedding = self.embedding_service.create_embeddings([query])[0]
        results = self.vector_repository.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        # 강의 자료의 구조에 맞춰 결과 반환 [cite: 742-746]
        return {
            "documents": results["documents"][0],
            "metadatas": results["metadatas"][0],
            "distances": results["distances"][0]
        }