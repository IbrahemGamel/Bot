from bot import MyClient
import discord
import os

if __name__ == '__main__':
  my_secret = 'MTA3MzQ1OTkyODg3MTczMTMyMA.GC9j8F.7kq6pOCe3RFDhc46Vt9eHx6hGTTothZ5tW0HPg'
  TOKEN = my_secret
  bot = MyClient
  bot.run_bot(discord.Client, TOKEN)
  # app.run(host='0.0.0.0', port='9082')
