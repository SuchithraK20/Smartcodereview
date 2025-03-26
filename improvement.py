from enum import Enum
import os
import ollama

class ResponseFormat(Enum):
    JSON = "json_object"
    TEXT = "text"


def generate_ollama_summary(file_path):
    """Generate a summary of potential issues and improvements using Ollama."""
    
    # Read the code from the provided file path
    try:
        with open(file_path, 'r') as file:
            code = file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

    # Construct the review prompt with a subtle approach
    review_prompt = f"""
    Analyze the following Python code and provide feedback on its correctness, efficiency, and maintainability:

    ```python
    {code}
    ```
    Your response should:
    - Highlight any potential indexing issues or boundary-related concerns.
    - Provide insights into any subtle errors that could affect the correctness of the code.
    - Suggest improvements while maintaining the intended functionality.
    - Ensure readability and best coding practices.
    - add unittests for the methods

    """
    TEMPERATURE = 0

    # Send the prompt to Ollama
    response_format = ResponseFormat.TEXT 
    response = ollama.generate(
        model="llama3.2",
        prompt=review_prompt,
        keep_alive="1h",
        format="" if response_format == ResponseFormat.TEXT else "json",
        options={"temperature": TEMPERATURE},
    )

    return response["response"]

if __name__ == "__main__":
    file_path = "/root/test_code/script.py"  

    # Ensure file exists before processing
    if os.path.exists(file_path):
        print(f"File {file_path} exists.")
        print(generate_ollama_summary(file_path))
    else:
        print(f"The file {file_path} does not exist.")
