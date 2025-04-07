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
    Sends the code content to Codellama for analysis and returns suggestions mapped to line numbers or general suggestions.
    """
    # Prepare the prompt for Codellama
    prompt = f"""
You are an expert code reviewer. Review the following code changes and provide specific, actionable feedback. Focus on:
1. Type safety and potential runtime issues
2. Architecture and design patterns
3. Code readability and maintainability
4. Security vulnerabilities (IMPORTANT: for security issues like 'eval', use the EXACT line where the dangerous function is called)
5. Performance implications

The code below shows:
- Each line starts with its EXACT line number followed by a colon
- Changed lines are marked with [CHANGED]
- You MUST use the EXACT line number shown at the start of the line in your response
- DO NOT use a line number unless you see it explicitly at the start of a line
- For security issues, use the line number where the actual dangerous code appears
- For other multi-line issues, use the first line number where the issue appears
- Context lines are shown without markers

IMPORTANT NOTES:
- For security issues (like eval, Function constructor, etc.), always use the line number where the dangerous function is actually called
- For performance issues (like nested loops), use the line number of the outer function or loop
- Double-check that your line numbers match exactly with where the issue occurs
Code to review from {filename}:

{file_patch}

Response format (use EXACT line numbers from the start of lines):
[
  {{
    "line": <number_from_start_of_line>,
    "type": "type-safety" | "architecture" | "readability" | "security" | "performance" | "suggestion" | "good-practice",
    "severity": "high" | "medium" | "low",
    "message": "<specific_issue_and_recommendation>"
  }}
]

Rules:
1. Only comment on [CHANGED] lines
2. Use EXACT line numbers shown at start of lines
3. Each line number must match one of: {changed_lines}
4. Consider context when making suggestions
5. Be specific and actionable in recommendations
6. For security issues, use the exact line where dangerous code appears
7. For other multi-line issues, use the first line number where the issue appears

If no issues found, return: []
"""
    
    # Call Codellama to analyze the code
    codellama_response = call_codellama(prompt)

    # Debugging: Log the raw response
    print(f"Codellama Response: {codellama_response}")

    # Parse the response to extract line-specific suggestions
    try:
        # Find the JSON array in the response
        json_start = codellama_response.find("[")
        json_end = codellama_response.rfind("]") + 1
        if json_start == -1 or json_end == -1:
            raise ValueError("No JSON array found in the response.")

        json_content = codellama_response[json_start:json_end]
        suggestions = json.loads(json_content)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Failed to parse Codellama response as JSON: {e}")
        suggestions = []

        # Fallback to plain text parsing
        for match in re.finditer(r"\[CHANGED\] Line (\d+): (.+)", codellama_response):
            line_number = int(match.group(1))
            message = match.group(2).strip()
            suggestions.append({"line": line_number, "message": message})

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
        line_suggestions["general"] = codellama_response.strip()

    return line_suggestions
