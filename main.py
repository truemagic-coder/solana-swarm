import os
from cyberchipped.ai import AI, SQLiteDatabase
from solders.pubkey import Pubkey as PublicKey
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.system_program import TransferParams, transfer
from solana.rpc.commitment import Confirmed
from solana.rpc.api import Client

def main():

    database = SQLiteDatabase("swarm.db")

    ai = AI(
            api_key=os.getenv("OPENAI_API_KEY"),
            name="Solana Swarm AI 0.0.1",
            instructions="You are an AI Agent that can perform actions on the Solana blockchain.",
            database=database,
        )

    @ai.add_tool
    def transfer_sol(address: str, amount: float) -> str:
        source = os.getenv("SOLANA_PRIVATE_KEY")
        
        source_key = Keypair.from_base58_string(source)
        
        destination_key = PublicKey.from_string(address)
        
        http_client = Client(os.getenv("SOLANA_RPC_URL"))
        
        latest_blockhash = http_client.get_latest_blockhash(commitment=Confirmed).value
        
        txn = Transaction().add(transfer(TransferParams(from_pubkey=source_key.public_key, to_pubkey=destination_key, lamports=int(amount * 10**9))))
        
        transaction = http_client.send_legacy_transaction(txn, source_key, commitment=Confirmed, recent_blockhash=latest_blockhash).value

        return f"Transferred {amount} SOL to {address} with transaction ID: {transaction}"

if __name__ == "__main__":
    main()
