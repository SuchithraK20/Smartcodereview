import os
from github import Github
from github_utils import get_pr_details, post_inline_comment
from unidiff import PatchSet

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
            suggestions = analyze_code_with_codellama(file.patch)

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
