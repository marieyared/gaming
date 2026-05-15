"""
orion_sim.py — ORION Macroeconomic Strategy Simulator
Run with: streamlit run orion_sim.py
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json, os, requests, random

st.set_page_config(
    page_title="ORION",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ════════════════════════════════════════════════════════════════
# THEME
# ════════════════════════════════════════════════════════════════
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body { background: #070a11 !important; }
.stApp { background: #070a11 !important; }
.main { background: #070a11 !important; }
.main .block-container { background: transparent !important; padding: 2.5rem 2.5rem 5rem; max-width: 1240px; }
*, p, div, span, label, h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif !important; }
footer, #MainMenu, header { visibility: hidden !important; }

[data-testid="stMetric"] {
    background: #0f1624 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    padding: 1.2rem !important;
}
[data-testid="stMetricLabel"] p { color: #64748b !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.08em; white-space: normal !important; }
[data-testid="stMetricValue"] { color: #f1f5f9 !important; font-family: 'DM Mono', monospace !important; font-size: 20px !important; }

.stButton > button {
    width: 100% !important;
    background: rgba(74,158,255,0.08) !important;
    color: #60a5fa !important;
    border: 1px solid rgba(74,158,255,0.22) !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 0.6rem 1rem !important;
}
.stButton > button:hover { background: rgba(74,158,255,0.18) !important; border-color: rgba(74,158,255,0.45) !important; }

[data-testid="column"] { background: transparent !important; }
[data-testid="stVerticalBlock"] { background: transparent !important; }

.stProgress > div > div > div { background: linear-gradient(90deg,#4a9eff,#10d9a0) !important; border-radius: 4px; }
.stProgress > div > div { background: rgba(255,255,255,0.06) !important; border-radius: 4px; height: 6px !important; }

.stTabs [data-baseweb="tab-list"] { background: rgba(15,22,36,0.8) !important; border-radius: 10px; padding: 4px; gap: 4px; border: 1px solid rgba(255,255,255,0.06); }
.stTabs [data-baseweb="tab"] { color: #64748b !important; border-radius: 8px; border: none !important; background: transparent !important; font-size: 13px !important; }
.stTabs [aria-selected="true"] { background: rgba(74,158,255,0.15) !important; color: #60a5fa !important; }
.stTabs [data-baseweb="tab-panel"] { background: transparent !important; padding-top: 1.5rem; }

hr { border: none !important; border-top: 1px solid rgba(255,255,255,0.07) !important; margin: 1.5rem 0 !important; }

div[data-testid="stMarkdownContainer"] p { color: #94a3b8; }
div[data-testid="stMarkdownContainer"] h1,
div[data-testid="stMarkdownContainer"] h2,
div[data-testid="stMarkdownContainer"] h3 { color: #f1f5f9 !important; }
</style>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# DATA — EVENTS
# ════════════════════════════════════════════════════════════════
EVENTS = {
    "inflation_shock": {
        "id": "inflation_shock",
        "name": "Inflation Shock",
        "category": "monetary",
        "severity": "high",
        "headline": "Consumer Prices Surge Past 8%",
        "description": "Inflation accelerates beyond central bank targets. Real yields collapse as bond markets sell off. Hard assets and commodities surge as investors seek inflation protection. Growth equities face a brutal repricing.",
        "effects": {
            "equities":    -0.06,
            "bonds":       -0.14,
            "real_estate": +0.03,
            "commodities": +0.18,
            "cash":         0.00,
            "crypto":      -0.08,
        },
        "resilience_impact": -8,
        "region_stress": {"us": 60, "europe": 72, "asia": 50, "emerging": 85, "gulf": 28},
        "affected_sectors": {
            "Fixed Income": -14, "Technology": -8, "Energy": +15,
            "Commodities": +18, "Real Estate": +3, "Consumer Staples": -5,
        },
    },
    "tech_crash": {
        "id": "tech_crash",
        "name": "Technology Crash",
        "category": "market",
        "severity": "severe",
        "headline": "AI Valuation Bubble Bursts",
        "description": "High-multiple technology stocks enter a violent correction. Growth equities shed a third of their value in weeks. Quality and value hold. A flight to safety begins as credit spreads widen.",
        "effects": {
            "equities":    -0.22,
            "bonds":       +0.04,
            "real_estate": -0.02,
            "commodities": -0.03,
            "cash":         0.00,
            "crypto":      -0.38,
        },
        "resilience_impact": -12,
        "region_stress": {"us": 90, "asia": 72, "europe": 50, "emerging": 42, "gulf": 20},
        "affected_sectors": {
            "Technology": -28, "Communication": -18, "Consumer Discretionary": -10,
            "Fixed Income": +4, "Healthcare": +2, "Utilities": +3,
        },
    },
    "banking_crisis": {
        "id": "banking_crisis",
        "name": "Banking System Stress",
        "category": "financial",
        "severity": "severe",
        "headline": "Systemic Banking Stress Detected",
        "description": "Regional bank failures trigger contagion fears across the financial system. Credit markets seize. Depositors flee to safety. Equities fall sharply as systemic risk spikes and credit availability collapses.",
        "effects": {
            "equities":    -0.18,
            "bonds":       +0.06,
            "real_estate": -0.08,
            "commodities": -0.04,
            "cash":         0.00,
            "crypto":      -0.28,
        },
        "resilience_impact": -15,
        "region_stress": {"europe": 88, "us": 75, "emerging": 70, "asia": 55, "gulf": 30},
        "affected_sectors": {
            "Financials": -25, "Real Estate": -8, "Technology": -12,
            "Fixed Income": +6, "Utilities": +4, "Healthcare": +3,
        },
    },
    "commodity_boom": {
        "id": "commodity_boom",
        "name": "Commodity Supercycle",
        "category": "supply",
        "severity": "medium",
        "headline": "Energy and Metals Hit Decade Highs",
        "description": "Supply constraints and geopolitical tension send energy and metals prices surging. Resource-exporting nations benefit. Import-dependent manufacturers face severe margin compression.",
        "effects": {
            "equities":    +0.03,
            "bonds":       -0.03,
            "real_estate": +0.05,
            "commodities": +0.28,
            "cash":         0.00,
            "crypto":      +0.05,
        },
        "resilience_impact": +2,
        "region_stress": {"gulf": 0, "emerging": 12, "us": 28, "asia": 42, "europe": 48},
        "affected_sectors": {
            "Energy": +30, "Commodities": +28, "Materials": +20,
            "Industrials": -5, "Consumer Discretionary": -8, "Technology": +2,
        },
    },
    "rate_hike_cycle": {
        "id": "rate_hike_cycle",
        "name": "Aggressive Rate Hike Cycle",
        "category": "monetary",
        "severity": "high",
        "headline": "Central Bank Raises Rates 150bps",
        "description": "Central banks move aggressively to contain inflation. Bond yields spike as long-duration assets reprice violently. Cash becomes competitive for the first time in a decade. Leveraged real estate faces severe pressure.",
        "effects": {
            "equities":    -0.10,
            "bonds":       -0.16,
            "real_estate": -0.10,
            "commodities": +0.04,
            "cash":        +0.04,
            "crypto":      -0.15,
        },
        "resilience_impact": -10,
        "region_stress": {"emerging": 82, "europe": 65, "asia": 62, "us": 55, "gulf": 35},
        "affected_sectors": {
            "Fixed Income": -16, "Real Estate": -10, "Utilities": -8,
            "Technology": -10, "Financials": +5, "Cash": +4,
        },
    },
    "ai_boom": {
        "id": "ai_boom",
        "name": "AI Productivity Surge",
        "category": "technology",
        "severity": "medium",
        "headline": "AI Breakthrough Triggers Broad Market Rally",
        "description": "A landmark AI capability breakthrough triggers a productivity boom narrative. Technology stocks lead a broad market rally. Earnings estimates rise across sectors as automation potential is priced in.",
        "effects": {
            "equities":    +0.18,
            "bonds":       -0.02,
            "real_estate": +0.04,
            "commodities": -0.03,
            "cash":         0.00,
            "crypto":      +0.25,
        },
        "resilience_impact": +5,
        "region_stress": {"us": 0, "asia": 10, "europe": 22, "emerging": 30, "gulf": 20},
        "affected_sectors": {
            "Technology": +25, "Communication": +15, "Consumer Discretionary": +10,
            "Industrials": +8, "Fixed Income": -2, "Energy": -3,
        },
    },
    "recession": {
        "id": "recession",
        "name": "Economic Recession",
        "category": "macro",
        "severity": "severe",
        "headline": "GDP Contracts for Second Consecutive Quarter",
        "description": "The economy tips into recession. Consumer spending collapses. Unemployment rises sharply. Earnings downgrades sweep across cyclical sectors. Quality bonds and cash become the only shelter.",
        "effects": {
            "equities":    -0.20,
            "bonds":       +0.08,
            "real_estate": -0.12,
            "commodities": -0.10,
            "cash":         0.00,
            "crypto":      -0.32,
        },
        "resilience_impact": -18,
        "region_stress": {"us": 80, "europe": 75, "emerging": 88, "asia": 65, "gulf": 40},
        "affected_sectors": {
            "Consumer Discretionary": -18, "Real Estate": -12, "Industrials": -15,
            "Financials": -12, "Fixed Income": +8, "Healthcare": +5,
        },
    },
    "currency_crisis": {
        "id": "currency_crisis",
        "name": "Currency Crisis",
        "category": "macro",
        "severity": "high",
        "headline": "Emerging Market Currencies in Freefall",
        "description": "Emerging market currencies collapse against the dollar. Capital flight accelerates as sovereign debt fears mount. USD-denominated assets and hard commodities become the beneficiaries.",
        "effects": {
            "equities":    -0.08,
            "bonds":       -0.06,
            "real_estate":  0.00,
            "commodities": +0.10,
            "cash":        +0.02,
            "crypto":      +0.08,
        },
        "resilience_impact": -6,
        "region_stress": {"emerging": 95, "asia": 62, "europe": 30, "us": 15, "gulf": 25},
        "affected_sectors": {
            "Emerging Markets": -20, "Commodities": +10, "Fixed Income": -6,
            "Technology": -5, "Financials": -8, "Energy": +8,
        },
    },
    "supply_chain_shock": {
        "id": "supply_chain_shock",
        "name": "Supply Chain Disruption",
        "category": "supply",
        "severity": "medium",
        "headline": "Critical Shipping Routes Disrupted",
        "description": "Major global shipping routes are disrupted. Manufacturing bottlenecks cascade worldwide. Input costs surge for goods-dependent businesses while energy and logistics sectors capitalize on the chaos.",
        "effects": {
            "equities":    -0.05,
            "bonds":       -0.02,
            "real_estate": +0.01,
            "commodities": +0.12,
            "cash":         0.00,
            "crypto":      -0.04,
        },
        "resilience_impact": -5,
        "region_stress": {"asia": 78, "europe": 62, "emerging": 55, "us": 45, "gulf": 30},
        "affected_sectors": {
            "Industrials": -10, "Consumer Discretionary": -8, "Technology": -5,
            "Energy": +12, "Commodities": +12, "Fixed Income": -2,
        },
    },
    "geopolitical_shock": {
        "id": "geopolitical_shock",
        "name": "Geopolitical Escalation",
        "category": "political",
        "severity": "high",
        "headline": "Military Conflict Escalates in Key Region",
        "description": "Military conflict escalates in a region critical to global energy supply. Safe haven demand surges globally. Energy prices spike. Risk assets sell off as uncertainty premiums expand across all markets.",
        "effects": {
            "equities":    -0.12,
            "bonds":       +0.05,
            "real_estate": -0.03,
            "commodities": +0.20,
            "cash":        +0.01,
            "crypto":      -0.10,
        },
        "resilience_impact": -10,
        "region_stress": {"emerging": 92, "europe": 82, "gulf": 72, "asia": 50, "us": 30},
        "affected_sectors": {
            "Energy": +20, "Commodities": +20, "Defense": +15,
            "Consumer Discretionary": -12, "Technology": -10, "Fixed Income": +5,
        },
    },
}

# Contextually appropriate decisions per event
EVENT_DECISIONS = {
    "inflation_shock":    ["stabilize", "hedge_inflation", "buy_commodities", "rotate_defensive"],
    "tech_crash":         ["stabilize", "raise_cash", "rotate_defensive", "extend_duration"],
    "banking_crisis":     ["stabilize", "raise_cash", "rotate_defensive", "diversify_global"],
    "commodity_boom":     ["stabilize", "buy_commodities", "hedge_inflation", "increase_risk"],
    "rate_hike_cycle":    ["stabilize", "raise_cash", "rotate_defensive", "buy_commodities"],
    "ai_boom":            ["stabilize", "increase_risk", "diversify_global", "hedge_inflation"],
    "recession":          ["stabilize", "raise_cash", "extend_duration", "rotate_defensive"],
    "currency_crisis":    ["stabilize", "buy_commodities", "diversify_global", "raise_cash"],
    "supply_chain_shock": ["stabilize", "buy_commodities", "rotate_defensive", "raise_cash"],
    "geopolitical_shock": ["stabilize", "buy_commodities", "raise_cash", "rotate_defensive"],
}


# ════════════════════════════════════════════════════════════════
# DATA — DECISIONS
# ════════════════════════════════════════════════════════════════
DECISIONS = {
    "stabilize": {
        "id": "stabilize",
        "name": "Hold Position",
        "icon": "◈",
        "description": "Maintain current allocation. Accept market outcome as positioned. No rebalancing.",
        "allocation_changes": {},
        "effect_modifiers": {},
        "resilience_delta": 0,
        "tag": "Neutral",
        "tag_color": "#64748b",
    },
    "raise_cash": {
        "id": "raise_cash",
        "name": "Raise Cash",
        "icon": "◉",
        "description": "Reduce equity and bond exposure. Build a cash buffer. Prioritize capital preservation.",
        "allocation_changes": {"cash": +0.20, "equities": -0.12, "bonds": -0.08},
        "effect_modifiers": {"equities": 0.80},
        "resilience_delta": +8,
        "tag": "Defensive",
        "tag_color": "#10d9a0",
    },
    "hedge_inflation": {
        "id": "hedge_inflation",
        "name": "Hedge Inflation",
        "icon": "◆",
        "description": "Rotate into commodities and real assets. Reduce long-duration bond exposure significantly.",
        "allocation_changes": {"commodities": +0.15, "bonds": -0.12, "equities": -0.03},
        "effect_modifiers": {"commodities": 1.30, "bonds": 0.70},
        "resilience_delta": +3,
        "tag": "Inflation Hedge",
        "tag_color": "#f59e0b",
    },
    "rotate_defensive": {
        "id": "rotate_defensive",
        "name": "Rotate Defensive",
        "icon": "◍",
        "description": "Shift equities toward defensive sectors: healthcare, utilities, consumer staples. Cushion downside.",
        "allocation_changes": {"bonds": +0.10, "cash": +0.05, "equities": -0.05, "commodities": -0.10},
        "effect_modifiers": {"equities": 0.72, "bonds": 1.10},
        "resilience_delta": +6,
        "tag": "Defensive Rotation",
        "tag_color": "#a78bfa",
    },
    "increase_risk": {
        "id": "increase_risk",
        "name": "Increase Risk Exposure",
        "icon": "◇",
        "description": "Deploy cash into equities. Accept higher volatility in pursuit of outsized upside.",
        "allocation_changes": {"equities": +0.20, "cash": -0.15, "bonds": -0.05},
        "effect_modifiers": {"equities": 1.28},
        "resilience_delta": -8,
        "tag": "Aggressive",
        "tag_color": "#f05e5e",
    },
    "buy_commodities": {
        "id": "buy_commodities",
        "name": "Concentrate in Commodities",
        "icon": "⬡",
        "description": "Significantly increase commodity allocation. Bet on hard assets outperforming in the current regime.",
        "allocation_changes": {"commodities": +0.25, "equities": -0.15, "bonds": -0.10},
        "effect_modifiers": {"commodities": 1.42},
        "resilience_delta": -4,
        "tag": "Concentrated",
        "tag_color": "#f59e0b",
    },
    "diversify_global": {
        "id": "diversify_global",
        "name": "Diversify Globally",
        "icon": "○",
        "description": "Rebalance toward international and emerging markets. Reduce home-country concentration risk.",
        "allocation_changes": {},
        "effect_modifiers": {"equities": 0.88},
        "resilience_delta": +5,
        "tag": "Diversification",
        "tag_color": "#4a9eff",
    },
    "extend_duration": {
        "id": "extend_duration",
        "name": "Extend Duration",
        "icon": "◉",
        "description": "Rotate into long-duration government bonds. High rate sensitivity — powerful in deflationary downturns.",
        "allocation_changes": {"bonds": +0.25, "equities": -0.15, "commodities": -0.10},
        "effect_modifiers": {"bonds": 1.38},
        "resilience_delta": +2,
        "tag": "Duration Play",
        "tag_color": "#38bdf8",
    },
}


# ════════════════════════════════════════════════════════════════
# DATA — SCENARIOS
# ════════════════════════════════════════════════════════════════
SCENARIOS = [
    {
        "id": "balanced",
        "name": "Balanced Investor",
        "subtitle": "Classic 60/40 facing macro headwinds",
        "starting_capital": 100_000,
        "portfolio": {"equities": 0.60, "bonds": 0.30, "real_estate": 0.00, "commodities": 0.00, "cash": 0.10, "crypto": 0.00},
        "starting_event": "inflation_shock",
        "event_pool": ["inflation_shock", "rate_hike_cycle", "recession", "ai_boom", "supply_chain_shock", "geopolitical_shock"],
        "description": "A classic balanced portfolio. Global inflation is rising and rates are about to move. Test your conviction.",
        "risk_level": "Medium",
        "risk_color": "#f59e0b",
    },
    {
        "id": "tech_heavy",
        "name": "Technology Overweight",
        "subtitle": "Concentrated equity position into a market correction",
        "starting_capital": 100_000,
        "portfolio": {"equities": 0.80, "bonds": 0.10, "real_estate": 0.00, "commodities": 0.00, "cash": 0.10, "crypto": 0.00},
        "starting_event": "tech_crash",
        "event_pool": ["tech_crash", "ai_boom", "inflation_shock", "recession", "geopolitical_shock", "rate_hike_cycle"],
        "description": "High conviction in equities. Markets are frothy. A severe correction is already underway in technology.",
        "risk_level": "High",
        "risk_color": "#f05e5e",
    },
    {
        "id": "conservative",
        "name": "Conservative Allocator",
        "subtitle": "Bond-heavy portfolio in an aggressive rate hike cycle",
        "starting_capital": 100_000,
        "portfolio": {"equities": 0.25, "bonds": 0.55, "real_estate": 0.10, "commodities": 0.00, "cash": 0.10, "crypto": 0.00},
        "starting_event": "rate_hike_cycle",
        "event_pool": ["rate_hike_cycle", "inflation_shock", "banking_crisis", "recession", "ai_boom", "currency_crisis"],
        "description": "Safety-first allocation. But rates are rising fast and your bond-heavy portfolio faces severe pressure.",
        "risk_level": "Low–Medium",
        "risk_color": "#10d9a0",
    },
    {
        "id": "real_assets",
        "name": "Real Assets Portfolio",
        "subtitle": "Hard assets at the start of a geopolitical commodity shock",
        "starting_capital": 100_000,
        "portfolio": {"equities": 0.30, "bonds": 0.10, "real_estate": 0.25, "commodities": 0.25, "cash": 0.10, "crypto": 0.00},
        "starting_event": "commodity_boom",
        "event_pool": ["commodity_boom", "geopolitical_shock", "supply_chain_shock", "inflation_shock", "recession", "rate_hike_cycle"],
        "description": "Concentrated in real assets. A commodity supercycle is beginning. Can you ride the wave without getting crushed?",
        "risk_level": "Medium",
        "risk_color": "#f59e0b",
    },
    {
        "id": "crisis",
        "name": "Systemic Crisis",
        "subtitle": "A banking crisis unfolds from a fully invested position",
        "starting_capital": 100_000,
        "portfolio": {"equities": 0.50, "bonds": 0.30, "real_estate": 0.10, "commodities": 0.00, "cash": 0.10, "crypto": 0.00},
        "starting_event": "banking_crisis",
        "event_pool": ["banking_crisis", "recession", "currency_crisis", "rate_hike_cycle", "geopolitical_shock", "supply_chain_shock"],
        "description": "Systemic banking stress is unfolding. Credit is tightening. Fear is spreading. Can you preserve capital?",
        "risk_level": "Very High",
        "risk_color": "#ef4444",
    },
]

ASSET_META = {
    "equities":    {"label": "Equities",    "color": "#4a9eff"},
    "bonds":       {"label": "Bonds",       "color": "#a78bfa"},
    "real_estate": {"label": "Real Estate", "color": "#10d9a0"},
    "commodities": {"label": "Commodities", "color": "#f59e0b"},
    "cash":        {"label": "Cash",        "color": "#64748b"},
    "crypto":      {"label": "Crypto",      "color": "#f97316"},
}

SEVERITY_COLOR = {"medium": "#f59e0b", "high": "#f97316", "severe": "#ef4444"}

MAX_TURNS = 10

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

PLOTLY_DARK = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor":  "rgba(0,0,0,0)",
    "font": {"color": "#94a3b8", "family": "Space Grotesk"},
}


# ════════════════════════════════════════════════════════════════
# SIMULATION ENGINE
# ════════════════════════════════════════════════════════════════
def init_state(scenario: dict) -> dict:
    portfolio = dict(scenario["portfolio"])
    return {
        "scenario_id":        scenario["id"],
        "scenario_name":      scenario["name"],
        "turn":               1,
        "capital":            float(scenario["starting_capital"]),
        "starting_capital":   float(scenario["starting_capital"]),
        "portfolio":          portfolio,
        "resilience":         compute_resilience(portfolio),
        "phase":              "event",
        "current_event_id":   scenario["starting_event"],
        "selected_decision":  None,
        "history":            [],
        "event_pool":         list(scenario["event_pool"]),
        "events_seen":        [],
    }


def compute_resilience(portfolio: dict) -> float:
    weights = list(portfolio.values())

    # Diversification via inverse Herfindahl (0-60 pts)
    hhi = sum(w ** 2 for w in weights)
    diversification = max(0.0, (1.0 - hhi)) * 60.0

    # Liquidity bonus: cash allocation (0-25 pts)
    liquidity = min(portfolio.get("cash", 0.0) * 200.0, 25.0)

    # Concentration penalty: >50% in one asset
    max_w = max(weights) if weights else 0.0
    penalty = max(0.0, (max_w - 0.5)) * 50.0

    score = diversification + liquidity - penalty + 15.0
    return max(0.0, min(100.0, round(score, 1)))


def apply_decision_to_portfolio(portfolio: dict, decision: dict) -> dict:
    new_p = dict(portfolio)
    for asset, delta in decision.get("allocation_changes", {}).items():
        new_p[asset] = max(0.0, new_p.get(asset, 0.0) + delta)

    total = sum(new_p.values())
    if total > 0:
        new_p = {k: v / total for k, v in new_p.items()}
    return new_p


def resolve_turn(state: dict) -> dict:
    event    = EVENTS[state["current_event_id"]]
    dec_id   = state.get("selected_decision") or "stabilize"
    decision = DECISIONS[dec_id]

    pre_portfolio  = dict(state["portfolio"])
    post_portfolio = apply_decision_to_portfolio(pre_portfolio, decision)

    capital       = state["capital"]
    mods          = decision.get("effect_modifiers", {})
    asset_results = {}
    new_capital   = 0.0

    for asset, alloc in post_portfolio.items():
        av           = capital * alloc
        base_ret     = event["effects"].get(asset, 0.0)
        mod          = mods.get(asset, 1.0)
        eff_ret      = base_ret * mod
        nav          = av * (1.0 + eff_ret)
        new_capital += nav
        asset_results[asset] = {
            "pre_value":  round(av,  0),
            "post_value": round(nav, 0),
            "return_pct": round(eff_ret * 100.0, 1),
            "alloc_pct":  round(alloc * 100.0,   1),
        }

    capital_change     = new_capital - capital
    capital_change_pct = (capital_change / capital * 100.0) if capital else 0.0

    base_resilience = compute_resilience(post_portfolio)
    new_resilience  = max(0.0, min(100.0,
        base_resilience
        + event.get("resilience_impact", 0)
        + decision.get("resilience_delta", 0)
    ))

    snapshot = {
        "turn":               state["turn"],
        "event_id":           event["id"],
        "event_name":         event["name"],
        "decision_id":        decision["id"],
        "decision_name":      decision["name"],
        "capital_before":     round(capital,          0),
        "capital_after":      round(new_capital,      0),
        "capital_change":     round(capital_change,   0),
        "capital_change_pct": round(capital_change_pct, 1),
        "resilience_before":  state["resilience"],
        "resilience_after":   round(new_resilience, 1),
        "portfolio_before":   pre_portfolio,
        "portfolio_after":    post_portfolio,
        "asset_results":      asset_results,
    }

    new_state                     = dict(state)
    new_state["capital"]          = round(new_capital, 0)
    new_state["portfolio"]        = post_portfolio
    new_state["resilience"]       = round(new_resilience, 1)
    new_state["history"]          = list(state["history"]) + [snapshot]
    new_state["events_seen"]      = list(state["events_seen"]) + [event["id"]]
    new_state["last_snapshot"]    = snapshot
    new_state["selected_decision"]= None
    new_state["phase"]            = "end" if state["turn"] >= MAX_TURNS else "resolution"

    return new_state


def advance_turn(state: dict) -> dict:
    new_state        = dict(state)
    new_state["turn"] = state["turn"] + 1
    new_state["phase"] = "event"
    new_state["selected_decision"] = None

    pool   = state["event_pool"]
    recent = state["events_seen"][-2:]
    choices = [e for e in pool if e not in recent] or pool
    new_state["current_event_id"] = random.choice(choices)
    return new_state


# ════════════════════════════════════════════════════════════════
# AI EXPLANATION
# ════════════════════════════════════════════════════════════════
def _get_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key.startswith("sk-"):
        return key
    try:
        key = str(st.secrets.get("ANTHROPIC_API_KEY", "")).strip()
        if key.startswith("sk-"):
            return key
    except Exception:
        pass
    return ""


@st.cache_data(ttl=7200, show_spinner=False)
def get_ai_explanation(snapshot_json: str) -> str:
    api_key = _get_api_key()
    if not api_key:
        return "Add ANTHROPIC_API_KEY to your environment or Streamlit secrets to enable AI explanations."

    snap = json.loads(snapshot_json)

    system = (
        "You are ORION's strategic intelligence engine — an institutional-grade financial AI. "
        "Analyze a portfolio simulation turn and explain the outcome in exactly 3 sentences. "
        "Rules: present tense, active voice. Reference specific numbers. Explain the macro relationship. "
        "Note what risks were created or reduced. Institutional tone: precise, insightful, zero fluff. "
        "Say 'the portfolio' not 'your portfolio'. No markdown. No bullet points. Plain text only."
    )

    active = {k: f"{v['alloc_pct']:.0f}% ({v['return_pct']:+.1f}%)" for k, v in snap["asset_results"].items() if v["alloc_pct"] > 0.5}
    user = (
        f"Turn {snap['turn']} — Event: {snap['event_name']} — Decision: {snap['decision_name']}\n\n"
        f"Portfolio: ${snap['capital_before']:,.0f} → ${snap['capital_after']:,.0f} "
        f"({snap['capital_change_pct']:+.1f}%)\n"
        f"Resilience: {snap['resilience_before']:.0f} → {snap['resilience_after']:.0f}\n\n"
        f"Asset returns: {json.dumps(active)}\n\n"
        f"Explain why this outcome occurred and what it means for the portfolio's risk profile."
    )

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-haiku-4-5", "max_tokens": 280, "system": system,
                  "messages": [{"role": "user", "content": user}]},
            timeout=20,
        )
        if resp.status_code == 200:
            return resp.json()["content"][0]["text"].strip()
        return f"AI explanation unavailable (HTTP {resp.status_code})."
    except Exception:
        return "AI explanation temporarily unavailable."


# ════════════════════════════════════════════════════════════════
# CHART BUILDERS
# ════════════════════════════════════════════════════════════════
def build_allocation_donut(portfolio: dict, label: str = "Allocation") -> go.Figure:
    items  = [(k, v) for k, v in portfolio.items() if v > 0.005]
    labels = [ASSET_META[k]["label"] for k, v in items]
    values = [v * 100 for k, v in items]
    colors = [ASSET_META[k]["color"] for k, v in items]

    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.65,
        marker=dict(colors=colors, line=dict(color="rgba(0,0,0,0)", width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color="#94a3b8"),
        hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>",
        sort=False,
        direction="clockwise",
    ))
    fig.update_layout(
        **PLOTLY_DARK, showlegend=False, height=260,
        margin=dict(t=10, b=10, l=10, r=10),
        annotations=[dict(text=label, x=0.5, y=0.5, showarrow=False,
                          font=dict(size=11, color="#64748b"))],
    )
    return fig


def build_history_chart(history: list, starting_capital: float) -> go.Figure:
    if not history:
        return go.Figure()

    turns  = [0] + [h["turn"]          for h in history]
    values = [history[0]["capital_before"]] + [h["capital_after"] for h in history]
    point_colors = []
    for i, v in enumerate(values):
        if i == 0:
            point_colors.append("#64748b")
        elif v >= values[i - 1]:
            point_colors.append("#10d9a0")
        else:
            point_colors.append("#ef4444")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=turns, y=values, fill="tozeroy",
        fillcolor="rgba(74,158,255,0.07)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=turns, y=values, mode="lines+markers",
        line=dict(color="#4a9eff", width=2.5),
        marker=dict(size=7, color=point_colors, line=dict(color="#070a11", width=2)),
        hovertemplate="Turn %{x}<br><b>$%{y:,.0f}</b><extra></extra>",
        showlegend=False,
    ))
    fig.add_hline(y=starting_capital,
                  line=dict(color="rgba(255,255,255,0.10)", width=1, dash="dot"))

    fig.update_layout(
        **PLOTLY_DARK, height=200,
        margin=dict(t=10, b=30, l=70, r=10),
        xaxis=dict(showgrid=False, tickcolor="#374151",
                   linecolor="rgba(255,255,255,0.06)",
                   title=dict(text="Turn", font=dict(size=11)),
                   tickmode="array", tickvals=turns),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)",
                   tickformat="$,.0f", linecolor="rgba(255,255,255,0.06)"),
    )
    return fig


def build_sector_bar(event: dict) -> go.Figure:
    sectors = event.get("affected_sectors", {})
    if not sectors:
        return go.Figure()

    sorted_s = sorted(sectors.items(), key=lambda x: x[1])
    labels   = [s[0] for s in sorted_s]
    values   = [s[1] for s in sorted_s]
    colors   = ["#ef4444" if v < 0 else "#10d9a0" for v in values]

    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker=dict(color=colors, opacity=0.85, line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>%{x:+.0f}%<extra></extra>",
    ))
    fig.add_vline(x=0, line=dict(color="rgba(255,255,255,0.12)", width=1))
    fig.update_layout(
        **PLOTLY_DARK, height=max(180, len(labels) * 34),
        margin=dict(t=10, b=20, l=140, r=40),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)",
                   ticksuffix="%", zeroline=False),
        yaxis=dict(showgrid=False, linecolor="rgba(255,255,255,0.06)"),
        bargap=0.32,
    )
    return fig


def build_world_map(event: dict) -> go.Figure:
    region_countries = {
        "us":       ["USA", "CAN"],
        "europe":   ["GBR", "DEU", "FRA", "ITA", "ESP", "NLD", "BEL",
                     "SWE", "NOR", "DNK", "FIN", "CHE", "AUT", "POL", "PRT", "GRC"],
        "asia":     ["CHN", "JPN", "KOR", "TWN", "IND", "THA", "IDN",
                     "MYS", "SGP", "PHL", "VNM", "BGD"],
        "emerging": ["BRA", "MEX", "ARG", "CHL", "COL", "ZAF", "TUR",
                     "EGY", "NGA", "PAK", "UKR", "RUS"],
        "gulf":     ["SAU", "ARE", "QAT", "KWT", "BHR", "OMN", "IRQ", "IRN"],
    }
    region_stress = event.get("region_stress", {})
    countries, stress_vals = [], []

    for region, stress in region_stress.items():
        for c in region_countries.get(region, []):
            countries.append(c)
            stress_vals.append(stress)

    shown = set(countries)
    for clist in region_countries.values():
        for c in clist:
            if c not in shown:
                countries.append(c)
                stress_vals.append(8)

    fig = go.Figure(go.Choropleth(
        locations=countries, z=stress_vals,
        colorscale=[
            [0.0, "rgba(16,217,160,0.12)"],
            [0.3, "rgba(74,158,255,0.35)"],
            [0.6, "rgba(245,158,11,0.65)"],
            [1.0, "rgba(239,68,68,0.92)"],
        ],
        showscale=False,
        marker=dict(line=dict(color="rgba(255,255,255,0.07)", width=0.5)),
        hovertemplate="%{location}<br>Stress index: %{z}/100<extra></extra>",
        zmin=0, zmax=100,
    ))
    fig.update_geos(
        showframe=False, showcoastlines=False,
        projection_type="equirectangular",
        bgcolor="rgba(0,0,0,0)",
        landcolor="rgba(25,35,55,0.7)",
        oceancolor="rgba(7,10,17,0.9)",
        showocean=True, showland=True,
        lakecolor="rgba(7,10,17,0.9)",
    )
    fig.update_layout(
        **PLOTLY_DARK, height=260,
        margin=dict(t=0, b=0, l=0, r=0),
        geo=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig


# ════════════════════════════════════════════════════════════════
# UI HELPERS
# ════════════════════════════════════════════════════════════════
def orion_wordmark():
    st.markdown(
        '<div style="font-family:\'DM Mono\',monospace;font-size:11px;'
        'letter-spacing:0.18em;color:#374151;text-transform:uppercase;'
        'margin-bottom:0.25rem;">◎ ORION</div>',
        unsafe_allow_html=True,
    )


def section_label(text: str):
    st.markdown(
        f'<div style="font-size:11px;letter-spacing:0.12em;color:#374151;'
        f'text-transform:uppercase;font-family:\'DM Mono\',monospace;'
        f'margin-bottom:0.75rem;">{text}</div>',
        unsafe_allow_html=True,
    )


def render_event_card(event: dict):
    sev   = event.get("severity", "medium")
    color = SEVERITY_COLOR.get(sev, "#f59e0b")
    st.markdown(f"""
<div style="
    background: linear-gradient(135deg,rgba(15,22,36,0.98) 0%,rgba(18,26,45,0.98) 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-left: 3px solid {color};
    border-radius: 14px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.25rem;
">
    <div style="font-size:11px;font-family:'DM Mono',monospace;letter-spacing:0.12em;
                color:{color};text-transform:uppercase;margin-bottom:0.75rem;">
        {event['category'].upper()} · {sev.upper()}
    </div>
    <div style="font-size:21px;font-weight:600;color:#f1f5f9;margin-bottom:0.6rem;line-height:1.25;">
        {event['headline']}
    </div>
    <div style="font-size:14px;color:#94a3b8;line-height:1.7;">
        {event['description']}
    </div>
</div>""", unsafe_allow_html=True)


def render_decision_card(decision: dict, selected: bool):
    border = "rgba(74,158,255,0.65)" if selected else "rgba(255,255,255,0.07)"
    bg     = "rgba(74,158,255,0.09)" if selected else "rgba(15,22,36,0.95)"
    glow   = "box-shadow: 0 0 24px rgba(74,158,255,0.14);" if selected else ""
    tc     = decision.get("tag_color", "#64748b")
    st.markdown(f"""
<div style="
    background:{bg};
    border:1px solid {border};
    border-radius:12px;
    padding:1.2rem 1.1rem 1rem;
    min-height:155px;
    {glow}
    display:flex;flex-direction:column;justify-content:space-between;
">
    <div>
        <div style="font-size:18px;color:#4a9eff;margin-bottom:7px;">{decision['icon']}</div>
        <div style="font-size:14px;font-weight:600;color:#f1f5f9;margin-bottom:5px;">{decision['name']}</div>
        <div style="font-size:12px;color:#64748b;line-height:1.55;">{decision['description']}</div>
    </div>
    <div style="margin-top:10px;">
        <span style="font-size:10px;font-family:'DM Mono',monospace;letter-spacing:0.07em;
                     color:{tc};background:rgba(255,255,255,0.04);
                     border:1px solid rgba(255,255,255,0.08);
                     border-radius:20px;padding:2px 10px;text-transform:uppercase;">{decision['tag']}</span>
    </div>
</div>""", unsafe_allow_html=True)


def render_ai_card(text: str):
    st.markdown(f"""
<div style="
    background: rgba(74,158,255,0.05);
    border: 1px solid rgba(74,158,255,0.18);
    border-radius: 14px;
    padding: 1.5rem 1.75rem;
    margin: 1rem 0;
">
    <div style="font-size:10px;font-family:'DM Mono',monospace;letter-spacing:0.14em;
                color:#4a9eff;text-transform:uppercase;margin-bottom:0.75rem;">◎ ORION Intelligence</div>
    <div style="font-size:14px;color:#cbd5e1;line-height:1.75;">{text}</div>
</div>""", unsafe_allow_html=True)


def render_turn_progress(turn: int, max_turns: int = MAX_TURNS):
    st.progress(turn / max_turns)
    st.markdown(
        f'<div style="font-size:11px;color:#374151;font-family:\'DM Mono\',monospace;'
        f'letter-spacing:0.1em;margin-top:-0.4rem;">CYCLE {turn} / {max_turns}</div>',
        unsafe_allow_html=True,
    )


def month_label(turn: int) -> str:
    return f"{MONTHS[(turn - 1) % 12]} 2025"


def fmt_currency(v: float) -> str:
    return f"${v:,.0f}"


def fmt_pct(v: float, sign: bool = True) -> str:
    return f"{v:+.1f}%" if sign else f"{v:.1f}%"


# ════════════════════════════════════════════════════════════════
# SCREENS
# ════════════════════════════════════════════════════════════════
def screen_intro():
    orion_wordmark()
    st.markdown(
        '<div style="font-size:32px;font-weight:300;color:#f1f5f9;line-height:1.2;margin-bottom:0.4rem;">'
        'Macroeconomic Strategy Simulator'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-size:14px;color:#64748b;line-height:1.7;max-width:560px;margin-bottom:2.5rem;">'
        'Navigate 10 cycles of economic turbulence. Make strategic portfolio decisions. '
        'Learn how global forces shape wealth. Survive what the world throws at you.'
        '</div>',
        unsafe_allow_html=True,
    )

    section_label("Choose your starting scenario")

    cols = st.columns(3)
    for i, scenario in enumerate(SCENARIOS):
        with cols[i % 3]:
            rc = scenario["risk_color"]
            st.markdown(f"""
<div style="
    background: rgba(15,22,36,0.95);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.4rem 1.3rem 1rem;
    margin-bottom: 1rem;
    min-height: 195px;
">
    <div style="font-size:11px;font-family:'DM Mono',monospace;letter-spacing:0.1em;
                color:{rc};text-transform:uppercase;margin-bottom:0.5rem;">
        Risk: {scenario['risk_level']}
    </div>
    <div style="font-size:16px;font-weight:600;color:#f1f5f9;margin-bottom:4px;">{scenario['name']}</div>
    <div style="font-size:12px;color:#64748b;margin-bottom:0.75rem;font-style:italic;">{scenario['subtitle']}</div>
    <div style="font-size:12px;color:#94a3b8;line-height:1.6;">{scenario['description']}</div>
</div>""", unsafe_allow_html=True)

            if st.button(f"Begin →", key=f"start_{scenario['id']}"):
                st.session_state.sim = init_state(scenario)
                st.rerun()

    st.markdown("---")
    st.markdown(
        '<div style="font-size:12px;color:#374151;line-height:1.8;">'
        'Each simulation runs 10 economic cycles · No real money involved · '
        'AI explanations powered by Claude · Educational use only'
        '</div>',
        unsafe_allow_html=True,
    )


def screen_event():
    sim   = st.session_state.sim
    event = EVENTS[sim["current_event_id"]]

    # Header
    orion_wordmark()
    render_turn_progress(sim["turn"])
    st.markdown(
        f'<div style="font-size:13px;color:#64748b;font-family:\'DM Mono\',monospace;'
        f'letter-spacing:0.08em;margin-bottom:1.5rem;">{month_label(sim["turn"])}'
        f' — {sim["scenario_name"]}</div>',
        unsafe_allow_html=True,
    )

    # Key metrics
    cap     = sim["capital"]
    start   = sim["starting_capital"]
    ret_pct = (cap - start) / start * 100
    res     = sim["resilience"]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Portfolio Value",  fmt_currency(cap))
    with c2:
        delta_color = "normal" if ret_pct >= 0 else "inverse"
        st.metric("Total Return", fmt_pct(ret_pct), delta=fmt_pct(ret_pct), delta_color=delta_color)
    with c3:
        st.metric("Resilience Score", f"{res:.0f} / 100")
    with c4:
        st.metric("Cycle", f"{sim['turn']} of {MAX_TURNS}")

    st.markdown("---")

    # Event
    section_label("Incoming economic event")
    render_event_card(event)

    # Portfolio + history
    col_l, col_r = st.columns([1, 1.6])
    with col_l:
        section_label("Current allocation")
        st.plotly_chart(
            build_allocation_donut(sim["portfolio"]),
            use_container_width=True, config={"displayModeBar": False},
        )
    with col_r:
        section_label("Portfolio history")
        if sim["history"]:
            st.plotly_chart(
                build_history_chart(sim["history"], sim["starting_capital"]),
                use_container_width=True, config={"displayModeBar": False},
            )
        else:
            st.markdown(
                '<div style="color:#374151;font-size:13px;padding-top:3rem;text-align:center;">'
                'History will appear after turn 1</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")
    _, cta, _ = st.columns([2, 1, 2])
    with cta:
        if st.button("Respond to this event →"):
            st.session_state.sim["phase"] = "decision"
            st.rerun()


def screen_decision():
    sim   = st.session_state.sim
    event = EVENTS[sim["current_event_id"]]

    orion_wordmark()

    sev   = event.get("severity", "medium")
    color = SEVERITY_COLOR.get(sev, "#f59e0b")
    st.markdown(f"""
<div style="
    background:rgba(15,22,36,0.8);border:1px solid rgba(255,255,255,0.07);
    border-left:3px solid {color};border-radius:10px;
    padding:0.85rem 1.25rem;margin-bottom:1.5rem;
    display:flex;align-items:center;gap:1rem;
">
    <div style="font-size:11px;font-family:'DM Mono',monospace;letter-spacing:0.1em;
                color:{color};text-transform:uppercase;">{event['name']}</div>
    <div style="font-size:14px;color:#94a3b8;"> — {event['headline']}</div>
</div>""", unsafe_allow_html=True)

    st.markdown(
        '<div style="font-size:22px;font-weight:500;color:#f1f5f9;margin-bottom:0.35rem;">'
        'Choose your strategic response'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-size:13px;color:#64748b;margin-bottom:1.75rem;">'
        'Your decision reshapes the portfolio before market effects are applied.'
        '</div>',
        unsafe_allow_html=True,
    )

    dec_ids = EVENT_DECISIONS.get(sim["current_event_id"], list(DECISIONS.keys())[:4])
    selected = sim.get("selected_decision")

    cols = st.columns(len(dec_ids))
    for i, dec_id in enumerate(dec_ids):
        dec = DECISIONS[dec_id]
        with cols[i]:
            render_decision_card(dec, selected == dec_id)
            label = "✓ Selected" if selected == dec_id else "Select"
            if st.button(label, key=f"pick_{dec_id}"):
                st.session_state.sim["selected_decision"] = dec_id
                st.rerun()

    st.markdown("---")

    if selected:
        chosen = DECISIONS[selected]
        st.markdown(f"""
<div style="
    background:rgba(74,158,255,0.06);border:1px solid rgba(74,158,255,0.15);
    border-radius:10px;padding:0.9rem 1.25rem;margin-bottom:1.25rem;
    display:flex;align-items:center;gap:1rem;
">
    <div style="font-size:11px;font-family:'DM Mono',monospace;letter-spacing:0.1em;color:#4a9eff;">
        SELECTED RESPONSE
    </div>
    <div style="font-size:14px;font-weight:600;color:#f1f5f9;">{chosen['name']}</div>
    <div style="font-size:13px;color:#94a3b8;">— {chosen['description']}</div>
</div>""", unsafe_allow_html=True)

    col_back, col_go = st.columns([1, 1])
    with col_back:
        if st.button("← Back"):
            st.session_state.sim["phase"] = "event"
            st.rerun()
    with col_go:
        confirm_label = "Simulate outcome →" if selected else "Simulate without changes →"
        if st.button(confirm_label):
            st.session_state.sim = resolve_turn(st.session_state.sim)
            st.rerun()


def screen_resolution():
    sim  = st.session_state.sim
    snap = sim["last_snapshot"]

    event    = EVENTS[snap["event_id"]]
    decision = DECISIONS[snap["decision_id"]]

    orion_wordmark()
    change_pct = snap["capital_change_pct"]
    change_color = "#10d9a0" if change_pct >= 0 else "#ef4444"
    direction    = "▲" if change_pct >= 0 else "▼"

    st.markdown(
        f'<div style="font-size:22px;font-weight:500;color:#f1f5f9;margin-bottom:0.3rem;">'
        f'Cycle {snap["turn"]} resolved'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="font-size:14px;color:#64748b;margin-bottom:1.5rem;">'
        f'{event["name"]} · {decision["name"]}'
        f'</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Portfolio Value", fmt_currency(snap["capital_after"]))
    with c2:
        res_delta = snap["resilience_after"] - snap["resilience_before"]
        st.metric("Resilience", f"{snap['resilience_after']:.0f}",
                  delta=f"{res_delta:+.0f}", delta_color="normal" if res_delta >= 0 else "inverse")
    with c3:
        st.metric("This Cycle", fmt_pct(change_pct),
                  delta=fmt_currency(snap["capital_change"]),
                  delta_color="normal" if change_pct >= 0 else "inverse")
    with c4:
        total_ret = (snap["capital_after"] - sim["starting_capital"]) / sim["starting_capital"] * 100
        st.metric("Total Return", fmt_pct(total_ret), delta_color="normal" if total_ret >= 0 else "inverse")

    st.markdown("---")

    # AI explanation
    section_label("◎ Strategic Analysis")
    with st.spinner("Analyzing outcome..."):
        explanation = get_ai_explanation(json.dumps(snap, default=str))
    render_ai_card(explanation)

    # World map + sector bar
    tab1, tab2 = st.tabs(["  Global Impact  ", "  Sector Performance  "])
    with tab1:
        section_label("Regional economic stress")
        st.plotly_chart(build_world_map(event), use_container_width=True, config={"displayModeBar": False})
    with tab2:
        section_label("Sector impact this cycle")
        st.plotly_chart(build_sector_bar(event), use_container_width=True, config={"displayModeBar": False})

    st.markdown("---")

    # Asset breakdown
    section_label("Asset class breakdown")
    col_l, col_r = st.columns(2)
    with col_l:
        section_label("Before decision")
        st.plotly_chart(
            build_allocation_donut(snap["portfolio_before"], "Before"),
            use_container_width=True, config={"displayModeBar": False},
        )
    with col_r:
        section_label("After decision + market")
        st.plotly_chart(
            build_allocation_donut(snap["portfolio_after"], "After"),
            use_container_width=True, config={"displayModeBar": False},
        )

    rows = []
    for asset, r in snap["asset_results"].items():
        if r["alloc_pct"] > 0.1:
            rows.append({
                "Asset":       ASSET_META[asset]["label"],
                "Allocation":  f"{r['alloc_pct']:.1f}%",
                "Return":      f"{r['return_pct']:+.1f}%",
                "Value Before": fmt_currency(r["pre_value"]),
                "Value After":  fmt_currency(r["post_value"]),
                "P&L":         fmt_currency(r["post_value"] - r["pre_value"]),
            })

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(
            df, use_container_width=True, hide_index=True,
            column_config={
                "Asset":        st.column_config.TextColumn(width="small"),
                "Return":       st.column_config.TextColumn(width="small"),
                "Allocation":   st.column_config.TextColumn(width="small"),
                "Value Before": st.column_config.TextColumn(width="medium"),
                "Value After":  st.column_config.TextColumn(width="medium"),
                "P&L":          st.column_config.TextColumn(width="small"),
            },
        )

    st.markdown("---")

    if sim["phase"] == "end":
        if st.button("View Final Results →"):
            st.session_state.sim["last_snapshot"] = None
            st.rerun()
    else:
        _, btn_col, _ = st.columns([1.5, 1, 1.5])
        with btn_col:
            next_turn_n = sim["turn"] + 1
            if st.button(f"Continue to Cycle {next_turn_n} →"):
                st.session_state.sim = advance_turn(st.session_state.sim)
                st.rerun()


def screen_end():
    sim     = st.session_state.sim
    history = sim["history"]

    final_cap = sim["capital"]
    start_cap = sim["starting_capital"]
    total_ret = (final_cap - start_cap) / start_cap * 100
    resilience = sim["resilience"]

    # Grade
    score = total_ret * 0.6 + resilience * 0.4
    if score >= 40:
        grade, grade_color = "S", "#10d9a0"
    elif score >= 20:
        grade, grade_color = "A", "#4a9eff"
    elif score >= 5:
        grade, grade_color = "B", "#a78bfa"
    elif score >= -5:
        grade, grade_color = "C", "#f59e0b"
    elif score >= -15:
        grade, grade_color = "D", "#f97316"
    else:
        grade, grade_color = "F", "#ef4444"

    orion_wordmark()
    st.markdown(
        '<div style="font-size:30px;font-weight:300;color:#f1f5f9;margin-bottom:0.35rem;">'
        'Simulation Complete'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="font-size:14px;color:#64748b;margin-bottom:2rem;">'
        f'{sim["scenario_name"]} · {MAX_TURNS} economic cycles'
        f'</div>',
        unsafe_allow_html=True,
    )

    col_val, col_ret, col_res, col_grade = st.columns(4)
    with col_val:
        st.metric("Final Value",  fmt_currency(final_cap))
    with col_ret:
        st.metric("Total Return", fmt_pct(total_ret),
                  delta_color="normal" if total_ret >= 0 else "inverse")
    with col_res:
        st.metric("Final Resilience", f"{resilience:.0f} / 100")
    with col_grade:
        st.markdown(f"""
<div style="background:#0f1624;border:1px solid rgba(255,255,255,0.07);
            border-radius:12px;padding:1.2rem;text-align:center;">
    <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.08em;
                color:#64748b;margin-bottom:8px;">Performance Grade</div>
    <div style="font-size:42px;font-weight:700;color:{grade_color};
                font-family:'DM Mono',monospace;line-height:1;">{grade}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Portfolio history chart
    section_label("Portfolio value over 10 cycles")
    st.plotly_chart(
        build_history_chart(history, start_cap),
        use_container_width=True, config={"displayModeBar": False},
    )

    # Turn-by-turn table
    section_label("Cycle-by-cycle history")
    table_rows = []
    for h in history:
        pnl_color = "▲" if h["capital_change_pct"] >= 0 else "▼"
        table_rows.append({
            "Cycle":      h["turn"],
            "Event":      h["event_name"],
            "Decision":   h["decision_name"],
            "Return":     f"{pnl_color} {h['capital_change_pct']:+.1f}%",
            "Value After": fmt_currency(h["capital_after"]),
            "Resilience": f"{h['resilience_after']:.0f}",
        })

    df = pd.DataFrame(table_rows)
    st.dataframe(df, use_container_width=True, hide_index=True,
                 column_config={
                     "Cycle":       st.column_config.NumberColumn(width="small"),
                     "Event":       st.column_config.TextColumn(width="medium"),
                     "Decision":    st.column_config.TextColumn(width="medium"),
                     "Return":      st.column_config.TextColumn(width="small"),
                     "Value After": st.column_config.TextColumn(width="medium"),
                     "Resilience":  st.column_config.TextColumn(width="small"),
                 })

    st.markdown("---")
    _, btn_col, _ = st.columns([2, 1, 2])
    with btn_col:
        if st.button("Play Again →"):
            del st.session_state.sim
            st.rerun()


# ════════════════════════════════════════════════════════════════
# ROUTING
# ════════════════════════════════════════════════════════════════
def main():
    if "sim" not in st.session_state:
        screen_intro()
        return

    sim   = st.session_state.sim
    phase = sim.get("phase", "event")

    if phase == "event":
        screen_event()
    elif phase == "decision":
        screen_decision()
    elif phase == "resolution":
        screen_resolution()
    elif phase == "end":
        if sim.get("last_snapshot"):
            screen_resolution()
        else:
            screen_end()
    else:
        screen_intro()

main()
