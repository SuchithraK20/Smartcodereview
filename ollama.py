import subprocess
import json

def call_codellama(prompt: str) -> str:
    """
    Calls the Codellama model with the given prompt and returns the response.
    """
    try:
        # Replace 'codellama' with the actual command or API call for Codellama
        result = subprocess.run(
            ["ollama", "run", "codellama", "--prompt", prompt],
            capture_output=True,
            text=True,
            check=True,
        )
        response = result.stdout.strip()
        return response
    except subprocess.CalledProcessError as e:
        print(f"Error calling Codellama: {e}")
        return "Error: Unable to process the request."

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
        return {}
