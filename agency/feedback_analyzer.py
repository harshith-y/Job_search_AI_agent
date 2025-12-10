"""
Feedback Analyzer - Extracts patterns from user's like/dislike decisions

This is the core of Level 1 agency: learning what the user actually wants
based on their feedback, not just what they say they want in preferences.
"""

from typing import Dict, List
from collections import Counter
import re


class FeedbackAnalyzer:
    """Analyzes user feedback to discover preference patterns."""

    def __init__(self, tracker_data: Dict):
        """
        Initialize with tracker data.

        Args:
            tracker_data: Dictionary of jobs from EnhancedJobTracker.jobs
        """
        self.jobs = tracker_data

    def get_jobs_by_status(self, status: str) -> List[Dict]:
        """Get all jobs with a specific status."""
        return [job for job in self.jobs.values() if job.get('status') == status]

    def extract_patterns(self) -> Dict:
        """
        Extract patterns from liked vs disliked jobs.
        Returns discovered positive and negative signals.
        """
        liked_jobs = self.get_jobs_by_status('liked')
        disliked_jobs = self.get_jobs_by_status('disliked')
        maybe_jobs = self.get_jobs_by_status('maybe')

        patterns = {
            'positive_signals': self._analyze_jobs(liked_jobs),
            'negative_signals': self._analyze_jobs(disliked_jobs),
            'uncertain_signals': self._analyze_jobs(maybe_jobs),
            'differential_signals': self._find_differentiators(liked_jobs, disliked_jobs),
            'stats': {
                'liked_count': len(liked_jobs),
                'disliked_count': len(disliked_jobs),
                'maybe_count': len(maybe_jobs),
                'total_reviewed': len(liked_jobs) + len(disliked_jobs) + len(maybe_jobs)
            }
        }

        return patterns

    def _analyze_jobs(self, jobs: List[Dict]) -> Dict:
        """Extract common patterns from a list of jobs."""
        companies = Counter()
        title_words = Counter()
        technologies = Counter()
        locations = Counter()
        job_types = Counter()

        # Keywords to look for in descriptions
        tech_keywords = [
            'pytorch', 'tensorflow', 'python', 'ml', 'ai', 'machine learning',
            'deep learning', 'healthcare', 'medical', 'clinical', 'biomedical',
            'data science', 'computer vision', 'nlp', 'research', 'graduate',
            'scheme', 'programme', 'junior', 'entry', 'intern'
        ]

        for job in jobs:
            # Company analysis
            company = (job.get('company') or '').lower().strip()
            if company and company not in ['unknown', 'linkedin job', 'indeed listing', 'glassdoor listing']:
                companies[company] += 1

            # Title keyword analysis
            title = (job.get('title') or '').lower()
            # Extract meaningful words (3+ chars, not common words)
            words = re.findall(r'\b[a-z]{3,}\b', title)
            stop_words = {'the', 'and', 'for', 'with', 'this', 'that', 'are', 'from', 'will', 'have', 'has'}
            for word in words:
                if word not in stop_words:
                    title_words[word] += 1

            # Technology extraction from description + summary
            desc = ((job.get('description') or '') + ' ' + (job.get('ai_summary') or '')).lower()
            for tech in tech_keywords:
                if tech in desc:
                    technologies[tech] += 1

            # Location analysis
            location = (job.get('city') or job.get('location') or '').lower()
            if location:
                locations[location] += 1

            # Job type analysis
            job_type = (job.get('type') or job.get('job_type') or '').lower()
            if job_type:
                job_types[job_type] += 1

        return {
            'companies': dict(companies.most_common(15)),
            'title_keywords': dict(title_words.most_common(30)),
            'technologies': dict(technologies.most_common(15)),
            'locations': dict(locations.most_common(10)),
            'job_types': dict(job_types.most_common(5))
        }

    def _find_differentiators(self, liked: List[Dict], disliked: List[Dict]) -> Dict:
        """Find keywords that strongly differentiate liked from disliked."""
        liked_patterns = self._analyze_jobs(liked)
        disliked_patterns = self._analyze_jobs(disliked)

        # Find words that appear much more in liked than disliked
        strong_positives = {}
        for word, count in liked_patterns['title_keywords'].items():
            disliked_count = disliked_patterns['title_keywords'].get(word, 0)
            # Word appears at least twice in liked and ratio is > 2x
            if count >= 2 and count > disliked_count * 2:
                strong_positives[word] = {
                    'liked_count': count,
                    'disliked_count': disliked_count,
                    'ratio': round(count / max(disliked_count, 1), 2)
                }

        # Find words that appear much more in disliked than liked
        strong_negatives = {}
        for word, count in disliked_patterns['title_keywords'].items():
            liked_count = liked_patterns['title_keywords'].get(word, 0)
            # Word appears at least twice in disliked and ratio is > 2x
            if count >= 2 and count > liked_count * 2:
                strong_negatives[word] = {
                    'liked_count': liked_count,
                    'disliked_count': count,
                    'ratio': round(count / max(liked_count, 1), 2)
                }

        # Find companies that are consistently liked/disliked
        liked_companies = {}
        for company, count in liked_patterns['companies'].items():
            if count >= 2:
                disliked_count = disliked_patterns['companies'].get(company, 0)
                if count > disliked_count:
                    liked_companies[company] = {
                        'liked_count': count,
                        'disliked_count': disliked_count
                    }

        disliked_companies = {}
        for company, count in disliked_patterns['companies'].items():
            if count >= 2:
                liked_count = liked_patterns['companies'].get(company, 0)
                if count > liked_count:
                    disliked_companies[company] = {
                        'liked_count': liked_count,
                        'disliked_count': count
                    }

        return {
            'strong_positives': strong_positives,
            'strong_negatives': strong_negatives,
            'liked_companies': liked_companies,
            'disliked_companies': disliked_companies
        }

    def calculate_accuracy_metrics(self) -> Dict:
        """Calculate Claude's filtering accuracy based on user feedback."""
        liked = len(self.get_jobs_by_status('liked'))
        maybe = len(self.get_jobs_by_status('maybe'))
        disliked = len(self.get_jobs_by_status('disliked'))

        total_reviewed = liked + maybe + disliked

        if total_reviewed == 0:
            return {
                'accuracy': 0,
                'precision': 0,
                'total_reviewed': 0,
                'message': 'No feedback data yet'
            }

        # Jobs Claude thought were good (passed filter) but user disliked = false positives
        false_positive_rate = disliked / total_reviewed

        # Jobs user actually liked = true positives
        true_positive_rate = liked / total_reviewed

        # Precision: of all jobs shown, how many did user actually like?
        precision = liked / total_reviewed

        # Maybe jobs are "uncertain" - could go either way
        uncertain_rate = maybe / total_reviewed

        return {
            'total_reviewed': total_reviewed,
            'liked': liked,
            'maybe': maybe,
            'disliked': disliked,
            'true_positive_rate': round(true_positive_rate, 3),
            'false_positive_rate': round(false_positive_rate, 3),
            'uncertain_rate': round(uncertain_rate, 3),
            'precision': round(precision, 3),
            'message': self._get_accuracy_message(precision, total_reviewed)
        }

    def _get_accuracy_message(self, precision: float, total: int) -> str:
        """Generate a human-readable accuracy message."""
        if total < 10:
            return "Not enough data yet (need 10+ reviews)"
        elif precision >= 0.6:
            return "Excellent! Filtering is well-calibrated to your preferences"
        elif precision >= 0.4:
            return "Good calibration, with room for improvement"
        elif precision >= 0.2:
            return "Moderate accuracy - learning from your feedback to improve"
        else:
            return "Low accuracy - significant learning needed"
