import requests
import json

def get_openai_response(prompt, api_key):
    """
    Send a prompt to the OpenAI API and return the response.

    Parameters:
    prompt (str): The input prompt to send to the OpenAI API.
    api_key (str): The API key for authentication with the OpenAI API.

    Returns:
    str: The response content from the OpenAI API.
    """
    if not api_key:
        raise ValueError("OpenAI API key is not provided.")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        response_json = response.json()
        return response_json['choices'][0]['message']['content']
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

# Example usage:
# openai_api_key = "your_openai_api_key_here"
# prompt = "What is the capital of France?"
# response = get_openai_response(prompt, openai_api_key)
# print(response)
