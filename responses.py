from db import User, Trade
import discord
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from sqlalchemy import or_
from discord.ext import commands


def create_embed_red(m):
  return discord.Embed(description=m, color=discord.Color.red())


def create_embed_blue(m):
  return discord.Embed(description=m, color=discord.Color.blue())


def create_embed_green(m):
  return discord.Embed(description=m, color=discord.Color.green())


engine = create_engine('sqlite:///DataBase.db')
Session = sessionmaker(bind=engine)
session = Session()


async def increament_user(user_id):
  user = session.query(User).filter(User.user_id == user_id).first()

  if user:
    user.trade_count += 1
    session.commit()
    return True, user.trade_count
  else:
    User.create_user(user_id=user_id, trade_count=1)
    user = session.query(User).filter(User.user_id == user_id).first()
    return True, user.trade_count


async def get_user_trade_count(user_id):
  user = session.query(User).filter(User.user_id == user_id).first()
  if user:
    session.commit()
    return user.trade_count
  else:
    return None


async def set_mod(user_id):
  user = session.query(User).filter(User.user_id == user_id).first()
  if user.is_mod == False:
    user.is_mod = True
    session.commit()
    return True
  else:
    return False


async def remove_mod(user_id):
  user = session.query(User).filter(User.user_id == user_id).first()
  if user.is_mod == True:
    user.is_mod = False
    session.commit()
    return True
  else:
    return False


async def set_trade_count(user_a, user_id, current_trade_count):
  user_a = session.query(User).filter(User.user_id == user_a).first()
  user_b = session.query(User).filter(User.user_id == user_id).first()
  if user_a.is_mod == True:
    trade_count = user_b.trade_count
    user_b.trade_count = current_trade_count
    session.commit()
    return True, trade_count, current_trade_count
  else:
    return False, None, None


@commands.cooldown(1, 30, commands.BucketType.guild)
async def vouch(self, message: discord.message):
  # Reading data in case trade happened before
  try:
    engine = create_engine('sqlite:///DataBase.db')

    Session = sessionmaker(bind=engine)
    session = Session()
  except:
    pass

  user_a = message.author

  # Making sure a user is mentioned
  try:
    user_b = message.mentions[0]
  except IndexError:
    embed = create_embed_red('Please Mention Correctly')
    await message.channel.send(embed=embed, reference=message)
    return

  # Checking trading yourself
  if user_a.id == user_b.id:
    embed = create_embed_red('You can\'t trade with your self')
    await message.channel.send(embed=embed, reference=message)
    return

  # Checking trading a bot
  if user_b.bot:
    embed = create_embed_red('You can\'t trade with a bot')
    await message.channel.send(embed=embed, reference=message)
    return

  # Checking 25 Trades Per Week
  trades_last_week = session.query(Trade).filter(
    or_(user_a.id == Trade.user_a_id,
        user_a.id == Trade.user_b_id), Trade.trade_status == 'Confirmed',
    Trade.time_of_trade > datetime.now() - timedelta(weeks=1))
  limit = 25
  if len(trades_last_week.all()) >= limit:
    availablity_date = trades_last_week.order_by(
      Trade.id).first().time_of_trade + timedelta(weeks=1)

    embed = create_embed_red(
      f'You Have Reached Out Your Limit `{limit}`\nYou Can Trade Again After `{availablity_date}`'
    )
    await message.channel.send(embed=embed, reference=message)
    return

  # Checking same users trade in less than 24 hours
  try:
    tradeList = [
      session.query(Trade).filter(
        user_a.id == Trade.user_a_id, user_b.id == Trade.user_b_id,
        Trade.trade_status == 'Confirmed').order_by(Trade.id.desc()).first()
    ]
    tradeList += [
      session.query(Trade).filter(
        user_b.id == Trade.user_a_id, user_a.id == Trade.user_b_id,
        Trade.trade_status == 'Confirmed').order_by(Trade.id.desc()).first()
    ]

    trade_time = [
      trade.time_of_trade for trade in tradeList if trade is not None
    ][0]

    accepted_trade_time = trade_time + timedelta(hours=24)

    if accepted_trade_time > datetime.now():
      availablity_date = (accepted_trade_time - datetime.now())
      embed = create_embed_red(
        f'You Can Trade With <@{user_b.id}> Again in `[{availablity_date}]`')
      await message.channel.send(embed=embed, reference=message)
      return

  except:
    pass

  description = message.content[7 + len(f'<@{user_b.id}>'):]
  message_embeds = [m.url for m in message.attachments]

  # Making sure Image(s) exists
  if not message_embeds:
    embed = create_embed_red('Please Provide An Image In The Same Message')
    await message.channel.send(embed=embed, reference=message)
    return
  embed = create_embed_green(
    f'Waiting For <@{user_b.id}> To Confirm (5m Timeout)')
  await message.channel.send(embed=embed, reference=message)

  # Waiting for metioned user to confirm
  try:
    msg = await self.client.wait_for(
      "message",
      check=lambda m: m.author == user_b and m.content == "+confirm",
      timeout=300)
    # print(msg)
    embed = create_embed_green(f'Your Trade Is Analysed By Staff... ')
    await message.channel.send(embed=embed, reference=msg)
  except:
    embed = create_embed_red(f'Timeout <@{user_b.id}> Didn\'t Respond In Time')
    await message.channel.send(embed=embed, reference=message)
    return

  # Creating the trade / Sending to Mod Chat

  with open('config.json') as f:
    data = json.load(f)
    mode_verify_channel = data['mod_verify_channel']
    verified_trades_channel = self.client.get_channel(
      data['verified_trades_channel'])
    denied_trades_channel = self.client.get_channel(
      data['denied_trades_channel'])

  mod_channel = self.client.get_channel(mode_verify_channel)

  embed = discord.Embed(
    title=f"Trade Between {message.author} and {message.mentions[0]}",
    description=description,
    color=discord.Color.blue())

  embeds = [embed] + [discord.Embed().set_image(url=m) for m in message_embeds]
  # print(embeds)
  # Accept and Deny
  new_message = await mod_channel.send(embeds=embeds)
  await new_message.add_reaction('✅')
  await new_message.add_reaction('❌')

  reaction, user = await self.client.wait_for(
    "reaction_add",
    check=lambda reaction, user: new_message.author != user and str(
      reaction.emoji) in ['✅', '❌'])

  if reaction.emoji == '✅':
    trade_status = 'Confirmed'
    # Increamenting to users
    a, trade_count_a = await increament_user(user_a.id)
    b, trade_count_b = await increament_user(user_b.id)

    embed = discord.Embed(
      title=f"Trade Between {message.author} and {message.mentions[0]}",
      description=
      f'<@{user_a.id}> Has {trade_count_a} Trades\n<@{user_b.id}> Has {trade_count_b} Trades',
      color=discord.Color.green())
    embed.set_footer(text=f'Trade Verified By <@{user.id}>')
    embeds = [embed] + [
      discord.Embed(color=discord.Color.green()).set_image(url=m)
      for m in message_embeds
    ]

    if a and b:

      await verified_trades_channel.send(embeds=embeds)

      await mod_channel.send(
        f'Trade Confirmed By <@{user.id}>: \n<@{user_a.id}> Has {trade_count_a} Trades\n<@{user_b.id}> Has {trade_count_b} Trades',
        reference=new_message)
      reason = None
    else:
      await verified_trades_channel.send(
        f'Trade Between <@{user_a.id}> and <@{user_b.id}> Failed To Be Recored In DB'
      )

  elif reaction.emoji == '❌':
    trade_status = 'Denied'
    # Adding a reason
    await mod_channel.send(
      'Add A Reason For Denying (No Timeout Please Respond)',
      reference=new_message)

    reason = (await
              self.client.wait_for("message",
                                   check=lambda m: m.author == user)).content
    await mod_channel.send(f'Trade Denied By <@{user.id}>',
                           reference=new_message)

    embed = discord.Embed(
      title=f"Trade Between {message.author} and {message.mentions[0]}",
      description=f'Reason: {reason}',
      color=discord.Color.red())
    embed.set_footer(text=f'Trade Denied By {user}')
    embeds = [embed] + [
      discord.Embed(color=discord.Color.red()).set_image(url=m)
      for m in message_embeds
    ]
    await denied_trades_channel.send(embeds=embeds)

  Trade.create_trade(user_a_id=user_a.id,
                     user_b_id=user_b.id,
                     description=description,
                     picture_url=message_embeds,
                     reason_of_deny=reason,
                     trade_status=trade_status)


async def init(self, message):
  guild = message.guild  # gets the guild object
  member_list = guild.members
  for member in member_list:
    member_roles = member.roles[1:]
    trade_count = sum([
      int(count.name.split(' ')[0]) for count in member_roles
      if 'TRADES' in count.name.upper()
    ])

    User.create_user(user_id=member.id, trade_count=trade_count)


async def total_trades(self, message):
  if message.mentions:
    trade_count = await get_user_trade_count(message.mentions[0].id)
    embed = discord.Embed(
      description=f'<@{message.mentions[0].id}> Trade Count Is {trade_count}',
      color=discord.Color.blue())
    await message.channel.send(embed=embed, reference=message)
  else:
    trade_count = await get_user_trade_count(message.author.id)
    embed = discord.Embed(description=f'Your Trade Count Is {trade_count}',
                          color=discord.Color.blue())
    await message.channel.send(embed=embed, reference=message)


async def remove_mods(self, message):
  mention_list = message.mentions
  if mention_list:
    for mention in mention_list:

      if await remove_mod(mention.id):
        embed = discord.Embed(description=f'<@{mention.id}> Has Been Removed',
                              color=discord.Color.green())
        await message.channel.send(embed=embed)
      else:
        embed = discord.Embed(description=f'<@{mention.id}> Isn\'t a Mod',
                              color=discord.Color.red())
        await message.channel.send(embed=embed)


async def add_mods(self, message):
  mention_list = message.mentions
  if mention_list:
    for mention in mention_list:

      if await set_mod(mention.id):
        embed = discord.Embed(description=f'<@{mention.id}> Has Been Added',
                              color=discord.Color.green())
        await message.channel.send(embed=embed)
      else:
        embed = discord.Embed(description=f'<@{mention.id}> Is Already Mod',
                              color=discord.Color.red())
        await message.channel.send(embed=embed)


async def set_trades(self, message):
  mention_list = message.mentions
  if not mention_list:
    embed = discord.Embed(description='Please Mention Someone',
                          color=discord.Color.red())
    await message.channel.send(embed=embed, reference=message)
    return

  try:
    num = int(message.content.split(' ')[2])
  except:
    embed = discord.Embed(description='Please Provide an Integer',
                          color=discord.Color.red())
    await message.channel.send(embed=embed, reference=message)
    return

  if mention_list:
    user = mention_list[0].id
    a, trade_count, current_trade_count = await set_trade_count(
      message.author.id, user, num)
    if a:
      embed = discord.Embed(
        description=
        f'<@{user}> Trade Count Changed From {trade_count} To {current_trade_count}',
        color=discord.Color.green())
      await message.channel.send(embed=embed, reference=message)
    else:
      embed = discord.Embed(description='Command is for mods only',
                            color=discord.Color.red())
      await message.channel.send(embed=embed, reference=message)


def get_place_values(n: int) -> list:
  return [int(value) * 10**place for place, value in enumerate(str(n)[::-1])]


async def sync_me(self, message):
  trade_count = await get_user_trade_count(message.author.id)
  values = get_place_values(trade_count)
  server_roles = [
    role for role in message.guild.roles[1:] if 'TRADES' in role.name.upper()
  ]
  # print(trade_count)
  [
    await message.author.remove_roles(role) for role in message.author.roles
    if 'TRADES' in role.name.upper()
  ]

  for value in values:
    try:
      role = list(
        filter(lambda x: value == int(x.name.split(' ')[0]), server_roles))[0]
      # print(role)
      await message.author.add_roles(role)
    except:
      pass

  embed = create_embed_green(
    f'Synced your roles according to your trades\nYou have {trade_count} Trades'
  )
  await message.channel.send(embed=embed, reference=message)
