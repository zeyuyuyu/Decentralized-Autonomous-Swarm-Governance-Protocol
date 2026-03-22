import subprocess
from typing import Dict, List, Optional
from dataclasses import dataclass
import re

@dataclass
class DiffMetrics:
    files_changed: int
    insertions: int 
    deletions: int
    semantic_score: float
    risk_level: str
    affected_components: List[str]

class GitDiffAnalyzer:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.risk_patterns = {
            'high': [r'password', r'token', r'secret', r'auth', r'credential'],
            'medium': [r'config', r'database', r'api', r'security'],
            'low': [r'readme', r'docs', r'comment', r'format']
        }
        
    def get_diff_stats(self, commit_range: Optional[str] = None) -> DiffMetrics:
        """Analyzes git diff and returns statistical and semantic metrics"""
        cmd = ['git', '-C', self.repo_path, 'diff', '--stat']
        if commit_range:
            cmd.append(commit_range)
            
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse basic metrics
        stats = result.stdout.strip().split('\n')[-1]
        files = int(re.search(r'(\d+) files? changed', stats).group(1))
        insertions = int(re.search(r'(\d+) insertion', stats).group(1)) if 'insertion' in stats else 0
        deletions = int(re.search(r'(\d+) deletion', stats).group(1)) if 'deletion' in stats else 0

        # Get full diff for semantic analysis
        diff = subprocess.run(['git', '-C', self.repo_path, 'diff', '--unified=0'],
                            capture_output=True, text=True).stdout

        # Calculate semantic risk score and affected components
        risk_score = self._calculate_risk_score(diff)
        components = self._identify_affected_components(diff)
        
        risk_level = self._classify_risk_level(risk_score)
        
        return DiffMetrics(
            files_changed=files,
            insertions=insertions,
            deletions=deletions,
            semantic_score=risk_score,
            risk_level=risk_level,
            affected_components=components
        )
    
    def _calculate_risk_score(self, diff_content: str) -> float:
        """Calculate a risk score based on pattern matching and heuristics"""
        score = 0.0
        
        for risk_level, patterns in self.risk_patterns.items():
            weight = 1.0 if risk_level == 'high' else 0.5 if risk_level == 'medium' else 0.2
            
            for pattern in patterns:
                matches = len(re.findall(pattern, diff_content, re.IGNORECASE))
                score += matches * weight
                
        return min(score, 10.0)  # Normalize to 0-10 scale
    
    def _identify_affected_components(self, diff_content: str) -> List[str]:
        """Identify main components affected by changes"""
        components = set()
        
        # Extract file paths from diff headers
        for line in diff_content.split('\n'):
            if line.startswith('+++') or line.startswith('---'):
                path = line[4:].strip()
                if path and not path.startswith('/dev/null'):
                    # Extract component from path (e.g., src/auth/login.py -> auth)
                    parts = path.split('/')
                    if len(parts) > 1:
                        components.add(parts[1])
                        
        return sorted(list(components))
    
    def _classify_risk_level(self, score: float) -> str:
        """Classify risk level based on semantic score"""
        if score >= 7.0:
            return 'HIGH'
        elif score >= 4.0:
            return 'MEDIUM'
        else:
            return 'LOW'

    def get_commit_summary(self, commit_hash: str) -> Dict[str, str]:
        """Get detailed commit information"""
        cmd = ['git', '-C', self.repo_path, 'show', '-s',
               '--format=%h%n%an%n%ae%n%at%n%s%n%b', commit_hash]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        
        return {
            'hash': lines[0],
            'author': lines[1],
            'email': lines[2],
            'timestamp': lines[3],
            'subject': lines[4],
            'body': '\n'.join(lines[5:]) if len(lines) > 5 else ''
        }