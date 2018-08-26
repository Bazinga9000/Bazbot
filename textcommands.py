from random import *
from itertools import cycle
from inspect import signature
import string
import shlex


mariol = {
"a" : "<:sm64_a:288105731712876545>",
"b" : "<:sm64_b:288105731859808256>",
"c" : "<:sm64_c:288105731469606914>",
"d" : "<:sm64_d:288105731893231616>",
"e" : "<:sm64_e:288105731960471552>",
"f" : "<:sm64_f:288105731847356417>",
"g" : "<:sm64_g:288105731662544897>",
"h" : "<:sm64_h:288105731708944385>",
"i" : "<:sm64_i:288105731951951872>",
"j" : "<:sm64_j:288105731981574144>",
"k" : "<:sm64_k:288105731629121537>",
"l" : "<:sm64_l:288105731582853133>",
"m" : "<:sm64_m:288105731708944386>",
"n" : "<:sm64_n:288105731809607681>",
"o" : "<:sm64_o:288105731578658818>",
"p" : "<:sm64_p:288105731964665856>",
"q" : "<:sm64_q:288105731767402497>",
"r" : "<:sm64_r:288105731679453185>",
"s" : "<:sm64_s:288105732090494976>",
"t" : "<:sm64_t:288105731687710721>",
"u" : "<:sm64_u:288105731914203138>",
"v" : "<:sm64_v:288105732035969024>",
"w" : "<:sm64_w:288105732103208960>",
"x" : "<:sm64_x:288105732065460225>",
"y" : "<:sm64_y:288105731813801985>",
"z" : "<:sm64_z:288105731738173441>",
"0" : "<:sm64_0:288105731779985408>",
"1" : "<:sm64_1:288105731398303745>",
"2" : "<:sm64_2:288105731687972865>",
"3" : "<:sm64_3:288105731763208192>",
"4" : "<:sm64_4:288105731780247552>",
"5" : "<:sm64_5:288105731587309569>",
"6" : "<:sm64_6:288105731599761409>",
"7" : "<:sm64_7:288105731406692354>",
"8" : "<:sm64_8:288105731855745024>",
"9" : "<:sm64_9:288105731901751296>",
"?" : "<:sm64_question:288105731830579201>",
"!" : "<:sm64_exclamation:371065483182473236>",
"'" : "<:sm64_quote:370989340295168021>",
'"' : "<:sm64_doublequote:370989340668723200>",
"." : "<:sm64_period:370991917514620929>",
"," : "<:sm64_comma:370991917800095754>",
":" : "<:sm64_colon:370991917845970954>",
";" : "<:sm64_semicolon:370991917703626753>",
"ü" : "<:sm64_u_umlaut:370985018471874560>",
"-" : "<:sm64_dash:370985018472005632>",
" " : "    "}
fullwidthl = ["！",'＂',"＃","＄","％","＆","＇","（","）","＊","＋","，","＝","．","／","０","１","２","３","４","５","６","７","８","９","；",
             "：","＜","＝","＞","？","＠","Ａ","Ｂ","Ｃ","Ｄ","Ｅ","Ｆ","Ｇ","Ｈ","Ｉ","Ｊ","Ｋ","Ｌ","Ｍ","Ｎ","Ｏ","Ｐ","Ｑ","Ｒ","Ｓ","Ｔ",
             "Ｕ","Ｖ","Ｗ","Ｘ","Ｙ","Ｚ","［","＼","］","＾","＿","｀","ａ","ｂ","ｃ","ｄ","ｅ","ｆ","ｇ","ｈ","ｉ","ｊ","ｋ","ｌ","ｍ","ｎ",
             "ｏ","ｐ","ｑ","ｒ","ｓ","ｔ","ｕ","ｖ","ｗ","ｘ","ｙ","ｚ","｛","｜","｝","~","]","   "]
dingsl = ["✏","✂","✁","👓","🕭","🕮","🕯","☎","✆","🖂","🖃","📪","🖬","📬","📭","📁","📂","📄","🗏","🗐","🗄","⌛","🖮","🖰","🖲","🖳","🖴",
         "🖫","🖬","✇","✍","🖎","✌","👌","👍","👎","☜","☞","☝","☟","✋","☺","😐","☹","💣","☠","⚐","🏱","✈","☼","💧","❄","🕆","✞","🕈",
         "✠","✡","☪","☯","ॐ","☸","♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓","j","&","●","❍","■","□","p","❑","❒","⬧","⧫","◆",
         "❖","⬥","⌧","⍓","⌘","❀","✿","❝","❞","   "]
natol = ["Alpha","Bravo","Charlie","Delta","Echo","Foxtrot","Golf","Hotel","India","Juliet","Kilo","Lima","Mike",
        "November","Oscar","Papa","Quebec","Romeo","Sierra","Tango","Uniform","Victor","Whiskey","X-Ray","Yankee","Zulu"]
frakturl = ["!","\"","#","$","%","&","'","(",")","*","+",",","-",".","/","0","1","2","3","4","5","6","7","8","9",
            ":",";","<","=",">","?","@","𝔄","𝔅","𝕮","𝔇","𝔈","𝔉","𝔊","𝕳","𝕴","𝔍","𝔎","𝔏","𝔐","𝔑","𝔒","𝔓","𝔔",
            "𝕽","𝔖","𝔗","𝔘","𝔙","𝔚","𝔛","𝔜","𝖅","[","\\","]","^","_","`","𝔞","𝔟","𝔠","𝔡","𝔢","𝔣","𝔤","𝔥","𝔦","𝔧","𝔨","𝔩",
            "𝔪","𝔫","𝔬","𝔭","𝔮","𝔯","𝔰","𝔱","𝔲","𝔳","𝔴","𝔵","𝔶","𝔷","{","|","}","~"," "]
blackboardl = {"A":"𝔸","a":"𝕒","B":"𝔹","b":"𝕓","C":"ℂ","c":"𝕔","D":"𝔻","d":"𝕕","E":"𝔼","e":"𝕖","F":"𝔽","f":"𝕗",
               "G":"𝔾","g":"𝕘","H":"ℍ","h":"𝕙","I":"𝕀","i":"𝕚","J":"𝕁","j":"𝕛","K":"𝕂","k":"𝕜","L":"𝕃","l":"𝕝",
               "M":"𝕄","m":"𝕞","N":"ℕ","n":"𝕟","O":"𝕆","o":"𝕠","P":"ℙ","p":"𝕡","Q":"ℚ","q":"𝕢","R":"ℝ",
               "r":"𝕣","S":"𝕊","s":"𝕤","T":"𝕋","t":"𝕥","U":"𝕌","u":"𝕦","V":"𝕍","v":"𝕧","W":"𝕎","w":"𝕨",
               "X":"𝕏","x":"𝕩","Y":"𝕐","y":"𝕪","Z":"ℤ","z":"𝕫","Γ":"ℾ","γ":"ℽ","Π":"ℿ","π":"ℼ","Σ":"⅀",
               "0":"𝟘","1":"𝟙","2":"𝟚","3":"𝟛","4":"𝟜","5":"𝟝","6":"𝟞","7":"𝟟","8":"𝟠","9":"𝟡"}
scriptl = {"A":"𝒜","B":"ℬ","C":"𝒞","D":"𝒟","E":"ℰ","F":"ℱ","G":"𝒢","H":"ℋ","I":"ℐ","J":"𝒥","K":"𝒦","L":"ℒ",
           "M":"ℳ","N":"𝒩","O":"𝒪","P":"𝒫","Q":"𝒬","R":"ℛ","S":"𝒮","T":"𝒯","U":"𝒰","V":"𝒱","W":"𝒲","X":"𝒳",
           "Y":"𝒴","Z":"𝒵","a":"𝒶","b":"𝒷","c":"𝒸","d":"𝒹","e":"ℯ","f":"𝒻","g":"ℊ","h":"𝒽","i":"𝒾","j":"𝒿","k":"𝓀",
           "l":"𝓁","m":"𝓂","n":"𝓃","o":"ℴ","p":"𝓅","q":"𝓆","r":"𝓇","s":"𝓈","t":"𝓉","u":"𝓊","v":"𝓋","w":"𝓌",
           "x":"𝓍","y":"𝓎","z":"𝓏"}
alphabet = string.ascii_lowercase




def shuffle_word(word):
    word = list(word)
    shuffle(word)
    return ''.join(word)

def mario(text):
    text = text.lower()

    newtext = ""

    for char in text:
        try:
            newtext += mariol[char]
        except:
            newtext += char

    return newtext

def elongate(text):
    newtext = ""

    for char in text:
        newtext += char
        newtext += " "

    newtext = newtext[:-1]

    return newtext

def bin(text):
    newtext = ""

    for char in text:
        binstring = format(ord(char), 'b')

        while len(binstring) < 8:
            binstring = "0" + binstring

        newtext = newtext + " " + binstring

    newtext = newtext.split(" ",1)[1]

    return newtext

def fullwidth(text):
    newtext = ""

    for char in text:
        try:
            newtext += fullwidthl[ord(char) - 33]
        except:
            newtext += char

    return newtext

def dings(text):
    newtext = ""

    for char in text:
        try:
            newtext += dingsl[ord(char) - 33]
        except:
            newtext += char

    return newtext

def mash(text):
    newtext = ""

    for char in text:
        try:

            choices = [mario, elongate, bin, fullwidth, dings, fraktur, blackboard, script]

            f = choice(choices)

            newtext += f(char)

        except:
            newtext += char

    return newtext

def reverse(text):
    return text[::-1]

def nato(text):
    text = text.lower()

    newtext = ""

    for char in text:
        try:
            o = ord(char.lower())
            assert (o >= 97 and o <= 122)
            newtext = newtext + natol[o - 97] + " "
        except:
            newtext = newtext + char + " "

    return newtext

def unbin(text):
    text = text.replace("\n", " ")
    chars = text.split(" ")
    newtext = ""

    for ch in chars:
        newtext += chr(int(ch, 2))

    return newtext

def scramble(text):
    return " ".join([shuffle_word(word) for word in text.split(" ")])

def hex(text):
    newtext = ""

    for char in text:
        newtext = newtext + " " + ("%x" % ord(char))

    newtext = newtext.split(" ",1)[1]

    return newtext

def unhex(text):
    chars = [int(x, 16) for x in text.split(" ")]
    newtext = ""

    for ch in chars:
        newtext += chr(ch)

    return newtext

def fraktur(text):
    newtext = ""

    for char in text:
        try:
            newtext += frakturl[ord(char) - 33]
        except:
            newtext += char

    return newtext

def blackboard(text):
    newtext = ""

    for char in text:
        try:
            newtext += blackboardl[char]
        except:
            newtext += char

    return newtext

def script(text):
    newtext = ""

    for char in text:
        try:
            newtext += scriptl[char]
        except:
            newtext += char

    return newtext

def cthulu(len):
    return "".join([chr(randint(33,126)) for i in range(int(len))])



newtext = ""
def rot(shift, plaintext):
    shifted_alphabet = alphabet[int(shift) % 26:] + alphabet[:int(shift) % 26]
    newtext = ""
    for i in plaintext:
        try:
            newtext += shifted_alphabet[alphabet.index(i.lower())]
        except:
            newtext += i


    return newtext


def vigenere(text,key):
    newtext = ""

    tl = len(text)
    kl = len(key)

    for i in range(tl):
        tc = text[i]
        kc = key[i%kl]

        if not tc in alphabet:
            newtext += tc
        else:
            tp = ord(tc.lower()) - ord('a')
            kp = ord(kc.lower()) - ord('a')

            newtext += alphabet[(tp + kp) % 26]

    return newtext


import unicodedata
def unirandom():

    while True:
        val = randint(1,100000)

        try:
            char = chr(val)
            name = unicodedata.name(char)

            if name != "UNKNOWN CHARACTER" and not name.startswith("CJK") and not name.startswith("HANGUL"):
                return val
        except:
            pass


def unimash(length):
    return "".join([chr(unirandom()) for i in range(int(length))])

def randspace(text):
    return "".join([i + (" " * randint(1,7)) for i in text])

def capitalize(text):
    return text.title()

def expand(text,times):
    if len(text) < 2: return times * text
    ans = text + "\n"
    for i in range(times):
        ans += (" " * (i+1)).join([j for j in text]) + "\n"
    return ans

commands = [mario,elongate,bin,fullwidth,dings,mash,reverse,nato,unbin,scramble,hex,unhex,fraktur,blackboard,script,
            cthulu,rot,vigenere,randspace,unimash,capitalize,expand]
commandnames = [str(x).split(" ")[1] for x in commands]


class NoCommand(Exception):
    pass

class BadArguments(Exception):
    pass

def chain(text):
    arguments = shlex.split(text)

    cmds = []

    for i in range(len(arguments)):

        if not arguments[0].startswith("--"): break

        param = arguments.pop(0)
        param = param.replace("--","")

        if param not in commandnames:
            raise NoCommand

        f = commands[commandnames.index(param)]

        if len(signature(f).parameters) == 2:
            cmds.append(arguments.pop(0))

        cmds.append(f)

    arg = " ".join(arguments)

    print(cmds)

    for i in range(len(cmds)):
        if len(cmds) == 0: break
        cmd = cmds.pop()

        if len(signature(cmd).parameters) == 2:
            arg = cmd(cmds.pop(),arg)
        else:
            arg = cmd(arg)


    return arg


