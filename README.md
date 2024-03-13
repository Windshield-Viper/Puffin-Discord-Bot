# Puffin Discord Bot
The rise in social media users in recent years has made community content moderation difficult. Here's my attempt at changing that, with an open-source Discord bot that aims to help moderators keep their communities safer.

[Bot Invite Link](https://discord.com/api/oauth2/authorize?client_id=1185076125752365136&permissions=1376537085952&scope=bot)

[Top.gg link](https://top.gg/bot/1185076125752365136)

Puffin is an auto-moderation Discord bot utilizing sentiment analysis and zero-shot learning. In addition, it also uses Google's Toxicity API. Please allow a few seconds for a message to be flagged in a text channel. Feel free to reach out with pull requests, feature requests, bug reports, or any other comments/issues you may have.


<img src="https://github.com/Windshield-Viper/Puffin-Discord-Bot/assets/109366063/0debaaaa-0697-4535-a0b3-f3ea9ee95ff1" width="400">


# Tech Stack
- Puffin is written using `discord.py`
- Database created with `MongoDB`
- Hosted on a Raspberry Pi 5
- ML models integrated using Hugging Face Pipelines

# Methodology
Puffin filters messages based on whether or not they hold specific emotions, their sentiment, zero-shot labels that the user specifies, and more. Flagged messages are added to a moderation queue that can be viewed via an ephemeral message if you have the right permissions. The algorithm used to determine whether or not a message should be flagged can be viewed in `moderation.py`. Future versions will iterate upon this algorithm.

# Citations
Lewis, Mike, et al. ‘BART: Denoising Sequence-to-Sequence Pre-Training for Natural Language Generation, Translation, and Comprehension’. *arXiv Preprint arXiv:1910. 13461*, 2019.

Pérez, Juan Manuel, et al. ‘Pysentimiento: A Python Toolkit for Sentiment Analysis and SocialNLP Tasks’. _arXiv [Cs.CL],_ 2021, http://arxiv.org/abs/2106.09462. arXiv.

Sanh, V., Debut, L., Chaumond, J., & Wolf, T. (2019). DistilBERT, a distilled version of BERT: Smaller, faster, cheaper and lighter. _ArXiv_. /abs/1910.01108

“Umbra’s Sync Command.” _Umbra’s Rantings_, 29 Jan. 2023, https://about.abstractumbra.dev/discord.py/2023/01/29/sync-command-example.html.
