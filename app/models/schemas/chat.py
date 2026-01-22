from pydantic import BaseModel

class ChatRequest(BaseModel):
    prompt: str

# [Step 1 수정] OpenAI/Upstage가 요구하는 정확한 중첩 구조입니다.
TIME_TOOL_SCHEMA = {
    "type": "function",
    "function": {  # <--- 이 'function' 키가 반드시 있어야 합니다!
        "name": "get_current_time",
        "description": "Retrieves current time for the given timezone.",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "타임존 (예: Asia/Seoul)",
                    "enum": [
                        "Asia/Seoul", "Asia/Tokyo", "Asia/Shanghai", "Asia/Singapore", 
                        "Asia/Dubai", "Europe/London", "Europe/Paris", "Europe/Berlin", 
                        "Europe/Moscow", "America/New_York", "America/Chicago", 
                        "America/Los_Angeles", "America/Vancouver", "America/Sao_Paulo", 
                        "Australia/Sydney", "Pacific/Auckland", "Asia/Kolkata", 
                        "Asia/Bangkok", "Africa/Johannesburg", "Pacific/Honolulu"
                    ]
                }
            },
            "required": ["timezone"],
            "additionalProperties": False
        },
        "strict": False  # strict 옵션도 function 안에 위치합니다.
    }
}