from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import os
from app.deps import get_agent_service, get_vector_service
from app.service.agent_service import AgentService
from app.service.vector_service import VectorService

router = APIRouter(prefix="/agent", tags=["Agent"])

# 요청/응답 스키마 정의
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    question: str
    ai_message: str

@router.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest, agent_service: AgentService = Depends(get_agent_service)):
    try:
        return agent_service.upstage_chat_agent(request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge")
async def inject_knowledge(vector_service: VectorService = Depends(get_vector_service)):
    # rules.json 파일을 읽어 VectorDB에 적재합니다
    try:
        # 파일 경로 확인
        file_path = "rules.json"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"{file_path} 파일을 찾을 수 없습니다.")

        with open(file_path, "r", encoding="utf-8") as f:
            rules_data = json.load(f)
        
        documents = []
        metadatas = []
        ids = []
        
        for i, rule in enumerate(rules_data):
            # [유연한 매핑] 항목 이름이 달라도 안전하게 가져옵니다.
            # 1. 위치 정보 찾기 (country -> office_name -> location 순서로 시도)
            loc = rule.get('country') or rule.get('office_name') or rule.get('location', 'Unknown')
            
            # 2. 본문 내용 찾기 (description -> content 순서로 시도)
            desc = rule.get('description') or rule.get('content', '')
            
            # 3. 저장할 텍스트 구성
            content = f"{loc} 지사 규정: {desc}"
            
            # 4. 메타데이터 구성 (description과 content를 제외한 모든 항목 포함)
            metadata = {k: v for k, v in rule.items() if k not in ['description', 'content']}
            metadata.update({"category": "office_rule", "location": loc})
            
            documents.append(content)
            metadatas.append(metadata)
            ids.append(f"rule_{i}")
        
        # 지식 저장 실행
        vector_service.save_knowledge(documents, metadatas, ids)
        return {"status": "success", "message": f"{len(documents)}개의 규정이 지식 베이스에 추가되었습니다."}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="rules.json 파일 형식이 올바른 JSON이 아닙니다.")
    except Exception as e:
        # 상세 에러 로그 출력 (도커 로그 확인용)
        print(f"Indexing Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"지식 주입 중 오류 발생: {str(e)}")