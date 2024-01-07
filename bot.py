import discord
import json
from dotenv import load_dotenv
import os
from discord.ext import commands
from model import pos_neg_neu_model, emotion_model
from moderation import check_message
import discord.ext
from pymongo.mongo_client import MongoClient
from db import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILDS = os.getenv('DISCORD_GUILD')
DB_URI = os.getenv("DB_URI")

#GUILDS = "Scifair Bot Server"



intents = discord.Intents.default()
intents.message_content = True

sent_bot = commands.Bot(command_prefix='!puffin ', intents=intents)

with open("modqueue.json", "r") as f:
    moderation_queue = json.load(f)

puffin_db = MongoClient(DB_URI)
#puffin_db = mongo_cluster.puffin


@sent_bot.event
async def on_ready():
    mongo_cluster = MongoClient(DB_URI)
    puffin_db = mongo_cluster.puffin

    print(f'Logged in as {sent_bot.user.name} ({sent_bot.user.id})')
    print('------')
    #await sent_bot.tree.sync(guild=discord.Object(id=1185275931904983162))
    for guild in sent_bot.guilds:
            await sent_bot.tree.sync(guild=guild)

            print(
                f'{sent_bot.user} is connected to the following guild:\n'
                f'{guild.name}(id: {guild.id})'
            )
    try:
        mongo_cluster.admin.command('ping')
        print("Successful connection to MongoDB!")
    except Exception as e:
        print(e)

@sent_bot.event
async def on_guild_join(guild):
    print(f'Bot joined a new guild: {guild.name} (ID: {guild.id})')

    # Find the main channel (you can customize this based on your criteria)
    main_channel = guild.system_channel or next((channel for channel in guild.channels if isinstance(channel, discord.TextChannel)), None)

    # Perform actions when the bot joins a new guild
    if main_channel and main_channel.permissions_for(guild.me).send_messages:
        welcome_message = "Thank you for adding me to your server! Use `/help` to see available commands. I won't work until you configure me with `/configure`."
        await main_channel.send(welcome_message)

@sent_bot.tree.command(
    name="analyze",
    description="Analyzes a message for sentiment and emotion.",
    #guild=discord.Object(id=1185275931904983162),
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

@sent_bot.tree.command(
    name="hello",
    description="Say hello!",
    #guild=discord.Object(id=1185275931904983162),
)
async def hello(ctx):
    await ctx.response.send_message("Hello from Puffin!")

@sent_bot.tree.command(name="help",
    description="View Puffin's help message.",
    #guild=discord.Object(id=1185275931904983162),
                       )
async def bot_help(ctx):
    await ctx.response.send_message("Hello! I am Puffin, a open-source NLP-based bot that can analyze and moderate messages that are negative or contain unwanted emotions. Available commands:\n"
                   "`/hello`: Say hello!\n"
                   "`/analyze <message>`: Analyze a message for sentiment and emotion.\n"
                   "`/configure`: Configure the bot for your server. Puffin will send you a private message and save the configuration in an encrypted database.\n"
                   "`/viewqueue`: View the moderation queue (which is stored in an encrypted database) via an ephemeral message.\n"
                   "`/clearqueue`: Clear the moderation queue.\n"
                   "`/puffin help`: View this help message.\n")

@sent_bot.tree.command(name="configure",
    description="Configure Puffin for your server",
    #guild=discord.Object(id=1185275931904983162),
)
@commands.has_permissions(kick_members=True)
@commands.guild_only()
async def configure(ctx):
    author = ctx.user
    try:
        await ctx.response.send_message("Configuration started. Check your private messages.", ephemeral=True)

        server_id = ctx.guild.id

        await author.send(f"Configuring server {server_id}.")

        await author.send("This bot is capable of analyzing messages for the emotions of sadness, joy, love, anger, fear, and surprise. What are emotions that are possibly irrelevant or unwanted for the purposes of your server? "
                          "Answer in the format of a comma-separated list of emotions (e.g. `sadness, anger, fear`).")
        unwanted_emotions = await sent_bot.wait_for("message", check=lambda m: m.author == author, timeout=600)
        # turn the comma-separated list into a list of emotions
        unwanted_emotions = [emotion.strip().lower() for emotion in unwanted_emotions.content.split(",")]

        await author.send("Are negative messages more likely to be malicious in your server? (y/n)")
        negative_messages_bad = await sent_bot.wait_for("message", check=lambda m: m.author == author, timeout=600)
        negative_messages_bad = str(negative_messages_bad.content).strip().lower()
        # turn the answer into a boolean
        negative_messages_bad = negative_messages_bad == "y"


        # with open("config.json", "r") as f:
        #     curr_config = json.load(f)

        if is_guild_in_config(puffin_db, server_id):
            await author.send("Server configuration already exists; updating configuration.")

            # # Update the server info with unwanted emotions and whether negative messages are bad
            # curr_config[server_id]["unwanted_emotions"] = unwanted_emotions
            # curr_config[server_id]["negative_messages_bad"] = negative_messages_bad
            # with open("config.json", "w") as f:
            #     json.dump(curr_config, f)

            update_config(puffin_db, server_id, unwanted_emotions, negative_messages_bad)
        else:
            # # Store configuration in a JSON file
            # config = {
            #     server_id: {
            #         "unwanted_emotions": unwanted_emotions,
            #         "negative_messages_bad": negative_messages_bad
            #     }
            # }
            await author.send("Server configuration does not exist; creating configuration.")
            # curr_config[server_id] = config[server_id]
            # with open("config.json", "w") as f:
            #     json.dump(curr_config, f)

            add_to_config(puffin_db, server_id, unwanted_emotions, negative_messages_bad)


        await author.send("Configuration saved successfully.")

    except Exception as err:
        await author.send(f"Configuration failed: {err}")

# Command: View Moderation Queue
@sent_bot.tree.command(name="viewqueue",
    description="View the moderation queue via an ephemeral message.",
    #guild=discord.Object(id=1185275931904983162),
)
@commands.has_permissions(kick_members=True)
@commands.guild_only()
async def viewqueue(ctx):
    with open("modqueue.json", "r") as f:
        moderation_queue = json.load(f)
        #moderation_queue = moderation_queue["data"]
    queue_message = "__**Moderation Queue**__:\n\n"
    # for entry in moderation_queue:
    #     if entry["guild"] == ctx.guild.id:
    #         queue_message += f"**User**: {entry['user']}\n**Content**: `{entry['content']}`\n__[Link to Message](<{entry['link']}>)__\n\n"
    db_queue = get_mod_queue(puffin_db, ctx.guild.id)
    # if len(db_queue) == 1:
    #     db_queue = [db_queue]
    if db_queue != []:
        db_queue_message = "__**Moderation Queue**__:\n\n"
        for entry in db_queue:
            try:
                db_queue_message += f"**User**: {entry['user']}\n**Content**: `{entry['content']}`\n__[Link to Message](<{entry['link']}>)__\n\n"
                #print("Added user to queue message")
                #print(db_queue_message)
            except Exception as err:
                print(type(entry))
                print(err)

        if db_queue_message != "__**Moderation Queue**__:\n\n":
            await ctx.response.send_message(db_queue_message, ephemeral=True)

        else:
            await ctx.response.send_message("Moderation Queue is empty, this was triggered", ephemeral=True)
    else:
        await ctx.response.send_message("Moderation Queue is empty.", ephemeral=True)
@sent_bot.tree.command(
    name="clearqueue",
    description="Clear the moderation queue.",
    #guild=discord.Object(id=1185275931904983162),
)
@commands.has_permissions(kick_members=True)
@commands.guild_only()
async def clearqueue(ctx):
    try:
        # with open("modqueue.json", "r") as f:
        #     moderation_queue = json.load(f)
        # guild_id = ctx.guild.id
        # guild_mod_queue = []
        # for entry in moderation_queue:
        #     if entry["guild"] != guild_id:
        #         guild_mod_queue.append(entry)
        # with open("modqueue.json", "w+") as f:
        #     json.dump({"data": guild_mod_queue}, f)
        clear_mod_queue(puffin_db, ctx.guild.id)
        await ctx.response.send_message("Moderation Queue cleared.", ephemeral=True)

    except Exception as err:
        await ctx.response.send_message(f"Clearing Moderation Queue failed: {err}", ephemeral=True)

    # try:
    #     with open("modqueue.json", "r") as f:
    #         moderation_queue = json.load(f)
    #     if moderation_queue != []:
    #         moderation_queue = []
    #         with open("modqueue.json", "w+") as f:
    #             json.dump(moderation_queue, f)
    #
    #         await ctx.response.send_message("Moderation Queue cleared.", ephemeral=True)
    #     else:
    #         await ctx.response.send_message("Moderation Queue is already empty.", ephemeral=True)
    # except Exception as err:
    #     await ctx.response.send_message(f"Clearing Moderation Queue failed: {err}", ephemeral=True)

# @sent_bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.CommandNotFound):
#         await ctx.send(f"Unknown command. Type `!help` for a list of available commands.")

@sent_bot.event
async def on_message(message):
    # with open("modqueue.json", "r") as f:
    #     moderation_queue = json.load(f)
    #     #moderation_queue = moderation_queue["data"]

    if message.author.bot or message.guild is None:
        return  # Ignore messages from other bots


    if check_message(message.content, message.guild.id, puffin_db):
        mod_message = {
            "user": message.author.name,
            "content": message.content,
            "link": message.jump_url,
            "guild": message.guild.id,
        }
        await message.channel.send(f"Message from {message.author.mention} flagged for moderation: {message.content}")
        # moderation_queue = {"data": moderation_queue}
        # with open("modqueue.json", "r+") as f:
        #     json.dump(moderation_queue, f)

        add_to_mod_queue(puffin_db, message.guild.id, mod_message)

    await sent_bot.process_commands(message)

from typing import Literal, Optional

import discord
from discord.ext import commands

@sent_bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

def run_sent_bot():
    sent_bot.run(TOKEN)


