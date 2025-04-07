from github import Github

def get_pr_details(token, repo_name, pr_number):
    github = Github(token)
    repo = github.get_repo(repo_name)
    pr = repo.get_pull(int(pr_number))
    return pr
