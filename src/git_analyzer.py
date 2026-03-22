import os
import git
import datetime

class GitAnalyzer:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)

    def get_commit_history(self):
        commits = list(self.repo.iter_commits('master'))
        commit_history = []
        for commit in commits:
            commit_history.append({
                'hash': commit.hexsha,
                'author': commit.author.name,
                'email': commit.author.email,
                'date': commit.committed_datetime.isoformat(),
                'message': commit.message
            })
        return commit_history

    def get_file_changes(self, file_path):
        diffs = self.repo.head.commit.diff(None, paths=file_path)
        file_changes = []
        for diff in diffs:
            file_changes.append({
                'file': diff.a_path,
                'additions': diff.additions,
                'deletions': diff.deletions,
                'lines_changed': diff.additions + diff.deletions
            })
        return file_changes

    def get_branch_info(self):
        branches = self.repo.branches
        branch_info = []
        for branch in branches:
            branch_info.append({
                'name': branch.name,
                'commit_hash': branch.commit.hexsha,
                'commit_date': branch.commit.committed_datetime.isoformat()
            })
        return branch_info

    def get_repository_info(self):
        return {
            'path': self.repo_path,
            'remote_url': self.repo.remote().url,
            'last_commit_date': self.repo.head.commit.committed_datetime.isoformat()
        }