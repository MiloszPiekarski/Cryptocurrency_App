try:
    import ray
except ImportError:
    print("⚠️ Ray not found. Using MockRay for synchronous fallback.")
    class MockRay:
        def remote(self, obj):
            return obj
        def is_initialized(self):
            return False
        def get(self, futures, timeout=None):
            return futures
    ray = MockRay()
import os
import random
import time
from datetime import datetime
from app.analysis.market_stats_processor import MarketStatisticsProcessor
from app.services.market_data import market_data
from app.services.vertex_client import vertex_service
import pandas as pd

# --- UTILS ---
def generate_id(prefix):
    return f"{prefix}_{random.randint(1000, 9999)}"

# --- SPECIALIZED AGENT CLASSES ---

@ray.remote
class ScoutAgent:
    """
    The Quant / Mathematician.
    Focus: Hard numbers, Z-Scores, Standard Deviations, Volume Deltas.
    Style: Clinical, precise, data-heavy.
    """
    def __init__(self, agent_id):
        self.agent_id = generate_id("SCOUT")

    def scan(self, symbol, current_price, stats, ohlcv_df):
        import pandas as pd
        import numpy as np
        if not stats or 'math_proof' not in stats:
             return {"role": "SCOUT", "id": self.agent_id, "signal": "NEUTRAL", "confidence": 0, "reasoning": "Insufficient data"}
        
        math_data = stats['math_proof']
        sigma = math_data['dispersion']['std_dev_sigma']
        mu = math_data['central_tendency']['mean_mu']
        
        # 1. Z-Score Analysis
        z_score = (current_price - mu) / sigma if sigma > 0 else 0
        
        # 2. Volume Delta
        vol_delta = 0.0
        if not ohlcv_df.empty:
            last_vol = ohlcv_df.iloc[-1]['volume']
            avg_vol = ohlcv_df['volume'].mean()
            vol_delta = ((last_vol - avg_vol) / avg_vol) * 100

        # Signals
        signal = "HOLD"
        confidence = 50
        
        if abs(z_score) > 2.5:
            signal = "SELL" if z_score > 0 else "BUY"
            confidence = 85
        elif vol_delta > 200:
            signal = "BUY" if current_price > mu else "SELL"
            confidence = 75

        # REAL AI GENERATION
        import asyncio
        indicators = {
            "symbol": symbol,
            "price": current_price,
            "z_score": round(z_score, 4),
            "sigma": round(sigma, 2),
            "vol_delta": round(vol_delta, 2)
        }
        
        # Run async Vertex call in sync method
        try:
            ai_reasoning = asyncio.run(vertex_service.analyze_market_context(indicators, "SCOUT"))
        except Exception as e:
            ai_reasoning = f"Neural Link Error: {e}. Z-Score: {z_score:.2f}."

        return {
            "role": "SCOUT",
            "id": self.agent_id,
            "type": "QUANT",
            "signal": signal,
            "confidence": confidence,
            "reasoning": ai_reasoning,
            "source_data": indicators
        }

@ray.remote
class HunterAgent:
    """
    The Trader.
    Focus: Order Book, Price Action, Support/Resistance, Walls.
    Style: Technical, aggressive, market-focused.
    """
    def __init__(self, agent_id):
        self.agent_id = generate_id("HUNTER")

    def hunt(self, symbol, current_price, orderbook, trades):
        if not orderbook:
             return {"role": "HUNTER", "id": self.agent_id, "signal": "NEUTRAL", "reasoning": "Orderbook unavailable"}

        # 1. Analyze Depth (Walls)
        bids = orderbook.get('bids', [])
        asks = orderbook.get('asks', [])
        
        if not bids or not asks:
            return {"role": "HUNTER", "id": self.agent_id, "signal": "NEUTRAL", "reasoning": "Thin book"}

        bid_wall_vol = sum(b['quantity'] for b in bids[:5])
        ask_wall_vol = sum(a['quantity'] for a in asks[:5])
        ratio = bid_wall_vol / ask_wall_vol if ask_wall_vol > 0 else 1.0
        
        signal = "HOLD"
        confidence = 50
        
        if ratio > 1.5:
            signal = "BUY"
            confidence = 75
        elif ratio < 0.6:
            signal = "SELL"
            confidence = 75

        # REAL AI GENERATION
        import asyncio
        indicators = {
            "symbol": symbol,
            "bid_vol_top5": round(bid_wall_vol, 2),
            "ask_vol_top5": round(ask_wall_vol, 2),
            "imbalance_ratio": round(ratio, 2)
        }
        
        try:
            ai_reasoning = asyncio.run(vertex_service.analyze_market_context(indicators, "HUNTER"))
        except Exception as e:
            ai_reasoning = f"Neural Link Error: {e}. Ratio: {ratio:.2f}."
            
        return {
            "role": "HUNTER",
            "id": self.agent_id,
            "type": "TRADER",
            "signal": signal,
            "confidence": confidence,
            "reasoning": ai_reasoning,
            "source_data": indicators
        }

@ray.remote
class AnalystAgent:
    """
    The Fundamentals / Narrative Expert.
    Focus: Sentiment, News (Vertex AI), Context.
    Style: Professional, concise, explanatory.
    """
    def __init__(self, agent_id):
        self.agent_id = generate_id("ANALYST")

    def analyze(self, symbol, current_price, ohlcv_df):
        import pandas as pd
        if not ohlcv_df.empty and 'RSI_14' in ohlcv_df.columns:
            rsi = ohlcv_df.iloc[-1]['RSI_14']
            
        tech_sentiment = "NEUTRAL"
        if rsi > 70: tech_sentiment = "OVERBOUGHT"
        elif rsi < 30: tech_sentiment = "OVERSOLD"
        
        signal = "HOLD"
        confidence = 50
        
        if tech_sentiment == "OVERSOLD":
            signal = "BUY"
            confidence = 60
        elif tech_sentiment == "OVERBOUGHT":
            signal = "SELL"
            confidence = 60

        # REAL AI GENERATION (Includes RSS Fetch internally)
        import asyncio
        indicators = {
            "symbol": symbol,
            "rsi": round(rsi, 2),
            "market_phase": tech_sentiment
        }
        
        try:
            ai_reasoning = asyncio.run(vertex_service.analyze_market_context(indicators, "ANALYST"))
        except Exception as e:
            ai_reasoning = f"Neural Link Error: {e}. RSI: {rsi:.2f}."

        return {
            "role": "ANALYST",
            "id": self.agent_id,
            "type": "NARRATIVE",
            "signal": signal,
            "confidence": confidence,
            "reasoning": ai_reasoning,
            "source_data": indicators
        }

@ray.remote
class DefenderAgent:
    """
    The Risk Officer.
    Focus: Risk Management, Volatility Capping.
    Style: Cautious, negative-bias (Veto power).
    """
    def __init__(self, agent_id):
        self.agent_id = generate_id("DEFENDER")

    def assess_risk(self, symbol, current_price, stats):
        if not stats or 'math_proof' not in stats:
             return {"role": "DEFENDER", "id": self.agent_id, "signal": "SKIP", "reasoning": "No Risk Data"}
        
        math_data = stats['math_proof']
        sigma = math_data['dispersion']['std_dev_sigma']
        
        if current_price > 0:
            volatility_rel = (sigma / current_price) * 100
        else:
            volatility_rel = 0.0
        
        status = "SAFE"
        veto = False
        reasoning = f"Volatility {volatility_rel:.2f}% is within acceptable limits."
        
        if volatility_rel > 3.0:
            status = "CRITICAL"
            veto = True
            reasoning = f"CRITICAL RISK. Volatility {volatility_rel:.2f}% exceeds safety threshold (3%). Trading Halted."
        elif volatility_rel > 1.5:
            status = "WARNING"
            reasoning = f"Elevated Risk. Volatility {volatility_rel:.2f}%. Reduce position sizing."
            
        return {
            "role": "DEFENDER",
            "id": self.agent_id,
            "type": "RISK",
            "signal": "HOLD" if veto else "SAFE", # Defender acts as a filter
            "risk_level": status,
            "veto": veto,
            "reasoning": reasoning,
            "source_data": {
                "volatility_pct": round(volatility_rel, 2)
            }
        }

@ray.remote
class NewsSentinelAgent:
    """
    The News Sentinel.
    Focus: Real-time global headlines, flash news, and social sentiment.
    Task: Scan news feeds and assess impact on the asset.
    """
    def __init__(self, agent_id):
        self.agent_id = generate_id("SENTINEL")

    async def scan_headlines(self, symbol):
        # We leverage the existing vertex_service to get news
        # In a full version, this would use a dedicated Search/News API
        try:
            headlines = await vertex_service._fetch_crypto_news()
            
            indicators = {
                "symbol": symbol,
                "news_dump": headlines
            }
            
            ai_reasoning = await vertex_service.analyze_market_context(indicators, "ANALYST")
            
            # Simple sentiment parsing from AI reasoning
            sentiment = "NEUTRAL"
            if "bullish" in ai_reasoning.lower(): sentiment = "BULLISH"
            elif "bearish" in ai_reasoning.lower(): sentiment = "BEARISH"
            
            return {
                "role": "SENTINEL",
                "id": self.agent_id,
                "type": "NEWS",
                "signal": "BUY" if sentiment == "BULLISH" else "SELL" if sentiment == "BEARISH" else "HOLD",
                "confidence": 70,
                "reasoning": ai_reasoning,
                "source_data": {"headlines": headlines}
            }
        except Exception as e:
            return {"role": "SENTINEL", "id": self.agent_id, "signal": "NEUTRAL", "reasoning": f"News link failed: {e}"}

@ray.remote
class StrategistAgent:
    """
    The Institutional Investor (MACRO).
    Focus: Long-term trends (BigQuery), 30-day volatility.
    """
    def __init__(self, agent_id):
        self.agent_id = generate_id("STRATEGIST")

    def plan(self, symbol):
        from app.services.bigquery_client import bq_service
        import pandas as pd
        
        # 1. Fetch 30-Day Macro Trend
        df = bq_service.get_historical_trends(symbol, days=30)
        
        if df is None or df.empty:
            return {
                "role": "STRATEGIST",
                "id": self.agent_id,
                "type": "MACRO",
                "signal": "NEUTRAL",
                "reasoning": "Historical deep-data unavailable for macro modeling.",
                "is_gated": False
            }
            
        # 2. Simple Trend Analysis
        start_price = df.iloc[0]['avg_price']
        end_price = df.iloc[-1]['avg_price']
        price_change = ((end_price - start_price) / start_price) * 100
        avg_volatility = df['price_volatility'].mean()
        
        signal = "HOLD"
        if price_change > 10: signal = "BUY"
        elif price_change < -10: signal = "SELL"
        
        return {
            "role": "STRATEGIST",
            "id": self.agent_id,
            "type": "MACRO",
            "signal": signal,
            "reasoning": f"30-Day Macro Review: Asset has shifted {price_change:.2f}% with average volatility of {avg_volatility:.2f}. Institutional bias is {signal}.",
            "is_gated": False,
            "source_data": {
                "30d_change": round(price_change, 2),
                "avg_volatility": round(avg_volatility, 2)
            }
        }

# --- HIVE MIND ORCHESTRATOR ---

class HiveMind:
    def __init__(self):
        self.enabled = False
        self.stats_engine = MarketStatisticsProcessor()
        # Skip Ray entirely due to space in path issue - use sync fallback always
        self.ray_workers_broken = True  # Set True to use fast sync fallback
        # Holders for agents
        self.scouts = []
        self.hunters = []
        self.analysts = []
        self.defenders = []
        self.strategists = []
        self.sentinels = []
        
        self.last_swarm_result = {}
        self.config_version = 0
        
    def start_swarm(self):
        """
        Explicitly start the swarm. Called only by the main driver process.
        """
        if self.enabled: return
        
        try:
            print("🧠 [HIVE] Initializing Ray...")
            
            # Create a symlink-based working directory to avoid spaces in path
            import shutil
            safe_working_dir = "/tmp/ray_turbo_workdir"
            
            # Pass ENV to Ray Workers with a safe working directory
            runtime_env = {
                "env_vars": {
                    "GOOGLE_CLOUD_PROJECT": os.getenv("GOOGLE_CLOUD_PROJECT"),
                    "GOOGLE_APPLICATION_CREDENTIALS": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
                    "PYTHONUNBUFFERED": "1",
                    "RAY_memory_usage_threshold": "0.98" # Allow more memory usage before killing
                },
                "working_dir": safe_working_dir if os.path.exists(safe_working_dir) else None
            }
            
            # Clean working_dir if None to avoid Ray issues
            if runtime_env["working_dir"] is None:
                del runtime_env["working_dir"]
            
            # RAY DISABLE (Stability Fix)
            self.ray_workers_broken = True
            self.last_swarm_result = {} # Cache for PDF generation
            
            # Skip Ray Init to avoid timeout/crash
            print("🧠 [HIVE] Cabinet Assembled (SYNC MODE - Ray Disabled).")
            self.enabled = True
            
        except Exception as e:
            print(f"⚠️ HIVE MIND INIT FAILURE: {e}")
            self.enabled = False

    def _gather_data_sync(self, symbol):
        """Helper to fetch IO-bound data synchronously in a thread."""
        stats = self.stats_engine.process_asset_statistics(symbol)
        ohlcv_df = market_data.get_ohlcv(symbol, limit=100)
        try:
            orderbook = market_data.get_orderbook(symbol, limit=10)
        except Exception as e:
            print(f"⚠️ [HIVE] Orderbook Fetch Failed: {e}")
            orderbook = None
        trades = market_data.get_trades(symbol, limit=50)
        return stats, ohlcv_df, orderbook, trades

    async def swarm_scan(self, symbol, price, agent_weights=None):
        # Default weights if not provided
        if agent_weights is None:
            agent_weights = {
                "scout": 1.0, "hunter": 1.0, "analyst": 1.0,
                "defender": 1.0, "strategist": 1.0
            }
        
        # Auto-start if not enabled, but only try once to avoid loop
        if not self.enabled and not ray.is_initialized():
             print("⚠️ [HIVE] Auto-starting Swarm on first request...")
             self.start_swarm()

        # 1. Gather REAL Data (IO Bound - do this before Ray wait)
        # We run this in a thread to fully unblock the event loop
        import asyncio
        loop = asyncio.get_event_loop()
        stats, ohlcv_df, orderbook, trades = await loop.run_in_executor(None, self._gather_data_sync, symbol)
        
        if not self.enabled:
             return {"error": "Swarm Offline"}

        try:
            # 2. Parallel Processing (CPU Bound / Logic) via Ray
            # Skip Ray if workers are known to be broken (path with spaces issue)
            if self.ray_workers_broken:
                loop = asyncio.get_event_loop()
                sync_out = await loop.run_in_executor(None, self._run_agents_sync, symbol, price, stats, ohlcv_df, orderbook, trades, agent_weights)
                results = sync_out.get('swarm_breakdown', [])
                consensus_text = sync_out.get('global_consensus', "Consensus Unavailable")
            else:
                try:
                    # Scouts need Stats + OHLCV
                    scout_futures = [a.scan.remote(symbol, price, stats, ohlcv_df) for a in self.scouts]
                    # Hunters need Orderbook + Trades
                    hunter_futures = [a.hunt.remote(symbol, price, orderbook, trades) for a in self.hunters]
                    # Analysts need OHLCV
                    analyst_futures = [a.analyze.remote(symbol, price, ohlcv_df) for a in self.analysts]
                    # Defenders need Stats
                    defender_futures = [a.assess_risk.remote(symbol, price, stats) for a in self.defenders]
                    # Strategists need Symbol
                    strategist_futures = [a.plan.remote(symbol) for a in self.strategists]
                    # Sentinels need Symbol (Async wait handles news)
                    sentinel_futures = [a.scan_headlines.remote(symbol) for a in self.sentinels]
                    
                    # 3. Aggregate with short timeout
                    all_futures = scout_futures + hunter_futures + analyst_futures + defender_futures + strategist_futures + sentinel_futures
                    results = ray.get(all_futures, timeout=5)  # Reduced timeout to 5 seconds
                    
                except Exception as ray_error:
                    # SYNCHRONOUS FALLBACK - Run agents locally if Ray workers fail
                    print(f"⚠️ [HIVE] Ray workers failed ({ray_error}), using sync fallback...")
                    self.ray_workers_broken = True  # Mark as broken for future requests
                    loop = asyncio.get_event_loop()
                    sync_out = await loop.run_in_executor(None, self._run_agents_sync, symbol, price, stats, ohlcv_df, orderbook, trades, agent_weights)
                    results = sync_out.get('swarm_breakdown', [])
                    consensus_text = sync_out.get('global_consensus', "Consensus Unavailable")

            # Filter results based on weights (User Requirement: disabled agents should disappear)
            active_results = []
            for r in results:
                role = r.get('role', '').lower()
                weight = agent_weights.get(role, 1.0)
                if weight > 0:
                    active_results.append(r)
            
            results = active_results # Use filtered results for all subsequent logic

            # Consensus for Ray path (if not generated by fallback)
            if 'consensus_text' not in locals():
                 consensus_text = "Consensus pending..."
                 try:
                     from app.services.vertex_client import vertex_service
                     consensus_text = vertex_service.generate_global_consensus_sync(results)
                 except Exception as e:
                     print(f"⚠️ [HIVE] Ray Consensus Failed: {e}")
            
            # 4. Synthesize Verdict with WEIGHTED voting
            score = 0
            total_weight = 0
            
            # Check Risk Veto
            risk_alert = next((r for r in results if r['role'] == "DEFENDER"), None)
            risk_status = risk_alert['risk_level'] if risk_alert else "UNKNOWN"
            
            if risk_status == "CRITICAL":
                verdict = "HALT"
                score = 0
            else:
                for r in results:
                    if r.get('is_gated'): continue # Skip gated strategist
                    
                    # Get agent weight based on role
                    role = r['role'].lower()
                    weight = agent_weights.get(role, 1.0)
                    
                    # Skip agents with 0 weight entirely
                    if weight == 0:
                        continue
                    
                    # Apply weighted score
                    if r['signal'] == "BUY": 
                        score += r['confidence'] * weight
                    elif r['signal'] == "SELL": 
                        score -= r['confidence'] * weight
                    total_weight += weight
                
                final_score = score / total_weight if total_weight > 0 else 0
                
                if final_score > 20: verdict = "BUY"
                elif final_score < -20: verdict = "SELL"
                else: verdict = "HOLD"

            final_confidence = round(abs(final_score), 2) if risk_status != "CRITICAL" else 0
            result_payload = {
                "symbol": symbol,
                "price": price,
                "verdict": verdict,
                "confidence_score": final_confidence,
                "risk_status": risk_status,
                "agents_active": len(results),
                "global_consensus": consensus_text, # NEW FIELD
                "swarm_breakdown": results, # The Evidence Log
                "timestamp": datetime.now().isoformat(),
                "math_context": stats['math_proof'] if stats else None,
                "summary_data": {
                    "price": price,
                    "high": stats['math_proof']['central_tendency']['mean_mu'] + (2 * stats['math_proof']['dispersion']['std_dev_sigma']) if stats and 'math_proof' in stats and 'central_tendency' in stats['math_proof'] and 'dispersion' in stats['math_proof'] else price * 1.02,
                    "low": stats['math_proof']['central_tendency']['mean_mu'] - (2 * stats['math_proof']['dispersion']['std_dev_sigma']) if stats and 'math_proof' in stats and 'central_tendency' in stats['math_proof'] and 'dispersion' in stats['math_proof'] else price * 0.98,
                    "volume": ohlcv_df.iloc[-1]['volume'] if not ohlcv_df.empty else 0,
                    "change_24h": ((ohlcv_df.iloc[-1]['close'] - ohlcv_df.iloc[0]['close']) / ohlcv_df.iloc[0]['close'] * 100) if not ohlcv_df.empty else 0
                }
            }
            
            # --- STRICT CONFIDENCE INJECTION ---
            # Overwrite AI's "hallucinated" confidence with our mathematical weighted mean.
            try:
                import json
                c_data = json.loads(consensus_text)
                if isinstance(c_data, dict):
                    c_data['global_confidence'] = final_confidence
                    # Re-serialize with strict confidence
                    result_payload['global_consensus'] = json.dumps(c_data)
            except Exception:
                # If text wasn't JSON, we leave it as is, frontend handles fallback
                pass
            
            # Cache the result for PDF generation
            self.last_swarm_result[symbol] = result_payload
            return result_payload
            
        except Exception as e:
            print(f"Swarm Runtime Error: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    def _run_agents_sync(self, symbol, price, stats, ohlcv_df, orderbook, trades, agent_weights=None):
        """Synchronous agent execution with CONTEXT INJECTION."""
        print(f"🔄 [HIVE] SYNC EXECUTION STARTED. Received Weights: {agent_weights}")
        
        if agent_weights is None:
            print("⚠️ [HIVE] No weights provided to sync runner, using defaults (ALL ON).")
            agent_weights = {"scout": 1.0, "hunter": 1.0, "analyst": 1.0, "defender": 1.0, "strategist": 1.0, "sentinel": 1.0}
        import pandas as pd
        import numpy as np
        
        # --- CALCULATE CONTEXT (Global Indicators) ---
        sma_50 = 0
        rsi = 50
        change_24h = 0.0
        position_vs_sma = "UNKNOWN"
        sigma = 0
        vol_delta = 0.0
        
        if stats and 'math_proof' in stats:
             sigma = stats['math_proof']['dispersion']['std_dev_sigma']
        
        if ohlcv_df is not None and not ohlcv_df.empty:
            closes = ohlcv_df['close']
            if len(closes) > 50:
                sma_50 = closes.rolling(window=50).mean().iloc[-1]
            
            # Simple RSI Calc
            delta = closes.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi_series = 100 - (100 / (1 + rs))
            rsi = rsi_series.iloc[-1] if not pd.isna(rsi_series.iloc[-1]) else 50
            
            change_24h = ((closes.iloc[-1] - closes.iloc[0]) / closes.iloc[0]) * 100
            
            # Vol Delta
            last_vol = ohlcv_df.iloc[-1]['volume']
            avg_vol = ohlcv_df['volume'].mean()
            vol_delta = ((last_vol - avg_vol) / avg_vol) * 100 if avg_vol > 0 else 0
        
        position_vs_sma = "ABOVE" if price > sma_50 else "BELOW"
        
        # Context Injector
        context = {
            "sma_50": round(sma_50, 2),
            "rsi": round(rsi, 2),
            "change": round(change_24h, 2),
            "position_vs_sma": position_vs_sma,
            "sigma": round(sigma, 2),
            "vol_delta": round(vol_delta, 2)
        }

        results = []
        
        # --- SCOUT (Sync) ---
        if agent_weights.get('scout', 1.0) > 0:
            try:
                scout_result = self._scout_scan_sync(symbol, price, stats, ohlcv_df, context)
                results.append(scout_result)
            except Exception as e:
                results.append({"role": "SCOUT", "signal": "HOLD", "confidence": 50, "reasoning": f"Error: {e}"})
        
        # --- HUNTER (Sync) ---
        if agent_weights.get('hunter', 1.0) > 0:
            try:
                hunter_result = self._hunter_hunt_sync(symbol, price, orderbook, trades, context, ohlcv_df)
                results.append(hunter_result)
            except Exception as e:
                results.append({"role": "HUNTER", "signal": "HOLD", "confidence": 50, "reasoning": f"Error: {e}"})
        
        # --- ANALYST (Sync) ---
        if agent_weights.get('analyst', 1.0) > 0:
            try:
                analyst_result = self._analyst_analyze_sync(symbol, price, ohlcv_df, context)
                results.append(analyst_result)
            except Exception as e:
                results.append({"role": "ANALYST", "signal": "HOLD", "confidence": 50, "reasoning": f"Error: {e}"})
        
        # --- DEFENDER (Sync) ---
        if agent_weights.get('defender', 1.0) > 0:
            try:
                defender_result = self._defender_assess_sync(symbol, price, stats, context, ohlcv_df)
                results.append(defender_result)
            except Exception as e:
                results.append({"role": "DEFENDER", "signal": "HOLD", "confidence": 50, "risk_level": "UNKNOWN", "reasoning": f"Error: {e}"})

        # --- STRATEGIST (Sync) ---
        if agent_weights.get('strategist', 1.0) > 0:
            try:
                # Fetch D1 candles for Macro View (User Requirement)
                ohlcv_d1 = market_data.get_ohlcv(symbol, timeframe='1d', limit=50)
                strategist_result = self._strategist_plan_sync(symbol, ohlcv_d1, context)
                results.append(strategist_result)
            except Exception as e:
                results.append({"role": "STRATEGIST", "signal": "HOLD", "confidence": 40, "reasoning": f"Strategist Error: {e}"})

        # --- SENTINEL (Sync) ---
        if agent_weights.get('sentinel', 1.0) > 0:
            try:
                sentinel_result = self._sentinel_scan_sync(symbol, context)
                results.append(sentinel_result)
            except Exception as e:
                results.append({"role": "SENTINEL", "signal": "HOLD", "confidence": 0, "reasoning": f"Sentinel Error: {e}"})

        # --- GLOBAL CONSENSUS (Sync) ---
        consensus_text = "Consensus unavailable."
        try:
             from app.services.vertex_client import vertex_service
             consensus_text = vertex_service.generate_global_consensus_sync(results)
        except Exception as e:
             print(f"⚠️ [HIVE] Consensus Gen Failed: {e}")
        
        return {
            "swarm_breakdown": results,
            "global_consensus": consensus_text,
            "timestamp": context.get('timestamp')
        }
    
    def _scout_scan_sync(self, symbol, current_price, stats, ohlcv_df, context):
        """Synchronous Scout agent logic."""
        import pandas as pd
        import numpy as np
        
        if not stats or 'math_proof' not in stats:
            return {"role": "SCOUT", "id": "SCOUT_SYNC", "signal": "NEUTRAL", "confidence": 50, "reasoning": "Insufficient data", "source_data": {"price": current_price}}
        
        math_data = stats['math_proof']
        sigma = math_data['dispersion']['std_dev_sigma']
        mu = math_data['central_tendency']['mean_mu']
        
        z_score = (current_price - mu) / sigma if sigma > 0 else 0
        vol_delta = 0.0
        if ohlcv_df is not None and not ohlcv_df.empty:
            last_vol = ohlcv_df.iloc[-1]['volume']
            avg_vol = ohlcv_df['volume'].mean()
            vol_delta = ((last_vol - avg_vol) / avg_vol) * 100 if avg_vol > 0 else 0
        
        signal = "HOLD"
        confidence = 50
        
        if abs(z_score) > 2.5:
            signal = "SELL" if z_score > 0 else "BUY"
            confidence = 85
        elif vol_delta > 200:
            signal = "BUY" if current_price > mu else "SELL"
            confidence = 75
        
        from app.services.vertex_client import vertex_service
        indicators = {
            "symbol": symbol,
            "price": current_price,
            "z_score": round(z_score, 4),
            "sigma": round(sigma, 2),
            "vol_delta": round(vol_delta, 2),
            **context # Inject Global Context
        }
        
        ai_response = vertex_service.analyze_market_context_sync(symbol, current_price, ohlcv_df, indicators, "SCOUT")
        
        return {
            "role": "SCOUT",
            "id": "SCOUT_SYNC",
            "type": "QUANT",
            "signal": ai_response.get('signal', 'HOLD'),
            "confidence": ai_response.get('confidence', 50),
            "reasoning": ai_response.get('reasoning', "Neural Link Failed"),
            "source_data": indicators
        }
    
    def _hunter_hunt_sync(self, symbol, current_price, orderbook, trades, context, ohlcv_df=None):
        """Synchronous Hunter agent logic."""
        # Fallback if orderbook is empty (User Requirement)
        if not orderbook or (not orderbook.get('bids') and not orderbook.get('asks')):
            from app.services.vertex_client import vertex_service
            indicators = {
                "symbol": symbol,
                "price": current_price,
                "note": "ORDERBOOK_MISSING_FALLBACK_TO_VOLUME",
                **context
            }
            ai_response = vertex_service.analyze_market_context_sync(symbol, current_price, ohlcv_df, indicators, "HUNTER")
            return {
                "role": "HUNTER", "id": "HUNTER_SYNC", "type": "TRADER",
                "signal": ai_response.get('signal', 'HOLD'), "confidence": ai_response.get('confidence', 50),
                "reasoning": ai_response.get('reasoning', "Volume Analysis"), "source_data": indicators
            }
        
        bids = orderbook.get('bids', [])
        asks = orderbook.get('asks', [])
        
        # Helper to extract volume regardless of format (dict vs list)
        def get_vol(items):
            vol = 0
            for item in items[:5]:
                if isinstance(item, dict):
                    vol += item.get('quantity', 0) or item.get('amount', 0)
                elif isinstance(item, (list, tuple)) and len(item) > 1:
                    vol += item[1]
            return vol

        bid_vol = get_vol(bids)
        ask_vol = get_vol(asks)
        
        imbalance_ratio = bid_vol / ask_vol if ask_vol > 0 else 1
        
        signal = "HOLD"
        confidence = 60
        
        if imbalance_ratio > 1.5:
            signal = "BUY"
            confidence = 70
        elif imbalance_ratio < 0.67:
            signal = "SELL"
            confidence = 70
        
        from app.services.vertex_client import vertex_service
        indicators = {
            "symbol": symbol,
            "price": current_price,
            "bid_vol_top5": bid_vol,
            "ask_vol_top5": ask_vol,
            "imbalance_ratio": round(imbalance_ratio, 2),
            **context
        }
        
        ai_response = vertex_service.analyze_market_context_sync(symbol, current_price, ohlcv_df, indicators, "HUNTER")
        
        return {
            "role": "HUNTER",
            "id": "HUNTER_SYNC",
            "type": "TRADER",
            "signal": ai_response.get('signal', signal), # Use AI signal preferably
            "confidence": ai_response.get('confidence', confidence),
            "reasoning": ai_response.get('reasoning', "Neural Link Failed"),
            "source_data": indicators
        }
    
    def _analyst_analyze_sync(self, symbol, current_price, ohlcv_df, context):
        """Synchronous Analyst agent logic."""
        import numpy as np
        
        # Use context RSI if available to ensure consistency
        rsi = context.get('rsi', 50)
        
        signal = "HOLD"
        confidence = 55
        
        # Dynamic Confidence (User Requirement: 50% + RSI_Score/2)
        # We'll factor RSI distance from neutral into confidence
        rsi_dist = abs(rsi - 50)
        confidence = 50 + rsi_dist # e.g. RSI 70 -> dist 20 -> 50+20 = 70%. RSI 20 -> dist 30 -> 80%.
        
        if rsi > 70:
            signal = "SELL"
        elif rsi < 30:
            signal = "BUY"
        
        from app.services.vertex_client import vertex_service
        indicators = {
            "symbol": symbol,
            "price": current_price,
            "rsi": round(rsi, 2),
            **context
        }
        
        ai_response = vertex_service.analyze_market_context_sync(symbol, current_price, ohlcv_df, indicators, "ANALYST")
        
        return {
            "role": "ANALYST",
            "id": "ANALYST_SYNC",
            "type": "SENTIMENT",
            "signal": ai_response.get('signal', signal),
            "confidence": ai_response.get('confidence', confidence),
            "reasoning": ai_response.get('reasoning', "Neural Link Failed"),
            "source_data": indicators
        }
    
    def _defender_assess_sync(self, symbol, current_price, stats, context, ohlcv_df=None):
        """Synchronous Defender agent logic."""
        risk_level = "NORMAL"
        confidence = 60
        
        if stats and 'math_proof' in stats:
            sigma = stats['math_proof']['dispersion']['std_dev_sigma']
            mu = stats['math_proof']['central_tendency']['mean_mu']
            z_score = abs((current_price - mu) / sigma) if sigma > 0 else 0
            
            if z_score > 3:
                risk_level = "CRITICAL"
                confidence = 90
            elif z_score > 2:
                risk_level = "HIGH"
                confidence = 75
        
        from app.services.vertex_client import vertex_service
        indicators = {
            "symbol": symbol,
            "z_score": round(z_score, 4) if 'z_score' in locals() else 0,
            "risk_level_internal": risk_level,
            **context
        }
        
        ai_response = vertex_service.analyze_market_context_sync(symbol, current_price, ohlcv_df, indicators, "DEFENDER")
        
        return {
            "role": "DEFENDER",
            "id": "DEFENDER_SYNC",
            "type": "RISK",
            "signal": ai_response.get('signal', "HOLD"),
            "confidence": ai_response.get('confidence', confidence),
            "risk_level": risk_level,
            "reasoning": ai_response.get('reasoning', "Neural Link Failed"),
            "source_data": indicators
        }
    
    def _strategist_plan_sync(self, symbol, ohlcv_d1, context):
        """Synchronous Strategist agent logic (Macro/Daily)."""
        signal = "HOLD"
        confidence = 60
        trend = "NEUTRAL"
        
        if ohlcv_d1 is not None and not ohlcv_d1.empty:
            closes = ohlcv_d1['close']
            if len(closes) > 20:
                sma_20 = closes.rolling(window=20).mean().iloc[-1]
                current = closes.iloc[-1]
                if current > sma_20:
                    trend = "BULLISH"
                else:
                    trend = "BEARISH"
        
        reasoning = f"Macro Trend ({trend}). D1 Analysis initiated."
        
        from app.services.vertex_client import vertex_service
        indicators = {
            "symbol": symbol,
            "timeframe": "D1",
            "trend": trend,
            **context
        }
        
        ai_response = vertex_service.analyze_market_context_sync(symbol, 0, ohlcv_d1, indicators, "STRATEGIST") # Price irrelevant for strategist logic
        
        return {
            "role": "STRATEGIST",
            "id": "STRATEGIST_SYNC",
            "type": "MACRO",
            "signal": ai_response.get('signal', "HOLD"),
            "confidence": ai_response.get('confidence', confidence),
            "reasoning": ai_response.get('reasoning', "Neural Link Failed"),
            "source_data": indicators
        }

    def _sentinel_scan_sync(self, symbol, context):
        """Synchronous Sentinel using mocked or fetched news."""
        from app.services.vertex_client import vertex_service
        
        # In a full sync mode, we might skip heavy external API calls or do them lightly.
        # Here we rely on Vertex to hallucinate/fetch based on its internal knowledge or passed context
        
        indicators = {
            "symbol": symbol,
            "type": "GLOABL_SENTIMENT",
            **context
        }
        
        # We re-use Analyst prompt or a dedicated one if available. 
        # For now, let's treat it as a specialized Analyst for "Global/Social"
        ai_response = vertex_service.analyze_market_context_sync(symbol, 0, None, indicators, "ANALYST")
        
        # Rename role to SENTINEL in output
        return {
            "role": "SENTINEL",
            "id": "SENTINEL_SYNC",
            "type": "SOCIAL",
            "signal": ai_response.get("signal", "HOLD"),
            "confidence": ai_response.get("confidence", 50),
            "reasoning": "[SENTINEL] " + ai_response.get("reasoning", "Scanning social vectors..."),
            "source_data": indicators
        }

# Singleton - Instantiate but DO NOT START automatically
hive = HiveMind()
