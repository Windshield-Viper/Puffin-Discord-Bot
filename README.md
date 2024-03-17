# Puffin Discord Bot
The rise in social media users in recent years has made community content moderation difficult. Here's my attempt at changing that, with an open-source Discord bot that aims to help moderators keep their communities safer.

[Bot Invite Link](https://discord.com/api/oauth2/authorize?client_id=1185076125752365136&permissions=1376537085952&scope=bot)

[Top.gg link](https://top.gg/bot/1185076125752365136)

Puffin is an auto-moderation Discord bot utilizing sentiment analysis and zero-shot learning. Please allow a few seconds for a message to be flagged in a text channel. Feel free to reach out with pull requests, feature requests, bug reports, or any other comments/issues you may have.


<img src="https://github.com/Windshield-Viper/Puffin-Discord-Bot/assets/109366063/0debaaaa-0697-4535-a0b3-f3ea9ee95ff1" width="400">


# Tech Stack
- Puffin is written using `discord.py`
- Database created with `MongoDB`
- Hosted on a Raspberry Pi 5
- ML models integrated using Hugging Face Pipelines
- ML model fine-tuned on Discord and Twitter data using Hugging Face Transformers

# Methodology
Puffin filters messages based on whether or not they hold specific emotions, their sentiment, zero-shot labels that the user specifies, and more. Flagged messages are added to a moderation queue that can be viewed via an ephemeral message if you have the right permissions. The algorithm used to determine whether or not a message should be flagged can be viewed in `moderation.py`. Future versions will iterate upon this algorithm. A custom-trained model trained on Discord and Twitter data is used. 

# Selected Citations
Devlin, Jacob, et al. BERT: Pre-Training of Deep Bidirectional Transformers for Language Understanding. arXiv:1810.04805, arXiv, 24 May 2019. arXiv.org, https://doi.org/10.48550/arXiv.1810.04805.
“Facebook: Global Daily Active Users 2023.” Statista, https://www.statista.com/statistics/346167/facebook-global-dau/. Accessed 15 Mar. 2024.
Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text. Eighth International Conference on Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014.
Lewis, Mike, et al. ‘BART: Denoising Sequence-to-Sequence Pre-Training for Natural Language Generation, Translation, and Comprehension’. arXiv Preprint arXiv:1910. 13461, 2019.
Pérez, Juan Manuel, et al. ‘Pysentimiento: A Python Toolkit for Sentiment Analysis and SocialNLP Tasks’. arXiv [Cs.CL], 2021, http://arxiv.org/abs/2106.09462. arXiv.
Ribeiro, Marco Tulio, et al. “Why Should I Trust You?”: Explaining the Predictions of Any Classifier. arXiv:1602.04938, arXiv, 9 Aug. 2016. arXiv.org, https://doi.org/10.48550/arXiv.1602.04938.
Sanh, V., Debut, L., Chaumond, J., & Wolf, T. (2019). DistilBERT, a distilled version of BERT: Smaller, faster, cheaper and lighter. ArXiv. /abs/1910.01108


