
input('''

            PyTetris

Based on 1989 Tetris (NES, Nintendo)
Playfield dimension: 10x20

-no kicks
-no lock delay
-Right handed version (clockwise rotation only)


Keys:
↑ or w  -   rotate Tetromino
← or a  -   move left
→ or d  -   move right 
↓ or s  -   soft drop
space   -   hard drop
esc     -   exit

PRESS ENTER TO START
''')


import random
import keyboard
import time
import threading


# play field:
col = 10
row = 24
Arr = [[0 for i in range(col)] for i in range(row)]

DEATH_ROW = 3
NEW_ROW = [0 for i in range(col)]       #[0,0,0,0,0,0,0,0,0,0]

# standard timings:
# {level : frames per gridcell} ; fall speed = 1sec * (48frames/60FPS)
falling_rate = {
    0 : 48,
    1 : 43,
    2 : 38,
    3 : 33,
    4 : 28,
    5 : 23,
    6 : 18,
    7 : 13,
    8 : 8,
    9 : 6,
    10 : 5,
    13 : 4,
    16 : 3,
    19 : 2,
    29 : 1}



# Tetromino data:
Tetrominoes = ['O', 'I', 'S', 'Z', 'L', 'J', 'T']

Tetromino = []
Ty, Tx= 0,0
prev_Tx = 0
prev_Ty = 0
prev_orientation = 0
T_orientation = 0
T_shape = None
next_T_shape = None

score = 0
level = 0
lines_cleared = 0
#highscore = 0


def endgame():
    global Play
    Play = False
    # End

def gameover():
    print("\nGame Over!\nScore: ", score)
    endgame()

    
def reset_T():
    global Tx,Ty,prev_Tx,prev_Ty,T_orientation,T_shape
    Tx=col//2
    Ty=1
    prev_Tx = Tx
    prev_Ty = Ty
    T_orientation = 0
    T_shape = T_get_shape()
    Tetromino = []

def add_score(lines):
    # standard score system;  { lines cleared : points}
    score_table = {   
        0 : 0,
        1 : 40 * (level + 1),
        2 : 100 * (level + 1),
        3 : 300 * (level + 1),
        4 : 1200 * (level + 1)}
    return score_table[lines]

# when Tetromino is dropped
def merge():
    global score, merging,lines_cleared
    merging = True
    lines = 0
    for i in Tetromino:     #   Tetromino = [   [x,y], [x1,y1], [x2,y2], [x3,y4]  ]
        Arr[i[1]][i[0]] = 1
    reset_T()
    time.sleep(0.8)
    for i in range(len(Arr)):
        if sum(Arr[i]) == col:
            Arr[i] = NEW_ROW
            Arr[:i+1] = Arr[i:i+1] + Arr[:i]

            lines += 1
            lines_cleared += 1
    refresh()    
    if sum(Arr[DEATH_ROW]) > 0:
        gameover()
        refresh()

    score += add_score(lines)
    merging = False
    return True

def T_get_shape():
    global next_T_shape
    T_shape = next_T_shape if next_T_shape != None else random.choice(Tetrominoes)
    next_T_shape = random.choice(Tetrominoes)
    return(T_shape)

def T_get_coordinates(x,y,orientation,shape):
    
    O = [[x, y],[x+1, y],[x+1, y-1],[x, y-1]]

    I =[[[x, y],[x, y-1],[x, y+1],[x,y+2]],
        [[x, y],[x+1, y],[x-1, y],[x+2,y]]]

    S =[[[x, y],[x+1, y],[x, y+1],[x-1, y+1]],
        [[x, y],[x, y-1],[x+1, y],[x+1, y+1]]]
    
    Z =[[[x, y],[x-1, y],[x, y+1],[x+1, y+1]],
        [[x, y],[x, y-1],[x-1, y],[x-1, y+1]]]
    
    L = [[[x, y],[x-1, y],[x+1, y],[x-1, y+1]], 
        [[x, y],[x, y+1],[x, y-1],[x-1, y-1]],
        [[x, y],[x+1, y],[x-1, y],[x+1, y-1]],
        [[x, y],[x, y-1],[x, y+1],[x+1, y+1]]]

    J = [[[x, y],[x-1, y],[x+1, y],[x+1, y+1]], 
        [[x, y],[x, y+1],[x, y-1],[x-1, y+1]],
        [[x, y],[x+1, y],[x-1, y],[x-1, y-1]],
        [[x, y],[x, y-1],[x, y+1],[x+1, y-1]]]
    
    T =[[[x, y],[x-1, y],[x+1, y],[x, y+1]], 
        [[x, y],[x, y+1],[x, y-1],[x-1, y]],
        [[x, y],[x+1, y],[x-1, y],[x, y-1]],
        [[x, y],[x, y-1],[x, y+1],[x+1, y]]]

    if shape == 'O':
        Tetromino = O
    elif shape == 'I':
        Tetromino = I[orientation%2]
    elif shape == 'S':
        Tetromino = S[orientation%2] 
    elif shape == 'Z':
        Tetromino = Z[orientation%2]     
    elif shape == 'L':
        Tetromino = L[orientation]
    elif shape == 'J':
        Tetromino = J[orientation]    
    elif shape == 'T':
        Tetromino = T[orientation]

    return Tetromino

merging = False
def T_move(direction='down'):
    global Tetromino, Ty, Tx, Arr, T_orientation, T_shape, prev_Tx, prev_Ty, prev_orientation
    merged = False
    if direction == 'up':
        T_orientation+=1
        if T_orientation == 4:
            T_orientation = 0
            
    elif direction == 'down':
        drop = False
        for i in Tetromino:
            if i[1] >= len(Arr)-1:
                drop = True
                break
            elif Arr[i[1]+1][i[0]] == 1:
                drop = True
                break
        if drop and not merging:
            merged = merge()        
            drop = False
            
        else:
            Ty+=1
    elif direction == 'left':
        Tx-=1
    elif direction == 'right':
        Tx+=1
    
    new_Tetromino = T_get_coordinates(Tx, Ty, T_orientation, T_shape)
    move = True
    rotate = False
        # i = [x,y] for each block in Tetromino, i[0] = x, i[1] = y. Arr[row][column]
    for i in new_Tetromino:
        # if Tetromino is out of bound or in contact with a block
        if  i[0] < 0 or \
        i[0] > len(Arr[0])-1 or \
        i[1] > len(Arr)-1 or \
        Arr[i[1]][i[0]] == 1:
            move = False
    if move or merged:
        Tetromino = new_Tetromino
        refresh()
    else:
        Tx = prev_Tx
        Ty = prev_Ty
        T_orientation = prev_orientation

    prev_orientation = T_orientation
    prev_Tx = Tx
    prev_Ty = Ty
    return merged

# update displayed string (Scr)
def refresh():
    global Play

    Scr = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
    if not Play:
        Scr += "\nGame Over!\nYour score: {}\n".format(score) 
    Scr+=  "░░" + ''.join(["░░" for i in range(col)])     #"██████████████████████"
    Scr+= "\n░"
    for y in range(4,row): 

        # Play area
        for x in range(col):
            if Arr[y][x] == 0:
                if [x,y] in Tetromino:
                    Scr += "██"
                else:
                    Scr += "  "            
            else:                
                Scr += "██"
        # Right panel
        if y in range(4,14):
            Scr +="░"
            if y == 4:
                Scr +="  Level: " + str(level)
            if y == 5:
                Scr +="  Score: " + str(score)
            if y == 6:
                Scr +="  Lines: " + str(lines_cleared)
            if y == 8:
                Scr += "  NEXT:"
            if next_T_shape != None:
                Next_T = T_get_coordinates(2, 10, 0, next_T_shape)
                for x in range(5):
                    if [x,y] in Next_T:
                        Scr+="██"
                    else: 
                        Scr+="  "            
            Scr +="\n░"
        else:
            Scr +="░\n░"  
    Scr+= "░" + ''.join(["░░" for i in range(col)])
    print (Scr)


def T_fall():
    while Play:
        if not merging:
            rate = falling_rate[level] if level in falling_rate else rate
            fall_speed = 1/(60/rate)
            time.sleep(fall_speed)
            T_move('down')

def rotate_delay():
    global rotate
    rotate = False
    time.sleep(.16)
    rotate = True


Play = True
rotate = True

refresh()
reset_T()

fall_thread = threading.Thread(target=T_fall)
fall_thread.start()

while Play:
    if lines_cleared >= (level * 10) + 10:
        level += 1

    if keyboard.is_pressed('up') or keyboard.is_pressed('w'):        
        if rotate:
            T_move('up') 
            threading.Thread(target=rotate_delay).start()
    if keyboard.is_pressed('down') or keyboard.is_pressed('s'):
        score+=1
        T_move('down')
        
    if keyboard.is_pressed('left') or keyboard.is_pressed('a'):
        T_move('left')
    if keyboard.is_pressed('right') or keyboard.is_pressed('d'):
        T_move('right')
    if keyboard.is_pressed('esc') or keyboard.is_pressed('q'):
        endgame()
    if keyboard.is_pressed(' '):
        merged = False
        while not merged:
            score+=1
            merged = T_move('down')            
            #time.sleep(1/(60*20))
            

    # testing
    if keyboard.is_pressed(']'):
        lines_cleared +=10
    if keyboard.is_pressed('['):
        lines_cleared -=10
    if keyboard.is_pressed('='):
        lines_cleared +=1
    if keyboard.is_pressed('-'):
        lines_cleared -=1

    time.sleep(.08)
