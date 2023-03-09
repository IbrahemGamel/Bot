from bot import MyClient
import discord
import os

if __name__ == '__main__':
  my_secret = os.environ['token']
  TOKEN = my_secret
  bot = MyClient
  bot.run_bot(discord.Client, TOKEN)
  # app.run(host='0.0.0.0', port='9082')
