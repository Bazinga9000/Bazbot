import random
import chesh_images as img
import math
import itertools
from copy import deepcopy
import numpy
import scipy.stats

class FlagError(Exception):
    pass

class Chesh:
    def __init__(self,board_width,board_height,flags=""):
        self.started = False

        self.players = []
        self.player_names = ["undefined","undefined"]

        self.width = board_width
        self.height = board_height

        self.occupied_rows = int(round(board_height/4))
        halfwidth = int(round(board_width/2))
        if self.width % 2:
            halfwidth += 1

        self.board = [[None for i in range(self.width)] for j in range(self.height)]

        self.royal_value = 4
        self.common_value = 1

        self.fatigue_increment = 1
        self.max_fatigue = 4

        self.selected_piece = None
        self.valid_moves = []

        self.color_w = random.randint(0,360)
        self.color_b = (self.color_w + 180)%360

        self.turn = 0
        self.ply = 0

        self.selfgame = False

        # Process Flags to Override things
        flags = [i.split("=") for i in flags.split(" ")]
        self.flags = {}
        for i in flags:
            if len(i) == 1:
                self.flags[i[0]] = ()
            elif len(i) == 2:
                self.flags[i[0]] = i[1]
            else:
                self.flags[i[0]] = i[1:]

        if "orows" in self.flags:
            if int(self.flags["orows"]) > self.height//4 or int(self.flags["orows"]) < 1:
                raise FlagError
            else:
                self.occupied_rows = int(self.flags["orows"])


        #Distribute Royals


        if "noroyals" not in self.flags:
            royals = self.generate_royal_positions()
        else:
            royals = []

        if "monarchy" in self.flags:
            self.common_value = 0
            self.royal_value = 1

        maxhealth = (self.common_value * self.occupied_rows * self.width) + (self.royal_value - self.common_value) * 2 * len(royals)
        if self.width % 2:
            maxhealth -= 1

        health = round(self.occupied_rows * self.width * 0.8)

        if "health" in self.flags:
            if self.flags["health"] == "max":
                health = maxhealth
            else:
                health = int(self.flags["health"])

        if "nofatigue" in self.flags:
            self.fatigue_increment = 0


        if health > maxhealth:
            raise FlagError

        self.healths = [health,health]

        pcs_w = []
        pcs_b = []

        pure_random = False

        if "purerandom" in self.flags:
            pure_random = True

        selectable_pieces = [i for i in pieces.keys() if limit[i] <= min(self.height,self.width)]

        sprite = img.spritesheet_size()
        sprite = tuple(i // 40 for i in sprite)
        sprites = []
        for i in range(sprite[0]):
            for j in range(sprite[1]):
                sprites.append((i,j))

        selectable_sprites = sprites[:]
        random.shuffle(selectable_sprites)

        for i in range(self.occupied_rows):
            pcs_w.append([])
            pcs_b.append([])

            for j in range(halfwidth):

                if not pure_random:
                    row_base = [1,4,6,8,10][self.occupied_rows-i-1]
                    base_tier = row_base - ((row_base/20) * (halfwidth - j + 1))
                    base_tier = max(base_tier,1)

                    piece_tiers = list(tiers[i] for i in selectable_pieces)
                    piece_tiers = [scipy.stats.norm(base_tier, 1).pdf(i) for i in piece_tiers]
                    s = sum(piece_tiers)
                    piece_tiers = [i/s for i in piece_tiers]


                    selected = numpy.random.choice(selectable_pieces,1,p=piece_tiers)[0]
                else:
                    selected = random.choice(selectable_pieces)

                move = pieces[selected]

                sprite = selectable_sprites.pop()
                if len(selectable_sprites) == 0:
                    selectable_sprites = sprites[:]
                    random.shuffle(selectable_sprites)

                royalty = (i,j) in royals

                pcs_w[-1].append(Piece(sprite,self.color_w,1,move,self,selected,royalty))
                pcs_b[-1].append(Piece(sprite,self.color_b,-1,move,self,selected,royalty))

            if board_width % 2:
                pcs_w[-1] = pcs_w[-1][:-1] + deepcopy(pcs_w[-1])[::-1]
                pcs_b[-1] = pcs_b[-1][:-1] + deepcopy(pcs_b[-1])[::-1]
            else:
                pcs_w[-1] = pcs_w[-1] + deepcopy(pcs_w[-1])[::-1]
                pcs_b[-1] = pcs_b[-1] + deepcopy(pcs_b[-1])[::-1]


        for row in range(len(pcs_w)):
            self.board[row] = deepcopy(pcs_w[row])
            self.board[-row-1] = deepcopy(pcs_b[row])


    def square_status(self,x,y):
        if self.board[y][x] == None:
            return 0
        else:
            return self.board[y][x].team



    '''
        royals = [False for i in range(halfwidth)]
        if board_width % 2:
            royals.append(False)
        count = 2
        position = 0
        while position < len(royals):
            royals[position] = True
            position += count

            count += 1


        royal_rows = [False for i in range(self.occupied_rows)]
        count = 2
        position = 0
        while position < len(royal_rows)-1:
            royal_rows[position] = True
            position += count
            count += 1

        royal_rows = royal_rows[::-1]
    '''

    def generate_royal_positions(self):
        valid_rows = []
        valid_columns = []

        halfwidth = self.width//2

        count = 2
        position = 0
        while position < halfwidth:
            valid_columns.append(position)
            position += count
            count += 1

        count = 2
        position = 0
        while position < self.occupied_rows - 1:
            valid_rows.append(position)
            position += count
            count += 1


        return list(itertools.product(valid_rows,valid_columns))


    def sum_move(self,position,move):
        new_pos = position
        for j in move:
            new_pos = (new_pos[0] + j[0], new_pos[1] + j[1])

        return new_pos

    def sum_moves(self,position,moves):
        return [self.sum_move(position,i) for i in moves]

    def position_list(self,position,move):
        poslist = []

        pos = position

        for j in move:
            pos = (pos[0] + j[0], pos[1] + j[1])
            poslist.append(pos)

        return poslist


    def position_lists(self,position,moves):
        return [self.position_list(position,i) for i in moves]





class Piece:
    def __init__(self,art,color,team,move,game,name,royal=False):
        self.art = art
        self.color = color
        self.team = team

        self.piecename = name

        if self.team == 1:
            self.move = move
        elif self.team == -1:
            self.move = invert(move)

        self.royal = royal


        if royal:
            self.color = (self.color + 60) % 360

        self.fatigue = 0
        self.game = game

    def getpos(self):
        for y,i in enumerate(self.game.board):
            for x,j in enumerate(i):
                if j is self:
                    return (x,y)



#The META

def printboard(board):
    for i in board:
        for j in i:
            if j is None:
                print("• ", end="")
            else:
                if j.team == 1:
                    print("+ ", end="")
                elif j.team == -1:
                    print("- ", end="")
        print()

#Switches Perspective between white and black
def invert(f):
    return transform(f,"-")

#Turns leapers into riders
def free(f,distance=-1,strict=False):
    def g(initpos,board):

        moves = f(initpos,board)
        new_moves = []
        for m in moves:
            for i in m:
                new_delta = (0,0) + i[2:]
                #new_moves.append(new_delta)
                dist_counter = 0
                while dist_counter != distance:
                    new_delta = (new_delta[0] + i[0], new_delta[1] + i[1]) + i[2:]

                    new_pos = (initpos[0] + new_delta[0], initpos[1] + new_delta[1])

                    if len(board) > new_pos[0] >= 0 and len(board[0]) > new_pos[1] >= 0:
                        if board[new_pos[0]][new_pos[1]] is not None:
                            if dist_counter == distance-1 or not strict: new_moves.append(new_delta + i[2:])
                            break
                        else:
                            if dist_counter == distance-1 or not strict: new_moves.append(new_delta + i[2:])
                    else:
                        break

                    dist_counter += 1

        return [[i] for i in new_moves]

    return g

#Creates a slider that follows a certain path, repeating if necessary
def free_path(path,distance=-1):
    def g(initpos,board):

        new_moves = []
        dist_counter = 0
        new_delta = (0,0)
        while dist_counter != distance:
            i = path[dist_counter%len(path)]
            new_delta = (new_delta[0] + i[0], new_delta[1] + i[1]) + i[2:]
            new_pos = (initpos[0] + new_delta[0], initpos[1] + new_delta[1])

            if len(board) > new_pos[0] >= 0 and len(board[0]) > new_pos[1] >= 0:
                if board[new_pos[0]][new_pos[1]] is not None:
                    new_moves.append(new_delta + i[2:])
                    break
                else:
                    new_moves.append(new_delta + i[2:])
            else:
                 break

            dist_counter += 1

        return [[i] for i in new_moves]
    return g


#Changes the type of all moves returned by a function
def typemod(f,newtype):
    def g(initpos,board):
        moves = f(initpos,board)

        return [i[:1] + (newtype) for i in moves]

    return g





#Clones pieces along specified symmetry axes
def transform(f,transforms):

    c = lambda b: list(zip(*b[::-1]))

    board_rotations = {
        "0" : lambda b: b,
        "1" : lambda b: c(c(c(b))),
        "2" : lambda b: c(c(b)),
        "3" : lambda b: c(b),
        "|" : lambda b: [i[::-1] for i in b],
        "-" : lambda b: b[::-1],
        "/" : lambda b: c(c(c(b[::-1]))),
        "\\": lambda b: c(b[::-1])


    }


    def shift_rotations(point,shift,rot):
        np = (point[0] - shift[0],point[1] - shift[1]) + point[2:]
        np = point_rots[rot](np)
        np = (np[0] + shift[0],np[1] + shift[1]) + np[2:]
        np = (int(np[0]),int(np[1])) + np[2:]
        return np

    inverses = {
        "0" : "0",
        "1" : "3",
        "2" : "2",
        "3" : "1",
        "|" : "|",
        "-" : "-",
        "/" : "/",
        "\\": "\\"
    }

    point_rots = {
        "0" : lambda t: t,
        "1" : lambda t: (-t[1],t[0]) + t[2:],
        "2" : lambda t: (-t[0],-t[1]) + t[2:],
        "3" : lambda t: (t[1],-t[0]) + t[2:],
        "|" : lambda t: (t[0], -t[1]) + t[2:],
        "-" : lambda t: (-t[0],t[1]) + t[2:],
        "\\" : lambda t: (t[1],t[0]) + t[2:],
        "/": lambda t: (-t[1],-t[0]) + t[2:]
    }

    transforms = transforms.replace("+","02|-")
    transforms = transforms.replace("x","02/\\")
    transforms = transforms.replace("*","0123|-/\\")
    transforms = transforms.replace("4","0123")

    def h(initpos,board):
        moves = []

        board_size = len(board)//2 - 0.5

        for i in transforms:
            new_board = board_rotations[i](board)

            pmoves = f(shift_rotations(initpos,(board_size,board_size),i),new_board)

            for m in pmoves:
                moves.append([point_rots[inverses[i]](k) for k in m])

        return moves

    return h

#Sticks two or more pieces together
def union(*pcs):

    def g(initpos,board):
        return sum((f(initpos,board) for f in pcs),[])
    return g


def remove_full(f):
    def g(initpos,board):
        moves = f(initpos,board)
        moves = [i for i in moves if len(board) > sum((j[0] for j in i), initpos[0]) >= 0]
        moves = [i for i in moves if len(board[0]) > sum((j[1] for j in i), initpos[1]) >= 0]
        moves = [i for i in moves if board[sum((j[0] for j in i), initpos[0])][sum((j[1] for j in i), initpos[1])] is None]
        return moves
    return g


def remove_empty(f):
    def g(initpos,board):
        moves = f(initpos,board)
        moves = [i for i in moves if len(board) > sum((j[0] for j in i), initpos[0]) >= 0]
        moves = [i for i in moves if len(board[0]) > sum((j[1] for j in i), initpos[1]) >= 0]
        moves = [i for i in moves if board[sum((j[0] for j in i), initpos[0])][sum((j[1] for j in i), initpos[1])] is not None]
        return moves
    return g

def collapse(f):
    def g(initpos,board):
        moves = f(initpos,board)
        new_moves = []
        for i in moves:
            new_delta = (0,0)
            for j in i:
                new_delta = (new_delta[0] + j[0], new_delta[1] + j[1])
            new_moves.append([new_delta])

        return new_moves

    return g


def lchain(*pcs,strict=False):
    def g(initpos,board):
        moves = pcs[0](initpos,board)

        all_moves = deepcopy(moves)

        for pc in pcs[1:]:
            new_moves = []

            for i in moves:
                newpos = initpos
                for j in i:
                    newpos = (newpos[0] + j[0], newpos[1] + j[1])
                next_moves = pc(newpos,board)
                for nm in next_moves:
                    temp = deepcopy(i)
                    temp.extend(nm)
                    new_moves.append(temp)

            all_moves.extend(new_moves)

            moves = deepcopy(new_moves)

        unique = []

        for i in all_moves:
            if i not in unique:
                unique.append(i)


        if strict:
            return [i for i in unique if len(i) == len(pcs)]

        return unique
    return g

def gchain(*pcs):
    if len(pcs) == 2:
        a = pcs[0]
        b = pcs[1]
        return collapse(union(a,lchain(remove_full(a),b)))
    else:
        return gchain(gchain(pcs[:-1]), pcs[-1])


def full_leaper(x,y):
    if x == 0 or y == 0:
        return transform(leaper(x,y),"4")
    elif x == y:
        return transform(leaper(x,y),"4")
    else:
        return transform(leaper(x,y),"*")

#The NON META
def leaper(x,y):
    def f(initpos,board):
        return [[(x,y)]]
    return f



#THE PIECES
pieces = {}


#Classical
pieces["pawn"] = leaper(1,0)
pieces["wazir"] = full_leaper(0,1)
pieces["ferz"] = full_leaper(1,1)
pieces["knight"] = full_leaper(1,2)
pieces["rook"] = free(pieces["wazir"])
pieces["bishop"] = free(pieces["ferz"])
pieces["queen"] = union(pieces["rook"],pieces["bishop"])
pieces["king"] = union(pieces["wazir"],pieces["ferz"])

#Leapers
pieces["dabbaba"] = full_leaper(0,2)
pieces["alfil"] = full_leaper(2,2)
pieces["threeleaper"] = full_leaper(0,3)
pieces["camel"] = full_leaper(1,3)
pieces["zebra"] = full_leaper(2,3)
pieces["tripper"] = full_leaper(3,3)
pieces["fourleaper"] = full_leaper(0,4)
pieces["giraffe"] = full_leaper(1,4)
pieces["lancer"] = full_leaper(2,4)
pieces["antelope"] = full_leaper(3,4)
pieces["commuter"] = full_leaper(4,4)
pieces["squirrel"] = union(pieces["knight"],pieces["dabbaba"],pieces["alfil"])
pieces["frog"] = union(pieces["ferz"],pieces["threeleaper"])
pieces["bison"] = union(pieces["knight"],pieces["camel"],pieces["zebra"])

#shogi
pieces["go_between"] = transform(pieces["pawn"],"02")
pieces["side_mover"] = union(pieces["go_between"],transform(free(pieces["go_between"]),"1"))
pieces["vertical_mover"] = transform(pieces["side_mover"],"1")
pieces["dragon_horse"] = union(pieces["king"],pieces["bishop"])
pieces["dragon_king"] = union(pieces["king"],pieces["rook"])
pieces["lance"] = free(pieces["pawn"])
pieces["reverse_chariot"] = free(pieces["go_between"])
pieces["blind_tiger"] = union(pieces["ferz"],transform(pieces["pawn"],"123"))
pieces["ferocious_leopard"] = union(pieces["ferz"],pieces["go_between"])
pieces["drunk_elephant"] = invert(pieces["blind_tiger"])
pieces["stone_general"] = transform(leaper(1,1),"01")
pieces["wood_general"] = free(pieces["stone_general"],2)
pieces["iron_general"] = union(pieces["stone_general"],pieces["pawn"])
pieces["copper_general"] = union(pieces["stone_general"],pieces["go_between"])
pieces["silver_general"] = union(pieces["ferz"],pieces["pawn"])
pieces["gold_general"] = union(pieces["wazir"],pieces["stone_general"])
pieces["coiled_serpent"] = invert(pieces["copper_general"])
pieces["old_monkey"] = invert(pieces["silver_general"])
pieces["reclining_dragon"] = invert(pieces["gold_general"])
pieces["kirin"] = union(pieces["dabbaba"],pieces["ferz"])
pieces["phoenix"] = union(pieces["alfil"],pieces["wazir"])
pieces["flying_stag"] = union(pieces["king"],pieces["reverse_chariot"])
pieces["flying_ox"] = union(pieces["bishop"],pieces["reverse_chariot"])
pieces["free_boar"] = transform(pieces["flying_stag"],"1")
pieces["whale"] = union(pieces["reverse_chariot"],invert(free(pieces["stone_general"])))
pieces["white_horse"] = invert(pieces["whale"])
pieces["horned_falcon"] = union(pieces["bishop"],transform(pieces["lance"],"123"),lchain(pieces["pawn"],pieces["go_between"]))
pieces["soaring_eagle"] = union(pieces["rook"],invert(free(pieces["stone_general"])),transform(lchain(leaper(1,1),transform(leaper(1,1),"02")),"03"))
pieces["lion"] = union(lchain(pieces["king"],pieces["king"]),pieces["squirrel"])
pieces["evil_wolf"] = union(pieces["stone_general"],transform(pieces["pawn"],"013"))
pieces["violent_ox"] = free(pieces["ferz"],2)
pieces["blind_monkey"] = transform(pieces["ferocious_leopard"],"1")
pieces["long_nosed_goblin"] = union(pieces["wazir"],transform(gchain(free(leaper(1,1)),free(leaper(1,-1))),"*"))
pieces["hook_mover"] = transform(gchain(free(leaper(1, 0)), free(leaper(0, 1))), "*")
pieces["old_kite"] = union(pieces["stone_general"],free(pieces["wazir"],2))
pieces["poisonous_snake"] = union(transform(pieces["pawn"],"13"),leaper(2,0),transform(leaper(2,2),"23"))
pieces["w_barbarian"] = union(free(transform(pieces["pawn"],"13"),2),invert(pieces["pawn"]),pieces["stone_general"])
pieces["e_barbarian"] = union(free(pieces["go_between"],2),transform(pieces["pawn"],"13"),pieces["stone_general"])
pieces["n_barbarian"] = union(pieces["blind_monkey"],pieces["wood_general"])
pieces["s_barbarian"] = invert(pieces["n_barbarian"])
pieces["rushing_bird"] = free(pieces["drunk_elephant"])
pieces["flying_horse"] = union(pieces["gold_general"],pieces["wood_general"])
pieces["old_rat"] = union(pieces["wood_general"],free(invert(pieces["pawn"]),2))
pieces["prancing_stag"] = union(pieces["drunk_elephant"],free(transform(pieces["pawn"],"13"),2))
pieces["savage_tiger"] = union(pieces["stone_general"],free(pieces["go_between"],2))
pieces["cavalry"] = transform(lchain(leaper(2,1),union(leaper(2,1),leaper(2,-1),leaper(-2,-1))),"*")
pieces["winged_horse"] = lchain(pieces["knight"],pieces["knight"])
pieces["donkey"] = union(pieces["wazir"],transform(leaper(2,0),"02"))
pieces["side_flyer"] = union(pieces["ferz"],free(transform(pieces["pawn"],"13")))
pieces["square_mover"] = union(pieces["rook"],pieces["stone_general"])
pieces["racing_chariot"] = invert(pieces["square_mover"])

#Shogi-Like
pieces["vertical_flyer"] = transform(pieces["side_flyer"],"1")
pieces["retreater"] = union(pieces["pawn"],free(invert(pieces["pawn"])))
pieces["cowardly_general"] = union(pieces["retreater"],transform(pieces["pawn"],"13"))
pieces["running_dog"] = union(pieces["pawn"],transform(pieces["pawn"],"13"),free(invert(pieces["stone_general"])))
pieces["roaming_assault"] = transform(lchain(pieces["pawn"],pieces["pawn"],pieces["pawn"],pieces["pawn"],pieces["pawn"]),"x")
pieces["thunderclap"] = lchain(pieces["wazir"],pieces["wazir"],pieces["wazir"],pieces["wazir"],pieces["wazir"],strict=True)
pieces["toluene"] = union(pieces["ferocious_leopard"],free(pieces["pawn"],2))
pieces["nitro"] = union(pieces["ferocious_leopard"],free(invert(pieces["pawn"]),2))
pieces["parachlor"] = union(pieces["ferocious_leopard"],free(pieces["go_between"],2))
pieces["antichlor"] = union(pieces["ferocious_leopard"],transform(free(pieces["go_between"],2,strict=True),"13"))

#Combinations
pieces["nightrider"] = free(pieces["knight"])
pieces["banshee"] = union(pieces["nightrider"],pieces["bishop"])
pieces["block"] = union(pieces["squirrel"],pieces["king"])
pieces["paladin"] = union(pieces["bishop"],pieces["knight"])
pieces["marshall"] = union(pieces["rook"],pieces["knight"])
pieces["amazon"] = union(pieces["queen"],pieces["knight"])
pieces["gryphon"] = transform(gchain(leaper(1,1),pieces["lance"]),"*")
pieces["gargoyle"] = union(pieces["gryphon"],pieces["rook"])
pieces["hippogriff"] = transform(gchain(pieces["wazir"],free(pieces["stone_general"])),"x")
pieces["lamassu"] = union(pieces["hippogriff"],pieces["bishop"])
pieces["ziz"] = union(pieces["gargoyle"],pieces["lamassu"])
pieces["octopus"] = transform(gchain(pieces["pawn"],free(leaper(2,1))),"*")
pieces["squid"] = transform(gchain(invert(pieces["pawn"]),free(leaper(2,1))),"*")
pieces["kraken"] = union(pieces["nightrider"],pieces["octopus"])
pieces["leviathan"] = union(pieces["nightrider"],pieces["squid"])
pieces["cthulu"] = union(pieces["octopus"],pieces["nightrider"],pieces["squid"])
pieces["yog-sothoth"] = union(pieces["cthulu"],pieces["ziz"])
pieces["pulser"] = union(pieces["bishop"],pieces["dabbaba"])
pieces["jouster"] = union(pieces["king"],pieces["lance"])
pieces["centaur"] = union(pieces["king"],pieces["knight"])
pieces["stallion"] = union(pieces["knight"],pieces["reverse_chariot"])
pieces["ninja"] = union(pieces["fourleaper"],pieces["threeleaper"],pieces["tripper"],pieces["alfil"],pieces["wazir"])
pieces["samurai"] = union(pieces["ninja"],pieces["camel"])
pieces["battering_ram"] = union(pieces["rook"],pieces["alfil"])
pieces["bearded_dragon"] = union(pieces["dragon_king"],transform(leaper(1,2),"03|\\"))
pieces["frilled_dragon"] = invert(pieces["bearded_dragon"])
pieces["komodo_dragon"] = union(pieces["dragon_king"],pieces["knight"])
pieces["sphinx"] = union(pieces["threeleaper"],pieces["camel"],pieces["zebra"],pieces["tripper"],lchain(pieces["squirrel"],pieces["king"]),lchain(pieces["king"],pieces["king"],pieces["king"]))
pieces["crook"] = transform(free_path([(0,1),(1,0)]),"*")
pieces["cardinal"] = transform(free_path([(1,1),(-1,1)]),"*")


def isprime(n):
    if int(n) != n: return False
    if n == 1: return False
    for i in range(2,round(n**0.5)+1):
        if n%i == 0:
            return False
    return True


def prime_mover(initpos,board):
    moves = []
    ix = initpos[0]
    iy = initpos[1]

    for x,i in enumerate(board):
        for y,j in enumerate(i):
            if isprime(((x-ix)**2 + (y-iy)**2)**0.5):
                moves.append((x-ix,y-iy))

    return [[i] for i in moves]


def bane_of_pythagoras(initpos,board):
    moves = []
    ix = initpos[0]
    iy = initpos[1]

    for x, i in enumerate(board):
        for y, j in enumerate(i):
            if isprime((x - ix) ** 2 + (y - iy) ** 2):
                moves.append((x - ix, y - iy))

    return [[i] for i in moves]

def qroke(initpos,board):
    valid_moves = pieces["rook"](initpos,board)

    all_squares = []
    for i in range(initpos[0],len(board)):
        for j in range(initpos[1],len(board[0])):
            all_squares.append((i,j))

    all_squares = sorted(all_squares,key=lambda p: ((initpos[0]-p[0])**2 + (initpos[1] - p[1])**2)**0.5)


    for sq in all_squares:
        if all((i,j) in valid_moves and board[i][j] is None for i,j in [(sq[0]-1,sq[1]),(sq[0],sq[1]-1)]):
            valid_moves.append(sq)

    return valid_moves


def void(initpos,board):
    moves = []

    for i in range(len(board)):
        for j in range(len(board)):
            moves.append((i-initpos[0],j-initpos[1]))

    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] is not None:
                for k in [-1,0,1]:
                    for l in [-1,0,1]:
                        if (k,l) != (0,0):
                            moves = [m for m in moves if m != ((i+k-initpos[0]),(j+l-initpos[1]))]

    return [[i] for i in moves]


pieces["prime_mover"] = prime_mover
pieces["bane_of_pythagoras"] = bane_of_pythagoras
pieces["roke"] = transform(qroke,"4")
pieces["void"] = void


tiers = {}
tiers['pawn'] = 0.83
tiers['go_between'] = 0.83
tiers['stone_general'] = 1
tiers['wood_general'] = 1
tiers['iron_general'] = 1.17
tiers['retreater'] = 1.5
tiers['alfil'] = 1.67
tiers['threeleaper'] = 1.67
tiers['tripper'] = 1.67
tiers['fourleaper'] = 1.67
tiers['commuter'] = 1.67
tiers['ferz'] = 1.83
tiers['dabbaba'] = 1.83
tiers['lancer'] = 1.83
tiers['wazir'] = 2
tiers['ferocious_leopard'] = 2
tiers['copper_general'] = 2
tiers['silver_general'] = 2
tiers['gold_general'] = 2
tiers['coiled_serpent'] = 2
tiers['old_monkey'] = 2
tiers['reclining_dragon'] = 2
tiers['evil_wolf'] = 2
tiers['cowardly_general'] = 2
tiers['giraffe'] = 2.17
tiers['antelope'] = 2.17
tiers['blind_tiger'] = 2.17
tiers['old_rat'] = 2.25
tiers['lance'] = 2.33
tiers['reverse_chariot'] = 2.33
tiers['frog'] = 2.5
tiers['violent_ox'] = 2.5
tiers['camel'] = 2.67
tiers['kirin'] = 2.75
tiers['blind_monkey'] = 2.75
tiers['old_kite'] = 2.75
tiers['savage_tiger'] = 2.75
tiers['donkey'] = 2.75
tiers['running_dog'] = 2.75
tiers['king'] = 2.83
tiers['drunk_elephant'] = 2.83
tiers['knight'] = 3
tiers['zebra'] = 3
tiers['phoenix'] = 3
tiers['w_barbarian'] = 3
tiers['e_barbarian'] = 3
tiers['n_barbarian'] = 3
tiers['s_barbarian'] = 3
tiers['prancing_stag'] = 3
tiers['poisonous_snake'] = 3.25
tiers['flying_horse'] = 3.25
tiers['antichlor'] = 3.25
tiers['side_mover'] = 3.5
tiers['toluene'] = 3.5
tiers['parachlor'] = 3.5
tiers['antichlor'] = 3.5
tiers['nitro'] = 3.5
tiers['vertical_mover'] = 3.67
tiers['flying_stag'] = 3.75
tiers['side_flyer'] = 4
tiers['jouster'] = 4
tiers['bishop'] = 4.17
tiers['vertical_flyer'] = 4.25
tiers['squirrel'] = 4.33
tiers['bison'] = 4.33
tiers['centaur'] = 4.75
tiers['stallion'] = 4.75
tiers['dragon_horse'] = 5
tiers['racing_chariot'] = 5
tiers['square_mover'] = 5
tiers['block'] = 5
tiers['rook'] = 5.17
tiers['rushing_bird'] = 5.25
tiers['pulser'] = 5.5
tiers['white_horse'] = 5.75
tiers['battering_ram'] = 5.75
tiers['dragon_king'] = 6
tiers['whale'] = 6
tiers['paladin'] = 6
tiers['ninja'] = 6
tiers['flying_ox'] = 6.25
tiers['free_boar'] = 6.25
tiers['horned_falcon'] = 6.25
tiers['soaring_eagle'] = 6.25
tiers['cavalry'] = 6.25
tiers['roke'] = 6.25
tiers['nightrider'] = 6.5
tiers['cardinal'] = 6.75
tiers['marshall'] = 7
tiers['gryphon'] = 7
tiers['hippogriff'] = 7
tiers['bearded_dragon'] = 7
tiers['frilled_dragon'] = 7
tiers['crook'] = 7
tiers['queen'] = 7.33
tiers['winged_horse'] = 7.5
tiers['lion'] = 7.75
tiers['banshee'] = 7.75
tiers['amazon'] = 8
tiers['gargoyle'] = 8
tiers['lamassu'] = 8
tiers['octopus'] = 8
tiers['squid'] = 8
tiers['samurai'] = 8
tiers['komodo_dragon'] = 8
tiers['void'] = 8.5
tiers['kraken'] = 9
tiers['leviathan'] = 9
tiers['roaming_assault'] = 9
tiers['long_nosed_goblin'] = 9.25
tiers['ziz'] = 9.25
tiers['sphinx'] = 9.25
tiers['thunderclap'] = 9.25
tiers['hook_mover'] = 10
tiers['cthulu'] = 10
tiers['yog-sothoth'] = 10.25
tiers['prime_mover'] = 11.5
tiers['bane_of_pythagoras'] = 17

limit = {}
limit['pawn'] = 4
limit['bishop'] = 4
limit['rook'] = 4
limit['queen'] = 4
limit['king'] = 4
limit['wazir'] = 4
limit['ferz'] = 4
limit['go_between'] = 4
limit['side_mover'] = 4
limit['vertical_mover'] = 4
limit['dragon_horse'] = 4
limit['dragon_king'] = 4
limit['lance'] = 4
limit['reverse_chariot'] = 4
limit['blind_tiger'] = 4
limit['ferocious_leopard'] = 4
limit['drunk_elephant'] = 4
limit['stone_general'] = 4
limit['iron_general'] = 4
limit['copper_general'] = 4
limit['silver_general'] = 4
limit['gold_general'] = 4
limit['coiled_serpent'] = 4
limit['old_monkey'] = 4
limit['reclining_dragon'] = 4
limit['flying_stag'] = 4
limit['flying_ox'] = 4
limit['free_boar'] = 4
limit['whale'] = 4
limit['white_horse'] = 4
limit['evil_wolf'] = 4
limit['blind_monkey'] = 4
limit['long_nosed_goblin'] = 4
limit['hook_mover'] = 4
limit['old_kite'] = 4
limit['w_barbarian'] = 4
limit['e_barbarian'] = 4
limit['n_barbarian'] = 4
limit['s_barbarian'] = 4
limit['rushing_bird'] = 4
limit['flying_horse'] = 4
limit['old_rat'] = 4
limit['prancing_stag'] = 4
limit['savage_tiger'] = 4
limit['side_flyer'] = 4
limit['vertical_flyer'] = 4
limit['racing_chariot'] = 4
limit['square_mover'] = 4
limit['gryphon'] = 4
limit['gargoyle'] = 4
limit['hippogriff'] = 4
limit['lamassu'] = 4
limit['ziz'] = 4
limit['octopus'] = 4
limit['squid'] = 4
limit['jouster'] = 4
limit['retreater'] = 4
limit['cowardly_general'] = 4
limit['running_dog'] = 4
limit['toluene'] = 4
limit['nitro'] = 4
limit['parachlor'] = 4
limit['antichlor'] = 4
limit['crook'] = 4
limit['cardinal'] = 4
limit['roke'] = 4
limit['knight'] = 6
limit['dabbaba'] = 6
limit['alfil'] = 6
limit['squirrel'] = 6
limit['wood_general'] = 6
limit['kirin'] = 6
limit['phoenix'] = 6
limit['horned_falcon'] = 6
limit['soaring_eagle'] = 6
limit['lion'] = 6
limit['violent_ox'] = 6
limit['poisonous_snake'] = 6
limit['donkey'] = 6
limit['nightrider'] = 6
limit['banshee'] = 6
limit['block'] = 6
limit['paladin'] = 6
limit['marshall'] = 6
limit['amazon'] = 6
limit['kraken'] = 6
limit['leviathan'] = 6
limit['cthulu'] = 6
limit['yog-sothoth'] = 6
limit['pulser'] = 6
limit['centaur'] = 6
limit['stallion'] = 6
limit['battering_ram'] = 6
limit['bearded_dragon'] = 6
limit['frilled_dragon'] = 6
limit['komodo_dragon'] = 6
limit['threeleaper'] = 8
limit['camel'] = 8
limit['zebra'] = 8
limit['tripper'] = 8
limit['frog'] = 8
limit['bison'] = 8
limit['sphinx'] = 8
limit['fourleaper'] = 10
limit['giraffe'] = 10
limit['lancer'] = 10
limit['antelope'] = 10
limit['commuter'] = 10
limit['cavalry'] = 10
limit['winged_horse'] = 10
limit['ninja'] = 10
limit['samurai'] = 10
limit['roaming_assault'] = 12
limit['thunderclap'] = 12
limit['prime_mover'] = 12
limit['bane_of_pythagoras'] = 12
limit['void'] = 12