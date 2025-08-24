from web3 import Web3

# 1. SETUP
alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/5nb2U_PSg6B9kzJuCdphk"

# 2. CONNECT
w3 = Web3(Web3.HTTPProvider(alchemy_url))
print(f"Connection Successful: {w3.is_connected()}")

contract_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
transfer_event_topic = w3.keccak(text="Transfer(address,address,uint256)").hex()


target_block = 18000000

print(f"\nScanning block #{target_block} for USDC Transfer events...")


event_filter = {
    "fromBlock": target_block,
    "toBlock": target_block,
    "address": contract_address,
    "topics": [transfer_event_topic]
}

logs = w3.eth.get_logs(event_filter)

print(f"Found {len(logs)} matching events in this block.")
print("Raw log data:")
for log in logs:
    print(log)