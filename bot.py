import discord
import json
from dotenv import load_dotenv
import os
from discord.ext import commands
from model import pos_neg_neu_model, emotion_model
from moderation import check_message
import discord.ext



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

GUILDS = "Scifair Bot Server"

intents = discord.Intents.default()
intents.message_content = True

sent_bot = commands.Bot(command_prefix='!puffin ', intents=intents)
#tree = discord.app_commands.CommandTree(sent_bot)

with open("modqueue.json", "r") as f:
    moderation_queue = json.load(f)

@sent_bot.event
async def on_ready():
    print(f'Logged in as {sent_bot.user.name} ({sent_bot.user.id})')
    print('------')
    await sent_bot.tree.sync(guild=discord.Object(id=1185275931904983162))
    for guild in sent_bot.guilds:
            if guild.name == GUILD:
                break

            print(
                f'{sent_bot.user} is connected to the following guild:\n'
                f'{guild.name}(id: {guild.id})'
            )
@sent_bot.tree.command(
    name="analyze",
    description="Analyzes a message for sentiment and emotion.",
    guild=discord.Object(id=1185275931904983162),
)
async def analyze(ctx, *, p_message:str):
    # whether the message is positive, negative, or neutral
    base_message = pos_neg_neu_model(p_message[18:])
    label = base_message[0]["label"]
    score = base_message[0]["score"]
   # emotion of the message
    emotion_message = emotion_model(p_message[18:])
    emotion_label = emotion_message[0]["label"]
    emotion_score = emotion_message[0]["score"]


    my_response = f"I am {round(score * 100)}% sure that was a `{label}` message. I am {round(emotion_score * 100)}% sure that was a message of emotion `{emotion_label}`."
    await ctx.response.send_message(my_response)

# @sent_bot.command()
# async def analyze(ctx, *, p_message):
#     # whether the message is positive, negative, or neutral
#     base_message = pos_neg_neu_model(p_message[18:])
#     label = base_message[0]["label"]
#     score = base_message[0]["score"]
#    # emotion of the message
#     emotion_message = emotion_model(p_message[18:])
#     emotion_label = emotion_message[0]["label"]
#     emotion_score = emotion_message[0]["score"]
#
#
#     response = f"I am {round(score * 100)}% sure that was a `{label}` message. I am {round(emotion_score * 100)}% sure that was a message of emotion `{emotion_label}`."
#     await ctx.send(response)

@sent_bot.tree.command(
    name="hello",
    description="Say hello!",
    guild=discord.Object(id=1185275931904983162),
)
async def hello(ctx):
    await ctx.response.send_message("Hello from Puffin!")
# @sent_bot.command()
# async def hello(ctx):
#     await ctx.send("Hello from sent_bot!")

@sent_bot.tree.command(name="help",
    description="View Puffin's help message.",
    guild=discord.Object(id=1185275931904983162),)
async def bot_help(ctx):
    await ctx.response.send_message("Hello! I am Puffin, a open-source NLP-based bot that can analyze and moderate messages that are negative or contain unwanted emotions. Available commands:\n"
                   "`/hello`: Say hello!\n"
                   "`/analyze <message>`: Analyze a message for sentiment and emotion.\n"
                   "`/configure`: Configure the bot for your server. Puffin will send you a private message and save the configuration in an encrypted database.\n"
                   "`/viewqueue`: View the moderation queue via an ephemeral message.\n"
                   "`/clearqueue`: Clear the moderation queue.\n"
                   "`/puffin help`: View this help message.\n")

# @sent_bot.command()
# async def bot_help(ctx):
#     await ctx.send("Hello! I am Puffin, a open-source NLP-based bot that can analyze and moderate messages that are negative or contain unwanted emotions. Available commands:\n"
#                    "`/hello`: Say hello!\n"
#                    "`/analyze <message>`: Analyze a message for sentiment and emotion.\n"
#                    "`/configure`: Configure the bot for your server. Puffin will send you a private message and save the configuration in an encrypted database.\n"
#                    "`/viewqueue`: View the moderation queue via an ephemeral message.\n"
#                    "`/clearqueue`: Clear the moderation queue.\n"
#                    "`/puffin help`: View this help message.\n")

@sent_bot.tree.command(name="configure",
    description="Configure Puffin for your server",
    guild=discord.Object(id=1185275931904983162),)
async def configure(ctx):
    author = ctx.user
    try:
        await ctx.response.send_message("Configuration started. Check your private messages.")

        server_id = str(ctx.guild.id)

        await author.send(f"Configuring server {server_id}.")

        await author.send("This bot is capable of analyzing messages for the emotions of sadness, joy, love, anger, fear, and surprise. What are emotions that are possibly irrelevant or unwanted for the purposes of your server? "
                          "Answer in the format of a comma-separated list of emotions (e.g. `sadness, anger, fear`).")
        unwanted_emotions = await sent_bot.wait_for("message", check=lambda m: m.author == author, timeout=60)
        # turn the comma-separated list into a list of emotions
        unwanted_emotions = [emotion.strip().lower() for emotion in unwanted_emotions.content.split(",")]

        await author.send("Are negative messages more likely to be malicious in your server? (y/n)")
        negative_messages_bad = await sent_bot.wait_for("message", check=lambda m: m.author == author, timeout=60)
        negative_messages_bad = str(negative_messages_bad.content).strip().lower()
        # turn the answer into a boolean
        negative_messages_bad = negative_messages_bad == "y"


        with open("config.json", "r") as f:
            curr_config = json.load(f)

        if str(server_id) in curr_config:
            await author.send("Server configuration already exists; updating configuration.")

            # Update the server info with unwanted emotions and whether negative messages are bad
            curr_config[server_id]["unwanted_emotions"] = unwanted_emotions
            curr_config[server_id]["negative_messages_bad"] = negative_messages_bad
            with open("config.json", "w") as f:
                json.dump(curr_config, f)
        else:
            # Store configuration in a JSON file
            config = {
                server_id: {
                    "unwanted_emotions": unwanted_emotions,
                    "negative_messages_bad": negative_messages_bad
                }
            }
            await author.send("Server configuration does not exist; creating configuration.")
            with open("config.json", "w") as f:
                json.dump(config, f)



        await author.send("Configuration saved successfully.")

    except Exception as err:
        await author.send(f"Configuration failed: {err}")

# Command: View Moderation Queue
@sent_bot.tree.command(name="viewqueue",
    description="View the moderation queue via an ephemeral message.",
    guild=discord.Object(id=1185275931904983162),)
async def viewqueue(ctx):
    with open("modqueue.json", "r") as f:
        moderation_queue = json.load(f)
    if moderation_queue:

        queue_message = "__**Moderation Queue**__:\n\n"
        for entry in moderation_queue:
            queue_message += f"**User**: {entry['user']}\n**Content**: `{entry['content']}`\n__[Link to Message](<{entry['link']}>)__\n\n"
        await ctx.response.send_message(queue_message)
    else:
        await ctx.response.send_message("Moderation Queue is empty.")
@sent_bot.tree.command(
    name="clearqueue",
    description="Clear the moderation queue.",
    guild=discord.Object(id=1185275931904983162),
)
async def clearqueue(ctx):
    try:
        with open("modqueue.json", "r") as f:
            moderation_queue = json.load(f)
        if moderation_queue != []:
            moderation_queue = []
            with open("modqueue.json", "w+") as f:
                json.dump(moderation_queue, f)

            await ctx.response.send_message("Moderation Queue cleared.")
        else:
            await ctx.response.send_message("Moderation Queue is already empty.")
    except Exception as err:
        await ctx.response.send_message(f"Clearing Moderation Queue failed: {err}")

# @sent_bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.CommandNotFound):
#         await ctx.send(f"Unknown command. Type `!help` for a list of available commands.")

@sent_bot.event
async def on_message(message):
    with open("modqueue.json", "r") as f:
        moderation_queue = json.load(f)
    if message.author.bot or message.guild is None:
        return  # Ignore messages from other bots


    if check_message(message.content, message.guild.id):
        moderation_queue.append({
            "user": message.author.name,
            "content": message.content,
            "link": message.jump_url
        })
        await message.channel.send(f"Message from {message.author.mention} flagged for moderation: {message.content}")
        with open("modqueue.json", "r+") as f:
            json.dump(moderation_queue, f)

    await sent_bot.process_commands(message)


def run_sent_bot():
    sent_bot.run(TOKEN)


