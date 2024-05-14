import asyncio
import random
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands
import sys
import requests
from translate import Translator
from Utils.DataBase import create_db, find, update_db, delete

RPS = ['rock','paper','scissors']
SLOT_MACHINE =[":8ball:",":moneybag:",":coin:",":gem:",":cherries:",":money_with_wings:"]
GUESS_URL = "http://127.0.0.1:8000/get-quiz"

class Games(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @app_commands.command(name='rps',description='Feeling lucky? Try Rock/Paper/Scissors with Aiko')
    @app_commands.choices(choices=[
    app_commands.Choice(name="Rock", value="rock"),
    app_commands.Choice(name="Paper", value="paper"),
    app_commands.Choice(name="Scissors", value="scissors"),
    ]
    )
    async def rps(self,interaction:discord.Interaction,choices: str):
        user_id = interaction.user.id
        username = interaction.user.name

        bot_choice = random.choice(RPS)
        rpsEmbeds = discord.Embed(title="Rock Paper Shoot!!!",colour = discord.Colour.random())
        rpsEmbeds.add_field(name="You chose: **" + choices + "**", value="**Bot chose: " + bot_choice + "**", inline=False)
        if((choices==bot_choice=="rock") or (choices==bot_choice=="scissors") or (choices==bot_choice=="paper")):
            rpsEmbeds.add_field(name="Your reward for this round",value="$25", inline=False)
            rpsEmbeds.description = "**Sorry, Tie**"
            await award_points(user_id,username,25)
        elif(choices=="rock"):
            rpsEmbeds.set_image(url="https://media.tenor.com/5XuwpvROzEoAAAAi/rock-paper-scissors-roshambo.gif")
            if(bot_choice== "scissors"):
                rpsEmbeds.description = "**you won** :grin:"
                rpsEmbeds.add_field(name="Your reward for this round",value="$50", inline=False)
                await award_points(user_id,username,50)
            else:
                rpsEmbeds.description = "**You Lost** :sob:"
                rpsEmbeds.add_field(name="Your reward for this round",value="$0", inline=False)
                await award_points(user_id, username, 0)
        elif(choices=="scissors"):
            rpsEmbeds.set_image(url="https://media.tenor.com/NyHqrePBRAEAAAAi/rock-paper-scissors-roshambo.gif")
            if(bot_choice == "paper"):
                rpsEmbeds.description = "**You Won** :grin:"
                rpsEmbeds.add_field(name="Your reward for this round",value="$50", inline=False)
                await award_points(user_id, username, 50)
            else:
                rpsEmbeds.description = "**You Lost** :sob:"
                rpsEmbeds.add_field(name="Your reward for this round",value="$0", inline=False)
                await award_points(user_id, username, 0)
        elif(choices == "paper"):
            rpsEmbeds.set_image(url="https://media.tenor.com/iXeUwKbISiQAAAAi/rock-paper-scissors-roshambo.gif")
            if(bot_choice == "rock"):
                rpsEmbeds.description = "**You Won** :grin:"
                rpsEmbeds.add_field(name="Your reward for this round",value="$50", inline=False)
                await award_points(user_id, username, 50)
            else:
                rpsEmbeds.description = "**You Lost** :sob:"
                rpsEmbeds.add_field(name="Your reward for this round",value="$0", inline=False)
                await award_points(user_id, username, 0)
        await  interaction.response.send_message(embed = rpsEmbeds)


    

    @app_commands.command(name="guess",description="guess the anime/game character...")
    async def guess(self, interaction: discord.Interaction):
        id = random.randint(1,9)
        updated_URL = GUESS_URL+"/"+str(id)
        guessEmbed = discord.Embed(title="Guess the character",colour=discord.Colour.random())
        fetched_data = await fetch_data(updated_URL)
        img = fetched_data["url"]
        ans = fetched_data["name"]
        guessEmbed.set_image(url=img)
        await interaction.response.send_message(embed= guessEmbed)




    @app_commands.command(name='slot',description="Let's see, How much luck do you have...")
    async def slot(self,interaction:discord.Interaction):
        user_id = interaction.user.id
        username = interaction.user.name
        special_emoji = ":money_with_wings:"
        first_box = random.choice(SLOT_MACHINE)
        second_box = random.choice(SLOT_MACHINE)
        third_box = random.choice(SLOT_MACHINE)

        jackpot = "500"
        winningpoint = "250"
        loserpoint = "0"

        slotMachineEmbeds = discord.Embed(title="Jungle Jackpot: Spin Your Way to Riches in the Wild!",colour=discord.Colour.random())
        slotMachineEmbeds.set_thumbnail(url="https://media.tenor.com/QMfaVm3kNy0AAAAi/moneda-girando-spinning.gif")
        if(first_box == second_box == third_box == special_emoji):
            winning_line = first_box+"  "+second_box+"  "+third_box
            slotMachineEmbeds.description = winning_line
            slotMachineEmbeds.add_field(name="Your Reward for this slot", value=":coin: " + jackpot)
            slotMachineEmbeds.set_footer(text="JACKPOT BITCH! You're a winner with this fantastic slot line!✨")
            slotMachineEmbeds.set_image(url="https://c.tenor.com/CSWyS926r04AAAAd/tenor.gif")
            await award_points(user_id,username,500)
        elif(first_box == second_box or first_box == third_box or second_box == third_box):
            winning_line = first_box+"  "+second_box+"  "+third_box
            slotMachineEmbeds.description = winning_line
            slotMachineEmbeds.add_field(name="Your Reward for this slot", value=":coin: " + winningpoint)
            slotMachineEmbeds.set_footer(text="You have less luck than meee!")
            slotMachineEmbeds.set_image(url="https://media.tenor.com/2euepBwORpgAAAAi/diluc-kaeya.gif")
            await award_points(user_id,username,250)
        else:
            winning_line = first_box+"  "+second_box+"  "+third_box
            slotMachineEmbeds.description = winning_line
            slotMachineEmbeds.add_field(name="Your Reward for this slot", value=":coin: " + loserpoint)
            slotMachineEmbeds.set_footer(text="You are a loser bitch...")
            slotMachineEmbeds.set_image(url="https://c.tenor.com/nNQa-ZjLAzgAAAAC/tenor.gif")
            await award_points(user_id,username,0)
        await interaction.response.send_message(embed=slotMachineEmbeds)

    @app_commands.command(name='view_points',description='Shows the points you earned from the games you won against the bot')
    async def view_points_cmd(self, interactions:discord.Interaction,user:discord.Member =None):
        BalanceEmbed = discord.Embed(title="Your wallet balance",colour=discord.Colour.random())
        BalanceEmbed.set_thumbnail(url="https://media.tenor.com/QMfaVm3kNy0AAAAi/moneda-girando-spinning.gif")
        if user is not None:
            user_id = user.id
            points = await find(user_id,1)
        else:
            user_id = interactions.user.id
            user = interactions.user
            points = await find(user_id,1)

        if type(points) == str:
            BalanceEmbed.description = f"{user.mention} hasnt participated in any games yet."
        else:
            BalanceEmbed.description = f"{user.mention}'s points {points}" 
        await interactions.response.send_message(embed=BalanceEmbed)

async def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None
    
async def award_points(user_id,username,points):
    if (await find(user_id)):
        await update_db(user_id=user_id,points=points)
    else:
        await create_db(user_id,username)
        await update_db(user_id=user_id,points=points)

async def setup(bot: commands.Bot):
    # print("Games is loaded")
    await bot.add_cog(Games(bot))