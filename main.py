 from discord.ext import commands 
from discord import Intents
from discord.ui import Button, View
import discord, asyncio, random
import pandas as pd
from datetime import datetime, timezone

intents = Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)
IDS = []

user_choose = {}
users_point = {}
users_cl = []
round1 = []
game_going = {"cancel": False, "host": 0}  

@bot.event
async def on_ready():
    print(f"{bot.user} is ready")
    
class Join(View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label='JOIN!', style=discord.ButtonStyle.blurple)
    async def join(self,  interaction: discord.Interaction, button: discord.ui.Button):
     users_point[interaction.user.id] = 0
     user_choose[interaction.user.id] = 0
     if users_point[interaction.user.id] in users_point.keys():
        await interaction.response.send_message("You already joined the game!")
     else:
        await interaction.response.send_message(f"<@{interaction.user.id}> you have successfully joined the game!", ephemeral=True)
      
     await asyncio.sleep(30)
     button.disabled = True
     await interaction.message.edit(view=self)

    @discord.ui.button(label="Cancel Game!", style=discord.ButtonStyle.danger)
    async def quitgame(self,  interaction: discord.Interaction, button: discord.ui.Button):
       if game_going["host"] == interaction.user.id:
          await interaction.response.send_message("game cancelled.")
          game_going["cancel"] = True
          button.disabled = True 
          game_going["host"] = 0
          await interaction.response.edit_message(view=self)
          await interaction.response.send_message("game cancelled.")
       else:
          emb = discord.Embed(description="Only host can cancel the game!", color=discord.Color.red())
          emb.set_author(name=interaction.user.name, icon_url=interaction.user.avatar) 
          await interaction.response.send_message(embed=emb, ephemeral=True)

class MyButton(Button):    
   def __init__(self, label):
       super().__init__(label=label, style=discord.ButtonStyle.success)

   async def callback(self, interaction: discord.Interaction):
    if interaction.user.id not in list(users_point.keys()):
       emb = discord.Embed(description="You haven't joined the game", color=discord.Color.red())
       emb.set_author(url=interaction.user.avatar)
       await interaction.response.send_message(embed=emb, ephemeral=True)

    user_choose[interaction.user.id] = int(self.label)

    if interaction.user.id in users_cl:
        await interaction.response.send_message("You clicked already.", ephemeral=True)
    else:
       if int(user_choose[interaction.user.id]) == round1[len(round1) - 1]:
         users_cl.append(interaction.user.id)
         users_point[interaction.user.id] += 1
         
       else:
         users_cl.append(interaction.user.id)
       await interaction.response.send_message(f"You picked your answer: **{self.label}**", ephemeral=True)

@bot.command()
async def test(ctx, buttons: int, rounds: int):
    game_going["host"] = ctx.author.id
    embed2 = discord.Embed(title="Which cup has the coin?", description=f"**Rules:**\n\n - From {buttons} buttons you have to click on a button which you think has the coin.\n - You can choose 1 option only.\n - If you guess it correct you earn 1 point.\n - Person with maximum points afmter `{rounds}` round wins!\n - Game starts after 30s.")
    await ctx.send(embed=embed2, view=Join())
    await asyncio.sleep(30)

    if game_going["cancel"] == False:
       kek = [f"<@{item}>" for item in list(users_point.keys())]
       xx = pd.Series(index=kek)

       embed3 = discord.Embed(title="All players that joined:", description=f'**Total players:** {len(users_point.keys())}\n {str(xx).removeprefix("NaN").removesuffix("dtype: float64")}', color=discord.Color.green())
       embed3.set_footer(text="Game starting in 10 seconds!")
       await ctx.send(embed=embed3)
    else:
       pass 
   
    while game_going["cancel"] == False:
       await asyncio.sleep(10)   
       xx = []
   
       for i in range(1, int(buttons) + 1):
           button = MyButton(f"{i}")
           xx.append(button)
   
       view = View()
   
       for i in xx:
           view.add_item(i)   

       for j in range(1, rounds+1):
           if game_going["cancel"] == True:
              break 
           else:
              embed = discord.Embed(title=f"Which cup has a coin?, Round {j}", description="`" + "🥤"*buttons + "`")  
              await ctx.send(embed=embed, view=view)
              no = random.randrange(1, buttons)
              round1.append(no)
              users_cl.clear()
      
              await asyncio.sleep(20)
           
              embb = discord.Embed(title=f"Number of round {j}", description=f"The number was **{no}**. Goodluck.", color=discord.Color.green())
              await ctx.send(embed=embb)

       values = [f"**{item}**" for item in list(users_point.values())]
       users = [f"<@{user}>" for user in list(users_point.keys())]
       x = pd.Series(values, users)

       em = discord.Embed(title="**ScoreCard of the cups game:\n\n** ", description=str(x).removesuffix("dtype: object"), color=discord.Color.blue())
       em.timestamp = datetime.now(timezone.utc)
       await ctx.send(embed=em)

    user_choose.clear()
    users_point.clear()
    game_going["cancel"] = True
    game_going["host"] = 0
    round1.clear()

# bot.run("token")
