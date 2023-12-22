from transformers import pipeline

pos_neg_neu_model = pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")

emotion_model = pipeline("text-classification", model='bhadresh-savani/distilbert-base-uncased-emotion')
