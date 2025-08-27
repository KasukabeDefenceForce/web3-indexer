import os
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()
ALCHEMY_KEY = os.getenv('ALCHEMY_KEY')
alchemy_url = f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}"
w3 = Web3(Web3.HTTPProvider(alchemy_url))

print(f"Connection Successful: {w3.is_connected()}")


PROVIDER_ADDRESS = "0x2f39d218133AFaB8F2B819B1066c7E434Ad94E9e"

PROVIDER_ABI = json.loads("""
[
    {
        "inputs": [],
        "name": "getPool",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]
""")


provider_contract = w3.eth.contract(address=PROVIDER_ADDRESS, abi=PROVIDER_ABI)

pool_address = provider_contract.functions.getPool().call()
AAVE_POOL_ADDRESS = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"

print(f"Successfully called the contract.")
print(f"The Aave V3 Pool address is: {pool_address}")


POOL_ABI = json.loads("""
[
    {
        "anonymous": false,
        "inputs": [
            { "indexed": true, "internalType": "address", "name": "collateralAsset", "type": "address" },
            { "indexed": true, "internalType": "address", "name": "debtAsset", "type": "address" },
            { "indexed": true, "internalType": "address", "name": "user", "type": "address" },
            { "indexed": false, "internalType": "uint256", "name": "debtToCover", "type": "uint256" },
            { "indexed": false, "internalType": "uint256", "name": "liquidatedCollateralAmount", "type": "uint256" },
            { "indexed": false, "internalType": "address", "name": "liquidator", "type": "address" },
            { "indexed": false, "internalType": "bool", "name": "receiveAToken", "type": "bool" }
        ],
        "name": "LiquidationCall",
        "type": "event"
    }
]
""")