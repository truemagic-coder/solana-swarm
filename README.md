# Solana Swarm

[![PyPI - Version](https://img.shields.io/pypi/v/solana-swarm)](https://pypi.org/project/solana-swarm/)

This CLI tool is a stateful AI agent that can perform actions on the Solana blockchain (devnet).

## Actions:
* Create new accounts
* Get balances of accounts
* Transfer between accounts

## Test Flow on Devnet:
* Install OpenAI API KEY for `zsh` shell:
    * `echo 'export OPENAI_API_KEY="YOUR_API_KEY"' >> ~/.zshrc`
* `pip install solana-swarm`
* `solana-swarm`
* Tell the AI to: `create 2 new accounts`
* Go to https://faucet.solana.com/ and airdrop 0.5 SOL into account 1 (cut and paste public key from CLI into site)
* Tell the AI to: `Check the balance of account 1` - should be 0.5 SOL
* Tell the AI to: `Transfer 0.25 SOL from account 1 to account 2` - should complete and show new balances
* NOTE: wallets are not saved between chats so if you `exit` you will lose access to the wallets!
