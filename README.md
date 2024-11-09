# Solana Swarm

[![PyPI - Version](https://img.shields.io/pypi/v/solana-swarm)](https://pypi.org/project/solana-swarm/)

[![Solana Swarm](https://cdn.cometheart.com/solana-swarm-logo.jpeg)](https://solana-swarm.com)



https://github.com/user-attachments/assets/16e7ec5e-a0a7-4bab-afca-dc621de1aa37



Solana Swarm is a stateful AI agent for the CLI that can perform actions on the Solana blockchain.

Fork it to create your own Solana Agent!

## Actions
* Create new Solana accounts
* Transfer SOL between accounts
* Lookup token address for a token by name or symbol from Jupiter strict list
* Requires free AlphaVybe Account:
    * Lookup USD price for a token
    * Lookup trading info for a token
    * Lookup OHLC data for a token
    * Calculate gain/losses for a token (1-day resolution)
    * Get SOL & SPL balances for accounts

## Setup
* Install OpenAI API KEY for zsh shell:
    * `echo 'export OPENAI_API_KEY="YOUR_API_KEY"' >> ~/.zshrc`
* Install AlphaVybe API KEY for zsh shell
    * `echo 'export VYBE_API_KEY="YOUR_API_KEY"' >> ~/.zshrc`

## Install
* `pip install solana-swarm`

## Usage

### Rate-Limited Public RPCs
* `solana-swarm` = mainnet-beta
* `solana-swarm --network devnet` = devnet

### Custom RPC
* `solana-swarm --rpc https://my-custom-rpc.com/123`

## Contributing
Contributions to Solana Swarm are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
