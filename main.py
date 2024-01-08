import bot
import signal
import atexit

import sys
import atexit
import signal


def exit_handler():
    print("Stopping puffin bot...")


def kill_handler(*args):
    sys.exit(0)


if __name__ == '__main__':
    # run the bot

    atexit.register(exit_handler)
    signal.signal(signal.SIGINT, kill_handler)
    signal.signal(signal.SIGTERM, kill_handler)

    bot.run_sent_bot()
