"""
Accuracy Tracker - Monitors and reports filtering accuracy over time

Tracks how well Claude's filtering matches user preferences over multiple sessions.
This enables the system to measure if it's actually improving.
"""

import json
import os
from datetime import datetime
from typing import Dict, List

from agency.feedback_analyzer import FeedbackAnalyzer


# Path relative to project root
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')


class AccuracyTracker:
    """Tracks Claude's filtering accuracy over time."""

    HISTORY_FILE = os.path.join(DATA_DIR, "accuracy_history.json")

    def __init__(self):
        self.history = self._load_history()

    def _load_history(self) -> Dict:
        try:
            if os.path.exists(self.HISTORY_FILE):
                with open(self.HISTORY_FILE, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

        return {
            "version": "1.0",
            "overall_accuracy": {},
            "by_job_type": {},
            "by_time_period": [],
            "sessions": []
        }

    def record_session(self, tracker_data: Dict):
        """Record accuracy metrics for a review session."""
        analyzer = FeedbackAnalyzer(tracker_data)
        metrics = analyzer.calculate_accuracy_metrics()

        if metrics['total_reviewed'] == 0:
            return

        # Create session record
        session = {
            'timestamp': datetime.now().isoformat(),
            'total_reviewed': metrics['total_reviewed'],
            'liked': metrics['liked'],
            'disliked': metrics['disliked'],
            'maybe': metrics['maybe'],
            'precision': metrics['precision']
        }

        # Add to sessions list
        self.history['sessions'].append(session)

        # Keep only last 50 sessions
        self.history['sessions'] = self.history['sessions'][-50:]

        # Update overall accuracy
        self._update_overall_accuracy()

        # Update time period tracking
        self._update_time_periods()

        self._save_history()

    def _update_overall_accuracy(self):
        """Calculate overall accuracy from all sessions."""
        sessions = self.history['sessions']
        if not sessions:
            return

        total_liked = sum(s['liked'] for s in sessions)
        total_disliked = sum(s['disliked'] for s in sessions)
        total_maybe = sum(s['maybe'] for s in sessions)
        total_reviewed = sum(s['total_reviewed'] for s in sessions)

        if total_reviewed == 0:
            return

        self.history['overall_accuracy'] = {
            'total_reviewed': total_reviewed,
            'total_liked': total_liked,
            'total_disliked': total_disliked,
            'total_maybe': total_maybe,
            'precision': round(total_liked / total_reviewed, 3),
            'last_updated': datetime.now().isoformat()
        }

    def _update_time_periods(self):
        """Group accuracy by week for trend analysis."""
        sessions = self.history['sessions']
        if not sessions:
            return

        # Group sessions by week
        weekly_data = {}
        for session in sessions:
            try:
                dt = datetime.fromisoformat(session['timestamp'])
                week = dt.strftime('%Y-W%W')

                if week not in weekly_data:
                    weekly_data[week] = {
                        'liked': 0,
                        'disliked': 0,
                        'maybe': 0,
                        'total': 0
                    }

                weekly_data[week]['liked'] += session['liked']
                weekly_data[week]['disliked'] += session['disliked']
                weekly_data[week]['maybe'] += session['maybe']
                weekly_data[week]['total'] += session['total_reviewed']
            except (ValueError, KeyError):
                continue

        # Convert to list sorted by week
        periods = []
        for week, data in sorted(weekly_data.items()):
            if data['total'] > 0:
                periods.append({
                    'week': week,
                    'accuracy': round(data['liked'] / data['total'], 3),
                    'sample_size': data['total'],
                    'liked': data['liked'],
                    'disliked': data['disliked']
                })

        self.history['by_time_period'] = periods[-12:]  # Keep last 12 weeks

    def get_accuracy_trend(self) -> Dict:
        """Get accuracy trend over time."""
        periods = self.history.get('by_time_period', [])

        if len(periods) < 2:
            return {
                'trend': 'insufficient_data',
                'message': 'Need at least 2 weeks of data for trend analysis',
                'periods': periods,
                'current_accuracy': periods[-1]['accuracy'] if periods else None
            }

        # Compare recent (last 2 periods) vs older
        recent = periods[-2:]
        older = periods[:-2] if len(periods) > 2 else []

        recent_avg = sum(p['accuracy'] for p in recent) / len(recent)

        if older:
            older_avg = sum(p['accuracy'] for p in older) / len(older)
            if recent_avg > older_avg + 0.05:
                trend = 'improving'
                message = f"Accuracy improving: {older_avg:.0%} -> {recent_avg:.0%}"
            elif recent_avg < older_avg - 0.05:
                trend = 'declining'
                message = f"Accuracy declining: {older_avg:.0%} -> {recent_avg:.0%}"
            else:
                trend = 'stable'
                message = f"Accuracy stable around {recent_avg:.0%}"
        else:
            trend = 'establishing'
            message = f"Current accuracy: {recent_avg:.0%}"

        return {
            'trend': trend,
            'message': message,
            'current_accuracy': round(recent_avg, 3),
            'periods': periods
        }

    def get_summary(self) -> Dict:
        """Get a summary of accuracy tracking."""
        overall = self.history.get('overall_accuracy', {})
        trend = self.get_accuracy_trend()

        return {
            'total_jobs_reviewed': overall.get('total_reviewed', 0),
            'overall_precision': overall.get('precision', 0),
            'trend': trend['trend'],
            'trend_message': trend['message'],
            'sessions_recorded': len(self.history.get('sessions', []))
        }

    def _save_history(self):
        os.makedirs(os.path.dirname(self.HISTORY_FILE), exist_ok=True)
        with open(self.HISTORY_FILE, 'w') as f:
            json.dump(self.history, f, indent=2)
