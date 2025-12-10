"""
Strategy Agent - Makes autonomous decisions about search strategies

Level 2 agency: The agent analyzes patterns and makes strategic decisions
about how to adjust search and filtering behavior.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


# Path relative to project root
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')


class StrategyAgent:
    """Autonomous agent that adjusts search strategies based on patterns."""

    STATE_FILE = os.path.join(DATA_DIR, "strategy_state.json")

    def __init__(self):
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        try:
            if os.path.exists(self.STATE_FILE):
                with open(self.STATE_FILE, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

        return {
            "version": "1.0",
            "current_strategy": {
                "strictness_level": "moderate",
                "search_breadth": "wide",
                "query_focus": [],
                "company_priorities": []
            },
            "autonomous_decisions": [],
            "pending_recommendations": []
        }

    def analyze_and_decide(self, learned_prefs: Dict) -> List[Dict]:
        """
        Analyze current state and make strategic decisions.

        Args:
            learned_prefs: Dictionary from PreferenceLearner

        Returns:
            List of decisions made
        """
        decisions = []

        # Decision 1: Adjust strictness based on user satisfaction
        strictness_decision = self._decide_strictness(learned_prefs)
        if strictness_decision:
            decisions.append(strictness_decision)

        # Decision 2: Focus queries on successful patterns
        query_decision = self._decide_query_focus(learned_prefs)
        if query_decision:
            decisions.append(query_decision)

        # Decision 3: Identify promising companies to prioritize
        company_decision = self._decide_company_focus(learned_prefs)
        if company_decision:
            decisions.append(company_decision)

        # Decision 4: Adjust search breadth
        breadth_decision = self._decide_search_breadth(learned_prefs)
        if breadth_decision:
            decisions.append(breadth_decision)

        # Record decisions
        for decision in decisions:
            decision['timestamp'] = datetime.now().isoformat()
            self.state['autonomous_decisions'].append(decision)

        # Keep only last 50 decisions
        self.state['autonomous_decisions'] = self.state['autonomous_decisions'][-50:]

        self._save_state()

        return decisions

    def _decide_strictness(self, learned_prefs: Dict) -> Optional[Dict]:
        """Decide whether to adjust filtering strictness."""
        adjustment = learned_prefs.get('strictness_adjustment', {})
        current = self.state['current_strategy']['strictness_level']
        recommended = adjustment.get('recommended', current)

        if recommended != current:
            self.state['current_strategy']['strictness_level'] = recommended
            return {
                'decision_type': 'adjust_strictness',
                'from': current,
                'to': recommended,
                'reason': adjustment.get('reason', 'Based on accuracy metrics'),
                'impact': f"Filtering strictness changed from {current} to {recommended}"
            }
        return None

    def _decide_query_focus(self, learned_prefs: Dict) -> Optional[Dict]:
        """Decide which search queries to prioritize."""
        patterns = learned_prefs.get('discovered_patterns', {})
        positives = patterns.get('differential_signals', {}).get('strong_positives', {})

        if not positives:
            return None

        # Find top keywords to focus on
        top_keywords = sorted(
            positives.items(),
            key=lambda x: x[1].get('ratio', 0),
            reverse=True
        )[:5]
        focus_keywords = [kw for kw, _ in top_keywords]

        current_focus = self.state['current_strategy'].get('query_focus', [])
        if set(focus_keywords) != set(current_focus):
            self.state['current_strategy']['query_focus'] = focus_keywords
            return {
                'decision_type': 'update_query_focus',
                'keywords': focus_keywords,
                'previous': current_focus,
                'reason': 'Based on user preference patterns',
                'impact': f"Search queries will prioritize: {', '.join(focus_keywords)}"
            }
        return None

    def _decide_company_focus(self, learned_prefs: Dict) -> Optional[Dict]:
        """Identify companies to prioritize in searches."""
        patterns = learned_prefs.get('discovered_patterns', {})
        liked_companies = patterns.get('differential_signals', {}).get('liked_companies', {})

        if not liked_companies:
            return None

        # Companies user has liked multiple times
        focus_companies = list(liked_companies.keys())[:5]

        current_priorities = self.state['current_strategy'].get('company_priorities', [])
        if set(focus_companies) != set(current_priorities):
            self.state['current_strategy']['company_priorities'] = focus_companies
            return {
                'decision_type': 'prioritize_companies',
                'companies': focus_companies,
                'previous': current_priorities,
                'reason': 'User has shown consistent interest in these companies',
                'impact': f"Will prioritize jobs from: {', '.join(focus_companies)}"
            }
        return None

    def _decide_search_breadth(self, learned_prefs: Dict) -> Optional[Dict]:
        """Decide whether to widen or narrow search breadth."""
        stats = learned_prefs.get('learning_stats', {})
        precision = stats.get('precision', 0.5)
        total = stats.get('total_feedback_processed', 0)

        if total < 20:
            return None  # Not enough data

        current_breadth = self.state['current_strategy'].get('search_breadth', 'wide')

        if precision < 0.25 and current_breadth != 'narrow':
            self.state['current_strategy']['search_breadth'] = 'narrow'
            return {
                'decision_type': 'adjust_search_breadth',
                'from': current_breadth,
                'to': 'narrow',
                'reason': f'Low precision ({precision:.0%}) - focusing on better-matched results',
                'impact': 'Search will be more targeted, fewer but better results'
            }
        elif precision > 0.6 and current_breadth != 'wide':
            self.state['current_strategy']['search_breadth'] = 'wide'
            return {
                'decision_type': 'adjust_search_breadth',
                'from': current_breadth,
                'to': 'wide',
                'reason': f'High precision ({precision:.0%}) - can explore more opportunities',
                'impact': 'Search will cast wider net for more opportunities'
            }

        return None

    def get_current_strategy(self) -> Dict:
        """Get current strategy settings for use in filtering/searching."""
        return self.state['current_strategy']

    def get_recent_decisions(self, limit: int = 10) -> List[Dict]:
        """Get recent autonomous decisions for transparency."""
        return self.state['autonomous_decisions'][-limit:]

    def get_strategy_summary(self) -> str:
        """Get a human-readable strategy summary."""
        strategy = self.state['current_strategy']
        decisions = self.get_recent_decisions(5)

        lines = []
        lines.append("CURRENT STRATEGY")
        lines.append("-" * 40)
        lines.append(f"  Strictness: {strategy.get('strictness_level', 'moderate')}")
        lines.append(f"  Search breadth: {strategy.get('search_breadth', 'wide')}")

        if strategy.get('query_focus'):
            lines.append(f"  Query focus: {', '.join(strategy['query_focus'][:3])}")

        if strategy.get('company_priorities'):
            lines.append(f"  Priority companies: {', '.join(strategy['company_priorities'][:3])}")

        if decisions:
            lines.append("\nRECENT DECISIONS:")
            for d in decisions[-3:]:
                lines.append(f"  - {d.get('decision_type', 'unknown')}: {d.get('impact', '')[:50]}")

        return '\n'.join(lines)

    def add_recommendation(self, recommendation: Dict):
        """Add a pending recommendation for user review."""
        recommendation['created_at'] = datetime.now().isoformat()
        recommendation['status'] = 'pending'
        self.state['pending_recommendations'].append(recommendation)
        self._save_state()

    def get_pending_recommendations(self) -> List[Dict]:
        """Get pending recommendations for user review."""
        return [r for r in self.state.get('pending_recommendations', [])
                if r.get('status') == 'pending']

    def _save_state(self):
        os.makedirs(os.path.dirname(self.STATE_FILE), exist_ok=True)
        with open(self.STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
