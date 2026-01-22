from fastapi import Depends
from app.repository.client.upstage_client import UpstageClient
from app.service.chat_service import ChatService
from app.service.time_service import TimeService
from app.core.db import get_chroma_collection
from app.repository.vector_repo import ChromaDBRepository
from app.service.embedding_service import EmbeddingService
from app.service.vector_service import VectorService
from app.service.agent_service import AgentService
from app.repository.client.upstage_client import UpstageClient


upstage_client = UpstageClient()

def get_upstage_client() -> UpstageClient:
    return upstage_client

def get_time_service() -> TimeService:
    return TimeService()

def get_chat_service(
    upstage_client: UpstageClient = Depends(get_upstage_client),
    time_service: TimeService = Depends(get_time_service)
) -> ChatService:
    
    return ChatService(upstage_client, time_service)

def get_vector_service():
    collection = get_chroma_collection()
    repository = ChromaDBRepository(collection)
    embedding_service = EmbeddingService()
    return VectorService(repository, embedding_service)

def get_agent_service():
    # 1번 과제에서 만든 UpstageClient와 TimeService를 재사용합니다
    upstage_client = UpstageClient()
    time_service = TimeService()
    
    # 방금 만든 VectorService를 가져옵니다
    vector_service = get_vector_service()
    
    return AgentService(upstage_client, time_service, vector_service)