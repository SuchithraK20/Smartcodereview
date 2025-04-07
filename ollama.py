import requests
import json

import requests
import json

def call_codellama(prompt: str) -> str:
    """
    Calls the Codellama model running on a local server and returns the concatenated response.
    """
    url = "http://127.0.0.1:11434/api/generate"  # Adjust the endpoint if necessary
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "codellama",  # Specify the model name
        "prompt": prompt,
        "temperature": 0.7,  # Adjust temperature as needed
        "max_tokens": 500    # Adjust max tokens as needed
    }

    try:
        response = requests.post(url, headers=headers, json=payload, stream=True)
        response.raise_for_status()  # Raise an error for HTTP status codes 4xx/5xx

        # Process the response as a stream of JSON objects
        full_response = ""
        for line in response.iter_lines():
            if line:  # Skip empty lines
                try:
                    json_line = json.loads(line)
                    full_response += json_line.get("response", "")
                except json.JSONDecodeError as e:
                    print(f"Failed to parse line as JSON: {line}")
                    continue

        return full_response.strip()
    except requests.exceptions.RequestException as e:
        print(f"Error calling Codellama: {e}")
        return "Error: Unable to process the request."
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")
        print(f"Raw response: {response.text}")
        return "Error: Unexpected response format."
    except (KeyError, IndexError) as e:
        print(f"Unexpected response structure: {e}")
        return "Error: Unexpected response structure."

def analyze_code_with_codellama(file_content: str) -> dict:
    """
    Sends the code content to Codellama for analysis and returns suggestions.
    """
    prompt = f"Review the following Python code and suggest improvements:\n\n{file_content}"
    response = call_codellama(prompt)
    try:
        # Parse the response if it's in JSON format
        suggestions = json.loads(response)
        return suggestions
    except json.JSONDecodeError:
        print("Failed to parse Codellama response.")
        print(f"Codellama Response: {response}")
        return {}
