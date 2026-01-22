from openai import OpenAI
import os
from typing import List

class EmbeddingService:
    def __init__(self):
        # Upstage API 설정을 초기화합니다 [cite: 675]
        self.client = OpenAI(
            api_key=os.getenv("UPSTAGE_API_KEY"),
            base_url="https://api.upstage.ai/v1"
        )

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        # 텍스트 리스트를 벡터 리스트로 변환합니다 [cite: 676]
        try:
            response = self.client.embeddings.create(
                model="solar-embedding-1-large-query", # [cite: 679]
                input=texts
            )
            return [embedding.embedding for embedding in response.data] # [cite: 680]
        except Exception as e:
            raise RuntimeError(f"임베딩 생성 실패: {str(e)}") # [cite: 681]