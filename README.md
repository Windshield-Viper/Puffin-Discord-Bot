# Puffin Discord Bot
The rise in social media users in recent years has made community content moderation difficult. Here's my attempt at changing that, with an open-source Discord bot that aims to help moderators keep their communities safer. Please allow 5-10 seconds for a message to be flagged in a text channel.

Puffin is an auto-moderation Discord bot utilizing sentiment analysis and zero-shot learning. Feel free to reach out with pull requests, feature requests, bug reports, or any other comments/issues you may have.

# Tech Stack
- Bot is written using `discord.py`
- Database created with `MongoDB`
- Hosted on a Raspberry Pi 5
- ML models integrated using Hugging Face Pipelines

# Citations
Lewis, Mike, et al. ‘BART: Denoising Sequence-to-Sequence Pre-Training for Natural Language Generation, Translation, and Comprehension’. *arXiv Preprint arXiv:1910. 13461*, 2019.

Pérez, Juan Manuel, et al. ‘Pysentimiento: A Python Toolkit for Sentiment Analysis and SocialNLP Tasks’. _arXiv [Cs.CL],_ 2021, http://arxiv.org/abs/2106.09462. arXiv.

Sanh, V., Debut, L., Chaumond, J., & Wolf, T. (2019). DistilBERT, a distilled version of BERT: Smaller, faster, cheaper and lighter. _ArXiv_. /abs/1910.01108

“Umbra’s Sync Command.” _Umbra’s Rantings_, 29 Jan. 2023, https://about.abstractumbra.dev/discord.py/2023/01/29/sync-command-example.html.
