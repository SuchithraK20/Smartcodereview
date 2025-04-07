import os
from github import Github
from github_utils import get_pr_details, post_inline_comment
from unidiff import PatchSet, UnidiffParseError
from ollama import analyze_code_with_codellama

def map_line_to_diff_position(patch, absolute_line):
    """
    Maps an absolute line number to a diff position.
    """
    patch_set = PatchSet(patch)
    for patched_file in patch_set:
        for hunk in patched_file:
            for line in hunk:
                if line.target_line_no == absolute_line:
                    return line.diff_line_no
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

            # Extract changed lines
            changed_lines = extract_changed_lines(file.patch)

            # Call the updated analyze_code_with_codellama function
            suggestions = analyze_code_with_codellama(file.patch, file.filename, changed_lines)

            # Debugging: Log suggestions
            print(f"Suggestions for {file.filename}: {suggestions}")

            # Handle line-specific and general suggestions
            for line, suggestion in suggestions.items():
                if line == "general":
                    # Post a general comment on the PR
                    pr.create_issue_comment(f"General suggestions for {file.filename}:\n\n{suggestion}")
                else:
                    position = map_line_to_diff_position(file.patch, line)
                    if position is None:
                        print(f"Could not map line {line} to a diff position.")
                        continue

                    # Post inline comment
                    post_inline_comment(pr, file.filename, position, suggestion)

if __name__ == "__main__":
    main()
