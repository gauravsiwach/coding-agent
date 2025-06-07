 
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
 
 
load_dotenv()
client = OpenAI()

SYSTEM_PROMPT = """
    You are a helpful AI assistant.
    Today Date is {datetime.now()}

"""
response = client.chat.completions.create(
    model="gpt-4.1-mini", 
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},       
        {"role": "user", "content": "What is date time today?"},        
        ],
)
print("\n\n🧠:"+response.choices[0].message.content)