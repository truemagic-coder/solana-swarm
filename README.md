# Solana Swarm

[![PyPI - Version](https://img.shields.io/pypi/v/solana-swarm)](https://pypi.org/project/solana-swarm/)

[![Solana Swarm](https://cdn.cometheart.com/solana-swarm-logo.jpeg)](https://solana-swarm.com)



https://github.com/user-attachments/assets/16e7ec5e-a0a7-4bab-afca-dc621de1aa37



Solana Swarm is a stateful AI agent for the CLI that can perform actions on the Solana blockchain.

Fork it to create your own Solana Agent!

## Actions
* Create new accounts
* Get balances of accounts
* Transfer between accounts

## Setup
* Install OpenAI API KEY for zsh shell:
    * `echo 'export OPENAI_API_KEY="YOUR_API_KEY"' >> ~/.zshrc`

## Install
* `pip install solana-swarm`

## Usage

### Rate-Limited Public RPCs
* `solana-swarm` = devnet
* `solana-swarm --network mainnet-beta` = mainnet-beta

### Custom RPC
* `solana-swarm --rpc https://my-custom-rpc.com/123`

### Example Test Flow on Devnet
* `solana-swarm`
* Tell the AI to: `create 2 new accounts`
* Go to https://faucet.solana.com/ and airdrop 0.5 SOL into account 1 (cut and paste public key from CLI into site)
* Tell the AI to: `Check the balance of account 1` - should be 0.5 SOL
* Tell the AI to: `Transfer 0.25 SOL from account 1 to account 2` - should complete and show new balances
* NOTE: wallets are not saved between chats so if you `exit` you will lose access to the wallets!

## Contributing
Contributions to Solana Swarm are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
