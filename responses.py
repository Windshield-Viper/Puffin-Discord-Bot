import random
from model import pos_neg_neu_model, emotion_model

def get_response(message: str) -> str:
    p_message = message.lower()

    if p_message == "!sent_bot hello":
        return "Hello from sent_bot!"

    if p_message == "!sent_bot help":
        return ("`Available commands: !sent_bot hello, !sent_bot analyze <message> "
                "(e.g. !sent_bot analyze I love you), !sent_bot help`. Use `-p` at the end of your message to send a "
                "private message.")

    #f p_message == "!sent_bot configure":


    if p_message.startswith("!sent_bot analyze "):

        # whether the message is positive, negative, or neutral
        base_message = pos_neg_neu_model(p_message[18:])
        label = base_message[0]["label"]
        score = base_message[0]["score"]

        # emotion of the message
        emotion_message = emotion_model(p_message[18:])
        emotion_label = emotion_message[0]["label"]
        emotion_score = emotion_message[0]["score"]


        return f"I am {round(score * 100)}% sure that was a `{label}` message. I am {round(emotion_score * 100)}% sure that was a message of emotion `{emotion_label}`."


        # if label == "POS":
        #     return f"I am {round(score * 100)}% sure that was a positive message."
        # elif label == "NEG":
        #     return f"I am {round(score * 100)}% sure that was a negative message."
        # else:
        #     return f"I am {round(score * 100)}% sure that was a neutral message."

    elif p_message.startswith("!"):
        return "Sorry, I don't understand that command. Type 'help' for a list of commands."
