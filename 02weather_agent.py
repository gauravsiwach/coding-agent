 
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import json
 
 
load_dotenv()
client = OpenAI()


def get_weather(city: str):
     return "42 degrees Celsius, sunny"

SYSTEM_PROMPT = """
    You are a helpful AI assistant who is splecialized in resolving user queries.
    You work on start, plan, action and observe mode.

    For the given user query and system tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tools. and based on the tool selection, you perform an action to call the tool.

    wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
        - Follow the output JSON format.
        - Always perform one step at a time and wait for the next input.
        - Carefully analyses the user query.

    Output JSON format:
        {{
            "step": "string",
            "content": "string",
            "function": "The name of the function if step is action",
            "input": "The input parameter for the function"
        }}
        
    Available tools:
        - "get_weather": Takes a city name as a input and return the current weather of the city.

    Example:
        User Query: What is the weather in New York?
        Output: {{"step": "plan", "content": "user is intersted in weather data of new york."}}
        Output: {{"step": "plan", "content": "from the available tools i should call the get_weather"}}
        Output: {{"step": "action", "function": "get_weather", "input": "new york"}}
        Output: {{"step": "observe", "content": "42 degrees Celsius"}}
        Output: {{"step": "output", "content": "The weather for new york to be 42 degrees Celsius."}}
        

"""
response = client.chat.completions.create(
    model="gpt-4.1-mini", 
    response_format={"type": "json_object"},
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},       
        {"role": "user", "content": "What is weather in meerut?"}, 
        {"role": "assistant", "content": json.dumps({"step": "plan", "content": "User wants to know the weather in Meerut."})},        
        {"role": "assistant", "content": json.dumps({"step": "plan", "content": "To provide the weather information for Meerut, I should call the get_weather function with input as Meerut."})},        
        {"role": "assistant", "content": json.dumps({"step": "action", "function": "get_weather", "input": "meerut"})},        
        {"role": "user", "content": json.dumps({"step": "observe", "output": "20"})}, 
        ],
)
print("\n🧠:"+response.choices[0].message.content)