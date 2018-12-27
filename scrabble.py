import importlib
import discord
from discord.ext import commands
import scrabble_internal as mech
import pickle
import random
import regex as re

flatten = lambda l: [item for sublist in l for item in sublist]


class ScrabbleGame():
    def __init__(self, bot):
        importlib.reload(mech)
        self.bot = bot
        try:
            with open("db/scrabblegames.pkl","rb") as f:
                self.pdb = pickle.load(f)

        except Exception as e:
            print(e)
            self.pdb = {}

        self.letters = [i for i in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"] + [i + i for i in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]

    def __unload(self):
        with open("db/scrabblegames.pkl","wb+") as f:
            pickle.dump(self.pdb,f)

    def getgame(self, ctx):
        return self.pdb[ctx.channel.id][ctx.author.id]

    def ingame(self, ctx):
        try:
            x = self.getgame(ctx)
            return True
        except:
            return False


    @commands.group(brief="Play Scrabble!")
    @commands.guild_only()
    async def scrabble(self, ctx):
        try:
            x = self.pdb[ctx.channel.id]
        except:
            self.pdb[ctx.channel.id] = {}


    @scrabble.command(brief="List all presets")
    async def presets(self,ctx):
        await ctx.send("```\n{}\n```".format(" ".join(i for i in mech.presets)))

    @scrabble.command(brief="List the tiles in a preset")
    async def listtiles(self,ctx,preset):
        if preset not in mech.presets:
            return await ctx.send("Uh oh! You friccin moron! That's an invalid preset!")

        ps = mech.presets[preset]

        message = "```\n"

        for tile in ps:
            letter = tile[0]
            quantity = tile[1]
            value = tile[2]
            #blankvalue = tile[3]
            if quantity != 0:
                if letter != "":
                    message += "{}×{}{} ".format(str(quantity),letter,mech.subscriptify(str(value)))
                else:
                    message += "{}×[] ".format(str(quantity))
        message += "\n```"

        await ctx.send(message)


    @scrabble.command(brief="Start the game")
    async def start(self, ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You're not in a game.")

        game = self.getgame(ctx)

        if game.started:
            return await ctx.send("Uh oh! You friccin moron! This game has already started!")

        player = game.findplayer(ctx.author.id)

        if not player.host:
            return await ctx.send("Uh oh! You friccin moron! You aren't the host!")

        game.startgame()

        for p in game.players:
            author = self.bot.get_user(p.id)
            try:
                await author.send("```\n" + p.handstring() + "\n```")
            except:
                await ctx.send("<@{}>, I was unable to send you your rack.")

        await ctx.send(file=discord.File(game.drawboard(), filename="board.png"))


    @scrabble.command(brief="Create a game")
    async def create(self, ctx, preset="english"):

        if self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You're already in a game!")


        if preset not in mech.presets:
            return await ctx.send("Uh oh! You friccin moron! That's an invalid preset!")

        self.pdb[ctx.channel.id][ctx.author.id] = (mech.Scrabble(preset))
        game = self.pdb[ctx.channel.id][ctx.author.id]
        game.players.append(mech.Player(ctx.author.id,ctx.author.name,True))
        await ctx.send("Game created! (Preset: {})".format(preset))


    @scrabble.command(brief="Join a game")
    async def join(self, ctx, user: str):
        if self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You're already in a game!")

        try:
            game = self.pdb[ctx.channel.id][ctx.message.mentions[0].id]
        except:
            return await ctx.send("Uh oh! You friccin moron! That player doesn't have a game!")

        if game.started:
            return await ctx.send("Uh oh! You friccin moron! This game has already started!")
        else:
            self.pdb[ctx.channel.id][ctx.author.id] = game
            game.players.append(mech.Player(ctx.author.id,ctx.author.name,False))
            await ctx.send("You have joined " + user + "'s Game!")

    @scrabble.command(brief="Leave your game")
    async def leave(self, ctx):

        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.channel.id][ctx.author.id]

        leaver = game.findplayer(ctx.author.id)

        for tile in leaver.tiles:
            game.bag.append(tile)
            random.shuffle(game.bag)

        game.players.remove(leaver)
        self.pdb[ctx.channel.id].pop(ctx.author.id, None)

        if len(game.players) != 0:
            game.players[0].host = True
            game.turn = game.turn % len(game.players)

        await ctx.send("You have left your game!")

    @scrabble.command(aliases=["info","board"],brief="View the board")
    async def status(self, ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.channel.id][ctx.author.id]

        if game.started == False:
            return await ctx.send("Uh oh! You friccin moron! The game hasn't started yet!")

        return await ctx.send(file=discord.File(game.drawboard(), filename="board.png"))

    @scrabble.command(brief="View your hand",aliases=["rack","tiles"])
    async def hand(self, ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.channel.id][ctx.author.id]

        if game.started == False:
            return await ctx.send("Uh oh! You friccin moron! The game hasn't started yet!")

        player = game.findplayer(ctx.author.id)
        author = self.bot.get_user(player.id)
        try:
            await author.send("```\n" + player.handstring() + "\n```")
            await ctx.send(":mailbox:")
        except:
            await ctx.send("<@{}>, I was unable to send you your rack.")

    def convert_position(self,position):
        row = int("".join([i for i in position if i in "0123456789"]))
        column = self.letters.index("".join([i for i in position if i not in "0123456789"]))

        return (column,row-1)


    @scrabble.command(brief="Exchange some of your tiles for new ones.",aliases=["swap"])
    async def exchange(self, ctx, *tiles):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.channel.id][ctx.author.id]

        if game.started == False:
            return await ctx.send("Uh oh! You friccin moron! The game hasn't started yet!")

        player = game.findplayer(ctx.author.id)

        if game.players[game.turn%len(game.players)] != player:
            return await ctx.send("Uh oh! You friccin moron! It's not your turn!")


        estring = "".join(tiles)
        estring = "".join(i for i in estring if i in [str(i+1) for i in range(len(player.tiles))])

        if estring != "".join(tiles):
            return await ctx.send("Uh oh! You friccin moron! That's an invalid list of tiles!")

        handsize = len(player.tiles)

        tiles = [int(i) for i in estring]
        removed = [player.tiles[i] for i in range(handsize) if i+1 in tiles]
        player.tiles = [player.tiles[i] for i in range(handsize) if i+1 not in tiles]

        for i in range(len(tiles)):
            player.tiles.append(game.bag.pop())

        player.sortrack()

        game.bag.extend(removed)
        random.shuffle(game.bag)

        game.turn = (game.turn + 1)%len(game.players)

        if len(tiles) == 0:
            return await ctx.send("You have passed your turn!")
        else:
            await ctx.send("You have exchanged the following tiles: " + " ".join(str(i) for i in  tiles))

            author = self.bot.get_user(player.id)
            try:
                await author.send("```\n" + player.handstring() + "\n```")
            except:
                await ctx.send("<@{}>, I was unable to send you your rack.")

        await ctx.send(file=discord.File(game.drawboard(), filename="board.png"))

    @scrabble.command(brief="Play tiles on the board")
    async def play(self, ctx, coordinate, direction, *, tiles):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.channel.id][ctx.author.id]

        if game.started == False:
            return await ctx.send("Uh oh! You friccin moron! The game hasn't started yet!")

        player = game.findplayer(ctx.author.id)

        if game.players[game.turn%len(game.players)] != player:
            return await ctx.send("Uh oh! You friccin moron! It's not your turn!")


        if not game.casesensitive:
            if game.chars[0].islower():
                tiles = tiles.lower()
            else:
                tiles = tiles.upper()

        #SPLIT INTO TOKENS

        components = game.chars + ["[" + x + "]" for x in game.chars]
        components = sorted(components, key=lambda x: len(x),reverse=True)
        regex = "|".join([i.replace("[","\[").replace("]","\]") for i in components]) + "|[^ ]"
        tokens = re.findall(regex,tiles)
        try:
            tokens = [(x,game.valuemap[x],False) if not x.startswith("[") else (x[1:-1],0,True) for x in tokens]
        except KeyError:
            return await ctx.send("Uh oh! You friccin moron! You played a letter not in the distribution!")

        #await ctx.send(tokens)
        if len(tokens) < 2:
            return await ctx.send("Uh oh! You friccin moron! You can't play a word with fewer than two letters!")


        horizontal = "left right l r > < horiz horizontal h".split(" ")
        vertical = "down d vert vertical v".split(" ")

        if direction.lower() in horizontal:
            delta = (1,0)
        elif direction.lower() in vertical:
            delta = (0,1)
        else:
            return await ctx.send("Uh oh! You friccin moron! That's an invalid direction!")


        opos = self.convert_position(coordinate.upper())
        pos = opos


        temp_rack = player.tiles[:]

        uses = 0

        neighbors = []

        for i in tokens:
            if not (0 <= pos[0] < len(game.tileboard)) or not (0 <= pos[1] < len(game.tileboard)):
                return await ctx.send("Uh oh! You friccin moron! You can't play that word there!")

            neighbors.extend([
                (pos[0]-1,pos[1]),
                (pos[0]+1,pos[1]),
                (pos[0],pos[1]-1),
                (pos[0],pos[1]+1)
            ])


            cur_tile = game.tileboard[pos[0]][pos[1]]
            if cur_tile is not None:
                if cur_tile != i:
                    return await ctx.send("Uh oh! You friccin moron! You can't play that word there!")
            else:
                if (i[0],i[1]) not in temp_rack:
                    if not i[2]:
                        return await ctx.send("Uh oh! You friccin moron! You can't play a tile that you don't have!")
                    else:
                        if any(q[0] == "" for q in temp_rack):
                            temp_rack.pop([q[0] for q in temp_rack].index(""))
                        else:
                            return await ctx.send("Uh oh! You friccin moron! You can't play a tile that you don't have!")
                else:
                    temp_rack.remove((i[0],i[1]))

                uses += 1

            pos = (pos[0] + delta[0], pos[1] + delta[1])

        neighbors = [p for p in neighbors if (0 <= p[0] < len(game.tileboard)) and (0 <= p[1] < len(game.tileboard))]

        half = round(len(game.tileboard)//2)

        if all(game.tileboard[i[0]][i[1]] is None and i != (half,half) for i in neighbors):
            return await ctx.send("Uh oh! You friccin moron! That play isn't connected to another tile!")


        new_placements = []

        words_to_score = []

        pos = opos


        for i in tokens:
            if game.tileboard[pos[0]][pos[1]] is None:
                new_placements.append(pos)
            game.tileboard[pos[0]][pos[1]] = i
            pos = (pos[0] + delta[0], pos[1] + delta[1])

            #word.append((pos,i[1],i[0]))

        backwards = (-delta[0],-delta[1])

        pos = opos

        #extrapolate current word
        word = []

        first_tile = game.tileboard[pos[0]][pos[1]]
        word = [(pos, first_tile[1], first_tile[0])]

        spos = (pos[0] + delta[0], pos[1] + delta[1])
        # scan forward
        while True:
            if not (0 <= spos[0] < len(game.tileboard)) or not (0 <= spos[1] < len(game.tileboard)):
                break
            if game.tileboard[spos[0]][spos[1]] is None:
                break

            t = game.tileboard[spos[0]][spos[1]]
            word.append((spos, t[1], t[0]))
            spos = (spos[0] + delta[0], spos[1] + delta[1])

        # scan backwards
        spos = (pos[0] + backwards[0], pos[1] + backwards[1])
        while True:
            if not (0 <= spos[0] < len(game.tileboard)) or not (0 <= spos[1] < len(game.tileboard)):
                break
            if game.tileboard[spos[0]][spos[1]] is None:
                break

            t = game.tileboard[spos[0]][spos[1]]
            word = [(spos, t[1], t[0])] + word
            spos = (spos[0] + backwards[0], spos[1] + backwards[1])
        words_to_score.append(word)

        pos = opos

        neg_antidelta = (-delta[1],-delta[0])
        pos_antidelta = (delta[1],delta[0])

        #extrapolate new words
        for i in tokens:
            if pos in new_placements:
                word = [(pos,i[1],i[0])]

                spos = (pos[0] + neg_antidelta[0], pos[1] + neg_antidelta[1])
                #scan neg_antidelta
                while True:
                    if not (0 <= spos[0] < len(game.tileboard)) or not (0 <= spos[1] < len(game.tileboard)):
                        break
                    if game.tileboard[spos[0]][spos[1]] is None:
                        break

                    t = game.tileboard[spos[0]][spos[1]]
                    word = [(spos,t[1],t[0])] + word
                    spos = (spos[0] + neg_antidelta[0], spos[1] + neg_antidelta[1])

                # scan pos_antidelta
                spos = (pos[0] + pos_antidelta[0], pos[1] + pos_antidelta[1])
                while True:
                    if not (0 <= spos[0] < len(game.tileboard)) or not (0 <= spos[1] < len(game.tileboard)):
                        break
                    if game.tileboard[spos[0]][spos[1]] is None:
                        break

                    t = game.tileboard[spos[0]][spos[1]]
                    word.append((spos, t[1], t[0]))
                    spos = (spos[0] + pos_antidelta[0], spos[1] + pos_antidelta[1])

                if len(word) != 1:
                    words_to_score.append(word)

            pos = (pos[0] + delta[0], pos[1] + delta[1])


        message = "```\nScore Ledger\n"
        scoredelta = 0
        if uses == 7:
            message += "Bingo - 50 points\n"
            scoredelta = 50


        for w in words_to_score:
            ws = self.score_word(game,w,new_placements)
            message += "Played {} - {} points\n".format("".join(i[2] for i in w),str(ws))
            scoredelta += ws

        message += "Total Score Gain - {} points\n".format(str(scoredelta))
        message += "```"
        player.score += scoredelta

        player.tiles = temp_rack[:]

        while len(game.bag) != 0 and len(player.tiles) < 7:
            player.tiles.append(game.bag.pop())

        game.turn = (game.turn + 1)%len(game.players)
        author = self.bot.get_user(player.id)
        try:
            await author.send("```\n" + player.handstring() + "\n```")
        except:
            await ctx.send("<@{}>, I was unable to send you your rack.")

        await ctx.send(message,file=discord.File(game.drawboard(), filename="board.png"))


    def score_word(self,game,word,newly_placed):
        word_multiplier = 1
        score = 0

        for letter in word:
            ls = letter[1]
            pos = letter[0]
            if pos in newly_placed:
                tile_bonus = game.board[pos[0]][pos[1]]
                if tile_bonus is not None:
                    if tile_bonus[1] in ["W","X"]:
                        word_multiplier += tile_bonus[0]
                    elif tile_bonus[0] in ["L"]:
                        ls *= tile_bonus[0]

            score += ls

        score *= word_multiplier
        return score

def setup(bot):
    bot.add_cog(ScrabbleGame(bot))