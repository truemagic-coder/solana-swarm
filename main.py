from typing import List
import os
from cyberchipped.ai import AI, SQLiteDatabase
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.system_program import TransferParams, transfer
from solana.rpc.commitment import Confirmed
from solana.rpc.api import Client

def main():

    database = SQLiteDatabase("swarm.db")
    http_client = Client("https://api.devnet.solana.com")
    keypairs : List[Keypair] = []
    
    ai = AI(
            api_key=os.getenv("OPENAI_API_KEY"),
            name="Solana Swarm AI 0.0.1",
            instructions="You are an AI Agent that can perform actions on the Solana blockchain.",
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
        keypair = Keypair()
        keypairs.append(keypair)
        
        return f"Created new account: {len(keypairs)} with public key: {keypair.pubkey()}"

    @ai.add_tool
    def get_balance(keypair_index: int) -> str:        
        try:
            balance = http_client.get_balance(pubkey=keypairs[keypair_index-1].pubkey(), commitment=Confirmed).value
            balance = balance / 10**9
            return f"Balance of {keypairs[keypair_index-1].pubkey()} is {balance} SOL"
        except Exception as e:
            return f"Error: {e}"

    @ai.add_tool
    def transfer_sol(from_keypair_index: int, to_keypair_index: int, sol_amount: float) -> str:   
        try:             
            latest_blockhash = http_client.get_latest_blockhash(commitment=Confirmed).value
            
            txn = Transaction().add(transfer(TransferParams(from_pubkey=keypairs[from_keypair_index-1].pubkey(), to_pubkey=keypairs[to_keypair_index-1].pubkey(), lamports=int(sol_amount * 10**9))))
            
            transaction = http_client.send_legacy_transaction(txn, keypairs[from_keypair_index-1], commitment=Confirmed, recent_blockhash=latest_blockhash).value

            return f"Transferred {sol_amount} SOL from {keypairs[from_keypair_index-1].pubkey()} to {keypairs[to_keypair_index].pubkey()} with transaction ID: {transaction}"
        except Exception as e:
            return f"Error: {e}"

if __name__ == "__main__":
    main()
