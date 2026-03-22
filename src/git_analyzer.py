import git
import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

class GitAnalyzer:
    def __init__(self, repo_path: str):
        self.repo = git.Repo(repo_path)
        self.reputation_scores = defaultdict(float)
        
    def calculate_contributor_reputation(self) -> Dict[str, float]:
        '''Calculate reputation scores for all contributors based on:
        - Commit frequency
        - Code longevity
        - Review participation
        - Issue engagement
        '''
        commits = list(self.repo.iter_commits('master'))
        
        for commit in commits:
            author_email = commit.author.email
            
            # Base score from commit
            self._add_commit_score(commit)
            
            # Code longevity score
            self._add_longevity_score(commit)
            
            # Review participation score
            self._add_review_score(commit)
            
        return dict(self.reputation_scores)

    def _add_commit_score(self, commit) -> None:
        '''Add points based on commit size and frequency'''
        author_email = commit.author.email
        
        # Points for commit size (measured by changed lines)
        try:
            stats = commit.stats.total
            changes = stats['insertions'] + stats['deletions']
            size_score = min(changes / 100.0, 5.0)  # Cap at 5 points
            self.reputation_scores[author_email] += size_score
        except:
            pass
            
        # Points for recent activity
        days_old = (datetime.datetime.now() - commit.authored_datetime).days
        recency_score = max(5.0 - (days_old / 30.0), 0)  # More points for recent commits
        self.reputation_scores[author_email] += recency_score

    def _add_longevity_score(self, commit) -> None:
        '''Add points based on how long code survives without being modified'''
        author_email = commit.author.email
        
        try:
            # Get blame info for changed files
            for file in commit.stats.files:
                blame = self.repo.blame('HEAD', file)
                for blame_commit, lines in blame:
                    if blame_commit.author.email == author_email:
                        days_survived = (datetime.datetime.now() - blame_commit.authored_datetime).days
                        longevity_score = min(days_survived / 180.0, 10.0)  # Cap at 10 points
                        self.reputation_scores[author_email] += longevity_score
        except:
            pass

    def _add_review_score(self, commit) -> None:
        '''Add points for code review participation'''
        author_email = commit.author.email
        
        try:
            # Check commit message for review references
            msg = commit.message.lower()
            if 'review' in msg or 'reviewed' in msg or 'reviewing' in msg:
                self.reputation_scores[author_email] += 2.0
                
            # Check for co-authored commits
            if 'co-authored-by' in msg:
                self.reputation_scores[author_email] += 3.0
        except:
            pass

    def get_top_contributors(self, limit: int = 10) -> List[Tuple[str, float]]:
        '''Return top N contributors by reputation score'''
        sorted_scores = sorted(
            self.reputation_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_scores[:limit]

    def get_reputation_percentile(self, email: str) -> float:
        '''Get contributor's reputation percentile'''
        if email not in self.reputation_scores:
            return 0.0
            
        score = self.reputation_scores[email]
        total_contributors = len(self.reputation_scores)
        below_score = sum(1 for s in self.reputation_scores.values() if s <= score)
        
        return (below_score / total_contributors) * 100.0