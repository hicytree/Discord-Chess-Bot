from io import StringIO
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
    global piece_turn
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
    piece_turn = 0

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
async def place(ctx, pos1: str, pos2: str):
    global turn
    global piece_turn

    if(game_started == False):
        print("games hasnt started hoe")
        return

    if(ctx.author != turn):
        await ctx.send("Please wait for your turn.")
        return

    pos1 = pos1.lower()
    pos2 = pos2.lower()

    if(not is_valid_pos(pos1, pos2)):
        await ctx.send("Please enter valid positions.")
        return

    or_x, or_y = find_coor(pos1)

    dest_x, dest_y = find_coor(pos2)

    if(not check_rules(or_x, or_y, dest_x, dest_y)):
        await ctx.send("Please enter valid positions.")
        return
    
    board[dest_x][dest_y] = board[or_x][or_y] 
    board[or_x][or_y] = 0

    await draw_board(ctx)

    moved_piece = board[dest_x][dest_y]
    if(moved_piece == 1 or moved_piece == 7):
        await ctx.send(f"Pawn placed at {pos2.upper()}.")
    elif(moved_piece == 2 or moved_piece == 8):
        await ctx.send(f"Rook placed at {pos2.upper()}.")
    elif(moved_piece == 3 or moved_piece == 9):
        await ctx.send(f"Knight placed at {pos2.upper()}.")
    elif(moved_piece == 4 or moved_piece == 10):
        await ctx.send(f"Bishop placed at {pos2.upper()}.")
    elif(moved_piece == 5 or moved_piece == 11):
        await ctx.send(f"Queen placed at {pos2.upper()}.")
    elif(moved_piece == 6 or moved_piece == 12):
        await ctx.send(f"King placed at {pos2.upper()}.")
    
    if(await check_win_con(ctx)):
        return
    else:
        if(turn == player1):
            turn = player2
            await ctx.send(f"It is {player2}'s turn.")
        else:
            turn = player1
            await ctx.send(f"It is {player1}'s turn.")

    piece_turn = 1 - piece_turn
    
def find_coor(str):
    row = -1
    col = -1

    if str[0] == 'a':
        col = 0
    elif str[0] == 'b':
        col = 1
    elif str[0] == 'c':
        col = 2
    elif str[0] == 'd':
        col = 3
    elif str[0] == 'e':
        col = 4
    elif str[0] == 'f':
        col = 5
    elif str[0] == 'g':
        col = 6
    elif str[0] == 'h':
        col = 7

    if str[1] == '8':
        row = 0
    elif str[1] == '7':
        row = 1
    elif str[1] == '6':
        row = 2
    elif str[1] == '5':
        row = 3
    elif str[1] == '4':
        row = 4
    elif str[1] == '3':
        row = 5
    elif str[1] == '2':
        row = 6
    elif str[1] == '1':
        row = 7
    
    return row, col

def is_valid_pos(pos1, pos2):
    char_set = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'}
    int_set = {'1', '2', '3', '4', '5', '6', '7', '8'}

    if(pos1[0] not in char_set or pos1[1] not in int_set):
        return False

    if(pos2[0] not in char_set or pos2[1] not in int_set):
        return False

    return True

def check_rules(or_x, or_y, dest_x, dest_y):
    global piece_turn
    poss_moves = set()

    if (piece_turn == 0 and board[or_x][or_y] < 7 and board[or_x][or_y] > 0) or (piece_turn == 1 and board[or_x][or_y] > 6):
        return False
    
    if (piece_turn == 0 and board[dest_x][dest_y] > 6) or (piece_turn == 1 and board[dest_x][dest_y] < 7 and board[dest_x][dest_y] > 0):
        return False
    
    if board[or_x][or_y] == 1:
        if is_on_board(or_x + 1, or_y + 1) and board[or_x + 1][or_y + 1] > 6:
            poss_moves.add((or_x + 1, or_y + 1))
        
        if is_on_board(or_x + 1, or_y - 1) and board[or_x + 1][or_y - 1] > 6:
            poss_moves.add((or_x + 1, or_y - 1))
            
        if or_x == 1 and board[or_x + 2][or_y] == 0 and board[or_x + 1][or_y] == 0:
            poss_moves.add((or_x + 2, or_y))

        if is_on_board(or_x + 1, or_y) and board[or_x + 1][or_y] == 0:
            poss_moves.add((or_x + 1, or_y))

    elif board[or_x][or_y] == 7:
        if is_on_board(or_x - 1, or_y + 1) and board[or_x - 1][or_y + 1] > 0 and board[or_x - 1][or_y + 1] < 7:
            poss_moves.add((or_x - 1, or_y + 1))
        
        if is_on_board(or_x - 1, or_y - 1) and board[or_x - 1][or_y - 1] > 0 and board[or_x - 1][or_y - 1] < 7:
            poss_moves.add((or_x - 1, or_y - 1))
            
        if or_x == 6 and board[or_x - 2][or_y] == 0 and board[or_x - 1][or_y] == 0:
            poss_moves.add((or_x - 2, or_y))

        if is_on_board(or_x - 1, or_y) and board[or_x - 1][or_y] == 0:
            poss_moves.add((or_x - 1, or_y))

    if((dest_x, dest_y) in poss_moves):
        return True
    else: 
        return False

def is_on_board(x, y):
    if x >= 0 and x < 8 and y >= 0 and y < 8:
        return True
    else:
        return False 

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
    return False
    '''
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
    '''

bot.run(TOKEN)