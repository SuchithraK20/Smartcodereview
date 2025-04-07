from github import Github

def get_pr_details(token, repo_name, pr_number):
    """
    Fetches the pull request details using the GitHub API.
    """
    github = Github(token)
    repo = github.get_repo(repo_name)
    pr = repo.get_pull(int(pr_number))
    return pr

def post_inline_comment(pr, file_path, position, comment_body):
    """
    Posts an inline comment to a specific line in a pull request.
    """
    try:
        pr.create_review_comment(
            body=comment_body,
            commit_id=pr.head.sha,
            path=file_path,
            position=position
        )
        print(f"Inline comment posted to {file_path} at position {position}")
    except Exception as e:
        print(f"Failed to post inline comment: {e}")
