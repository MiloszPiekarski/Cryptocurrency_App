from web3 import Web3

# Using Ankr Public RPC for "Zero Setup" Professional Access
RPC_URL = "https://rpc.ankr.com/eth"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

def get_latest_block():
    try:
        if w3.is_connected():
            block = w3.eth.get_block('latest')
            return {
                "number": block.number,
                "timestamp": block.timestamp,
                "transactions_count": len(block.transactions)
            }
        return None
    except Exception as e:
        # print(f"Blockchain Error: {e}") # Silent fail for MVP if network issue
        return None

def check_whale_movements(min_value_eth=50):
    # Scan latest block for big tx
    # Implementation of "Whale profiling" (Phase 4, Point 18)
    whale_txs = []
    try:
        if not w3.is_connected(): return []
        
        block = w3.eth.get_block('latest', full_transactions=True)
        for tx in block.transactions:
             value_eth = float(w3.from_wei(tx.value, 'ether'))
             if value_eth >= min_value_eth:
                 whale_txs.append({
                     "hash": tx.hash.hex(),
                     "from": tx['from'],
                     "to": tx['to'],
                     "value": value_eth
                 })
    except Exception as e:
        # print(f"Whale Scan Error: {e}")
        pass
    return whale_txs[:5] # Return top 5
