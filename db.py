import os
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
import pprint
import json

load_dotenv()
DB_URI = os.getenv("DB_URI")


# def setup_db():
#     # CAUTION: this will delete all data in the database and replace it with the modqueue.json file and the config.json file
#     # Create a new client and connect to the server
#     puffin_db = MongoClient(DB_URI)
#
#     # Send a ping to confirm a successful connection
#     try:
#         puffin_db.admin.command('ping')
#         print("Pinged your deployment. You successfully connected to MongoDB!")
#     except Exception as e:
#         print(e)
#
#     # load in moderation queue
#     with open("modqueue.json", "r") as f:
#         moderation_queue = json.load(f)
#
#     mongo_mod_queue = puffin_db.puffin.modqueue
#
#     # put the mod queue into the database
#     if len(moderation_queue) > 1:
#         mongo_mod_queue.insert_many([moderation_queue])
#     else:
#         mongo_mod_queue.insert_one(moderation_queue)
#     # load in config
#     with open("config.json", "r") as f:
#         config = json.load(f)
#
#     mongo_config = puffin_db.puffin.config
#
#     # put the config into the database
#     mongo_config.insert_many([config])
#
#     # close the connection
#     puffin_db.close()


def get_mod_queue(mongo_client, guild_id):
    mongo_moderation_queue = mongo_client.puffin.modqueue
    # return all the data as a list
    #print(type([a for a in mongo_moderation_queue.find({"guild": guild_id})][0]))
    if len([a for a in mongo_moderation_queue.find({"guild": guild_id})]) != 0:
        return [a for a in mongo_moderation_queue.find({"guild": guild_id})]
    else:
        return []

def clear_mod_queue(mongo_client, guild_id):
    mongo_moderation_queue = mongo_client.puffin.modqueue
    # mongo_moderation_queue.delete_many({"guild": guild_id})
    mongo_moderation_queue.delete_many({"guild": guild_id})

def add_to_mod_queue(mongo_client, guild_id, mod_queue_item):
    mongo_moderation_queue = mongo_client.puffin.modqueue
    mongo_moderation_queue.insert_one(mod_queue_item)

def get_mod_queue_count(mongo_client, guild_id):
    mongo_moderation_queue = mongo_client.puffin.modqueue
    # return all the data as a list
    return mongo_moderation_queue.count_documents({"guild": guild_id})

def get_all_config(mongo_client):
    mongo_config = mongo_client.puffin.config
    # return all the data as a list
    return [a for a in mongo_config.find()]
def get_config(mongo_client, guild_id):
    mongo_config = mongo_client.puffin.config
    # return all the data as a list
    return [a for a in mongo_config.find({"guild": guild_id})]

def is_guild_in_config(mongo_client, guild_id):
    mongo_config = mongo_client.puffin.config
    # return all the data as a list
    if len([a for a in mongo_config.find({"guild": guild_id})]) != 0:
        return True
    else:
        return False

def update_config(mongo_client, guild_id, unwanted_emotions, negative_messages_bad):
    mongo_config = mongo_client.puffin.config
    mongo_config.update_one({"guild": guild_id}, {"$set": {"unwanted_emotions": unwanted_emotions, "negative_messages_bad": negative_messages_bad}})

def add_to_config(mongo_client, guild_id, unwanted_emotions, negative_messages_bad):
    mongo_config = mongo_client.puffin.config
    mongo_config.insert_one({"guild": guild_id, "unwanted_emotions": unwanted_emotions, "negative_messages_bad": negative_messages_bad})



if __name__ == "__main__":

    puffin_db = MongoClient(DB_URI)
    print(get_mod_queue(puffin_db, 1185275931904983162))