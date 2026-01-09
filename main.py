from google import genai
from tools import my_tools
import time

# YOUR FULL KEY HERE
api_key = "AIzaSyDpBVsZdenyRWknc5FNGEfiLJw6xkH3wFQ"

client = genai.Client(api_key=api_key)

print("Agent starting...")

prompt = "Write a Python script named 'count_to_ten.py' that prints numbers 1 to 10."


# We are using the alias that worked for you before
model_name = "gemini-flash-latest" 

for attempt in range(1): 
    try:
        response = client.models.generate_content(
            model=model_name, 
            contents=prompt,
            config={
                'tools': my_tools,
                'tool_config': {
                    'function_calling_config': {
                        'mode': 'ANY' # Force tool use
                    }
                }
            }
        )

        if response.function_calls:
            for call in response.function_calls:
                print(f"🤖 AI is writing file: {call.args['filename']}...")
                if call.name == "create_file":
                    from tools import create_file
                    result = create_file(**call.args)
                    print(result)
        else:
            print("AI reply:", response.text)
        
        break # Success!

    except Exception as e:
        if "429" in str(e):
            print("⏳ specific model busy. Waiting 10 seconds...")
            time.sleep(10)
        else:
            print(f"❌ Error: {e}")
            break