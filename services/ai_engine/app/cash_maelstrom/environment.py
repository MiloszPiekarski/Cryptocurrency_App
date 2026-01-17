from typing import List, Dict, Any
import random
from .analytics.statistics_module import StatisticsModule
from .agents.core_entities import SimulationSession, Scout, RiskProfile

class MarketEnvironment:
    def __init__(self, symbol: str, start_price: float, panic_mode: bool = False):
        self.symbol = symbol
        self.current_price = start_price
        self.panic_mode = panic_mode
        self.price_history: List[float] = [start_price]
        self.session = SimulationSession(f"SIM_{symbol}", duration_hours=24)
        
        # Deploy standard swarm
        self.scout = Scout("Swarm_Scout_Alpha")
        self.session.add_agent(self.scout)

    def step(self):
        """
        Advancing the market by one tick (simulated).
        """
        # Physics Engines
        volatility = 0.02 if self.panic_mode else 0.005
        drift = -0.01 if self.panic_mode else 0.0001
        
        shock = random.gauss(drift, volatility)
        change = self.current_price * shock
        self.current_price += change
        
        # Ensure positive price
        self.current_price = max(0.01, self.current_price)
        self.price_history.append(self.current_price)
        
        # Notify Agents
        self.session.inject_market_event("PRICE_UPDATE", {
            "price": self.current_price,
            "change": change
        })

    def run(self, steps: int = 50) -> Dict[str, Any]:
        self.session.start_simulation()
        
        for _ in range(steps):
            self.step()
            
        stats = StatisticsModule(self.price_history)
        report = stats.get_full_report()
        
        # Determination
        start = self.price_history[0]
        end = self.price_history[-1]
        prediction = "BULLISH" if end > start else "BEARISH"
        
        if self.panic_mode and end < start * 0.8:
            prediction = "CRASH_IMMINENT"

        return {
            "symbol": self.symbol,
            "trajectory": self.price_history,
            "prediction": prediction,
            "stats": {
                "mean": report["mean"],
                "std_dev": report["std_dev"],
                "variance": report["variance"]
            },
            "panic_mode": self.panic_mode
        }
