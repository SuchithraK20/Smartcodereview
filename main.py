import os
from github import Github
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
            suggestions = analyze_code_with_codellama(file.patch)
            for line, suggestion in suggestions.items():
                pr.create_review_comment(
                    body=suggestion,
                    commit_id=pr.head.sha,
                    path=file.filename,
                    position=line,
                )

if __name__ == "__main__":
    main()
