import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd

from data_pipeline.event_mapper import IMPACT_MATRIX, ETF_DESCRIPTIONS, get_expected_impact, get_signal_from_score
from data_pipeline.news_fetcher import HISTORICAL_EVENTS
from llm_engine.signal_generator import generate_signals_from_analysis, analyse_headline_without_llm

# PAGE CONFIG
st.set_page_config(
    page_title = "Macrosignal",
    layout     = "wide",
    initial_sidebar_state = "expanded"
)

# CUSTOM CSS
st.markdown("""
<style>
    .buy-signal   { color: #00c853; font-weight: bold; font-size: 1.1rem; }
    .sell-signal  { color: #f44336; font-weight: bold; font-size: 1.1rem; }
    .hold-signal  { color: #ff9800; font-weight: bold; font-size: 1.1rem; }
    .metric-label { font-size: 0.8rem; color: #888; }
    .headline-box { background: #1e1e2e; padding: 1rem; border-radius: 8px;
                    border-left: 4px solid #7c3aed; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ────────────────────────────────────────────────────
with st.sidebar:
    st.title(" Settings")

    use_groq = st.checkbox(" Use LLaMA 3 (Groq API)", value=False,
                           help="Requires Groq API key in config.py")

    st.divider()
    st.subheader(" About")
    st.markdown("""
    **GeoFinance AI** predicts ETF market signals
    based on geopolitical news analysis.

    **How it works:**
    1. Enter a news headline
    2. LLM classifies the event type
    3. Impact matrix maps event → ETF effects
    4. Signals generated: BUY / SELL / HOLD

    **ETFs tracked:**
    - XLE — Energy / Oil
    - GLD — Gold
    - ITA — Defence
    - SOXX — Semiconductors
    - JETS — Airlines
    - XLF — Financials
    - TLT — Bonds
    - DBA — Agriculture
    """)


# ── MAIN HEADER ────────────────────────────────────────────────
st.title(" Macrosignal")
st.subheader("Geopolitical Risk → Market Signal Analysis")
st.divider()


# ── TAB LAYOUT ─────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Live Analysis", "Historical Events", "Event Map"])


# ══════════════════════════════════════════════════════════════
# TAB 1 — Live Headline Analysis
# ══════════════════════════════════════════════════════════════
with tab1:
    st.header("Analyse a Headline")

    # Input section
    col1, col2 = st.columns([3, 1])
    with col1:
        headline = st.text_input(
            "Enter a geopolitical news headline:",
            placeholder="e.g. Russia launches strikes on Ukraine energy grid"
        )
    with col2:
        severity_override = st.slider("Severity", 1, 4, 2, help="1=Minor, 4=Critical")

    # Example headlines
    st.caption("Try these examples:")
    example_cols = st.columns(3)
    examples = [
        "Russia escalates military operations in Ukraine",
        "Federal Reserve raises interest rates by 0.75%",
        "US announces major chip export ban on China",
        "OPEC agrees to cut oil production",
        "Israel and Hamas reach ceasefire deal",
        "Pandemic emergency declared by WHO",
    ]
    for i, ex in enumerate(examples):
        if example_cols[i % 3].button(ex[:40] + "...", key=f"ex_{i}"):
            headline = ex

    # Analyse button
    if st.button("Analyse", type="primary") and headline:

        with st.spinner("Analysing..."):

            # Run analysis
            if use_groq:
                try:
                    from config import GROQ_API_KEY
                    from llm_engine.groq_client import GeoFinanceAnalyser
                    analyser = GeoFinanceAnalyser()
                    analysis = analyser.analyse(headline)
                    analysis["severity"] = severity_override   # allow manual override
                    st.success("LLaMA 3 analysis complete")
                except Exception as e:
                    st.warning(f"Groq failed: {e}. Using rule-based fallback.")
                    analysis = analyse_headline_without_llm(headline)
            else:
                analysis = analyse_headline_without_llm(headline)
                analysis["severity"] = severity_override

            # Generate signals
            output = generate_signals_from_analysis(analysis)

        # RESULTS DISPLAY 
        st.divider()

        # Event metadata
        meta_col1, meta_col2, meta_col3, meta_col4 = st.columns(4)
        meta_col1.metric("Event Type", analysis["event_type"].replace("_", " ").title())
        meta_col2.metric("Region",     analysis["region"].replace("_", " ").title())
        meta_col3.metric("Severity",   f"{analysis['severity']}/4")
        meta_col4.metric("Confidence", f"{analysis['confidence']:.0%}")

        if analysis.get("summary"):
            st.info(f"{analysis['summary']}")

        st.divider()

        # Signal cards
        st.subheader("Market Signals")
        signals = output["signals"]

        # Display in a grid
        cols = st.columns(4)
        sorted_signals = sorted(signals.items(), key=lambda x: abs(x[1]["score"]), reverse=True)

        for i, (etf, data) in enumerate(sorted_signals):
            with cols[i % 4]:
                signal = data["signal"]
                score  = data["score"]

                colour = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "🟡"
                delta_sign = f"+{score:.2f}" if score > 0 else f"{score:.2f}"

                st.metric(
                    label = f"{colour} {etf}",
                    value = signal,
                    delta = delta_sign,
                )
                st.caption(data["description"][:35])

        # Top movers table
        st.subheader("Highest Impact ETFs")
        top_df = pd.DataFrame(output["top_movers"], columns=["ETF", "Score"])
        top_df["Signal"]    = top_df["Score"].apply(get_signal_from_score)
        top_df["Direction"] = top_df["Score"].apply(lambda s: "↑ LONG" if s > 0 else "↓ SHORT")
        top_df["Score"]     = top_df["Score"].apply(lambda s: f"{s:+.2f}")
        st.dataframe(top_df, use_container_width=True, hide_index=True)



# TAB 2 — Historical Events

with tab2:
    st.header("Historical Events & Actual Market Reactions")
    st.caption("These are real events with real market outcomes — used for model validation")

    for event in HISTORICAL_EVENTS:
        with st.expander(f"{event['date']}  —  {event['title']}"):

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Type:** {event['event_type'].replace('_', ' ').title()}")
                st.markdown(f"**Region:** {event['region'].replace('_', ' ').title()}")
                st.markdown(f"**Severity:** {event['severity']}/4")

            with col2:
                st.markdown("**Actual Market Reactions:**")
                for key, val in event.items():
                    if key.startswith("actual_") and key.endswith("_change"):
                        etf = key.replace("actual_", "").replace("_change", "").upper()
                        colour = "🟢" if val > 0 else "🔴"
                        st.markdown(f"  {colour} **{etf}**: {val:+.1f}%")

            # Run our model's prediction
            analysis = {
                "event_type":  event["event_type"],
                "region":      event["region"],
                "severity":    event["severity"],
                "confidence":  0.8,
                "summary":     event["title"],
                "headline":    event["title"]
            }
            output = generate_signals_from_analysis(analysis)

            st.markdown("**Our Model's Signals:**")
            signal_cols = st.columns(len(output["signals"]))
            for i, (etf, data) in enumerate(output["signals"].items()):
                sig = data["signal"]
                icon = "🟢" if sig == "BUY" else "🔴" if sig == "SELL" else "🟡"
                signal_cols[i].markdown(f"**{etf}**<br>{icon}{sig}", unsafe_allow_html=True)



# TAB 3 — Event Impact Map

with tab3:
    st.header("Event → ETF Impact Map")
    st.caption("Explore how different event types affect each market sector")

    # Event selector
    event_type = st.selectbox(
        "Select event type:",
        options = list(IMPACT_MATRIX.keys()),
        format_func = lambda x: x.replace("_", " ").title()
    )

    region = st.select_slider(
        "Region:",
        options = ["middle_east", "europe", "asia", "north_america", "global"],
        value   = "global"
    )

    severity = st.slider("Severity:", 1, 4, 2)

    # Get impacts
    impacts = get_expected_impact(event_type, region, severity)

    # Build display dataframe
    rows = []
    for etf, score in sorted(impacts.items(), key=lambda x: -abs(x[1])):
        rows.append({
            "ETF":         etf,
            "Description": ETF_DESCRIPTIONS[etf],
            "Score":       score,
            "Signal":      get_signal_from_score(score),
            "Bar":         " " * min(int(abs(score)), 10) if score != 0 else "─"
        })

    impact_df = pd.DataFrame(rows)

    # Style the dataframe
    def colour_signal(val):
        if val == "BUY":  return "color: #00c853; font-weight: bold"
        if val == "SELL": return "color: #f44336; font-weight: bold"
        return "color: #ff9800"

    styled = impact_df.style.applymap(colour_signal, subset=["Signal"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # Show event examples
    event_data = IMPACT_MATRIX[event_type]
    st.subheader("Real-World Examples")
    for ex in event_data["examples"]:
        st.markdown(f"- {ex}")
