# PGNbot
Discord bot for displaying and traversing chess PGN (Portable Game Notation) files.

https://user-images.githubusercontent.com/96760624/147914647-e974f3f0-120e-4d75-8a5a-61e9f02518dc.mp4

# Installation & Setup
## Dependencies
```shell
pip install -U discord.py chess requests cairosvg
```
## Discord Setup
Requires a Bot user with the Priviliged Gateway Intents enabled, and a channel on your server where the bot can upload images.

## Configuration
Should be straight-forward; the two necessary fields in `config.json` are the bot's client token (`DISCORD_TOKEN` - a string) and the channel for images (`DISCORD_IMG_CHANNEL` - an integer).

# TODO
- [ ] Add support for exploring and adding branch lines
- [ ] Scrape lichess.org and chess.com game links for PGNs
- [ ] Add support for puzzles