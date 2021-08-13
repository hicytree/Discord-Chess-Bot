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

    first_turn = random.randint(0, 1)

    if(first_turn):
        turn = p2
        await ctx.send(f"It is {player2}'s turn.")
    else:
        turn = p1
        await ctx.send(f"It is {player1}'s turn.")

    await draw_board(ctx)

    game_started = True

async def has_game_started(ctx):
    return game_started

@bot.command(name='place', help='Places piece in the spot in the board')
@commands.check(has_game_started)
async def place(ctx, row: int, col: int):
    global turn

    if(game_started == False):
        print("games hasnt started hoe")
        return

    if(ctx.author != turn):
        await ctx.send("Please wait for your turn.")
        return

    if(row > num_rows or col > num_cols or row <= 0 or col <= 0):
        await ctx.send("Please enter a valid row/column.")
        return

    position = (row - 1) * num_cols + (col - 1)

    if(board[position] != 0):
        await ctx.send(f"There already is a piece placed at row {row} and column {col}, please try again.")
        return
        
    if(turn == player1):
        board[position] = 1
    else:
        board[position] = 2

    await draw_board(ctx)
    await ctx.send(f"Piece placed at row {row} and column {col}.")

    await check_win_con(ctx)

    if(turn == player1):
        turn = player2
        await ctx.send(f"It is {player2}'s turn.")
    else:
        turn = player1
        await ctx.send(f"It is {player1}'s turn.")

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
        
async def check_win_con(ctx):
    global game_started
    win_true = False

    if(0 not in board):
        await ctx.send(f"The game has ended in a draw between {player1} and {player2}.")
        game_started = False
        return

    if(turn == player1):
        piece = 1
    else:
        piece = 2

    for i in range(num_rows):
        not_won = True
        for j in range(num_cols):
            position = i * num_cols + j
            if(board[position] != piece):
                not_won = False
                break
        win_true = not_won

        if(win_true):
            await ctx.send(f"Congrats player {turn} on winning the game!")
            game_started = False
            return

    for i in range(num_cols):
        not_won = True
        for j in range(num_rows):
            position = j * num_rows + i
            if(board[position] != piece):
                not_won = False
                break
        win_true = not_won

        if(win_true):
            await ctx.send(f"Congrats player {turn} on winning the game!")
            game_started = False
            return

    curr_row = 0
    curr_col = 0
    
    not_won = True
    while(curr_row < num_rows and curr_col < num_cols):
        position = curr_row * num_cols + curr_col
        if(board[position] != piece):
            not_won = False
            break
        curr_row += 1
        curr_col += 1
    win_true = not_won

    if(win_true):
        await ctx.send(f"Congrats player {turn} on winning the game!")
        game_started = False
        return  

    curr_row = 2
    curr_col = 0

    not_won = True
    while(curr_row >= 0 and curr_col < num_cols):
        position = curr_row * num_cols + curr_col
        if(board[position] != piece):
            not_won = False
            break
        curr_row -= 1
        curr_col += 1
    win_true = not_won

    if(win_true):
        await ctx.send(f"Congrats player {turn} on winning the game!")
        game_started = False
        return

bot.run(TOKEN)