import requests
import json

class TimeService:
    def __init__(self):
        self.base_url = "http://worldtimeapi.org/api/timezone"

    def get_current_time(self, timezone: str) -> str:
        
        try:
            response = requests.get(f"{self.base_url}/{timezone}")
            response.raise_for_status()
            data = response.json()
            
            return json.dumps({
                "datetime": data.get("datetime"),
                "timezone": data.get("timezone")
            })
        except Exception as e:
            return json.dumps({"error": str(e)})