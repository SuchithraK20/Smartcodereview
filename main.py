import os
from github import Github
from github_utils import get_pr_details
from ollama import analyze_code_with_codellama

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
            print(f"Analyzing file: {file.filename}")  # Debugging
            suggestions = analyze_code_with_codellama(file.patch)
            
            # Debugging: Log suggestions
            print(f"Suggestions for {file.filename}: {suggestions}")
            
            for line, suggestion in suggestions.items():
                try:
                    print(f"Posting comment to {file.filename} at line {line}: {suggestion}")  # Debugging
                    pr.create_review_comment(
                        body=suggestion,
                        commit_id=pr.head.sha,
                        path=file.filename,
                        position=line,  # Ensure this is the correct diff position
                    )
                except Exception as e:
                    print(f"Failed to post comment: {e}")  # Debugging

if __name__ == "__main__":
    main()
