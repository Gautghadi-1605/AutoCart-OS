import requests

def ask_llama(prompt: str) -> str:
    url = "http://localhost:11434/api/generate"

    response = requests.post(
        url,
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]
