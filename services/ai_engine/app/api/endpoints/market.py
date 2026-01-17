from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.services.screener_service import ScreenerService
import numpy as np

router = APIRouter()

@router.get("/screener", response_model=List[Dict[str, Any]])
async def get_screener_data():
    """
    Get enriched market screener data with Top 20 cryptocurrencies,
    sparkline history, and AI-simulated Quant Scores.
    """
    service = ScreenerService()
    try:
        data = await service.get_top_cryptos(limit=20)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.exchange.close()


@router.get("/risk-metrics", response_model=Dict[str, Any])
async def get_risk_metrics():
    """
    Calculate real-time market risk metrics from live market data.
    All values are normalized to 0-100 scale.
    
    Metrics:
    - Volatility: Based on 24h price range (high-low)/price
    - Volume: Normalized volume score across top assets
    - Momentum: Based on aggregate 24h price changes
    - Liquidity: Inverse of spread/volatility (higher = more liquid)
    - Market Stress: Composite indicator of market tension
    """
    service = ScreenerService()
    try:
        data = await service.get_top_cryptos(limit=10)
        
        if not data:
            return {
                "volatility": 50,
                "volume": 50,
                "momentum": 50,
                "liquidity": 50,
                "stress": 50,
                "avg_30d": {
                    "volatility": 45,
                    "volume": 55,
                    "momentum": 50,
                    "liquidity": 60,
                    "stress": 45
                }
            }
        
        # Calculate Volatility (0-100)
        # Using (high_24h - low_24h) / price as volatility proxy
        volatilities = []
        for coin in data:
            price = coin.get('price', 0)
            high = coin.get('high_24h', price)
            low = coin.get('low_24h', price)
            if price > 0:
                vol = ((high - low) / price) * 100
                volatilities.append(min(vol * 10, 100))  # Scale and cap at 100
        
        avg_volatility = np.mean(volatilities) if volatilities else 50
        
        # Calculate Volume Score (0-100)
        # Normalize volumes relative to BTC volume
        volumes = [coin.get('volume_usdt', 0) for coin in data]
        max_vol = max(volumes) if volumes else 1
        volume_score = np.mean([min((v / max_vol) * 100, 100) for v in volumes]) if volumes else 50
        
        # Calculate Momentum (0-100)
        # Based on 24h changes, 50 = neutral, >50 = bullish, <50 = bearish
        changes = [coin.get('change_24h', 0) for coin in data]
        avg_change = np.mean(changes) if changes else 0
        # Map -10% to +10% range to 0-100 scale
        momentum = 50 + (avg_change * 5)  # +1% = 55, -1% = 45
        momentum = max(0, min(100, momentum))
        
        # Calculate Liquidity Score (0-100)
        # Higher volume + lower volatility = higher liquidity
        liquidity = 100 - (avg_volatility * 0.3) + (volume_score * 0.3)
        liquidity = max(0, min(100, liquidity))
        
        # Calculate Market Stress (0-100)
        # High volatility + negative momentum + low liquidity = high stress
        stress = (avg_volatility * 0.4) + ((100 - momentum) * 0.3) + ((100 - liquidity) * 0.3)
        stress = max(0, min(100, stress))
        
        # 30-day average (simulated based on current with slight offset)
        # In production, this would come from historical data
        avg_30d = {
            "volatility": max(0, min(100, avg_volatility * 0.85)),  # Usually less volatile
            "volume": max(0, min(100, volume_score * 1.05)),       # Slightly higher avg volume
            "momentum": 50,                                         # Neutral over 30 days
            "liquidity": max(0, min(100, liquidity * 1.1)),        # Higher avg liquidity
            "stress": max(0, min(100, stress * 0.9))               # Lower avg stress
        }
        
        return {
            "volatility": round(avg_volatility, 1),
            "volume": round(volume_score, 1),
            "momentum": round(momentum, 1),
            "liquidity": round(liquidity, 1),
            "stress": round(stress, 1),
            "avg_30d": avg_30d
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.exchange.close()
