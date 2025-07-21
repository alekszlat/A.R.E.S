import requests
import os

LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "http://127.0.0.1:8080/completion")

def complete(prompt, n_predict=64):
    """
    Sends a prompt to the LLM endpoint and returns the generated text.
    
    Args:
        prompt (str): The input text to send to the LLM.
        n_predict (int): The number of tokens to predict.
        
    Returns:
        str: The generated text from the LLM.
    """
    payload = {
        "prompt": prompt,
        "n_predict": n_predict
    }
    
    try:
        response = requests.post(LLM_ENDPOINT, json=payload, timeout=60)
        response.raise_for_status()
        return response.json().get("content", "")
    except requests.RequestException as e:
        print(f"Error communicating with LLM: {e}")
        return ""

if __name__ == "__main__":
    print(complete("Hello, who are you?"))