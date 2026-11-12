"""
24/7 CONTINUOUS MONITORING CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Comprehensive configuration for continuous intelligence monitoring.
Extends base IRGC Monica Witt configuration with time-based parameters.

PRIMARY OBJECTIVES:
  1. Monica Witt (all known aliases)
  2. IRGC & Quds Force activities
  3. Related espionage/counterintelligence cases
  4. Known associates & co-conspirators
  5. Temporal pattern analysis
"""

from datetime import time, timedelta
from enum import Enum
from typing import Dict, List, Optional


# ============================================================================
# CONTINUOUS MONITORING PARAMETERS
# ============================================================================

class MonitoringProfile(Enum):
    """Monitoring intensity profiles"""
    LIGHT = "light"          # 30 minute intervals (500 locations)
    STANDARD = "standard"    # 10 minute intervals (1000+ locations)
    INTENSIVE = "intensive"  # 5 minute intervals (all locations)
    EMERGENCY = "emergency"  # 1 minute intervals (critical monitoring)


# Default continuous monitoring settings
CONTINUOUS_MONITORING = {
    "enabled": True,
    "profile": MonitoringProfile.STANDARD.value,
    
    # Check intervals (in seconds)
    "check_intervals": {
        "light": 1800,          # 30 minutes
        "standard": 600,        # 10 minutes (recommended)
        "intensive": 300,       # 5 minutes
        "emergency": 60,        # 1 minute (critical alerts only)
    },
    
    # Daily schedule (24-hour format)
    "daily_schedule": {
        "enabled": True,
        "high_activity_hours": [
            (6, 10),    # 6am-10am: Early business hours
            (10, 14),   # 10am-2pm: Mid-day
            (14, 18),   # 2pm-6pm: Afternoon
        ],
        "normal_hours": [
            (18, 22),   # 6pm-10pm: Evening
            (22, 23),   # 10pm-11pm: Late evening
        ],
        "low_activity_hours": [
            (23, 6),    # 11pm-6am: Night
        ],
    },
    
    # Activity-based intervals
    "adaptive_intervals": {
        "high_activity": 300,       # 5 min during peak hours
        "normal_activity": 600,     # 10 min during normal hours
        "low_activity": 1800,       # 30 min during low hours
    },
    
    # Maximum continuous operation
    "max_continuous_hours": 24,    # Restart after 24 hours
    "restart_interval": 86400,     # 24 hours in seconds
    
    # Anomaly detection
    "anomaly_detection": {
        "enabled": True,
        "baseline_cycles": 100,     # Number of cycles to establish baseline
        "deviation_threshold": 2.0, # Standard deviations to trigger alert
    },
}


# ============================================================================
# EXPANDED SEARCH TARGETS - Monica Witt Case
# ============================================================================

EXPANDED_MONICA_WITT_ALIASES = [
    # Known/confirmed aliases
    "Monica Witt",
    "Fatemah Zahra",
    "Narges Witt",
    "Monica Elfriede Witt",
    "Fatmah Zahra",
    "Fatemah Zahra Witt",
    "Monica Elfriede",
    "Narges",
    
    # Potential variations
    "M. Witt",
    "M.E. Witt",
    "Witt Monica",
    "Zahra Fatemah",
    "Zahra Fatmah",
    "Fatemah Zahra-Witt",
    
    # Case identifiers
    "Agent Witt",
    "Operation Nightingale",  # Potential operation codename
    "Case 18-CR-00002",        # Potential court case reference
]


EXPANDED_IRGC_ALIASES = [
    # Official names
    "Islamic Revolutionary Guard Corps",
    "Iranian Revolutionary Guard Corps",
    
    # Standard abbreviations
    "IRGC",
    "I.R.G.C.",
    
    # Main organizational units
    "IRGC-Quds Force",
    "IRGC-QF",
    "Quds Force",
    "IRGC-E",
    "IRGC-Aerospace Force",
    "IRGC-Ground Force",
    "IRGC Navy",
    "IRGC Air Force",
    "IRGC Cyber Division",
    "IRGC Intelligence Organization",
    
    # Related designations
    "Revolutionary Guards",
    "Revolutionary Guard Corps",
    "Sepah",
    "Sepah-e Pasdaran",
    "Iranian Guard",
    "IRGC-linked",
    
    # Foreign references
    "Pasadaran",
    "Corps des Gardiens",
]


# ============================================================================
# EXPANDED ASSOCIATE TRACKING
# ============================================================================

KNOWN_ASSOCIATES = {
    "operators": [
        {
            "name": "Qasem Soleimani",
            "aliases": ["Soleimani", "Qassem Soleimani", "Qasem Sulaymani"],
            "role": "Former Quds Force Commander",
            "significance": "Linked to Monica Witt case",
            "status": "Deceased (2020)",
        },
        {
            "name": "Esmail Qaani",
            "aliases": ["Qaani", "Ismail Qaani"],
            "role": "Quds Force Commander",
            "significance": "Successor to Soleimani",
            "status": "Active",
        },
        {
            "name": "Ahmad Vahidi",
            "aliases": ["Vahidi", "Ahmad Vahidi"],
            "role": "Defense Minister / IRGC Official",
            "significance": "Connected to intelligence operations",
            "status": "Active",
        },
    ],
    
    "organizations": [
        {
            "name": "Ministry of Intelligence and Security",
            "aliases": ["MOIS", "VAJA", "Ministry of Intelligence"],
            "connection": "Coordinates with IRGC",
            "significance": "Iranian intelligence agency",
        },
        {
            "name": "Basij Resistance Force",
            "aliases": ["Basij", "Basij-e Mostaz'afin"],
            "connection": "IRGC militia affiliate",
            "significance": "Provides paramilitary support",
        },
    ],
}


# ============================================================================
# EXPANDED SEARCH LOCATIONS
# ============================================================================

# Comprehensive list of federal data sources for continuous monitoring
EXPANDED_SEED_URLS = {
    "federal_courts": [
        "https://www.uscourts.gov/",
        "https://www.uscourts.gov/news-and-updates",
        "https://pacer.uscourts.gov/",
        "https://www.pacer.login.uscourts.gov/cgi-bin/login.pl",
    ],
    
    "circuit_courts": [
        "https://www.ca1.uscourts.gov/",  # 1st Circuit
        "https://www.ca2.uscourts.gov/",  # 2nd Circuit
        "https://www.ca3.uscourts.gov/",  # 3rd Circuit
        "https://www.ca4.uscourts.gov/",  # 4th Circuit
        "https://www.ca5.uscourts.gov/",  # 5th Circuit (Houston area)
        "https://www.ca6.uscourts.gov/",  # 6th Circuit
        "https://www.ca7.uscourts.gov/",  # 7th Circuit
        "https://www.ca8.uscourts.gov/",  # 8th Circuit
        "https://www.ca9.uscourts.gov/",  # 9th Circuit
        "https://www.ca10.uscourts.gov/", # 10th Circuit
        "https://www.ca11.uscourts.gov/", # 11th Circuit
        "https://www.cadc.uscourts.gov/",  # DC Circuit
        "https://www.cafc.uscourts.gov/",  # Federal Circuit
    ],
    
    "district_courts_primary": [
        "https://www.sdtx.uscourts.gov/",   # Southern District of Texas (Houston)
        "https://www.txd.uscourts.gov/",    # Northern District of Texas (Dallas)
        "https://www.njd.uscourts.gov/",    # District of New Jersey
        "https://www.wdtx.uscourts.gov/",   # Western District of Texas
        "https://www.edtx.uscourts.gov/",   # Eastern District of Texas
    ],
    
    "fbi_counterintelligence": [
        "https://www.fbi.gov/investigate/counterintelligence",
        "https://www.fbi.gov/investigate/counterintelligence/foreign-interference",
        "https://www.fbi.gov/investigate/counterintelligence/espionage",
        "https://www.fbi.gov/news",
        "https://www.fbi.gov/news/stories",
    ],
    
    "doj_national_security": [
        "https://www.justice.gov/nsd/",
        "https://www.justice.gov/nsd/counterintelligence-security-section",
        "https://www.justice.gov/criminal-nsd/",
        "https://www.justice.gov/opa/",
        "https://www.justice.gov/opa/pr",
    ],
    
    "usao_offices": [
        "https://www.justice.gov/usao-sdtx/",     # Southern District Texas
        "https://www.justice.gov/usao-ndtx/",     # Northern District Texas
        "https://www.justice.gov/usao-nj/",       # New Jersey
        "https://www.justice.gov/usao-wdtx/",     # Western District Texas
        "https://www.justice.gov/usao/",          # All USAO offices
    ],
    
    "intelligence_agencies": [
        "https://www.odni.gov/",      # Director of National Intelligence
        "https://www.cia.gov/",       # CIA
        "https://www.state.gov/",     # State Department
        "https://www.defense.gov/",   # DoD
    ],
    
    "foia_databases": [
        "https://www.justice.gov/foia",
        "https://vault.fbi.gov/",
        "https://www.state.gov/foia-requests/",
    ],
    
    "news_aggregation": [
        "https://news.google.com/search?q=Monica%20Witt",
        "https://news.google.com/search?q=IRGC",
        "https://news.google.com/search?q=espionage",
    ],
    
    "sanctions_lists": [
        "https://www.treasury.gov/resource-center/sanctions/sdn-list/",
        "https://www.treasury.gov/resource-center/sanctions/ofac-sanctions-lists/",
        "https://www.state.gov/key-topics-bureau-of-counterterrorism/terrorist-organizations/",
    ],
}


# ============================================================================
# ENHANCED SEARCH TERM CATEGORIES
# ============================================================================

EXPANDED_SEARCH_TERMS = {
    "monica_witt_direct": EXPANDED_MONICA_WITT_ALIASES,
    
    "irgc_direct": EXPANDED_IRGC_ALIASES,
    
    "espionage_indicators": [
        "espionage",
        "espionage act",
        "classified information",
        "unauthorized disclosure",
        "national defense information",
        "disclosure of secrets",
        "violation of espionage act",
        "foreign intelligence service",
        "intelligence operation",
        "covert operation",
        "intelligence sharing",
        "security clearance revocation",
    ],
    
    "irgc_activities": [
        "extraterritorial operations",
        "cyber operations",
        "drone development",
        "missile program",
        "nuclear program",
        "sanctions evasion",
        "terrorism support",
        "proxy forces",
        "regional destabilization",
    ],
    
    "case_legal_indicators": [
        "indictment",
        "complaint",
        "motion",
        "affidavit",
        "sentencing",
        "plea agreement",
        "appeal",
        "judgment",
        "conviction",
        "prosecution",
        "trial",
        "evidence",
        "testimony",
    ],
    
    "counterintelligence": [
        "counterintelligence",
        "CI investigation",
        "foreign agent",
        "agent of foreign government",
        "espionage network",
        "intelligence gathering",
        "surveillance",
        "dead drop",
        "asset recruitment",
    ],
    
    "operational_context": [
        "Air Force",
        "military officer",
        "security clearance",
        "classified facility",
        "defense contractor",
        "intelligence community",
        "federal officer",
        "national security",
    ],
    
    "temporal_indicators": [
        "2013",  # Case timeline start
        "2015",
        "2016",
        "2017",
        "2018",  # Indictment year
        "2019",
        "2020",
        "2021",
        "recent",
        "ongoing",
    ],
    
    "geographic_indicators": [
        "Houston",
        "Texas",
        "San Antonio",
        "Iran",
        "Tehran",
        "United States",
        "federal court",
        "southern district",
    ],
    
    "associate_names": [
        "Qasem Soleimani",
        "Esmail Qaani",
        "Ahmad Vahidi",
        "Basij",
    ],
}


# ============================================================================
# ALERT CONFIGURATION
# ============================================================================

ALERT_CONFIGURATION = {
    "enabled": True,
    
    "critical_keywords": [
        "Monica Witt",
        "Fatemah Zahra",
        "IRGC-Quds Force",
        "espionage",
        "classified",
        "indictment",
    ],
    
    "alert_levels": {
        "CRITICAL": {
            "keywords": EXPANDED_MONICA_WITT_ALIASES + ["espionage", "indictment"],
            "notify_immediately": True,
            "log_level": "ERROR",
        },
        "WARNING": {
            "keywords": EXPANDED_IRGC_ALIASES + ["intelligence", "operation"],
            "notify_immediately": False,
            "log_level": "WARNING",
        },
        "INFO": {
            "keywords": ["government", "agency", "federal"],
            "notify_immediately": False,
            "log_level": "INFO",
        },
    },
    
    "notification_channels": {
        "log_file": True,
        "console": True,
        "webhook": False,
        "email": False,
    },
    
    "deduplication": {
        "enabled": True,
        "window_seconds": 3600,  # 1 hour - don't repeat alerts within this time
    },
}


# ============================================================================
# PERFORMANCE TUNING
# ============================================================================

PERFORMANCE_CONFIG = {
    "concurrent_requests": 4,       # Parallel crawl threads
    "request_timeout": 30,          # Seconds per request
    "connection_pool_size": 10,
    "cache_enabled": True,
    "cache_ttl": 3600,              # 1 hour
    "cache_max_size": 1000,
    "memory_limit_mb": 2048,        # Max memory for cache
    "retry_attempts": 3,
    "retry_backoff": 2.0,           # Exponential backoff multiplier
}


# ============================================================================
# DATA PERSISTENCE & ARCHIVAL
# ============================================================================

DATA_ARCHIVAL = {
    "enabled": True,
    "archive_directory": "./crawler_archive",
    
    "archival_schedule": {
        "daily": True,
        "daily_time": "00:00",           # Midnight
        "weekly": True,
        "weekly_day": "Sunday",
        "monthly": True,
        "monthly_day": 1,
    },
    
    "retention_policy": {
        "hot_data_days": 7,              # Keep in active database
        "warm_data_days": 30,            # Keep in cache
        "cold_data_days": 365,           # Keep in archive
        "delete_after_days": 1095,       # 3 years
    },
    
    "export_formats": [
        "json",
        "csv",
        "sqlite",
        "parquet",
    ],
}


# ============================================================================
# ENTITY RELATIONSHIP ANALYSIS
# ============================================================================

RELATIONSHIP_ANALYSIS = {
    "enabled": True,
    
    "relationship_types": [
        "mentions_together",           # Co-occurrence in documents
        "commands",                    # Org hierarchy
        "operated_by",                 # Org staffing
        "coordinates_with",            # Inter-org cooperation
        "supports",                    # Material support
        "recruited_by",                # Recruitment
        "location_proximity",          # Geographic co-location
        "temporal_proximity",          # Timeline correlation
    ],
    
    "confidence_thresholds": {
        "direct_mention": 0.95,        # Names mentioned together
        "contextual": 0.75,            # Contextual relationship
        "temporal": 0.65,              # Time-based correlation
        "geographic": 0.70,            # Location-based
    },
    
    "knowledge_graph": {
        "enabled": True,
        "export_interval": 3600,       # Export every hour
        "format": "json",
        "include_confidence": True,
        "include_sources": True,
    },
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_expanded_aliases() -> List[str]:
    """Get all aliases across all targets"""
    aliases = set()
    aliases.update(EXPANDED_MONICA_WITT_ALIASES)
    aliases.update(EXPANDED_IRGC_ALIASES)
    
    for associate in KNOWN_ASSOCIATES["operators"]:
        aliases.update(associate.get("aliases", []))
    
    for org in KNOWN_ASSOCIATES["organizations"]:
        aliases.update(org.get("aliases", []))
    
    return sorted(list(aliases))


def get_all_expanded_seed_urls() -> List[str]:
    """Get all seed URLs for continuous monitoring"""
    urls = []
    for url_list in EXPANDED_SEED_URLS.values():
        urls.extend(url_list)
    return list(set(urls))


def get_all_expanded_search_terms() -> List[str]:
    """Get all search terms"""
    terms = []
    for term_list in EXPANDED_SEARCH_TERMS.values():
        terms.extend(term_list)
    return list(set(terms))


def get_check_interval(profile: str = "standard") -> int:
    """Get check interval for profile"""
    return CONTINUOUS_MONITORING["check_intervals"].get(
        profile,
        CONTINUOUS_MONITORING["check_intervals"]["standard"]
    )


def is_peak_hours() -> bool:
    """Determine if current time is peak activity hours"""
    from datetime import datetime
    
    current_hour = datetime.now().hour
    schedule = CONTINUOUS_MONITORING["daily_schedule"]
    
    for start, end in schedule.get("high_activity_hours", []):
        if start <= current_hour < end:
            return True
    
    return False


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("24/7 CONTINUOUS MONITORING CONFIGURATION")
    print("=" * 70)
    
    print(f"\n📊 EXTENDED TARGETS:")
    print(f"   Monica Witt Aliases: {len(EXPANDED_MONICA_WITT_ALIASES)}")
    print(f"   IRGC Aliases: {len(EXPANDED_IRGC_ALIASES)}")
    print(f"   Known Associates: {len(KNOWN_ASSOCIATES['operators']) + len(KNOWN_ASSOCIATES['organizations'])}")
    
    print(f"\n🌐 MONITORING SOURCES:")
    print(f"   Total Seed URLs: {len(get_all_expanded_seed_urls())}")
    for category, urls in EXPANDED_SEED_URLS.items():
        print(f"     {category}: {len(urls)} sources")
    
    print(f"\n🔍 SEARCH COVERAGE:")
    print(f"   Total Unique Search Terms: {len(get_all_expanded_search_terms())}")
    for category, terms in EXPANDED_SEARCH_TERMS.items():
        print(f"     {category}: {len(terms)} terms")
    
    print(f"\n⏰ MONITORING PROFILE: {CONTINUOUS_MONITORING['profile']}")
    interval = get_check_interval(CONTINUOUS_MONITORING['profile'])
    print(f"   Check Interval: {interval}s ({interval // 60} min)")
    
    print(f"\n✅ Configuration loaded successfully!")


# Central inactive-by-default compatibility accessors.
from research_config import active_search_terms, verified_aliases
get_all_expanded_aliases = verified_aliases
get_all_expanded_search_terms = active_search_terms
def get_all_expanded_seed_urls():
    return []
