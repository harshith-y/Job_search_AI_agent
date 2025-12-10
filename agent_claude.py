"""
Job Filtering Agent using Claude (Anthropic API)
Uses Claude Sonnet 4 for both industry jobs AND PhD positions

NOW WITH LEARNING:
- Loads learned preferences from agency/preference_learner.py
- Combines static preferences with dynamically learned patterns
- Adapts filtering based on user's like/dislike history
"""

import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _get_learned_preferences():
    """
    Load learned preferences from the agency module.
    Returns empty values if agency module not available.
    """
    try:
        from agency.preference_learner import PreferenceLearner
        learner = PreferenceLearner()
        return {
            'notes': learner.get_dynamic_notes(),
            'strictness': learner.get_strictness_recommendation(),
            'summary': learner.get_learning_summary()
        }
    except ImportError:
        # Agency module not installed yet
        return {'notes': '', 'strictness': None, 'summary': {}}
    except Exception as e:
        print(f"   (Note: Could not load learned preferences: {e})")
        return {'notes': '', 'strictness': None, 'summary': {}}


def filter_industry_job(job):
    """
    Filter industry ML/AI jobs using Claude Sonnet 4
    Uses personalized preferences from user_preferences.py
    NOW WITH: Dynamic learned preferences from user feedback
    """

    # Load user preferences
    try:
        from user_preferences import (
            INDUSTRY_PREFERENCES,
            USER_PROFILE,
            PERSONALIZATION_NOTES,
            FILTERING_CONFIG
        )
    except ImportError:
        # Fallback to defaults if preferences file doesn't exist
        INDUSTRY_PREFERENCES = {
            "target_roles": ["Machine Learning Engineer", "Research Scientist"],
            "avoid_roles": ["Data Analyst"],
            "preferred_tech": ["PyTorch", "TensorFlow"],
        }
        USER_PROFILE = {"current_level": "Entry-Level", "location_preferences": ["UK"]}
        PERSONALIZATION_NOTES = ""
        FILTERING_CONFIG = {"industry_strictness": "moderate"}

    # Load learned preferences (from user feedback)
    learned = _get_learned_preferences()

    # Build personalized prompt
    target_roles = INDUSTRY_PREFERENCES.get("target_roles", [])
    avoid_roles = INDUSTRY_PREFERENCES.get("avoid_roles", [])
    preferred_tech = INDUSTRY_PREFERENCES.get("preferred_tech", [])
    research_interests = INDUSTRY_PREFERENCES.get("research_interests", [])
    red_flags = INDUSTRY_PREFERENCES.get("red_flags", [])

    # Use learned strictness if available, otherwise use config
    strictness = learned.get('strictness') or FILTERING_CONFIG.get("industry_strictness", "moderate")

    # Combine static and learned personalization notes
    combined_notes = PERSONALIZATION_NOTES
    if learned.get('notes'):
        combined_notes = f"{PERSONALIZATION_NOTES}\n\n{learned['notes']}"
    
    prompt = f"""
You are an AI assistant helping filter industry ML/AI jobs for a specific person.

USER PROFILE:
- Level: {USER_PROFILE.get('current_level', 'Entry-Level')}
- Locations: {', '.join(USER_PROFILE.get('location_preferences', ['UK']))}

JOB DETAILS:
Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
Description: {job['description']}

FILTERING CRITERIA (Personalized):

TARGET ROLES (what they're looking for):
{chr(10).join(f"- {role}" for role in target_roles)}

AVOID ROLES (not interested):
{chr(10).join(f"- {role}" for role in avoid_roles)}

PREFERRED TECHNOLOGIES:
{chr(10).join(f"- {tech}" for tech in preferred_tech)}

RESEARCH INTERESTS:
{chr(10).join(f"- {area}" for area in research_interests)}

RED FLAGS (automatic reject if present):
{chr(10).join(f"- {flag}" for flag in red_flags)}

PERSONALIZATION NOTES:
{combined_notes}

STRICTNESS: {strictness}
- strict: Only perfect matches with all preferred criteria
- moderate: Good match with most criteria (some flexibility)
- lenient: Reasonable match with core criteria (more flexible)

RESPOND IN THIS FORMAT:
Relevant: YES/NO
Match Score: [0-100%]
Key Skills: [list 3-5 key requirements]
Why Relevant: [2-3 sentences explaining match with user's interests]
Concerns: [any red flags or concerns, or "None"]
Summary: [2-3 line summary focusing on: role, key tech, why interesting for this specific user]
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text
        
        is_relevant = "YES" in content.split("Relevant:")[1].split("\n")[0].upper()
        
        # Extract summary
        try:
            summary = content.split("Summary:")[1].strip()
        except:
            lines = content.splitlines()
            summary = "\n".join(lines[1:]).strip()
        
        industry_info = {
            "summary": summary,
            "full_analysis": content
        }
        
        return is_relevant, industry_info

    except Exception as e:
        print(f"❌ Claude API error: {e}")
        return False, {"summary": "Error processing"}


def filter_phd_position(position):
    """
    Filter PhD positions using Claude Sonnet 4
    Uses personalized preferences from user_preferences.py
    NOW WITH: Dynamic learned preferences from user feedback
    """

    # Load user preferences
    try:
        from user_preferences import (
            PHD_PREFERENCES,
            USER_PROFILE,
            PERSONALIZATION_NOTES,
            FILTERING_CONFIG
        )
    except ImportError:
        # Fallback to defaults
        PHD_PREFERENCES = {
            "research_areas": ["Machine Learning", "Computer Vision"],
            "funding": {"must_be_funded": True},
        }
        USER_PROFILE = {"location_preferences": ["UK"]}
        PERSONALIZATION_NOTES = ""
        FILTERING_CONFIG = {"phd_strictness": "moderate"}

    # Load learned preferences (from user feedback)
    learned = _get_learned_preferences()

    # Build personalized prompt
    research_areas = PHD_PREFERENCES.get("research_areas", [])
    avoid_areas = PHD_PREFERENCES.get("avoid_areas", [])
    must_be_funded = PHD_PREFERENCES.get("funding", {}).get("must_be_funded", True)
    preferred_unis = PHD_PREFERENCES.get("preferred_universities", [])
    red_flags = PHD_PREFERENCES.get("red_flags", [])

    # Use learned strictness if available, otherwise use config
    strictness = learned.get('strictness') or FILTERING_CONFIG.get("phd_strictness", "moderate")

    # Combine static and learned personalization notes
    combined_notes = PERSONALIZATION_NOTES
    if learned.get('notes'):
        combined_notes = f"{PERSONALIZATION_NOTES}\n\n{learned['notes']}"
    
    prompt = f"""
You are an AI assistant helping filter PhD positions in Machine Learning/AI for a specific person.

USER PROFILE:
- Locations: {', '.join(USER_PROFILE.get('location_preferences', ['UK']))}

POSITION DETAILS:
Title: {position['title']}
University/Institute: {position['company']}
Location: {position['location']}
Description: {position['description']}

FILTERING CRITERIA (Personalized):

TARGET RESEARCH AREAS:
{chr(10).join(f"- {area}" for area in research_areas)}

AVOID RESEARCH AREAS:
{chr(10).join(f"- {area}" for area in avoid_areas)}

FUNDING REQUIREMENT:
- Must be funded: {must_be_funded}
- Look for keywords: "funded", "stipend", "scholarship", "EPSRC", "UKRI", "CDT"

PREFERRED UNIVERSITIES/INSTITUTES (bonus if matches):
{chr(10).join(f"- {uni}" for uni in preferred_unis)}

RED FLAGS (automatic reject):
{chr(10).join(f"- {flag}" for flag in red_flags)}

PERSONALIZATION NOTES:
{combined_notes}

STRICTNESS: {strictness}
- strict: Perfect research area match + confirmed funding
- moderate: Good research area match + likely funded (some flexibility)
- lenient: Related research area + possible funding (cast wider net)

FILTERING STEPS:

Step 1: Is this position FUNDED?
- If clearly UNFUNDED and must_be_funded=True → Answer NO
- If funding unclear → Mark as "Funding unclear - check manually"
- If funded or likely funded → Continue

Step 2: Research area match?
- Does it match target research areas?
- Is it in the avoid list?
- Rate match: 0-100%

Step 3: Institution quality?
- Is it a preferred university/institute?
- Supervisor track record (if mentioned)?

Step 4: Any red flags?
- Check against red flags list
- Expired deadline?
- Other concerns?

RESPOND IN THIS FORMAT:
Relevant: YES/NO/MAYBE
Funding: FUNDED/UNFUNDED/UNCLEAR
Research Match: [percentage 0-100%]
Institution: [comment on university/supervisor if notable]
Key Info: [deadline, start date, special requirements]
Why Relevant: [2-3 sentences on research fit and funding]
Red Flags: [if any, or "None"]
Summary: [2-3 line summary focusing on: research area, funding details, why interesting for this specific user]

IF UNFUNDED and must_be_funded=True → Relevant: NO
IF unclear research area → Relevant: MAYBE
IF perfect match + funded → Relevant: YES
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text
        lines = content.splitlines()
        
        # Parse response
        is_relevant = "YES" in content.split("Relevant:")[1].split("\n")[0].upper()
        is_maybe = "MAYBE" in content.split("Relevant:")[1].split("\n")[0].upper()
        
        # Extract key info
        try:
            funding = content.split("Funding:")[1].split("\n")[0].strip()
            research_match = content.split("Research Match:")[1].split("\n")[0].strip()
            key_info = content.split("Key Info:")[1].split("\n")[0].strip()
            summary = content.split("Summary:")[1].split("Red Flags:")[0].strip() if "Summary:" in content else ""
            red_flags = content.split("Red Flags:")[1].strip() if "Red Flags:" in content else "None"
        except:
            # Fallback if parsing fails
            funding = "Unknown"
            research_match = "Unknown"
            key_info = "See description"
            summary = "\n".join(lines[1:]).strip()
            red_flags = "None"
        
        # Create structured output
        phd_info = {
            "is_relevant": is_relevant,
            "is_maybe": is_maybe,
            "funding_status": funding,
            "research_match": research_match,
            "key_info": key_info,
            "summary": summary,
            "red_flags": red_flags
        }
        
        return is_relevant or is_maybe, phd_info

    except Exception as e:
        print(f"❌ Claude API error: {e}")
        return False, {"summary": "Error processing", "funding_status": "Unknown"}


# Backwards compatibility - default to industry filter
def summarize_job(job):
    """Default function - filters as industry job"""
    return filter_industry_job(job)


# Quick test
if __name__ == "__main__":
    print("Testing Claude API connection...")
    
    test_job = {
        "title": "Machine Learning Engineer",
        "company": "Test Company",
        "location": "London, UK",
        "description": "We are seeking an ML engineer with PyTorch experience..."
    }
    
    try:
        is_relevant, info = filter_industry_job(test_job)
        print(f"✅ Claude API working!")
        print(f"   Test job relevant: {is_relevant}")
        print(f"   Summary: {info['summary'][:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Check your ANTHROPIC_API_KEY in .env")