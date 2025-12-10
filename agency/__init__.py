"""
Agency Module - Agentic components for Job Search Tool

Level 1 (Light Agency):
- FeedbackAnalyzer: Analyzes liked/disliked patterns
- PreferenceLearner: Updates dynamic preferences
- AccuracyTracker: Tracks filtering accuracy

Level 2 (Medium Agency):
- StrategyAgent: Autonomous strategy decisions
- DeadlineMonitor: Proactive deadline alerts
- QueryOptimizer: Self-improving queries
"""

from agency.feedback_analyzer import FeedbackAnalyzer
from agency.preference_learner import PreferenceLearner
from agency.accuracy_tracker import AccuracyTracker
from agency.strategy_agent import StrategyAgent
from agency.deadline_monitor import DeadlineMonitor
from agency.query_optimizer import QueryOptimizer

__all__ = [
    'FeedbackAnalyzer',
    'PreferenceLearner',
    'AccuracyTracker',
    'StrategyAgent',
    'DeadlineMonitor',
    'QueryOptimizer'
]
