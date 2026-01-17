import time
import random
from analytics.statistics_module import StatisticsModule
from agents.core_entities import Scout, SimulationSession, RiskProfile

def print_banner():
    print(r"""
   ______           __      __  ___            __      __                      
  / ____/___ ______/ /_    /  |/  /___  ___  / /_____/ /__________  ____ ___ 
 / /   / __ `/ ___/ __ \  / /|_/ / __ \/ _ \/ / ___/ __/ ___/ __ \/ __ `__ \
/ /___/ /_/ (__  ) / / / / /  / / / / /  __/ (__  ) /_/ /  / /_/ / / / / / /
\____/\__,_/____/_/ /_/ /_/  /_/_/ /_/\___/_/____/\__/_/   \____/_/ /_/ /_/ 
                                                                               
    >> AUTONOMOUS AI HEDGE FUND SIMULATION TERMINAL <<
    >> MODE: ANALYSIS & HIGH-FIDELITY SIMULATION ONLY <<
    """)

def run_simulation_demo():
    print_banner()
    time.sleep(1)

    # 1. Initialize Session
    session = SimulationSession("ALPHA_GENESIS_01", duration_hours=24)
    session.start_simulation()

    # 2. Deploy Agents
    print("\n[SYSTEM] Deploying Swarm Intelligence...")
    scout_alpha = Scout("Scout-Alpha")
    scout_beta = Scout("Scout-Beta")
    session.add_agent(scout_alpha)
    session.add_agent(scout_beta)
    time.sleep(1)

    # 3. Simulate Data Stream
    print("\n[DATA_STREAM] Connecting to Global Awareness Stream...")
    btc_prices = []
    
    for i in range(20):
        # Generate random walk price
        last_price = btc_prices[-1] if btc_prices else 50000.0
        change = random.uniform(-100, 100)
        price = last_price + change
        btc_prices.append(price)
        
        # Real-time agent reaction
        if i % 5 == 0:
            scout_alpha.execute_task({"price_change": change, "current_price": price})
        
        time.sleep(0.05) # fast forward

    # 4. Statistical Analysis
    print("\n[ANALYTICS] Processing Stream Data through Statistics Module...")
    stats = StatisticsModule(btc_prices)
    report = stats.get_full_report()

    print("\n" + "="*40)
    print(" STATISTICAL REPORT: BTC/USDT (SIMULATION)")
    print("="*40)
    print(f"Data Points: {report['count']}")
    print(f"Mean Price:  ${report['mean']:,.2f}")
    print(f"Variance:    {report['variance']:,.2f}")
    print(f"Std Dev:     {report['std_dev']:,.2f}")
    
    print("\n[VISUALIZATION] Generating Histogram Data...")
    hist = report['histogram']
    print(f"Bins: {hist['bin_edges']}")
    print(f"Counts: {hist['counts']}")

    # 5. Risk Assessment
    print("\n[RISK_CORE] Evaluating Position Risk...")
    risk_profile = RiskProfile(risk_level="AGGRESSIVE")
    is_safe = risk_profile.evaluate_risk(report['std_dev'] / report['mean']) # Coeff of Variation
    print(f"Risk Assessment: {'SAFE' if is_safe else 'HIGH RISK DETECTED'}")

    print("\nSimulation Complete.")

if __name__ == "__main__":
    run_simulation_demo()
