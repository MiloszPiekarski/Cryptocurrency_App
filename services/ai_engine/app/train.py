import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
import os
from app.models.lstm_model import CryptoLSTM

from app.services.market_data import market_data

# Use Real Data
def generate_mock_data(days=60):
    # This function is deprecated but kept for fallback
    # In production flow, we use market_data.get_ohlcv directly
    pass

def train_model(symbol="BTC/USDT", epochs=20):
    print(f"🚀 Starting REAL training for {symbol} using Binance Data...")
    
    # 1. Fetch Real Data
    # Fetch 1000 candles (approx 40 days of hourly data)
    limit = 1000
    df = market_data.get_ohlcv(symbol, timeframe='1h', limit=limit)
    
    if df.empty:
        print("❌ Failed to fetch data. Aborting training.")
        return {"status": "error", "message": "No data"}
        
    print(f"📊 Downloaded {len(df)} candles. Close price: {df['close'].iloc[-1]}")

    data = df['close'].values.astype(float)
    
    # Normalize
    mean = np.mean(data)
    std = np.std(data)
    data_norm = (data - mean) / std
    
    # Create Sequences
    seq_length = 10
    X = []
    y = []
    for i in range(len(data_norm) - seq_length):
        X.append(data_norm[i:i+seq_length])
        y.append(data_norm[i+seq_length])
        
    X = torch.tensor(X, dtype=torch.float32).unsqueeze(-1) # [Batch, Seq, Features]
    y = torch.tensor(y, dtype=torch.float32).unsqueeze(-1)
    
    # 2. Init Model
    model = CryptoLSTM(input_size=1, hidden_size=32, num_layers=1, output_size=1)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    
    # 3. Training Loop
    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(X)
        loss = criterion(outputs, y)
        loss.backward()
        optimizer.step()
        
        if (epoch+1) % 5 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.6f}")
            
    # 4. Save Model
    save_dir = "data/models"
    os.makedirs(save_dir, exist_ok=True)
    save_path = f"{save_dir}/{symbol.replace('/', '_')}_lstm.pth"
    torch.save(model.state_dict(), save_path)
    
    print(f"✅ Model saved to {save_path}")
    
    return {
        "status": "success",
        "final_loss": loss.item(),
        "path": save_path
    }

if __name__ == "__main__":
    train_model()
