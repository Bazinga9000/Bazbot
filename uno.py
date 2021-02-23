from discord.ext import commands
import random

class CardNotInHand(Exception):
    pass

class InvalidPlay(Exception):
    pass

class MalformedPlay(Exception):
    pass

class Player():
    def __init__(self,auth,game):
        self.name = auth.name
        self.id = auth.id
        self.game = game
        self.hand = []
        self.score = 0
        self.ishost = False

        self.hasdrawn = False

        self.cmap = {"RED" : "R", "GREEN" : "G", "YELLOW" : "Y", "BLUE" : "B",
                     "R" : "R", "G" : "G", "Y" : "Y", "B" : "B"}

    def draw(self,amount=1):
        for i in range(amount):
            try:
                self.hand.append(self.game.deck.pop())
            except:
                self.game.newdeck()
                self.hand.append(self.game.deck.pop())


    def gethand(self):
        return " ".join(sorted(self.hand,key = lambda x: x[::-1]))

    def play(self,card,args):

        card = card.upper()

        if len(card) == 1:
            card += " "

        if card not in self.hand:
            raise CardNotInHand

        rank = card[:-1]
        suit = card[-1]

        topcard = self.game.discardpile[-1]

        trank = topcard[:-1]

        if self.game.drawstack != 0 and rank not in ["T","F"]:
            raise InvalidPlay

        if suit != " " and (trank != rank and suit != self.game.color):
            if self.game.drawstack != 0 and rank in ["T","F"]:
                pass
            else:
                raise InvalidPlay

        if rank in ["W","F"]:
            if len(args) == 0:
                raise MalformedPlay

            if args[0].upper() not in self.cmap:
                raise MalformedPlay
            else:
                suit = self.cmap[args[0].upper()]

        self.game.discardpile.append(card)
        self.game.color = suit
        self.game.handlecard(card)
        self.hand.remove(card)
        self.game.turn = (self.game.turn + self.game.turndirection) % len(self.game.players)




class Uno():
    def __init__(self,threshold):
        self.gametype = "Uno"
        self.started = False

        self.players = []
        self.eliminated = []

        self.threshold = threshold


    def newdeck(self):
        ranks = ["0","1","2","3","4","5","6","7","8","9","1","2","3","4","5","6","7","8","9","T","T",
                 "S","S","R","R"]
        suits = ["R","G","B","Y"]

        self.deck = []

        for rank in ranks:
            for suit in suits:
                self.deck.append(rank + suit)

        self.deck.extend(["W ","W ","W ","W ","F ","F ","F ","F "])

        random.shuffle(self.deck)


    def initround(self):
        self.discardpile = []

        self.color = ""

        self.turn = 0
        self.turndirection = 1
        self.drawstack = 0

        self.newdeck()

        for player in self.players:
            player.hand = []
            player.draw(7)

        self.discardpile.append(self.deck.pop())
        self.color = self.discardpile[-1][-1]

        while self.discardpile[-1][-1] == " ":
            self.discardpile.append(self.deck.pop())
            self.color = self.discardpile[-1][-1]

    def getdeck(self):
        return " ".join(reversed(self.deck))

    def getdp(self):
        return " ".join(reversed(self.discardpile))

    def value(self,card):
        if card[0].isdigit():
            return int(card[0])
        elif len(card) == 0: #wild, draw 4
            return 50
        else:
            return 20

    def handlecard(self,card):
        if card.startswith("S"):
            self.turn = (self.turn + self.turndirection) % len(self.players)
        elif card.startswith("R"):
            self.turndirection *= -1
        elif card.startswith("T"):
            self.drawstack += 2
        elif card.startswith("F"):
            self.drawstack += 4


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


class UnoGame(commands.Cog):
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
        return game.players[[x.name for x in game.players].index(id)]

    @commands.guild_only()
    @commands.group(brief="Uno (the card game)")
    async def uno(self,ctx):
        try:
            x = self.pdb[ctx.guild.id]
        except:
            self.pdb[ctx.guild.id] = {}


    @uno.command()
    async def create(self,ctx,*threshold):

        if self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You're already in a game!")

        if len(threshold) != 0:
            try:
                t = int(threshold[0])
            except:
                return await ctx.send("Uh oh! You friccin moron! `threshold` isn't an int!")
        else:
            t = 500



        self.games.append(Uno(t))
        self.pdb[ctx.guild.id][ctx.author.id] = self.games[-1]
        self.games[-1].players.append(Player(ctx.author,self.games[-1]))
        self.games[-1].players[0].ishost = True
        await ctx.send("Game created with elimination threshold `" + str(t) + "`!")

    @uno.command()
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

    @uno.command()
    async def leave(self,ctx):

        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]

        game.players = [x for x in game.players if x.id != ctx.author.id]
        self.pdb[ctx.guild.id].pop(ctx.author.id,None)

        if len(game.players) == 0:
            self.games.remove(game)
        else:
            self.games[-1].players[0].ishost = True

        await ctx.send("You have left your game!")

    @uno.command()
    async def start(self,ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]
        player = self.getplayer(game,ctx.author.name)

        if not player.ishost:
            return await ctx.send("Uh oh! You friccin moron! You aren't the host!")

        game.started = True

        game.initround()

        for player in game.players:
            author = self.bot.get_user(player.id)
            await author.send("**Your Hand**\n```\n" + player.gethand() + "\n```")


        await ctx.send("**Discard Pile**\n```\n" + game.getdp() + "\n```\n**Current Color: " + game.color + "**")
        await ctx.send("It is now **" + game.players[game.turn].name + "'s** Turn!")

    def turnmessage(self,game):
        message = "**Discard Pile**\n```\n" + game.getdp() + "\n```\n**Current Color: " + game.color + "**"
        message += "\n"
        message += "It is now **" + game.players[game.turn].name + "'s** Turn!"
        if game.drawstack != 0: 
            message += "\n***THERE ARE " + str(game.drawstack) + " CARDS TO BE DRAWN***"
            
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
            message = message + "​" + player.name + ": " + str(player.score) + "\n"

        message += "--ELIMINATED--\n"

        for c, player in enumerate(game.eliminated):
            rank = len(game.players) + c + 1
            message = message + "- " + player.name + " - " + str(rank) + self.place(rank) + \
                      " (Final Score: " + str(player.score) + ")"

        message += "```"
        
        return message
        
    @uno.command()
    async def scores(self,ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]

        
        await ctx.send(self.scoremessage(game))

    @uno.command()
    async def play(self,ctx, card, *args):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]
        player = self.getplayer(game,ctx.author.name)

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

        player.hasdrawn = False

        if len(player.hand) == 0:
            game.updatescores()
            await ctx.send("**The Round has Concluded! The current scores are: **\n" + self.scoremessage(game))

            if len(game.players) != 1:
                game.initround()
                await ctx.send(self.turnmessage(game))
            else:
                await ctx.send("**The game has concluded! " + game.players[0].name + " is the winner!**")
                for player in game.players:
                    self.pdb[ctx.guild.id].pop(player.id, None)
                    self.games.remove(game)
        else:
            await ctx.send(self.turnmessage(game))


    @uno.command()
    async def info(self,ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]
        await ctx.send(self.turnmessage(game))

    @uno.command()
    async def draw(self,ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]
        player = self.getplayer(game,ctx.author.name)

        if game.players.index(player) != game.turn:
            return await ctx.send("Uh oh! You friccin moron! It's not your turn!")

        if game.drawstack != 0:
            player.draw(game.drawstack)
            game.drawstack = 0
            game.turn = (game.turn + game.turndirection) % len(game.players)
            await ctx.send(self.turnmessage(game))
        else:
            player.draw(1)
            player.hasdrawn = True
            await ctx.send("Card Drawn! If you still can't play anything, you can either draw again or pass your turn with `b9!uno pass`")

    @uno.command(name="pass")
    async def _pass(self,ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]
        player = self.getplayer(game,ctx.author.name)

        if game.players.index(player) != game.turn:
            return await ctx.send("Uh oh! You friccin moron! It's not your turn!")

        if game.drawstack != 0:
            return await ctx.send("Uh oh! You friccin moron! You can't pass with cards to draw!")

        if not player.hasdrawn:
            return await ctx.send("Uh oh! You friccin moron! You haven't drawn yet!")

        player.hasdrawn = False
        game.turn = (game.turn + game.turndirection) % len(game.players)

        await ctx.send(self.turnmessage(game))



    @uno.command()
    async def hand(self,ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]
        player = self.getplayer(game,ctx.author.name)

        await ctx.author.send("**Your Hand**\n```\n" + player.gethand() + "\n```")
        await ctx.send(":mailbox:")

    @uno.command()
    async def handsizes(self,ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]

        message = "```\n"

        for player in game.players:
            message = message + player.name + " has " + str(len(player.hand)) + " cards in hand.\n"

        message += "```"
        await ctx.send(message)

    @uno.command()
    async def help(self,ctx):
        message = "In order to play a card, type `b9!uno play <card>`. If the card is a wild card, you also have to specify the color.\n"
        message += "For example: `b9!uno play W red` plays a wild card and sets the color to red.\n"
        message += "A Card is specified by two characters, the first of which being the type of card, and the second being the color.\n"
        message += "For example: `4G` is a Green 4, and `RR` is a Red Reverse.\n"
        message += "The card symbols are as follows:\n"
        message += "0-9: The Number Cards\n"
        message += "T: Draw Two\n"
        message += "S: Skip\n"
        message += "R: Reverse\n"
        message += "W: Wild Card\n"
        message += "F: Wild Draw Four"

        await ctx.send(message)

    #commands that will be deleted when testing is complete
    '''
    @uno.command()
    async def drawseven(self,ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]
        player = self.getplayer(game,ctx.author.name)

        player.draw(7)
        await ctx.send("**Drawn 7 Cards.**")

    @uno.command()
    async def scry(self,ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]
        await ctx.send("**The Deck**\n```\n" + game.getdeck() + "\n```")
    '''

def setup(bot):
    bot.add_cog(UnoGame(bot))




