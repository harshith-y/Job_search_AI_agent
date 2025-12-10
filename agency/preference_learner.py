"""
Preference Learner - Updates PERSONALIZATION_NOTES dynamically based on feedback

This is the key component that closes the feedback loop:
User reviews jobs -> Patterns extracted -> Claude's prompts updated -> Better filtering
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional

from agency.feedback_analyzer import FeedbackAnalyzer


# Path relative to project root
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')


class PreferenceLearner:
    """Learns and updates preferences from user feedback."""

    LEARNED_PREFS_FILE = os.path.join(DATA_DIR, "learned_preferences.json")

    def __init__(self):
        self.learned_prefs = self._load_learned_preferences()

    def _load_learned_preferences(self) -> Dict:
        """Load existing learned preferences or create empty structure."""
        try:
            if os.path.exists(self.LEARNED_PREFS_FILE):
                with open(self.LEARNED_PREFS_FILE, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"   Warning: Could not load learned preferences: {e}")

        return self._create_empty_structure()

    def _create_empty_structure(self) -> Dict:
        return {
            "version": "1.0",
            "last_updated": None,
            "learning_stats": {
                "total_feedback_processed": 0,
                "liked_count": 0,
                "disliked_count": 0,
                "maybe_count": 0
            },
            "discovered_patterns": {
                "positive_signals": {},
                "negative_signals": {},
                "differential_signals": {}
            },
            "dynamic_personalization_notes": "",
            "strictness_adjustment": {
                "current": "moderate",
                "recommended": "moderate",
                "reason": "No feedback data yet"
            }
        }

    def learn_from_feedback(self, tracker_data: Dict) -> Dict:
        """
        Analyze tracker data and update learned preferences.
        Returns a summary of what was learned.
        """
        analyzer = FeedbackAnalyzer(tracker_data)

        # Extract patterns
        patterns = analyzer.extract_patterns()
        accuracy = analyzer.calculate_accuracy_metrics()

        # Update learned preferences
        self.learned_prefs['last_updated'] = datetime.now().isoformat()
        self.learned_prefs['learning_stats'] = {
            'total_feedback_processed': accuracy['total_reviewed'],
            'liked_count': accuracy['liked'],
            'disliked_count': accuracy['disliked'],
            'maybe_count': accuracy['maybe'],
            'precision': accuracy['precision']
        }
        self.learned_prefs['discovered_patterns'] = patterns

        # Generate dynamic personalization notes
        self.learned_prefs['dynamic_personalization_notes'] = self._generate_notes(patterns, accuracy)

        # Recommend strictness adjustment
        self.learned_prefs['strictness_adjustment'] = self._recommend_strictness(accuracy)

        # Save
        self._save_learned_preferences()

        return {
            'patterns_found': len(patterns.get('differential_signals', {}).get('strong_positives', {})),
            'negative_patterns_found': len(patterns.get('differential_signals', {}).get('strong_negatives', {})),
            'accuracy': accuracy,
            'notes_generated': bool(self.learned_prefs['dynamic_personalization_notes']),
            'strictness_recommendation': self.learned_prefs['strictness_adjustment']['recommended']
        }

    def _generate_notes(self, patterns: Dict, accuracy: Dict) -> str:
        """Generate human-readable notes for Claude's prompt."""
        notes = []
        notes.append("=" * 50)
        notes.append("LEARNED FROM USER FEEDBACK")
        notes.append("=" * 50)

        total = accuracy.get('total_reviewed', 0)
        if total < 5:
            notes.append(f"\n(Only {total} jobs reviewed so far - need more data)")
            return '\n'.join(notes)

        # Stats summary
        notes.append(f"\nFeedback summary: {accuracy['liked']} liked, {accuracy['disliked']} disliked, {accuracy['maybe']} maybe")
        notes.append(f"Current precision: {accuracy['precision']:.0%}")

        # Strong positive signals
        positives = patterns.get('differential_signals', {}).get('strong_positives', {})
        if positives:
            top_positives = sorted(positives.items(), key=lambda x: x[1]['ratio'], reverse=True)[:7]
            notes.append("\nSTRONGLY PREFERRED (user consistently likes these keywords):")
            for word, data in top_positives:
                notes.append(f"  + '{word}' (liked {data['liked_count']}x vs disliked {data['disliked_count']}x)")

        # Strong negative signals
        negatives = patterns.get('differential_signals', {}).get('strong_negatives', {})
        if negatives:
            top_negatives = sorted(negatives.items(), key=lambda x: x[1]['ratio'], reverse=True)[:7]
            notes.append("\nSTRONGLY AVOIDED (user consistently dislikes these keywords):")
            for word, data in top_negatives:
                notes.append(f"  - '{word}' (disliked {data['disliked_count']}x vs liked {data['liked_count']}x)")

        # Liked companies
        liked_companies = patterns.get('differential_signals', {}).get('liked_companies', {})
        if liked_companies:
            notes.append("\nPREFERRED COMPANIES (user has liked multiple jobs from):")
            for company, data in list(liked_companies.items())[:5]:
                notes.append(f"  + {company} ({data['liked_count']} liked)")

        # Disliked companies
        disliked_companies = patterns.get('differential_signals', {}).get('disliked_companies', {})
        if disliked_companies:
            notes.append("\nAVOIDED COMPANIES (user has disliked multiple jobs from):")
            for company, data in list(disliked_companies.items())[:5]:
                notes.append(f"  - {company} ({data['disliked_count']} disliked)")

        # Accuracy-based guidance
        precision = accuracy.get('precision', 0)
        if precision < 0.3:
            notes.append(f"\nFILTERING GUIDANCE: User only liked {precision:.0%} of suggestions.")
            notes.append("  -> Be MORE selective! Apply stricter criteria.")
            notes.append("  -> Prioritize jobs with the STRONGLY PREFERRED keywords above.")
        elif precision > 0.6:
            notes.append(f"\nFILTERING GUIDANCE: User liked {precision:.0%} of suggestions.")
            notes.append("  -> Good calibration! Continue with current approach.")

        notes.append("\n" + "=" * 50)

        return '\n'.join(notes)

    def _recommend_strictness(self, accuracy: Dict) -> Dict:
        """Recommend strictness level based on accuracy metrics."""
        precision = accuracy.get('precision', 0.5)
        total = accuracy.get('total_reviewed', 0)

        if total < 10:
            return {
                "current": "moderate",
                "recommended": "moderate",
                "reason": "Not enough feedback data yet (need 10+ reviews)"
            }

        if precision < 0.2:
            return {
                "current": "lenient",
                "recommended": "strict",
                "reason": f"Very low precision ({precision:.0%}) - too many irrelevant jobs passing filter"
            }
        elif precision < 0.35:
            return {
                "current": "lenient",
                "recommended": "moderate",
                "reason": f"Low precision ({precision:.0%}) - tighten filtering somewhat"
            }
        elif precision < 0.5:
            return {
                "current": "moderate",
                "recommended": "moderate",
                "reason": f"Moderate precision ({precision:.0%}) - filtering calibrated reasonably"
            }
        elif precision < 0.7:
            return {
                "current": "moderate",
                "recommended": "lenient",
                "reason": f"Good precision ({precision:.0%}) - could explore more opportunities"
            }
        else:
            return {
                "current": "strict",
                "recommended": "very_lenient",
                "reason": f"High precision ({precision:.0%}) - may be missing good opportunities, try wider net"
            }

    def get_dynamic_notes(self) -> str:
        """Get the current dynamic personalization notes for Claude."""
        return self.learned_prefs.get('dynamic_personalization_notes', '')

    def get_strictness_recommendation(self) -> str:
        """Get the recommended strictness level."""
        return self.learned_prefs.get('strictness_adjustment', {}).get('recommended', 'moderate')

    def get_learning_summary(self) -> Dict:
        """Get a summary of what has been learned."""
        return {
            'last_updated': self.learned_prefs.get('last_updated'),
            'stats': self.learned_prefs.get('learning_stats', {}),
            'strictness': self.learned_prefs.get('strictness_adjustment', {}),
            'has_learned_data': bool(self.learned_prefs.get('dynamic_personalization_notes'))
        }

    def _save_learned_preferences(self):
        """Save learned preferences to file."""
        os.makedirs(os.path.dirname(self.LEARNED_PREFS_FILE), exist_ok=True)
        with open(self.LEARNED_PREFS_FILE, 'w') as f:
            json.dump(self.learned_prefs, f, indent=2)
