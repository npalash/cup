from discord.ext import commands 
from discord import Intents
from discord.ui import Button, View
import discord, asyncio, random
import pandas as pd
from datetime import datetime, timezone
from traceback import print_exception

intents = Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

class Join(Button):
    def __init__(self, user_p: dict, user_c: dict):
        super().__init__(label='Join the game.', style=discord.ButtonStyle.blurple)
        self.message = None
        self.user_p = user_p
        self.user_c = user_c 

    async def callback(self, interaction: discord.Interaction): 
       if interaction.user.id in self.user_c.keys():
         await interaction.response.send_message("You already joined the game!", ephemeral=True)
         return 
       await interaction.response.send_message(f"<@{interaction.user.id}> you have successfully joined the game!", ephemeral=True)
       self.user_p[interaction.user.id] = 0
       self.user_c[interaction.user.id] = 0

class Quit(Button):
    def __init__(self, user_p: dict, user_c: dict, host: int, game_going: dict):
        super().__init__(label="Cancel", style=discord.ButtonStyle.danger)
        self.message = None
        self.user_p = user_p
        self.user_c = user_c 
        self.host = host
        self.game_going = game_going

    async def callback(self,interaction: discord.Interaction):
        if self.host == interaction.user.id:
            can_emb = discord.Embed(title="Game cancelled!", description="The host thought to cancel the game. Successfully cancelled the game.", color=discord.Color.red())
            can_emb.timestamp = datetime.now(timezone.utc)
            await interaction.response.send_message(embed=can_emb)
            self.host = 0
            self.game_going["cancel"] = True
        
            for item in self.view.children:
                item.disabled = True 
            await self.message.edit(view=self.view)
        else:
            emb = discord.Embed(description="Only host can cancel the game!", color=discord.Color.red())
            emb.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=emb, ephemeral=True)

class MyButton(Button):     
    def __init__(self, label, user_c: dict, user_p: dict, number: int, user_clicked: list, timeout: int, custom_id):
        super().__init__(label=label, style=discord.ButtonStyle.success, custom_id=custom_id)
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
            self.user_c[interaction.user.id] = int(self.custom_id)

            if interaction.user.id in self.user_clicked:
                await interaction.response.send_message("You clicked already.", ephemeral=True)
            else:
                if self.user_c[interaction.user.id] == self.number:
                    self.user_p[interaction.user.id] += 1
                self.user_clicked.append(interaction.user.id)
                await interaction.response.send_message(f"You picked your answer: **{self.custom_id}**", ephemeral=True)

@bot.command() 
async def test(ctx, buttons: int = 0, rounds: int = 0):
    if buttons == 1 or buttons > 24:
        await ctx.send("Button can't exceed 24 nor it can be just 1 button.")
    elif rounds == 0 and buttons == 0:
        await ctx.send("Usage: .test <number of buttons> <number of rounds to play.>")
    elif rounds == 0 or buttons == 0:
        await ctx.send("Buttons or rounds can't be 0.")
    elif rounds < 0 or buttons < 0:
        await ctx.send("Rounds or buttons can't be in negative!")

    else:
        embed2 = discord.Embed(title="Which cup has the coin?", description=f"**Rules:**\n\n - From {buttons} buttons you have to click on a button which you think has the coin.\n - You can choose 1 option only.\n - For each round `20 seconds` are given.\n - If you guess it correct you earn 1 point.\n - Person with maximum points after `{rounds}` rounds wins!\n - Game starts after 30s.")

        user_c = {}
        user_p = {}
        user_clicked = []
        view2 = View()
        game_going = {"cancel": False}

        join_view = Join(user_c=user_c, user_p=user_p)
        quit_ = Quit(user_c=user_c, user_p=user_p, host=ctx.author.id, game_going=game_going)
        view2.add_item(join_view)
        view2.add_item(quit_)
        join_message = await ctx.send(embed=embed2, view=view2)
        join_view.message = join_message
        quit_.message = join_message 
        await ctx.message.delete()

        await asyncio.sleep(30)

        for item in view2.children:
            item.disabled = True
        await join_message.edit(view=view2)

        if len(user_c) == 0 and game_going["cancel"] == False:
            await ctx.send("No one joined the game so we end this here :pensive:")
    
        if game_going['cancel'] == False and len(user_c) > 0:
            kek = [f"<@{item}>" for item in list(user_c.keys())]
         
            embed3 = discord.Embed(title="All players that joined:", description=f'**Total players:** {len(kek)} {"\n".join(kek)}', color=discord.Color.green())
            embed3.set_footer(text="Game starting in 10 seconds!")
            await ctx.send(embed=embed3)
            
        await asyncio.sleep(10)   
    
        for j in range(1, rounds+1):
            if game_going["cancel"] == False and len(kek) > 0:
                no = random.randrange(1, buttons)
                button = [MyButton("🥤", number=no, user_c=user_c, user_p=user_p, user_clicked=user_clicked, timeout=20, custom_id=f"{i}") for i in range(1, buttons+1)]
                view = View()
                
                for item in button:
                    view.add_item(item)
                quitt = Quit(user_c=user_c, user_p=user_p, host=ctx.author.id, game_going=game_going) 
                view.add_item(quitt)
                embed = discord.Embed(title=f"Which cup has a coin?, Round {j}", description="`" + "🥤"*buttons + "`")  
                cups_message = await ctx.send(embed=embed, view=view)
                quitt.message = cups_message
     
                await asyncio.sleep(20)
            
                for item in view.children:
                    item.disabled = True
                await cups_message.edit(view=view)
            
                if game_going["cancel"] == False:
                    embb = discord.Embed(title=f"Number of round {j}", description=f"The number was **{no}**. Goodluck.", color=discord.Color.green())
                    user_clicked.clear()
                    await ctx.send(embed=embb)
        
        if game_going["cancel"] == False:
            values = [f"**{item}**" for item in list(user_p.values())]
            users = [f"<@{user}>" for user in list(user_p.keys())]
            x = pd.Series(values, users)
            game_going["cancel"] = False
            em = discord.Embed(title="**ScoreCard of the cups game:\n\n** ", description=str(x).removesuffix("dtype: object"), color=discord.Color.blue())
            em.timestamp = datetime.now(timezone.utc)
            em.set_footer(text="The game has ended.")
            await ctx.send(embed=em)

@test.error
async def test_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("The number or buttons or rounds must be numbers not something else!")
    else:
        print_exception(error)

bot.run("TOEKN")
