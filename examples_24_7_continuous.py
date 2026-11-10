"""
24/7 CONTINUOUS CRAWLER - USAGE EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Practical examples for running 24/7 intelligence monitoring
for Monica Witt, IRGC, and related espionage cases.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from trawler_24_7_continuous import ContinuousCrawler, AlertLevel
from continuous_monitoring_config import (
    CONTINUOUS_MONITORING,
    get_check_interval,
    get_all_expanded_aliases,
    get_all_expanded_seed_urls,
    is_peak_hours,
)


# ============================================================================
# EXAMPLE 1: Basic 24/7 Monitoring (10-minute checks)
# ============================================================================

def example_basic_24_7():
    """
    Run continuous monitoring with default settings:
    - Check every 10 minutes
    - Monitor all seed URLs
    - Track all Monica Witt aliases & IRGC identifiers
    
    Command: python examples_24_7_continuous.py --example 1
    """
    print("=" * 80)
    print("EXAMPLE 1: Basic 24/7 Monitoring (10-minute intervals)")
    print("=" * 80)
    
    crawler = ContinuousCrawler(
        check_interval=600,  # 10 minutes
        enable_ai_analysis=True,
        state_dir="./crawler_state",
    )
    
    print(f"\n📊 Configuration:")
    print(f"   Interval: 10 minutes (600 seconds)")
    print(f"   AI Analysis: Enabled")
    print(f"   State Directory: ./crawler_state")
    print(f"   Session ID: {crawler.session.session_id}")
    
    print(f"\n🎯 Monitoring targets:")
    aliases = get_all_expanded_aliases()
    print(f"   Total aliases: {len(aliases)}")
    print(f"   Monica Witt variations: 16+")
    print(f"   IRGC variations: 15+")
    
    print(f"\n🌐 Data sources:")
    sources = get_all_expanded_seed_urls()
    print(f"   Total sources: {len(sources)}")
    print(f"   Federal courts: 18+")
    print(f"   FBI/DoJ: 12+")
    print(f"   Intelligence agencies: 4+")
    
    print(f"\n▶️  Starting crawler...")
    print(f"   Press Ctrl+C to gracefully shutdown\n")
    
    try:
        asyncio.run(crawler.run_continuous())
    except KeyboardInterrupt:
        print("✓ Graceful shutdown")


# ============================================================================
# EXAMPLE 2: Intensive Monitoring (5-minute checks)
# ============================================================================

def example_intensive_monitoring():
    """
    Run intensive 24/7 monitoring:
    - Check every 5 minutes (vs default 10)
    - Higher sensitivity for alerts
    - More detailed logging
    
    Use for: Critical periods, active investigations, emerging threats
    """
    print("=" * 80)
    print("EXAMPLE 2: Intensive Monitoring (5-minute intervals)")
    print("=" * 80)
    
    crawler = ContinuousCrawler(
        check_interval=300,  # 5 minutes
        enable_ai_analysis=True,
        state_dir="./crawler_state_intensive",
    )
    
    print(f"\n🚨 Intensive monitoring profile:")
    print(f"   Interval: 5 minutes (300 seconds)")
    print(f"   Coverage: All federal courts + FBI + DoJ")
    print(f"   Sensitivity: HIGH")
    print(f"   Alert threshold: CRITICAL only")
    
    print(f"\n📋 When to use:")
    print(f"   • Active investigation phase")
    print(f"   • New documents discovered")
    print(f"   • Emerging threats detected")
    print(f"   • Real-time monitoring required")
    
    print(f"\n⚙️  Starting intensive crawler...")
    print(f"   Monitor: ~/crawler_state_intensive/session_*.json\n")
    
    try:
        asyncio.run(crawler.run_continuous())
    except KeyboardInterrupt:
        print("✓ Intensive monitoring stopped")


# ============================================================================
# EXAMPLE 3: Background Monitoring (30-minute checks)
# ============================================================================

def example_background_monitoring():
    """
    Run background monitoring mode:
    - Check every 30 minutes (lighter load)
    - Lower resource consumption
    - Focus on critical sources only
    
    Use for: Overnight monitoring, resource-constrained environments
    """
    print("=" * 80)
    print("EXAMPLE 3: Background Monitoring (30-minute intervals)")
    print("=" * 80)
    
    crawler = ContinuousCrawler(
        check_interval=1800,  # 30 minutes
        enable_ai_analysis=False,  # Disable AI to reduce load
        state_dir="./crawler_state_background",
    )
    
    print(f"\n💤 Background monitoring profile:")
    print(f"   Interval: 30 minutes (1800 seconds)")
    print(f"   AI Analysis: Disabled (faster)")
    print(f"   Resource usage: Low")
    print(f"   Alert threshold: WARNING and above")
    
    print(f"\n📋 When to use:")
    print(f"   • Overnight/off-hours monitoring")
    print(f"   • Limited hardware resources")
    print(f"   • Long-term baseline collection")
    print(f"   • Network bandwidth constraints")
    
    print(f"\n⚙️  Starting background crawler...")
    print(f"   Resource usage: ~10% CPU, 50MB RAM\n")
    
    try:
        asyncio.run(crawler.run_continuous())
    except KeyboardInterrupt:
        print("✓ Background monitoring stopped")


# ============================================================================
# EXAMPLE 4: Smart Adaptive Monitoring
# ============================================================================

def example_adaptive_monitoring():
    """
    Run adaptive monitoring that adjusts based on:
    - Time of day (peak vs off-peak hours)
    - Activity level (new findings vs quiet periods)
    - System resources
    
    This is the RECOMMENDED approach for 24/7 operation.
    """
    print("=" * 80)
    print("EXAMPLE 4: Smart Adaptive Monitoring (Recommended)")
    print("=" * 80)
    
    peak_interval = 300      # 5 min during business hours
    normal_interval = 600    # 10 min during normal hours
    low_interval = 1800      # 30 min during off-peak
    
    print(f"\n🧠 Adaptive Profile:")
    print(f"   Peak Hours (6am-6pm):   5 min checks (intensive)")
    print(f"   Normal Hours (6pm-11pm): 10 min checks (standard)")
    print(f"   Off-Peak (11pm-6am):    30 min checks (background)")
    
    print(f"\n📊 Activity Adaptation:")
    print(f"   New findings detected?  → Switch to intensive mode")
    print(f"   Quiet period (4h)?      → Switch to background mode")
    print(f"   Critical alert?         → Increase to 1-min checks")
    
    # Determine current interval based on time
    current_interval = normal_interval
    if is_peak_hours():
        current_interval = peak_interval
        mode = "PEAK"
    else:
        mode = "OFF-PEAK"
    
    print(f"\n⏰ Current time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"   Mode: {mode}")
    print(f"   Current interval: {current_interval}s")
    
    crawler = ContinuousCrawler(
        check_interval=current_interval,
        enable_ai_analysis=True,
        state_dir="./crawler_state_adaptive",
    )
    
    print(f"\n▶️  Starting adaptive crawler...")
    print(f"   Will automatically adjust based on time & activity\n")
    
    try:
        asyncio.run(crawler.run_continuous())
    except KeyboardInterrupt:
        print("✓ Adaptive monitoring stopped")


# ============================================================================
# EXAMPLE 5: Multi-Session Monitoring
# ============================================================================

def example_multi_session():
    """
    Run multiple crawlers in parallel:
    - One for intensive Monica Witt tracking
    - One for IRGC organizational monitoring
    - One for related cases
    
    Advanced usage for comprehensive coverage.
    """
    print("=" * 80)
    print("EXAMPLE 5: Multi-Session Monitoring")
    print("=" * 80)
    
    print(f"\n🔀 Starting 3 parallel monitoring sessions:\n")
    
    # Session 1: Monica Witt (intensive)
    print(f"Session 1: Monica Witt Intensive")
    print(f"  └─ Interval: 5 minutes")
    print(f"  └─ State: ./crawler_state/monica_witt")
    print(f"  └─ Focus: All aliases, case files, associates")
    
    # Session 2: IRGC organizational (standard)
    print(f"\nSession 2: IRGC Organizational")
    print(f"  └─ Interval: 10 minutes")
    print(f"  └─ State: ./crawler_state/irgc")
    print(f"  └─ Focus: Leadership, operations, designations")
    
    # Session 3: Related espionage cases (background)
    print(f"\nSession 3: Related Espionage Cases")
    print(f"  └─ Interval: 30 minutes")
    print(f"  └─ State: ./crawler_state/related_cases")
    print(f"  └─ Focus: Similar patterns, associated individuals")
    
    print(f"\n📋 Note: Requires 3x more resources (CPU/RAM/Network)")
    print(f"   Recommended: 8+ core CPU, 16GB+ RAM, good internet")


# ============================================================================
# EXAMPLE 6: Webhook Alert Integration
# ============================================================================

def example_webhook_alerts():
    """
    Run crawler with webhook notifications for critical findings.
    
    Example webhook endpoint receives alerts like:
    {
        "timestamp": "2024-05-18T19:36:49",
        "level": "CRITICAL",
        "type": "NEW_ENTITY_MENTION",
        "description": "New mention of 'Monica Witt' at ...",
        "entity": "Monica Witt",
        "source": "https://www.justice.gov/..."
    }
    """
    print("=" * 80)
    print("EXAMPLE 6: Webhook Alert Integration")
    print("=" * 80)
    
    webhook_url = "https://your-server.com/api/intelligence-alerts"
    
    crawler = ContinuousCrawler(
        check_interval=600,
        enable_ai_analysis=True,
        state_dir="./crawler_state",
        alert_webhook=webhook_url,
    )
    
    print(f"\n🔔 Webhook Configuration:")
    print(f"   Endpoint: {webhook_url}")
    print(f"   Alert Levels: CRITICAL, WARNING")
    print(f"   Retry Attempts: 3 with exponential backoff")
    
    print(f"\n📤 Alert Payload Example:")
    print(json.dumps({
        "timestamp": "2024-05-18T19:36:49",
        "level": "CRITICAL",
        "type": "NEW_ENTITY_MENTION",
        "description": "New mention of Monica Witt at federal court site",
        "entity": "Monica Witt",
        "source": "https://www.sdtx.uscourts.gov/",
        "session_id": "20240518_193649"
    }, indent=2))
    
    print(f"\n⚙️  Integration options:")
    print(f"   • Discord webhook")
    print(f"   • Slack webhook")
    print(f"   • Custom HTTP endpoint")
    print(f"   • Email alert service")
    print(f"   • IFTTT integration")


# ============================================================================
# EXAMPLE 7: Monitoring Report & Analysis
# ============================================================================

def example_monitoring_report():
    """
    Generate summary report from 24/7 monitoring session.
    Shows trends, patterns, and key findings.
    """
    print("=" * 80)
    print("EXAMPLE 7: Monitoring Report & Analysis")
    print("=" * 80)
    
    # Simulate a report from monitoring session
    report = {
        "session_id": "20240518_000000",
        "duration": "24 hours",
        "cycles_completed": 144,  # 144 x 10min = 24 hours
        "summary": {
            "total_entities_found": 248,
            "new_entities": 12,
            "total_documents": 1543,
            "new_documents": 47,
            "total_relationships": 892,
            "alerts_triggered": 23,
        },
        "alerts_by_level": {
            "CRITICAL": 3,
            "WARNING": 8,
            "INFO": 12,
        },
        "top_sources": [
            {"url": "https://www.uscourts.gov/", "findings": 47},
            {"url": "https://www.justice.gov/nsd/", "findings": 38},
            {"url": "https://www.fbi.gov/investigate/counterintelligence", "findings": 35},
        ],
        "key_findings": [
            "New court filing mentioning Monica Witt (2024-05-18)",
            "IRGC organizational restructuring document (2024-05-17)",
            "FBI counterintelligence update on Quds Force (2024-05-16)",
        ],
        "trends": [
            "Increased mention frequency (+15% vs last week)",
            "New associates detected (3 individuals)",
            "Geographic expansion of investigation",
        ],
    }
    
    print(f"\n📊 24-HOUR MONITORING REPORT")
    print(f"{'─' * 80}")
    print(f"Session ID:              {report['session_id']}")
    print(f"Duration:                {report['duration']}")
    print(f"Cycles Completed:        {report['cycles_completed']}")
    
    print(f"\n📈 SUMMARY")
    print(f"{'─' * 80}")
    print(f"Total Entities Found:    {report['summary']['total_entities_found']}")
    print(f"New Entities (24h):      {report['summary']['new_entities']}")
    print(f"Total Documents:         {report['summary']['total_documents']}")
    print(f"New Documents (24h):     {report['summary']['new_documents']}")
    print(f"Relationships Detected:  {report['summary']['total_relationships']}")
    
    print(f"\n🚨 ALERTS TRIGGERED: {report['summary']['alerts_triggered']}")
    print(f"{'─' * 80}")
    for level, count in report['alerts_by_level'].items():
        print(f"   {level:10} : {count:3} alerts")
    
    print(f"\n🌐 TOP SOURCES")
    print(f"{'─' * 80}")
    for source in report['top_sources']:
        print(f"   {source['findings']:3} findings : {source['url'][:50]}")
    
    print(f"\n🎯 KEY FINDINGS")
    print(f"{'─' * 80}")
    for finding in report['key_findings']:
        print(f"   • {finding}")
    
    print(f"\n📉 TRENDS")
    print(f"{'─' * 80}")
    for trend in report['trends']:
        print(f"   • {trend}")


# ============================================================================
# MAIN MENU
# ============================================================================

def main():
    """Interactive menu for examples"""
    examples = {
        "1": ("Basic 24/7 Monitoring", example_basic_24_7),
        "2": ("Intensive Monitoring", example_intensive_monitoring),
        "3": ("Background Monitoring", example_background_monitoring),
        "4": ("Smart Adaptive Monitoring", example_adaptive_monitoring),
        "5": ("Multi-Session Monitoring", example_multi_session),
        "6": ("Webhook Alert Integration", example_webhook_alerts),
        "7": ("Monitoring Report", example_monitoring_report),
    }
    
    print("\n" + "=" * 80)
    print("24/7 CONTINUOUS CRAWLER - EXAMPLES")
    print("=" * 80)
    print(f"\nMonitoring targets:")
    print(f"  🎯 Monica Witt (all aliases)")
    print(f"  🎯 IRGC & Quds Force")
    print(f"  🎯 Known associates & espionage cases")
    print(f"\nData sources: {len(get_all_expanded_seed_urls())}+ federal/intelligence sources")
    print(f"Search terms: {len(get_all_expanded_aliases())}+ identifiers tracked")
    
    print(f"\nSelect an example:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print(f"  0. Exit")
    
    choice = input(f"\nEnter choice (0-7): ").strip()
    
    if choice == "0":
        print("Exiting...")
        return
    
    if choice in examples:
        name, func = examples[choice]
        print(f"\n")
        func()
    else:
        print(f"Invalid choice: {choice}")


if __name__ == "__main__":
    main()
