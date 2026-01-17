import os
import logging
import json
import asyncio
import aiohttp
import xml.etree.ElementTree as ET
from datetime import datetime

from dotenv import load_dotenv

# Configure logger
logger = logging.getLogger(__name__)

# Ensure env is loaded
load_dotenv()

class VertexService:
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
             # Last resort fallback if env isn't set yet
             self.project_id = "gen-lang-client-0955370217"
        self.location = "us-central1"
        self.initialized = False
        self.model = None
        self.cache = {} 
        
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel
            
            # 1. Credential Check
            creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            
            # Optimization: Try to read project_id from the JSON key directly
            if creds_path and os.path.exists(creds_path):
                try:
                    with open(creds_path, 'r') as f:
                        key_data = json.load(f)
                        if 'project_id' in key_data:
                            self.project_id = key_data['project_id']
                            logger.info(f"Detected Project ID from Key: {self.project_id}")
                except Exception:
                    pass # Fail silently, fallback to env

            print(f"🧠 [HIVE] Vertex AI Connecting to {self.project_id}...")
            vertexai.init(project=self.project_id, location=self.location)

            models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest"]
            for model_name in models_to_try:
                try:
                    test_model = GenerativeModel(model_name)
                    self.model = test_model
                    self.initialized = True
                    print(f"✅ [HIVE] Vertex AI Initialized: {model_name}")
                    break
                except Exception as e:
                    logger.warning(f"Failed model check {model_name}: {e}")
            
            if not self.initialized:
                print("❌ [HIVE] Vertex AI: All model attempts failed. Service in Standby.")
            
        except ImportError:
            logger.error("Vertex AI Warning: google-cloud-aiplatform not installed. Service disabled.")
        except Exception as e:
            logger.error(f"Vertex AI Initialization Failed: {e}")

    async def _fetch_crypto_news(self):
        """Fetches real headlines from CoinDesk RSS for Analyst Agent"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://www.coindesk.com/arc/outboundfeeds/rss/", timeout=5) as response:
                    if response.status == 200:
                         content = await response.text()
                         root = ET.fromstring(content)
                         headlines = []
                         for item in root.findall('.//item')[:5]:
                             title = item.find('title').text
                             headlines.append(f"- {title}")
                         return "\n".join(headlines)
        except Exception as e:
            logger.error(f"News Fetch Failed: {e}")
            return "Market news unavailable. Assume neutral context."
        return "No significant news found."

    def _generate_sync(self, prompt: str) -> str:
        """
        Internal synchronous generation to be run in a thread executor.
        """
        if not self.model:
            raise Exception("Vertex Model not initialized")
            
        response = self.model.generate_content(prompt)
        return response.text

    def _clean_json(self, text: str) -> str:
        """Extracts JSON from text, handling markdown and leading/trailing fluff."""
        text = text.strip()
        # Remove markdown code blocks if present
        if text.startswith("```"):
            lines = text.split('\n')
            if len(lines) > 1:
                # Remove first line (```json or ```) and last line (```)
                text = "\n".join(lines[1:-1])
        text = text.strip()
        if text.endswith("```"):
            text = text[:-3].strip()

        if "{" in text and "}" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            return text[start:end]
        
        # Fallback: If no JSON found, return a valid JSON error structure
        # ensuring the frontend never crashes on "Agenci..." text.
        import json
        return json.dumps({
            "summary": "AI Output Invalid: " + text[:50] + "...", 
            "verdict": "HOLD"
        })

    async def analyze_market_context(self, indicators: dict, agent_type: str) -> str:
        """
        Generates professional market analysis using Vertex AI.
        STRICT MODE: No caching, no fallbacks, real-time generation only.
        """
        if not self.initialized:
            # STRICT ERROR - User wants to know if keys are missing
            return "VERTEX AI ERROR: Service not initialized. Check server logs/credentials."

        symbol = indicators.get("symbol", "BTC/USDT")
        
        # 1. Add TIMESTAMP to force uniqueness and prevent caching (User Requirement)
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 2. Build Prompt based on Persona
        sys_instruction = "SYSTEM: Respond STRICTLY in ENGLISH. Do not use any other language. Use professional Wall Street financial terminology."
        prompt_intro = f"{sys_instruction}\nCurrent time: {current_time_str}. You are an AI crypto trading expert."
        prompt = ""
        
        if agent_type == "SCOUT":
            # PURE MATH
            prompt = f"""
            {sys_instruction}
            
            Role: Quantitative Analyst (Scout).
            Task: Analyze raw data for {symbol}. Provide ONLY facts based on numbers. No fluff.
            
            Data:
            - Price: {indicators.get('price')}
            - Z-Score: {indicators.get('z_score')}
            - Volatility (Sigma): {indicators.get('sigma')}
            - Volume Delta: {indicators.get('vol_delta')}%
            
            Format: Short, technical sentences. State exact Z-Score deviation.
            """
            
        elif agent_type == "HUNTER":
            # TRADER / ORDER BOOK
            prompt = f"""
            {sys_instruction}
            
            Role: High-frequency Trader (Hunter).
            Task: Analyze order book liquidity. Identify walls and pressure.
            
            Data:
            - Bid Volume (top 5): {indicators.get('bid_vol_top5')}
            - Ask Volume (top 5): {indicators.get('ask_vol_top5')}
            - Imbalance Ratio: {indicators.get('imbalance_ratio')}x
            
            Format: Aggressive trading jargon. 'Buy wall detected', 'Sell pressure', 'Liquidity hunt'.
            """
            
        elif agent_type == "ANALYST":
            # NEWS / SENTIMENT
            headlines = await self._fetch_crypto_news()
            prompt = f"""
            {sys_instruction}
            
            Role: Market Analyst (Psychologist).
            Task: Determine market sentiment based on technical indicators and LATEST HEADLINES.
            
            Technical: RSI = {indicators.get('rsi')}
            
            LATEST HEADLINES:
            {headlines}
            
            Format: Professional commentary. Quote specific headline if relevant. Translate any non-English headlines to English. Gauge FOMO/Fear.
            """
        
        elif agent_type == "DEFENDER":
            prompt = f"""
            {sys_instruction}
            
            Role: Risk Manager (Defender).
            Task: Protect capital. Identify potential crashes or liquidation risks.
            
            Data:
            - Current Price: {indicators.get('price')}
            - ATR: {indicators.get('atr')}
            - Distance from ATH: {indicators.get('dist_ath')}%
            
            Format: Warning, terse. Focus on preservation.
            """
        
        elif agent_type == "STRATEGIST":
            prompt = f"""
            {sys_instruction}
            
            Role: Macro Strategist.
            Task: Provide long-term forecast based on D1 trends.
            
            Data:
            - Trend D1: {indicators.get('d1_trend')}
            - Macro Context: {indicators.get('macro_view')}
            
            Format: Strategic, forward-looking.
            """
            
        else:
            prompt = f"{sys_instruction} Role: Default Agent. Analyze {symbol} at price {indicators.get('price')}."

        # 3. Call Vertex AI
        try:
            # We wrap the sync call in a thread for async compatibility
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self._generate_sync, prompt)
            
            cleaned_text = response.replace("*", "").strip()
            
            # NO MOCK CACHING - User demands live generation every time
            
            return cleaned_text
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Vertex Generation Error: {error_str}")
            
            # STRICT ERRORS ONLY - DO NOT RETURN FAKE ANALYSIS
            if "Consumer invalid" in error_str or "Permission denied" in error_str:
                return "AI AUTH ERROR: Check Google Cloud Project ID & Credentials."
            
            if "Quota exceeded" in error_str:
                return f"AI QUOTA EXCEEDED: Vertex AI rate limit reached. ([{current_time_str}])"
            
            # Raw error for transparency
            return f"VERTEX ERROR: {error_str}"

    def analyze_market_context_sync(self, symbol: str, price: float, ohlcv_df, extra_data: dict, agent_role: str) -> dict:
        """
        New Decision Engine: Advanced Data -> Vertex AI -> JSON Verdict.
        """
        if not self.initialized:
             return {"signal": "HOLD", "confidence": 0, "reasoning": "Vertex AI Init Failed."}
             
        # 1. DATA FEEDER (Calculate Advanced Indicators)
        agent_data = self._get_agent_data(ohlcv_df, agent_role, extra_data)
        
        # 2. PROMPT ENGINEERING (JSON Enforced)
        system_instruction = f"""
        SYSTEM: Respond STRICTLY in ENGLISH. Do not use any other language. Use professional Wall Street financial terminology.
        
        You are {agent_role}. Your task is to analyze {symbol} (Price: {price}).
        You receive advanced technical data: {agent_data}.
        
        DECISION RULES:
        1. Analyze data based on your specialization.
        2. Determine SIGNAL (BUY/SELL/HOLD).
        3. Determine CONFIDENCE (0-100%) - be strict, no high scores without strong evidence.
        4. Write REASONING - concise, data-driven. Max 2-3 sentences.
        
        REQUIRED RESPONSE FORMAT (JSON):
        {{
            "signal": "BUY" | "SELL" | "HOLD",
            "confidence": <int>,
            "reasoning": "<string>"
        }}
        You must respond strictly in JSON format. Do not use Markdown code blocks.
        """
        
        try:
            raw_response = self._generate_sync(system_instruction)
            cleaned_json = self._clean_json(raw_response)
            import json
            parsed_response = json.loads(cleaned_json)
            return parsed_response
            
        except Exception as e:
            msg = f"Neural Link Error for {agent_role}: {e}"
            print(f"⚠️ [VERTEX] JSON Parse Error: {e}")
            return {"signal": "HOLD", "confidence": 0, "reasoning": "AI Parsing Error."}

    def _get_agent_data(self, df, role, extra_data):
        """Calculates dedicated indicators based on role."""
        
        data_summary = {}
        
        if df is None or df.empty:
             if role in ["SENTINEL", "ANALYST"]:
                 return "Sentiment / News Focus. No distinct Technical Data."
             return "No OHLCV Data Available."
             
        # Ensure TA extension is ready (usually auto-loaded by import but sometimes needs explicit init)
        # Assuming df has 'close', 'high', 'low', 'volume'
        
        if role == "SCOUT":
            # RSI, MACD, Bollinger, EMA
            rsi = df.ta.rsi(length=14).iloc[-1] if len(df) > 14 else 50
            
            macd = df.ta.macd()
            # pandas_ta returns columns like MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9
            # We use column 0 (MACD line)
            macd_val = macd.iloc[:, 0].iloc[-1] if not macd.empty else 0
            
            bb = df.ta.bbands(length=20)
            # Safe access for %B (usually column index 4 for bbands, but we try by name or index)
            bb_p = 0.5
            if not bb.empty:
                # Try standard name 'BBP_20_2.0'
                if 'BBP_20_2.0' in bb.columns:
                     bb_p = bb['BBP_20_2.0'].iloc[-1]
                # Fallback to last column (usually %B or bandwidth)
                else:
                     bb_p = bb.iloc[:, -1].iloc[-1]

            ema_200 = df.ta.ema(length=200).iloc[-1] if len(df) > 200 else 0
            
            data_summary = {
                "RSI_14": round(rsi, 2),
                "MACD": round(macd_val, 2),
                "Bollinger_%B": round(bb_p, 2),
                "EMA_200": round(ema_200, 2),
                "Z_Score": extra_data.get('z_score', 'N/A')
            }
            
        elif role == "HUNTER":
            # Volume Ratio, Imbalance, Money Flow
            avg_vol = df['volume'].rolling(30).mean().iloc[-1]
            curr_vol = df['volume'].iloc[-1]
            vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 1
            
            # MFI (Money Flow Index) if available or manual
            mfi = df.ta.mfi().iloc[-1] if len(df) > 14 else 50
            
            imbalance = extra_data.get('imbalance_ratio', 'N/A')
            bid_vol = extra_data.get('bid_vol_top5', 0)
            ask_vol = extra_data.get('ask_vol_top5', 0)
            
            data_summary = {
                "Volume_Ratio_24h_vs_30d": round(vol_ratio, 2),
                "Money_Flow_Index": round(mfi, 2),
                "OrderBook_Imbalance": imbalance,
                "Bid_Pressure": bid_vol,
                "Ask_Pressure": ask_vol
            }
            
        elif role == "DEFENDER":
            # ATR, Volatility
            atr = df.ta.atr(length=14).iloc[-1] if len(df) > 14 else 0
            # Distance from ATH (Approx max of period)
            period_max = df['high'].max()
            current = df['close'].iloc[-1]
            dist_ath = ((current - period_max) / period_max) * 100
            
            data_summary = {
                "ATR": round(atr, 2),
                "Distance_From_High": round(dist_ath, 2),
                "Volatility_Sigma": extra_data.get('sigma', 'N/A'),
                "Risk_Level_Internal": extra_data.get('risk_level_internal', 'UNKNOWN')
            }
            
        elif role == "ANALYST":
            # Sentiment / Price Action
            sma_50 = df.ta.sma(length=50).iloc[-1] if len(df) > 50 else 0
            current = df['close'].iloc[-1]
            trend = "BULLISH" if current > sma_50 else "BEARISH"
            change = extra_data.get('change', 0)
            
            data_summary = {
                "Price_vs_SMA50": trend,
                "Change_24h": f"{change}%",
                "Market_Momentum": "Positive" if change > 0 else "Negative"
            }
            
        elif role == "STRATEGIST":
             # Use generic or passed D1 trend
             data_summary = {
                 "D1_Trend": extra_data.get('trend', 'UNKNOWN'),
                 "Macro_View": "Long_Term_Focus"
             }
             
        return str(data_summary)

    async def generate_global_consensus(self, agents_results: list) -> str:
        """
        Synthesizes a global consensus from agent reports.
        """
        if not self.initialized: return "Consensus System Offline."
        
        agents_text = "\n".join([f"- {a['role']}: {a['signal']} (Conf: {a['confidence']}%) - {a['reasoning']}" for a in agents_results])
        
        prompt = f"""
        SYSTEM: Respond STRICTLY in ENGLISH. Do not use any other language. Use professional Wall Street financial terminology.
        REPORTS:
        {agents_text}

        TASK:
        You are the Head of Analytics. Summarize the reports from your agents. Write a cohesive 'Executive Summary' strictly in ENGLISH.
        
        OUTPUT JSON:
        {{
            "summary": "Summary content in English...",
            "verdict": "BUY" | "SELL" | "HOLD" | "STRONG BUY" | "STRONG SELL"
        }}
        You must respond strictly in JSON format. Do not use Markdown code blocks.
        """
        
        try:
            # Sync call in executor because vertex sync is blocking
            loop = asyncio.get_event_loop()
            raw_response = await loop.run_in_executor(None, self._generate_sync, prompt)
            
             # Clean Markdown/Fluff
            clean_resp = self._clean_json(raw_response)
            
            return clean_resp

        except Exception as e:
            logger.error(f"Consensus Gen Error: {e}")
            return '{"summary": "Error generating consensus.", "verdict": "HOLD"}'

    def generate_global_consensus_sync(self, agents_results: list) -> str:
         """
         Synchronous version of global consensus generation.
         """
         if not self.initialized: return '{"summary": "System Offline", "verdict": "HOLD"}'
         
         agents_text = "\n".join([f"- {a.get('role','UNKNOWN')}: {a.get('signal','HOLD')} (Conf: {a.get('confidence',0)}%) - {a.get('reasoning','')}" for a in agents_results])

         prompt = f"""
        SYSTEM: Respond STRICTLY in ENGLISH. Do not use any other language. Use professional Wall Street financial terminology.
        You are the Hive Leader (Hive Mind). Input: Reports from all agents. 
        
        REPORTS:
        {agents_text}

        TASK:
        You are the Head of Analytics. Summarize the reports from your agents. Write a cohesive 'Executive Summary' strictly in ENGLISH.
        
        OUTPUT JSON:
        {{
            "summary": "Summary text in English...",
            "verdict": "BUY" | "SELL" | "HOLD" | "STRONG BUY" | "STRONG SELL"
        }}
        You must respond strictly in JSON format. Do not use Markdown code blocks.
        """
         try:
             raw_response = self._generate_sync(prompt)
             return self._clean_json(raw_response)
         except Exception as e:
             print(f"Consensus Error: {e}")
             return '{"summary": "Consensus Unavailable", "verdict": "UNKNOWN"}'

# Create singleton instance
vertex_service = VertexService()
