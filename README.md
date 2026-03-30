# MacroSignal
### Global Geopolitical Intelligence → International Market Signal Engine

> A system that monitors geopolitical events happening anywhere in the world and generates real-time **BUY / SELL / HOLD** signals across international stock indices, commodities, and currencies — powered by LLaMA 3 and XGBoost.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![LLaMA](https://img.shields.io/badge/LLM-LLaMA%203%20via%20Groq-orange?style=flat-square)
![XGBoost](https://img.shields.io/badge/ML-XGBoost-green?style=flat-square)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red?style=flat-square)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow?style=flat-square)

---

##  The Idea

Geopolitical events don't stay local. They ripple across the entire world.

When Russia escalated in Ukraine in February 2022:

```
One event. Eight consequences. Eight different markets.

Ukraine conflict escalates
        │
        ├── Wheat futures          +40%   Ukraine = 30% of global wheat supply
        ├── European energy stocks  -18%   Continent dependent on Russian gas
        ├── 🇩🇪 German DAX            -20%   Europe's largest economy, fully exposed
        ├── US Defence stocks      +14%   NATO countries begin rearming
        ├── Russian MOEX           -50%   Sanctions + capital flight
        ├── EUR/USD                -12%   European recession fears
        ├── Gold                   +10%   Global safe haven buying
        └── Corn futures           +30%   Food supply chain disruption
```

Most financial tools react *after* the market has already moved. MacroSignal is built to map these global ripple effects **the moment a headline breaks** — before the crowd prices them in.

---

##  What the System Does

The system works in three stages:

**Stage 1 — Read the event**

LLaMA 3 reads a news headline and extracts structured information:
- Which countries are involved
- What type of event it is (conflict, sanctions, election, rate decision...)
- How severe it is on a scale of 1 to 4
- Which regions are directly and indirectly exposed
- Confidence in the classification

**Stage 2 — Map global exposure**

For every affected region, the system looks up how that event type historically impacts:
- International stock indices (which national markets go up or down and why)
- Commodities (which supply chains break, which prices spike)
- Currencies (which strengthen as safe havens, which weaken under pressure)

**Stage 3 — Generate signals**

BUY / SELL / HOLD output for every tracked instrument, with a score and plain English reasoning. Signals are scaled by severity and confidence — a severity-4 event with 95% LLM confidence generates a much stronger signal than a severity-1 event at 60%.

---

## What MacroSignal Tracks

### International Stock Indices
| Index | Country | Why it matters geopolitically |
|-------|---------|-------------------------------|
| S&P 500 | 🇺🇸 USA | Global benchmark, affected by every major event |
| DAX | 🇩🇪 Germany | Europe's largest economy, highly export-dependent |
| FTSE 100 | 🇬🇧 UK | Heavy energy and mining sector weighting |
| Nikkei 225 | 🇯🇵 Japan | Semiconductor supply chains, North Asia conflict risk |
| Sensex | 🇮🇳 India | Emerging market bellwether, benefits from China tensions |
| Shanghai Composite | 🇨🇳 China | US-China trade war proxy, Taiwan Strait risk |
| ASX 200 | 🇦🇺 Australia | Iron ore, coal, LNG — China demand driven |
| MOEX | 🇷🇺 Russia | Direct sanctions and energy exposure |
| BIST 100 | 🇹🇷 Turkey | Regional crossroads between Middle East and Europe |
| JSE | 🇿🇦 South Africa | Gold, platinum, African political risk |

### Commodities
| Commodity | Geopolitical driver |
|-----------|---------------------|
| Crude Oil (WTI + Brent) | Middle East conflict, OPEC decisions, Russian supply cuts |
| Natural Gas | European energy dependency, Russian pipeline politics |
| Gold | Universal safe haven — rises with any global uncertainty |
| Wheat | Ukraine and Russia control 30% of global exports |
| Corn | US-China trade war, climate disasters, biofuel policy |
| Lithium | EV supply chains, China's dominance, South American politics |
| Copper | Global growth indicator, China manufacturing demand |
| Coal | European energy crisis, Asian demand and climate policy |

### Currencies
| Pair | Why it moves with geopolitics |
|------|-------------------------------|
| EUR/USD | European stability, ECB policy, Russia-Ukraine exposure |
| GBP/USD | UK political risk, post-Brexit fragility |
| JPY/USD | Yen is a safe haven — strengthens when the world gets nervous |
| USD/RUB | Russian sanctions, oil price dependency |
| USD/CNY | US-China trade tensions, Taiwan risk |
| USD/INR | India emerging market sentiment |

### More scope - might go local ( area or country specific )

---

##  How Events Map to Markets

The core knowledge base of the system — how each event type is expected to move each asset class:

| Event Type | Oil | Gold | Wheat | EUR/USD | Defence | Semiconductors |
|------------|-----|------|-------|---------|---------|----------------|
| Middle East conflict | ↑↑ Strong | ↑↑ Strong | → Neutral | ↓ Weak | ↑↑ Strong | ↓ Weak |
| Russia-Europe escalation | ↑↑ Strong | ↑↑ Strong | ↑↑ Strong | ↓↓ Very weak | ↑↑ Strong | → Neutral |
| US-China trade war | → Neutral | ↑ Moderate | → Neutral | → Neutral | → Neutral | ↓↓ Very weak |
| Taiwan crisis | ↑ Moderate | ↑↑ Strong | → Neutral | ↓ Weak | ↑↑ Strong | ↓↓↓ Severe |
| OPEC production cut | ↑↑↑ Severe | → Neutral | → Neutral | ↓ Weak | → Neutral | ↓ Weak |
| Interest rate hike | ↓ Weak | ↓↓ Strong | → Neutral | ↓ Weak | → Neutral | ↓↓ Strong |
| Global pandemic | ↓↓ Strong | ↑↑ Strong | ↑ Moderate | ↓ Weak | → Neutral | ↑ Moderate |
| Peace agreement | ↓ Weak | ↓↓ Strong | ↓ Weak | ↑ Moderate | ↓↓ Strong | ↑ Moderate |


---

## The LLM Component — Prompt Engineering

The headline goes in. Structured JSON comes out. No free text. No paragraphs. Just the exact data the pipeline needs.

**Input:**
```
"China conducts largest ever military exercises around Taiwan Strait"
```

**LLaMA 3 output:**
```json
{
  "event_type": "military_escalation",
  "primary_region": "asia",
  "countries_involved": ["China", "Taiwan", "USA"],
  "severity": 4,
  "confidence": 0.92,
  "affected_markets": {
    "indices": ["Shanghai", "Nikkei", "S&P500"],
    "commodities": ["Oil", "Gold", "Lithium"],
    "currencies": ["USD/CNY", "JPY/USD"]
  },
  "summary": "Military posturing threatening Taiwan Strait shipping lanes and global semiconductor supply chains"
}
```

Getting a large language model to output consistent, parseable JSON — with no preamble, no markdown, no hallucinated fields — is the core prompt engineering challenge of the project.

---

## Sample Output

```
════════════════════════════════════════════════════════════════
MACROSIGNAL — GLOBAL MARKET REPORT
════════════════════════════════════════════════════════════════
Headline:   China conducts military exercises around Taiwan
Event:      Military Escalation
Region:     Asia-Pacific
Severity:   4 / 4
Confidence: 92%
Taiwan Strait threatened — semiconductor supply chains
    and regional shipping lanes at acute risk

─── STOCK INDICES ───────────────────────────────────────────────
🇺🇸  S&P 500        🟡 HOLD   -0.8    Indirect supply chain exposure
🇩🇪  DAX            🟡 HOLD   -1.2    European chip manufacturing risk
🇯🇵  Nikkei 225     🔴 SELL   -3.6    Japan front-line exposure
🇨🇳  Shanghai       🔴 SELL   -2.8    Sanctions risk, capital flight
🇮🇳  Sensex         🟢 BUY    +1.4    Capital rotating into India
🇦🇺  ASX 200        🔴 SELL   -1.9    China trade dependency

─── COMMODITIES ─────────────────────────────────────────────────
Crude Oil       🟢 BUY    +2.8    Strait of Malacca disruption risk
Gold            🟢 BUY    +3.6    Global safe haven demand
Lithium         🔴 SELL   -3.2    Taiwan critical to chip supply chain
Wheat           🟡 HOLD    0.0    No direct impact

─── CURRENCIES ──────────────────────────────────────────────────
JPY / USD       🟢 BUY    +2.4    Yen safe haven buying
USD / CNY       🔴 SELL   -3.0    Yuan weakens on sanctions risk
USD / INR       🟡 HOLD   -0.6    Mild emerging market pressure

Highest conviction: Gold ↑   Lithium ↓   Nikkei ↓   JPY ↑
════════════════════════════════════════════════════════════════
```

---

## Backtesting — Real Events, Real Outcomes

| Date | Event | MacroSignal Called | What Actually Happened |
|------|-------|-------------------|------------------------|
| Feb 2022 | Russia invades Ukraine | Wheat ↑, DAX ↓, Gold ↑, EUR ↓ | Wheat +40%, DAX -20%, Gold +8%, EUR -12% |
| Oct 2022 | OPEC cuts 2M barrels/day | Oil ↑, Airlines ↓ | WTI +8%, Airline stocks -5% |
| Oct 2022 | US chip export ban on China | Nikkei ↓, Shanghai ↓, Lithium ↓ | Nikkei -3%, Shanghai -4%, Semis -8% |
| Oct 2023 | Israel-Hamas war begins | Oil ↑, Gold ↑, JETS ↓ | Oil +4%, Gold +8%, Airlines -6% |
| Mar 2023 | SVB bank collapse | Gold ↑, Bank stocks ↓ | Gold +4%, KBW Bank Index -22% |

---




## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| LLM | LLaMA 3 8B via Groq API | Free tier, fast, no GPU needed |
| ML Model | XGBoost | Best-in-class for structured financial data |
| Market Data | yfinance | Free, global coverage — indices, FX, commodities |
| News | RSS feeds (Reuters, BBC, Al Jazeera, FT) | Free, no rate limits, real global coverage |
| Dashboard | Streamlit | Python-native web app, zero frontend code |





## Disclaimer

This project is for educational and research purposes only. Nothing here constitutes financial advice. Always do your own research before making investment decisions.


## About

Built by **Soham** — exploring the intersection of geopolitical intelligence and quantitative finance.

> *The core insight: risk doesn't stay local. A conflict in one region disrupts supply chains, triggers capital flight, moves currencies, and reshapes entire sectors across the globe. MacroSignal maps those ripple effects systematically.*

---

