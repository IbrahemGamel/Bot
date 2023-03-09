from bot import MyClient
import discord
import os
from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
  return "Bot up and running"


if __name__ == '__main__':
  my_secret = os.environ['token']
  TOKEN = my_secret
  bot = MyClient
  bot.run_bot(discord.Client, TOKEN)
  # app.run(host='0.0.0.0', port='9082')
