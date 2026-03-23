import git
import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

class GitAnalyzer:
    def __init__(self, repo_path: str):
        self.repo = git.Repo(repo_path)
        self.contribution_scores = defaultdict(float)
        self.influence_weights = {
            'commit': 1.0,
            'code_change': 0.01,  # per line
            'merge': 2.0,
            'review': 1.5
        }

    def analyze_contributions(self, start_date: datetime.datetime = None) -> Dict[str, float]:
        """Analyzes git history to compute developer influence scores"""
        commits = list(self.repo.iter_commits())
        
        for commit in commits:
            if start_date and commit.committed_datetime < start_date:
                continue
                
            # Base commit score
            self.contribution_scores[commit.author.email] += self.influence_weights['commit']
            
            # Code change impact
            if len(commit.parents) > 0:
                diffs = commit.parents[0].diff(commit)
                lines_changed = sum(d.change_type != 'D' and d.diff.count(b'\n') or 0 
                                  for d in diffs)
                self.contribution_scores[commit.author.email] += (
                    lines_changed * self.influence_weights['code_change']
                )
            
            # Merge contribution
            if len(commit.parents) > 1:
                self.contribution_scores[commit.author.email] += self.influence_weights['merge']

        return dict(self.contribution_scores)

    def get_top_contributors(self, limit: int = 10) -> List[Tuple[str, float]]:
        """Returns top contributors sorted by influence score"""
        sorted_scores = sorted(
            self.contribution_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_scores[:limit]

    def get_contribution_timeline(self, email: str) -> List[Tuple[datetime.datetime, int]]:
        """Gets timeline of contributions for a specific developer"""
        timeline = []
        for commit in self.repo.iter_commits(author=email):
            timeline.append((commit.committed_datetime, 1))
        return sorted(timeline)

    def calculate_team_collaboration_score(self) -> float:
        """Calculates overall team collaboration metric"""
        if not self.contribution_scores:
            self.analyze_contributions()
            
        total_score = sum(self.contribution_scores.values())
        num_contributors = len(self.contribution_scores)
        
        if num_contributors <= 1:
            return 0.0
            
        # Calculate standard deviation of contributions
        mean = total_score / num_contributors
        variance = sum((score - mean) ** 2 for score in self.contribution_scores.values()) / num_contributors
        std_dev = variance ** 0.5
        
        # Higher collaboration score when contributions are more evenly distributed
        collaboration_score = 1.0 / (1.0 + std_dev/mean)
        return round(collaboration_score, 3)

    def export_metrics(self) -> Dict:
        """Exports all calculated metrics"""
        if not self.contribution_scores:
            self.analyze_contributions()
            
        return {
            'total_contributors': len(self.contribution_scores),
            'total_contribution_score': sum(self.contribution_scores.values()),
            'collaboration_score': self.calculate_team_collaboration_score(),
            'top_contributors': self.get_top_contributors(),
            'contribution_scores': dict(self.contribution_scores)
        }