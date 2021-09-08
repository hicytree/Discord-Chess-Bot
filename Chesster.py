import os
import random
from dotenv import load_dotenv
import discord
from discord.ext import commands
from PIL import Image

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

    board = [[2, 3, 4, 5, 6, 4, 3, 2], 
             [1, 1, 1, 1, 1, 1, 1, 1], 
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [7, 7, 7, 7, 7, 7, 7, 7],
             [8, 9, 10, 11, 12, 10, 9, 8]]

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

    if(await check_win_con(ctx)):
        return
    else:
        if(turn == player1):
            turn = player2
            await ctx.send(f"It is {player2}'s turn.")
        else:
            turn = player1
            await ctx.send(f"It is {player1}'s turn.")

async def draw_board(ctx):
    cboard = Image.open("chessboard.png")
    cboard = cboard.convert("RGBA")
    
    pieces = Image.open("chesspieces.png")
    pieces = pieces.convert("RGBA")

    width, height = pieces.size
    pieces = pieces.resize((int(0.8 * width), int(0.8 * height)))

    width, height = pieces.size
    width /= 6
    height /= 2

    width = int(width)
    height = int(height)

    wking = pieces.crop((0, 0, width, height))
    wqueen = pieces.crop((width, 0, width * 2, height))
    wbishop = pieces.crop((width * 2, 0, width * 3, height))
    wknight = pieces.crop((width * 3, 0, width * 4, height))
    wrook = pieces.crop((width * 4, 0, width * 5, height))
    wpawn = pieces.crop((width * 5, 0, width * 6, height))

    bking = pieces.crop((0, height, width, height * 2))
    bqueen = pieces.crop((width, height, width * 2, height * 2))
    bbishop = pieces.crop((width * 2, height, width * 3, height * 2))
    bknight = pieces.crop((width * 3, height, width * 4, height * 2))
    brook = pieces.crop((width * 4, height, width * 5, height * 2))
    bpawn = pieces.crop((width * 5, height, width * 6, height * 2))

    displace = 32
    square_size = 97
    curr_x = 0
    curr_y = 0

    for row in board:
        for piece in row:
            if piece == 1:
                cboard.paste(bpawn, (curr_x * square_size + displace, curr_y * square_size + displace), bpawn)
            elif piece == 2:
                cboard.paste(brook, (curr_x * square_size + displace, curr_y * square_size + displace), brook)
            elif piece == 3:
                cboard.paste(bknight, (curr_x * square_size + displace, curr_y * square_size + displace), bknight)
            elif piece == 4:
                cboard.paste(bbishop, (curr_x * square_size + displace, curr_y * square_size + displace), bbishop)
            elif piece == 5:
                cboard.paste(bqueen, (curr_x * square_size + displace, curr_y * square_size + displace), bqueen)
            elif piece == 6:
                cboard.paste(bking, (curr_x * square_size + displace, curr_y * square_size + displace), bking)
            elif piece == 7:
                cboard.paste(wpawn, (curr_x * square_size + displace, curr_y * square_size + displace), wpawn)
            elif piece == 8:
                cboard.paste(wrook, (curr_x * square_size + displace, curr_y * square_size + displace), wrook)
            elif piece == 9:
                cboard.paste(wknight, (curr_x * square_size + displace, curr_y * square_size + displace), wknight)
            elif piece == 10:
                cboard.paste(wbishop, (curr_x * square_size + displace, curr_y * square_size + displace), wbishop)
            elif piece == 11:
                cboard.paste(wqueen, (curr_x * square_size + displace, curr_y * square_size + displace), wqueen)
            elif piece == 12:
                cboard.paste(wking, (curr_x * square_size + displace, curr_y * square_size + displace), wking)

            curr_x += 1
        
        curr_x = 0
        curr_y += 1

    cboard.save("currboard.png")
   
    await ctx.send(file=discord.File('currboard.png'))
        
async def check_win_con(ctx):
    global game_started
    win_true = False

    if(0 not in board):
        await ctx.send(f"The game has ended in a draw between {player1} and {player2}.")
        game_started = False
        return True

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
            return True

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
            return True

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
        return True

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
        return True

bot.run(TOKEN)