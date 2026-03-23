import os
import subprocess
import json

class GitAnalyzer:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def get_commit_history(self):
        os.chdir(self.repo_path)
        commit_history = subprocess.check_output(['git', 'log', '--pretty=format:"%h,%an,%ae,%ad,%s"']).decode().strip().split('\n')
        commits = []
        for commit_line in commit_history:
            commit_data = commit_line.strip('"').split(',')
            commits.append({
                'hash': commit_data[0],
                'author_name': commit_data[1],
                'author_email': commit_data[2],
                'date': commit_data[3],
                'message': commit_data[4]
            })
        return commits

    def get_branch_info(self):
        os.chdir(self.repo_path)
        branch_list = subprocess.check_output(['git', 'branch', '-a']).decode().strip().split('\n')
        branches = []
        for branch in branch_list:
            branch_name = branch.strip('* ')
            branches.append(branch_name)
        return branches

    def get_repo_stats(self):
        os.chdir(self.repo_path)
        num_commits = len(self.get_commit_history())
        num_branches = len(self.get_branch_info())
        return {
            'num_commits': num_commits,
            'num_branches': num_branches
        }

    def analyze_repo(self):
        commit_history = self.get_commit_history()
        branch_info = self.get_branch_info()
        repo_stats = self.get_repo_stats()
        return {
            'commit_history': commit_history,
            'branch_info': branch_info,
            'repo_stats': repo_stats
        }
