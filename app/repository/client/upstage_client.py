import os
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI


from app.core.tools import run_conversation
from app.models.schemas.chat import ChatRequest, TIME_TOOL_SCHEMA

load_dotenv()

class UpstageClient:
    def __init__(self):
        self.api_key = os.getenv("UPSTAGE_API_KEY")
        if not self.api_key:
            raise ValueError("UPSTAGE_API_KEY environment variable is required")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.upstage.ai/v1"
        )
        self.async_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.upstage.ai/v1"
        )

    def chat_streaming(self, message: ChatRequest):
        stream = self.client.chat.completions.create(
            model="solar-pro2",
            messages=message.prompt,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    async def chat_streaming_async(self, message: ChatRequest):
        stream = await self.async_client.chat.completions.create(
            model="solar-pro2",
            messages=message.prompt,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def chat_with_tools(self, prompt: str):
       
        return self.client.chat.completions.create(
            model="solar-pro2",
            messages=[{"role": "user", "content": prompt}],
            tools=[TIME_TOOL_SCHEMA], 
            tool_choice="auto"        
        )