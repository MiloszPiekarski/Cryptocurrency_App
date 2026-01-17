from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import random

class TraderAgent(Agent):
    def __init__(self, unique_id, model, strategy="random"):
        super().__init__(unique_id, model)
        self.money = 10000
        self.holdings = 0
        self.safe_haven_holdings = 0 # Gold/Bonds
        self.strategy = strategy 

    def step(self):
        price = self.model.price
        decision = 0 # 0: hold, 1: buy, -1: sell, 2: flee_to_safety
        
        # --- STRATEGY LOGIC ---
        if self.model.panic_mode:
            # Panic logic: Sell everything, buy Gold (Safe Haven)
            decision = 2
        elif self.strategy == "momentum":
            if self.model.trend > 0: decision = 1
            else: decision = -1
        elif self.strategy == "mean_reversion":
            if price > self.model.avg_price: decision = -1
            else: decision = 1
        elif self.strategy == "chartist":
             if self.model.rsi > 70: decision = -1
             elif self.model.rsi < 30: decision = 1
        else:
            decision = random.choice([-1, 0, 1])
            
        # --- EXECUTION ---
        if decision == 2: # Flee to Safety (Point 8 & 30)
            if self.holdings > 0:
                # Sell crypto
                proceeds = self.holdings * price
                self.holdings = 0
                self.money += proceeds
                self.model.sell_orders += 5 # Panic selling pressure
            
            # Buy Safe Haven (Simulated)
            if self.money > 0:
                self.safe_haven_holdings += self.money
                self.money = 0
                
        elif decision == 1 and self.money >= price:
            self.holdings += 1
            self.money -= price
            self.model.buy_orders += 1
        elif decision == -1 and self.holdings > 0:
            self.holdings -= 1
            self.money += price
            self.model.sell_orders += 1

class MarketModel(Model):
    def __init__(self, initial_price=50000, num_agents=100, panic_mode=False):
        super().__init__()
        self.num_agents = num_agents
        self.schedule = RandomActivation(self)
        self.price = initial_price
        self.avg_price = initial_price
        self.trend = 0
        self.rsi = 50
        self.panic_mode = panic_mode
        
        self.buy_orders = 0
        self.sell_orders = 0
        
        for i in range(num_agents):
            strategy = random.choice(["momentum", "mean_reversion", "chartist", "noise"])
            a = TraderAgent(i, self, strategy)
            self.schedule.add(a)
            
        self.datacollector = DataCollector(
            model_reporters={"Price": "price", "RSI": "rsi"}
        )

    def step(self):
        self.buy_orders = 0
        self.sell_orders = 0
        
        self.schedule.step()
        
        # Market Microstructure Physics
        imbalance = self.buy_orders - self.sell_orders
        
        if self.panic_mode:
            # External shock + panic selling pressure
            impact = 0.02 * self.price # 2% drops per step in panic
            imbalance = -abs(self.sell_orders) # Force negative
        else:
            impact = 0.0005 * self.price 
        
        new_price = self.price + (imbalance * impact)
        # Noise
        noise = random.uniform(-0.001, 0.001) * self.price
        new_price += noise
        
        self.trend = new_price - self.price
        self.price = max(0.01, new_price) # No negative prices
        self.avg_price = (self.avg_price * 0.95) + (self.price * 0.05)
        
        # RSI update
        gain = max(0, self.trend)
        loss = max(0, -self.trend)
        rs = gain / (loss + 1e-9)
        self.rsi = 100 - (100 / (1 + rs))
        
        self.datacollector.collect(self)

def run_simulation(start_price, steps=50, panic_scenario=False):
    model = MarketModel(initial_price=start_price, num_agents=200, panic_mode=panic_scenario)
    for i in range(steps):
        model.step()
        
    final_price = model.price
    df = model.datacollector.get_model_vars_dataframe()
    
    return {
        "model": "Digital Twin (Mesa Agent-Based)",
        "scenario": "PANIC_CRASH" if panic_scenario else "NORMAL_MARKET",
        "initial_price": start_price,
        "final_predicted_price": round(final_price, 2),
        "prediction": "BULLISH" if final_price > start_price else "BEARISH",
        "steps_simulated": steps,
        "panic_triggered": panic_scenario,
        "trajectory": df["Price"].tail(20).tolist(),
        "rsi_trajectory": df["RSI"].tail(20).tolist()
    }
