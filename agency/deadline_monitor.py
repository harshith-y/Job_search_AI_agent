"""
Deadline Monitor - Proactive tracking and alerts for job deadlines

Level 2 agency: The system proactively watches deadlines for jobs
the user has liked or marked as maybe, and generates alerts.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class DeadlineMonitor:
    """Monitors deadlines for liked/maybe jobs and generates alerts."""

    def __init__(self, tracker_data: Dict):
        """
        Initialize with tracker data.

        Args:
            tracker_data: Dictionary of jobs from EnhancedJobTracker.jobs
        """
        self.jobs = tracker_data

    def check_deadlines(self, warn_days: int = 7) -> List[Dict]:
        """
        Check for upcoming deadlines on liked/maybe jobs.

        Args:
            warn_days: Number of days before deadline to start warning

        Returns:
            List of deadline alerts sorted by urgency
        """
        alerts = []
        now = datetime.now()

        for url, job in self.jobs.items():
            status = job.get('status', '')

            # Only track jobs user has shown interest in
            if status not in ['liked', 'maybe', 'new']:
                continue

            deadline_str = job.get('deadline', '')
            if not deadline_str or deadline_str in ['Not specified', 'Not Specified', 'N/A', '']:
                continue

            deadline = self._parse_deadline(deadline_str)
            if not deadline:
                continue

            days_remaining = (deadline - now).days

            # Create alert based on urgency
            if days_remaining < 0:
                # Already passed
                alerts.append(self._create_alert(
                    url, job, deadline_str, days_remaining,
                    urgency='expired',
                    action=f"Deadline passed {abs(days_remaining)} days ago - check if still accepting"
                ))
            elif days_remaining <= 2:
                # Very urgent
                alerts.append(self._create_alert(
                    url, job, deadline_str, days_remaining,
                    urgency='critical',
                    action=f"Only {days_remaining} day(s) left! Apply NOW!"
                ))
            elif days_remaining <= 5:
                # Urgent
                alerts.append(self._create_alert(
                    url, job, deadline_str, days_remaining,
                    urgency='urgent',
                    action=f"Apply within {days_remaining} days"
                ))
            elif days_remaining <= warn_days:
                # Warning
                alerts.append(self._create_alert(
                    url, job, deadline_str, days_remaining,
                    urgency='warning',
                    action=f"Deadline approaching in {days_remaining} days"
                ))

        # Sort by urgency (critical first) then by days remaining
        urgency_order = {'critical': 0, 'urgent': 1, 'warning': 2, 'expired': 3}
        alerts.sort(key=lambda x: (urgency_order.get(x['urgency'], 99), x['days_remaining']))

        return alerts

    def _create_alert(self, url: str, job: Dict, deadline_str: str,
                      days_remaining: int, urgency: str, action: str) -> Dict:
        """Create a deadline alert dictionary."""
        return {
            'type': 'deadline_alert',
            'urgency': urgency,
            'job_url': url,
            'job_title': job.get('title', 'Unknown'),
            'company': job.get('company', 'Unknown'),
            'deadline': deadline_str,
            'days_remaining': days_remaining,
            'status': job.get('status', 'unknown'),
            'action_needed': action,
            'location': job.get('city') or job.get('location', '')
        }

    def _parse_deadline(self, deadline_str: str) -> Optional[datetime]:
        """Parse deadline string into datetime."""
        if not deadline_str:
            return None

        deadline_lower = deadline_str.lower().strip()
        original_text = deadline_str.strip()

        # Month name mappings
        month_map = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9, 'sept': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12,
        }

        # Pattern 1: "31 December 2024" or "31 Dec 2024"
        match = re.search(
            r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\s+(\d{4})',
            deadline_lower
        )
        if match:
            day = int(match.group(1))
            month = month_map.get(match.group(2), 1)
            year = int(match.group(3))
            try:
                return datetime(year, month, day)
            except ValueError:
                pass

        # Pattern 2: "December 31, 2024"
        match = re.search(
            r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\s+(\d{1,2}),?\s+(\d{4})',
            deadline_lower
        )
        if match:
            month = month_map.get(match.group(1), 1)
            day = int(match.group(2))
            year = int(match.group(3))
            try:
                return datetime(year, month, day)
            except ValueError:
                pass

        # Pattern 3: "31/12/2024" or "31-12-2024" (UK format: DD/MM/YYYY)
        match = re.search(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', original_text)
        if match:
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))
            if day <= 31 and month <= 12:
                try:
                    return datetime(year, month, day)
                except ValueError:
                    pass

        # Pattern 4: "2024-12-31" (ISO format)
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})', original_text)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            try:
                return datetime(year, month, day)
            except ValueError:
                pass

        # Pattern 5: Just "31 December" - assume next occurrence
        match = re.search(
            r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)',
            deadline_lower
        )
        if match:
            day = int(match.group(1))
            month = month_map.get(match.group(2), 1)
            year = datetime.now().year
            try:
                parsed = datetime(year, month, day)
                # If date is in the past, assume next year
                if parsed < datetime.now() - timedelta(days=30):
                    parsed = datetime(year + 1, month, day)
                return parsed
            except ValueError:
                pass

        return None

    def get_urgent_alerts(self, max_days: int = 5) -> List[Dict]:
        """Get only urgent alerts (deadlines within max_days)."""
        all_alerts = self.check_deadlines(warn_days=max_days)
        return [a for a in all_alerts if a['urgency'] in ['critical', 'urgent']]

    def generate_report(self, warn_days: int = 7) -> str:
        """Generate a human-readable deadline report."""
        alerts = self.check_deadlines(warn_days)

        if not alerts:
            return "No upcoming deadlines for your liked/maybe jobs."

        lines = []
        lines.append("=" * 50)
        lines.append("DEADLINE ALERTS")
        lines.append("=" * 50)

        # Group by urgency
        critical = [a for a in alerts if a['urgency'] == 'critical']
        urgent = [a for a in alerts if a['urgency'] == 'urgent']
        warnings = [a for a in alerts if a['urgency'] == 'warning']
        expired = [a for a in alerts if a['urgency'] == 'expired']

        if critical:
            lines.append("\n!!! CRITICAL - 2 DAYS OR LESS !!!")
            for a in critical:
                lines.append(f"  [{a['status'].upper()}] {a['job_title']}")
                lines.append(f"           @ {a['company']}")
                lines.append(f"           Deadline: {a['deadline']} ({a['days_remaining']} days)")

        if urgent:
            lines.append("\n!! URGENT - 5 DAYS OR LESS !!")
            for a in urgent:
                lines.append(f"  [{a['status'].upper()}] {a['job_title']}")
                lines.append(f"           @ {a['company']}")
                lines.append(f"           Deadline: {a['deadline']} ({a['days_remaining']} days)")

        if warnings:
            lines.append(f"\nUPCOMING (within {warn_days} days):")
            for a in warnings:
                lines.append(f"  [{a['status'].upper()}] {a['job_title']}")
                lines.append(f"           @ {a['company']} - {a['days_remaining']} days left")

        if expired:
            lines.append("\nEXPIRED (check if still accepting):")
            for a in expired:
                lines.append(f"  [{a['status'].upper()}] {a['job_title']} @ {a['company']}")
                lines.append(f"           Deadline was: {a['deadline']}")

        lines.append("\n" + "=" * 50)

        return '\n'.join(lines)

    def get_stats(self) -> Dict:
        """Get deadline monitoring stats."""
        alerts = self.check_deadlines(warn_days=14)

        return {
            'total_tracked': len([j for j in self.jobs.values() if j.get('status') in ['liked', 'maybe']]),
            'with_deadlines': len(alerts),
            'critical': len([a for a in alerts if a['urgency'] == 'critical']),
            'urgent': len([a for a in alerts if a['urgency'] == 'urgent']),
            'upcoming': len([a for a in alerts if a['urgency'] == 'warning']),
            'expired': len([a for a in alerts if a['urgency'] == 'expired'])
        }
