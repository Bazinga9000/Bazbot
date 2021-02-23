import pokerhe as p
import money as m
import random

from discord.ext import commands

class Player():

    def __init__(self,auth,game):
        self.name = auth.name
        self.id = auth.id
        self.game = game
        self.hand = []
        self.ishost = False

    def draw(self):
        return self.game.deck.pop()

    def discard(self,pos): #not used in 5-card-draw, possibly useful if i steal this code
        self.game.deck.insert(0,self.hand[pos])
        self.hand.remove(self.hand[pos])

    def swap(self,pos): #swap a card with a new card
        self.game.deck.insert(0,self.hand[pos])
        self.hand[pos] = self.draw()


    def formathand(self):
        return " ".join(self.hand)



class Poker():
    def __init__(self,ante):
        self.gametype = "Poker"
        self.started = False
        self.players = []
        self.aliveplayers = []
        self.deadplayers = []
        self.turn = 0
        self.phase = 0 #initial bet, discard, final bet
        self.bet = 0
        self.pot = 0
        self.ante = ante
        self.startingplayer = -1
        self.actions = 0
        self.playercount = 0
        self.callcount = 0

    def newdeck(self):
        ranks = "AKQJT98765432"
        suits = "♥♣♠♦"

        self.deck = []

        for r in ranks:
            for s in suits:
                self.deck.append(r+s)

        random.shuffle(self.deck)


    def newround(self,players):
        self.phase = 0
        self.aliveplayers = players
        self.calls = [False for i in self.aliveplayers]
        self.startingplayer = (self.startingplayer + 1) % len(self.aliveplayers)
        self.turn = self.startingplayer
        self.pot = 0
        self.bet = self.ante
        self.playercount = len(self.aliveplayers)
        for player in self.aliveplayers:
            m.add_amount(player.id,-self.ante)
            self.pot += self.ante

        self.newdeck()

        for player in players:
            player.hand = [player.draw() for i in range(5)]


    def status(self):
        if self.phase != 3:
            message = ""
            message += "There are `" + str(len(self.aliveplayers)) + "` players still in.\n"
            message += "We are currently in the " + ["Opening Bet","Discard","Second Bet"][self.phase] + " Phase.\n"
            message += "The Pot stands at `∰" + str(self.pot) + "`.\n"
            if self.phase != 1: message += "The Bet stands at `∰" + str(self.bet) + "`.\n"
            message += "It is " + self.aliveplayers[self.turn].name + "'s Turn to act."
        else:
            message = ""
            for i,player in enumerate(self.aliveplayers):
                if i == 0:
                    message += "**The Winner of the Hand**\n"
                    message += "`" + player.name + "` - " + p.name(p.convert(player.hand)) + " (`" + player.formathand() + "`)\n"
                    message += "*Losers*\n"
                else:
                    message += "`" + player.name + "` - " + p.name(p.convert(player.hand)) + " (`" + player.formathand() + "`)\n"


            for player in reversed(self.deadplayers):
                message += "`" + player.name + "` - " + p.name(p.convert(player.hand)) + " (`" + player.formathand() + "`)\n"

        return message


    def handlephase(self):
        self.bet = 0
        self.playercount = len(self.aliveplayers)
        self.actions = 0
        self.callcount = 0
        if self.phase == 3:
            self.endround()
            self.started = False

    def handlebet(self,amount):
        if amount == self.bet:
            self.callcount += 1
        else:
            self.callcount = 1

        m.add_amount(self.players[self.turn].id,-amount)
        self.pot += amount
        self.turn = (self.turn + 1) % len(self.aliveplayers)
        self.actions += 1
        self.bet = amount
        if self.callcount == self.playercount:
            self.phase += 1
            self.handlephase()


    def handlediscard(self,cards):
        player = self.aliveplayers[self.turn]
        if cards != "0":
            for card in set(cards):
                player.swap(int(card) - 1)

        self.turn = (self.turn + 1) % len(self.aliveplayers)
        self.actions += 1

        if self.actions == self.playercount:
            self.phase += 1
            self.handlephase()


    def handlefold(self):
        self.actions += 1
        self.deadplayers.append(self.aliveplayers[self.turn])
        self.aliveplayers.remove(self.aliveplayers[self.turn])
        del self.calls[self.turn]

        if len(self.aliveplayers) == 1:
            self.phase = 3
            self.endround()
            return

        self.turn = self.turn % len(self.aliveplayers)

        if self.actions == self.playercount:
            self.phase += 1
            self.handlephase()

    def endround(self):
        self.aliveplayers = sorted(self.aliveplayers, key=lambda x: p.convert(x.hand), reverse=True)
        copy = self.aliveplayers[:]
        max_hand = p.convert(self.aliveplayers[0].hand)

        for player in copy:
            if p.convert(player.hand) != max_hand:
                self.aliveplayers.remove(player)
                self.deadplayers.append(player)

        for player in self.aliveplayers:
            m.add_amount(player.id,self.pot//len(self.aliveplayers))




class PokerGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = []
        self.pdb = {}

    def getgame(self, ctx):
        return self.pdb[ctx.guild.id][ctx.author.id]

    def ingame(self, ctx):
        try:
            x = self.getgame(ctx)
            return True
        except:
            return False

    def getplayer(self, game, id):
        return game.players[[x.id for x in game.players].index(id)]

    @commands.guild_only()
    @commands.group(brief="Poker (5 Card Draw)")
    async def poker(self, ctx):
        try:
            x = self.pdb[ctx.guild.id]
        except:
            self.pdb[ctx.guild.id] = {}

        m.get_amount(ctx.author.id) #assure they have money

    @poker.command()
    async def create(self, ctx, *ante):

        if self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You're already in a game!")



        if len(ante) != 0:
            try:
                t = int(str(ante[0]))
            except:
                return await ctx.send("Uh oh! You friccin moron! `ante` isn't an int!")


        else:
            t = 10

        if t > (m.get_amount(ctx.author.id) // 10):
            return await ctx.send("Uh oh! You friccin moron! Your ante can't be more than 10% of your wealth!")

        if t < 1:
            return await ctx.send("Uh oh! You friccin moron! Your ante can't be less than one!")


        self.games.append(Poker(t))
        self.pdb[ctx.guild.id][ctx.author.id] = self.games[-1]
        self.games[-1].players.append(Player(ctx.author, self.games[-1]))
        self.games[-1].players[0].ishost = True
        await ctx.send("Game created with an ante of `∰" + str(t) + "`")

    @poker.command()
    async def join(self, ctx, user: str):
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
            game.players.append(Player(ctx.author, self.games[-1]))
            return await ctx.send("You have joined " + user + "'s Game!")

    @poker.command()
    async def leave(self, ctx):

        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]

        game.players = [x for x in game.players if x.id != ctx.author.id]
        self.pdb[ctx.guild.id].pop(ctx.author.id, None)

        if len(game.players) == 0:
            self.games.remove(game)
        else:
            game.players[0].ishost = True

            if game.started:
                game.turn = game.turn % len(game.players)

        await ctx.send("You have left your game!")

    @poker.command()
    async def start(self, ctx):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]
        player = self.getplayer(game, ctx.author.id)

        if len(game.players) < 2:
            return await ctx.send("Uh oh! You friccin moron! You can't start a game with only one player!")

        if not player.ishost:
            return await ctx.send("Uh oh! You friccin moron! You aren't the host!")

        game.started = True

        message = "```\n"

        aliveplayers = []
        for player in game.players:
            if m.get_amount(player.id) < game.ante:
                message += player.name + " can't pay the ante for this round, and will sit out."
            else:
                message += player.name + " paid the ante of ∰" + str(game.ante) + "."
                aliveplayers.append(player)

            message += "\n"

        message += "```"
        await ctx.send(message)
        game.newround(aliveplayers)
        for player in aliveplayers:
            await self.bot.get_user(player.id).send("**Your Hand**\n```\n" + player.formathand() + "\n```")

        await ctx.send(game.status())


    @poker.command(name="raise")
    async def _raise(self, ctx, amount : int):

        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]

        players = [i.id for i in game.players]
        aliveplayers = [i.id for i in game.aliveplayers]
        player = ctx.author.id

        if player not in aliveplayers:
            return await ctx.send("Uh oh! You friccin moron! You aren't in this hand!")

        turn = aliveplayers.index(player)

        if game.turn != turn:
            return await ctx.send("Uh oh! You friccin moron! It's not your turn!")

        if game.phase == 1:
            return await ctx.send("Uh oh! You friccin moron! You can't bet during the discard phase!")

        if amount <= game.bet:
            return await ctx.send("Uh oh! You friccin moron! You can't lower the bet!")

        if amount > m.get_amount(player):
            return await ctx.send("Uh oh! You fricicn moron! You can't meet that bet!")


        game.handlebet(amount)
        await ctx.send(game.status())

    @poker.command()
    async def call(self, ctx):

        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]

        players = [i.id for i in game.players]
        aliveplayers = [i.id for i in game.aliveplayers]
        player = ctx.author.id

        if player not in aliveplayers:
            return await ctx.send("Uh oh! You friccin moron! You aren't in this hand!")

        if game.phase == 1:
            return await ctx.send("Uh oh! You friccin moron! You can't bet during the discard phase!")

        turn = aliveplayers.index(player)

        if game.turn != turn:
            return await ctx.send("Uh oh! You friccin moron! It's not your turn!")


        if game.bet > m.get_amount(player):
            return await ctx.send("Uh oh! You fricicn moron! You can't meet that bet! You must either fold or go all in!")

        game.handlebet(game.bet)
        await ctx.send(game.status())

    @poker.command()
    async def fold(self, ctx):

        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]

        players = [i.id for i in game.players]
        aliveplayers = [i.id for i in game.aliveplayers]
        player = ctx.author.id

        if player not in aliveplayers:
            return await ctx.send("Uh oh! You friccin moron! You aren't in this hand!")

        turn = aliveplayers.index(player)
        if game.turn != turn:
            return await ctx.send("Uh oh! You friccin moron! It's not your turn!")

        if game.phase == 1:
            return await ctx.send("Uh oh! You friccin moron! You can't fold in the discard phase!")

        game.handlefold()
        await ctx.send(game.status())


    @poker.command()
    async def discard(self, ctx, cards : str):
        if not self.ingame(ctx):
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        game = self.pdb[ctx.guild.id][ctx.author.id]

        players = [i.id for i in game.players]
        aliveplayers = [i.id for i in game.aliveplayers]
        player = ctx.author.id


        if player not in aliveplayers:
            return await ctx.send("Uh oh! You friccin moron! You aren't in this hand!")

        turn = aliveplayers.index(player)
        if game.turn != turn:
            return await ctx.send("Uh oh! You friccin moron! It's not your turn!")


        if game.phase != 1:
            return await ctx.send("Uh oh! You friccin moron! You can't discard during a betting phase!")



        if cards != "0" and any(cards.count(str(i)) > 1 for i in range(1,6)):
            return await ctx.send("Uh oh! You friccin moron! That's an invalid discard string!"
                                  "`b9!discard 0` to discard nothing."
                                  "`b9!discard 1` to discard card #1"
                                  "`b9!discard 2` to discard card #2"
                                  "`b9!discard 123` to discard cards 1,2, and 3"
                                  "`b9!discard 12345` to discard everything.")
        else:
            game.handlediscard(cards)
            await self.bot.get_user(player).send("**Your Hand**\n```\n" + game.aliveplayers[turn].formathand() + "\n```")
            await ctx.send(game.status())


def setup(bot):
    bot.add_cog(PokerGame(bot))