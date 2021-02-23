import random
from PIL import Image, ImageDraw, ImageFont
import hsluv
import io


'''
    2 blank tiles (scoring 0 points)
    1 point: E ×12, A ×9, I ×9, O ×8, N ×6, R ×6, T ×6, L ×4, S ×4, U ×4
    2 points: D ×4, G ×3
    3 points: B ×2, C ×2, M ×2, P ×2
    4 points: F ×2, H ×2, V ×2, W ×2, Y ×2
    5 points: K ×1
    8 points: J ×1, X ×1
    10 points: Q ×1, Z ×1'''


subs = {"0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉"}
def subscriptify(string):
    s = string
    for i in subs:
        s = s.replace(i,subs[i])
    return s

presets = {
    "english" : [
        ("",2,0),
        ("E",12,1),
        ("A",9,1),
        ("I",9,1),
        ("O",8,1),
        ("N",6,1),
        ("R",6,1),
        ("T",6,1),
        ("L",4,1),
        ("S",4,1),
        ("U",4,1),
        ("D",4,2),
        ("G",3,2),
        ("B",2,3),
        ("C",2,3),
        ("M",2,3),
        ("P",2,3),
        ("F",2,4),
        ("H",2,4),
        ("V",2,4),
        ("W",2,4),
        ("Y",2,4),
        ("K",1,5),
        ("J",1,8),
        ("X",1,8),
        ("Q",1,10),
        ("Z",1,10)
    ],
    "spanish" : [
        ("",2,0),
        ("A",12,1),
        ("E",12,1),
        ("O",9,1),
        ("I",6,1),
        ("S",6,1),
        ("N",5,1),
        ("R",5,1),
        ("U",5,1),
        ("L",5,1),
        ("T",4,1),
        ("D",5,2),
        ("G",2,2),
        ("C",4,3),
        ("B",2,3),
        ("M",2,3),
        ("P",2,3),
        ("H",2,4),
        ("F",1,4),
        ("V",1,4),
        ("Y",1,4),
        ("CH",1,5),
        ("Q",1,5),
        ("J",1,8),
        ("LL",1,8),
        ("Ñ",1,8),
        ("RR",1,8),
        ("X",1,8),
        ("Z",1,10)
    ],
    "english_blanks": [
        ("", 20, 0),
        ("E", 12, 1),
        ("A", 9, 1),
        ("I", 9, 1),
        ("O", 8, 1),
        ("N", 6, 1),
        ("R", 6, 1),
        ("T", 6, 1),
        ("L", 4, 1),
        ("S", 4, 1),
        ("U", 4, 1),
        ("D", 4, 2),
        ("G", 3, 2),
        ("B", 2, 3),
        ("C", 2, 3),
        ("M", 2, 3),
        ("P", 2, 3),
        ("F", 2, 4),
        ("H", 2, 4),
        ("V", 2, 4),
        ("W", 2, 4),
        ("Y", 2, 4),
        ("K", 1, 5),
        ("J", 1, 8),
        ("X", 1, 8),
        ("Q", 1, 10),
        ("Z", 1, 10)
    ],
    "ipa_english": [
        ("",2,0),
        ("ə",7,1),
        ("n",7,1),
        ("ɪ",6,1),
        ("l",6,1),
        ("s",6,1),
        ("t",6,1),
        ("k",5,1),
        ("ɹ",5,1),
        ("d",5,1),
        ("i",4,1),
        ("m",4,1),
        ("ɛ",3,1),
        ("z",3,1),
        ("ɑ",3,2),
        ("æ",3,2),
        ("b",2,2),
        ("oʊ",2,2),
        ("p",2,2),
        ("aɪ",2,3),
        ("eɪ",2,3),
        ("f",2,3),
        ("g",2,3),
        ("ɔ",2,3),
        ("v",2,3),
        ("h",1,4),
        ("ŋ",1,4),
        ("ʃ",1,4),
        ("u",1,4),
        ("w",1,4),
        ("dʒ",1,5),
        ("j",1,5),
        ("tʃ",1,5),
        ("aʊ",1,8),
        ("ɔɪ",1,8),
        ("θ",1,8),
        ("ʊ",1,8),
        ("ð",1,10),
        ("ʒ",1,10)
    ],
    "math" : [
        ("",3,0),
        ("=",20,1),
        ("0",7,1),
        ("1",7,1),
        ("2",7,1),
        ("3",6,2),
        ("4",6,2),
        ("5",6,2),
        ("6",5,3),
        ("7",5,3),
        ("8",5,3),
        ("+",4,3),
        ("-",4,3),
        ("9",4,4),
        ("×",4,4),
        ("÷",4,4),
        ("^",3,10),
        ("√",3,10)
    ],
    "romaji" : [
        ("",2,0),
        ("U",13,1),
        ("A",12,1),
        ("I",12,1),
        ("O",10,1),
        ("N",7,1),
        ("K",6,2),
        ("S",6,2),
        ("E",5,2),
        ("R",4,2),
        ("T",4,2),
        ("H",4,3),
        ("M",3,3),
        ("G",2,4),
        ("Y",2,4),
        ("B",2,5),
        ("D",2,5),
        ("J",1,6),
        ("Z",1,6),
        ("F",1,8),
        ("P",1,8),
        ("W",1,8),
        ("C",1,10),
        ("V",0,0,20)
    ],

}

'''
       2 blank tiles (scoring 0 points)
   1 point: ə ×7, n ×7, ɪ ×6, l ×6, s ×6, t ×6, k ×5, ɹ ×5, d ×4, i ×4, m ×4, ɛ ×3, z ×3
   2 points: ɑ ×3, æ ×3, b ×2, oʊ ×2, p ×2
   3 points: aɪ ×2,eɪ ×2, f ×2, ɡ ×2, ɔ ×2, v ×2
   4 points: h ×1, ŋ ×1, ʃ ×1, u ×1, w ×1
   5 points: dʒ ×1, j ×1, tʃ ×1
   8 points: aʊ ×1, ɔɪ ×1, θ ×1, ʊ ×1
   10 points: ð ×1, ʒ ×1
   '''

board_template = [
    [(2,"X"), None, None, None, (2,"L"),None,None,(3,"W"),None,None,(2,"L")],
    [None, (2,"L"),None,None,None,(2,"L"),None,None,(2,"W"),None,None],
    [None,None,(3,"L"),None,None,None,(3,"L"),None,None,(2,"W"),None],
    [None,None,None,(2,"W"),None,None,None,None,None,None,(3,"W")],
    [(2,"L"),None,None,None,(2,"W"),None,None,(2,"L"),None,None,None],
    [None,(2,"L"),None,None,None,(2,"W"),None,None,(4,"L"),None,None],
    [None,None,(3,"L"),None,None,None,(2,"W"),None,None,(3,"L"),None],
    [(3,"W"),None,None,None,(2,"L"),None,None,(3,"W"),None,None,(2,"L")],
    [None,(2,"W"),None,None,None,(4,"L"),None,None,(2,"W"),None,None],
    [None,None,(2,"W"),None,None,None,(3,"L"),None,None,(2,"W"),None],
    [(2,"L"),None,None,(3,"W"),None,None,None,(2,"L"),None,None,(4,"W")]
]


def formattile(tile):
    l = tile[0] if tile[0] != "" else "[]"
    v = subscriptify(str(tile[1])) if tile[1] != 0 else ""
    return l + v

class Player():
    def __init__(self,id,name,host):
        self.id = id
        self.name = name
        self.host = host
        self.tiles = []
        self.hue = None
        self.score = 0

    def handstring(self):
        return " ".join([formattile(i) for i in self.tiles])

    def sortrack(self):
        self.tiles = sorted(self.tiles, key=lambda x: x[0])


class Scrabble:
    def __init__(self,preset):
        self.started = False
        self.players = []
        self.bag = []
        self.preset = preset
        self.board = None
        self.tileboard = None
        self.turn = 0


        #TILE DATA

        if self.preset in presets:
            ps = presets[self.preset]
            self.tileset = []
            self.valuemap = {}
            self.blankvaluemap = {}

            for i in ps:
                self.valuemap[i[0]] = i[2]
                if len(i) >= 4:
                    self.blankvaluemap[i[0]] = i[3]
                else:
                    self.blankvaluemap[i[0]] = 0
                self.tileset.append((i[0],i[2]))

        self.chars = [i[0] for i in self.tileset]
        self.chars.remove("")


        #self.digraphs = any(len(i) != 1 for i in self.chars)
        self.casesensitive = any(not (i.isupper() or i.islower()) for i in self.chars)


        #END TILE DATA

    def findplayer(self,id):
        for player in self.players:
            if player.id == id:
                return player

        return None


    def startgame(self):
        self.started = True

        bag_multiplier = len(self.players)//4

        if self.preset in presets:
            for i in presets[self.preset]:
                for j in range(i[1]*(1+bag_multiplier)):
                    self.bag.append((i[0],i[2]))

        random.shuffle(self.bag)

        for n,p in enumerate(self.players):
            p.hue = 360 * n/len(self.players)


        board_width = min(8 + max(len(self.players)-4,0),11)

        b = [i[:board_width] for i in board_template][:board_width]
        b = [i[1:][::-1] + i for i in b]
        self.board = b[1:][::-1] + b[:]

        self.tileboard = [[None for i in range(len(self.board))] for j in range(len(self.board))]


        for p in self.players:
            for i in range(7):
                p.tiles.append(self.bag.pop())

            p.sortrack()





    def drawboard(self):
        return game_image(self)


#DRAW CODE BELOW THIS LINE


def converthsv(hsv):
    t = hsluv.hsluv_to_rgb(hsv)
    i = tuple(int(i * 255) for i in t)
    return i

letters = [i for i in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"] + ["AA","BB","CC","DD"]

def getfont(size):
    return ImageFont.truetype("./cmdimages/anguleux.ttf",size)


#Draws text at the given position
def draw_outline_text(draw, text, coords, font, shadowcolor):
    x,y = coords
    draw.text((x - 5, y), text, font=font, fill=shadowcolor)
    draw.text((x + 5, y), text, font=font, fill=shadowcolor)
    draw.text((x, y - 5), text, font=font, fill=shadowcolor)
    draw.text((x, y + 5), text, font=font, fill=shadowcolor)

def center_text(draw, text, coords, font, fill, outline):
    wfont, hfont = draw.textsize(text, font=font)
    c = (coords[0]-wfont/2,coords[1]-hfont/2)
    if outline: draw_outline_text(draw, text, c, font, (0,0,0))
    draw.text(c, text, fill=fill, font=font)

def right_justify_text(draw, text, coords, font, fill, outline):
    wfont, hfont = draw.textsize(text, font=font)
    c = (coords[0]-wfont,coords[1]-hfont/2)
    if outline: draw_outline_text(draw, text, c, font, (0,0,0))
    draw.text(c, text, fill=fill, font=font)

def left_justify_text(draw, text, coords, font, fill, outline):
    wfont, hfont = draw.textsize(text, font=font)
    c = (coords[0],coords[1]-hfont/2)
    if outline: draw_outline_text(draw, text, c, font, (0,0,0))
    draw.text(c, text, fill=fill, font=font)

def text(draw,text,color,size,location,alignment,outline=False):
    font = getfont(size)

    if alignment == "center":
        center_text(draw, text, location, font, color,outline)
    elif alignment == "right":
        right_justify_text(draw,text,location,font,color,outline)
    elif alignment == "left":
        left_justify_text(draw,text,location,font,color,outline)




def draw_colored_box(d,pos,color):
    points = [(OFFSET + 50*pos[1], OFFSET + 50*pos[0]),
              (OFFSET + 50 * pos[1] + 50, OFFSET + 50 * pos[0] + 50)]

    for i in range(4):
        d.rectangle(points,color)


OFFSET = 35

def game_image(game):

    h = len(game.board)
    w = len(game.board[0])


    m = 0
    for i in game.players:
        m = max(m,len("{} - {}".format(i.name,i.score)))

    m = max(m,len("Tiles in Bag - {}".format(len(game.bag))))
    RIGHT_OFFSET = max(200,16*m)

    image = Image.new("RGBA",(RIGHT_OFFSET+2*OFFSET+50*w,2*OFFSET+50*h),(0,0,0,255))
    d = ImageDraw.Draw(image)



    for x,i in enumerate(game.board):
        for y,j in enumerate(i):
            if game.tileboard[x][y] is not None:
                tile = game.tileboard[x][y]

                letter = tile[0]
                value = tile[1]
                isblank = tile[2]

                draw_colored_box(d,[y,x],(50,50,50))

                color = (200, 200, 0)
                if isblank: color = (200, 0, 200)

                if value != 0: text(d, str(value), color, 18, (
                OFFSET + 50 * x + 27, OFFSET + 50 * y + 22 - (d.textsize(letter, getfont(36))[1] // 2)
                ), "center")
                text(d, letter, color, 36, (OFFSET + 50 * x + 27, OFFSET + 50 * y + 21), "center")

            elif j is not None:
                if j[1] == "L": hue = 180
                if j[1] == "W" or j[1] == "X": hue = 0
                lightness = 50 + (20 * (j[0]-2))

                #print(j[0], j[1], hue, lightness)

                #hue = random.randint(0,360)
                #lightness = random.randint(0,100)

                bstring = str(j[0]) + j[1]
                if bstring == "2X": bstring = "◆"

                pos = (OFFSET + 50 * x + 27, OFFSET + 50 * y + 21)
                text(d, bstring, converthsv((hue,100,lightness)), 36, pos, "center")




    for i in range(h+1):
        ipoint = (OFFSET,OFFSET+(50*i))
        fpoint = (OFFSET+50*w,OFFSET+(50*i))
        d.line([ipoint,fpoint],(200,200,200),2)
    for i in range(w+1):
        ipoint = (OFFSET+(50*i),OFFSET)
        fpoint = (OFFSET+(50*i),OFFSET+50*h)
        d.line([ipoint,fpoint],(200,200,200),2)


    colors = [converthsv((i,100,76,8)) for i in [p.hue for p in game.players]]

    #draw nambers
    for i in range(w):
        pos = (OFFSET + 50*i + 25, h*50 + OFFSET + OFFSET//2)
        text(d,letters[i],(200,200,200),36,pos,"center")

    for i in range(h):
        pos = (OFFSET - 5, OFFSET + i*50 + 5 + OFFSET//2)
        text(d,str(i+1),(200,200,200),36,pos,"right")


    #draw turn N indicator

    ypos = OFFSET

    pos = (OFFSET + 50*w + RIGHT_OFFSET//2, ypos)
    color = colors[game.turn]
    text(d,"Move {}".format(game.turn+1),color,50,pos,"center")

    ypos += d.textsize("Move", getfont(50))[1]

    #Scores
    text(d,"Scores",(200,200,200),40,(OFFSET+ 50*w + RIGHT_OFFSET//2, ypos),"center")
    ypos += d.textsize("Scores", getfont(40))[1]

    for i in sorted(game.players,key=lambda p: p.score, reverse=True):
        scoretext = "{} - {}".format(i.name,i.score)
        pos = (OFFSET + 50*w + RIGHT_OFFSET//2, ypos)
        text(d,scoretext,converthsv((i.hue,100,76,8)),36,pos,"center")
        ypos += d.textsize(scoretext,getfont(36))[1]

    ypos += d.textsize(scoretext,getfont(36))[1]

    #Bag size
    pos = (OFFSET + 50 * w + RIGHT_OFFSET // 2, ypos)
    text(d,"Tiles in Bag - {}".format(len(game.bag)), (200,200,200), 36, pos, "center")


    #text_size = d.multiline_textsize(black_text,getfont(40))[1]
    #d.multiline_text((OFFSET + 50*w + 10, OFFSET + 50*h - text_size - 10),black_text,black_color,getfont(40))
    #d.multiline_text((OFFSET + 50*w + 10, OFFSET), white_text, white_color, getfont(40))

    file = io.BytesIO()
    image.save(file, format="PNG")
    file.seek(0)
    return file