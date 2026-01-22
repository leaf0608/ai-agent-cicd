import logging
import os
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from openai import OpenAI

# 로깅 및 예외 처리 관련 임포트
from app.logging import init_logging
from app.exceptions import UserNotFoundError, EmailNotAllowedNameExistsError
from app.models.schemas.chat import ChatRequest

# 라우터 임포트 
from app.api.route.user_routers import router as user_router
from app.api.route.chat_router import chat_router
from app.api.route.agent_routers import router as agent_router

# 환경 변수 로드 [cite: 100-103]
load_dotenv()

# 앱 초기화 및 로깅 설정
app = FastAPI(title="Global Collaboration Guide AI Agent")
init_logging()
logger = logging.getLogger(__name__)

# --- [예외 핸들러 섹션] ---

@app.exception_handler(EmailNotAllowedNameExistsError)
async def email_not_allowed_handler(request: Request, exc: EmailNotAllowedNameExistsError):
    logger.exception("Email Not Allowed exception occurred")
    return JSONResponse(
        status_code=409,
        content={"error": "Email Not Allowed", "message": str(exc)}
    )

@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    logger.exception("User Not Found exception occurred")
    return JSONResponse(
        status_code=404,
        content={"error": "User Not Found", "message": str(exc)}
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.exception("Bad Request exception occurred")
    return JSONResponse(
        status_code=400,
        content={"error": "Bad Request", "message": str(exc)}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.exception("HTTP exception occurred")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTP Exception", "message": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception occurred")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "message": "Something went wrong"}
    )

# --- [라우터 등록 섹션] ---
# 중복을 제거하고 필요한 라우터를 순서대로 등록합니다.

app.include_router(user_router)
app.include_router(router=chat_router)
app.include_router(router=agent_router) # AI 에이전트 전용 라우터 (Prefix: /agent)

logger.info("애플리케이션 및 에이전트 서비스 시작")

# --- [기본/테스트 엔드포인트 섹션] ---

@app.get("/")
async def root():
    return {"message": "Global Collaboration Guide AI Agent API is Running"} 

@app.get("/hello")
async def hello():
    return {"message": "Hello FastAPI!"}

@app.post("/query")
async def query_embedding_test(message: ChatRequest):
    """임베딩 생성 테스트를 위한 엔드포인트"""
    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        raise ValueError("UPSTAGE_API_KEY environment variable is required")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.upstage.ai/v1"
    )
    # [cite: 677-680] Upstage 임베딩 모델 호출
    response = client.embeddings.create(
        input=message.prompt,
        model="solar-embedding-1-large-query"
    )

    return response.data[0].embedding