import sqlite3
import time
import random
import datetime
import uuid

# Configuration
DB_TYPE = "SQLITE" # Change to 'POSTGRES' and update connection params below
PG_PARAMS = {
    "dbname": "cash_maelstrom",
    "user": "postgres",
    "password": "password",
    "host": "localhost"
}

class PerformanceTester:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        if DB_TYPE == "SQLITE":
            self.conn = sqlite3.connect(":memory:") # In-memory for fast demo
        else:
            import psycopg2
            self.conn = psycopg2.connect(**PG_PARAMS)
        self.cursor = self.conn.cursor()
        print(f"Connected to {DB_TYPE} database.")

    def setup_schema(self):
        print("Setting up schema...")
        # Simplified schema for the test
        self.cursor.execute("""
            CREATE TABLE market_history (
                id INTEGER PRIMARY KEY,
                asset_pair TEXT,
                price REAL,
                volume REAL,
                timestamp TEXT
            )
        """)
        self.conn.commit()

    def generate_dummy_data(self, num_rows=10000):
        print(f"Generating {num_rows} dummy rows...")
        data = []
        base_time = datetime.datetime.now()
        assets = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT']
        
        for i in range(num_rows):
            asset = random.choice(assets)
            price = random.uniform(100, 50000)
            volume = random.uniform(1, 100)
            ts = (base_time - datetime.timedelta(minutes=i)).isoformat()
            data.append((asset, price, volume, ts))
        
        self.cursor.executemany("INSERT INTO market_history (asset_pair, price, volume, timestamp) VALUES (?, ?, ?, ?)", data)
        self.conn.commit()
        print("Data insertion complete.")

    def run_benchmark(self, query, description):
        start_time = time.perf_counter()
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        end_time = time.perf_counter()
        duration = (end_time - start_time) * 1000 # ms
        print(f"Benchmark [{description}]: {duration:.4f} ms (Rows: {len(results)})")
        return duration

    def create_index(self):
        print("Creating Indexes...")
        t0 = time.time()
        self.cursor.execute("CREATE INDEX idx_asset_pair ON market_history(asset_pair)")
        self.cursor.execute("CREATE INDEX idx_timestamp ON market_history(timestamp)")
        self.conn.commit()
        print(f"Indexes created in {time.time()-t0:.4f}s")

    def run_full_test(self):
        self.connect()
        self.setup_schema()
        self.generate_dummy_data(50000) # 50k for noticeable impact

        query = "SELECT * FROM market_history WHERE asset_pair = 'BTC/USDT' AND price > 20000"

        print("\n--- PRE-INDEXING TEST ---")
        time_pre = self.run_benchmark(query, "No Index")

        self.create_index()

        print("\n--- POST-INDEXING TEST ---")
        time_post = self.run_benchmark(query, "With Index")

        print("\n--- PERFORMANCE REPORT ---")
        improvement = time_pre / time_post if time_post > 0 else 0
        print(f"Improvement Factor: {improvement:.2f}x FASTER")
        
        # ASCII Chart
        max_width = 50
        bar_pre = int(max_width)
        bar_post = int(max_width * (time_post / time_pre)) if time_pre > 0 else 0
        
        print("\nVisual Comparison:")
        print(f"Pre-Index  | {'█' * bar_pre} ({time_pre:.2f}ms)")
        print(f"Post-Index | {'█' * bar_post} ({time_post:.2f}ms)")

if __name__ == "__main__":
    tester = PerformanceTester()
    tester.run_full_test()
