import json
import click
import os
import asyncio
import sqlite3
import requests
from cyberchipped import AI, SQLiteDatabase
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.system_program import TransferParams, transfer
from solana.rpc.api import Client

DB_PATH = "swarm.db"


def initialize_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS keypairs (
                pubkey TEXT PRIMARY KEY,
                secret_key BLOB
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                address TEXT PRIMARY KEY,
                name TEXT,
                symbol TEXT,
                decimals INTEGER,
                daily_volume REAL,
                created_at TEXT,
                full_data JSON
            )
        """)
        conn.commit()


def fetch_and_store_tokens():
    url = "https://tokens.jup.ag/tokens?tags=verified"
    response = requests.get(url)
    if response.status_code == 200:
        tokens = response.json()
        store_tokens(tokens)
        print(f"Fetched and stored {len(tokens)} tokens.")
    else:
        print(f"Failed to fetch tokens. Status code: {response.status_code}")


def get_token_info(token_query):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            """
            SELECT address, name, symbol
            FROM tokens
            WHERE name LIKE ? OR symbol LIKE ?
            LIMIT 1
        """,
            (f"%{token_query}%", f"%{token_query}%"),
        )
        result = cursor.fetchone()
        if result:
            return {
                "address": result[0],
                "name": result[1],
                "symbol": result[2]
            }
        return None


def store_tokens(tokens):
    with sqlite3.connect(DB_PATH) as conn:
        for token in tokens:
            conn.execute(
                """
                INSERT OR REPLACE INTO tokens 
                (address, name, symbol, decimals, daily_volume, created_at, full_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    token["address"],
                    token["name"],
                    token["symbol"],
                    token["decimals"],
                    token.get("daily_volume"),
                    token.get("created_at"),
                    json.dumps(token),
                ),
            )
        conn.commit()


def store_keypair(pubkey: str, secret_key: bytes):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO keypairs (pubkey, secret_key) VALUES (?, ?)",
            (pubkey, secret_key),
        )
        conn.commit()


def get_keypairs():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT pubkey, secret_key FROM keypairs")
        return cursor.fetchall()


async def main(network: str, rpc: str):
    database = SQLiteDatabase(DB_PATH)
    initialize_db()
    fetch_and_store_tokens()  # Fetch and store tokens when initializing

    http_client = None
    if network == "mainnet-beta":
        http_client = Client("https://api.mainnet-beta.solana.com")
    if network == "devnet":
        http_client = Client("https://api.devnet.solana.com")
    if rpc is not None:
        http_client = Client(rpc)
    stored_keypairs = get_keypairs()
    keypairs = [Keypair.from_bytes(secret_key) for _, secret_key in stored_keypairs]

    ai = AI(
        api_key=os.getenv("OPENAI_API_KEY"),
        name="Solana Swarm AI",
        instructions="""
                You are an AI Agent on the command-line that can perform actions on the Solana blockchain.
                IMPORTANT: You do not use markdown in your responses.
                IMPORTANT: Show the text responses and explain the error messages to the user.
                IMPORTANT: Do not cache errors always retry the functions.
                IMPORTANT: Only pass the account numbers not public keys to the functions.
                CRITICAL: Only use the `map_token_name_to_info` function to get token addresses (address).
                CRITICAL: Only use the `get_ohlc_data` function to get token OHLC data.
                CRITICAL: Only use the `get_trading_info` function to get token trading information.
            """,
        database=database,
    )

    @ai.add_tool
    def list_wallets() -> str:
        try:
            wallets = [
                f"{index+1}: {keypair.pubkey()}"
                for index, keypair in enumerate(keypairs)
            ]
            return "\n".join(wallets)
        except Exception as e:
            return f"Error: {e}"

    @ai.add_tool
    def create_account() -> str:
        try:
            keypair = Keypair()
            keypairs.append(keypair)
            store_keypair(str(keypair.pubkey()), bytes(keypair))
            return f"Created new account: {len(keypairs)} with public key: {keypair.pubkey()}"
        except Exception as e:
            return f"Error: {e}"

    @ai.add_tool
    def get_balance(account_number: str) -> str:
        try:
            account_number = int(account_number)
            url = f"https://api.vybenetwork.xyz/account/token-balance/{keypairs[account_number - 1].pubkey()}"

            headers = {
                "accept": "application/json",
                "X-API-KEY": os.getenv("VYBE_API_KEY"),
            }

            response = requests.get(url, headers=headers)

            return f"Data: {response.json()}"
        except Exception as e:
            return f"Error: {e}"

    @ai.add_tool
    def transfer_sol(
        from_account_number: str, to_account_number: str, sol_amount: str
    ) -> str:
        try:
            from_account_number = int(from_account_number)
            to_account_number = int(to_account_number)
            sol_amount = float(sol_amount)
            instruction = transfer(
                TransferParams(
                    from_pubkey=keypairs[from_account_number - 1].pubkey(),
                    to_pubkey=keypairs[to_account_number - 1].pubkey(),
                    lamports=int(sol_amount * 10**9),
                )
            )
            recent_blockhash = http_client.get_latest_blockhash().value.blockhash
            txn = Transaction.new_signed_with_payer(
                [instruction],
                payer=keypairs[from_account_number - 1].pubkey(),
                signing_keypairs=[keypairs[from_account_number - 1]],
                recent_blockhash=recent_blockhash,
            )
            signature = http_client.send_transaction(txn).value

            return f"Transferred {sol_amount} SOL from {keypairs[from_account_number-1].pubkey()} to {keypairs[to_account_number-1].pubkey()} with transaction ID: {signature}"
        except Exception as e:
            return f"Error: {e}"

    @ai.add_tool
    def map_token_name_to_info(token_query: str) -> str:
        try:
            token_info = get_token_info(token_query)
            if token_info:
                return f"Token Information:\nName: {token_info['name']}\nSymbol: {token_info['symbol']}\nAddress: {token_info['address']}"
            else:
                return f"No token found matching '{token_query}'"
        except Exception as e:
            return f"Error: {e}"

    @ai.add_tool
    def get_trading_info(token_query: str) -> str:
        try:
            token_info = get_token_info(token_query)
            if token_info:
                token_address = token_info["address"]
                url = f"https://api.vybenetwork.xyz/token/{token_address}"

                headers = {
                    "accept": "application/json",
                    "X-API-KEY": os.getenv("VYBE_API_KEY"),
                }

                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    return f"Token Information:\nName: {token_info['name']}\nSymbol: {token_info['symbol']}\nAddress: {token_info['address']}\nData: {data}"
                else:
                    return f"Failed to fetch token price. Status code: {response.status_code}"
        except Exception as e:
            return f"Error: {e}"
        
    
    @ai.add_tool
    def get_ohlc_data(token_query: str) -> str:
        try:
            token_info = get_token_info(token_query)
            if token_info:
                token_address = token_info["address"]
                url = f"https://api.vybenetwork.xyz/price/{token_address}/token-quote-ohlcv"

                headers = {
                    "accept": "application/json",
                    "X-API-KEY": os.getenv("VYBE_API_KEY"),
                }

                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    return f"Token Information:\nName: {token_info['name']}\nSymbol: {token_info['symbol']}\nAddress: {token_info['address']}\nData: ${data['data'][0]}"
                else:
                    return f"Failed to fetch OHLC Data. Status code: {response.status_code}"
        except Exception as e:
            return f"Error: {e}"

    print("Welcome to the Solana Swarm AI. Type 'exit' to quit.")

    async with ai as ai_instance:
        while True:
            user_input = input("You: ").strip()

            if user_input.lower() == "exit":
                print("Goodbye!")
                break

            print("AI: ", end="", flush=True)
            async for chunk in ai_instance.text("1", user_input):
                print(chunk, end="", flush=True)
            print()  # New line after the complete response


@click.command()
@click.option(
    "--network",
    required=False,
    default="mainnet-beta",
    type=click.Choice(["devnet", "mainnet-beta"]),
    help="Solana Network to connect",
)
@click.option("--rpc", required=False, help="Custom RPC URL")
def cli(network: str = "mainnet-beta", rpc: str = None):
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set the OPENAI_API_KEY environment variable.")
    if not os.getenv("VYBE_API_KEY"):
        print("Please set the VYBE_API_KEY environment variable.")
    asyncio.run(main(network, rpc))


if __name__ == "__main__":
    cli()
