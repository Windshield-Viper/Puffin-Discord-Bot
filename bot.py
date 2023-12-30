import discord
import responses
import json
from dotenv import load_dotenv
import os
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


TOKEN = 'MTE4NTA3NjEyNTc1MjM2NTEzNg.GdiEPo.qR5aiYEDXl6maS2dSu3H_b76IVgstgAz4jjjg8'
GUILDS = "Scifair Bot Server"

config_bot = commands.Bot(command_prefix='!sent_bot configure')

@config_bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
async def nine_nine(ctx):
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)

bot.run(TOKEN)


# async def configure(message):
#
#     intents = discord.Intents.default()
#     client = discord.Client(intents=intents)
#     # configure name and description in JSON file config.json
#     await message.author.send("Configuration started. ")
#     await message.author.send("What is the name of your server?")
#
#     @client.event
#     async def on_message(message):
#         server_name = message.content
#         await message.author.send("Your server name is: " + str(server_name))
#         await message.author.send("What is the description of your server?")
#
#     # @client.event
#     # async def on_message(message):
#     #     server_description = message.content
#     #
#     #
#     # # name = await client.wait_for('message')
#     # # await message.author.send("What is the description of your server?")
#     # # description = await client.wait_for('message')
#     # # add name and description to JSON file, keeping other contents of the file
#     # with open('config.json', 'r') as f:
#     #     config = json.load(f)
#     # config['name'] = server_name
#     # config['description'] = server_description
#     # with open('config.json', 'w') as f:
#     #     json.dump(config, f)
#     # await message.author.send("Configuration complete. ")
#

async def send_message(message, user_message, is_private):
    try:
        # if user_message == "!sent_bot configure":
        #     await configure(message)
        # else:
            response = responses.get_response(user_message)
            await message.author.send(response) if is_private else await message.channel.send(response)

    except Exception as e:
        print(e)

def run_discord_bot():
    TOKEN = 'MTE4NTA3NjEyNTc1MjM2NTEzNg.GdiEPo.qR5aiYEDXl6maS2dSu3H_b76IVgstgAz4jjjg8'
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} has connected to Discord!')
        for guild in client.guilds:
            if guild.name == GUILD:
                break

        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f'{username} said: {user_message} ({channel})')

        if message.content[-3:] == " -p":
            user_message = user_message[0:len(user_message) - 3]
            await send_message(message, user_message, is_private=True)
        elif message.content == "!sent_bot configure":
            #await configure(message)
            return
        else:
            await send_message(message, user_message, is_private=False)

    client.run(TOKEN)