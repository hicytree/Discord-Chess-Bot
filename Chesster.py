from io import StringIO
import os
import random
from dotenv import load_dotenv
import discord
from discord.ext import commands
from PIL import Image
import copy

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
    
    global white_rook_1_moved
    global white_rook_2_moved
    global white_king_moved

    global black_rook_1_moved
    global black_rook_2_moved
    global black_king_moved

    white_rook_1_moved = False
    white_rook_2_moved = False
    white_king_moved = False

    black_rook_1_moved = False
    black_rook_2_moved = False
    black_king_moved = False

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

    #check if piece trying to move is your piece
    if (piece_turn == 0 and board[or_x][or_y] < 7 and board[or_x][or_y] > 0) or (piece_turn == 1 and board[or_x][or_y] > 6):
        await ctx.send("Please enter valid positions.")
        return
    
    if (piece_turn == 0 and board[dest_x][dest_y] > 6) or (piece_turn == 1 and board[dest_x][dest_y] < 7 and board[dest_x][dest_y] > 0):
        await ctx.send("Please enter valid positions.")
        return

    #check if piece movement matches chess rules for piece movement
    if(not check_rules(or_x, or_y, dest_x, dest_y)):
        await ctx.send("Please enter valid positions.")
        return
    
    board[dest_x][dest_y] = board[or_x][or_y] 
    board[or_x][or_y] = 0

    if piece_turn == 0 and board[dest_x][dest_y] == 7 and dest_x == 0:
        await ctx.send("What do you want to promote your pawn into?\n1 for rook\n2 for knight\n3 for bishop\n4 for queen")
        
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and msg.content in ["1", "2", "3", "4"]

        msg = await bot.wait_for("message", check=check)
        if msg.content == "1":
            board[dest_x][dest_y] = 8
        elif msg.content == "2":
            board[dest_x][dest_y] = 9
        elif msg.content == "3":
            board[dest_x][dest_y] = 10
        elif msg.content == "4":
            board[dest_x][dest_y] = 11
    elif piece_turn == 1 and board[dest_x][dest_y] == 7 and dest_x == 7:
        await ctx.send("What do you want to promote your pawn into?\n1 for rook\n2 for knight\n3 for bishop\n4 for queen")
        
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and msg.content in ["1", "2", "3", "4"]

        msg = await bot.wait_for("message", check=check)
        if msg.content == "1":
            board[dest_x][dest_y] = 2
        elif msg.content == "2":
            board[dest_x][dest_y] = 3
        elif msg.content == "3":
            board[dest_x][dest_y] = 4
        elif msg.content == "4":
            board[dest_x][dest_y] = 5

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
    
#convert chess positions to index of board array
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

#given a position on the board with a piece, check if the piece can move to the destination according to chess rules
def check_rules(or_x, or_y, dest_x, dest_y):
    global piece_turn
    global board
    
    global white_rook_1_moved
    global white_rook_2_moved
    global white_king_moved

    global black_rook_1_moved
    global black_rook_2_moved
    global black_king_moved
    
    poss_moves = set()
    castle1 = False
    castle2 = False
    castle3 = False
    castle4 = False

    in_check = False
    king_row = -1
    king_col = -1

    if piece_turn == 0:
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] == 12:
                    king_row = i
                    king_col = j
    else:
         for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] == 6:
                    king_row = i
                    king_col = j

    if pos_is_threatened(king_row, king_col):
        in_check = True

    #black pawn functionality
    if board[or_x][or_y] == 1:
        if is_on_board(or_x + 1, or_y + 1) and board[or_x + 1][or_y + 1] > 6:
            poss_moves.add((or_x + 1, or_y + 1))
        
        if is_on_board(or_x + 1, or_y - 1) and board[or_x + 1][or_y - 1] > 6:
            poss_moves.add((or_x + 1, or_y - 1))
            
        if or_x == 1 and board[or_x + 2][or_y] == 0 and board[or_x + 1][or_y] == 0:
            poss_moves.add((or_x + 2, or_y))

        if is_on_board(or_x + 1, or_y) and board[or_x + 1][or_y] == 0:
            poss_moves.add((or_x + 1, or_y))
    
    #black rook functionality
    elif board[or_x][or_y] == 2:
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] == 0:
            poss_moves.add((temp_x + 1, temp_y))        
            temp_x += 1

        if is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] > 6:
            poss_moves.add((temp_x + 1, temp_y))        
        
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] == 0:
            poss_moves.add((temp_x - 1, temp_y))        
            temp_x -= 1
        
        if is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] > 6:
            poss_moves.add((temp_x - 1, temp_y))        

        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] == 0:
            poss_moves.add((temp_x, temp_y + 1))        
            temp_y += 1

        if is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] > 6:
            poss_moves.add((temp_x, temp_y + 1))       
        
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] == 0:
            poss_moves.add((temp_x , temp_y - 1))        
            temp_y -= 1
        
        if is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] > 6:
            poss_moves.add((temp_x, temp_y - 1))       
    
    #black knight functionality
    elif board[or_x][or_y] == 3:
        if is_on_board(or_x - 2, or_y + 1) and (board[or_x - 2][or_y + 1] == 0 or board[or_x - 2][or_y + 1] > 6):
            poss_moves.add((or_x - 2, or_y + 1)) 
        
        if is_on_board(or_x - 2, or_y - 1) and (board[or_x - 2][or_y - 1] == 0 or board[or_x - 2][or_y - 1] > 6):
            poss_moves.add((or_x - 2, or_y - 1)) 
        
        if is_on_board(or_x - 1, or_y - 2) and (board[or_x - 1][or_y - 2] == 0 or board[or_x - 1][or_y - 2] > 6):
            poss_moves.add((or_x - 1, or_y - 2)) 

        if is_on_board(or_x + 1, or_y - 2) and (board[or_x + 1][or_y - 2] == 0 or board[or_x + 1][or_y - 2] > 6):
            poss_moves.add((or_x + 1, or_y - 2))

        if is_on_board(or_x - 1, or_y + 2) and (board[or_x - 1][or_y + 2] == 0 or board[or_x - 1][or_y + 2] > 6):
            poss_moves.add((or_x - 1, or_y + 2)) 

        if is_on_board(or_x + 1, or_y + 2) and (board[or_x + 1][or_y + 2] == 0 or board[or_x + 1][or_y + 2] > 6):
            poss_moves.add((or_x + 1, or_y + 2))

        if is_on_board(or_x + 2, or_y + 1) and (board[or_x + 2][or_y + 1] == 0 or board[or_x + 2][or_y + 1] > 6):
                poss_moves.add((or_x + 2, or_y + 1)) 
        
        if is_on_board(or_x + 2, or_y - 1) and (board[or_x + 2][or_y - 1] == 0 or board[or_x + 2][or_y - 1] > 6):
            poss_moves.add((or_x + 2, or_y - 1)) 

    #black bishop functionality
    elif board[or_x][or_y] == 4:
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] == 0:
            poss_moves.add((temp_x + 1, temp_y + 1))        
            temp_x += 1
            temp_y += 1

        if is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] > 6:
            poss_moves.add((temp_x + 1, temp_y + 1))        
            
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] == 0:
            poss_moves.add((temp_x + 1, temp_y - 1))        
            temp_x += 1
            temp_y -= 1

        if is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] > 6:
            poss_moves.add((temp_x + 1, temp_y - 1))

        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] == 0:
            poss_moves.add((temp_x - 1, temp_y + 1))        
            temp_x -= 1
            temp_y += 1

        if is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] > 6:
            poss_moves.add((temp_x - 1, temp_y + 1))

        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] == 0:
            poss_moves.add((temp_x - 1, temp_y - 1))        
            temp_x -= 1
            temp_y -= 1

        if is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] > 6:
            poss_moves.add((temp_x - 1, temp_y - 1))

    #black queen functionality
    elif board[or_x][or_y] == 5:
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] == 0:
            poss_moves.add((temp_x + 1, temp_y))        
            temp_x += 1

        if is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] > 6:
            poss_moves.add((temp_x + 1, temp_y))        
        
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] == 0:
            poss_moves.add((temp_x - 1, temp_y))        
            temp_x -= 1
        
        if is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] > 6:
            poss_moves.add((temp_x - 1, temp_y))        

        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] == 0:
            poss_moves.add((temp_x, temp_y + 1))        
            temp_y += 1

        if is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] > 6:
            poss_moves.add((temp_x, temp_y + 1))       
        
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] == 0:
            poss_moves.add((temp_x , temp_y - 1))        
            temp_y -= 1
        
        if is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] > 6:
            poss_moves.add((temp_x, temp_y - 1))

        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] == 0:
            poss_moves.add((temp_x + 1, temp_y + 1))        
            temp_x += 1
            temp_y += 1

        if is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] > 6:
            poss_moves.add((temp_x + 1, temp_y + 1))        
            
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] == 0:
            poss_moves.add((temp_x + 1, temp_y - 1))        
            temp_x += 1
            temp_y -= 1

        if is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] > 6:
            poss_moves.add((temp_x + 1, temp_y - 1))

        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] == 0:
            poss_moves.add((temp_x - 1, temp_y + 1))        
            temp_x -= 1
            temp_y += 1

        if is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] > 6:
            poss_moves.add((temp_x - 1, temp_y + 1))

        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] == 0:
            poss_moves.add((temp_x - 1, temp_y - 1))        
            temp_x -= 1
            temp_y -= 1

        if is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] > 6:
            poss_moves.add((temp_x - 1, temp_y - 1))

    #black king functionality
    elif board[or_x][or_y] == 6:
        if  is_on_board(or_x + 1, or_y) and not pos_is_threatened(or_x + 1, or_y) and (board[or_x + 1][or_y] == 0 or board[or_x + 1][or_y] > 6):
            poss_moves.add((or_x + 1, or_y))

        if is_on_board(or_x - 1, or_y) and not pos_is_threatened(or_x - 1, or_y) and (board[or_x - 1][or_y] == 0 or board[or_x - 1][or_y] > 6):
            poss_moves.add((or_x - 1, or_y))

        if is_on_board(or_x, or_y + 1) and not pos_is_threatened(or_x, or_y + 1) and (board[or_x][or_y + 1] == 0 or board[or_x][or_y + 1] > 6):
            poss_moves.add((or_x, or_y + 1))

        if is_on_board(or_x, or_y - 1) and not pos_is_threatened(or_x, or_y - 1) and (board[or_x][or_y - 1] == 0 or board[or_x][or_y - 1] > 6):
            poss_moves.add((or_x, or_y - 1))

        if is_on_board(or_x + 1, or_y + 1) and not pos_is_threatened(or_x + 1, or_y + 1) and (board[or_x + 1][or_y + 1] == 0 or board[or_x + 1][or_y + 1] > 6):
            poss_moves.add((or_x + 1, or_y + 1))

        if is_on_board(or_x + 1, or_y - 1) and not pos_is_threatened(or_x + 1, or_y - 1) and (board[or_x + 1][or_y - 1] == 0 or board[or_x + 1][or_y - 1] > 6):
            poss_moves.add((or_x + 1, or_y - 1))

        if is_on_board(or_x - 1, or_y + 1) and not pos_is_threatened(or_x - 1, or_y + 1) and (board[or_x - 1][or_y + 1] == 0 or board[or_x - 1][or_y + 1] > 6):
            poss_moves.add((or_x - 1, or_y + 1))

        if is_on_board(or_x - 1, or_y - 1) and not pos_is_threatened(or_x - 1, or_y - 1) and (board[or_x - 1][or_y - 1] == 0 or board[or_x - 1][or_y - 1] > 6):
            poss_moves.add((or_x - 1, or_y - 1))

        if black_rook_1_moved == False and black_king_moved == False and board[0][0] == 2 and not pos_is_threatened(0, 0) and not pos_is_threatened(0, 1) and not pos_is_threatened(0, 2) and not pos_is_threatened(0, 3) and not pos_is_threatened(0, 4) and board[0][1] == 0 and board[0][2] == 0 and board[0][3] == 0:
            poss_moves.add((0, 2))
            castle1 = True

        if black_rook_2_moved == False and black_king_moved == False and board[0][7] == 2 and not pos_is_threatened(0, 4) and not pos_is_threatened(0, 5) and not pos_is_threatened(0, 6) and not pos_is_threatened(0, 7)  and board[0][5] == 0 and board[0][6] == 0:
            poss_moves.add((0, 6))
            castle2 = True

    #white pawn functionality
    elif board[or_x][or_y] == 7:
        if is_on_board(or_x - 1, or_y + 1) and board[or_x - 1][or_y + 1] > 0 and board[or_x - 1][or_y + 1] < 7:
            poss_moves.add((or_x - 1, or_y + 1))
        
        if is_on_board(or_x - 1, or_y - 1) and board[or_x - 1][or_y - 1] > 0 and board[or_x - 1][or_y - 1] < 7:
            poss_moves.add((or_x - 1, or_y - 1))
            
        if or_x == 6 and board[or_x - 2][or_y] == 0 and board[or_x - 1][or_y] == 0:
            poss_moves.add((or_x - 2, or_y))

        if is_on_board(or_x - 1, or_y) and board[or_x - 1][or_y] == 0:
            poss_moves.add((or_x - 1, or_y))
    
    #white rook functionality
    elif board[or_x][or_y] == 8:
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] == 0:
            poss_moves.add((temp_x + 1, temp_y))        
            temp_x += 1
        
        if is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] > 0 and board[temp_x + 1][temp_y] < 7:
            poss_moves.add((temp_x + 1, temp_y))        
        
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] == 0:
            poss_moves.add((temp_x - 1, temp_y))        
            temp_x -= 1
        
        if is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] > 0 and board[temp_x - 1][temp_y] < 7:
            poss_moves.add((temp_x - 1, temp_y))   
        
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] == 0:
            poss_moves.add((temp_x, temp_y + 1))        
            temp_y += 1
        
        if is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] > 0 and board[temp_x][temp_y + 1] < 7:
            poss_moves.add((temp_x, temp_y + 1))   
        
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] == 0:
            poss_moves.add((temp_x , temp_y - 1))        
            temp_y -= 1

        if is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] > 0 and board[temp_x][temp_y - 1] < 7:
            poss_moves.add((temp_x, temp_y - 1))

    #white knight functionality
    elif board[or_x][or_y] == 9:
        if is_on_board(or_x - 2, or_y + 1) and (board[or_x - 2][or_y + 1] < 7):
            poss_moves.add((or_x - 2, or_y + 1)) 
        
        if is_on_board(or_x - 2, or_y - 1) and (board[or_x - 2][or_y - 1] < 7):
            poss_moves.add((or_x - 2, or_y - 1)) 
        
        if is_on_board(or_x - 1, or_y - 2) and (board[or_x - 1][or_y - 2]< 7):
            poss_moves.add((or_x - 1, or_y - 2)) 

        if is_on_board(or_x + 1, or_y - 2) and (board[or_x + 1][or_y - 2] < 7):
            poss_moves.add((or_x + 1, or_y - 2))

        if is_on_board(or_x - 1, or_y + 2) and (board[or_x - 1][or_y + 2] < 7):
            poss_moves.add((or_x - 1, or_y + 2)) 

        if is_on_board(or_x + 1, or_y + 2) and (board[or_x + 1][or_y + 2] < 7):
            poss_moves.add((or_x + 1, or_y + 2))

        if is_on_board(or_x + 2, or_y + 1) and (board[or_x + 2][or_y + 1] < 7):
                poss_moves.add((or_x + 2, or_y + 1)) 
        
        if is_on_board(or_x + 2, or_y - 1) and (board[or_x + 2][or_y - 1] < 7):
            poss_moves.add((or_x + 2, or_y - 1))  
        
    #white bishop functionality
    elif board[or_x][or_y] == 10:
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] == 0:
            poss_moves.add((temp_x + 1, temp_y + 1))        
            temp_x += 1
            temp_y += 1

        if is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] > 0 and board[temp_x + 1][temp_y + 1] < 7:
            poss_moves.add((temp_x + 1, temp_y + 1))        
            
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] == 0:
            poss_moves.add((temp_x + 1, temp_y - 1))        
            temp_x += 1
            temp_y -= 1

        if is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] > 0 and board[temp_x + 1][temp_y - 1] < 7:
            poss_moves.add((temp_x + 1, temp_y - 1))

        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] == 0:
            poss_moves.add((temp_x - 1, temp_y + 1))        
            temp_x -= 1
            temp_y += 1

        if is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] > 0 and board[temp_x - 1][temp_y + 1] < 7:
            poss_moves.add((temp_x - 1, temp_y + 1))

        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] == 0:
            poss_moves.add((temp_x - 1, temp_y - 1))        
            temp_x -= 1
            temp_y -= 1

        if is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] > 0 and board[temp_x - 1][temp_y - 1] < 7:
            poss_moves.add((temp_x - 1, temp_y - 1))
    
    #white queen functionality
    elif board[or_x][or_y] == 11:
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] == 0:
            poss_moves.add((temp_x + 1, temp_y))        
            temp_x += 1
        
        if is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] > 0 and board[temp_x + 1][temp_y] < 7:
            poss_moves.add((temp_x + 1, temp_y))        
        
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] == 0:
            poss_moves.add((temp_x - 1, temp_y))        
            temp_x -= 1
        
        if is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] > 0 and board[temp_x - 1][temp_y] < 7:
            poss_moves.add((temp_x - 1, temp_y))   
        
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] == 0:
            poss_moves.add((temp_x, temp_y + 1))        
            temp_y += 1
        
        if is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] > 0 and board[temp_x][temp_y + 1] < 7:
            poss_moves.add((temp_x, temp_y + 1))   
        
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] == 0:
            poss_moves.add((temp_x , temp_y - 1))        
            temp_y -= 1

        if is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] > 0 and board[temp_x][temp_y - 1] < 7:
            poss_moves.add((temp_x, temp_y - 1))
        
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] == 0:
            poss_moves.add((temp_x + 1, temp_y + 1))        
            temp_x += 1
            temp_y += 1

        if is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] > 0 and board[temp_x + 1][temp_y + 1] < 7:
            poss_moves.add((temp_x + 1, temp_y + 1))        
            
        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] == 0:
            poss_moves.add((temp_x + 1, temp_y - 1))        
            temp_x += 1
            temp_y -= 1

        if is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] > 0 and board[temp_x + 1][temp_y - 1] < 7:
            poss_moves.add((temp_x + 1, temp_y - 1))

        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] == 0:
            poss_moves.add((temp_x - 1, temp_y + 1))        
            temp_x -= 1
            temp_y += 1

        if is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] > 0 and board[temp_x - 1][temp_y + 1] < 7:
            poss_moves.add((temp_x - 1, temp_y + 1))

        temp_x = or_x
        temp_y = or_y

        while is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] == 0:
            poss_moves.add((temp_x - 1, temp_y - 1))        
            temp_x -= 1
            temp_y -= 1

        if is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] > 0 and board[temp_x - 1][temp_y - 1] < 7:
            poss_moves.add((temp_x - 1, temp_y - 1))

    #white king functionality
    elif board[or_x][or_y] == 12:
        if is_on_board(or_x + 1, or_y) and not pos_is_threatened(or_x + 1, or_y) and board[or_x + 1][or_y] < 7:
            poss_moves.add((or_x + 1, or_y))

        if is_on_board(or_x - 1, or_y) and not pos_is_threatened(or_x - 1, or_y) and board[or_x - 1][or_y] < 7:
            poss_moves.add((or_x - 1, or_y))

        if is_on_board(or_x, or_y + 1) and not pos_is_threatened(or_x, or_y + 1) and board[or_x][or_y + 1] < 7:
            poss_moves.add((or_x, or_y + 1))

        if is_on_board(or_x, or_y - 1) and not pos_is_threatened(or_x, or_y - 1) and board[or_x][or_y - 1] < 7:
            poss_moves.add((or_x, or_y - 1))

        if is_on_board(or_x + 1, or_y + 1) and not pos_is_threatened(or_x + 1, or_y + 1) and board[or_x + 1][or_y + 1] < 7:
            poss_moves.add((or_x + 1, or_y + 1))

        if is_on_board(or_x + 1, or_y - 1) and not pos_is_threatened(or_x + 1, or_y - 1) and board[or_x + 1][or_y - 1] < 7:
            poss_moves.add((or_x + 1, or_y - 1))

        if is_on_board(or_x - 1, or_y + 1) and not pos_is_threatened(or_x - 1, or_y + 1) and board[or_x - 1][or_y + 1] < 7:
            poss_moves.add((or_x - 1, or_y + 1))

        if is_on_board(or_x - 1, or_y - 1) and not pos_is_threatened(or_x - 1, or_y - 1) and board[or_x - 1][or_y - 1] < 7:
            poss_moves.add((or_x - 1, or_y - 1))

        if white_rook_1_moved == False and white_king_moved == False and board[7][0] == 8 and not pos_is_threatened(7, 0) and not pos_is_threatened(7, 1) and not pos_is_threatened(7, 2) and not pos_is_threatened(7, 3) and not pos_is_threatened(7, 4) and board[7][1] == 0 and board[7][2] == 0 and board[7][3] == 0:
            poss_moves.add((7, 2))
            castle3 = True

        if white_rook_2_moved == False and white_king_moved == False and board[7][7] == 8 and not pos_is_threatened(7, 4) and not pos_is_threatened(7, 5) and not pos_is_threatened(7, 6) and not pos_is_threatened(7, 7)  and board[7][5] == 0 and board[7][6] == 0:
            poss_moves.add((7, 6))
            castle4 = True

    #using the possible moves, check if the position trying to be moved to is legal
    if((dest_x, dest_y) in poss_moves):
        if in_check:
            temp_board = copy.deepcopy(board)
            board[dest_x][dest_y] = board[or_x][or_y] 
            board[or_x][or_y] = 0

            if piece_turn == 0:
                for i in range(len(board)):
                    for j in range(len(board[i])):
                        if board[i][j] == 12:
                            king_row = i
                            king_col = j
            else:
                for i in range(len(board)):
                    for j in range(len(board[i])):
                        if board[i][j] == 6:
                            king_row = i
                            king_col = j
            

            if pos_is_threatened(king_row, king_col):
                board = temp_board
                return False
            else:
                board = temp_board

        if black_rook_1_moved == False and or_x == 0 and or_y == 0:
            black_rook_1_moved = True
        elif black_rook_2_moved == False and or_x == 0 and or_y == 7:
            black_rook_2_moved = True
        elif black_king_moved == False and or_x == 0 and or_y == 4:
            black_king_moved = True
        elif white_rook_1_moved == False and or_x == 7 and or_y == 0:
            white_rook_1_moved = True
        elif white_rook_2_moved == False and or_x == 7 and or_y == 7:
            white_rook_2_moved = True
        elif white_king_moved == False and or_x == 7 and or_y == 4:
            white_king_moved = True
        
        if castle1 == True:
            board[0][0] = 0
            board[0][3] = 2
        elif castle2 == True:
            board[0][7] = 0
            board[0][5] = 2
        elif castle3 == True:
            board[7][7] = 0
            board[7][5] = 8
        elif castle4 == True:
            board[7][7] = 0
            board[7][5] = 8

        return True
    else: 
        return False

def is_on_board(x, y):
    if x >= 0 and x < 8 and y >= 0 and y < 8:
        return True
    else:
        return False 

def pos_is_threatened(row, col):
    global piece_turn
    poss_moves = set()

    enemy_pieces = set()
    if piece_turn == 0:
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] > 0 and board[i][j] < 7:
                    enemy_pieces.add((i, j))
    else:
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] > 6:
                    enemy_pieces.add((i, j))

    for (x, y) in enemy_pieces:
        #black pawn functionality
        if board[x][y] == 1:
            if is_on_board(x + 1, y + 1) and board[x + 1][y + 1] > 6:
                poss_moves.add((x + 1, y + 1))
            
            if is_on_board(x + 1, y - 1) and board[x + 1][y - 1] > 6:
                poss_moves.add((x + 1, y - 1))
                
            if x == 1 and board[x + 2][y] == 0 and board[x + 1][y] == 0:
                poss_moves.add((x + 2, y))

            if is_on_board(x + 1, y) and board[x + 1][y] == 0:
                poss_moves.add((x + 1, y))
        
        #black rook functionality
        elif board[x][y] == 2:
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] == 0:
                poss_moves.add((temp_x + 1, temp_y))        
                temp_x += 1

            if is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] > 6:
                poss_moves.add((temp_x + 1, temp_y))        
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] == 0:
                poss_moves.add((temp_x - 1, temp_y))        
                temp_x -= 1
            
            if is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] > 6:
                poss_moves.add((temp_x - 1, temp_y))        

            temp_x = x
            temp_y = y

            while is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] == 0:
                poss_moves.add((temp_x, temp_y + 1))        
                temp_y += 1

            if is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] > 6:
                poss_moves.add((temp_x, temp_y + 1))       
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] == 0:
                poss_moves.add((temp_x , temp_y - 1))        
                temp_y -= 1
            
            if is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] > 6:
                poss_moves.add((temp_x, temp_y - 1))       
        
        #black knight functionality
        elif board[x][y] == 3:
            if is_on_board(x - 2, y + 1) and (board[x - 2][y + 1] == 0 or board[x - 2][y + 1] > 6):
                poss_moves.add((x - 2, y + 1)) 
            
            if is_on_board(x - 2, y - 1) and (board[x - 2][y - 1] == 0 or board[x - 2][y - 1] > 6):
                poss_moves.add((x - 2, y - 1)) 
            
            if is_on_board(x - 1, y - 2) and (board[x - 1][y - 2] == 0 or board[x - 1][y - 2] > 6):
                poss_moves.add((x - 1, y - 2)) 

            if is_on_board(x + 1, y - 2) and (board[x + 1][y - 2] == 0 or board[x + 1][y - 2] > 6):
                poss_moves.add((x + 1, y - 2))

            if is_on_board(x - 1, y + 2) and (board[x - 1][y + 2] == 0 or board[x - 1][y + 2] > 6):
                poss_moves.add((x - 1, y + 2)) 

            if is_on_board(x + 1, y + 2) and (board[x + 1][y + 2] == 0 or board[x + 1][y + 2] > 6):
                poss_moves.add((x + 1, y + 2))

            if is_on_board(x + 2, y + 1) and (board[x + 2][y + 1] == 0 or board[x + 2][y + 1] > 6):
                    poss_moves.add((x + 2, y + 1)) 
            
            if is_on_board(x + 2, y - 1) and (board[x + 2][y - 1] == 0 or board[x + 2][y - 1] > 6):
                poss_moves.add((x + 2, y - 1)) 

        #black bishop functionality
        elif board[x][y] == 4:
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] == 0:
                poss_moves.add((temp_x + 1, temp_y + 1))        
                temp_x += 1
                temp_y += 1

            if is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] > 6:
                poss_moves.add((temp_x + 1, temp_y + 1))        
                
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] == 0:
                poss_moves.add((temp_x + 1, temp_y - 1))        
                temp_x += 1
                temp_y -= 1

            if is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] > 6:
                poss_moves.add((temp_x + 1, temp_y - 1))

            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] == 0:
                poss_moves.add((temp_x - 1, temp_y + 1))        
                temp_x -= 1
                temp_y += 1

            if is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] > 6:
                poss_moves.add((temp_x - 1, temp_y + 1))

            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] == 0:
                poss_moves.add((temp_x - 1, temp_y - 1))        
                temp_x -= 1
                temp_y -= 1

            if is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] > 6:
                poss_moves.add((temp_x - 1, temp_y - 1))

        #black queen functionality
        elif board[x][y] == 5:
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] == 0:
                poss_moves.add((temp_x + 1, temp_y))        
                temp_x += 1

            if is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] > 6:
                poss_moves.add((temp_x + 1, temp_y))        
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] == 0:
                poss_moves.add((temp_x - 1, temp_y))        
                temp_x -= 1
            
            if is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] > 6:
                poss_moves.add((temp_x - 1, temp_y))        

            temp_x = x
            temp_y = y

            while is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] == 0:
                poss_moves.add((temp_x, temp_y + 1))        
                temp_y += 1

            if is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] > 6:
                poss_moves.add((temp_x, temp_y + 1))       
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] == 0:
                poss_moves.add((temp_x , temp_y - 1))        
                temp_y -= 1
            
            if is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] > 6:
                poss_moves.add((temp_x, temp_y - 1))

            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] == 0:
                poss_moves.add((temp_x + 1, temp_y + 1))        
                temp_x += 1
                temp_y += 1

            if is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] > 6:
                poss_moves.add((temp_x + 1, temp_y + 1))        
                
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] == 0:
                poss_moves.add((temp_x + 1, temp_y - 1))        
                temp_x += 1
                temp_y -= 1

            if is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] > 6:
                poss_moves.add((temp_x + 1, temp_y - 1))

            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] == 0:
                poss_moves.add((temp_x - 1, temp_y + 1))        
                temp_x -= 1
                temp_y += 1

            if is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] > 6:
                poss_moves.add((temp_x - 1, temp_y + 1))

            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] == 0:
                poss_moves.add((temp_x - 1, temp_y - 1))        
                temp_x -= 1
                temp_y -= 1

            if is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] > 6:
                poss_moves.add((temp_x - 1, temp_y - 1))

        #black king functionality
        elif board[x][y] == 6:
            if is_on_board(x + 1, y) and (board[x + 1][y] == 0 or board[x + 1][y] > 6):
                poss_moves.add((x + 1, y))

            if is_on_board(x - 1, y) and (board[x - 1][y] == 0 or board[x - 1][y] > 6):
                poss_moves.add((x - 1, y))

            if is_on_board(x, y + 1) and (board[x][y + 1] == 0 or board[x][y + 1] > 6):
                poss_moves.add((x, y + 1))

            if is_on_board(x, y - 1) and (board[x][y - 1] == 0 or board[x][y - 1] > 6):
                poss_moves.add((x, y - 1))

            if is_on_board(x + 1, y + 1) and (board[x + 1][y + 1] == 0 or board[x + 1][y + 1] > 6):
                poss_moves.add((x + 1, y + 1))

            if is_on_board(x + 1, y - 1) and (board[x + 1][y - 1] == 0 or board[x + 1][y - 1] > 6):
                poss_moves.add((x + 1, y - 1))

            if is_on_board(x - 1, y + 1) and (board[x - 1][y + 1] == 0 or board[x - 1][y + 1] > 6):
                poss_moves.add((x - 1, y + 1))

            if is_on_board(x - 1, y - 1) and (board[x - 1][y - 1] == 0 or board[x - 1][y - 1] > 6):
                poss_moves.add((x - 1, y - 1))

        #white pawn functionality
        elif board[x][y] == 7:
            if is_on_board(x - 1, y + 1) and board[x - 1][y + 1] > 0 and board[x - 1][y + 1] < 7:
                poss_moves.add((x - 1, y + 1))
            
            if is_on_board(x - 1, y - 1) and board[x - 1][y - 1] > 0 and board[x - 1][y - 1] < 7:
                poss_moves.add((x - 1, y - 1))
                
            if x == 6 and board[x - 2][y] == 0 and board[x - 1][y] == 0:
                poss_moves.add((x - 2, y))

            if is_on_board(x - 1, y) and board[x - 1][y] == 0:
                poss_moves.add((x - 1, y))
        
        #white rook functionality
        elif board[x][y] == 8:
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] == 0:
                poss_moves.add((temp_x + 1, temp_y))        
                temp_x += 1
            
            if is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] > 0 and board[temp_x + 1][temp_y] < 7:
                poss_moves.add((temp_x + 1, temp_y))        
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] == 0:
                poss_moves.add((temp_x - 1, temp_y))        
                temp_x -= 1
            
            if is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] > 0 and board[temp_x - 1][temp_y] < 7:
                poss_moves.add((temp_x - 1, temp_y))   
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] == 0:
                poss_moves.add((temp_x, temp_y + 1))        
                temp_y += 1
            
            if is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] > 0 and board[temp_x][temp_y + 1] < 7:
                poss_moves.add((temp_x, temp_y + 1))   
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] == 0:
                poss_moves.add((temp_x , temp_y - 1))        
                temp_y -= 1

            if is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] > 0 and board[temp_x][temp_y - 1] < 7:
                poss_moves.add((temp_x, temp_y - 1))

        #white knight functionality
        elif board[x][y] == 9:
            if is_on_board(x - 2, y + 1) and (board[x - 2][y + 1] < 7):
                poss_moves.add((x - 2, y + 1)) 
            
            if is_on_board(x - 2, y - 1) and (board[x - 2][y - 1] < 7):
                poss_moves.add((x - 2, y - 1)) 
            
            if is_on_board(x - 1, y - 2) and (board[x - 1][y - 2]< 7):
                poss_moves.add((x - 1, y - 2)) 

            if is_on_board(x + 1, y - 2) and (board[x + 1][y - 2] < 7):
                poss_moves.add((x + 1, y - 2))

            if is_on_board(x - 1, y + 2) and (board[x - 1][y + 2] < 7):
                poss_moves.add((x - 1, y + 2)) 

            if is_on_board(x + 1, y + 2) and (board[x + 1][y + 2] < 7):
                poss_moves.add((x + 1, y + 2))

            if is_on_board(x + 2, y + 1) and (board[x + 2][y + 1] < 7):
                    poss_moves.add((x + 2, y + 1)) 
            
            if is_on_board(x + 2, y - 1) and (board[x + 2][y - 1] < 7):
                poss_moves.add((x + 2, y - 1))  
            
        #white bishop functionality
        elif board[x][y] == 10:
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] == 0:
                poss_moves.add((temp_x + 1, temp_y + 1))        
                temp_x += 1
                temp_y += 1

            if is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] > 0 and board[temp_x + 1][temp_y + 1] < 7:
                poss_moves.add((temp_x + 1, temp_y + 1))        
                
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] == 0:
                poss_moves.add((temp_x + 1, temp_y - 1))        
                temp_x += 1
                temp_y -= 1

            if is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] > 0 and board[temp_x + 1][temp_y - 1] < 7:
                poss_moves.add((temp_x + 1, temp_y - 1))

            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] == 0:
                poss_moves.add((temp_x - 1, temp_y + 1))        
                temp_x -= 1
                temp_y += 1

            if is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] > 0 and board[temp_x - 1][temp_y + 1] < 7:
                poss_moves.add((temp_x - 1, temp_y + 1))

            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] == 0:
                poss_moves.add((temp_x - 1, temp_y - 1))        
                temp_x -= 1
                temp_y -= 1

            if is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] > 0 and board[temp_x - 1][temp_y - 1] < 7:
                poss_moves.add((temp_x - 1, temp_y - 1))
        
        #white queen functionality
        elif board[x][y] == 11:
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] == 0:
                poss_moves.add((temp_x + 1, temp_y))        
                temp_x += 1
            
            if is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] > 0 and board[temp_x + 1][temp_y] < 7:
                poss_moves.add((temp_x + 1, temp_y))        
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] == 0:
                poss_moves.add((temp_x - 1, temp_y))        
                temp_x -= 1
            
            if is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] > 0 and board[temp_x - 1][temp_y] < 7:
                poss_moves.add((temp_x - 1, temp_y))   
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] == 0:
                poss_moves.add((temp_x, temp_y + 1))        
                temp_y += 1
            
            if is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] > 0 and board[temp_x][temp_y + 1] < 7:
                poss_moves.add((temp_x, temp_y + 1))   
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] == 0:
                poss_moves.add((temp_x , temp_y - 1))        
                temp_y -= 1

            if is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] > 0 and board[temp_x][temp_y - 1] < 7:
                poss_moves.add((temp_x, temp_y - 1))
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] == 0:
                poss_moves.add((temp_x + 1, temp_y + 1))        
                temp_x += 1
                temp_y += 1

            if is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] > 0 and board[temp_x + 1][temp_y + 1] < 7:
                poss_moves.add((temp_x + 1, temp_y + 1))        
                
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] == 0:
                poss_moves.add((temp_x + 1, temp_y - 1))        
                temp_x += 1
                temp_y -= 1

            if is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] > 0 and board[temp_x + 1][temp_y - 1] < 7:
                poss_moves.add((temp_x + 1, temp_y - 1))

            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] == 0:
                poss_moves.add((temp_x - 1, temp_y + 1))        
                temp_x -= 1
                temp_y += 1

            if is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] > 0 and board[temp_x - 1][temp_y + 1] < 7:
                poss_moves.add((temp_x - 1, temp_y + 1))

            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] == 0:
                poss_moves.add((temp_x - 1, temp_y - 1))        
                temp_x -= 1
                temp_y -= 1

            if is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] > 0 and board[temp_x - 1][temp_y - 1] < 7:
                poss_moves.add((temp_x - 1, temp_y - 1))

        #white king functionality
        elif board[x][y] == 12:
            if is_on_board(x + 1, y) and board[x + 1][y] < 7:
                poss_moves.add((x + 1, y))

            if is_on_board(x - 1, y) and board[x - 1][y] < 7:
                poss_moves.add((x - 1, y))

            if is_on_board(x, y + 1) and board[x][y + 1] < 7:
                poss_moves.add((x, y + 1))

            if is_on_board(x, y - 1) and board[x][y - 1] < 7:
                poss_moves.add((x, y - 1))

            if is_on_board(x + 1, y + 1) and board[x + 1][y + 1] < 7:
                poss_moves.add((x + 1, y + 1))

            if is_on_board(x + 1, y - 1) and board[x + 1][y - 1] < 7:
                poss_moves.add((x + 1, y - 1))

            if is_on_board(x - 1, y + 1) and board[x - 1][y + 1] < 7:
                poss_moves.add((x - 1, y + 1))

            if is_on_board(x - 1, y - 1) and board[x - 1][y - 1] < 7:
                poss_moves.add((x - 1, y - 1))

        if((row, col) in poss_moves):
            return True

    return False

#draw the board according to the positions of the pieces of the board array
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
    global piece_turn
    global game_started
    global board
    global turn

    king_row = -1
    king_col = -1
    piece_turn = 1 - piece_turn
    if piece_turn == 0:
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] == 12:
                    king_row = i
                    king_col = j
    else:
         for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] == 6:
                    king_row = i
                    king_col = j

    poss_moves = set()

    pieces = set()
    if piece_turn == 1:
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] > 0 and board[i][j] < 7:
                    pieces.add((i, j))
    else:
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] > 6:
                    pieces.add((i, j))

    for (x, y) in pieces:
        #black pawn functionality
        if board[x][y] == 1:
            if is_on_board(x + 1, y + 1) and board[x + 1][y + 1] > 6:
                poss_moves.add((x, y, x + 1, y + 1))
            
            if is_on_board(x + 1, y - 1) and board[x + 1][y - 1] > 6:
                poss_moves.add((x, y, x + 1, y - 1))
                
            if x == 1 and board[x + 2][y] == 0 and board[x + 1][y] == 0:
                poss_moves.add((x, y, x + 2, y))

            if is_on_board(x + 1, y) and board[x + 1][y] == 0:
                poss_moves.add((x, y, x + 1, y))
        
        #black rook functionality
        elif board[x][y] == 2:
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] == 0:
                poss_moves.add((x, y, temp_x + 1, temp_y))        
                temp_x += 1

            if is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] > 6:
                poss_moves.add((x, y, temp_x + 1, temp_y))        
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] == 0:
                poss_moves.add((x, y, temp_x - 1, temp_y))        
                temp_x -= 1
            
            if is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] > 6:
                poss_moves.add((x, y, temp_x - 1, temp_y))        

            temp_x = x
            temp_y = y

            while is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] == 0:
                poss_moves.add((x, y, temp_x, temp_y + 1))        
                temp_y += 1

            if is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] > 6:
                poss_moves.add((x, y, temp_x, temp_y + 1))       
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] == 0:
                poss_moves.add((x, y, temp_x , temp_y - 1))        
                temp_y -= 1
            
            if is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] > 6:
                poss_moves.add((x, y, temp_x, temp_y - 1))       
        
        #black knight functionality
        elif board[x][y] == 3:
            if is_on_board(x - 2, y + 1) and (board[x - 2][y + 1] == 0 or board[x - 2][y + 1] > 6):
               poss_moves.add((x, y, x - 2, y + 1)) 
            
            if is_on_board(x - 2, y - 1) and (board[x - 2][y - 1] == 0 or board[x - 2][y - 1] > 6):
                poss_moves.add((x, y, x - 2, y - 1)) 
            
            if is_on_board(x - 1, y - 2) and (board[x - 1][y - 2] == 0 or board[x - 1][y - 2] > 6):
                poss_moves.add((x, y, x - 1, y - 2)) 

            if is_on_board(x + 1, y - 2) and (board[x + 1][y - 2] == 0 or board[x + 1][y - 2] > 6):
                poss_moves.add((x, y, x + 1, y - 2))

            if is_on_board(x - 1, y + 2) and (board[x - 1][y + 2] == 0 or board[x - 1][y + 2] > 6):
                poss_moves.add((x, y, x - 1, y + 2)) 

            if is_on_board(x + 1, y + 2) and (board[x + 1][y + 2] == 0 or board[x + 1][y + 2] > 6):
                poss_moves.add((x, y, x + 1, y + 2))

            if is_on_board(x + 2, y + 1) and (board[x + 2][y + 1] == 0 or board[x + 2][y + 1] > 6):
                poss_moves.add((x, y, x + 2, y + 1)) 
            
            if is_on_board(x + 2, y - 1) and (board[x + 2][y - 1] == 0 or board[x + 2][y - 1] > 6):
                poss_moves.add((x, y, x + 2, y - 1)) 

        #black bishop functionality
        elif board[x][y] == 4:
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] == 0:
                poss_moves.add((x, y, temp_x + 1, temp_y + 1))        
                temp_x += 1
                temp_y += 1

            if is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] > 6:
                poss_moves.add((x, y, temp_x + 1, temp_y + 1))        
                
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] == 0:
                poss_moves.add((x, y, temp_x + 1, temp_y - 1))        
                temp_x += 1
                temp_y -= 1

            if is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] > 6:
                poss_moves.add((x, y, temp_x + 1, temp_y - 1))

            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] == 0:
                poss_moves.add((x, y, temp_x - 1, temp_y + 1))        
                temp_x -= 1
                temp_y += 1

            if is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] > 6:
                poss_moves.add((x, y, temp_x - 1, temp_y + 1))

            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] == 0:
                poss_moves.add((x, y, temp_x - 1, temp_y - 1))        
                temp_x -= 1
                temp_y -= 1

            if is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] > 6:
                poss_moves.add((x, y, temp_x - 1, temp_y - 1))

        #black queen functionality
        elif board[x][y] == 5:
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] == 0:
                poss_moves.add((x, y, temp_x + 1, temp_y))        
                temp_x += 1

            if is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] > 6:
                poss_moves.add((x, y, temp_x + 1, temp_y))        
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] == 0:
                poss_moves.add((x, y, temp_x - 1, temp_y))        
                temp_x -= 1
            
            if is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] > 6:
                poss_moves.add((x, y, temp_x - 1, temp_y))        

            temp_x = x
            temp_y = y

            while is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] == 0:
                poss_moves.add((x, y, temp_x, temp_y + 1))        
                temp_y += 1

            if is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] > 6:
                poss_moves.add((x, y, temp_x, temp_y + 1))       
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] == 0:
                poss_moves.add((x, y, temp_x , temp_y - 1))        
                temp_y -= 1
            
            if is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] > 6:
                poss_moves.add((x, y, temp_x, temp_y - 1))

            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] == 0:
                poss_moves.add((x, y, temp_x + 1, temp_y + 1))        
                temp_x += 1
                temp_y += 1

            if is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] > 6:
                poss_moves.add((x, y, temp_x + 1, temp_y + 1))        
                
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] == 0:
                poss_moves.add((x, y, temp_x + 1, temp_y - 1))        
                temp_x += 1
                temp_y -= 1

            if is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] > 6:
                poss_moves.add((x, y, temp_x + 1, temp_y - 1))

            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] == 0:
                poss_moves.add((x, y, temp_x - 1, temp_y + 1))        
                temp_x -= 1
                temp_y += 1

            if is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] > 6:
                poss_moves.add((x, y, temp_x - 1, temp_y + 1))

            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] == 0:
                poss_moves.add((x, y, temp_x - 1, temp_y - 1))        
                temp_x -= 1
                temp_y -= 1

            if is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] > 6:
                poss_moves.add((x, y, temp_x - 1, temp_y - 1))

        #black king functionality
        elif board[x][y] == 6:
            if is_on_board(x + 1, y) and (board[x + 1][y] == 0 or board[x + 1][y] > 6):
                poss_moves.add((x, y, x + 1, y))

            if is_on_board(x - 1, y) and (board[x - 1][y] == 0 or board[x - 1][y] > 6):
                poss_moves.add((x, y, x - 1, y))

            if is_on_board(x, y + 1) and (board[x][y + 1] == 0 or board[x][y + 1] > 6):
                poss_moves.add((x, y, x, y + 1))

            if is_on_board(x, y - 1) and (board[x][y - 1] == 0 or board[x][y - 1] > 6):
                poss_moves.add((x, y, x, y - 1))

            if is_on_board(x + 1, y + 1) and (board[x + 1][y + 1] == 0 or board[x + 1][y + 1] > 6):
                poss_moves.add((x, y, x + 1, y + 1))

            if is_on_board(x + 1, y - 1) and (board[x + 1][y - 1] == 0 or board[x + 1][y - 1] > 6):
                poss_moves.add((x, y, x + 1, y - 1))

            if is_on_board(x - 1, y + 1) and (board[x - 1][y + 1] == 0 or board[x - 1][y + 1] > 6):
                poss_moves.add((x, y, x - 1, y + 1))

            if is_on_board(x - 1, y - 1) and (board[x - 1][y - 1] == 0 or board[x - 1][y - 1] > 6):
                poss_moves.add((x, y, x - 1, y - 1))

        #white pawn functionality
        elif board[x][y] == 7:
            if is_on_board(x - 1, y + 1) and board[x - 1][y + 1] > 0 and board[x - 1][y + 1] < 7:
                poss_moves.add((x, y, x - 1, y + 1))
            
            if is_on_board(x - 1, y - 1) and board[x - 1][y - 1] > 0 and board[x - 1][y - 1] < 7:
                poss_moves.add((x, y, x - 1, y - 1))
                
            if x == 6 and board[x - 2][y] == 0 and board[x - 1][y] == 0:
                poss_moves.add((x, y, x - 2, y))

            if is_on_board(x - 1, y) and board[x - 1][y] == 0:
                poss_moves.add((x, y, x - 1, y))
        
        #white rook functionality
        elif board[x][y] == 8:
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] == 0:
                poss_moves.add((x, y, temp_x + 1, temp_y))        
                temp_x += 1
            
            if is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] > 0 and board[temp_x + 1][temp_y] < 7:
                poss_moves.add((x, y, temp_x + 1, temp_y))        
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] == 0:
                poss_moves.add((x, y, temp_x - 1, temp_y))        
                temp_x -= 1
            
            if is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] > 0 and board[temp_x - 1][temp_y] < 7:
                poss_moves.add((x, y, temp_x - 1, temp_y))   
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] == 0:
                poss_moves.add((x, y, temp_x, temp_y + 1))        
                temp_y += 1
            
            if is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] > 0 and board[temp_x][temp_y + 1] < 7:
                poss_moves.add((x, y, temp_x, temp_y + 1))   
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] == 0:
                poss_moves.add((x, y, temp_x , temp_y - 1))        
                temp_y -= 1

            if is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] > 0 and board[temp_x][temp_y - 1] < 7:
                poss_moves.add((x, y, temp_x, temp_y - 1))

        #white knight functionality
        elif board[x][y] == 9:
            if is_on_board(x - 2, y + 1) and (board[x - 2][y + 1] < 7):
                poss_moves.add((x, y, x - 2, y + 1)) 
            
            if is_on_board(x - 2, y - 1) and (board[x - 2][y - 1] < 7):
                poss_moves.add((x, y, x - 2, y - 1)) 
            
            if is_on_board(x - 1, y - 2) and (board[x - 1][y - 2]< 7):
                poss_moves.add((x, y, x - 1, y - 2)) 

            if is_on_board(x + 1, y - 2) and (board[x + 1][y - 2] < 7):
                poss_moves.add((x, y, x + 1, y - 2))

            if is_on_board(x - 1, y + 2) and (board[x - 1][y + 2] < 7):
                poss_moves.add((x, y, x - 1, y + 2)) 

            if is_on_board(x + 1, y + 2) and (board[x + 1][y + 2] < 7):
                poss_moves.add((x, y, x + 1, y + 2))

            if is_on_board(x + 2, y + 1) and (board[x + 2][y + 1] < 7):
                poss_moves.add((x, y, x + 2, y + 1)) 
            
            if is_on_board(x + 2, y - 1) and (board[x + 2][y - 1] < 7):
                poss_moves.add((x, y, x + 2, y - 1))  
            
        #white bishop functionality
        elif board[x][y] == 10:
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] == 0:
                poss_moves.add((x, y, temp_x + 1, temp_y + 1))        
                temp_x += 1
                temp_y += 1

            if is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] > 0 and board[temp_x + 1][temp_y + 1] < 7:
                poss_moves.add((x, y, temp_x + 1, temp_y + 1))        
                
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] == 0:
                poss_moves.add((x, y, temp_x + 1, temp_y - 1))        
                temp_x += 1
                temp_y -= 1

            if is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] > 0 and board[temp_x + 1][temp_y - 1] < 7:
                poss_moves.add((x, y, temp_x + 1, temp_y - 1))

            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] == 0:
                poss_moves.add((x, y, temp_x - 1, temp_y + 1))        
                temp_x -= 1
                temp_y += 1

            if is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] > 0 and board[temp_x - 1][temp_y + 1] < 7:
                poss_moves.add((x, y, temp_x - 1, temp_y + 1))

            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] == 0:
                poss_moves.add((x, y, temp_x - 1, temp_y - 1))        
                temp_x -= 1
                temp_y -= 1

            if is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] > 0 and board[temp_x - 1][temp_y - 1] < 7:
                poss_moves.add((x, y, temp_x - 1, temp_y - 1))
        
        #white queen functionality
        elif board[x][y] == 11:
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] == 0:
                poss_moves.add((x, y, temp_x + 1, temp_y))        
                temp_x += 1
            
            if is_on_board(temp_x + 1, temp_y) and board[temp_x + 1][temp_y] > 0 and board[temp_x + 1][temp_y] < 7:
                poss_moves.add((x, y, temp_x + 1, temp_y))        
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] == 0:
                poss_moves.add((x, y, temp_x - 1, temp_y))        
                temp_x -= 1
            
            if is_on_board(temp_x - 1, temp_y) and board[temp_x - 1][temp_y] > 0 and board[temp_x - 1][temp_y] < 7:
                poss_moves.add((x, y, temp_x - 1, temp_y))   
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] == 0:
                poss_moves.add((x, y, temp_x, temp_y + 1))        
                temp_y += 1
            
            if is_on_board(temp_x, temp_y + 1) and board[temp_x][temp_y + 1] > 0 and board[temp_x][temp_y + 1] < 7:
                poss_moves.add((x, y, temp_x, temp_y + 1))   
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] == 0:
                poss_moves.add((x, y, temp_x , temp_y - 1))        
                temp_y -= 1

            if is_on_board(temp_x, temp_y - 1) and board[temp_x][temp_y - 1] > 0 and board[temp_x][temp_y - 1] < 7:
                poss_moves.add((x, y, temp_x, temp_y - 1))
            
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] == 0:
                poss_moves.add((x, y, temp_x + 1, temp_y + 1))        
                temp_x += 1
                temp_y += 1

            if is_on_board(temp_x + 1, temp_y + 1) and board[temp_x + 1][temp_y + 1] > 0 and board[temp_x + 1][temp_y + 1] < 7:
                poss_moves.add((x, y, temp_x + 1, temp_y + 1))        
                
            temp_x = x
            temp_y = y

            while is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] == 0:
                poss_moves.add((x, y, temp_x + 1, temp_y - 1))        
                temp_x += 1
                temp_y -= 1

            if is_on_board(temp_x + 1, temp_y - 1) and board[temp_x + 1][temp_y - 1] > 0 and board[temp_x + 1][temp_y - 1] < 7:
                poss_moves.add((x, y, temp_x + 1, temp_y - 1))

            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] == 0:
                poss_moves.add((x, y, temp_x - 1, temp_y + 1))        
                temp_x -= 1
                temp_y += 1

            if is_on_board(temp_x - 1, temp_y + 1) and board[temp_x - 1][temp_y + 1] > 0 and board[temp_x - 1][temp_y + 1] < 7:
                poss_moves.add((x, y, temp_x - 1, temp_y + 1))

            temp_x = x
            temp_y = y

            while is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] == 0:
                poss_moves.add((x, y, temp_x - 1, temp_y - 1))        
                temp_x -= 1
                temp_y -= 1

            if is_on_board(temp_x - 1, temp_y - 1) and board[temp_x - 1][temp_y - 1] > 0 and board[temp_x - 1][temp_y - 1] < 7:
                poss_moves.add((x, y, temp_x - 1, temp_y - 1))

        #white king functionality
        elif board[x][y] == 12:
            if is_on_board(x + 1, y) and board[x + 1][y] < 7:
                poss_moves.add((x, y, x + 1, y))

            if is_on_board(x - 1, y) and board[x - 1][y] < 7:
                poss_moves.add((x, y, x - 1, y))

            if is_on_board(x, y + 1) and board[x][y + 1] < 7:
                poss_moves.add((x, y, x, y + 1))

            if is_on_board(x, y - 1) and board[x][y - 1] < 7:
                poss_moves.add((x, y, x, y - 1))

            if is_on_board(x + 1, y + 1) and board[x + 1][y + 1] < 7:
                poss_moves.add((x, y, x + 1, y + 1))

            if is_on_board(x + 1, y - 1) and board[x + 1][y - 1] < 7:
                poss_moves.add((x, y, x + 1, y - 1))

            if is_on_board(x - 1, y + 1) and board[x - 1][y + 1] < 7:
                poss_moves.add((x, y, x - 1, y + 1))

            if is_on_board(x - 1, y - 1) and board[x - 1][y - 1] < 7:
                poss_moves.add((x, y, x - 1, y - 1))
    
    if not pos_is_threatened(king_row, king_col) and len(poss_moves) == 0:
        await ctx.send("The game has ended in a tie.")
        game_started = False
        return True
    elif pos_is_threatened(king_row, king_col):
        for (x1, y1, x2, y2) in poss_moves:
            temp_board = copy.deepcopy(board)
            board[x2][y2] = board[x1][y1] 
            board[x1][y1] = 0
            
            king_row = -1
            king_col = -1

            if piece_turn == 0:
                for i in range(len(board)):
                    for j in range(len(board[i])):
                        if board[i][j] == 12:
                            king_row = i
                            king_col = j
            else:
                for i in range(len(board)):
                    for j in range(len(board[i])):
                        if board[i][j] == 6:
                            king_row = i
                            king_col = j

            if pos_is_threatened(king_row, king_col):
                board = temp_board
            else:
                board = temp_board
                piece_turn = 1 - piece_turn
                return False
        await ctx.send(f"Congratulations player {turn} on winning the chess game")
        game_started = False
        return True
    else:
        piece_turn = 1 - piece_turn
        return False
    
bot.run(TOKEN)