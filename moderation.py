from model import pos_neg_neu_model, emotion_model, all_emotion_model
import json
from pymongo.mongo_client import MongoClient


def check_message(message, guild_id, mongo_client):
    # look up the guild configuration
    # if the guild is not in the configuration, return false
    # if the guild is in the configuration, check the configuration
    # if the configuration is not set, return false

    neg_bad = False
    unwanted_emotions = []

    # with open("config.json", "r") as f:
    #     curr_config = json.load(f)


    curr_config = mongo_client.puffin.config

    if len([a for a in curr_config.find({"guild": guild_id})]) == 0:
        print("Guild not in config - maybe it hasn't been configured yet?")
        return False
    else:

        guild_config = [a for a in curr_config.find({"guild": guild_id})][0]
        if guild_config["negative_messages_bad"]:
            neg_bad = True
        if guild_config["unwanted_emotions"]:
            unwanted_emotions = guild_config["unwanted_emotions"]




    # whether the message is positive, negative, or neutral
    base_message = pos_neg_neu_model(message)
    sent_label = base_message[0]["label"]
    sent_score = base_message[0]["score"]
    # emotion of the message
    emotions = all_emotion_model(message)[0]

    big_emotions = []

    for emotion in emotions:
        if emotion["score"] > 0.5:
            big_emotions.append(emotion["label"])

    if neg_bad:
        if sent_label == "NEG" and sent_score > 0.9:
            return True
        elif sent_label == "NEG" and sent_score > 0.5:
            for emotion in big_emotions:
                if emotion in unwanted_emotions:
                    return True
    else:
        for emotion in big_emotions:
            if emotion in unwanted_emotions:
                return True

    return False