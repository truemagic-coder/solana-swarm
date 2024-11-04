from typing import List
import click
import os
import asyncio
from cyberchipped import AI, SQLiteDatabase
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.system_program import TransferParams, transfer
from solana.rpc.commitment import Confirmed
from solana.rpc.api import Client

async def main(network: str, rpc: str):

    database = SQLiteDatabase("swarm.db")
    http_client = None
    if network == "mainnet-beta":
        http_client = Client("https://api.mainnet-beta.solana.com")
    if network == "devnet":
        http_client = Client("https://api.devnet.solana.com")
    if rpc is not None:
        http_client = Client(rpc)
    keypairs : List[Keypair] = []
    
    ai = AI(
            api_key=os.getenv("OPENAI_API_KEY"),
            name="Solana Swarm AI",
            instructions="""
                You are an AI Agent that can perform actions on the Solana blockchain.
                Show the text responses and explain the error messages to the user.
                Do not cache errors always retry the functions.
                Only pass the account numbers not public keys to the functions.
            """,
            database=database,
        )
    
    @ai.add_tool
    def list_wallets() -> str:
        try:
            wallets = [f"{index+1}: {keypair.pubkey()}" for index, keypair in enumerate(keypairs)]
            return "\n".join(wallets)
        except Exception as e:
            return f"Error: {e}"
    
    @ai.add_tool
    def create_account() -> str:
        try:
            keypair = Keypair()
            keypairs.append(keypair)
            return f"Created new account: {len(keypairs)} with public key: {keypair.pubkey()}"
        except Exception as e:
            return f"Error: {e}"

    @ai.add_tool
    def get_balance(account_number: str) -> str:    
        try:
            account_number = int(account_number)
            balance = http_client.get_balance(pubkey=keypairs[account_number-1].pubkey(), commitment=Confirmed).value
            balance = balance / 10**9
            return f"Balance of {keypairs[account_number-1].pubkey()} is {balance} SOL"
        except Exception as e:
            return f"Error: {e}"

    @ai.add_tool
    def transfer_sol(from_account_number: str, to_account_number: str, sol_amount: str) -> str:
        try:   
            from_account_number = int(from_account_number)
            to_account_number = int(to_account_number)
            sol_amount = float(sol_amount)
            instruction = transfer(TransferParams(from_pubkey=keypairs[from_account_number-1].pubkey(), to_pubkey=keypairs[to_account_number-1].pubkey(), lamports=int(sol_amount * 10**9)))
            recent_blockhash = http_client.get_latest_blockhash().value.blockhash
            txn = Transaction.new_signed_with_payer([instruction], payer=keypairs[from_account_number-1].pubkey(), signing_keypairs=[keypairs[from_account_number-1]], recent_blockhash=recent_blockhash)
            signature = http_client.send_transaction(txn).value

            return f"Transferred {sol_amount} SOL from {keypairs[from_account_number-1].pubkey()} to {keypairs[to_account_number-1].pubkey()} with transaction ID: {signature}"
        except Exception as e:
            return f"Error: {e}"
    

    print("Welcome to the Solana Swarm AI. Type 'exit' to quit.")
    
    async with ai as ai_instance:
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            
            print("AI: ", end="", flush=True)
            async for chunk in ai_instance.text("1", user_input):
                print(chunk, end="", flush=True)
            print()  # New line after the complete response

@click.command()
@click.option("--network", required=False, default="devnet", type=click.Choice(["devnet", "mainnet-beta"]), help="Solana Network to connect")
@click.option("--rpc", required=False, help="Custom RPC URL")
def cli(network: str = "devnet", rpc: str = None):
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set the OPENAI_API_KEY environment variable.")
    asyncio.run(main(network, rpc))
