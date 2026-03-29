
import feedparser       # reads RSS feeds (pip install feedparser)
import json
import os
from datetime import datetime
from data_pipeline.event_mapper import detect_region

# RSS FEED SOURCES 
# Free geopolitical/financial news feeds — no API key needed
RSS_FEEDS = {
    "Reuters World":    "https://feeds.reuters.com/reuters/worldNews",
    "BBC World":        "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Al Jazeera":       "https://www.aljazeera.com/xml/rss/all.xml",
    "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    "FT World":         "https://www.ft.com/world?format=rss",
}

# Keywords that flag a headline as geopolitically relevant
GEOPOLITICAL_KEYWORDS = [
    "war", "conflict", "attack", "invasion", "military", "sanctions",
    "tariff", "trade", "election", "president", "oil", "energy",
    "interest rate", "fed", "central bank", "inflation", "recession",
    "missile", "nuclear", "nato", "opec", "crisis", "agreement",
    "ceasefire", "treaty", "coup", "protest", "sanctions"
]


def fetch_headlines(max_per_source=10):
    """
    Fetch latest geopolitical headlines from all RSS sources.

    Returns:
        list of dicts: [{title, source, region, published, url}]
    """
    all_headlines = []

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            print(f"  Fetching from {source_name}...")
            feed = feedparser.parse(feed_url)

            count = 0
            for entry in feed.entries:
                if count >= max_per_source:
                    break

                title = entry.get("title", "").strip()
                if not title:
                    continue

                # Only keep geopolitically relevant headlines
                title_lower = title.lower()
                is_relevant = any(kw in title_lower for kw in GEOPOLITICAL_KEYWORDS)

                if is_relevant:
                    all_headlines.append({
                        "title":     title,
                        "source":    source_name,
                        "region":    detect_region(title),
                        "published": entry.get("published", "Unknown"),
                        "url":       entry.get("link", ""),
                        "fetched_at": datetime.now().isoformat()
                    })
                    count += 1

        except Exception as e:
            print(f"  Could not fetch {source_name}: {e}")

    print(f"\n Fetched {len(all_headlines)} relevant headlines total")
    return all_headlines


def save_headlines(headlines, output_path="data/raw/headlines.json"):
    """Save headlines to a JSON file for later use."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(headlines, f, indent=2)
    print(f" Saved to {output_path}")


def load_headlines(path="data/raw/headlines.json"):
    """Load previously saved headlines."""
    if not os.path.exists(path):
        print(f" No headlines file found at {path}. Run fetch_headlines() first.")
        return []
    with open(path, "r") as f:
        return json.load(f)


# SAMPLE HISTORICAL EVENTS
# For testing without internet — real past events with known outcomes
HISTORICAL_EVENTS = [
    {
        "title":    "Russia launches full-scale invasion of Ukraine",
        "date":     "2022-02-24",
        "region":   "europe",
        "event_type": "conflict_escalation",
        "severity": 4,
        "actual_xle_change": 8.2,    # XLE went up 8.2% next week
        "actual_gld_change": 3.1,
    },
    {
        "title":    "US Fed raises interest rates by 75 basis points",
        "date":     "2022-06-15",
        "region":   "north_america",
        "event_type": "interest_rate_hike",
        "severity": 3,
        "actual_xlf_change": 2.1,
        "actual_tlt_change": -5.8,
    },
    {
        "title":    "OPEC agrees to cut oil production by 2 million barrels",
        "date":     "2022-10-05",
        "region":   "middle_east",
        "event_type": "energy_crisis",
        "severity": 3,
        "actual_xle_change": 5.4,
        "actual_jets_change": -3.2,
    },
    {
        "title":    "US imposes sweeping chip export ban on China",
        "date":     "2022-10-07",
        "region":   "asia",
        "event_type": "trade_war",
        "severity": 4,
        "actual_soxx_change": -7.8,
        "actual_gld_change": 1.2,
    },
    {
        "title":    "Israel declares war after Hamas attack",
        "date":     "2023-10-08",
        "region":   "middle_east",
        "event_type": "conflict_escalation",
        "severity": 4,
        "actual_xle_change": 4.1,
        "actual_gld_change": 2.8,
        "actual_jets_change": -4.5,
    },
    {
        "title":    "Fed signals end of rate hiking cycle",
        "date":     "2023-11-01",
        "region":   "north_america",
        "event_type": "interest_rate_cut",
        "severity": 2,
        "actual_tlt_change": 5.2,
        "actual_soxx_change": 4.1,
    },
]


# TEST / RUN
if __name__ == "__main__":
    print(" GeoFinance News Fetcher\n")

    # Show historical events (works without internet)
    print(" Historical Events in our database:")
    for event in HISTORICAL_EVENTS:
        print(f"  [{event['date']}] {event['title']}")
        print(f"    Region: {event['region']} | Type: {event['event_type']} | Severity: {event['severity']}/4\n")

    # Try live fetch
    print("\n Attempting live news fetch...")
    try:
        headlines = fetch_headlines(max_per_source=5)
        if headlines:
            print(f"\n Sample live headlines:")
            for h in headlines[:3]:
                print(f"  [{h['region'].upper()}] {h['title']}")
            save_headlines(headlines)
    except Exception as e:
        print(f"Live fetch failed (normal if no internet): {e}")
        print("Using historical events for now — that's fine for development!")
