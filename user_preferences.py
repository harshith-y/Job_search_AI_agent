"""
User Preferences Configuration
Customize job filtering to match YOUR specific interests
Edit this file to personalize your job search!
"""

# ============================================================================
# YOUR PROFILE
# ============================================================================

USER_PROFILE = {
    "name": "Harshith",
    "current_level": "Recent Graduate / Entry-Level",  # Entry-Level, Mid-Level, Senior, PhD Student
    "location_preferences": ["UK", "London", "Cambridge", "Oxford", "Remote"],
    "willing_to_relocate": True,
}


# ============================================================================
# INDUSTRY JOB PREFERENCES
# ============================================================================

INDUSTRY_PREFERENCES = {
    # Roles you're interested in (in priority order)
    "target_roles": [
        "Machine Learning Engineer",
        "Research Scientist",
        "AI Research Engineer",
        "Computer Vision Engineer",
        "NLP Engineer / Researcher",
        "Deep Learning Engineer",
        "MLOps Engineer",
        "Data Scientist (ML-focused)",
    ],
    
    # Roles you're NOT interested in
    "avoid_roles": [
        "Pure Data Analyst (no ML)",
        "Software Engineer (no ML component)",
        "Project Manager",
        "Sales / Business Development",
        "Data Engineer (ETL only)",
    ],
    
    # Technologies/frameworks you want to work with
    "preferred_tech": [
        "PyTorch",
        "TensorFlow",
        "Transformers / LLMs",
        "Computer Vision",
        "Reinforcement Learning",
        "JAX",
        "Python",
        "CUDA / GPU programming",
    ],
    
    # Research areas you find interesting
    "research_interests": [
        "Large Language Models",
        "Computer Vision",
        "Reinforcement Learning",
        "Multimodal AI",
        "AI Safety / Alignment",
        "Robotics with ML",
        "Generative Models",
    ],
    
    # Company types you prefer
    "company_preferences": {
        "startup": True,        # Small startups (< 50 people)
        "scale_up": True,       # Growing companies (50-500)
        "big_tech": True,       # FAANG, DeepMind, etc.
        "research_lab": True,   # Pure research organizations
        "university": True,     # University research positions
        "consulting": False,    # Consulting firms
    },
    
    # Work style preferences
    "work_style": {
        "remote": "Open to it",          # Required, Preferred, Open to it, No
        "hybrid": "Preferred",           # Required, Preferred, Open to it, No
        "in_office": "Open to it",       # Required, Preferred, Open to it, No
    },
    
    # Red flags (automatic reject if present)
    "red_flags": [
        "requires 10+ years experience",
        "requires security clearance",
        "sales role",
        "unpaid internship",
    ],
    
    # Nice-to-haves (bonus points)
    "bonus_points": [
        "research publication opportunities",
        "conference attendance budget",
        "GPU compute access",
        "open source contribution",
        "mentorship program",
        "learning budget",
    ],
}


# ============================================================================
# PHD POSITION PREFERENCES
# ============================================================================

PHD_PREFERENCES = {
    # Research areas (in priority order)
    "research_areas": [
        "Machine Learning / Deep Learning",
        "Computer Vision",
        "Natural Language Processing / LLMs",
        "Reinforcement Learning",
        "Multimodal Learning",
        "AI Safety / Robustness",
        "Computational Neuroscience (with ML)",
        "Robotics (with ML)",
    ],
    
    # Areas you're NOT interested in
    "avoid_areas": [
        "Pure mathematics (no ML application)",
        "Pure statistics (no ML)",
        "Bioinformatics (unless heavy ML)",
        "Hardware design",
        "Quantum computing (unless ML applications)",
    ],
    
    # Funding requirements
    "funding": {
        "must_be_funded": True,          # True = only show funded positions
        "minimum_stipend": 18000,        # Minimum annual stipend (GBP)
        "fees_covered": True,            # Must cover tuition fees
    },
    
    # University preferences (any of these is good)
    "preferred_universities": [
        "Cambridge", "Oxford", "Imperial", "UCL", "Edinburgh",
        "Manchester", "Warwick", "Bristol", "Southampton",
        "Alan Turing Institute", "DeepMind", "Google Research",
    ],
    
    # Supervisor qualities you're looking for
    "supervisor_preferences": [
        "Active publication record (recent papers)",
        "Good H-index / citations",
        "Industry collaborations",
        "Grant funding secured",
        "Supervises multiple PhD students",
    ],
    
    # Program characteristics
    "program_preferences": {
        "cdt": "Preferred",              # Required, Preferred, Open to it, No
        "industry_partnership": "Preferred",
        "internship_opportunities": "Preferred",
        "interdisciplinary": "Open to it",
    },
    
    # Deal-breakers
    "red_flags": [
        "no funding mentioned",
        "self-funded only",
        "supervisor has no recent publications",
        "expired deadline",
        "requires specific previous degree",
    ],
    
    # Nice-to-haves
    "bonus_points": [
        "conference travel budget",
        "GPU compute access",
        "industry placement year",
        "publication expectations clear",
        "collaborative research environment",
        "multiple co-supervisors",
    ],
}


# ============================================================================
# FILTERING STRICTNESS
# ============================================================================

FILTERING_CONFIG = {
    # How strict should Claude be?
    "industry_strictness": "moderate",   # strict, moderate, lenient
    "phd_strictness": "moderate",        # strict, moderate, lenient
    
    # Explanation:
    # strict = Only perfect matches (might miss opportunities)
    # moderate = Good matches with some flexibility (recommended)
    # lenient = Cast wider net (more false positives)
    
    # Should Claude explain rejections?
    "explain_rejections": False,  # True = see why jobs were filtered out
}


# ============================================================================
# PERSONALIZATION NOTES
# ============================================================================

PERSONALIZATION_NOTES = """
These are notes Claude will consider when filtering:

- I'm particularly interested in roles that combine research and engineering
- I prefer positions where I can publish papers or contribute to open source
- I'm open to both industry and PhD, whichever offers better learning opportunities
- I want to work on cutting-edge AI problems, not just applying existing models
- Team culture and mentorship are very important to me
- I prefer smaller teams where I can have more impact
- Remote work is nice but not essential if the role is exciting
- I'm willing to start with a lower salary for the right learning opportunity
"""

# ============================================================================
# HOW TO USE THIS FILE
# ============================================================================

"""
1. Edit the preferences above to match YOUR interests
2. Be specific! The more detailed, the better Claude can filter
3. Run: python main.py
4. Claude will use these preferences when filtering jobs
5. Adjust preferences over time as you learn what you want

Example customizations:
- If you only want research roles: Remove "MLOps", "Data Scientist" from target_roles
- If you want remote only: Set remote to "Required", others to "No"
- If you only want funded PhDs: Keep must_be_funded = True
- If you want specific tech: Add "Rust", "Go", "C++" to preferred_tech
"""
