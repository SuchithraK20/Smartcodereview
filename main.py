import os
from github import Github
from github_utils import get_pr_details, post_inline_comment
from unidiff import PatchSet, UnidiffParseError
from ollama import analyze_code_with_codellama

def map_line_to_diff_position(patch, absolute_line):
    """
    Maps an absolute line number to a diff position.
    """
    try:
        patch_set = PatchSet(patch)
        for patched_file in patch_set:
            for hunk in patched_file:
                for line in hunk:
                    if line.target_line_no == absolute_line:
                        print(f"Mapping absolute line {absolute_line} to diff position {line.diff_line_no}")
                        return line.diff_line_no
    except Exception as e:
        print(f"Error parsing patch or mapping line {absolute_line}: {e}")
    print(f"Could not map absolute line {absolute_line} to a diff position.")
    return None

def extract_changed_lines(patch):
    """
    Extracts the line numbers of changed lines from the patch.
    """
    try:
        patch_set = PatchSet(patch)
        changed_lines = []
        for patched_file in patch_set:
            for hunk in patched_file:
                for line in hunk:
                    if line.is_added:  # Only consider added lines
                        changed_lines.append(line.target_line_no)
        return changed_lines
    except UnidiffParseError as e:
        print(f"Failed to parse patch: {e}")
        return []

def sanitize_patch_content(patch_content):
    """
    Sanitizes the patch content to avoid any special character issues.
    """
    return patch_content.replace("@@", "@@@").replace("-", "_").replace("+", "~")

def validate_patch_format(patch_content):
    """
    Validates the format of the patch content to ensure it is correctly structured.
    """
    if not patch_content.startswith("@@"):
        raise ValueError("Invalid patch format: missing hunk header.")
    return True

def handle_codellama_suggestions(suggestions, file, pr):
    """
    Handles suggestions by posting inline comments or general comments to the PR.
    """
    for line, suggestion in suggestions.items():
        if line == "general":
            # Post a general comment on the PR
            pr.create_issue_comment(f"General suggestions for {file.filename}:\n\n{suggestion}")
        else:
            position = map_line_to_diff_position(file.patch, int(line))
            if position is None:
                print(f"Could not map line {line} to a diff position.")
                continue

            # Post inline comment
            post_inline_comment(pr, file.filename, position, suggestion)

def main():
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("GITHUB_PR_NUMBER")

    github = Github(token)
    repo = github.get_repo(repo_name)
    pr = repo.get_pull(int(pr_number))

    # Fetch PR changes
    files = pr.get_files()
    for file in files:
        if file.filename.endswith(".py"):
            print(f"Analyzing file: {file.filename}")
            print(f"Patch content for {file.filename}:\n{file.patch}")  # Log the raw patch content

            # Ensure that the patch is in the correct format
            try:
                patch_content = file.patch
                # Validate the patch format before proceeding
                if validate_patch_format(patch_content):
                    print("Patch content loaded correctly.")
                else:
                    print("Patch format is invalid.")
                    continue
            except Exception as e:
                print(f"Error loading patch content: {e}")
                continue

            # Sanitize patch content to avoid special character issues
            sanitized_patch_content = sanitize_patch_content(patch_content)

            # Extract changed lines from the patch
            changed_lines = extract_changed_lines(sanitized_patch_content)

            # Call the analyze_code_with_codellama function for code review
            suggestions = analyze_code_with_codellama(sanitized_patch_content, file.filename, changed_lines)

            # Debugging: Log suggestions for each file
            print(f"Suggestions for {file.filename}: {suggestions}")

            # Handle line-specific and general suggestions
            handle_codellama_suggestions(suggestions, file, pr)

if __name__ == "__main__":
    main()
