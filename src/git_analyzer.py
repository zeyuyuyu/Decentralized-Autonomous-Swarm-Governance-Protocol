import git
import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

class GitAnalyzer:
    def __init__(self, repo_path: str):
        self.repo = git.Repo(repo_path)
        self.contribution_metrics = {}
    
    def analyze_contributions(self, days_back: int = 90) -> Dict:
        """Analyze git contributions and generate metrics over specified time period"""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_back)
        commits = list(self.repo.iter_commits('main'))
        
        author_stats = defaultdict(lambda: {
            'commit_count': 0,
            'lines_added': 0,
            'lines_removed': 0,
            'files_modified': set(),
            'commit_dates': []
        })

        for commit in commits:
            if datetime.datetime.fromtimestamp(commit.committed_date) < cutoff_date:
                continue
                
            stats = commit.stats.total
            author = commit.author.email
            
            author_stats[author]['commit_count'] += 1
            author_stats[author]['lines_added'] += stats['insertions']
            author_stats[author]['lines_removed'] += stats['deletions'] 
            author_stats[author]['commit_dates'].append(commit.committed_date)
            
            for item in commit.stats.files:
                author_stats[author]['files_modified'].add(item)

        # Calculate additional metrics
        for author in author_stats:
            dates = author_stats[author]['commit_dates']
            if len(dates) > 1:
                date_diffs = []
                sorted_dates = sorted(dates)
                for i in range(len(sorted_dates)-1):
                    diff = sorted_dates[i+1] - sorted_dates[i]
                    date_diffs.append(diff)
                avg_time_between_commits = sum(date_diffs) / len(date_diffs)
                author_stats[author]['avg_hours_between_commits'] = avg_time_between_commits / 3600
            
            author_stats[author]['files_modified'] = len(author_stats[author]['files_modified'])
            del author_stats[author]['commit_dates']

        self.contribution_metrics = dict(author_stats)
        return self.contribution_metrics

    def get_hotspots(self) -> List[Tuple[str, int]]:
        """Identify code hotspots - files with most frequent changes"""
        file_changes = defaultdict(int)
        
        for commit in self.repo.iter_commits('main'):
            for file in commit.stats.files:
                file_changes[file] += 1
                
        return sorted(file_changes.items(), key=lambda x: x[1], reverse=True)

    def get_contribution_summary(self) -> Dict:
        """Generate a high-level summary of repository contributions"""
        if not self.contribution_metrics:
            self.analyze_contributions()
            
        total_commits = sum(author['commit_count'] for author in self.contribution_metrics.values())
        total_lines_added = sum(author['lines_added'] for author in self.contribution_metrics.values())
        total_lines_removed = sum(author['lines_removed'] for author in self.contribution_metrics.values())
        
        return {
            'total_contributors': len(self.contribution_metrics),
            'total_commits': total_commits,
            'total_lines_added': total_lines_added,
            'total_lines_removed': total_lines_removed,
            'top_contributors': sorted(
                self.contribution_metrics.items(),
                key=lambda x: x[1]['commit_count'],
                reverse=True
            )[:5]
        }

    def get_author_impact(self, author_email: str) -> Dict:
        """Get detailed impact metrics for a specific author"""
        if not self.contribution_metrics:
            self.analyze_contributions()
            
        if author_email not in self.contribution_metrics:
            return {}
            
        author_stats = self.contribution_metrics[author_email]
        total_commits = sum(a['commit_count'] for a in self.contribution_metrics.values())
        total_lines = sum(a['lines_added'] + a['lines_removed'] for a in self.contribution_metrics.values())
        
        return {
            **author_stats,
            'commit_percentage': (author_stats['commit_count'] / total_commits) * 100,
            'code_change_percentage': ((author_stats['lines_added'] + author_stats['lines_removed']) / total_lines) * 100
        }