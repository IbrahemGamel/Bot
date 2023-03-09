import discord
from responses import vouch, init, sync_me, total_trades, add_mods, remove_mods, set_trades
import asyncio, random
from flask import Flask




  
class MyClient(discord.Client):
    def run_bot(self, TOKEN):
    
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        self.client = MyClient(intents=intents)
        self.client.run(TOKEN)
        
      
    async def on_ready(self):
        self.client.loop.create_task(self.update_status())
        
    async def update_status(self):
      await self.client.wait_until_ready()  # Wait until the client is ready
      while not self.client.is_closed():  # Keep updating the status as long as the client is running
          presenence = random.choice(['With BCTC', 'With Blasome'])
          await self.client.change_presence(activity=discord.Game(presenence))  # Update the bot's status
          await asyncio.sleep(300)  # Wait for 5 minutes before updating again
        

    
    async def on_message(self, message):
        
        if message.author == self.user:
            return
        
        prefex = message.content.split(' ')[0]
        def create_embed(m):
            return discord.Embed(description=m, color=discord.Color.red())

        match prefex:
            
            case "+vouch":
                await vouch(self, message)
                
            case "+init":
                if message.author.guild_permissions.administrator:
                    await init(self, message)
                    await message.channel.send(embed=discord.Embed(description='Created All Users',               
                                                                  color=discord.Color.green()), reference=message)
                    
                else:
                    await message.channel.send(embed=create_embed('Command is for Admins only'), reference=message)
            
            case "+syncme":
                await sync_me(self, message)
            
            case "+totaltrades":
                await total_trades(self, message)
                
            case "+addmod":
                if message.author.guild_permissions.administrator:
                    await add_mods(self, message)
                else:
                    await message.channel.send(embed=create_embed('Command is for Admins only'), reference=message)
            
            case "+removemod":
                if message.author.guild_permissions.administrator:
                    await remove_mods(self, message)
                else:
                    await message.channel.send(embed=create_embed('Command is for Admins only'), reference=message)
            
            case "+settrades":
                await set_trades(self, message)
              
    
 
