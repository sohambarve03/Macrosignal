# ══════════════════════════════════════════════════════════════
# data_pipeline/event_mapper.py
#
# 📖 WHAT THIS FILE DOES:
#   This is the "knowledge base" of the project — a dictionary
#   that maps real-world geopolitical events to their expected
#   effect on each ETF (market sector).
#
# 📖 WHY THIS MATTERS:
#   When LLaMA reads a headline like "Russia escalates Ukraine war",
#   it classifies it as event_type="conflict_escalation", region="europe".
#   This file then tells us: ok, that means XLE (oil) goes UP,
#   JETS (airlines) goes DOWN, ITA (defence) goes UP.
#
# 📖 WHAT IS AN ETF?
#   ETF = Exchange Traded Fund. Instead of buying one stock,
#   you buy a "basket" of related stocks. Safer, cleaner signals.
#   XLE = top oil companies, GLD = gold price, ITA = defence companies
# ══════════════════════════════════════════════════════════════

# ── ETF DESCRIPTIONS ───────────────────────────────────────────
# Key: ticker symbol  |  Value: what sector it represents
ETF_DESCRIPTIONS = {
    "XLE":  "Energy / Oil & Gas (ExxonMobil, Chevron, Shell)",
    "GLD":  "Gold (safe-haven asset, rises in uncertainty)",
    "ITA":  "Defence & Aerospace (Lockheed, Raytheon, Boeing)",
    "SOXX": "Semiconductors / Chips (Nvidia, Intel, TSMC)",
    "JETS": "Airlines & Aviation (Delta, United, Ryanair)",
    "XLF":  "Financials / Banks (JPMorgan, Goldman, Bank of America)",
    "TLT":  "US Government Bonds (20+ year treasury bonds)",
    "DBA":  "Agriculture / Food Commodities (wheat, corn, soybeans)",
}

# ── THE IMPACT MATRIX ──────────────────────────────────────────
# This is the core knowledge of the project.
# Structure: event_type → region_modifier → {ETF: impact_score}
#
# Impact scores:
#   +4 = very strong positive (strong BUY signal)
#   +2 = moderate positive
#    0 = no effect
#   -2 = moderate negative
#   -4 = very strong negative (strong SELL signal)

IMPACT_MATRIX = {

    "conflict_escalation": {
        # War / military conflict starting or intensifying
        "description": "Military conflict escalating or new war starting",
        "examples": ["Russia Ukraine escalation", "Middle East military strikes", "Taiwan Strait tensions"],
        "base_impacts": {
            "XLE":  3,   # Oil spikes when supply routes threatened
            "GLD":  4,   # Gold always rises in war — safe haven
            "ITA":  4,   # Defence contractors get huge contracts
            "SOXX":-2,   # Chips supply chains disrupted
            "JETS":-4,   # Airlines collapse (no-fly zones, fear)
            "XLF": -2,   # Banks hate uncertainty
            "TLT":  2,   # Government bonds rise (flight to safety)
            "DBA":  2,   # Food prices rise (supply disruption)
        },
        "region_multipliers": {
            "middle_east": {"XLE": 1.5},        # Middle East = extra oil impact
            "europe":      {"DBA": 1.5},        # Ukraine = extra food impact
            "asia":        {"SOXX": -1.5},      # Taiwan/China = extra chip impact
            "global":      {"GLD": 1.3},        # Global crisis = extra gold
        }
    },

    "conflict_resolution": {
        # Peace deals, ceasefires, diplomatic breakthroughs
        "description": "Peace negotiations, ceasefires, or conflict ending",
        "examples": ["Israel Hamas ceasefire", "Russia Ukraine peace talks", "NATO de-escalation"],
        "base_impacts": {
            "XLE": -2,   # Oil drops when supply fears ease
            "GLD": -3,   # Gold falls when fear goes away
            "ITA": -2,   # Defence spending may decrease
            "SOXX": 2,   # Supply chains normalize
            "JETS": 3,   # Airlines recover
            "XLF":  2,   # Banks love stability
            "TLT": -1,   # Bonds less needed as safe haven
            "DBA": -2,   # Food prices normalise
        },
        "region_multipliers": {
            "middle_east": {"XLE": 1.4},
            "europe":      {"DBA": 1.3},
        }
    },

    "trade_war": {
        # Tariffs, sanctions, trade restrictions between major economies
        "description": "Countries imposing tariffs or trade restrictions",
        "examples": ["US China tariffs", "EU sanctions on Russia", "semiconductor export ban"],
        "base_impacts": {
            "XLE": -1,
            "GLD":  2,   # Gold rises with economic uncertainty
            "ITA":  1,
            "SOXX":-4,   # Chip makers hurt most by trade restrictions
            "JETS":-2,
            "XLF": -2,
            "TLT":  1,
            "DBA": -1,
        },
        "region_multipliers": {
            "asia":   {"SOXX": 1.8},    # US-China = devastating for chips
            "global": {"GLD":  1.4},
        }
    },

    "sanctions": {
        # Economic sanctions imposed on a country
        "description": "International economic sanctions on a country",
        "examples": ["Iran oil sanctions", "Russia SWIFT ban", "North Korea sanctions"],
        "base_impacts": {
            "XLE":  3,   # Sanctions on oil producers = supply shock
            "GLD":  2,
            "ITA":  1,
            "SOXX":-1,
            "JETS":-1,
            "XLF": -3,   # Banks exposed to sanctioned country suffer
            "TLT":  1,
            "DBA":  2,
        },
        "region_multipliers": {
            "middle_east": {"XLE": 2.0},   # Sanctioning oil producers = big spike
            "europe":      {"XLF": 1.5},   # European banks exposed to Russia
        }
    },

    "election": {
        # Major election result in a significant economy
        "description": "Election results or political transition",
        "examples": ["US presidential election", "French election", "emerging market election"],
        "base_impacts": {
            "XLE":  0,   # Depends on who wins — neutral base
            "GLD":  1,   # Slight uncertainty premium
            "ITA":  0,
            "SOXX": 0,
            "JETS": 0,
            "XLF":  1,   # Markets tend to rally post-election (certainty)
            "TLT": -1,
            "DBA":  0,
        },
        "region_multipliers": {
            "north_america": {"XLF": 2.0, "SOXX": 1.5},   # US election = huge market impact
        }
    },

    "interest_rate_hike": {
        # Central bank raising interest rates
        "description": "Central bank increasing interest rates",
        "examples": ["Fed raises rates", "ECB rate hike", "Bank of England increases rates"],
        "base_impacts": {
            "XLE": -1,
            "GLD": -2,   # Gold falls — bonds become more attractive
            "ITA": -1,
            "SOXX":-3,   # Growth stocks hit hard by rate hikes
            "JETS":-1,
            "XLF":  3,   # Banks profit from higher rates
            "TLT": -4,   # Bond prices fall when rates rise (inverse relationship)
            "DBA":  0,
        },
        "region_multipliers": {
            "north_america": {"XLF": 1.5, "TLT": 1.5},
        }
    },

    "interest_rate_cut": {
        # Central bank lowering interest rates
        "description": "Central bank cutting interest rates",
        "examples": ["Fed cuts rates", "ECB rate cut", "emergency rate cut"],
        "base_impacts": {
            "XLE":  1,
            "GLD":  3,   # Gold rises when rates cut (opportunity cost falls)
            "ITA":  1,
            "SOXX": 3,   # Growth stocks love low rates
            "JETS": 2,
            "XLF": -2,   # Banks earn less on loans
            "TLT":  4,   # Bond prices rise when rates fall
            "DBA":  1,
        },
        "region_multipliers": {
            "north_america": {"TLT": 1.4, "SOXX": 1.3},
        }
    },

    "energy_crisis": {
        # Oil/gas supply shock or energy shortage
        "description": "Energy supply disruption or shortage",
        "examples": ["OPEC cuts production", "pipeline attack", "gas shortage in Europe"],
        "base_impacts": {
            "XLE":  4,   # Energy companies profit massively
            "GLD":  2,
            "ITA":  0,
            "SOXX":-2,   # Manufacturing costs rise
            "JETS":-4,   # Airlines' biggest cost is fuel
            "XLF": -1,
            "TLT":  1,
            "DBA":  2,   # Food production costs rise
        },
        "region_multipliers": {
            "middle_east": {"XLE": 2.0},
            "europe":      {"XLE": 1.6, "JETS": 1.4},
        }
    },

    "pandemic": {
        # Disease outbreak or public health emergency
        "description": "Disease outbreak, lockdowns, or health emergency",
        "examples": ["COVID lockdown", "new virus variant", "WHO emergency declaration"],
        "base_impacts": {
            "XLE": -3,
            "GLD":  3,
            "ITA":  0,
            "SOXX": 1,   # Tech/remote work benefits
            "JETS":-4,   # Airlines devastated
            "XLF": -2,
            "TLT":  3,
            "DBA":  1,
        },
        "region_multipliers": {
            "asia":   {"SOXX": 1.3},
            "global": {"GLD":  1.5, "JETS": 1.3},
        }
    },

    "climate_disaster": {
        # Major natural disaster or climate event
        "description": "Hurricane, earthquake, flood, or major climate event",
        "examples": ["Gulf hurricane season", "Japan earthquake", "European floods"],
        "base_impacts": {
            "XLE":  2,   # Oil infrastructure damage = supply shock
            "GLD":  1,
            "ITA":  0,
            "SOXX":-1,
            "JETS":-2,
            "XLF": -1,
            "TLT":  1,
            "DBA":  2,   # Crop damage = food prices up
        },
        "region_multipliers": {
            "north_america": {"XLE": 1.5},
            "asia":          {"SOXX": 1.4},
        }
    },
}

# ── REGION DEFINITIONS ─────────────────────────────────────────
REGION_KEYWORDS = {
    "middle_east": ["iran", "iraq", "saudi", "israel", "gaza", "lebanon",
                    "syria", "yemen", "qatar", "uae", "persian gulf", "opec"],
    "europe":      ["russia", "ukraine", "eu", "europe", "nato", "germany",
                    "france", "uk", "britain", "poland", "germany"],
    "asia":        ["china", "taiwan", "japan", "korea", "india", "hong kong",
                    "beijing", "shanghai", "south china sea"],
    "north_america": ["us", "usa", "united states", "america", "fed", "federal reserve",
                      "canada", "washington", "wall street"],
    "global":      ["global", "worldwide", "international", "imf", "world bank",
                    "g7", "g20", "united nations", "un"],
}


# ── FUNCTIONS ──────────────────────────────────────────────────

def detect_region(text):
    """
    Detect which region a news headline is about.
    Returns the region name or 'global' if unclear.
    """
    text_lower = text.lower()
    for region, keywords in REGION_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            return region
    return "global"


def get_expected_impact(event_type, region="global", severity=2):
    """
    Get expected ETF impact scores for a geopolitical event.

    Args:
        event_type (str): One of the keys in IMPACT_MATRIX
        region     (str): Region where event is happening
        severity   (int): 1=minor, 2=moderate, 3=high, 4=critical

    Returns:
        dict: {ETF_ticker: impact_score} for all 8 ETFs

    Example:
        >>> get_expected_impact("conflict_escalation", "middle_east", 3)
        {"XLE": 4.5, "GLD": 4.0, "ITA": 4.0, ...}
    """
    # Check event type exists in our matrix
    if event_type not in IMPACT_MATRIX:
        print(f"⚠️  Unknown event type: {event_type}")
        return {etf: 0 for etf in ETF_DESCRIPTIONS.keys()}

    event_data = IMPACT_MATRIX[event_type]
    base_impacts = event_data["base_impacts"].copy()

    # Apply regional multipliers if they exist for this region
    region_mults = event_data.get("region_multipliers", {}).get(region, {})
    for etf, multiplier in region_mults.items():
        if etf in base_impacts:
            base_impacts[etf] *= multiplier

    # Apply severity scaling
    # severity 1 = 50% impact, 2 = 100%, 3 = 150%, 4 = 200%
    severity_scale = severity / 2.0
    final_impacts = {
        etf: round(score * severity_scale, 2)
        for etf, score in base_impacts.items()
    }

    return final_impacts


def get_signal_from_score(score):
    """Convert a numeric score to a BUY/SELL/HOLD signal."""
    if score >= 1.0:
        return "BUY"
    elif score <= -1.0:
        return "SELL"
    else:
        return "HOLD"


def summarise_event(event_type, region="global", severity=2):
    """
    Print a human-readable summary of an event's expected market impact.
    Great for understanding the project logic.
    """
    if event_type not in IMPACT_MATRIX:
        print(f"Unknown event type: {event_type}")
        return

    impacts = get_expected_impact(event_type, region, severity)
    event_info = IMPACT_MATRIX[event_type]

    print(f"\n{'='*55}")
    print(f"EVENT:    {event_type.upper().replace('_', ' ')}")
    print(f"REGION:   {region}")
    print(f"SEVERITY: {severity}/4")
    print(f"{'='*55}")

    for etf, score in sorted(impacts.items(), key=lambda x: -abs(x[1])):
        signal  = get_signal_from_score(score)
        bar     = "█" * int(abs(score))
        arrow   = "↑" if score > 0 else "↓" if score < 0 else "→"
        print(f"  {etf:5s}  {signal:4s}  {arrow} {score:+.1f}  {bar}")

    print(f"\n  📋 Examples: {', '.join(event_info['examples'][:2])}")


# ── TEST IT ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🗺️  GeoFinance Event Mapper — Testing\n")

    # Test 1: Middle East conflict
    summarise_event("conflict_escalation", "middle_east", severity=3)

    # Test 2: Rate hike
    summarise_event("interest_rate_hike", "north_america", severity=2)

    # Test 3: Trade war with China
    summarise_event("trade_war", "asia", severity=3)

    # Test detect_region
    headline = "Russia launches new offensive in Ukraine"
    region = detect_region(headline)
    print(f"\n🌍 Detected region for '{headline}': {region}")
