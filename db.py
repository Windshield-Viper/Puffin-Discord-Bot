import os
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv

load_dotenv()
DB_URI = os.getenv("DB_URI")


def get_mod_queue(mongo_client, guild_id):
    mongo_moderation_queue = mongo_client.puffin.modqueue
    if len([a for a in mongo_moderation_queue.find({"guild": guild_id})]) != 0:
        return [a for a in mongo_moderation_queue.find({"guild": guild_id})]
    else:
        return []


def clear_mod_queue(mongo_client, guild_id):
    mongo_moderation_queue = mongo_client.puffin.modqueue
    mongo_moderation_queue.delete_many({"guild": guild_id})


def add_to_mod_queue(mongo_client, mod_queue_item):
    mongo_moderation_queue = mongo_client.puffin.modqueue
    mongo_moderation_queue.insert_one(mod_queue_item)


def get_mod_queue_count(mongo_client, guild_id):
    mongo_moderation_queue = mongo_client.puffin.modqueue
    return mongo_moderation_queue.count_documents({"guild": guild_id})


def get_all_config(mongo_client):
    mongo_config = mongo_client.puffin.config
    return [a for a in mongo_config.find()]


def get_config(mongo_client, guild_id):
    mongo_config = mongo_client.puffin.config
    return [a for a in mongo_config.find({"guild": guild_id})]


def is_guild_in_config(mongo_client, guild_id):
    mongo_config = mongo_client.puffin.config
    if len([a for a in mongo_config.find({"guild": guild_id})]) != 0:
        return True
    else:
        return False


def update_config(mongo_client, guild_id, unwanted_emotions, negative_messages_bad, zero_shot_labels, lexicon):
    mongo_config = mongo_client.puffin.config
    mongo_config.update_one({"guild": guild_id}, {
        "$set": {"unwanted_emotions": unwanted_emotions, "negative_messages_bad": negative_messages_bad},
        "$set": {"zero_shot_labels": zero_shot_labels}, "$set": {"lexicon": lexicon}}, upsert=True)


def add_to_config(mongo_client, guild_id, unwanted_emotions, negative_messages_bad, zero_shot_labels, lexicon):
    mongo_config = mongo_client.puffin.config
    mongo_config.insert_one(
        {"guild": guild_id, "unwanted_emotions": unwanted_emotions, "negative_messages_bad": negative_messages_bad,
         "zero_shot_labels": zero_shot_labels, "lexicon": lexicon})


if __name__ == "__main__":
    puffin_db = MongoClient(DB_URI)
    print(get_mod_queue(puffin_db, 1185275931904983162))
