#
# pgnbot.py v2022-01-02
#
# TODO create channel for each game


import discord
import logging
import chess
import chess.pgn
import chess.svg
import requests
import io
import os
import json
from cairosvg import svg2png

logging.basicConfig(level=logging.INFO)
client = discord.Client()

intents = discord.Intents.none()
intents.reactions = True
intents.members = True
intents.guilds = True



with open("config.json", "r") as f:
    config = json.load(f)
print(config)
active_messages = {}

# send_image(message.channel, "1.png", game.headers, message.author.mention)
async def send_image(channel, filename, desc = " ", content = ""):
    images_channel = client.get_channel(config["DISCORD_IMG_CHANNEL"])
    img_msg = await images_channel.send("", file=discord.File(open(filename, 'rb')))
    return await channel.send(content, embed=discord.Embed(type='image',description=desc).set_image(url = str(img_msg.attachments[0])))

class ActiveMessage:
    def __init__(self, game, message):
        self.game = game
        self.moves = [m for m in game.mainline_moves()]
        self.board = game.board()
        self.n = 0
        self.message = message
        self.path = "images/" + str(message.id) + "/"
        os.mkdir(self.path)
        self.icache = {}

    async def precache(self):
        images_channel = client.get_channel(config["DISCORD_IMG_CHANNEL"])
        i = 0
        for m in self.moves:
            svg = chess.svg.board(self.board)
            filename = self.path + "temp.png"
            svg2png(bytestring = svg, write_to=filename)
            img_msg = await images_channel.send("", file=discord.File(open(filename, 'rb')))
            self.icache[i] = str(img_msg.attachments[0])
            self.board.push(m)
            i = i + 1
        self.board.reset()
        os.remove(self.path + "temp.png")
        os.rmdir(self.path)

    async def render(self):
        if not config["PRECACHE_MOVES"]:
            if not self.n in self.icache:
                svg = chess.svg.board(self.board)
                filename = self.path + str(self.n) + ".png"
                svg2png(bytestring = svg, write_to=filename)
                images_channel = client.get_channel(config["DISCORD_IMG_CHANNEL"])
                img_msg = await images_channel.send("", file=discord.File(open(filename, 'rb')))
                self.icache[self.n] = str(img_msg.attachments[0])
        new_embed = self.message.embeds[0].set_image(url = self.icache[self.n])
        await self.message.edit(embed = new_embed)
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if len(message.attachments) == 1 and str(message.attachments[0])[-3:] == "pgn":
        g = io.StringIO(requests.get(message.attachments[0]).text)
        game = chess.pgn.read_game(g)
        chess_msg = await message.channel.send(message.author.mention, embed=discord.Embed(type="image",description=game.headers))
        await chess_msg.add_reaction("⬅️")
        await chess_msg.add_reaction("➡️")
        active_messages[chess_msg.id] = ActiveMessage(game, chess_msg)
        if config["PRECACHE_MOVES"]:
            await active_messages[chess_msg.id].precache()
        await active_messages[chess_msg.id].render()

@client.event
async def on_reaction_add(reaction, user):
    if user == client.user:
        return
    if reaction.message.id in active_messages.keys():
        message = active_messages[reaction.message.id]
        if reaction.emoji == "➡️":
            if message.n + 1 < len(message.moves):
                message.board.push(message.moves[message.n])
                message.n = message.n + 1
        if reaction.emoji == "⬅️":
            if message.n > 0:
                message.board.pop()
                message.n = message.n - 1
        await message.render()
    await reaction.remove(user)

            

client.run(config["DISCORD_TOKEN"])
