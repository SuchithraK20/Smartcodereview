import requests
import json
import re

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
        return "Error: Unexpected response format."
    except (KeyError, IndexError) as e:
        print(f"Unexpected response structure: {e}")
        return "Error: Unexpected response structure."
        
def analyze_code_with_codellama(file_patch: str) -> dict:
    """
    Sends the code content to Codellama for analysis and returns suggestions mapped to line numbers or general suggestions.
    """
    # Prepare the prompt for Codellama
    prompt = f"Review the following Python code and provide concise, actionable suggestions. If possible, include the line numbers for specific improvements:\n\n{file_patch}"
    
    # Call Codellama to analyze the code
    codellama_response = call_codellama(prompt)

    # Debugging: Log the raw response
    print(f"Codellama Response: {codellama_response}")

    # Parse the response to extract line-specific suggestions
    suggestions = {}
    try:
        # Attempt to extract line-specific suggestions
        for match in re.finditer(r"Line (\d+): (.+)", codellama_response):
            line_number = int(match.group(1))
            suggestion = match.group(2).strip()
            suggestions[line_number] = suggestion

        # If no line-specific suggestions are found, add general suggestions
        if not suggestions:
            suggestions["general"] = codellama_response.strip()
    except Exception as e:
        print(f"Failed to parse suggestions: {e}")

    return suggestions
