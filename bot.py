from dotenv import load_dotenv
import os
from models import pos_neg_neu_model, strongest_emotion_model
from moderation import check_message
import discord.ext
from pymongo.mongo_client import MongoClient
from db import *
from typing import Literal, Optional
import discord
from discord.ext import commands
from googleapiclient import discovery

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILDS = os.getenv('DISCORD_GUILD')
DB_URI = os.getenv("DB_URI")
API_KEY = os.getenv("GOOGLE_API_KEY")


intents = discord.Intents.default()
intents.message_content = True

sent_bot = commands.Bot(command_prefix='!puffin ', intents=intents)

puffin_db = MongoClient(DB_URI)
google_api_client = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=API_KEY,
        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
        static_discovery=False,
    )



@sent_bot.event
async def on_ready():
    mongo_cluster = MongoClient(DB_URI)
    puffin_db = mongo_cluster.puffin

    print(f'Logged in as {sent_bot.user.name} ({sent_bot.user.id})')
    print('------')

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

    main_channel = guild.system_channel or next(
        (channel for channel in guild.channels if isinstance(channel, discord.TextChannel)), None)

    if main_channel and main_channel.permissions_for(guild.me).send_messages:
        welcome_message = ("Thank you for adding me to your server! Use `/help` to see available commands. I won't "
                           "work until you configure me with `/configure`.")
        await main_channel.send(welcome_message)


@sent_bot.tree.command(
    name="analyze",
    description="Analyzes a message for sentiment and emotion.",
)
async def analyze(ctx, *, p_message: str):
    # whether the message is positive, negative, or neutral
    base_message = pos_neg_neu_model(p_message[18:])
    label = base_message[0]["label"]
    score = base_message[0]["score"]

    # emotion of the message
    emotion_message = strongest_emotion_model(p_message[18:])
    emotion_label = emotion_message[0]["label"]
    emotion_score = emotion_message[0]["score"]

    my_response = f"I am {round(score * 100)}% sure that was a `{label}` message. I am {round(emotion_score * 100)}% sure that was a message of emotion `{emotion_label}`."
    await ctx.response.send_message(my_response)


@sent_bot.tree.command(
    name="hello",
    description="Say hello!",
)
async def hello(ctx):
    await ctx.response.send_message("Hello from Puffin!")


@sent_bot.tree.command(name="help",
                       description="View Puffin's help message.",
                       )
async def bot_help(ctx):
    await ctx.response.send_message("Hello! I am Puffin, a open-source NLP-based bot that can analyze and moderate "
                                    "messages that are negative or contain unwanted emotions using various techniques "
                                    "such as"
                                    "sentiment analysis and zero-shot classification. Available commands:\n"
                                    "`/hello`: Say hello!\n"
                                    "`/analyze <message>`: Analyze a message for sentiment and emotion.\n"
                                    "`/configure`: Configure the bot for your server. Puffin will send you a private message and save the configuration in an encrypted database.\n"
                                    "`/viewqueue`: View the moderation queue (which is stored in an encrypted database) via an ephemeral message.\n"
                                    "`/clearqueue`: Clear the moderation queue.\n"
                                    "`/puffin help`: View this help message.\n"
                                    )


@sent_bot.tree.command(name="configure",
                       description="Configure Puffin for your server",
                       )
@commands.has_permissions(kick_members=True)
@commands.guild_only()
async def configure(ctx):
    author = ctx.user
    try:
        await ctx.response.send_message("Configuration started. Check your private messages.", ephemeral=True)

        server_id = ctx.guild.id

        await author.send(f"Configuring server {server_id}.")

        while True:
            await author.send(
                "This bot is capable of analyzing messages for the emotions of sadness, joy, love, anger, "
                "fear, and surprise. What are emotions that are possibly irrelevant or unwanted for the purposes of your server? "
                "Answer in the format of a comma-separated list of emotions (e.g. `sadness, anger, fear`).")
            potential_emotions = ["sadness", "joy", "love", "anger", "fear", "surprise"]
            unwanted_emotions = await sent_bot.wait_for("message", check=lambda m: m.author == author, timeout=600)
            # turn the comma-separated list into a list of emotions
            unwanted_emotions = [emotion.strip().lower() for emotion in unwanted_emotions.content.split(",")]
            # check if the emotions are valid
            for emotion in unwanted_emotions:
                if emotion not in potential_emotions:
                    await author.send(f"Invalid emotion: {emotion}. Please try again.")
                    break
            else:
                break

        await author.send("Are negative messages more likely to be malicious in your server? Keep in mind that answering 'y' will flag any messages "
                          "in the server that seem to be negative. (y/n)")
        negative_messages_bad = await sent_bot.wait_for("message", check=lambda m: m.author == author, timeout=600)
        negative_messages_bad = str(negative_messages_bad.content).strip().lower()
        # turn the answer into a boolean
        negative_messages_bad = negative_messages_bad == "y"

        await author.send(
            "This bot uses zero-shot text classification to allow you to set custom labels to moderate your server."
            " What are some custom labels that you would like to use for zero-shot classification? Answer in the format of a comma-separated list of labels (e.g. `spam, nsfw`).")
        zero_shot_labels = await sent_bot.wait_for("message", check=lambda m: m.author == author, timeout=600)
        # turn the comma-separated list into a list of labels
        zero_shot_labels = [label.strip().lower() for label in zero_shot_labels.content.split(",")]

        if is_guild_in_config(puffin_db, server_id):
            await author.send("Server configuration already exists; updating configuration.")

            update_config(puffin_db, server_id, unwanted_emotions, negative_messages_bad, zero_shot_labels)
        else:
            await author.send("Server configuration does not exist; creating configuration.")

            add_to_config(puffin_db, server_id, unwanted_emotions, negative_messages_bad, zero_shot_labels)

        await author.send("Configuration saved successfully.")

    except Exception as err:
        await author.send(f"Configuration failed: {err}")


@sent_bot.tree.command(name="viewqueue",
                       description="View the moderation queue via an ephemeral message.",
                       )
@commands.has_permissions(kick_members=True)
@commands.guild_only()
async def viewqueue(ctx):
    db_queue = get_mod_queue(puffin_db, ctx.guild.id)

    if db_queue:
        db_queue_message = "__**Moderation Queue**__:\n\n"
        for entry in db_queue:
            try:
                db_queue_message += f"**Content**: `{entry['content']}`\n**Reason for flag:** *{entry['reason']}*\n__[Link to Message](<{entry['link']}>)__\n\n"

            except Exception as err:
                print(type(entry))
                print(err)

        if db_queue_message != "__**Moderation Queue**__:\n\n":

            #make the message send in pieces if it's too long
            if len(db_queue_message) < 2000:
                await ctx.response.send_message(db_queue_message, ephemeral=True)
            else:
                # tell the user that the message will be sent as a pm
                await ctx.response.send_message("Moderation Queue is too long to send in a channel, sending as a private message.", ephemeral=True)
                # break the message into pieces and send
                for i in range(0, len(db_queue_message), 2000):
                    await ctx.user.send(db_queue_message[i:i + 2000])



        else:
            await ctx.response.send_message("Moderation Queue is empty, this was triggered", ephemeral=True)
    else:
        await ctx.response.send_message("Moderation Queue is empty.", ephemeral=True)


@sent_bot.tree.command(
    name="clearqueue",
    description="Clear the moderation queue.",
)
@commands.has_permissions(kick_members=True)
@commands.guild_only()
async def clearqueue(ctx):
    try:
        clear_mod_queue(puffin_db, ctx.guild.id)
        await ctx.response.send_message("Moderation Queue cleared.", ephemeral=True)

    except Exception as err:
        await ctx.response.send_message(f"Clearing Moderation Queue failed: {err}", ephemeral=True)


@sent_bot.event
async def on_message(message):
    if message.author.bot or message.guild is None:
        return  # Ignore messages from other bots
    print(check_message(message.content, message.guild.id, puffin_db, google_api_client))
    if check_message(message.content, message.guild.id, puffin_db, google_api_client)[0]:
        mod_message = {
            # "user": message.author.name,
            "content": message.content,
            "link": message.jump_url,
            "guild": message.guild.id,
            "reason": check_message(message.content, message.guild.id, puffin_db, google_api_client)[1],
        }
        # await message.channel.send(f"Message from {message.author.mention} flagged for moderation: {message.content}")

        add_to_mod_queue(puffin_db, mod_message)

    await sent_bot.process_commands(message)


# credit to https://about.abstractumbra.dev/discord.py/2023/01/29/sync-command-example.html
@sent_bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object],
               spec: Optional[Literal["~", "*", "^"]] = None) -> None:
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
