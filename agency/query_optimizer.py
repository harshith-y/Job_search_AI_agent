"""
Query Optimizer - Self-improving search query generation

Level 2 agency: Tracks which search queries produce the best results
(jobs that users actually like) and adjusts query strategy accordingly.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


# Path relative to project root
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')


class QueryOptimizer:
    """Tracks query performance and optimizes future searches."""

    PERFORMANCE_FILE = os.path.join(DATA_DIR, "query_performance.json")

    def __init__(self):
        self.performance = self._load_performance()

    def _load_performance(self) -> Dict:
        try:
            if os.path.exists(self.PERFORMANCE_FILE):
                with open(self.PERFORMANCE_FILE, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

        return {
            "version": "1.0",
            "queries": {},
            "last_updated": None,
            "generated_queries": []
        }

    def record_query_results(self, query: str, jobs_found: int, source: str = "google"):
        """
        Record how many jobs a query found.

        Args:
            query: The search query
            jobs_found: Number of jobs returned
            source: Source type (google, scraper, etc.)
        """
        key = f"{source}:{query[:100]}"  # Limit key length

        if key not in self.performance['queries']:
            self.performance['queries'][key] = {
                'query': query,
                'source': source,
                'total_jobs_found': 0,
                'jobs_liked': 0,
                'jobs_disliked': 0,
                'jobs_maybe': 0,
                'run_count': 0,
                'first_run': datetime.now().isoformat(),
                'last_run': None
            }

        self.performance['queries'][key]['total_jobs_found'] += jobs_found
        self.performance['queries'][key]['run_count'] += 1
        self.performance['queries'][key]['last_run'] = datetime.now().isoformat()

        self._save_performance()

    def update_query_feedback(self, job_url: str, source_query: Optional[str], status: str):
        """
        Update query performance based on user feedback on a job.

        Args:
            job_url: URL of the job
            source_query: The query that found this job (if known)
            status: User's feedback (liked, disliked, maybe)
        """
        if not source_query:
            return

        # Find matching query in our records
        for key, data in self.performance['queries'].items():
            if source_query in data.get('query', ''):
                if status == 'liked':
                    data['jobs_liked'] += 1
                elif status == 'disliked':
                    data['jobs_disliked'] += 1
                elif status == 'maybe':
                    data['jobs_maybe'] += 1
                break

        self._save_performance()

    def get_query_effectiveness(self) -> List[Dict]:
        """
        Get queries ranked by effectiveness.

        Returns:
            List of query performance data, sorted by effectiveness
        """
        results = []

        for key, data in self.performance['queries'].items():
            total_feedback = data.get('jobs_liked', 0) + data.get('jobs_disliked', 0)

            if total_feedback > 0:
                effectiveness = data['jobs_liked'] / total_feedback
            elif data.get('total_jobs_found', 0) > 0:
                effectiveness = 0.5  # Unknown, assume neutral
            else:
                effectiveness = 0

            results.append({
                'query': data.get('query', key),
                'source': data.get('source', 'unknown'),
                'effectiveness': round(effectiveness, 3),
                'total_jobs': data.get('total_jobs_found', 0),
                'liked': data.get('jobs_liked', 0),
                'disliked': data.get('jobs_disliked', 0),
                'maybe': data.get('jobs_maybe', 0),
                'run_count': data.get('run_count', 0),
                'feedback_count': total_feedback
            })

        return sorted(results, key=lambda x: (x['feedback_count'] > 0, x['effectiveness']), reverse=True)

    def suggest_query_adjustments(self) -> List[Dict]:
        """
        Suggest which queries to keep, drop, or modify.

        Returns:
            List of suggestions for query adjustments
        """
        suggestions = []
        effectiveness = self.get_query_effectiveness()

        for q in effectiveness:
            total_feedback = q['liked'] + q['disliked']

            if total_feedback < 3:
                continue  # Not enough data

            if q['effectiveness'] < 0.15:
                suggestions.append({
                    'query': q['query'],
                    'action': 'drop',
                    'reason': f"Very low effectiveness ({q['effectiveness']:.0%})",
                    'stats': f"{q['liked']} liked vs {q['disliked']} disliked",
                    'priority': 'high'
                })
            elif q['effectiveness'] < 0.3:
                suggestions.append({
                    'query': q['query'],
                    'action': 'review',
                    'reason': f"Low effectiveness ({q['effectiveness']:.0%})",
                    'stats': f"{q['liked']} liked vs {q['disliked']} disliked",
                    'priority': 'medium'
                })
            elif q['effectiveness'] > 0.6 and total_feedback >= 5:
                suggestions.append({
                    'query': q['query'],
                    'action': 'expand',
                    'reason': f"High effectiveness ({q['effectiveness']:.0%})",
                    'stats': f"{q['liked']} liked vs {q['disliked']} disliked",
                    'priority': 'high'
                })
            elif q['effectiveness'] > 0.5:
                suggestions.append({
                    'query': q['query'],
                    'action': 'keep',
                    'reason': f"Good effectiveness ({q['effectiveness']:.0%})",
                    'stats': f"{q['liked']} liked vs {q['disliked']} disliked",
                    'priority': 'low'
                })

        return sorted(suggestions, key=lambda x: x['priority'] == 'high', reverse=True)

    def generate_new_queries(self, learned_patterns: Dict) -> List[str]:
        """
        Generate new search queries based on learned patterns.

        Args:
            learned_patterns: Patterns from FeedbackAnalyzer

        Returns:
            List of suggested new queries
        """
        new_queries = []

        positives = learned_patterns.get('differential_signals', {}).get('strong_positives', {})
        liked_companies = learned_patterns.get('differential_signals', {}).get('liked_companies', {})

        # Generate queries from strong positive keywords
        for keyword, data in list(positives.items())[:5]:
            if data.get('ratio', 0) > 2.0:
                # Strong signal - create queries
                new_queries.append(f'"{keyword}" UK job graduate')
                new_queries.append(f'site:greenhouse.io "{keyword}" UK')
                new_queries.append(f'site:lever.co "{keyword}" UK')

        # Generate queries for liked companies
        for company in list(liked_companies.keys())[:3]:
            new_queries.append(f'site:{company.replace(" ", "")}.com careers')
            new_queries.append(f'"{company}" careers graduate UK')

        # Store generated queries
        for q in new_queries:
            if q not in self.performance.get('generated_queries', []):
                self.performance.setdefault('generated_queries', []).append(q)

        self._save_performance()

        return new_queries

    def get_summary(self) -> Dict:
        """Get a summary of query optimization."""
        effectiveness = self.get_query_effectiveness()
        suggestions = self.suggest_query_adjustments()

        high_performers = [q for q in effectiveness if q['effectiveness'] > 0.5 and q['feedback_count'] >= 3]
        low_performers = [q for q in effectiveness if q['effectiveness'] < 0.3 and q['feedback_count'] >= 3]

        return {
            'total_queries_tracked': len(self.performance.get('queries', {})),
            'queries_with_feedback': len([q for q in effectiveness if q['feedback_count'] > 0]),
            'high_performers': len(high_performers),
            'low_performers': len(low_performers),
            'suggestions': len(suggestions),
            'generated_queries': len(self.performance.get('generated_queries', []))
        }

    def get_report(self) -> str:
        """Generate a human-readable report."""
        effectiveness = self.get_query_effectiveness()
        suggestions = self.suggest_query_adjustments()

        lines = []
        lines.append("QUERY PERFORMANCE REPORT")
        lines.append("=" * 50)

        # Top performers
        top = [q for q in effectiveness if q['effectiveness'] > 0.5 and q['feedback_count'] >= 3][:5]
        if top:
            lines.append("\nTOP PERFORMING QUERIES:")
            for q in top:
                lines.append(f"  [{q['effectiveness']:.0%}] {q['query'][:50]}...")
                lines.append(f"       {q['liked']} liked, {q['disliked']} disliked")

        # Bottom performers
        bottom = [q for q in effectiveness if q['effectiveness'] < 0.3 and q['feedback_count'] >= 3][:5]
        if bottom:
            lines.append("\nLOW PERFORMING QUERIES:")
            for q in bottom:
                lines.append(f"  [{q['effectiveness']:.0%}] {q['query'][:50]}...")
                lines.append(f"       Consider removing or modifying")

        # Suggestions
        if suggestions:
            lines.append("\nRECOMMENDATIONS:")
            for s in suggestions[:5]:
                lines.append(f"  [{s['action'].upper()}] {s['query'][:40]}...")
                lines.append(f"       {s['reason']}")

        lines.append("\n" + "=" * 50)

        return '\n'.join(lines)

    def _save_performance(self):
        self.performance['last_updated'] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(self.PERFORMANCE_FILE), exist_ok=True)
        with open(self.PERFORMANCE_FILE, 'w') as f:
            json.dump(self.performance, f, indent=2)
