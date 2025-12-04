"""
User Preferences Configuration
CUSTOMIZED FOR: Recent Undergrad Graduate seeking Entry-Level ML Roles
Edit this file to match YOUR specific interests and background!
"""

# ============================================================================
# YOUR PROFILE
# ============================================================================

USER_PROFILE = {
    "name": "Harshith",
    "current_level": "Recent Graduate - Entry Level",  # NOT PostDoc level!
    "education": "Undergraduate Degree",  # Bachelor's degree
    "location_preferences": ["UK", "London", "Cambridge", "Oxford", "Remote"],
    "willing_to_relocate": True,
}


# ============================================================================
# INDUSTRY JOB PREFERENCES
# ============================================================================

INDUSTRY_PREFERENCES = {
    # Roles you're interested in (ENTRY-LEVEL focus)
    "target_roles": [
        "Machine Learning Engineer",
        "Junior Machine Learning Engineer",
        "Graduate Machine Learning Engineer",
        "ML Engineer",
        "Research Engineer",
        "AI Engineer",
        "Computer Vision Engineer",
        "NLP Engineer",
        "Data Scientist (ML-focused)",
        "Graduate Researcher",
        "Research Assistant (ML)",
    ],
    
    # Roles you're NOT interested in (Important!)
    "avoid_roles": [
        "Senior Machine Learning Engineer",  # Too senior
        "Lead ML Engineer",  # Too senior
        "Principal Engineer",  # Too senior
        "Engineering Manager",  # Management
        "Data Analyst (no ML)",  # Not ML-focused
        "Software Engineer (no ML)",  # No ML component
        "Project Manager",
        "Sales / Business Development",
        "Data Engineer (ETL only)",  # No ML
        "PostDoc",  # You're not at PostDoc level!
        "Postdoctoral",  # You're not at PostDoc level!
    ],
    
    # Technologies/frameworks you want to work with
    "preferred_tech": [
        "PyTorch",
        "TensorFlow",
        "Transformers",
        "Hugging Face",
        "Computer Vision",
        "NLP / LLMs",
        "Python",
        "JAX",
        "Scikit-learn",
        "Deep Learning",
    ],
    
    # Research areas you find interesting
    "research_interests": [
        "Large Language Models",
        "Computer Vision",
        "Natural Language Processing",
        "Deep Learning",
        "Reinforcement Learning",
        "Multimodal AI",
        "Generative Models",
        "AI Safety",
    ],
    
    # Company types you prefer
    "company_preferences": {
        "startup": True,        # Small startups
        "scale_up": True,       # Growing companies
        "big_tech": True,       # FAANG, DeepMind, etc.
        "research_lab": True,   # Research organizations
        "university": True,     # University research positions
        "consulting": False,    # Consulting firms
    },
    
    # Work style preferences
    "work_style": {
        "remote": "Open to it",
        "hybrid": "Preferred",
        "in_office": "Open to it",
    },
    
    # RED FLAGS (automatic reject if present) - IMPORTANT!
    "red_flags": [
        "requires phd",  # You don't have a PhD
        "phd required",
        "phd preferred",
        "postdoc",  # Not a PostDoc role!
        "postdoctoral",
        "post-doctoral",
        "requires 5+ years experience",  # Too experienced
        "requires 10+ years experience",
        "senior level only",
        "lead position",
        "principal engineer",
        "requires security clearance",
        "sales role",
        "unpaid internship",
    ],
    
    # Nice-to-haves (bonus points)
    "bonus_points": [
        "graduate program",  # Good for recent grads!
        "training provided",  # Good for entry-level
        "mentorship program",
        "learning budget",
        "conference attendance",
        "research publication opportunities",
        "open source contribution",
        "gpu access",
    ],
}


# ============================================================================
# PHD POSITION PREFERENCES (If considering PhD)
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
    ],
    
    # Areas you're NOT interested in
    "avoid_areas": [
        "Pure mathematics (no ML application)",
        "Pure statistics (no ML)",
        "Bioinformatics (unless heavy ML)",
        "Hardware design",
    ],
    
    # Funding requirements
    "funding": {
        "must_be_funded": True,          # Only funded positions
        "minimum_stipend": 18000,        # Minimum GBP per year
        "fees_covered": True,
    },
    
    # University preferences
    "preferred_universities": [
        "Cambridge", "Oxford", "Imperial", "UCL", "Edinburgh",
        "Manchester", "Warwick", "Bristol", "Southampton",
        "Alan Turing Institute",
    ],
    
    # Red flags
    "red_flags": [
        "no funding mentioned",
        "self-funded only",
        "expired deadline",
    ],
    
    # Nice-to-haves
    "bonus_points": [
        "conference travel budget",
        "gpu compute access",
        "industry placement",
        "publication expectations clear",
    ],
}


# ============================================================================
# FILTERING STRICTNESS
# ============================================================================

FILTERING_CONFIG = {
    # How strict should Claude be?
    "industry_strictness": "moderate",   # strict, moderate, lenient
    "phd_strictness": "moderate",
    
    # Explanation:
    # strict = Only perfect matches (might miss opportunities)
    # moderate = Good matches with flexibility (recommended)
    # lenient = Cast wider net (more false positives)
    
    # Should Claude explain rejections?
    "explain_rejections": False,
}


# ============================================================================
# PERSONALIZATION NOTES
# ============================================================================

PERSONALIZATION_NOTES = """
IMPORTANT CONTEXT FOR FILTERING:

EDUCATION & EXPERIENCE:
- I have an undergraduate degree (Bachelor's)
- I am NOT at PostDoc level
- I am looking for ENTRY-LEVEL or GRADUATE positions
- I do NOT have a PhD yet (considering PhD programs though)

WHAT I'M LOOKING FOR:
- Entry-level ML Engineer or Research Engineer roles
- Graduate programs at tech companies
- Roles where I can learn and grow
- Good mentorship and training
- Hands-on ML work (not just data pipelines)

AUTOMATIC REJECTS:
- PostDoc positions (I don't have a PhD!)
- Senior/Lead/Principal roles (too experienced)
- Roles requiring PhD
- Roles requiring 5+ years experience

IDEAL ROLES:
- "Graduate Machine Learning Engineer"
- "Junior ML Engineer"  
- "Research Assistant" or "Research Engineer"
- "ML Engineer" (entry-level)
- Roles that say "recent graduates welcome"

COMPANIES I'M INTERESTED IN:
- Big AI labs (DeepMind, OpenAI, Anthropic)
- Tech companies (Google, Microsoft, Meta)
- AI startups
- Research-focused companies
- UK universities (for research positions)

WORK STYLE:
- Prefer hybrid (some remote, some in-office)
- Open to full remote or full in-office
- Willing to relocate for great opportunity

SALARY EXPECTATIONS:
- Entry-level UK: £30k-50k is realistic
- Graduate programs: £40k-60k
- Big tech: £50k-70k possible
- I'm more interested in learning than maximizing salary initially
"""

# ============================================================================
# HOW TO CUSTOMIZE THIS FILE
# ============================================================================

"""
TO CUSTOMIZE FOR YOU:

1. Update USER_PROFILE with your info
2. Adjust target_roles to roles you want
3. Add to red_flags any deal-breakers
4. Update preferred_tech with what you know/want to learn
5. Adjust research_interests to your interests
6. Edit PERSONALIZATION_NOTES with your story

EXAMPLES:

If you have more experience:
- Change "Entry-Level" to "Mid-Level"
- Remove "requires 5+ years" from red_flags
- Add "Senior" roles to target_roles

If you only want remote:
- Set remote: "Required"
- Set in_office: "No"

If you have a PhD:
- Remove "postdoc" from red_flags
- Add "Postdoctoral Researcher" to target_roles
- Change current_level to "PhD Graduate"

The more specific you are, the better Claude can filter!
"""