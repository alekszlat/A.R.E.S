import requests
import os

LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "http://127.0.0.1:8080/completion")

"""
SYSTEM_PROMPT = "### Instruction: You are Jarvis, an AI assistant. Answer helpfully.\n"
USER_PREFIX = "User: "
AI_PREFIX = "\nJarvis: "
"""

"""
SYSTEM_PROMPT = (
    "You are Jarvis, a helpful and concise AI assistant. "
    "Answer user questions clearly and once. Avoid repeating phrases."
    "Answer in short sentences, and do not use filler words.\n"
    "If greeted, reply with a short greeting, then wait for a question."
    "If asked for help, provide a brief and direct answer."
    "If asked to repeat, say 'I already answered that.'\n"
)
"""
SYSTEM_PROMPT = (
    "You are Jarvis, a polite, concise, and helpful AI assistant. "
    "Always respond as Jarvis, never mention being an AI model. "
    "Greet users with 'Hello, sir! How can I help you?' if they greet you. "
    "Answer questions clearly and to the point.\n"
    "\n"
    "User: Hi Jarvis\n"
    "Jarvis: Hello, sir! How can I help you?\n"
    "User: What can you do?\n"
    "Jarvis: I can answer questions, provide information, and help with a variety of tasks. How may I assist you?\n"
)

def complete(prompt, n_predict=32):
    """
    Sends a prompt to the LLM endpoint and returns the generated text.
    
    Args:
        prompt (str): The input text to send to the LLM.
        n_predict (int): The number of tokens to predict.
        
    Returns:
        str: The generated text from the LLM.
    """

    chat_prompt = f"{SYSTEM_PROMPT}User: {prompt}\nJarvis:"
    payload = {
        "prompt": chat_prompt,         # your SYSTEM + examples + "User: ...\nJarvis: "
        "n_predict": n_predict,
        "stop": ["\nUser:"],           # <-- stop when it tries to continue the dialogue
        # optional hygiene
        "temperature": 0.7,
    }
    try:
        response = requests.post(LLM_ENDPOINT, json=payload, timeout=60)
        response.raise_for_status()
        return response.json().get("content", "")
    except requests.RequestException as e:
        print(f"Error communicating with LLM: {e}")
        return ""

if __name__ == "__main__":
    print(complete("What is the capital of France?"))