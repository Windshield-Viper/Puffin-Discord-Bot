import discord
import responses
import json

TOKEN = 'MTE4NTA3NjEyNTc1MjM2NTEzNg.GdiEPo.qR5aiYEDXl6maS2dSu3H_b76IVgstgAz4jjjg8'
async def configure(message):

    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    # configure name and description in JSON file config.json
    await message.author.send("Configuration started. ")
    await message.author.send("What is the name of your server?")

    @client.event
    async def on_message(message):
        server_name = message.content

    await message.author.send("What is the description of your server?")

    @client.event
    async def on_message(message):
        server_description = message.content


    # name = await client.wait_for('message')
    # await message.author.send("What is the description of your server?")
    # description = await client.wait_for('message')
    # add name and description to JSON file, keeping other contents of the file
    with open('config.json', 'r') as f:
        config = json.load(f)
    config['name'] = server_name
    config['description'] = server_description
    with open('config.json', 'w') as f:
        json.dump(config, f)
    await message.author.send("Configuration complete. ")


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
            await configure(message)
        else:
            await send_message(message, user_message, is_private=False)

    client.run(TOKEN)