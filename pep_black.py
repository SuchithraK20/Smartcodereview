import os
import autopep8
import black
import pycodestyle
from pathlib import Path

# Function to check for PEP 8 violations using pycodestyle
def check_pep8(file_path):
    """Checks for PEP 8 compliance using pycodestyle."""
    style_guide = pycodestyle.StyleGuide()
    result = style_guide.check_files([file_path])
    return result

# Function to format the code using autopep8 (aggressive)
def auto_format_pep8(file_path):
    """Auto-formats the Python code using autopep8 with aggressive settings."""
    with open(file_path, 'r') as f:
        code = f.read()

    # Use aggressive setting for fixing issues, including long lines and indentation
    formatted_code = autopep8.fix_code(code, options={'aggressive': 2, 'max_line_length': 79})

    # Write the formatted code back to the file
    with open(file_path, 'w') as f:
        f.write(formatted_code)

    print(f"PEP8 formatted code written back to {file_path}")
    return formatted_code

# Function to format code using Black (with custom line length)
def format_with_black(file_path):
    """Auto-formats the Python code using Black."""
    file_path = Path(file_path)

    # Format the file in place using Black
    try:
        black.format_file_in_place(file_path, fast=False, mode=black.FileMode(line_length=79))
        print(f"Black formatting applied to {file_path}")
    except Exception as e:
        print(f"Error during Black formatting: {e}")

# Function to check and auto-correct PEP 8, Pylint, and Black issues
def check_and_auto_correct(file_path):
    # Check PEP 8 issues
    print(f"\nChecking PEP 8 issues for {file_path}...")
    pep8_result = check_pep8(file_path)
    pep8_issues = ""
    if pep8_result.total_errors > 0:
        pep8_issues = f"PEP 8 issues found: {pep8_result.total_errors}\n"
        pep8_result.print_statistics()
    else:
        pep8_issues = "No PEP 8 issues found."

    # Show feedback to client
    print("\nPEP 8 Feedback:\n", pep8_issues)

    print("\nFormatting code with Black...")
    # Format with Black
    format_with_black(file_path)
    print("Black formatting applied.")

    # Re-check after Black formatting
    print("\nRe-running checks after applying corrections...")

    # Re-checking PEP 8
    print("\nRe-checking PEP 8 after applying corrections...")
    pep8_result_after = check_pep8(file_path)
    if pep8_result_after.total_errors == 0:
        print("No PEP 8 issues after correction.")
    else:
        print(f"Remaining PEP 8 issues: {pep8_result_after.total_errors}")
        pep8_result_after.print_statistics()

    return pep8_issues

# Function to confirm with client and auto-apply fixes if confirmed
def confirm_and_apply_fixes(file_path):
    # Get the issues and feedback
    check_and_auto_correct(file_path)

    # Ask the client for confirmation
    confirm = input("\nDo you want to apply the changes and fix the issues? (yes/no): ").lower()

    if confirm == 'yes':
        print("\nApplying fixes...\n")
        # Apply auto-corrections
        auto_format_pep8(file_path)
        format_with_black(file_path)

        # Generate a summary using Ollama
        print("Fixes have been applied successfully.")
    else:
        print("\nNo changes applied. Please manually review the issues.")

# Main function to check and fix code
if __name__ == "__main__":
    file_path = "/root/test_code/script.py"  

    # Ensure file exists before processing
    if os.path.exists(file_path):
        print(f"File {file_path} exists. Proceeding to apply fixes.")
        confirm_and_apply_fixes(file_path)
    else:
        print(f"The file {file_path} does not exist.")
