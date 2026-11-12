"""
IRGC & Monica Witt Intelligence Crawler Configuration
Customize targets, aliases, search terms, and data sources
"""

# ============================================================================
# PRIMARY TARGETS
# ============================================================================

PRIMARY_TARGETS = {
    "monica_witt": {
        "name": "Monica Witt",
        "aliases": [
            "Monica Witt",
            "Fatemah Zahra",
            "Narges Witt",
            "Monica Elfriede Witt",
            "Fatmah Zahra",
            "Fatemah Zahra Witt",
            "Agent Witt",
            "Monica Elfriede",
            "Narges",
            "Wayward Storm",
        ],
        "entity_type": "PERSON",
        "significance": "ESPIONAGE",
        "role": "Air Force officer, alleged IRGC operative",
        "charges": ["Espionage", "Unauthorized disclosure of classified information"],
        "description": "Former U.S. Air Force officer accused of sharing classified information with IRGC"
    },
    "irgc": {
        "name": "Iranian Revolutionary Guard Corps",
        "aliases": [
            "IRGC",
            "Islamic Revolutionary Guard Corps",
            "IRGC-Quds Force",
            "IRGC-QF",
            "Quds Force",
            "Revolutionary Guards",
            "Sepah",
            "IRGC-E (Quds Force)",
        ],
        "entity_type": "ORGANIZATION",
        "significance": "ESPIONAGE",
        "branches": [
            "Quds Force",
            "IRGC Navy",
            "IRGC Air Force",
            "Cyber Division",
        ],
        "description": "Military organization of Iran; Quds Force specializes in extraterritorial operations and intelligence"
    }
}

# ============================================================================
# RELATED TARGETS (Secondary entities to track)
# ============================================================================

RELATED_TARGETS = {
    "quds_force": {
        "name": "Quds Force",
        "aliases": ["Quds Force", "IRGC-QF", "IRGC-E"],
        "entity_type": "ORGANIZATION",
        "significance": "ESPIONAGE",
        "description": "Special operations division of IRGC, focuses on extraterritorial operations"
    },
    "mois": {
        "name": "Ministry of Intelligence and Security",
        "aliases": ["MOIS", "Ministry of Intelligence", "VAJA"],
        "entity_type": "ORGANIZATION",
        "significance": "ESPIONAGE",
        "description": "Iranian intelligence agency, coordinates with IRGC"
    },
    "soleimani": {
        "name": "Qasem Soleimani",
        "aliases": ["Soleimani", "Qasem Soleimani", "Qassem Soleimani"],
        "entity_type": "PERSON",
        "significance": "TERRORIST_SUPPORT",
        "description": "Former Quds Force commander (killed 2020), linked to Monica Witt case"
    },
    "mojtaba_masoumpour": {
        "name": "Mojtaba Masoumpour",
        "aliases": ["Mojtaba Masoumpour", "Masoumpour"],
        "entity_type": "PERSON",
        "significance": "CYBER_ESPIONAGE",
        "description": "IRGC-linked hacker and co-defendant in the Witt case"
    },
    "phosphorus": {
        "name": "Phosphorus",
        "aliases": ["Charming Kitten", "APT35", "Ajax Security Team", "NewsBeef"],
        "entity_type": "ORGANIZATION",
        "significance": "CYBER_WARFARE",
        "description": "IRGC-linked cyber espionage group Witt is believed to have joined"
    },
    "behzad_mesri": {
        "name": "Behzad Mesri",
        "aliases": ["Behzad Mesri", "Skote Vahshat"],
        "entity_type": "PERSON",
        "significance": "CYBER_ESPIONAGE",
        "description": "Iranian hacker associated with IRGC and Witt-related operations"
    },
    "hossein_parvar": {
        "name": "Hossein Parvar",
        "aliases": ["Hossein Parvar"],
        "entity_type": "PERSON",
        "significance": "CYBER_ESPIONAGE",
        "description": "Co-conspirator in IRGC intelligence operations"
    },
    "mohamad_paryar": {
        "name": "Mohamad Paryar",
        "aliases": ["Mohamad Paryar"],
        "entity_type": "PERSON",
        "significance": "CYBER_ESPIONAGE",
        "description": "Co-conspirator identified in Witt indictment"
    },
    "marzieh_hashemi": {
        "name": "Marzieh Hashemi",
        "aliases": ["Marzieh Hashemi", "Melanie Franklin"],
        "entity_type": "PERSON",
        "significance": "INTELLIGENCE_RECRUITMENT",
        "description": "American-Iranian journalist/presenter linked to Witt recruitment"
    },
    "new_horizon": {
        "name": "New Horizon Organization",
        "aliases": ["New Horizon", "Hollywoodism Conference"],
        "entity_type": "ORGANIZATION",
        "significance": "INFORMATION_WARFARE",
        "description": "IRGC-sponsored organization used for recruitment and propaganda"
    }
}

# ============================================================================
# SEARCH TERMS (Keywords to match in documents)
# ============================================================================

SEARCH_TERMS = {
    "monica_witt_direct": [
        "Monica Witt",
        "Fatemah Zahra",
        "Narges Witt",
        "Monica Elfriede Witt",
        "Fatmah Zahra",
        "Wayward Storm",
        "Fatemah Zahra Witt",
        "Melanie Franklin", # Link to Hashemi context
        "Phosphorus",
        "Charming Kitten",
    ],
    "irgc_direct": [
        "IRGC",
        "Quds Force",
        "Islamic Revolutionary Guard",
        "Revolutionary Guard Corps",
    ],
    "known_allies": [
        "Mojtaba Masoumpour",
        "Behzad Mesri",
        "Hossein Parvar",
        "Mohamad Paryar",
        "Skote Vahshat",
        "Marzieh Hashemi",
        "Kevin Barrett",
    ],
    "case_specific": [
        "espionage",
        "classified information",
        "unauthorized disclosure",
        "intelligence operation",
        "Air Force",
        "counterintelligence",
        "foreign intelligence",
        "Air Medal",
        "Airborne Cryptologic Language Analyst",
        "Air Force Commendation Medal",
        "Aerial Achievement Medal",
        "Special Access Program",
        "TOP SECRET/SCI",
        "DD Form 214",
        "Title 18 charges",
        "target packages",
        "fraudulent Facebook accounts",
        "2016 U.S.–Iran naval incident",
        "U.S. Navy sailors questioning",
        "Phosphorus cyberwarfare",
        "2020 presidential election candidate",
        "informant exposure",
        "disrupted intelligence-gathering",
    ],
    "career_residue": [
        "Operation Iraqi Freedom",
        "OIF",
        "RC-135V/W",
        "Rivet Joint",
        "Offutt Air Force Base",
        "95th Expeditionary Reconnaissance Squadron",
        "95th ERS",
        "95 ERS",
        "Joint Base Andrews",
        "Crete Naval Base",
        "Diego Garcia",
        "Saudi Arabia",
        "Qatar",
        "OSI Desk Officer",
        "MySpace",
        "LiveJournal",
        "IRC logs",
        "Blogger",
        "Blogspot",
        "Google+",
        "Presidio of Monterey",
        "DLI Monterey",
        "17-mile drive",
        "Cannery Row",
        "WAPS testing",
        "ALS graduation",
        "Big Safari program",
        "Middle East Desk Officer",
        "Booz Allen Hamilton",
        "Chenega Federal Systems",
        "AMIDEAST",
        "Iraqi Fulbright Program",
        "Falls Church",
        "University of Maryland",
        "UMCP",
        "George Washington University",
        "GWU",
        "Dubai",
        "Tajikistan",
        "Afghanistan",
        "Parsian Azadi Hotel",
        "New Horizon Organization",
        "Hollywoodism Conference",
    ],
    "ideological_markers": [
        "anti-Iranian propaganda",
        "peace-loving nation",
        "anti-Islamic propaganda",
        "Quran study",
        "culture of tolerance for sexual harassment",
        "International Affairs Review",
        "Press TV",
        "Hollywoodism",
        "hyper-zealous",
        "performative loyalty",
        "unwavering defense",
        "BLUF",
        "Bottom Line Up Front",
        "Western Union",
        "wire transfer",
        "last four digits",
        "overt act",
        "travel manifest",
        "boarding pass",
        "Dubai transit",
        "Tajikistan border",
        "breach data",
        "leaked credentials",
        "drone strikes",
        "extrajudicial killings",
        "atrocities against children",
        "gross incompetence",
        "war crimes",
        "WikiLeaks",
        "Snowden",
    ],
    "time_capsule_2013": [
        "Miley Cyrus VMAs",
        "twerking",
        "Justin Bieber Brazil",
        "Paula Deen scandal",
        "Reese Witherspoon arrest",
        "Lance Armstrong Oprah",
        "Paul Walker",
        "Prince George birth",
        "2013 government shutdown",
        "debt ceiling crisis 2013",
        "Boston Marathon bombing",
        "Obama second inauguration",
        "Breaking Bad finale",
        "Walter White",
        "Red Wedding",
        "Game of Thrones Season 3",
        "Harlem Shake",
        "What Does the Fox Say",
        "Macklemore Thrift Shop",
        "Blurred Lines",
        "Royals Lorde",
    ],
    "syntactic_interference": [
        "traveled with", # Farsi 'ba' bleed
        "spoke with him", # instead of 'to'
        "at the end of the day", # overused in Farsi-English translation
        "in the path of", # literal translation of 'dar rahe'
        "is it possible to", # literal 'emkan darad'
        "give me a hand", # misused contextually
    ],
    "farsi_literal_idioms": [
        "hand not ache",         # Daste shoma dard nakone (Thank you)
        "place is empty",        # Jaye shoma khali (You were missed)
        "place was empty",
        "ate the ground",        # Zamin khordam (I fell down)
        "don't be tired",        # Khaste nabashid (Greeting/Goodbye)
        "not be tired",
        "on my eyes",            # Roo cheshmam (Certainly/With pleasure)
        "liver of mine",         # Jeegare mani (Endearment)
        "sour mouth",            # Talk nonsense
        "water behind",          # Ritual for travelers
    ],
    "western_creature_comforts": [
        "Palladium Mall",        # High-end Tehran mall for western brands
        "Iran Mall",
        "Netflix VPN",
        "Amazon shipping to Iran",
        "Starbucks equivalent",
        "Vanilla Latte",
        "western groceries",
        "Apple Store Tehran",
        "US cosmetics",
        "American snacks",
        "Starbucks",
        "Dunkin",
        "Tampax",
        "Always brand",
        "Kotex",
        "Playtex",
        "applicator tampons", # Specific US-style preference marker
        "Ziploc",
        "Kraft Mac and Cheese",
        "Cheerios",
        "Root Beer",
    ],
    "linguistic_fossils": [
        "drill downs",
        "flag bearer",
        "transvestite",
        "transexual",
        "Ketabi", # Formal written style
        "DLI-standard",
        "academic Farsi",
        "archaic syntax",
        "formal verb endings",
        "present arms",
        "order arms",
        "left face",
        "about face",
        "guidon",
        "Civil Air Patrol",
        "CAP cadet",
        "orientation flight",
        "ground team",
        "phreaking",
        "AFI 36-2903",
        "getting a 5 on an EPR",
        "all caps writing",
        "block lettering signature",
    ],
    "grey_market_logistics": [
        "Dubai to Tehran shipping",
        "UAE to Iran courier",
        "hand carry service",
        "personal shopper Dubai",
        "customs clearance help Tehran",
        "restricted items shipping",
    ],
    "community_nodes": [
        "Ex-Pat Mom Tehran",
        "Ex-Pat Women Tehran",
        "Tehran Ladies Social",
    ],
    "noise_exclusions": [
        # Placeholder for 'Standard Military Mundanity' provided by the Command Chief
        # Terms that are too common among all veterans to be useful as a Monica-specific signal
        "MRE",
        "FOB",
        "deployment",
        "DFAC",
        "standard issue",
        "vets helping vets",
    ],
    "iran_specific": [
        "Iran",
        "Iranian intelligence",
        "Iranian government",
        "Tehran",
        "Islamic Republic",
    ],
    "charges": [
        "espionage act",
        "national defense information",
        "export control",
        "sanctions violation",
        "material support",
        "conspiracy",
    ]
}

# ============================================================================
# FEDERAL DATA SOURCES (Seed URLs)
# ============================================================================

SEED_URLS = {
    "federal_courts": [
        "https://www.uscourts.gov/",
        "https://pacer.uscourts.gov/",
        "https://www.ca5.uscourts.gov/",  # 5th Circuit
    ],
    "specific_courts": [
        "https://www.sdtx.uscourts.gov/",  # Southern District of Texas (Houston)
        "https://www.txd.uscourts.gov/",   # District of Texas
        "https://www.njd.uscourts.gov/",   # District of New Jersey
    ],
    "fbi": [
        "https://www.fbi.gov/investigate/counterintelligence",
        "https://www.fbi.gov/investigate/counterintelligence/foreign-interference",
        "https://www.fbi.gov/news",
    ],
    "doj": [
        "https://en.wikipedia.org/wiki/Monica_Witt", # Baseline Reference Point
        "https://www.justice.gov/nsd/",  # National Security Division
        "https://www.justice.gov/criminal-nsd/",
        "https://www.justice.gov/opa/",  # Office of Public Affairs
        "https://www.justice.gov/criminal-vcs/",  # Counterintelligence
    ],
    "usao": [
        "https://www.justice.gov/usao-sdtx/",  # USAO Southern District Texas
        "https://www.justice.gov/usao-ndtx/",  # USAO Northern District Texas
        "https://www.justice.gov/usao-nj/",    # USAO New Jersey
    ],
    "intelligence": [
        "https://www.odni.gov/",  # Director of National Intelligence
        "https://www.cia.gov/",
    ],
    "cyber_security": [
        "https://www.cisa.gov/news-events/cybersecurity-advisories",
        "https://www.treasury.gov/resource-center/sanctions/SDN-List/Pages/default.aspx",
        "https://www.crowdstrike.com/blog/category/threat-intel/",
    ],
}

# ============================================================================
# CRAWLER PARAMETERS
# ============================================================================

CRAWLER_PARAMS = {
    "max_pages": 100,           # Maximum pages to crawl
    "max_depth": 5,             # Maximum link depth to follow
    "timeout": 30,              # Request timeout in seconds
    "rate_limit": 1.0,          # Seconds between requests (respectful)
    "extract_pdfs": True,       # Extract text from PDFs
    "extract_metadata": True,   # Extract document metadata
    "use_cache": True,          # Cache results
    "cache_dir": "crawler_cache",
}

# ============================================================================
# DOCUMENT TYPES TO IDENTIFY
# ============================================================================

DOCUMENT_TYPES = [
    "INDICTMENT",
    "COMPLAINT",
    "MOTION",
    "AFFIDAVIT",
    "SENTENCING",
    "PLEA",
    "APPEAL",
    "JUDGMENT",
    "WARRANT",
    "CHARGES",
    "TESTIMONY",
    "FILING",
]

# ============================================================================
# DOCUMENT PATTERNS (Regex patterns for extraction)
# ============================================================================

EXTRACTION_PATTERNS = {
    "case_number": r"(\d{2}-[A-Z]{2}-\d{5}|\d+-\d+-\d+)",
    "date": r"(\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2})",
    "defendant": r"(?:United States v\.|v\. |defendant:)\s*([A-Z][A-Za-z\s]+)",
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "phone": r"\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})",
    "ssn": r"\d{3}-\d{2}-\d{4}",
}

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

OUTPUT_CONFIG = {
    "formats": ["json", "csv", "txt"],
    "report_name": "irgc_monica_witt_intelligence_report",
    "summary_name": "irgc_monica_witt_summary",
    "csv_name": "monica_witt_documents",
    "include_full_text": True,
    "include_metadata": True,
    "include_context": True,
    "context_chars": 200,  # Characters before/after match
}

# ============================================================================
# ANALYSIS CONFIGURATION
# ============================================================================

ANALYSIS_CONFIG = {
    "fuzzy_match": True,           # Use fuzzy matching for aliases
    "fuzzy_threshold": 0.85,       # Fuzzy match threshold
    "network_analysis": True,      # Build connection networks
    "timeline_analysis": True,     # Create timeline
    "entity_clustering": True,     # Cluster related entities
    "export_knowledge_graph": True,  # Export as knowledge graph
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

from research_config import active_search_terms, verified_aliases


def get_all_aliases():
    """Only source-reviewed aliases; historical dictionaries above are inactive."""
    return verified_aliases()


def get_all_search_terms():
    return active_search_terms()


def get_all_seed_urls():
    """No automatically activated historical sources."""
    return []


def get_monica_witt_aliases():
    return verified_aliases()


def get_irgc_aliases():
    return []


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("IRGC & Monica Witt Intelligence Crawler Configuration")
    print("=" * 60)

    print("\nMonica Witt Aliases:")
    for alias in get_monica_witt_aliases():
        print(f"  • {alias}")

    print("\nIRGC Identifiers:")
    for alias in get_irgc_aliases():
        print(f"  • {alias}")

    print(f"\nTotal aliases tracked: {len(get_all_aliases())}")
    print(f"Total search terms: {len(get_all_search_terms())}")
    print(f"Total seed URLs: {len(get_all_seed_urls())}")

    print("\nCrawler Parameters:")
    for param, value in CRAWLER_PARAMS.items():
        print(f"  {param}: {value}")

    print("\nConfiguration loaded successfully!")

