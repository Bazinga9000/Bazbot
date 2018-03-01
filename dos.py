import discord
from discord.ext import commands
import random

class CardNotInHand(Exception):
    pass

class InvalidPlay(Exception):
    pass

class MalformedPlay(Exception):
    pass

class InvalidDP(Exception):
    pass

class Player():
    def __init__(self,auth,game):
        self.name = auth.name
        self.id = auth.id
        self.game = game
        self.hand = []
        self.score = 0
        self.drawn = 0
        self.ishost = False

        self.hasdrawn = False

    def draw(self,amount=1):
        for i in range(amount):
            try:
                self.hand.append(self.game.deck.pop())
            except:
                self.game.newdeck()
                self.hand.append(self.game.deck.pop())


    def gethand(self):
        if self.drawn == 0:
            return " ".join(sorted(self.hand,key = self.game.sort))
        else:

            sortedhand = sorted(self.hand,key = self.game.sort)
            message = ""

            recents = self.hand[-self.drawn:]

            for h in sortedhand:
                if h in recents:
                    message = message + "<" + h + "> "
                else:
                    message = message + h + " "

            return message

    def play(self,card,args):

        card = self.game.repalias(card.upper())

        if len(card) == 1 or card == "WF":
            card += " "

        if card not in self.hand:
            raise CardNotInHand

        args = list(args)

        if card[:-1] not in ["W","WF","X"]:
            if len(args) == 0:
                args = [0] + args

        else:
            if len(args) == 1:
                args = [0] + args


        try:
            dp = int(str(args[0]))
            args[0] = dp
            assert 0 <= dp < len(self.game.discardpiles)
        except:
            raise InvalidDP

        rank = card[:-1]
        suit = card[-1]

        topcard = self.game.discardpiles[dp][-1]


        if self.game.ranks[dp] == "💀" and self.game.drawstack != 0 and rank != "💀":
            raise InvalidPlay


        stackable = ["T","F","WF","💀","?","🛡"]

        if self.game.drawstack != 0 and rank not in stackable:
            raise InvalidPlay

        if self.game.colors[dp] != " ":
            if suit != " " and (self.game.ranks[dp] != rank and suit != self.game.colors[dp]):
                if self.game.drawstack != 0 and rank in stackable:
                    pass
                else:
                    raise InvalidPlay

        if not self.validateargs(card,args):
            raise MalformedPlay

        self.game.discardpiles[dp].append(card)
        self.hand.remove(card)
        self.game.colors[dp] = suit
        self.game.ranks[dp] = rank
        self.game.handlecard(card,args)
        self.game.turn = (self.game.turn + self.game.turndirection) % len(self.game.players)


    def validateargs(self,card,args):
        if card[:-1] not in ["W","WF","X"]:
            return True

        if len(args) == 1:
            return False

        card = card[:-1]

        if card in ["W","WF"] and args[1].upper() not in self.game.cmap:
            return False

        if card in ["X"] and self.game.repalias(args[1].upper()) not in self.game.ranklist:
            return False

        return True


class Dos():
    def __init__(self,threshold):
        self.gametype = "Dos"
        self.started = False

        self.players = []
        self.eliminated = []

        self.threshold = threshold


        self.aliases = [["DS","DOUBLESKIP","⇉"],
                        ["COMM","COMMUNIST","COMMUNISM","☭"],
                        ["EYE","REVELATION","REVEL","👁"],
                        ["RS","REVERSESKIP","⤣"],
                        ["GR","GRIM","GRIMREAPER","SKULL","💀"],
                        ["SH","SHUFFLE","⟳"],
                        ["SG","SECONDGO","↶"],
                        ["DT","DRAWTWO","T"],
                        ["DF","DRAWFOUR","F"],
                        ["RV","REVERSE","R"],
                        ["SK","SKIP","S"],
                        ["MD","METADRAW","?"],
                        ["DE","DEF","DRAWFENDER","🛡"],
                        ["MT","MITOSIS","➗"],
                        ["SD","SPLASHDAMAGE","💧"]
                       ]

        self.cmap = {"RED": "R", "GREEN": "G", "YELLOW": "Y", "BLUE": "B", "ORANGE": "O", "PURPLE": "P",
                     "R": "R", "G": "G", "Y": "Y", "B": "B", "O": "O", "P": "P"}

        self.ranklist = ["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15",
                      "T","F","?","R","S","»","⇉","⤣","⟳","↶","👁","$","☭","🛡","➗","💧","💀","X","W","WF"]

        self.colorlist = ["R","O","Y","G","B","P"," "]
        self.sort = lambda x: len(self.ranklist) * self.colorlist.index(x[-1]) + self.ranklist.index(x[:-1])


    def repalias(self,card):
        c = card

        for a in self.aliases:
            for al in a:
                c = c.replace(al,a[-1])

        return c

    def facevalue(self,card):
        rank = card[:-1]

        try:
            return int(rank)
        except:
            return 0

    def newdeck(self):
        nums = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15"]
        specials = ["T","F","R","?","S","⇉","⤣","👁","↶","⟳","X","»"]
        suits = ["R","G","B","Y","O","P"]


        ranks = ["0"] + nums * 2 + specials

        self.deck = []

        for rank in ranks:
            for suit in suits:
                self.deck.append(rank + suit)

        indivs = ["W ","WF "] * 8 + ["☭R","$G","🛡Y","➗B","💧P","💀 "] * 4

        self.deck.extend(indivs)

        random.shuffle(self.deck)

    def initround(self):
        self.discardpiles = [[]]

        self.colors = [""]
        self.ranks = [" "]

        self.turn = 0
        self.turndirection = 1
        self.drawstack = 0

        self.newdeck()

        for player in self.players:
            player.hand = []
            player.draw(7)
            player.drawn = 0

        self.discardpiles[0].append(self.deck.pop())

        while self.discardpiles[0][-1][-1] == " ":
            self.discardpiles[0].append(self.deck.pop())

        self.colors[0] = self.discardpiles[0][-1][-1]
        self.ranks[0] = self.discardpiles[0][-1][:-1]

    def getdeck(self):
        return " ".join(reversed(self.deck))

    def getdp(self,n):
        return " ".join(reversed(self.discardpiles[n]))

    def value(self,card):
        if card[:-1].isdigit():
            return int(card[:-1])
        else:
            values = {"T" : 20, "S" : 20, "R" : 20, "F" : 20, "?" : 30, "W" : 50, "WF" : 50,
                      "⇉" : 20, "⤣" : 20, "☭" : 20, "$" : 40, "👁" : 20, "💀" : 0, "⟳" : 5,
                      "↶" : 20, "X" : 40, "🛡" : 20, "➗" : 40, "💧" : 40, "»" : 20}
            return values[card[:-1]]

    def handlecard(self,card,args):

        dp = int(args[0])

        if card.startswith("S"): #skip
            self.turn = (self.turn + self.turndirection) % len(self.players)
        elif card.startswith("R"): #reverse
            self.turndirection *= -1
        elif card.startswith("T"): #draw two
            self.drawstack += 2
        elif card.startswith("F"): #draw four
            self.drawstack += 4
        elif card.startswith("WF"): #wild draw four
            self.drawstack += 4
            self.colors[dp] = self.cmap[args[1].upper()]
        elif card.startswith("W"): #wild
            self.colors[dp] = self.cmap[args[1].upper()]
        elif card.startswith("⇉"): #doubleskip
            self.turn = (self.turn + self.turndirection + self.turndirection) % len(self.players)
        elif card.startswith("⤣"): #reverse skip
            self.turndirection *= -1
            self.turn = (self.turn + self.turndirection) % len(self.players)
        elif card.startswith("»"): #skipdraw
            self.turn = (self.turn + self.turndirection) % len(self.players)
            self.drawstack += 2
        elif card.startswith("💀"): #grim reaper
            self.drawstack += 8
        elif card.startswith("⟳"): #shuffle
            random.shuffle(self.discardpiles[dp])
            self.colors[dp] = self.discardpiles[dp][-1][-1]
            self.ranks[dp] = self.discardpiles[dp][-1][:-1]
        elif card.startswith("?"): #metadraw
            fv = self.facevalue(self.discardpiles[dp][-2])
            if fv == 0: self.drawstack += 2
            self.drawstack += fv
        elif card.startswith("↶"): #second go
            self.turn = (self.turn - self.turndirection) % len(self.players)

        #communist
        elif card.startswith("☭"):
            cards = []
            for player in self.players:
                hand = player.hand

                for c in hand:
                    cards.append(c)

                player.hand = []

            random.shuffle(cards)

            while len(cards) != 0:
                for player in self.players:
                    player.hand.append(cards.pop())
                    if len(cards) == 0: break
        elif card.startswith("X"): #metadraw
            self.ranks[dp] = self.repalias(args[1].upper())

        #trickledown
        elif card.startswith("$"):
            handsizes = [len(x.hand) for x in self.players]
            poor = handsizes.index(max(handsizes))
            rich = handsizes.index(min(handsizes))
            tax = int(min(handsizes)/2)

            pp = self.players[poor]
            rp = self.players[rich]

            for i in range(tax):
                random.shuffle(rp.hand)
                pp.hand.append(rp.hand.pop())
        #mitosis
        elif card.startswith("➗"):

            half = len(self.discardpiles[dp])//2

            dpa = self.discardpiles[dp][:half]
            dpb = self.discardpiles[dp][half:]

            self.discardpiles[dp] = dpa
            self.colors[dp] = self.discardpiles[dp][-1][-1]
            self.ranks[dp] = self.discardpiles[dp][-1][:-1]

            self.discardpiles.append(dpb)
            self.colors.append(self.discardpiles[-1][-1][-1])
            self.ranks.append(self.discardpiles[-1][-1][:-1])

    def updatescores(self):


        self.temp = []

        for player in self.players:
            player.score += sum([self.value(card) for card in player.hand])
            if player.score >= self.threshold:
                self.temp.append(player)

        #in the case of multiple players eliminated in a round, the person with the higher score is eliminated first.
        for player in sorted(self.temp,key=lambda x: x.score):
            self.eliminated.append(player)

        self.players = [x for x in self.players if x.score < self.threshold]


class DosGame():
    def __init__(self, bot):
        self.bot = bot
        self.games = []
        self.pdb = {}


    def getgame(self,ctx):
        return self.pdb[ctx.guild.id][ctx.author.id]
    def ingame(self,ctx):
        try:
            x = self.getgame(ctx)
            return True
        except:
            return False

    def getplayer(self,game,id):
        return game.players[[x.id for x in game.players].index(id)]

    @commands.group(brief="Dos (the card game)")
    async def dos(self,ctx):
        try:
            x = self.pdb[ctx.guild.id]
        except:
            self.pdb[ctx.guild.id] = {}


        if ctx.guild is None:
            return await ctx.send("Uh oh! You friccin moron! You can't use this command in DMs!")

    @dos.command()
    async def create(self,ctx,*threshold):

        if self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You're already in a game!")

        if len(threshold) != 0:
            try:
                t = int(str(threshold[0]))
            except:
                return await ctx.send("Uh oh! You friccin moron! `threshold` isn't an int!")
        else:
            t = 1


        if t < 1:
            return await ctx.send("Uh oh! You friccin moron! Your threshold can't be less than one!")


        self.games.append(Dos(t))
        self.pdb[ctx.guild.id][ctx.author.id] = self.games[-1]
        self.games[-1].players.append(Player(ctx.author,self.games[-1]))
        self.games[-1].players[0].ishost = True
        await ctx.send("Game created with elimination threshold `" + str(t) + "`!")

    @dos.command()
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
            game.players.append(Player(ctx.author,self.games[-1]))
            return await ctx.send("You have joined " + user + "'s Game!")

    @dos.command()
    async def leave(self,ctx):

        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]

        game.players = [x for x in game.players if x.id != ctx.author.id]
        self.pdb[ctx.guild.id].pop(ctx.author.id,None)

        if len(game.players) == 0:
            self.games.remove(game)
        else:
            game.players[0].ishost = True

            if game.started:
                game.turn = game.turn % len(game.players)

        await ctx.send("You have left your game!")

    @dos.command()
    async def start(self,ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]
        player = self.getplayer(game,ctx.author.id)

        if not player.ishost:
            return await ctx.send("Uh oh! You friccin moron! You aren't the host!")

        game.started = True

        game.initround()

        for player in game.players:
            author = self.bot.get_user(player.id)
            await author.send("**Your Hand**\n```\n" + player.gethand() + "\n```")


        await ctx.send(self.turnmessage(game))

    def turnmessage(self,game):
        message = ""

        for dp in range(len(game.discardpiles)):
            message += "**Discard Pile " + str(dp) + "**\n```\n" + game.getdp(dp) + "\n```\n"

            if game.colors[dp] != " ":
                message += "\n**Color: " + game.colors[dp] + "**"
            else:
                message += "\n**Color: Any Color**"

            message += "\n**Rank: " + game.ranks[dp] + "**\n\n"


        for player in game.players:
            if "👁" in [x[0] for x in player.hand]:
                message += "\n**" + player.name + "'s Hand**\n```md\n" + player.gethand() + "\n```"


        message += "It is now **" + game.players[game.turn].name + "'s** Turn!"
        if game.drawstack != 0:
            message += "\n***THERE ARE " + str(game.drawstack) + " CARDS TO BE DRAWN***\n"

        return message

    def place(self,num):
        if num == 1: return "st"
        if num == 2: return "nd"
        if num == 3: return "rd"
        if num > 20:
            if num % 10 == 1: return "st"
            if num % 10 == 2: return "nd"
            if num % 10 == 3: return "rd"

        return "th"

    def scoremessage(self,game):
        pcount = len(game.players) + len(game.eliminated)

        message = "```diff\n"

        for player in sorted(game.players, key=lambda x: x.score):
            message = message + "+ ​" + player.name + ": " + str(player.score) + "\n"

        message += "--ELIMINATED--\n"

        for c, player in enumerate(game.eliminated):
            rank = len(game.players) + c + 1
            message = message + "- " + player.name + " - " + str(rank) + self.place(rank) + \
                      " (Final Score: " + str(player.score) + ")\n"

        message += "```"

        return message

    @dos.command()
    async def scores(self,ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]

        if not game.started:
            return await ctx.send("Uh oh! You friccin moron! This game hasn't started yet!")

        await ctx.send(self.scoremessage(game))

    @dos.command()
    async def play(self,ctx, card, *args):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]
        player = self.getplayer(game,ctx.author.id)

        if not game.started:
            return await ctx.send("Uh oh! You friccin moron! This game hasn't started yet!")

        if game.players.index(player) != game.turn:
            return await ctx.send("Uh oh! You friccin moron! It's not your turn!")

        try:
            player.play(card,args)
        except CardNotInHand:
            return await ctx.send("Uh oh! You friccin moron! You don't have that card!")
        except InvalidPlay:
            return await ctx.send("Uh oh! You friccin moron! You can't play that card now!")
        except MalformedPlay:
            return await ctx.send("Uh oh! You friccin moron! Something's wrong with your additional arguments!")
        except InvalidDP:
            return await ctx.send("Uh oh! You friccin moron! Your discard pile is invalid!")

        player.hasdrawn = False
        player.drawn = 0

        if len(player.hand) == 0:
            game.updatescores()
            await ctx.send("**The Round has Concluded! The current scores are: **\n" + self.scoremessage(game))

            if len(game.players) != 1:
                game.initround()
                await ctx.send(self.turnmessage(game))
            else:
                await ctx.send("**The game has concluded! " + game.players[0].name + " is the winner!**")
                for player in (game.players + game.eliminated):
                    self.pdb[ctx.guild.id].pop(player.id, None)
                    try:
                        self.games.remove(game)
                    except:
                        pass
        else:
            await ctx.send(self.turnmessage(game))

    @dos.command(aliases=["alias"])
    async def aliases(self,ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]

        message = "```\n"

        for a in game.aliases:
            message += a[-1] + ": " + ", ".join([x.lower() for x in a[:-1]]) + "\n"

        message += "\n```"
        await ctx.send(message)

    @dos.command()
    async def info(self,ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]

        if not game.started:
            return await ctx.send("Uh oh! You friccin moron! This game hasn't started yet!")

        await ctx.send(self.turnmessage(game))

    @dos.command()
    async def turn(self,ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]

        if not game.started:
            return await ctx.send("Uh oh! You friccin moron! This game hasn't started yet!")

        message = "```"

        for p,player in enumerate(game.players):
            message += "\n" + str(p) + " - " + player.name
            if p == game.turn:
                message += " ← Current Turn"

        message += "\n Turn Direction: " + ["=","↓","↑"][game.turndirection] + "\n```"


        await ctx.send(message)


    @dos.command()
    async def draw(self,ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]

        if not game.started:
            return await ctx.send("Uh oh! You friccin moron! This game hasn't started yet!")

        player = self.getplayer(game,ctx.author.id)

        if game.players.index(player) != game.turn:
            return await ctx.send("Uh oh! You friccin moron! It's not your turn!")

        if game.drawstack != 0:
            player.draw(game.drawstack)

            if "💧P" in player.hand:
                prevplayer = game.players[(game.turn - game.turndirection) % len(game.players)]
                prevplayer.draw(game.drawstack // 2)
                prevplayer.drawn = (game.drawstack // 2)

            player.drawn = game.drawstack
            game.drawstack = 0
            game.turn = (game.turn + game.turndirection) % len(game.players)
            await ctx.send(self.turnmessage(game))
        else:
            player.draw(1)
            player.drawn = 1
            player.hasdrawn = True
            await ctx.send("Card Drawn! If you still can't play anything, you can either draw again or pass your turn with `b9!dos pass`")
            await ctx.author.send("**Your Hand**\n```md\n" + player.gethand() + "\n```")

    @dos.command(name="pass")
    async def _pass(self,ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]
        player = self.getplayer(game,ctx.author.id)

        if game.players.index(player) != game.turn:
            return await ctx.send("Uh oh! You friccin moron! It's not your turn!")

        if game.drawstack != 0:
            return await ctx.send("Uh oh! You friccin moron! You can't pass with cards to draw!")

        if not player.hasdrawn:
            return await ctx.send("Uh oh! You friccin moron! You haven't drawn yet!")

        player.hasdrawn = False
        game.turn = (game.turn + game.turndirection) % len(game.players)

        await ctx.send(self.turnmessage(game))

    @dos.command()
    async def hand(self,ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]

        if not game.started:
            return await ctx.send("Uh oh! You friccin moron! This game hasn't started yet!")

        player = self.getplayer(game,ctx.author.id)

        await ctx.author.send("**Your Hand**\n```md\n" + player.gethand() + "\n```")
        await ctx.send(":mailbox:")



    @dos.command()
    async def handsizes(self,ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]

        if not game.started:
            return await ctx.send("Uh oh! You friccin moron! This game hasn't started yet!")

        message = "```\n"

        for player in game.players:
            message = message + player.name + " has " + str(len(player.hand)) + " cards in hand.\n"

        message += "```"
        await ctx.send(message)

    @dos.command()
    async def help(self,ctx):
        message = "View the rules of Dos here:\n<https://docs.google.com/document/d/1GaDNNKicyl1r6bzCzUutcVoDu0j-8Asx_GzLsoabYXg/edit#>"
        await ctx.send(message)

    #commands that will be deleted when testing is complete

    @dos.command()
    async def scry(self,ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]
        await ctx.send("**The Deck**\n```\n" + game.getdeck() + "\n```")

    @dos.command()
    async def give(self,ctx,card):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]
        player = self.getplayer(game,ctx.author.id)
        player.hand.append(game.repalias(card.upper()))

def setup(bot):
    bot.add_cog(DosGame(bot))




