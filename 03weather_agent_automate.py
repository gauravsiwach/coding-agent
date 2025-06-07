# This code is an example of an AI agent that is resolve the weather realted query on real time, it can also 
# execute the system commands, save information in the file, generate the html page, etc. 
# sample query: 
# What is the weather in New York?
# what is the weather in Mumbai?
# what is the weather in delhi in Fahrenheit?
# what is average of weather in delhi and mumbai?
# what is the weather in New York and mumbai? and write the output in a file named weather.txt
# create a app that tale city name as input and fetch the weather of the city and display it in a html page.

from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import json
import requests
import os
import subprocess
 
load_dotenv()
client = OpenAI()

SAFE_COMMANDS = ["dir", "echo", "type", "mkdir"]

def run_command(command: str):
    if any(command.startswith(cmd) for cmd in SAFE_COMMANDS):
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip()
    return "⚠️ Unsafe command blocked", ""


def get_weather(city: str):
     url = f"https://wttr.in/{city}?format=%C+%t"
     response = requests.get(url)
     if response.status_code == 200:
         return f"weather in {city} is {response.text}."
     
     return "something went wrong while fetching the weather data."


available_tools = {
    "get_weather": get_weather,
    "run_command ": run_command 
}

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
        - Be Careful while executing commonds, make sure you must not executing any harmful commands or that delete the system files.

    Output JSON format:
        {{
            "step": "string",
            "content": "string",
            "function": "The name of the function if step is action",
            "input": "The input parameter for the function"
        }}
        
    Available tools:
        - "get_weather": Takes a city name as a input and return the current weather of the city.
        - "run_command ": Takes a windows command as string input and execute the commond and return the output after executing it.

    Example:
        User Query: What is the weather in New York?
        Output: {{"step": "plan", "content": "user is intersted in weather data of new york."}}
        Output: {{"step": "plan", "content": "from the available tools i should call the get_weather"}}
        Output: {{"step": "action", "function": "get_weather", "input": "new york"}}
        Output: {{"step": "observe", "content": "42 degrees Celsius"}}
        Output: {{"step": "output", "content": "The weather for new york to be 42 degrees Celsius."}}

"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

while True:
    query= input("ask weather related query: ")
    messages.append({"role": "user", "content": query})

    while True:
        response= client.chat.completions.create(
            model="gpt-4.1-mini", 
            response_format={"type": "json_object"},
            messages=messages,
        )
        messages.append({"role":"assistant", "content":response.choices[0].message.content})
        parsed_response = json.loads(response.choices[0].message.content)
        
        if parsed_response.get("step") == "plan":
            print("🧠: "+parsed_response.get("content"))
            continue
        
        if parsed_response.get("step") == "action":
            tool_name = parsed_response.get("function")
            tool_input = parsed_response.get("input")

            print(f"🔎: Calling tool:{tool_name} with input: {tool_input}")
            
            if(available_tools.get(tool_name)):
                output= available_tools[tool_name](tool_input)
                messages.append({"role": "user", "content": json.dumps({"step": "observe", "output": output})})
                continue

        if parsed_response.get("step") == "output":
            print(f"🔮: "+parsed_response.get("content"))
            break


    