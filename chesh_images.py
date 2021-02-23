from PIL import Image, ImageDraw, ImageChops, ImageFont
import hsluv
import io
import requests
from io import BytesIO

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





def sprite(x,y):
    return (40*x,40*y,40*(x+1),40*(y+1))

def colorchange(sprite,color):
    blank = Image.new("RGBA", (40, 40), color)
    s = ImageChops.add(blank, sprite)
    return s


def spritesheet_size():
    return Image.open("./cmdimages/cheshspritesheet.png").size


def draw_colored_box(d,pos,color):
    points = [(OFFSET + 50*pos[1], OFFSET + 50*pos[0]),
              (OFFSET + 50 * pos[1] + 50, OFFSET + 50 * pos[0] + 50)]

    for i in range(4):
        d.rectangle(points,color)


OFFSET = 35

def hp(n):
    if n > 15:
        return "♥x{}".format(n)
    else:
        s = "♥♥♥♥♥\n" * (n//5) + "♥" * (n%5)
        if n%5 == 0: s = s[:-1]
        return s

def game_image(game,moves=[]):
    h = game.height
    w = game.width

    image = Image.new("RGBA",(200+2*OFFSET+50*w,2*OFFSET+50*h),(0,0,0,255))
    spritesheet = Image.open("./cmdimages/cheshspritesheet.png")
    d = ImageDraw.Draw(image)

    #draw MOVES
    if game.valid_moves != []:
        spos = game.selected_piece

        game.valid_moves = sorted(game.valid_moves,key= lambda b: len(b), reverse=True)

        for move,pos in zip(game.valid_moves, game.sum_moves(spos, game.valid_moves)):

            if game.width > pos[1] >= 0 and game.height > pos[0] >= 0:

                if len(move) == 1:
                    color = (0,0,100)

                    if game.board[pos[0]][pos[1]] is not None:
                        color = (100,0,0)
                else:
                    color = (0,100,0)


                draw_colored_box(d,(pos[0],pos[1]),color)


        draw_colored_box(d, spos, (100,100,0))



    for i in range(h+1):
        ipoint = (OFFSET,OFFSET+(50*i))
        fpoint = (OFFSET+50*w,OFFSET+(50*i))
        d.line([ipoint,fpoint],(200,200,200),2)
    for i in range(w+1):
        ipoint = (OFFSET+(50*i),OFFSET)
        fpoint = (OFFSET+(50*i),OFFSET+50*h)
        d.line([ipoint,fpoint],(200,200,200),2)


    for x,i in enumerate(game.board):
        for y,j in enumerate(i):
            if j is not None:
                psprite = spritesheet.crop(sprite(*j.art))

                hue = j.color
                saturation = [100,50,25,12.5][j.fatigue]
                val = 76.8
                rgb = converthsv((hue,saturation,val))

                psprite = colorchange(psprite, rgb + (0,))

                image.paste(psprite,(OFFSET + 5 + 50*y,OFFSET + 5 + 50*x),psprite)


    white_color = converthsv((game.color_w,100,76.8))
    black_color = converthsv((game.color_b,100,76.8))

    #draw nambers
    for i in range(w):
        pos = (OFFSET + 50*i + 25, h*50 + OFFSET + OFFSET//2)
        text(d,letters[i],(200,200,200),36,pos,"center")

    for i in range(h):
        pos = (OFFSET - 5, OFFSET + i*50 + 5 + OFFSET//2)
        text(d,str(h-i),(200,200,200),36,pos,"right")


    #draw turn N indicator

    pos = (OFFSET + 50*w + 10, OFFSET + 25*h)
    color = white_color if game.ply % 2 else black_color
    text(d,"Move {}".format(game.ply+1),color,50,pos,"left")

    if game.selected_piece is not None:
        titlecase = lambda x: x.replace("_"," ").title()
        string = titlecase(game.board[game.selected_piece[0]][game.selected_piece[1]].name)
        text(d,string,color,30,(pos[0], pos[1] + d.textsize("Move 0",getfont(50))[1]),"left")

    if 0 in game.healths:
        cw = white_color
        cb = black_color

        tw = "Defeat"
        tb = "Defeat"

        if game.healths == [0,0]:
            tw = "Deftory"
            tb = "Deftory"
            cw = converthsv(((game.color_w + 90)%360,100,76.8))
            cb = converthsv(((game.color_b + 90)%360,100,76.8))

        elif game.healths[0] == 0:
            tw = "Victory"
        else:
            tb = "Victory"

        fontsize = max(60,10 * h)
        text(d, tw, cw, fontsize, (OFFSET + 25*w, OFFSET + 25*game.occupied_rows), "center",outline=True)
        text(d,tb,cb,fontsize,(OFFSET + 25*w, OFFSET + 50*game.height - 25*game.occupied_rows), "center",outline=True)

    #Draw HP

    black_text = '{}\n{}'.format(hp(game.healths[0]),game.player_names[0])
    white_text = '{}\n{}'.format(game.player_names[1],hp(game.healths[1]))


    text_size = d.multiline_textsize(black_text,getfont(40))[1]
    d.multiline_text((OFFSET + 50*w + 10, OFFSET + 50*h - text_size - 10),black_text,black_color,getfont(40))
    d.multiline_text((OFFSET + 50*w + 10, OFFSET), white_text, white_color, getfont(40))

    file = io.BytesIO()
    image.save(file, format="PNG")
    file.seek(0)
    return file



def image_from_url(url):
    try:
        response = requests.get(url)
        return Image.open(BytesIO(response.content))
    except:
        return None

def game_gif(game,framerate=250):
    images = []

    for url in game.urls:
        i = image_from_url(url)
        if i is not None:
            images.append(i)


    for i in range(7):
        images.append(images[-1])


    file = io.BytesIO()
    images[0].save(file,
                   format="GIF",
                   save_all=True,
                   append_images=images[1:],
                   duration=framerate,
                   loop=0)

    file.seek(0)
    return file


'''
HSLUV values


Saturation = (100 - 20*fatigue)
Lightness 76.8


INFO

Default Value: 80

Saturations (Fatigue Based): 80/60/40/20

Royals get a +20 HUE'''