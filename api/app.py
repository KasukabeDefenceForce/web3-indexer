from flask import Flask, jsonify
from web3 import Web3
import logging
import os
from flask_cors import CORS
import json
from dotenv import load_dotenv

load_dotenv()
ALCHEMY_KEY=os.environ['ALCHEMY_KEY']
FRONTEND_URLS=os.environ['FRONTEND_URLS']
allowed_origins = FRONTEND_URLS.split(',')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
)

app = Flask(__name__)
CORS(app, origins=allowed_origins)
ALCHEMY_URL = f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}"
w3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))

AAVE_POOL_ADDRESS = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
AAVE_POOL_ABI = json.loads("""[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"collateralAsset","type":"address"},{"indexed":true,"internalType":"address","name":"debtAsset","type":"address"},{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"debtToCover","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"liquidatedCollateralAmount","type":"uint256"},{"indexed":false,"internalType":"address","name":"liquidator","type":"address"},{"indexed":false,"internalType":"bool","name":"receiveAToken","type":"bool"}],"name":"LiquidationCall","type":"event"}]""")
aave_pool_contract = w3.eth.contract(address=AAVE_POOL_ADDRESS, abi=AAVE_POOL_ABI)

ORACLE_ADDRESS = "0x54586bE62E3c3580375aE3723C145253060Ca0C2"
ORACLE_ABI = json.loads("""[{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getAssetPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]""")
oracle_contract = w3.eth.contract(address=ORACLE_ADDRESS, abi=ORACLE_ABI)


@app.route("/transfers")
def transfers():
    if not w3.is_connected():
        logging.error("Failed to connect to the blockchain.")
        return jsonify({"error": "Cannot connect to the blockchain"}), 500
    logging.info(f"Connection Successful: {w3.is_connected()}")

    contract_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    transfer_event_topic = w3.keccak(text="Transfer(address,address,uint256)").hex()


    latest_block = w3.eth.block_number


    logging.info(f"\nScanning block #{latest_block} for USDC Transfer events...")


    event_filter = {
        "fromBlock": latest_block - 5,
        "toBlock": latest_block,
        "address": contract_address,
        "topics": [transfer_event_topic]
    }

    logs = w3.eth.get_logs(event_filter)

    logging.info(f"Found {len(logs)} matching events in this block.")
    transfers_list = []
    for log in logs:
        from_address = "0x" + log['topics'][1].hex()[-40:]
        to_address = "0x" + log['topics'][2].hex()[-40:]
        amount_raw = int(log['data'].hex(), 16)
        amount_friendly = amount_raw / (10 ** 6)
        
        transfers_list.append({
            "from": from_address,
            "to": to_address,
            "amount": amount_friendly,
            "blockNumber": log['blockNumber']
        })

    return jsonify({'data': transfers_list})

@app.route("/liquidations")
def liquidations():
    if not w3.is_connected():
        logging.error("Failed to connect to the blockchain.")
        return jsonify({"error": "Cannot connect to the blockchain"}), 500
    
    logging.info("Received a request for /liquidations")
    latest_block = w3.eth.block_number
    start_block = latest_block - 10
    logging.info(f"Scanning blocks {start_block} to {latest_block} for LiquidationCall events...")

    liquidation_event_topic = aave_pool_contract.events.LiquidationCall.get_topic()
    event_filter = {
        "fromBlock": start_block,
        "toBlock": latest_block,
        "address": AAVE_POOL_ADDRESS,
        "topics": [liquidation_event_topic]
    }
    logs = w3.eth.get_logs(event_filter)
    logging.info(f"Found {len(logs)} liquidation events in this block range.")

    liquidations_list = []
    for log in logs:
        event_data = aave_pool_contract.events.LiquidationCall().process_log(log)
        args = event_data['args']
        block_number = log['blockNumber']
        collateral_price_raw = oracle_contract.functions.getAssetPrice(args['collateralAsset']).call(block_identifier=block_number)
        debt_price_raw = oracle_contract.functions.getAssetPrice(args['debtAsset']).call(block_identifier=block_number)

        collateral_value_usd = (args['liquidatedCollateralAmount'] / 1e18) * (collateral_price_raw / 1e8)
        debt_value_usd = (args['debtToCover'] / 1e6) * (debt_price_raw / 1e8)

        liquidations_list.append({
            "user": args['user'],
            "liquidator": args['liquidator'],
            "collateralAsset": args['collateralAsset'],
            "debtAsset": args['debtAsset'],
            "collateralValueUSD": f"{collateral_value_usd:.2f}",
            "debtValueUSD": f"{debt_value_usd:.2f}",
            "blockNumber": block_number
        })
    return jsonify({'liquidations': liquidations_list})
