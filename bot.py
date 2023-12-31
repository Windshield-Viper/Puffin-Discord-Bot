import discord
import json
from dotenv import load_dotenv
import os
from discord.ext import commands
from model import pos_neg_neu_model, emotion_model

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

GUILDS = "Scifair Bot Server"

intents = discord.Intents.default()
intents.message_content = True

sent_bot = commands.Bot(command_prefix='!sent_bot ', intents=intents)
@sent_bot.event
async def on_ready():
    print(f'Logged in as {sent_bot.user.name} ({sent_bot.user.id})')
    print('------')

    for guild in sent_bot.guilds:
            if guild.name == GUILD:
                break

            print(
                f'{sent_bot.user} is connected to the following guild:\n'
                f'{guild.name}(id: {guild.id})'
            )
@sent_bot.command()
async def analyze(ctx, *, p_message):
    # whether the message is positive, negative, or neutral
    base_message = pos_neg_neu_model(p_message[18:])
    label = base_message[0]["label"]
    score = base_message[0]["score"]
   # emotion of the message
    emotion_message = emotion_model(p_message[18:])
    emotion_label = emotion_message[0]["label"]
    emotion_score = emotion_message[0]["score"]


    response = f"I am {round(score * 100)}% sure that was a `{label}` message. I am {round(emotion_score * 100)}% sure that was a message of emotion `{emotion_label}`."
    await ctx.send(response)
@sent_bot.command()
async def hello(ctx):
    await ctx.send("Hello from sent_bot!")

@sent_bot.command()
async def bot_help(ctx):
    await ctx.send("`Available commands: !sent_bot hello, !sent_bot analyze <message> "
                "(e.g. !sent_bot analyze I love you), !sent_bot help`.")

@sent_bot.command()
async def configure(ctx):

    try:
        author = ctx.message.author

        await author.send(f"Please provide the server name")
        server_name = await sent_bot.wait_for("message", check=lambda m: m.author == ctx.author, timeout=60)
        server_name = str(server_name.content).strip().upper()

        await author.send(f"Please provide the server description")
        server_description = await sent_bot.wait_for("message", check=lambda m: m.author == ctx.author, timeout=60)
        server_description = str(server_description.content).strip().upper()

        # Store configuration in a JSON file
        config = {
            "server_name": server_name,
            "server_description": server_description
        }

        with open("config.json", "w") as f:
            json.dump(config, f)



        await author.send("Configuration saved successfully.")

    except Exception as err:
        await author.send(f"Configuration failed: {err}")

@sent_bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Unknown command. Type `!help` for a list of available commands.")



def run_sent_bot():
    sent_bot.run(TOKEN)


