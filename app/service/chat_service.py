import json
from app.repository.client.upstage_client import UpstageClient
from app.service.time_service import TimeService

class ChatService:
    def __init__(self, upstage_client: UpstageClient, time_service: TimeService):
        self.client = upstage_client
        self.time_service = time_service

    def upstage_chat_function_calling(self, prompt: str):
        
        messages = [{"role": "user", "content": prompt}]
        response = self.client.chat_with_tools(prompt)
        message = response.choices[0].message

        
        if message.tool_calls:
            
            messages.append(message)

            for tool_call in message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                timezone = args.get("timezone")
                
                
                time_info = self.time_service.get_current_time(timezone)
                
                
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": "get_current_time",
                    "content": time_info,
                })

            
            final_response = self.client.client.chat.completions.create(
                model="solar-pro2",
                messages=messages
            )
            return {"ai_message": final_response.choices[0].message.content}
        
        return {"ai_message": message.content}