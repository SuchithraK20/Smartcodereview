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
        
def analyze_code_with_codellama(file_patch: str, filename: str, changed_lines: list) -> dict:
    """
    Sends the code content to Codellama for analysis and returns suggestions mapped to line numbers.
    Only considers suggestions for changed lines.
    """
    # Prepare the prompt for Codellama
    prompt = f"""
Please review the following code changes and provide suggestions for improvement in a JSON format. 
The code below shows the updated code, with changes explicitly marked with [CHANGED] at the end of each line.
- Only lines marked with [CHANGED] should be reviewed. 
- For each line marked with [CHANGED], provide a detailed comment on the specific change, focusing on issues such as readability, security, performance, or suggestions for improvement.
- Ignore all lines that do not have the [CHANGED] marker at the end. Focus **only** on the lines marked as [CHANGED].
- For each [CHANGED] line, provide a suggestion for improving that particular line or section of code.
- Be specific in your recommendations. If there are no issues with the line, return an empty list for that line.

The format of the response should look like the following:
[
    {
        "line": <exact line number>,
        "type": "readability" | "security" | "performance" | "suggestion" | "good-practice",
        "severity": "high" | "medium" | "low",
        "message": "<specific_issue_and_recommendation>"
    }
]

Code to review from {filename}:

{file_patch}

Response format (use EXACT line numbers from the start of lines):
[ 
    { 
        "line": <line_number>,
        "type": "type-safety" | "architecture" | "readability" | "security" | "performance" | "suggestion" | "good-practice",
        "severity": "high" | "medium" | "low",
        "message": "<specific_issue_and_recommendation>"
    }
]

Rules:
1. ONLY review lines marked with [CHANGED].
2. Be specific and actionable in your comments, focusing on improvement suggestions for the marked lines.
3. DO NOT comment on any lines that are NOT marked with [CHANGED].
4. If you find no issues with a line, skip it and do not comment on it.
"""



    # Call Codellama to analyze the code
    codellama_response = call_codellama(prompt)

    # Debugging: Log the raw response
    print(f"Codellama Response: {codellama_response}")

    # Parse the response to extract line-specific suggestions
    suggestions = []
    try:
        # Handle JSON response
        if "general" in codellama_response:
            json_start = codellama_response.find("[")
            json_end = codellama_response.rfind("]") + 1
            if json_start != -1 and json_end != -1:
                json_content = codellama_response[json_start:json_end]
                suggestions = json.loads(json_content)
            else:
                raise ValueError("No valid JSON array found in the response.")
        else:
            suggestions = json.loads(codellama_response)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Failed to parse Codellama response as JSON: {e}")
        print("Attempting to parse as plain text.")

        # Handle streaming response fallback
        if isinstance(codellama_response, str):
            suggestions = _handle_plain_text_response(codellama_response)
        else:
            print("Codellama response is not a valid string.")

    # Map suggestions to line numbers
    line_suggestions = {}
    for suggestion in suggestions:
        line = suggestion.get("line")
        message = suggestion.get("message")
        if line and message:
            # Only include suggestions for changed lines
            if int(line) in changed_lines:
                line_suggestions[int(line)] = message

    # If no line-specific suggestions, add general suggestions
    if not line_suggestions and isinstance(codellama_response, str):
        # Extract general suggestions if present
        general_start = codellama_response.find("General suggestions")
        if general_start != -1:
            line_suggestions["general"] = codellama_response[general_start:].strip()
        else:
            line_suggestions["general"] = codellama_response.strip()

    return line_suggestions
def _handle_plain_text_response(response: str) -> list:
    """
    Handles plain text responses from Codellama and extracts actionable feedback.
    """
    suggestions = []
    try:
        # Use regex to extract line-specific suggestions
        matches = re.findall(r'"line":\s*(\d+),.*?"message":\s*"(.*?)"', response, re.DOTALL)
        for match in matches:
            line, message = match
            suggestions.append({"line": int(line), "message": message.strip()})
    except Exception as e:
        print(f"Failed to parse plain text response: {e}")
    return suggestions