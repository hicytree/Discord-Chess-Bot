import os
import random
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='$')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

game_started = False
num_rows = 3
num_cols = 3

@bot.command(name='start', help='Starts the game between two players')
async def start_game(ctx, p1: discord.Member, p2: discord.Member):
    global board 
    global player1
    global player2
    global turn
    global game_started

    board = [0 for i in range(9)]
    player1 = p1
    player2 = p2

    await ctx.send(f"Game has started between {player1} and {player2}")

    first_turn = random.randint(1, 1)

    if(first_turn):
        turn = p2
        await ctx.send(f"It is {player2}'s turn.")
    else:
        turn = p1
        await ctx.send(f"It is {player1}'s turn.")

    game_started = True

async def has_game_started(ctx):
    return game_started

@bot.command(name='place', help='Places piece in the spot in the board')
@commands.check(has_game_started)
async def place(ctx, row: int, col: int):
    if(ctx.author != turn):
        await ctx.send("Please wait for your turn.")
        return

    position = (row - 1) * num_cols + (col - 1)

    if(turn == player1):
        board[position] = 1
    else:
        board[position] = 2

    await draw_board(ctx)
    await ctx.send(f"Piece placed at row {row} and column {col}.")

async def draw_board(ctx):
    line = ""
    count = 0
    for val in board:
        if(val == 0):
            line += ":white_large_square:"
            count += 1
        elif(val == 1):
            line += ":o2:"
            count += 1
        else:
            line += ":regional_indicator_x:"
            count += 1
        
        if(count == num_cols):
            await ctx.send(line)
            line = ""
            count = 0
        


            



"""
@bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
async def nine_nine(ctx):
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)

@bot.command(name='roll_dice', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))
"""

bot.run(TOKEN)