# [1단계] 빌더 스테이지
FROM python:3.12-slim AS builder
WORKDIR /app

# 빌드에 필요한 도구와 uv 설치
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && \
    pip install --no-cache-dir uv

# 의존성 파일 복사 및 설치
COPY pyproject.toml uv.lock ./
RUN uv sync --no-cache

# [2단계] 실행 스테이지
FROM python:3.12-slim
WORKDIR /app

# 빌더에서 생성된 가상환경 폴더 전체를 복사
COPY --from=builder /app/.venv /app/.venv
# 소스 코드 전체 복사
COPY . .

# [핵심] 가상환경의 실행 파일 경로를 환경 변수에 추가합니다.
# 이렇게 하면 'uv run' 없이도 설치된 패키지들을 바로 사용할 수 있습니다.
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# 'uv'를 찾지 않고, 가상환경에 이미 설치된 uvicorn을 바로 실행합니다.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8800"]