from transformers import pipeline
from nltk.sentiment.vader import SentimentIntensityAnalyzer

pos_neg_neu_model = pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")

strongest_emotion_model = pipeline("text-classification", model='bhadresh-savani/distilbert-base-uncased-emotion')
all_emotion_model = pipeline("text-classification", model='bhadresh-savani/distilbert-base-uncased-emotion',
                             return_all_scores=True)
zero_shot_classifier = pipeline("zero-shot-classification",
                                model="facebook/bart-large-mnli")
vader = SentimentIntensityAnalyzer()
