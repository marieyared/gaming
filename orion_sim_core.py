"""
orion_sim_core.py — Shared simulation data and engine.
Imported by both orion_sim.py (standalone dark-theme app) and app.py (embedded tab).
No Streamlit UI code here — pure data and logic only.
"""

import random

MAX_TURNS = 10

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# ── Events ────────────────────────────────────────────────────────────────────
EVENTS = {
    "inflation_shock": {
        "id": "inflation_shock",
        "name": "Inflation Shock",
        "category": "monetary",
        "severity": "high",
        "headline": "Consumer Prices Surge Past 8%",
        "description": (
            "Inflation accelerates beyond central bank targets. Real yields collapse as bond markets sell off. "
            "Hard assets and commodities surge as investors seek inflation protection. "
            "Growth equities face a brutal repricing."
        ),
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
        "historical_analogue": (
            "Mirrors 2021–2022, when US CPI peaked at 9.1%. The Bloomberg Global Agg bond index lost 16% "
            "while energy commodities gained over 60% — the sharpest bond–commodity divergence in 40 years."
        ),
    },
    "tech_crash": {
        "id": "tech_crash",
        "name": "Technology Crash",
        "category": "market",
        "severity": "severe",
        "headline": "AI Valuation Bubble Bursts",
        "description": (
            "High-multiple technology stocks enter a violent correction. Growth equities shed a third of their "
            "value in weeks. Quality and value hold. A flight to safety begins as credit spreads widen."
        ),
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
        "historical_analogue": (
            "Echoes 2022, when the Nasdaq fell 33% and high-multiple growth stocks lost 50–70%. "
            "Value stocks outperformed growth by over 30 percentage points — the largest spread since the 2000 dot-com bust."
        ),
    },
    "banking_crisis": {
        "id": "banking_crisis",
        "name": "Banking System Stress",
        "category": "financial",
        "severity": "severe",
        "headline": "Systemic Banking Stress Detected",
        "description": (
            "Regional bank failures trigger contagion fears across the financial system. Credit markets seize. "
            "Depositors flee to safety. Equities fall sharply as systemic risk spikes and credit availability collapses."
        ),
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
        "historical_analogue": (
            "Echoes the 2023 SVB/Signature collapse and the 2008 GFC. In 2023, the KBW Bank Index fell 25% in weeks; "
            "in 2008, US financials lost over 50% as interbank lending froze completely."
        ),
    },
    "commodity_boom": {
        "id": "commodity_boom",
        "name": "Commodity Supercycle",
        "category": "supply",
        "severity": "medium",
        "headline": "Energy and Metals Hit Decade Highs",
        "description": (
            "Supply constraints and geopolitical tension send energy and metals prices surging. "
            "Resource-exporting nations benefit. Import-dependent manufacturers face severe margin compression."
        ),
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
        "historical_analogue": (
            "Mirrors 2021–2022, when oil surged from $70 to $120/bbl and the Bloomberg Commodity Index gained 38% "
            "in 12 months. Energy stocks doubled while consumer goods companies saw margin compression."
        ),
    },
    "rate_hike_cycle": {
        "id": "rate_hike_cycle",
        "name": "Aggressive Rate Hike Cycle",
        "category": "monetary",
        "severity": "high",
        "headline": "Central Bank Raises Rates 150bps",
        "description": (
            "Central banks move aggressively to contain inflation. Bond yields spike as long-duration assets "
            "reprice violently. Cash becomes competitive for the first time in a decade. "
            "Leveraged real estate faces severe pressure."
        ),
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
        "historical_analogue": (
            "Parallels the 2022–2023 Fed cycle: 525bps of hikes over 18 months. The Bloomberg US Agg bond index "
            "fell 13% — its worst calendar year since 1926. Long-duration bonds lost nearly 30%."
        ),
    },
    "ai_boom": {
        "id": "ai_boom",
        "name": "AI Productivity Surge",
        "category": "technology",
        "severity": "medium",
        "headline": "AI Breakthrough Triggers Broad Market Rally",
        "description": (
            "A landmark AI capability breakthrough triggers a productivity boom narrative. Technology stocks lead "
            "a broad market rally. Earnings estimates rise across sectors as automation potential is priced in."
        ),
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
        "historical_analogue": (
            "Mirrors the 2023–2024 AI-driven rally: Nvidia gained 240%, the S&P 500 rose 24%, and the Nasdaq "
            "surged 43% in a single calendar year — the most concentrated performance in market history."
        ),
    },
    "recession": {
        "id": "recession",
        "name": "Economic Recession",
        "category": "macro",
        "severity": "severe",
        "headline": "GDP Contracts for Second Consecutive Quarter",
        "description": (
            "The economy tips into recession. Consumer spending collapses. Unemployment rises sharply. "
            "Earnings downgrades sweep across cyclical sectors. Quality bonds and cash become the only shelter."
        ),
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
        "historical_analogue": (
            "Echoes the 2008 GFC, when the S&P 500 fell 57% over 18 months, and the 2020 COVID shock, "
            "which delivered a 34% drawdown in just 33 days. Government bonds gained 8–12% in both episodes."
        ),
    },
    "currency_crisis": {
        "id": "currency_crisis",
        "name": "Currency Crisis",
        "category": "macro",
        "severity": "high",
        "headline": "Emerging Market Currencies in Freefall",
        "description": (
            "Emerging market currencies collapse against the dollar. Capital flight accelerates as sovereign debt "
            "fears mount. USD-denominated assets and hard commodities become the beneficiaries."
        ),
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
        "historical_analogue": (
            "Similar to 2018, when the Turkish lira lost 45% and the Argentine peso collapsed 50% in a single year. "
            "The 1997 Asian crisis saw currencies across the region fall 30–80%, triggering sovereign defaults."
        ),
    },
    "supply_chain_shock": {
        "id": "supply_chain_shock",
        "name": "Supply Chain Disruption",
        "category": "supply",
        "severity": "medium",
        "headline": "Critical Shipping Routes Disrupted",
        "description": (
            "Major global shipping routes are disrupted. Manufacturing bottlenecks cascade worldwide. "
            "Input costs surge for goods-dependent businesses while energy and logistics sectors capitalize."
        ),
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
        "historical_analogue": (
            "Mirrors the 2021–2022 post-COVID supply crunch and the 2024 Red Sea shipping crisis. "
            "Global container costs rose 4× in 2021; the Red Sea campaign added $1B/day in rerouting costs."
        ),
    },
    "geopolitical_shock": {
        "id": "geopolitical_shock",
        "name": "Geopolitical Escalation",
        "category": "political",
        "severity": "high",
        "headline": "Military Conflict Escalates in Key Region",
        "description": (
            "Military conflict escalates in a region critical to global energy supply. Safe haven demand surges "
            "globally. Energy prices spike. Risk assets sell off as uncertainty premiums expand across all markets."
        ),
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
        "historical_analogue": (
            "Echoes the February 2022 Russia-Ukraine escalation: Brent crude jumped 30% within weeks, "
            "European equity indices fell 15%, and defense stocks surged 20%+."
        ),
    },
}

# ── Event → available decisions ───────────────────────────────────────────────
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

# ── Decisions ─────────────────────────────────────────────────────────────────
# tag_color values work on both light (#f8f7f4) and dark (#070a11) backgrounds.
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
        "tag_color": "#94a3b8",
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
        "tag_color": "#1D9E75",
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
        "tag_color": "#F59E0B",
    },
    "rotate_defensive": {
        "id": "rotate_defensive",
        "name": "Rotate Defensive",
        "icon": "◍",
        "description": "Shift equities toward defensive sectors: healthcare, utilities, consumer staples. Cushion downside with more bonds.",
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
        "tag_color": "#dc2626",
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
        "tag_color": "#F59E0B",
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
        "tag_color": "#378ADD",
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

# ── Starting scenarios ────────────────────────────────────────────────────────
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
        "risk_color": "#F59E0B",
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
        "risk_color": "#dc2626",
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
        "risk_color": "#1D9E75",
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
        "risk_color": "#F59E0B",
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
        "risk_color": "#dc2626",
    },
]

# ── Engine ────────────────────────────────────────────────────────────────────

def compute_resilience(portfolio: dict) -> float:
    weights = list(portfolio.values())
    hhi          = sum(w ** 2 for w in weights)
    diversif     = max(0.0, (1.0 - hhi)) * 60.0
    liquidity    = min(portfolio.get("cash", 0.0) * 200.0, 25.0)
    max_w        = max(weights) if weights else 0.0
    penalty      = max(0.0, (max_w - 0.5)) * 50.0
    return max(0.0, min(100.0, round(diversif + liquidity - penalty + 15.0, 1)))


def apply_decision(portfolio: dict, decision: dict) -> dict:
    new_p = dict(portfolio)
    for asset, delta in decision.get("allocation_changes", {}).items():
        new_p[asset] = max(0.0, new_p.get(asset, 0.0) + delta)
    total = sum(new_p.values())
    if total > 0:
        new_p = {k: v / total for k, v in new_p.items()}
    return new_p


def init_state(scenario: dict) -> dict:
    portfolio = dict(scenario["portfolio"])
    total = sum(portfolio.values())
    if total > 0:
        portfolio = {k: v / total for k, v in portfolio.items()}
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
        "last_snapshot":      None,
        "use_real_portfolio": scenario.get("use_real_portfolio", False),
    }


def resolve_turn(state: dict) -> dict:
    event    = EVENTS[state["current_event_id"]]
    dec_id   = state.get("selected_decision") or "stabilize"
    decision = DECISIONS[dec_id]
    pre_p    = dict(state["portfolio"])
    post_p   = apply_decision(pre_p, decision)
    capital  = state["capital"]
    mods     = decision.get("effect_modifiers", {})
    asset_results = {}
    new_capital   = 0.0
    for asset, alloc in post_p.items():
        av      = capital * alloc
        eff_ret = event["effects"].get(asset, 0.0) * mods.get(asset, 1.0)
        nav     = av * (1.0 + eff_ret)
        new_capital += nav
        asset_results[asset] = {
            "pre_value":  round(av,  0),
            "post_value": round(nav, 0),
            "return_pct": round(eff_ret * 100.0, 1),
            "alloc_pct":  round(alloc * 100.0,   1),
        }
    cap_change     = new_capital - capital
    cap_change_pct = (cap_change / capital * 100.0) if capital else 0.0
    new_res = max(0.0, min(100.0,
        compute_resilience(post_p)
        + event.get("resilience_impact", 0)
        + decision.get("resilience_delta", 0)
    ))
    snapshot = {
        "turn":               state["turn"],
        "event_id":           event["id"],
        "event_name":         event["name"],
        "decision_id":        decision["id"],
        "decision_name":      decision["name"],
        "capital_before":     round(capital,        0),
        "capital_after":      round(new_capital,    0),
        "capital_change":     round(cap_change,     0),
        "capital_change_pct": round(cap_change_pct, 1),
        "resilience_before":  state["resilience"],
        "resilience_after":   round(new_res, 1),
        "portfolio_before":   pre_p,
        "portfolio_after":    post_p,
        "asset_results":      asset_results,
    }
    new_state = dict(state)
    new_state.update({
        "capital":           round(new_capital, 0),
        "portfolio":         post_p,
        "resilience":        round(new_res, 1),
        "history":           list(state["history"]) + [snapshot],
        "events_seen":       list(state["events_seen"]) + [event["id"]],
        "last_snapshot":     snapshot,
        "selected_decision": None,
        "phase":             "end" if state["turn"] >= MAX_TURNS else "resolution",
    })
    return new_state


def advance_turn(state: dict) -> dict:
    pool    = state["event_pool"]
    recent  = state["events_seen"][-2:]
    choices = [e for e in pool if e not in recent] or pool
    new_state = dict(state)
    new_state.update({
        "turn":              state["turn"] + 1,
        "phase":             "event",
        "selected_decision": None,
        "current_event_id":  random.choice(choices),
    })
    return new_state
