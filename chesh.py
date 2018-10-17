import itertools
import random
import importlib
import discord
from discord.ext import commands
import chesh_mechanics as mech
import chesh_images as img
import pickle

class Player():
    def __init__(self,id,host):
        self.id = id
        self.host = host


class CheshGame():
    def __init__(self, bot):
        importlib.reload(mech)
        importlib.reload(img)
        self.bot = bot
        try:
            with open("cheshgames.pkl","rb") as f:
                self.pdb = pickle.load(f)

            for i in self.pdb.values():
                for j in i.values():
                    for k in j.board:
                        for l in k:
                            if l is not None:
                                l.move = l.getmove()

        except Exception as e:
            print(e)
            self.pdb = {}

        self.letters = [i for i in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"] + ["AA", "BB", "CC", "DD"]

    def __unload(self):
        for i in self.pdb.values():
            for j in i.values():
                for k in j.board:
                    for l in k:
                        if l is not None:
                            l.move = None

        with open("cheshgames.pkl","wb+") as f:
            pickle.dump(self.pdb,f)

    def getgame(self, ctx):
        return self.pdb[ctx.channel.id][ctx.author.id]

    def ingame(self, ctx):
        try:
            x = self.getgame(ctx)
            return True
        except:
            return False


    @commands.group(brief="Play Chesh! (A clone of the app of the same name, with more jank)")
    @commands.guild_only()
    async def chesh(self, ctx):
        try:
            x = self.pdb[ctx.channel.id]
        except:
            self.pdb[ctx.channel.id] = {}


    @chesh.command(brief="Create a game played through one account")
    async def selfcreate(self, ctx, board_height: int, board_width: int, *, flags=""):

        if self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You're already in a game!")

        if not (20 >= board_height >= 4 and 20 >= board_width >= 4):
            return await ctx.send("Uh oh! You friccin moron! Your dimensions must be in between four and twenty inclusive.")

        try:
            self.pdb[ctx.channel.id][ctx.author.id] = (mech.Chesh(board_width, board_height, flags=flags))
        except mech.FlagError:
            return await ctx.send("Uh oh! You friccin moron! One of your flags was invalid!")
        game = self.pdb[ctx.channel.id][ctx.author.id]
        game.players.append(Player(ctx.author.id, True))
        game.players.append(Player(ctx.author.id, False))

        game.player_names = ["Player 1","Player 2"]
        game.started = True
        game.selfgame = True

        await ctx.send("Game created!")
        await ctx.send(file=discord.File(img.game_image(game), filename="board.png"))


    @chesh.command(brief="Create a game played through two accounts")
    async def create(self, ctx, board_height : int, board_width : int, *, flags=""):

        if self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You're already in a game!")


        if not (20 >= board_height >= 4 and 20 >= board_width >= 4):
            return await ctx.send("Uh oh! You friccin moron! Your dimensions must be in between four and twenty inclusive.")


        try:
            self.pdb[ctx.channel.id][ctx.author.id] = (mech.Chesh(board_width, board_height, flags=flags))
        except mech.FlagError:
            return await ctx.send("Uh oh! You friccin moron! One of your flags was invalid!")
        game = self.pdb[ctx.channel.id][ctx.author.id]
        game.players.append(Player(ctx.author.id,True))
        game.player_names[0] = ctx.author.name
        await ctx.send("Game created!")
        #await ctx.send(file=discord.File(img.game_image(self.games[-1]), filename="board.png"))


    @chesh.command()
    async def join(self, ctx, user: str):
        if self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You're already in a game!")

        try:
            game = self.pdb[ctx.channel.id][ctx.message.mentions[0].id]
        except:
            return await ctx.send("Uh oh! You friccin moron! That player doesn't have a game!")

        if len(game.players) == 2:
            return await ctx.send("Uh oh! You friccin moron! This game has already started!")
        else:
            self.pdb[ctx.channel.id][ctx.author.id] = game
            game.players.append(Player(ctx.author.id,False))
            game.player_names[1] = ctx.author.name
            game.started = True
            await ctx.send("You have joined " + user + "'s Game!")
            return await ctx.send(file=discord.File(img.game_image(game), filename="board.png"))


    @chesh.command()
    async def leave(self, ctx):

        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.channel.id][ctx.author.id]

        game.players = [x for x in game.players if x.id != ctx.author.id]
        self.pdb[ctx.channel.id].pop(ctx.author.id, None)

        if len(game.players) != 0:
            game.players[0].host = True

        await ctx.send("You have left your game!")


    def convert_position(self,position):
        row = int("".join([i for i in position if i in "0123456789"]))
        column = self.letters.index("".join([i for i in position if i not in "0123456789"]))

        return (row,column)

    @chesh.command()
    async def select(self, ctx, position):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")


        game = self.pdb[ctx.channel.id][ctx.author.id]
        pid = [i.id for i in game.players].index(ctx.author.id)


        if game.started == False:
            return await ctx.send("Uh oh! You friccin moron! The game hasn't started yet!")

        if game.selfgame:
            pid = game.ply % 2

        if pid != game.ply % 2:
            return await ctx.send("Uh oh! You friccin moron! It's not your turn!")


        try:
            pos = self.convert_position(position.upper())
            pos = (game.height - pos[0],pos[1])
        except:
            return await ctx.send("Uh oh! You friccin moron! Your position is invalid!")


        if not game.height > pos[0] >= 0 or not game.width > pos[1] >= 0:
            return await ctx.send("Uh oh! You friccin moron! That position is out of bounds!")


        if game.selected_piece is not None:
            return await ctx.send("You can't select another piece! Move the one you've already selected!")

        if game.board[pos[0]][pos[1]] is None:
            return await ctx.send("Uh oh! You friccin moron! There's nothing on that square!")

        else:

            for i in range(len(game.board)):
                for j in range(len(game.board[i])):
                    p = game.board[i][j]
                    if p is not None:
                        if p.team == [-1,1][pid] and pos != (i,j):
                            p.fatigue = max(0,p.fatigue - game.fatigue_increment)

            piece = game.board[pos[0]][pos[1]]
            if piece.team != [-1,1][pid]:
                return await ctx.send("Uh oh! You friccin moron! That's not your piece!")

            game.selected_piece = pos
            game.valid_moves = piece.move(pos,game.board)

            return await ctx.send(file=discord.File(img.game_image(game), filename="board.png"))


    @chesh.command()
    async def move(self, ctx, *positions):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")


        game = self.pdb[ctx.channel.id][ctx.author.id]
        pid = [i.id for i in game.players].index(ctx.author.id)

        if game.selfgame:
            pid = game.ply % 2

        if game.started == False:
            return await ctx.send("Uh oh! You friccin moron! The game hasn't started yet!")

        if pid != game.ply % 2:
            return await ctx.send("Uh oh! You friccin moron! It's not your turn!")


        try:
            positions = [self.convert_position(i.upper()) for i in positions]
            positions = [(game.height - i[0],i[1]) for i in positions]
        except:
            return await ctx.send("Uh oh! You friccin moron! Your position is invalid!")


        for pos in positions:
            if not game.height > pos[0] >= 0 or not game.width > pos[1] >= 0:
                return await ctx.send("Uh oh! You friccin moron! That position is out of bounds!")

        pl = game.position_lists(game.selected_piece,game.valid_moves)

        if positions not in pl:
            return await ctx.send("Uh oh! You friccin moron! That move is not legal!")
        else:
            current_pos = game.selected_piece
            for p in positions:
                target = game.board[p[0]][p[1]]

                if target is not None:
                    health_index = [0,1,0][target.team]
                    if target.royal:
                        game.healths[health_index] = max(0, game.healths[health_index] - game.royal_value)
                    else:
                        game.healths[health_index] = max(0, game.healths[health_index] - game.common_value)


                game.board[p[0]][p[1]] = game.board[current_pos[0]][current_pos[1]]
                game.board[current_pos[0]][current_pos[1]] = None
                current_pos = p

            pc = game.board[current_pos[0]][current_pos[1]]
            pc.fatigue += game.fatigue_increment
            if pc.fatigue == game.max_fatigue:
                await ctx.send("**Your piece died due to fatigue!**")
                game.board[current_pos[0]][current_pos[1]] = None
                health_index = [0, 1, 0][pc.team]
                if pc.royal:
                    game.healths[health_index] = max(0, game.healths[health_index] - game.royal_value)
                else:
                    game.healths[health_index] = max(0, game.healths[health_index] - game.common_value)


        game.selected_piece = None
        game.valid_moves = []

        game.ply += 1
        game.turn = (game.turn + 1)%2

        await ctx.send("Piece Moved!")
        await ctx.send(file=discord.File(img.game_image(game), filename="board.png"))

        if 0 in game.healths:
            for i in game.players:
                self.pdb[ctx.channel.id].pop(i.id, None)

    @chesh.command(aliases=["info","board"])
    async def status(self, ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.channel.id][ctx.author.id]

        if game.started == False:
            return await ctx.send("Uh oh! You friccin moron! The game hasn't started yet!")

        return await ctx.send(file=discord.File(img.game_image(game), filename="board.png"))


    @chesh.command(brief="Transmute a piece into another [only works if the `debug` flag is enabled]")
    async def inject(self, ctx, position, newpiece):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.channel.id][ctx.author.id]
        pid = [i.id for i in game.players].index(ctx.author.id)

        if "debug" not in game.flags:
            return await ctx.send("Uh oh! You friccin moron! This game is not debug enabled!")
        
        if game.started == False:
            return await ctx.send("Uh oh! You friccin moron! The game hasn't started yet!")

        if pid != game.ply % 2:
            return await ctx.send("Uh oh! You friccin moron! It's not your turn!")
        

        try:
            pos = self.convert_position(position.upper())
            pos = (game.height - pos[0], pos[1])
        except:
            return await ctx.send("Uh oh! You friccin moron! Your position is invalid!")

        if not game.height > pos[0] >= 0 or not game.width > pos[1] >= 0:
            return await ctx.send("Uh oh! You friccin moron! That position is out of bounds!")

        if game.board[pos[0]][pos[1]] is None:
            return await ctx.send("Uh oh! You friccin moron! There's nothing on that square!")

        else:
            piece = game.board[pos[0]][pos[1]]
            #if piece.team != [-1, 1][pid]:
            #    return await ctx.send("Uh oh! You friccin moron! That's not your piece!")
            if piece.team == -1:
                piece.move = mech.invert(mech.pieces[newpiece])
            else:
                piece.move = mech.pieces[newpiece]


            await ctx.send("Replaced the piece on {} (Previously {}) with {}".format(position, piece.name, newpiece))
            piece.name = newpiece

            return await ctx.send(file=discord.File(img.game_image(game), filename="board.png"))


    @chesh.command(brief="Lists all flags usable in b9!chesh.")
    async def flags(self,ctx):
        message = '''
        `orows=<number>` - Sets the number of occupied rows (No more than a quarter the board height)
        `noroyals` - Removes all royals from the game
        `monarchy` - Only capturing royals deals damage (1 per royal)
        `health=<number>` - Sets the started health to the specified number (No more than the total value of all pieces)
        `nofatigue` - Disables fatigue, allowing a piece to be moved arbitrarily many times repeatedly
        `purerandom` - Changes piece generation to be completely random, as opposed to placing stronger pieces towards the back.
        '''

        await ctx.send(message)

def setup(bot):
    bot.add_cog(CheshGame(bot))