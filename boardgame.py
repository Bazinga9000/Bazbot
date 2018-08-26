import discord
from discord.ext import commands
import re

class ABG():
    def __init__(self,board_w,board_h,preplacement):
        self.board = []
        self.gametype = "Board"

        for i in range(board_h):
            try:
                self.board.append(preplacement[i])
            except:
                self.board.append("")
        for i in range(len(self.board)):
            string = self.board[i]

            if len(string) > board_w:
                string = string[:board_w]

            while len(string) < board_w:
                string += "."

            self.board[i] = string

        self.players = []
        self.started = False

        self.w = board_w
        self.h = board_h

        self.capturetoggle = False
        self.captured = []


    def boardstring(self):
        lines = ["".join(i) for i in self.board]
        lines = ['{:>2}'.format(str(i+1)) + "  " + lines[i] for i in range(len(lines))]

        lines = [""] + lines

        topstring = "    " + "".join(["abcdefghijklmnopqrstuvwxyz"[i%26] for i in range(self.w)])
        lines = [topstring] + lines

        if self.w > 26:
            topstring = "                             " + "".join(["a" for i in range(26,self.w)])
            lines = [topstring] + lines


        text = "```\n" + "\n".join(lines).replace("`","ˋ") + "\n```"
        if self.capturetoggle: text += "\n **Captures:**```\n" + " ".join(self.captured) + "```"

        return text

    def move(self,r1,c1,r2,c2):
        if r1 < 0 or r2 < 0 or c1 < 0 or c2 < 0:
            raise Exception
        else:
            piecelist = [list(i) for i in self.board]
            if piecelist[r2][c2] != ".":
                self.captured.append(piecelist[r2][c2])

            piecelist[r2][c2] = piecelist[r1][c1]
            piecelist[r1][c1] = "."
            self.board = ["".join(i) for i in piecelist]

    def place(self,r,c,ch):
        if r < 0 or c < 0:
            raise Exception
        else:
            piecelist = [list(i) for i in self.board]
            piecelist[r][c] = ch[0]
            self.board = ["".join(i) for i in piecelist]

    def swap(self,r1,c1,r2,c2):
        if r1 < 0 or r2 < 0 or c1 < 0 or c2 < 0:
            raise Exception
        else:
            piecelist = [list(i) for i in self.board]
            piece = piecelist[r2][c2]
            piecelist[r2][c2] = piecelist[r1][c1]
            piecelist[r1][c1] = piece
            self.board = ["".join(i) for i in piecelist]

class BoardGame():
    def __init__(self, bot):
        self.bot = bot
        self.games = []
        self.pdb = {}


    alphabet = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z",
                "aa","ab","ac","ad","ae","af","ag","ah","ai","aj","ak","al","am","an"]
    presets = {
        "chess" : [8,8,["rnbqkbnr","pppppppp",".",".",".",".","PPPPPPPP","RNBQKBNR"]],
        "baxany" :  [16,16,["łlĵæчɲaekaɲчæĵlł",
                                "ςdxëtλqhhqλtëxdς",
                                "rgiḱɠğvccvğɠḱigr",
                                "πγzɔonmbbmnoɔzγπ",
                                "pppppppppppppppp",
                                ".",
                                ".",
                                ".",
                                ".",
                                ".",
                                ".",
                                "PPPPPPPPPPPPPPPP",
                                "ΠΓZƆONMBBMNOƆZΓΠ",
                                "RGIḰʛĞVCCVĞʛḰIGR",
                                "ΣDXËTΛQHHQΛTËXDΣ",
                                "ŁLĴÆЧƝAEKAƝЧÆĴLŁ"]],
        "checkers" : [8,8,[".o.o.o.o","o.o.o.o",".o.o.o.o",".",".","x.x.x.x.",".x.x.x.x","x.x.x.x."]],
        "uttt" : [11,11,['...|...|...', '...|...|...', '...|...|...', '---+---+---', '...|...|...', '...|...|...', '...|...|...', '---+---+---', '...|...|...', '...|...|...', '...|...|...']],
        "horde" : [8,8,["rnbqkbnr","pppppppp",".",".","PPPPPPPP","PPPPPPPP","PPPPPPPP","PPPPPPPP"]],
        "shogi" : [9,9,["LNSGKGSNL",".R.....B.","PPPPPPPPP",".",".",".","ppppppppp",".b.....r.","lnsgkgsnl"]]
    }
    def coord2num(self,coord):
        split = lambda s: re.split(r'(\d+)', s)
        c = split(coord)
        return (int(c[1]) - 1, self.alphabet.index(c[0]))
    def getgame(self,ctx):
        return self.pdb[ctx.guild.id][ctx.author.id]
    def ingame(self,ctx):
        try:
            x = self.getgame(ctx)
            return True
        except:
            return False

    @commands.group(brief="Abstract Board Game player")
    async def board(self,ctx):
        try:
            x = self.pdb[ctx.guild.id]
        except:
            self.pdb[ctx.guild.id] = {}

    @board.command()
    async def preset(self,ctx, preset : str):

        if self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You're already in a game!")

        try:
            p = self.presets[preset]
            self.games.append(ABG(p[0], p[1], p[2]))
            self.pdb[ctx.guild.id][ctx.author.id] = self.games[-1]
            self.games[-1].players.append(ctx.author.id)
            await ctx.send("Game created!")
            await ctx.send(self.games[-1].boardstring())
        except:
            return await ctx.send("Uh oh! You friccin moron! That's not a valid preset!")

    @board.command(name="presets")
    async def getpresets(self,ctx):
        await ctx.send("The available presets are: ``" + ", ".join(list(self.presets.keys())) + "``")

    @board.command()
    async def create(self,ctx,length : int, height : int, *pieces):

        if self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You're already in a game!")

        if length > 40 or height > 40:
            return await ctx.send("Uh oh! You friccin moron! That board is too big! The max size is `40x40`!")

        self.games.append(ABG(length, height, pieces))
        self.pdb[ctx.guild.id][ctx.author.id] = self.games[-1]
        self.games[-1].players.append(ctx.author.id)
        await ctx.send("Game created!")
        await ctx.send(self.games[-1].boardstring())

    @board.command()
    async def join(self,ctx,user : str):
        if self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You're already in a game!")

        try:
            game = self.pdb[ctx.guild.id][ctx.message.mentions[0].id]
        except:
            return await ctx.send("Uh oh! You friccin moron! That player doesn't have a game!")

        if game.started:
            return await ctx.send("Uh oh! You friccin moron! This game has already started!")
        else:
            self.pdb[ctx.guild.id][ctx.author.id] = game
            game.players.append(ctx.author.id)
            return await ctx.send("You have joined " + user + "'s Game!")

    @board.command()
    async def leave(self,ctx):

        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]
        game.players.remove(ctx.author.id)

        self.pdb[ctx.guild.id].pop(ctx.author.id,None)

        if len(game.players) == 0:
            self.games.remove(game)

        await ctx.send("You have left your game!")

    @board.command()
    async def move(self,ctx, original_square : str, new_square : str):
        try:
            try:
                game = self.getgame(ctx)
            except:
                await ctx.send("Uh oh! You friccin moron! You aren't in a game!")
                return


            try:
                o = self.coord2num(original_square)
                n = self.coord2num(new_square)
            except:
                await ctx.send("Uh oh! You friccin moron! You entered an invalid coordinate!")
                return

            game.move(o[0],o[1],n[0],n[1])
            await ctx.send("Moved the piece on {} to {}".format(original_square,new_square))
            await ctx.send(game.boardstring())
        except Exception as e:
            await ctx.send("Uh oh! You friccin moron! That's not a valid square!")

    @board.command()
    async def captures(self,ctx):
        try:
            game = self.getgame(ctx)
            game.capturetoggle = not game.capturetoggle

            if game.capturetoggle:
                await ctx.send("Your game will now show captured pieces!")
            else:
                await ctx.send("Your game will no longer show captured pieces!")

        except:
            await ctx.send("Uh oh! You friccin moron! You aren't in a game!")
            return

    @board.command()
    async def swap(self,ctx, original_square, new_square):
        try:
            try:
                game = self.getgame(ctx)
            except:
                await ctx.send("Uh oh! You friccin moron! You aren't in a game!")
                return

            try:
                o = self.coord2num(original_square)
                n = self.coord2num(new_square)
            except:
                await ctx.send("Uh oh! You friccin moron! You entered an invalid coordinate!")
                return

            game.swap(o[0],o[1],n[0],n[1])
            await ctx.send("Swapped the pieces on {} and {}".format(original_square, new_square))
            await ctx.send(game.boardstring())
        except Exception as e:
            await ctx.send("Uh oh! You friccin moron! That's not a valid square!")

    @board.command()
    async def place(self,ctx, square : str, piece : str):
        try:
            try:
                game = self.getgame(ctx)
            except:
                await ctx.send("Uh oh! You friccin moron! You aren't in a game!")
                return


            try:
                o = self.coord2num(square)
            except:
                await ctx.send("Uh oh! You friccin moron! You entered an invalid coordinate!")
                return


            game.place(o[0],o[1],piece)
            await ctx.send("Placed a `{}` on {}".format(piece[0].replace("`","ˋ"), square))
            await ctx.send(game.boardstring())
        except Exception as e:
            await ctx.send("Uh oh! You friccin moron! That's not a valid square!")

    @board.command()
    async def show(self, ctx):
        try:
            game = self.getgame(ctx)
            await ctx.send(game.boardstring())
        except:
            await ctx.send("Uh oh! You friccin moron! You aren't in a game!")
            return


def setup(bot):
    bot.add_cog(BoardGame(bot))




