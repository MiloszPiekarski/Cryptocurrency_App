from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import datetime
import uuid

# --- Patterns & Interfaces ---

class Observer(ABC):
    @abstractmethod
    def update(self, event_type: str, data: Any):
        pass

class Subject:
    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, event_type: str, data: Any):
        for observer in self._observers:
            observer.update(event_type, data)

class AnalysisStrategy(ABC):
    """Strategy Pattern Interface for analysis logic."""
    @abstractmethod
    def analyze(self, data: Any) -> Dict[str, Any]:
        pass

class DatabaseConnection:
    """Singleton Pattern for Database Connection."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection_string = "postgresql://user:pass@localhost:5432/cash_maelstrom"
            cls._instance.is_connected = False
            print("DatabaseConnection Singleton Created")
        return cls._instance

    def connect(self):
        if not self.is_connected:
            print(f"Connecting to DB at {self.connection_string}...")
            self.is_connected = True

# --- Core Entities ---

class RiskProfile:
    def __init__(self, risk_level: str = "MODERATE", max_drawdown: float = 0.15):
        self.risk_level = risk_level
        self.max_drawdown = max_drawdown # 15%
        self.stop_loss_threshold = 0.05
    
    def evaluate_risk(self, volatility: float) -> bool:
        if self.risk_level == "AGGRESSIVE":
            return volatility < 0.5
        return volatility < 0.2

class AssetAnalytics:
    def __init__(self, asset_symbol: str):
        self.asset_symbol = asset_symbol
        self.current_price = 0.0
        self.volatility = 0.0
        self.sentiment_score = 0.0 # -1.0 to 1.0

    def update_metrics(self, price: float, sentiment: float):
        self.current_price = price
        self.sentiment_score = sentiment
        # Volatility calc would go here

class MarketAgent(Observer, ABC):
    def __init__(self, name: str, role: str, strategy: AnalysisStrategy):
        self.id = str(uuid.uuid4())
        self.name = name
        self.role = role
        self.strategy = strategy
        self.logs: List[str] = []

    def log(self, message: str):
        timestamp = datetime.datetime.now().isoformat()
        entry = f"[{timestamp}] [{self.role}] {self.name}: {message}"
        self.logs.append(entry)
        print(entry)

    def set_strategy(self, strategy: AnalysisStrategy):
        self.strategy = strategy

    @abstractmethod
    def execute_task(self, market_data: Any):
        pass

    def update(self, event_type: str, data: Any):
        # React to market events (Observer)
        self.log(f"Received event {event_type}")
        if event_type == "MARKET_CRASH_WARNING":
             self.log("INITIATING DEFENSIVE PROTOCOLS")

# --- Specific Agent Implementations ---

class VolatilityAnalysisStrategy(AnalysisStrategy):
    def analyze(self, data: Any) -> Dict[str, Any]:
        # Dummy logic
        val = data.get("price_change", 0)
        return {"volatility_alert": abs(val) > 5.0}

class SentimentAnalysisStrategy(AnalysisStrategy):
    def analyze(self, data: Any) -> Dict[str, Any]:
        return {"sentiment_trend": "POSITIVE" if data.get("sentiment", 0) > 0 else "NEGATIVE"}

class Scout(MarketAgent):
    def __init__(self, name: str):
        super().__init__(name, "SCOUT", VolatilityAnalysisStrategy())

    def execute_task(self, market_data: Any):
        self.log("Scouting market data...")
        result = self.strategy.analyze(market_data)
        self.log(f"Analysis Result: {result}")

class SimulationSession:
    def __init__(self, session_name: str, duration_hours: int):
        self.id = str(uuid.uuid4())
        self.name = session_name
        self.duration_hours = duration_hours
        self.agents: List[MarketAgent] = []
        self.market_event_stream = Subject()
        self.is_active = False

    def add_agent(self, agent: MarketAgent):
        self.agents.append(agent)
        self.market_event_stream.attach(agent)

    def start_simulation(self):
        self.is_active = True
        print(f"Simulation '{self.name}' STARTED.")
        # DB connection usage
        db = DatabaseConnection()
        db.connect()

    def inject_market_event(self, event_type: str, data: Any):
        print(f"\n--- Injecting Event: {event_type} ---")
        self.market_event_stream.notify(event_type, data)
