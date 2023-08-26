import discord
import os
from dotenv import load_dotenv

from file_activity import *

load_dotenv()
BOTTOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    print(message)
    username = str(message.author).split("#")[0]
    user_msg = str(message.content)
    channel = str(message.channel.name)
    print(f"{username}: {user_msg} ({channel})")

    # make sure the bot doesn't respond to itself
    if message.author == client.user:
        return


    if user_msg.lower() == "!commands":
        await message.channel.send(f"\
             !hello: Greetings message\
             \n!bye: Farewell message\
             \n!pb get activity: Returns 4 of the latest changes to the 'Everything Sheet' \
             \n!pb Things to Do: Returns contents of the 'Things to Do' sheet\
             \n!pb Places to Eat: Returns contents of the 'Places to Eat' sheet")

        return
    
    if user_msg.lower() == "!hello":
        await message.channel.send(f"Hello {username}")
        return

    if user_msg.lower() == "!pb things to do":
        thingsToDo = getSpreadsheetInfo("Things to Do")
        # print(thingsToDo)
        for things in thingsToDo:
            await message.channel.send(f"{things}")
        return
    
    if user_msg.lower() == "!pb places to eat":
        placesToEat = getSpreadsheetInfo("Places to Eat")
        for places in placesToEat:
            await message.channel.send(f"{places}")

        return

    if user_msg.lower() == "!pb get activity":
        activities = getActivity()
        for activity in activities:
            time = getTimeInfo(activity)
            action = getActionInfo(activity['primaryActionDetail'])
            actors = map(getActorInfo, activity['actors'])
            targets = map(getTargetInfo, activity['targets'])
            actors_str, targets_str = "", ""
            actor_name = getUserName(actors_str.join(actors))
            target_name = targets_str.join(targets)
            await message.channel.send(f"{time}, {action}, {actor_name}, {target_name}")
        return

    elif user_msg.lower() == "!bye":
        await message.channel.send(f"See you later {username}")
        return

if __name__ == "__main__":
    client.run(BOTTOKEN)