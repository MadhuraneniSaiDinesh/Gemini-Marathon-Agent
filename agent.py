import subprocess
from google import genai
from tools import my_tools, create_file
import time
import sys

# PASTE YOUR FULL KEY HERE
api_key = "AIzaSyD6aNTK9o2RAMctqNaofcGqLPewThBau4w"
client = genai.Client(api_key=api_key)

# We will try these models in order. If one fails, we switch to the next.
MODEL_ROSTER = [
    "gemini-2.0-flash",       # Newest stable
    "gemini-flash-latest",    # Standard 1.5 Flash
    "gemini-1.5-flash-8b",    # Lightweight (often has separate quota)
    "gemini-1.5-pro-latest"   # Pro (Backup)
]

def run_script(filename):
    """Runs the generated script."""
    print(f"⚙️ Running {filename}...")
    try:
        result = subprocess.run(["python", filename], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except subprocess.TimeoutExpired:
        return False, "Error: Script took too long to run (Timeout)."
    except FileNotFoundError:
        return False, f"Error: The file '{filename}' was never created."

def ask_gemini(prompt, history=[]):
    """Tries to get a response using the model roster."""
    full_content = history + [prompt]
    
    for model_name in MODEL_ROSTER:
        try:
            # print(f"   (Trying model: {model_name}...)") 
            response = client.models.generate_content(
                model=model_name, 
                contents=full_content,
                config={'tools': my_tools, 'tool_config': {'function_calling_config': {'mode': 'AUTO'}}}
            )
            
            if response.function_calls:
                for call in response.function_calls:
                    if call.name == "create_file":
                        print(f"✍️ Writing code to {call.args['filename']}...")
                        create_file(**call.args)
                        return f"CODE_WRITTEN: {call.args['filename']}"
            return response.text

        except Exception as e:
            # If it's a quota/not-found error, strictly try the next model
            if "429" in str(e) or "404" in str(e):
                continue # Skip to next model
            else:
                # Real error? Wait a bit then try next
                time.sleep(1)
    
    return "Error: All models exhausted."

# --- THE INTERACTIVE LOOP ---

print("\n🤖 GEMINI MARATHON AGENT READY (Multi-Model Mode)")
user_task = input("👉 What should I build? (Keep it simple!): ")

print(f"\n--- STARTING TASK: {user_task} ---")
history_log = [] 
initial_prompt = f"Write a complete Python script named 'app.py' that does the following: {user_task}. Use the create_file tool."

print("🧠 Thinking...")
result = ask_gemini(initial_prompt, history_log)

if "Error" in result and "CODE_WRITTEN" not in result:
    print("\n❌ IDLE: All quotas are full right now. Please wait 1 hour.")
    sys.exit()

# The Healing Loop
for attempt in range(5):
    print(f"\n--- ATTEMPT {attempt+1} ---")
    
    success, output = run_script("app.py")
    
    if success:
        print("\n✅ SUCCESS! The app works.")
        print("Output:", output)
        break
    else:
        print("\n❌ CRASHED! Fixing it...")
        # Trim error to save tokens
        short_error = output.strip()[:300] 
        print(f"Error: {short_error}...") 
        
        fix_prompt = f"The file 'app.py' crashed with this error:\n{short_error}\nPlease rewrite 'app.py' to fix this. Use the create_file tool."
        
        print("🧠 Thinking (Fixing)...")
        ask_gemini(fix_prompt, history_log)
        time.sleep(5)