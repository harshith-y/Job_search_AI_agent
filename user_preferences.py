"""
User Preferences Configuration - MERGED VERSION
Education: MEng (Integrated Master's - counts as undergraduate)
Focus: Graduate schemes + Biomedical + ML Healthcare + Data Science + Research
Mode: DISCOVERY (very lenient filtering to find hidden gems)
"""

# ============================================================================
# YOUR PROFILE
# ============================================================================

USER_PROFILE = {
    "name": "Harshith",
    "current_level": "Recent MEng Graduate - Entry Level / Seeking Graduate Schemes",
    "education": "Integrated Master's (MEng) - Undergraduate level", 
    "location_preferences": ["UK", "London", "Cambridge", "Oxford", "Remote UK"],
    "willing_to_relocate": True,
    "cv_focus": "ML for medical applications and research",
}


# ============================================================================
# GRADUATE SCHEME PATTERN RECOGNITION (NEW!)
# ============================================================================

# These keywords help identify graduate schemes that might be missed
GRADUATE_SCHEME_KEYWORDS = [
    # Explicit schemes
    "graduate scheme", "graduate programme", "graduate program",
    "early careers programme", "graduate rotation",
    "graduate development programme",
    
    # Specific types
    "2 year programme", "3 year programme",
    "rotation programme", "leadership programme",
    "future leaders", "early talent",
    
    # Timeline indicators
    "graduate intake 2025", "september 2025 start",
    "graduate cohort", "2025 cohort",
    
    # Related opportunities
    "insight week", "spring week", "vacation scheme",
    "industrial placement", "year in industry",
    
    # Company-specific names
    "future leaders programme", "leadership development programme",
    "accelerated development programme",
]


# ============================================================================
# INDUSTRY JOB PREFERENCES
# ============================================================================

INDUSTRY_PREFERENCES = {
    # PRIMARY INTERESTS - Biomedical + ML + Healthcare
    "target_roles": [
        # ========================================
        # GRADUATE SCHEMES & PROGRAMMES (TOP PRIORITY!)
        # ========================================
        "Graduate Scheme",
        "Graduate Programme",
        "Graduate Program",
        "Engineering Graduate Scheme",
        "Technology Graduate Scheme",
        "Data Graduate Scheme",
        "Science Graduate Scheme",
        "Healthcare Graduate Scheme",
        "Pharmaceutical Graduate Scheme",
        "Biotech Graduate Programme",
        "Graduate Rotation Programme",
        "Graduate Development Programme",
        "Graduate Trainee",
        "Graduate Analyst",
        
        # ========================================
        # GRADUATE-LEVEL ROLES (Engineering, Data, ML)
        # ========================================
        # Engineering Graduate Roles
        "Graduate Engineer",
        "Graduate Biomedical Engineer",
        "Graduate Electrical Engineer",
        "Graduate Electronic Engineer",
        "Graduate Software Engineer",
        "Associate Engineer",
        "Junior Engineer",
        
        # Data & Analytics Graduate Roles
        "Graduate Data Scientist",
        "Graduate Data Analyst",
        "Graduate Business Analyst",
        "Graduate Analytics Consultant",
        
        # ML/AI Graduate Roles
        "Graduate Machine Learning Engineer",
        "Graduate AI Engineer",
        "Graduate Research Engineer",
        "Graduate ML Scientist",
        
        # Consulting Graduate Roles
        "Graduate Consultant",
        "Graduate Technology Consultant",
        "Graduate Engineering Consultant",
        "Associate Consultant",
        
        # ========================================
        # BIOMEDICAL ENGINEERING
        # ========================================
        "Biomedical Engineer",
        "Junior Biomedical Engineer",
        "Medical Device Engineer",
        "Clinical Engineer",
        "Healthcare Technology Engineer",
        "Bioelectronics Engineer",
        "Electronic Engineer (Medical Devices)",
        "Electrical Engineer (Healthcare)",
        "Embedded Systems Engineer (Medical)",
        
        # ========================================
        # ML FOR HEALTHCARE/MEDICAL
        # ========================================
        "Machine Learning Engineer (Healthcare)",
        "ML Engineer (Medical Applications)",
        "AI Engineer (Healthcare)",
        "Medical AI Researcher",
        "Clinical AI Engineer",
        "Healthcare ML Specialist",
        
        # ========================================
        # DATA SCIENCE (General + Medical)
        # ========================================
        "Data Scientist",
        "Junior Data Scientist",
        "Healthcare Data Scientist",
        "Medical Data Scientist",
        "Clinical Data Scientist",
        "Data Analyst",
        "Junior Data Analyst",
        "Business Intelligence Analyst",
        
        # ========================================
        # BIOINFORMATICS + BIOSTATISTICS
        # ========================================
        "Bioinformatics Scientist",
        "Bioinformatics Engineer",
        "Bioinformatics Analyst",
        "Computational Biologist",
        "Biostatistician",
        "Statistical Programmer",
        "Statistical Analyst (Clinical)",
        
        # ========================================
        # RESEARCH ROLES
        # ========================================
        "Research Engineer",
        "Research Scientist",
        "Research Associate",
        "Research Assistant",
        "ML Research Engineer",
        "Computational Research Scientist",
        
        # ========================================
        # GENERAL ML/AI ROLES
        # ========================================
        "Machine Learning Engineer",
        "Junior Machine Learning Engineer",
        "ML Engineer",
        "Research Engineer (ML)",
        "AI Engineer",
        "Computer Vision Engineer",
        "NLP Engineer",
        "Deep Learning Engineer",
        
        # ========================================
        # INTERNSHIPS & ENTRY-LEVEL
        # ========================================
        "Intern",
        "Internship",
        "Summer Intern",
        "Research Intern",
        "Engineering Intern",
        "Data Science Intern",
        "ML Intern",
        "Assistant Engineer",
        "Assistant Data Scientist",
    ],
    
    # Roles to AVOID
    "avoid_roles": [
        "Senior Engineer",
        "Lead Engineer",
        "Principal Engineer",
        "Staff Engineer",
        "Engineering Manager",
        "Director",
        "PostDoc",  # Have MEng, not PhD!
        "Postdoctoral",
        "Software Engineer (no ML/healthcare)",
        "Frontend Developer",
        "Backend Developer (no ML/data)",
        "Sales Engineer",
        "Project Manager (no technical work)",
    ],
    
    # Technologies/Skills you want to work with
    "preferred_tech": [
        # ML/AI
        "PyTorch", "TensorFlow", "Scikit-learn", "Machine Learning",
        "Deep Learning", "Neural Networks", "Computer Vision", "NLP",
        "Medical Imaging",
        
        # Data Science
        "Python", "R", "Pandas", "NumPy", "Data Analysis",
        "Statistical Modeling", "Data Visualization",
        
        # Biomedical/Healthcare
        "Medical Imaging", "Clinical Data", "Healthcare Analytics",
        "Bioinformatics", "Genomics", "Biostatistics",
        
        # Electronics/Engineering
        "Embedded Systems", "Signal Processing", "Medical Devices",
        "Biosensors", "MATLAB",
        
        # General
        "SQL", "Git", "Docker",
    ],
    
    # Research/Application areas you find interesting
    "research_interests": [
        # Healthcare/Medical focus
        "Medical AI", "Healthcare Machine Learning",
        "Medical Imaging Analysis", "Clinical Decision Support",
        "Drug Discovery", "Genomics / Bioinformatics",
        "Diagnostic AI", "Healthcare Data Science",
        "Biomedical Signal Processing", "Medical Device Development",
        "Wearable Health Tech", "Digital Health", "Precision Medicine",
        
        # General ML (also interested)
        "Computer Vision", "Natural Language Processing",
        "Deep Learning", "Reinforcement Learning",
    ],
    
    # Company types you prefer
    "company_preferences": {
        "medtech_companies": True,
        "pharma_biotech": True,
        "healthtech_startups": True,
        "ai_healthcare": True,
        "consulting": True,  # Cambridge Consultants!
        "hospitals_research": True,
        "big_tech": True,
        "research_lab": True,
        "university": True,
        "general_ml_startups": True,
        "data_science_companies": True,
    },
    
    # Work style preferences
    "work_style": {
        "remote": "Open to it",
        "hybrid": "Preferred",
        "in_office": "Open to it",
    },
    
    # RED FLAGS (automatic reject)
    "red_flags": [
        "requires phd", "phd required", "phd preferred",
        "postdoc", "postdoctoral",
        "requires 3+ years experience",
        "requires 5+ years experience",
        "requires 10+ years experience",
        "senior level only", "lead position", "principal engineer",
        "requires security clearance",
        "unpaid internship",
        "sales only",
        # Location red flags (NEW for discovery)
        "USA only", "United States only", "Europe only",
        "remote (US)", "remote (EU)", "remote international",
    ],
    
    # BONUS POINTS (things you'd love to see)
    "bonus_points": [
        # Graduate scheme specific - STRONG signals!
        "graduate scheme", "graduate programme", "graduate program",
        "rotation programme", "structured training",
        "graduate development", "leadership programme",
        "fast-track programme", "early careers",
        "future leaders", "early talent", "2025 intake",
        
        # Entry-level indicators
        "graduate", "intern", "internship", "entry level", "junior",
        "trainee", "associate", "0-1 years experience",
        "no experience required", "training provided",
        "mentorship", "onboarding programme",
        
        # Healthcare/Biomedical - YOUR INTERESTS!
        "medical applications", "healthcare", "clinical",
        "biomedical", "bioinformatics", "drug discovery",
        "medical imaging", "diagnostic", "precision medicine",
        "digital health", "medical device", "pharmaceutical",
        "biotech", "genomics", "proteomics",
        "research", "r&d", "laboratory", "computational research",
        
        # Location - UK emphasis!
        "UK", "London", "Cambridge", "Oxford", "Manchester",
        "Edinburgh", "Bristol", "Remote UK",
        
        # Career development
        "learning budget", "professional development",
        "conference attendance", "publication opportunities",
        "career progression", "promotion pathway",
        "chartership support",
        
        # Work environment
        "gpu access", "flexible working", "hybrid working",
        "work-life balance", "collaborative team",
        "innovative", "cutting-edge",
        
        # Company quality signals (for hidden gems!)
        "funded", "series A", "series B", "scale-up",
    ],
}


# ============================================================================
# PHD PREFERENCES (Still exploring)
# ============================================================================

PHD_PREFERENCES = {
    "research_areas": [
        "Machine Learning for Healthcare",
        "Medical AI / Clinical AI",
        "Medical Imaging Analysis",
        "Computational Biology",
        "Bioinformatics",
        "Healthcare Data Science",
        "Precision Medicine",
        "Drug Discovery (ML-based)",
        "Biomedical Engineering",
        "Medical Device Development",
        "Biosensors and Diagnostics",
        "Biomedical Signal Processing",
        "Machine Learning / Deep Learning",
        "Computer Vision",
        "Natural Language Processing",
    ],
    
    "avoid_areas": [
        "Pure mathematics (no application)",
        "Pure statistics (no application)",
        "Theoretical computer science (no application)",
        "Hardware chip design",
        "Quantum computing",
    ],
    
    "funding": {
        "must_be_funded": True,
        "minimum_stipend": 18000,
        "fees_covered": True,
    },
    
    "preferred_universities": [
        "Cambridge", "Oxford", "Imperial", "UCL", "King's College London",
        "Edinburgh", "Manchester", "Warwick",
        "Southampton", "Bristol", "Glasgow", "Newcastle",
        "Alan Turing Institute", "Francis Crick Institute", "Wellcome Trust",
    ],
    
    "red_flags": [
        "no funding mentioned",
        "self-funded only",
        "expired deadline",
        "teaching-only position",
    ],
    
    "bonus_points": [
        "medical applications", "clinical collaboration",
        "hospital partnership", "industry placement",
        "conference travel", "gpu compute", "interdisciplinary",
    ],
}


# ============================================================================
# FILTERING CONFIGURATION
# ============================================================================

FILTERING_CONFIG = {
    # CHANGED: "very_lenient" for DISCOVERY MODE!
    "industry_strictness": "very_lenient",  # Was "lenient" - now more inclusive!
    "phd_strictness": "lenient",
    "explain_rejections": False,
}


# ============================================================================
# PERSONALIZATION NOTES FOR CLAUDE - DISCOVERY MODE
# ============================================================================

PERSONALIZATION_NOTES = """
⚠️ DISCOVERY MODE PHILOSOPHY - VERY IMPORTANT! ⚠️

FILTERING APPROACH:
- BE VERY INCLUSIVE - This is about DISCOVERING opportunities!
- When in doubt → INCLUDE the role!
- Better to see 50 roles and skip 20, than miss 5 good ones!
- False positives > False negatives
- User can filter later in GUI
- Goal: Find hidden gems like LifeArc, Cambridge Consultants

LOCATION REQUIREMENT:
✅ MUST be in UK (London, Cambridge, Oxford, other UK cities, Remote UK)
❌ REJECT: USA, United States, Europe only, "Remote (US)", "Remote (EU)"

GRADUATE SCHEME DETECTION:
Look for these patterns in title OR description:
- "graduate scheme", "graduate programme", "early careers programme"
- "rotation programme", "future leaders", "early talent"
- "2025 intake", "graduate cohort", "2 year programme"
If ANY of these appear → VERY HIGH PRIORITY match!

HIDDEN GEM COMPANY PRIORITY:
Jobs from these sources = AUTOMATICALLY interesting:
- LifeArc, Oxford Nanopore, BenevolentAI, Healx
- Small biotech/medtech companies (10-100 employees)
- Translational research organizations
- Boutique consultancies (Cambridge Consultants, etc.)

ABOUT ME:
- Recent MEng graduate (4-year integrated Master's degree)
- MEng counts as UNDERGRADUATE for graduate scheme eligibility
- Eligible for ALL graduate schemes including "undergraduates only"
- Looking for: Graduate schemes, entry-level roles, research positions
- Maximum 1-2 years experience requirement

MY CAREER INTERESTS (ALL EQUALLY IMPORTANT!):

1. GRADUATE SCHEMES (TOP PRIORITY!)
   - Engineering, Technology, Data, Science, Healthcare, Pharma, Consulting
   - Rotation programmes, structured training
   - I'm eligible for ALL schemes

2. BIOMEDICAL ENGINEERING
   - Electrical/electronic engineering + computation in biology/medicine
   - Medical devices, biosensors, healthcare technology
   - Intentionally broad - exploring different paths!

3. ML FOR HEALTHCARE
   - Medical imaging, clinical AI, diagnostic systems
   - Drug discovery, precision medicine
   - Any ML applied to medicine/biology

4. DATA SCIENCE
   - Healthcare data science, bioinformatics, biostatistics
   - Clinical data analysis
   - General data science (also interesting!)

5. RESEARCH ROLES
   - Research engineer, research scientist
   - Computational research, lab + computational mix
   - R&D in biotech/pharma

6. CONSULTING
   - Technical consulting (Cambridge Consultants!)
   - Healthcare consulting, engineering consulting

7. PHARMA/BIOTECH
   - Pharmaceutical companies (GSK, AstraZeneca)
   - Biotech startups, genomics companies

8. GENERAL ML/AI
   - Computer vision, NLP, deep learning
   - Even non-healthcare ML roles

WHAT I'M OPEN TO:
✅ Graduate schemes (all types!)
✅ Biomedical engineering roles
✅ ML for healthcare
✅ Research positions
✅ Consulting
✅ Pharma/biotech companies
✅ Startups (healthcare AI, biotech, general ML)
✅ Data science
✅ Academic/university roles
✅ Roles that are "adjacent" to my interests

WHAT I'M NOT INTERESTED IN:
❌ PostDoc (have MEng, not PhD)
❌ Senior/Lead/Principal roles
❌ Requires PhD
❌ 3+ years experience required
❌ Pure software engineering (no ML/data/healthcare)
❌ Sales-focused roles
❌ Jobs outside UK

INCLUSION CRITERIA (When in doubt, INCLUDE if):
1. Graduate scheme/programme in title or description
2. Biomedical + engineering keywords present
3. ML/AI + healthcare keywords present
4. Research + computational keywords present
5. Entry-level + any of my interest areas
6. From a "hidden gem" company (LifeArc, Oxford Nanopore, etc.)
7. Could POSSIBLY be interesting based on my broad interests

EXCLUSION CRITERIA (Hard nos):
1. PostDoc or "PhD required"
2. Senior/Lead/Principal level
3. 3+ years experience required
4. Non-UK location
5. Pure software engineering (no ML/data/healthcare component)

GRAY AREA - BE INCLUSIVE:
- "Data Scientist" (no healthcare mentioned) → INCLUDE (could be healthcare)
- "Research Associate" (unclear field) → INCLUDE if UK-based
- "Engineer" (vague) → INCLUDE if at relevant company
- Slightly too much experience → INCLUDE if it's a grad scheme

KEY PHRASES:
EXCELLENT: "graduate scheme", "graduate programme", "rotation programme",
           "early careers", "MEng preferred", "UK", "London", "Cambridge"

GOOD: "graduate", "entry level", "junior", "0-2 years",
      "biomedical", "medical", "healthcare", "bioinformatics",
      "machine learning", "data science", "research", "r&d",
      "consulting", "pharma", "biotech"

BAD: "senior", "lead", "postdoc", "3+ years", "PhD required",
     "USA", "Europe", "remote international"

REMEMBER:
- This is DISCOVERY phase - be very inclusive!
- False positives are OK - user can filter in GUI
- Don't miss graduate schemes!
- Don't miss hidden gems like LifeArc!
- UK location is REQUIRED
- When in doubt → INCLUDE!
"""


# ============================================================================
# EXAMPLES
# ============================================================================

"""
SHOULD INCLUDE (Discovery mode):

✅ "Graduate Programme - Technology" (Always include!)
✅ "Research Associate - LifeArc" (Hidden gem!)
✅ "Data Scientist - Small Biotech Startup" (Could be interesting!)
✅ "Engineer - Medical Device Company" (Relevant company!)
✅ "Junior ML Engineer" (Entry-level ML!)
✅ "Rotation Programme - 2 years" (Grad scheme pattern!)
✅ "Computational Scientist" (Could be interesting!)
✅ "Data Analyst" (Could be healthcare!)

SHOULD EXCLUDE:

❌ "Senior ML Engineer" (Too senior)
❌ "PostDoc in Computational Biology" (PostDoc)
❌ "Lead Data Scientist - 5+ years" (Too experienced)
❌ "ML Engineer - San Francisco" (USA, not UK)
❌ "PhD Researcher" (Requires PhD)
"""


# ============================================================================
# HOW TO CUSTOMIZE
# ============================================================================

"""
TO ADJUST AS YOU DISCOVER MORE:

1. Add companies to config.yaml as you find them
2. Adjust strictness if too many/too few matches
3. Update target_roles as you narrow down interests
4. Add to bonus_points as you learn what matters

CURRENT APPROACH:
- Very lenient filtering = Discovery mode
- Finding hidden gems like LifeArc
- Graduate schemes from direct sources
- 30-50 matches expected (vs 4 before!)
"""