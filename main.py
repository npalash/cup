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

class Join(View):
    def __init__(self, user_p: dict, user_c: dict, host: int, game_going: dict):
        super().__init__()
        self.message = None
        self.user_p = user_p
        self.user_c = user_c 
        self.host = host
        self.game_going = game_going

    @discord.ui.button(label='JOIN!', style=discord.ButtonStyle.blurple)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
      self.user_p[interaction.user.id] = 0
      self.user_c[interaction.user.id] = 0
      self.game_going["cancel"] = False 
      await interaction.response.send_message(f"<@{interaction.user.id}> you have successfully joined the game!", ephemeral=True)

      await asyncio.sleep(10)
      button.disabled = True 
      await self.message.edit(view=self)
      
    def joiners(self):
        return self.user_c
    
    @discord.ui.button(label="Cancel Game!", style=discord.ButtonStyle.danger)
    async def quitgame(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.host == interaction.user.id:
            can_emb = discord.Embed(title="Game cancelled!", description="The host thought to cancel the game. Successfully cancelled the game.")
            can_emb.timestamp = datetime.now(timezone.utc)
            await interaction.response.send_message(embed=can_emb)
            self.host = 0
            self.game_going["cancel"] = True 
            self.user_c.clear()
            self.user_p.clear()
            for item in self.children:
                item.disabled = True 
                await self.message.edit(view=self)
            await interaction.response.edit_message(view=self)
        else:
            emb = discord.Embed(description="Only host can cancel the game!", color=discord.Color.red())
            emb.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=emb, ephemeral=True)

class MyButton(Button):     
    def __init__(self, label, user_c: dict, user_p: dict, number: int, user_clicked: list, timeout: int):
        super().__init__(label=label, style=discord.ButtonStyle.success)
        self.number = number 
        self.user_c = user_c
        self.user_p = user_p
        self.user_clicked = user_clicked
        self.timeout = timeout
        self.message = None

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id not in self.user_c:
            emb = discord.Embed(description="You haven't joined the game", color=discord.Color.red())
            emb.set_author(url=interaction.user.avatar.url, name=interaction.user.name)
            await interaction.response.send_message(embed=emb, ephemeral=True)
        else:
            self.user_c[interaction.user.id] = int(self.label)

            if interaction.user.id in self.user_clicked:
                await interaction.response.send_message("You clicked already.", ephemeral=True)
            else:
                if self.user_c[interaction.user.id] == self.number:
                    self.user_p[interaction.user.id] += 1
                else:
                    self.user_clicked.append(interaction.user.id)
                await interaction.response.send_message(f"You picked your answer: **{self.label}**", ephemeral=True)

@bot.command()
async def test(ctx, buttons: int = 0, rounds: int = 0):
    if buttons == 1 or buttons > 25:
        await ctx.send("Button can't exceed 25 nor it can be just 1 button.")

    elif rounds == 0 or buttons == 0:
        await ctx.send("Usage: .test <number of buttons> <number of rounds to play.>")
    elif rounds > 25 or rounds == 0 and buttons > 1:
        await ctx.send("rounds can't be more than 25 neither 0.")
    elif rounds < 0 or buttons < 0:
        await ctx.send("Rounds or buttons can't be in negative!") 
    elif str(type(buttons)) == "<class 'str'>" or str(type(rounds)) == "<class 'str'>":
        await ctx.send("The arguments buttons and rounds need to be numbers")

    else:
        embed2 = discord.Embed(
        title="Which cup has the coin?",
        description=f"**Rules:**\n\n - From {buttons} buttons you have to click on a button which you think has the coin.\n - You can choose 1 option only.\n - For each round `20 seconds` are given.\n - If you guess it correct you earn 1 point.\n - Person with maximum points after `{rounds}` rounds wins!\n - Game starts after 30s."
    )

        user_c = {}
        user_p = {}
        user_clicked = []
        game_going = {"cancel": False}
    
        join_view = Join(user_c=user_c, user_p=user_p, host=ctx.author.id, game_going=game_going)
        join_message = await ctx.send(embed=embed2, view=join_view)
        join_view.message = join_message
        await ctx.message.delete()
        await asyncio.sleep(30)
    
        if game_going['cancel'] == False:
            kek = [f"<@{item}>" for item in Join(user_c=user_c, user_p=user_p, host=ctx.author.id, game_going=game_going).joiners()]
            xx = pd.Series(index=kek, data=[" "] * len(kek))
        
            embed3 = discord.Embed(
                title="All players that joined:",
                description=f'**Total players:** {len(kek)}\n {str(xx).removesuffix("dtype: object")}',
                color=discord.Color.green()
            )
            embed3.set_footer(text="Game starting in 10 seconds!")
            await ctx.send(embed=embed3)
        else:
            pass 
            
        await asyncio.sleep(10)   
    
        xx = []
    
        for j in range(1, rounds+1):
            if game_going["cancel"] == False:
                no = random.randrange(1, buttons)
                for i in range(1, buttons + 1):
                    button = MyButton(f"{i}", number=no, user_c=user_c, user_p=user_p, user_clicked=user_clicked, timeout=20)
                    xx.append(button)
                view = View()
        
                for s in xx:
                    view.add_item(s)
                embed = discord.Embed(title=f"Which cup has a coin?, Round {j}", description="`" + "🥤"*buttons + "`")  
                cups_message = await ctx.send(embed=embed, view=view)
        
                await asyncio.sleep(20)
        
                button.message = cups_message
                for item in view.children:
                    item.disabled = True
                await cups_message.edit(view=view)
            
                embb = discord.Embed(title=f"Number of round {j}", description=f"The number was **{no}**. Goodluck.", color=discord.Color.green())
                xx.clear()
                user_clicked.clear()
                await ctx.send(embed=embb)
            else:
                pass 
        
        values = [f"**{item}**" for item in list(user_p.values())]
        users = [f"<@{user}>" for user in list(user_p.keys())]
        x = pd.Series(values, users)
        game_going["cancel"] = False
        if len(users) == 0:
            pass 
        else:
            em = discord.Embed(title="**ScoreCard of the cups game:\n\n** ", description=str(x).removesuffix("dtype: object"), color=discord.Color.blue())
            em.timestamp = datetime.now(timezone.utc)
            em.set_footer(text="The game has ended.")
            await ctx.send(embed=em)

@test.error
async def test_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Invalid input! Please enter a valid number for buttons and rounds.")

bot.run("token")
