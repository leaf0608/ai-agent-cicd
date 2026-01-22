import json
import os
from typing import List, Dict, Any
from app.repository.client.upstage_client import UpstageClient
from app.service.time_service import TimeService
from app.service.vector_service import VectorService

class AgentService:
    def __init__(self, upstage_client: UpstageClient, time_service: TimeService, vector_service: VectorService):
        self.client = upstage_client
        self.time_service = time_service
        self.vector_service = vector_service

    # [수정된 부분] 하드코딩 없이 모든 항목을 동적으로 메타데이터로 저장합니다.
    def add_knowledge_from_file(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            rules = json.load(f)

        for item in rules:
            # 1. 'description' 항목을 본문 내용으로 사용합니다.
            content = item.get("description", "")
            
            # 2. 하드코딩 방지: 'description'을 제외한 모든 항목(office_name, country 등)을 
            # 자동으로 메타데이터로 변환합니다.
            metadata = {k: v for k, v in item.items() if k != "description"}

            # 3. VectorDB에 저장 (vector_service에 해당 메서드가 있다고 가정)
            self.vector_service.add_text(
                text=content,
                metadata=metadata
            )
        
        return {"status": "success", "message": f"{len(rules)}개의 지식이 성공적으로 주입되었습니다."}

    def upstage_chat_agent(self, prompt: str):
        # 1. 사용자의 질문을 분석하여 도구(시간 조회)가 필요한지 확인합니다
        messages = [{"role": "user", "content": prompt}]
        response = self.client.chat_with_tools(prompt)
        message = response.choices[0].message

        # 도구 호출이 필요한 경우 (예: 런던 시간 확인)
        if message.tool_calls:
            messages.append(message)
            for tool_call in message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                timezone = args.get("timezone")
                
                # 실시간 시간 데이터 획득
                time_info = self.time_service.get_current_time(timezone)
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": "get_current_time",
                    "content": time_info,
                })

        # 2. VectorDB에서 관련 사내 규정(RAG)을 검색합니다
        search_results = self.vector_service.search(prompt, n_results=2)
        # 검색된 결과가 없을 경우를 대비해 기본값 처리
        context = "\n".join(search_results.get("documents", ["관련 규정을 찾을 수 없습니다."]))

        # 3. 최종 답변 생성 프롬프트 구성
        final_prompt = self._generate_agent_prompt(prompt, context)
        # LLM에게 전달할 마지막 메시지 업데이트
        messages[0]["content"] = final_prompt 

        final_response = self.client.client.chat.completions.create(
            model="solar-pro", # 사용 중인 모델명 확인 필요
            messages=messages
        )
        
        return {
            "question": prompt,
            "ai_message": final_response.choices[0].message.content
        }

    def _generate_agent_prompt(self, query: str, context: str) -> str:
        return f"""당신은 글로벌 협업 가이드 에이전트입니다. 
제공된 [사내 규정]과 검색된 실시간 정보를 바탕으로 사용자의 질문에 답변하세요.

[사내 규정]
{context}

사용자 질문: {query}

답변 시 주의사항:
1. 제공된 [사내 규정]에 명시된 해당 국가/도시의 근무 시간과 점심 시간을 반드시 확인하세요.
2. 실시간 정보로 획득한 현재 현지 시간과 규정을 비교하여 연락 가능 여부를 논리적으로 설명하세요.
3. 만약 점심시간이나 업무 시간 외라면, 현지 시간 기준으로 언제 연락하는 것이 좋을지 제안하세요.
"""