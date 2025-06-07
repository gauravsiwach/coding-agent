# This code is a sample AI agent that creates a React app using Vite.
# Sample query: "Create a React app with a navbar and login page."

from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import json
import os
import subprocess
 
load_dotenv()
client = OpenAI()

dev_server_process = None  # Global variable to store the development server process

SAFE_COMMANDS = ["dir", "echo", "type", "mkdir", "npm create", "npm install", "npm run dev", "cd"]


def stop_command():
    global dev_server_process
    if dev_server_process and dev_server_process.poll() is None:
        dev_server_process.terminate()
        return "🛑 Dev server stopped successfully.", ""
    return "ℹ️ No dev server is currently running.", ""

def run_command(command: str):
    global dev_server_process
    print("💻 Running command...")
    
    parts = [part.strip() for part in command.split("&&")]
    working_dir = os.getcwd()

    for part in parts:
        if part.startswith("cd"):
            path = part.replace("cd", "").strip()
            working_dir = os.path.join(working_dir, path)
            continue
        
        if not any(part.startswith(cmd) for cmd in SAFE_COMMANDS):
            return "Unsafe command blocked", ""

        if part.startswith("npm run dev"):
            print("Starting development server...")
            dev_server_process  = subprocess.Popen(part, shell=True, cwd=working_dir)
            return "Development server started in background.", ""
        
        result = subprocess.run(part, shell=True, capture_output=True, text=True, cwd=working_dir)
        
        if result.returncode != 0:
            print(f"Error running: {part}")
            return result.stdout.strip(), result.stderr.strip()

    return "All commands executed successfully.", ""

def write_file(file_path : str, content : str):
    print("💻 Running command...")
    with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
    output = f"✅ File written to {file_path}"
    return output

available_tools = {
    "run_command": run_command,
    "write_file": write_file,
    "stop_command": stop_command
}

SYSTEM_PROMPT = """
    You are a helpful AI assistant specialized in creating React applications using Vite.
    Before starting the app creation, if any essential information (like app name) is missing from the user 
    query, ask a clarifying question to get that information.
    
    Clarify the following:
        - App name: "What name do you want to give your app?"
        - Theme preference: "Do you want to enable multiple themes (light and dark mode) in your React app? (yes/no)"
        - Default theme: "What should be the default theme (light or dark mode)? (light/dark)" if multiple themes are enabled.
    
        After the app is created:
        - Ask: "Do you want to run the app now? (yes/no)"

        After the app is running:
        - Ask: "Do you want to stop the running app? (yes stop/no)"

    Your process:
        1. Analyze the user query.
        2. If essential info (app name or multi-theme preference) is missing, output a "clarify" step asking the user for that info.
        3. Once everything is available, plan the steps.
        4. Otherwise, plan the steps needed to create the app.
        5. Perform one step at a time by selecting from available tools.
        6. Wait for the result of each step before proceeding.
        7. After app creation, ask the user if they want to run the app.
        8. Always output responses in this JSON format:
       
        {    
        "step": "clarify" | "plan" | "action" | "observe" | "output",
        "function": "name_of_function_if_action_step",
        "input": "input_for_the_function_or_content"
        }


   Available tools:
        - run_command: Execute shell commands such as creating the app or installing dependencies.
        - write_file: Create or update code files with given content.

    Rules:
        - Never perform multiple steps in one response.
        - Ask clarifying questions when needed before starting.
        - Carefully analyze user input before planning.
        - Ensure safety by avoiding harmful commands.
        - Respond step-by-step until the user query is fully resolved.

    Output JSON format:
        {{
            "step": "string",
            "content": "string",
            "function": "The name of the function if step is action",
            "input": "The input parameter for the function"
        }}
        
    Example:
        User query: "Create a React app with a navbar and login page."

        Output (if app name missing):
        {"step": "clarify", "input": "What name do you want to give your app?"}

        User replies: "MyApp"

        Output (if multi-theme preference missing):
        {"step": "clarify", "input": "Do you want to enable multiple themes (light and dark mode) in your React app? (yes/no)"}

        User replies: "yes"

        Output (if multi-theme is enabled):
        {"step": "clarify", "input": "what should be default theme (light and dark mode)? (light/dark)"}

        User replies: "light"

       Output:
            {"step": "plan", "input": "User wants a React app named 'MyApp' with navbar and login page, and multiple themes enabled with light as default."}
            {"step": "action", "function": "run_command", "input": "npm create vite@latest MyApp -- --template react"}
            {"step": "observe", "input": "Project created successfully."}
            {"step": "action", "function": "write_file", "input": {"path": "MyApp/src/components/Navbar.jsx", "content": "// React Navbar code here"}}
            {"step": "clarify", "input": "Do you want to run the app now? (yes/no)"}
            {"step": "action", "function": "run_command", "input": "cd MyApp && npm install && npm run dev"}
            {"step": "output", "content": "React app 'MyApp' setup is complete and is now running."}
            {"step": "clarify", "input": "Do you want to stop the running app? (yes/no)"}
            {"step": "action", "function": "stop_command"}
            {"step": "output", "content": "React app is stoped now."}
            
"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

query= input("Welcome into react app agent->: ")
messages.append({"role": "user", "content": query})

while True:
        response= client.chat.completions.create(
            model="gpt-4.1-mini", 
            response_format={"type": "json_object"},
            messages=messages,
        )
        messages.append({"role":"assistant", "content":response.choices[0].message.content})
        parsed_response = json.loads(response.choices[0].message.content)
        
        if parsed_response.get("step") == "clarify":
            print("🤔: "+parsed_response.get("input"))
            user_input = input(":-->")
            messages.append({"role": "user", "content": user_input})
            continue

        if parsed_response.get("step") == "plan":
            print("🧠: "+parsed_response.get("input"))
            continue
        
        if parsed_response.get("step") == "action":
            tool_name = parsed_response.get("function")
            tool_input = parsed_response.get("input")

            print(f"🔎: Calling tool: {tool_name}  with input: {tool_input}")
            
            if(available_tools.get(tool_name)):
                 if tool_name == "write_file":
                    output = available_tools[tool_name](tool_input["path"], tool_input["content"])
                    messages.append({"role": "user", "content": json.dumps({"step": "observe", "output": output})})
                    continue
                 if tool_name == "run_command":
                    output = available_tools[tool_name](tool_input)
                    messages.append({"role": "user", "content": json.dumps({"step": "observe", "output": output})})
                    continue
                 if tool_name == "stop_command":
                    output = available_tools[tool_name]()
                    messages.append({"role": "user", "content": json.dumps({"step": "observe", "output": output})})
                    continue


        if parsed_response.get("step") == "output":
            message_text = parsed_response.get("input") or parsed_response.get("content")
            print("🤔: " + message_text)
            stop_indicators = ["stopped", "app has been stopped", "terminated", "shut down", "stopping the app", "app is no longer running"]
            if any(indicator in message_text.lower() for indicator in stop_indicators):
                break
            else:
              continue


 
 
# response = client.chat.completions.create(
#     model="gpt-4.1-mini", 
#     messages=[
#         {"role": "system", "content": SYSTEM_PROMPT},       
#         {"role": "user", "content": "create a hello world app with name hello_world"},  
#         # {"role": "assistant", "content": json.dumps({"step": "clarify", "input": "What name do you want to give your app?"})},              
#         # {"role": "user", "content": "app name is todo-app"}, 
#         {"role": "assistant", "content": json.dumps({"step": "clarify", "input": "Do you want to enable multiple themes (light and dark mode) in your React app? (yes/no)"})},           
#         {"role": "user", "content": "yes"},
#         {"role": "assistant", "content": json.dumps({"step": "clarify", "input": "What should be the default theme (light or dark mode)? (light/dark)"})},           
#         {"role": "user", "content": "light"}, 
#         {"role": "assistant", "content": json.dumps({"step": "plan", "input": "User wants a React app named 'hello_world' with a Hello World display and multiple themes enabled with light as default."})},
#         {"role": "assistant", "content": json.dumps({"step": "action", "function": "run_command", "input": "npm create vite@latest hello_world -- --template react"})},
#         {"role": "assistant", "content": json.dumps({"step": "observe", "input": "Project 'hello_world' created successfully with Vite React template."})},           
        
#         {"role": "assistant", "content": json.dumps({"step": "action", "function": "write_file", "input": {"path": "hello_world/src/App.css", "content": "/* Base styles */\n.App {\n  text-align: center;\n  padding: 2rem;\n  font-family: Arial, sans-serif;\n}\n\n.App-header {\n  margin: 0 auto;\n}\n\nbutton {\n  margin-top: 1rem;\n  padding: 0.5rem 1rem;\n  cursor: pointer;\n  font-size: 1rem;\n  border: none;\n  border-radius: 4px;\n}\n\n/* Light theme */\n:root[data-theme='light'] {\n  --bg-color: #ffffff;\n  --text-color: #000000;\n  --button-bg: #e0e0e0;\n  --button-text: #000000;\n}\n\n/* Dark theme */\n:root[data-theme='dark'] {\n  --bg-color: #121212;\n  --text-color: #ffffff;\n  --button-bg: #333333;\n  --button-text: #ffffff;\n}\n\nbody, .App {\n  background-color: var(--bg-color);\n  color: var(--text-color);\n}\n\nbutton {\n  background-color: var(--button-bg);\n  color: var(--button-text);\n}\n\nbutton:hover {\n  opacity: 0.8;\n}\n"}})},
#         {"role": "user", "content": json.dumps({"step": "observe", "output": "File written to hello_world/src/App.jsx"})},
#         {"role": "user", "content": json.dumps({"step": "action", "function": "write_file", "input": {"path": "hello_world/src/App.jsx", "content": "import { useState, useEffect } from 'react';\nimport './App.css';\n\nfunction App() {\n  const [theme, setTheme] = useState('light');\n\n  useEffect(() => {\n    document.documentElement.setAttribute('data-theme', theme);\n  }, [theme]);\n\n  const toggleTheme = () => {\n    setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'));\n  };\n\n  return (\n    <div className=\"App\">\n      <h1>Hello World</h1>\n      <button onClick={toggleTheme}>\n        Switch to {theme === 'light' ? 'Dark' : 'Light'} Mode\n      </button>\n    </div>\n  );\n}\n\nexport default App;\n"}})},
        
#         {"role": "assistant", "content": json.dumps({"step": "clarify", "input": "Do you want to run the app now? (yes/no)"})},
#         {"role": "user", "content": "yes"},
#         {"role": "assistant", "content": json.dumps({"step": "action", "function": "run_command", "input": "cd hello_world && npm install && npm run dev"})},
       
#         {"role": "assistant", "content": json.dumps({"step": "output", "input": "React app 'hello_world' setup is complete and is now running with multiple themes enabled and light as default."})},

#         # {"role": "assistant", "content": json.dumps({"step": "clarify", "input": "Do you want to stop the running app? (yes stop/no)"})},
#         # {"role": "user", "content": "yes"},

#         # {"role": "assistant", "content": json.dumps({"step": "action", "function": "stop_command", "input": ""})},
        
#         # {"role": "assistant", "content": json.dumps({"step": "output", "input": "The running app 'hello_world' has been stopped."})},
        
#         ],
# )
# print("\n\n🧠:"+response.choices[0].message.content)
    