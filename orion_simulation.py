"""
orion_simulation.py
───────────────────
Core simulation engine for ORION macro-financial strategy simulation.
"""

import random
import json
from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum


class AssetClass(Enum):
    EQUITIES = "equities"
    BONDS = "bonds"
    REAL_ESTATE = "real_estate"
    CASH = "cash"
    COMMODITIES = "commodities"


class Region(Enum):
    US = "US"
    EU = "EU"
    ASIA = "Asia"
    EMERGING = "Emerging Markets"


class Sector(Enum):
    TECHNOLOGY = "Technology"
    HEALTHCARE = "Healthcare"
    FINANCIALS = "Financials"
    ENERGY = "Energy"
    CONSUMER = "Consumer"
    INDUSTRIALS = "Industrials"
    MATERIALS = "Materials"


@dataclass
class Portfolio:
    """Player's portfolio state"""
    total_value: float = 100000.0
    allocation: Dict[AssetClass, float] = field(default_factory=lambda: {
        AssetClass.EQUITIES: 0.5,
        AssetClass.BONDS: 0.2,
        AssetClass.REAL_ESTATE: 0.2,
        AssetClass.CASH: 0.1,
        AssetClass.COMMODITIES: 0.0
    })
    regional_exposure: Dict[Region, float] = field(default_factory=lambda: {
        Region.US: 0.6,
        Region.EU: 0.2,
        Region.ASIA: 0.15,
        Region.EMERGING: 0.05
    })
    sector_exposure: Dict[Sector, float] = field(default_factory=lambda: {
        Sector.TECHNOLOGY: 0.25,
        Sector.HEALTHCARE: 0.15,
        Sector.FINANCIALS: 0.15,
        Sector.ENERGY: 0.1,
        Sector.CONSUMER: 0.15,
        Sector.INDUSTRIALS: 0.1,
        Sector.MATERIALS: 0.1
    })

    def calculate_resilience_score(self) -> float:
        """Calculate portfolio resilience score (0-100)"""
        # Diversification across assets
        asset_diversity = 1 - max(self.allocation.values()) / sum(self.allocation.values())

        # Regional diversification
        regional_diversity = 1 - max(self.regional_exposure.values()) / sum(self.regional_exposure.values())

        # Sector diversification
        sector_diversity = 1 - max(self.sector_exposure.values()) / sum(self.sector_exposure.values())

        # Cash buffer
        cash_buffer = self.allocation[AssetClass.CASH]

        # Liquidity proxy (cash + short-term bonds)
        liquidity = self.allocation[AssetClass.CASH] + 0.5 * self.allocation[AssetClass.BONDS]

        resilience = (
            asset_diversity * 25 +
            regional_diversity * 20 +
            sector_diversity * 20 +
            cash_buffer * 100 * 15 +
            liquidity * 100 * 20
        )

        return min(100, max(0, resilience))


@dataclass
class EconomicEvent:
    """Macroeconomic event that affects the economy"""
    name: str
    description: str
    effects: Dict[str, float]  # Asset class impacts
    regional_effects: Dict[Region, float] = field(default_factory=dict)
    sector_effects: Dict[Sector, float] = field(default_factory=dict)
    volatility_increase: float = 0.0
    systemic_risk: float = 0.0


class Decision(Enum):
    INCREASE_LIQUIDITY = "Increase Liquidity"
    HEDGE_INFLATION = "Hedge Inflation"
    ROTATE_DEFENSIVE = "Rotate Defensive"
    BUY_COMMODITIES = "Buy Commodities"
    DIVERSIFY_GLOBALLY = "Diversify Globally"
    INCREASE_RISK = "Increase Risk Exposure"
    REDUCE_LEVERAGE = "Reduce Leverage"
    INCREASE_DURATION = "Increase Duration"
    CONCENTRATE_TECHNOLOGY = "Concentrate in Technology"
    STABILIZE_PORTFOLIO = "Stabilize Portfolio"


@dataclass
class SimulationState:
    """Current state of the simulation"""
    portfolio: Portfolio
    current_month: int = 1
    economic_events: List[EconomicEvent] = field(default_factory=list)
    decision_history: List[Decision] = field(default_factory=list)
    performance_history: List[float] = field(default_factory=list)
    resilience_history: List[float] = field(default_factory=list)


class OrionSimulation:
    """Main simulation engine"""

    def __init__(self):
        self.events = self._load_events()
        self.state = SimulationState(Portfolio())

    def _load_events(self) -> List[EconomicEvent]:
        """Load predefined economic events"""
        return [
            EconomicEvent(
                name="Inflation Shock",
                description="Unexpected rise in inflation pressures global markets",
                effects={
                    AssetClass.BONDS: -0.15,
                    AssetClass.COMMODITIES: 0.25,
                    AssetClass.EQUITIES: -0.10,
                    AssetClass.CASH: 0.05,
                    AssetClass.REAL_ESTATE: -0.05
                },
                regional_effects={
                    Region.US: -0.05,
                    Region.EU: -0.10,
                    Region.ASIA: 0.05,
                    Region.EMERGING: 0.15
                },
                sector_effects={
                    Sector.ENERGY: 0.30,
                    Sector.MATERIALS: 0.20,
                    Sector.TECHNOLOGY: -0.15,
                    Sector.FINANCIALS: -0.10
                },
                volatility_increase=0.20,
                systemic_risk=0.15
            ),
            EconomicEvent(
                name="Tech Crash",
                description="Technology sector experiences significant correction",
                effects={
                    AssetClass.EQUITIES: -0.25,
                    AssetClass.BONDS: 0.05,
                    AssetClass.CASH: 0.02
                },
                sector_effects={
                    Sector.TECHNOLOGY: -0.40,
                    Sector.HEALTHCARE: -0.10,
                    Sector.FINANCIALS: 0.05,
                    Sector.ENERGY: 0.10
                },
                volatility_increase=0.30,
                systemic_risk=0.10
            ),
            EconomicEvent(
                name="Banking Crisis",
                description="Banking sector instability spreads to broader markets",
                effects={
                    AssetClass.EQUITIES: -0.20,
                    AssetClass.BONDS: -0.10,
                    AssetClass.CASH: 0.10,
                    AssetClass.REAL_ESTATE: -0.15
                },
                sector_effects={
                    Sector.FINANCIALS: -0.35,
                    Sector.REAL_ESTATE: -0.20,
                    Sector.TECHNOLOGY: -0.05
                },
                volatility_increase=0.25,
                systemic_risk=0.25
            ),
            EconomicEvent(
                name="Commodity Boom",
                description="Global demand drives commodity prices higher",
                effects={
                    AssetClass.COMMODITIES: 0.35,
                    AssetClass.EQUITIES: 0.10,
                    AssetClass.BONDS: -0.05
                },
                regional_effects={
                    Region.EMERGING: 0.20,
                    Region.ASIA: 0.15,
                    Region.US: 0.05
                },
                sector_effects={
                    Sector.ENERGY: 0.40,
                    Sector.MATERIALS: 0.30,
                    Sector.INDUSTRIALS: 0.15
                },
                volatility_increase=0.15,
                systemic_risk=0.05
            ),
            EconomicEvent(
                name="Rate Hike Cycle",
                description="Central banks aggressively raise interest rates",
                effects={
                    AssetClass.BONDS: -0.20,
                    AssetClass.REAL_ESTATE: -0.15,
                    AssetClass.EQUITIES: -0.10,
                    AssetClass.CASH: 0.08
                },
                regional_effects={
                    Region.US: -0.10,
                    Region.EU: -0.15,
                    Region.ASIA: -0.05
                },
                sector_effects={
                    Sector.FINANCIALS: 0.10,
                    Sector.TECHNOLOGY: -0.20,
                    Sector.REAL_ESTATE: -0.25
                },
                volatility_increase=0.20,
                systemic_risk=0.10
            )
        ]

    def select_random_event(self) -> EconomicEvent:
        """Select a random economic event"""
        return random.choice(self.events)

    def apply_decision(self, decision: Decision):
        """Apply a strategic decision to the portfolio"""
        if decision == Decision.INCREASE_LIQUIDITY:
            self.state.portfolio.allocation[AssetClass.CASH] += 0.10
            self.state.portfolio.allocation[AssetClass.EQUITIES] -= 0.05
            self.state.portfolio.allocation[AssetClass.BONDS] -= 0.05

        elif decision == Decision.HEDGE_INFLATION:
            self.state.portfolio.allocation[AssetClass.COMMODITIES] += 0.15
            self.state.portfolio.allocation[AssetClass.BONDS] -= 0.10
            self.state.portfolio.allocation[AssetClass.CASH] -= 0.05

        elif decision == Decision.ROTATE_DEFENSIVE:
            self.state.portfolio.allocation[AssetClass.BONDS] += 0.10
            self.state.portfolio.allocation[AssetClass.CASH] += 0.05
            self.state.portfolio.allocation[AssetClass.EQUITIES] -= 0.15

        elif decision == Decision.BUY_COMMODITIES:
            self.state.portfolio.allocation[AssetClass.COMMODITIES] += 0.20
            self.state.portfolio.allocation[AssetClass.EQUITIES] -= 0.10
            self.state.portfolio.allocation[AssetClass.REAL_ESTATE] -= 0.10

        elif decision == Decision.DIVERSIFY_GLOBALLY:
            self.state.portfolio.regional_exposure[Region.US] -= 0.10
            self.state.portfolio.regional_exposure[Region.EU] += 0.05
            self.state.portfolio.regional_exposure[Region.ASIA] += 0.05
            self.state.portfolio.regional_exposure[Region.EMERGING] += 0.05

        elif decision == Decision.INCREASE_RISK:
            self.state.portfolio.allocation[AssetClass.EQUITIES] += 0.15
            self.state.portfolio.allocation[AssetClass.CASH] -= 0.10
            self.state.portfolio.allocation[AssetClass.BONDS] -= 0.05

        elif decision == Decision.REDUCE_LEVERAGE:
            self.state.portfolio.allocation[AssetClass.CASH] += 0.10
            self.state.portfolio.allocation[AssetClass.EQUITIES] -= 0.10

        elif decision == Decision.INCREASE_DURATION:
            self.state.portfolio.allocation[AssetClass.BONDS] += 0.15
            self.state.portfolio.allocation[AssetClass.CASH] -= 0.10
            self.state.portfolio.allocation[AssetClass.EQUITIES] -= 0.05

        elif decision == Decision.CONCENTRATE_TECHNOLOGY:
            self.state.portfolio.sector_exposure[Sector.TECHNOLOGY] += 0.20
            self.state.portfolio.sector_exposure[Sector.HEALTHCARE] -= 0.05
            self.state.portfolio.sector_exposure[Sector.FINANCIALS] -= 0.05
            self.state.portfolio.sector_exposure[Sector.ENERGY] -= 0.05
            self.state.portfolio.sector_exposure[Sector.CONSUMER] -= 0.05

        elif decision == Decision.STABILIZE_PORTFOLIO:
            # Balance allocations
            target = 1.0 / len(self.state.portfolio.allocation)
            for asset in self.state.portfolio.allocation:
                self.state.portfolio.allocation[asset] = target

        # Normalize allocations
        total = sum(self.state.portfolio.allocation.values())
        for asset in self.state.portfolio.allocation:
            self.state.portfolio.allocation[asset] /= total

        # Normalize exposures
        total_regional = sum(self.state.portfolio.regional_exposure.values())
        for region in self.state.portfolio.regional_exposure:
            self.state.portfolio.regional_exposure[region] /= total_regional

        total_sector = sum(self.state.portfolio.sector_exposure.values())
        for sector in self.state.portfolio.sector_exposure:
            self.state.portfolio.sector_exposure[sector] /= total_sector

        self.state.decision_history.append(decision)

    def simulate_month(self, event: EconomicEvent, decision: Decision) -> Dict[str, Any]:
        """Simulate one month of economic activity"""
        # Apply decision first
        self.apply_decision(decision)

        # Calculate returns based on event
        asset_returns = {}
        for asset, base_return in event.effects.items():
            # Add some randomness
            volatility = event.volatility_increase
            random_factor = random.gauss(0, volatility)
            asset_returns[asset] = base_return + random_factor

        # Regional adjustments
        regional_returns = {}
        for region, effect in event.regional_effects.items():
            regional_returns[region] = effect + random.gauss(0, 0.05)

        # Sector adjustments
        sector_returns = {}
        for sector, effect in event.sector_effects.items():
            sector_returns[sector] = effect + random.gauss(0, 0.05)

        # Calculate portfolio return
        portfolio_return = 0
        for asset, weight in self.state.portfolio.allocation.items():
            portfolio_return += weight * asset_returns.get(asset, 0)

        # Apply regional and sector adjustments
        regional_adjustment = sum(
            self.state.portfolio.regional_exposure[region] * regional_returns.get(region, 0)
            for region in self.state.portfolio.regional_exposure
        )

        sector_adjustment = sum(
            self.state.portfolio.sector_exposure[sector] * sector_returns.get(sector, 0)
            for sector in self.state.portfolio.sector_exposure
        )

        total_return = portfolio_return + regional_adjustment + sector_adjustment

        # Update portfolio value
        old_value = self.state.portfolio.total_value
        self.state.portfolio.total_value *= (1 + total_return)

        # Record history
        self.state.performance_history.append(self.state.portfolio.total_value)
        self.state.resilience_history.append(self.state.portfolio.calculate_resilience_score())
        self.state.economic_events.append(event)
        self.state.current_month += 1

        return {
            "event": event,
            "portfolio_return": total_return,
            "old_value": old_value,
            "new_value": self.state.portfolio.total_value,
            "asset_returns": asset_returns,
            "regional_returns": regional_returns,
            "sector_returns": sector_returns,
            "resilience_score": self.state.portfolio.calculate_resilience_score()
        }

    def get_ai_explanation(self, simulation_result: Dict[str, Any]) -> str:
        """Generate AI-style explanation of the simulation results"""
        event = simulation_result["event"]
        portfolio_return = simulation_result["portfolio_return"]
        resilience = simulation_result["resilience_score"]

        explanation = f"**{event.name}:** {event.description}\n\n"

        if portfolio_return > 0:
            explanation += f"Your portfolio gained {portfolio_return:.1%} this month. "
        else:
            explanation += f"Your portfolio lost {abs(portfolio_return):.1%} this month. "

        # Explain key drivers
        if event.effects.get(AssetClass.COMMODITIES, 0) > 0 and self.state.portfolio.allocation[AssetClass.COMMODITIES] > 0.1:
            explanation += "Your commodity exposure helped offset losses in other assets. "
        elif event.effects.get(AssetClass.BONDS, 0) < 0 and self.state.portfolio.allocation[AssetClass.BONDS] > 0.2:
            explanation += "Bond holdings were pressured by rising rates. "
        elif event.effects.get(AssetClass.EQUITIES, 0) < 0 and self.state.portfolio.allocation[AssetClass.EQUITIES] > 0.4:
            explanation += "Equity exposure suffered from market volatility. "

        explanation += f"\n\n**Resilience Score:** {resilience:.1f}/100\n"

        if resilience > 70:
            explanation += "Your portfolio shows strong diversification and crisis resistance."
        elif resilience > 40:
            explanation += "Your portfolio has moderate resilience but could benefit from more diversification."
        else:
            explanation += "Your portfolio shows vulnerability to economic shocks. Consider increasing liquidity and diversification."

        return explanation</content>
<parameter name="filePath">/Users/marieyared/Desktop/startup/finance/finance-app/finance-simplified copy/orion_simulation.py