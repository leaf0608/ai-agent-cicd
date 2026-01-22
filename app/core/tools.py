import json

from openai import OpenAI


def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if unit is None:
        unit = "fahrenheit"

    if "seoul" in location.lower():
        return json.dumps({"location": "Seoul", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps(
            {"location": "San Francisco", "temperature": "72", "unit": unit}
        )
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})



# Step 2: Send the query and available functions to the model
def run_conversation(client: OpenAI):
    messages = [
        {
            "role": "user",
            # "content": "What's the weather like in San Francisco, Seoul, and Paris?",
            "content": "한국에 서울, 경기도 성남 날씨는 어때?",
        }
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        # "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                        "unit": {"type": "string", "enum": ["celsius"]},
                    },
                    "required": ["location"],
                },
            },
        }
    ]

    # Step 3: Check if the model has requested a function call
    # The model identifies that the query requires external data (e.g., real-time weather) and decides to call a relevant function, such as a weather API.
    response = client.chat.completions.create(
        model="solar-pro2",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Step 4: Execute the function call
    # The JSON response from the model may not always be valid, so handle errors appropriately
    if tool_calls:
        available_functions = {
            "get_current_weather": get_current_weather,
        }  # You can define multiple functions here as needed
        messages.append(response_message)  # Add the assistant's reply to the conversation history

        # Step 5: Process each function call and provide the results to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                location=function_args.get("location"),
                unit=function_args.get("unit"),
            )  # Call the function with the provided arguments
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # Append the function response to the conversation history

        # Step 6: Generate a new response from the model using the updated conversation history
        second_response = client.chat.completions.create(
            model="solar-pro2",
            messages=messages,
        )
        return second_response  # Return the final response from the model
    return response_message
