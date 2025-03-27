import subprocess
import ollama
import os
from enum import Enum

class ResponseFormat(Enum):
    JSON = "json_object"
    TEXT = "text"

# Function to run Pylint and get feedback
def run_pylint(file_path):
    """Runs Pylint and returns feedback."""
    pylint_output = subprocess.run(
        ['pylint', file_path],
        capture_output=True,
        text=True
    )
    return pylint_output.stdout

# Function to generate a prompt for Ollama to suggest fixes based on Pylint feedback
def generate_ollama_fix_prompt(pylint_feedback, file_path):
    """Generates a prompt for Ollama to suggest fixes based on Pylint feedback."""
    try:
        with open(file_path, 'r') as file:
            code = file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

    # Constructing the prompt for Ollama to provide suggestions
    prompt = f"""
    Given the following Pylint feedback, analyze the code and provide the final, fully corrected code.

    Pylint Feedback:
    {pylint_feedback}

    Python Code:
    ```python
    {code}
    ```
    Your task is to:
        - Shorten overly long function names.
        - Make variable names more descriptive.
        - Add docstrings where necessary.
        - Add checks to prevent out-of-range indexing.
        - Add unit tests using Python's built-in 'assert' statements for each function.
        - Provide ONLY the final, corrected Python code, including unit tests, without explanations or steps.
        - Output the fixed code directly.
        - Correct all Pylint errors and warnings, including syntax errors, function naming errors, and other issues.
        - Provide ONLY the final, corrected Python code, without explanations or steps.
        - Output the fixed code directly.
    """
    return prompt

# Function to interact with Ollama and get suggested fixes
def get_ollama_fixes(pylint_feedback, file_path):
    """Use Ollama to get code fixes based on Pylint feedback."""
    prompt = generate_ollama_fix_prompt(pylint_feedback, file_path)
    TEMPERATURE = 0
    response_format = ResponseFormat.TEXT
    response = ollama.generate(
        model="codellama",  # Ensure you're using the correct model
        prompt=prompt,
        keep_alive="1h",
        format="" if response_format == ResponseFormat.TEXT else "json",
        options={"temperature": TEMPERATURE},
    )

    # Debug: log the response from Ollama
    print("Ollama's Response:\n", response["response"])

    fixed_code = response["response"]
    if "```python" in fixed_code:
        fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()

    return fixed_code

# Function to apply the fixes to the Python file
def apply_ollama_fixes(file_path, fixes):
    """Applies the suggested fixes to the file."""
    if fixes is None:
        print("No fixes provided, skipping file update.")
        return

    try:
        if not fixes.strip():
            print("Ollama's suggested fix is empty. Aborting file update.")
            return

        print(f"Applying the following fixes to {file_path}:\n{fixes}")

        with open(file_path, 'w') as file:
            file.write(fixes)
        print(f"Fixes have been applied successfully to {file_path}.")

        # Verify the fixes with Pylint
        pylint_verification = run_pylint(file_path)
        if "Your code has been rated at 10.00/10" in pylint_verification:
            print(f"Pylint verification successful.")
        else:
            print(f"Pylint verification failed:\n{pylint_verification}")

    except Exception as e:
        print(f"Error writing file {file_path}: {e}")

# Main function to process the file
def process_code(file_path):
    # Run Pylint and get feedback
    pylint_feedback = run_pylint(file_path)
    print("Pylint Feedback:\n", pylint_feedback)

    # Use Ollama to get suggestions or fixes
    fixes = get_ollama_fixes(pylint_feedback, file_path)
    if fixes:
        print("\nSuggested Fixes:\n", fixes)

        # Apply the fixes to the file
        apply_ollama_fixes(file_path, fixes)
    else:
        print("\nNo fixes were suggested by Ollama.")

# Example usage
file_path = "/root/test_code/script.py"  # Path to your Python script
process_code(file_path)