from models import pos_neg_neu_model, strongest_emotion_model, all_emotion_model, zero_shot_classifier
from pymongo.mongo_client import MongoClient
from googleapiclient import discovery
from dotenv import load_dotenv
import os
import json

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")


def check_message(message, guild_id, mongo_client, google_api_client):
    neg_bad = False
    unwanted_emotions = []
    zero_shot_labels = []
    curr_config = mongo_client.puffin.config

    if len([a for a in curr_config.find({"guild": guild_id})]) == 0:
        print("Guild not in config - maybe it hasn't been configured yet?")
        return (False, "Guild not in config - maybe it hasn't been configured yet?")
    else:

        guild_config = [a for a in curr_config.find({"guild": guild_id})][0]
        if guild_config["negative_messages_bad"]:
            neg_bad = True
        if guild_config["unwanted_emotions"]:
            unwanted_emotions = guild_config["unwanted_emotions"]
        if guild_config["zero_shot_labels"]:
            zero_shot_labels = guild_config["zero_shot_labels"]

    analyze_request = {
        'comment': {'text': 'friendly greetings from python'},
        'requestedAttributes': {'TOXICITY': {}}
    }

    # whether the message is positive, negative, or neutral
    base_message = pos_neg_neu_model(message)
    sent_label = base_message[0]["label"]
    sent_score = base_message[0]["score"]
    # emotion of the message
    emotions = all_emotion_model(message)[0]

    big_emotions = []

    toxicity_response = google_api_client.comments().analyze(body=analyze_request).execute()
    toxicity_response = float(json.dumps(toxicity_response["attributeScores"]["TOXICITY"]["summaryScore"]["value"], indent=2))

    for emotion in emotions:
        if emotion["score"] > 0.6:
            big_emotions.append(emotion["label"])
        if emotion["score"] == max([a["score"] for a in emotions]):
            biggest_emotion = emotion["label"]
        if emotion["score"] == sorted([a["score"] for a in emotions])[-2]:
            second_biggest_emotion = emotion["label"]


    if neg_bad:
        if sent_label == "NEG" and sent_score < 0.8:
            if biggest_emotion in unwanted_emotions:
                return (True, f"Negative, contains unwanted emotion {biggest_emotion}")
            elif second_biggest_emotion in unwanted_emotions:
                return (True, f"Negative, contains unwanted emotion {second_biggest_emotion}")
        else:
            if sent_label == "NEG" and sent_score > 0.8:
                return (True, "Very negative")
            else:
                if toxicity_response > 0.8:
                    return (True, "Toxicity score very high")
                return (False, "Not negative, does not contain an unwanted emotion")
    else:
        if (biggest_emotion in unwanted_emotions) and (not ((sent_label == "NEU" and sent_score > 0.60) or (sent_label == "POS" and sent_score > 0.60))):
            print(sent_label)
            print(sent_score)
            return (True, f"Unwanted emotion {biggest_emotion}")
        else:
            if toxicity_response > 0.8:
                return (True, "Toxicity score very high")
            return (False, "Does not contain an unwanted emotion OR seems to be very pos/neutral")

    # zero shot classification
    zero_shot = zero_shot_classifier(message, zero_shot_labels, multi_label=True)
    for label in zero_shot["labels"]:
        if (zero_shot_labels["scores"][zero_shot_labels["labels"].index(label)] > 0.8):
            return (True, f"Message contains custom label {label}")

    return (False, "Not negative, does not contain unwanted emotion, low toxicity score, and does not contain custom filters")

if __name__ == "__main__":
    # neg_bad = False
    # unwanted_emotions = []
    # zero_shot_labels = []
    #
    #
    #
    #
    # # whether the message is positive, negative, or neutral
    # base_message = pos_neg_neu_model("U joking or fr?")
    # sent_label = base_message[0]["label"]
    # sent_score = base_message[0]["score"]
    # # emotion of the message
    # print(base_message)

    google_api_client = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=API_KEY,
        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
        static_discovery=False,
    )

    analyze_request = {
        'comment': {'text': 'friendly greetings from python'},
        'requestedAttributes': {'TOXICITY': {}}
    }

    response = google_api_client.comments().analyze(body=analyze_request).execute()
    response = float(json.dumps(response["attributeScores"]["TOXICITY"]["summaryScore"]["value"], indent=2))



    print(response)
    print(type(response))

