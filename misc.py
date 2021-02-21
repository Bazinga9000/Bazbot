import discord
from discord.ext import commands
from sympy import *
import numpy
import hashlib
import math
import dice
import glob
import asyncio
import random
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import warnings
import itertools
import time
import datetime
import io
from io import TextIOWrapper, BytesIO
import pickle
import re
import ipa_to_onyanthu as onyan
import regex
import hsluv
import inspect
import os
import collections

warnings.simplefilter('error', Image.DecompressionBombWarning)

x, t, z, nu = symbols('x t z nu')
e = math.e
pi = math.pi


with open("standopowa.txt","r") as f:
    stand_abilities = f.read().splitlines()


compressalphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!\"#$%&'()*+,-./:;<=>?@[]^_" \
                   "`{|}~¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö" \
                   "÷øùúûüýþÿĀāĂăĄąĆćĈĉĊċČčĎďĐđĒēĔĕĖėĘęĚěĜĝĞğĠġĢģĤĥĦħĨĩĪīĬĭĮįİıĲĳĴĵĶķĸĹĺĻļĽľĿŀŁł" \
                   "ŃńŅņŇňŉŊŋŌōŎŏŐőŒœŔŕŖŗŘřŚśŜŝŞşŠšŢţŤťŦŧŨũŪūŬŭŮůŰűŲųŴŵŶŷŸŹźŻżŽžſƀƁƂƃƄƅƆƇƈƉƊƋƌƍ" \
                   "ƎƏƐƑƒƓƔƕƖƗƘƙƚƛƜƝƞƟƠơƢƣƤƥƦƧƨƩƪƫƬƭƮƯưƱƲƳƴƵƶƷƸƹƺƻƼƽƾƿǀǁǂǃǄǅǆǇǈǉǊǋǌǍǎǏǐǑǒǓǔǕǖǗ" \
                   "ǘǙǚǛǜǝǞǟǠǡǢǣǤǥǦǧǨǩǪǫǬǭǮǯǰǱǲǳǴǵǶǷǸǹǺǻǼǽǾǿȀȁȂȃȄȅȆȇȈȉȊȋȌȍȎȏȐȑȒȓȔȕȖȗȘșȚțȜȝȞȟȠȡ" \
                   "ȢȣȤȥȦȧȨȩȪȫȬȭȮȯȰȱȲȳȴȵȶȷȸȹȺȻȼȽȾȿɀɁɂɃɄɅɆɇɈɉɊɋɌɍɎɏɐɑɒɓɔɕɖɗɘəɚɛɜɝɞɟɠɡɢɣɤɥɦɧɨɩɪɫɬ" \
                   "ɭɮɯɰɱɲɳɴɵɶɷɸɹɺɻɼɽɾɿʀʁʂʃʄʅʆʇʈʉʊʋʌʍʎʏʐʑʒʓʔʕʖʗʘʙʚʛͰͱͲͳʹ͵Ͷͷͺͻͼͽ;Ϳ΄΅Ά·ΈΉΊΌΎΏΐΑΒ" \
                   "ΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩΪΫάέήίΰαβγδεζηθικλμνξοπρςστυφχψωϊϋόύώϏϐϑϒϓϔϕϖϗϘϙϚϛϜϝ" \
                   "ϞϟϠϡϢϣϤϥϦϧϨϩϪϫϬϭϮϯϰϱϲϳϴϵ϶ϷϸϹϺϻϼϽϾϿЀЁЂЃЄЅІЇЈЉЊЋЌЍЎЏАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧ" \
                   "ШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюяѐёђѓєѕіїјљњћќѝўџѠѡѢѣѤѥѦѧѨѩѪѫѬѭѮѯѰѱ" \
                   "ѲѳѴѵѶѷѸѹѺѻѼѽѾѿҀҁ҂ҊҋҌҍҎҏҐґҒғҔҕҖҗҘҙҚқҜҝҞҟҠҡҢңҤҥҦҧҨҩҪҫҬҭҮүҰұҲҳҴҵҶҷҸҹҺһҼҽҾҿӀӁӂ" \
                   "ӃӄӅӆӇӈӉӊӋӌӍӎӏӐӑӒӓӔӕӖӗӘәӚӛӜӝӞӟӠӡӢӣӤӥӦӧӨөӪӫӬӭӮӯӰӱӲӳӴӵӶӷӸӹӺӻӼӽӾӿԀԁԂԃԄԅԆԇԈԉԊԋԌ" \
                   "ԍԎԏԐԑԒԓԔԕԖԗԘԙԚԛԜԝԞԟԠԡԢԣԤԥԦԧԨ"


wordinit = compressalphabet[340:680]
wordterm = compressalphabet[:340]
spaceterm = compressalphabet[680:1020]

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ratel = lambda x: int(hashlib.sha256(x.lower().encode('utf-8')).hexdigest(),16) % 101
        self.ts = {}

        ###givetake
        try:
            with open("givetake.pkl","rb") as f:
                p = pickle.load(f)
                self.givetakescore = p[0]
                self.givetakeleaderboard = p[1]

        except:
            self.givetakescore = 0
            self.givetakeleaderboard = {}


        ###battle
        #top
        try:
            with open("battle.pkl","rb") as f:
                p = pickle.load(f)
                self.battle_global_best = p[0]
                self.battle_individual_leaderboard = p[1]
                self.battle_server_leaderboard = p[2]

        except:
            self.battle_global_best = (0,137001076284063744,382927393045741568)
            self.battle_individual_leaderboard = {}
            self.battle_server_leaderboard = {}

        #bottom
        try:
            with open("battle.pkl","rb") as f:
                p = pickle.load(f)
                self.battle_global_worst = p[3]
                self.battle_individual_leaderboard_worst = p[4]
                self.battle_server_leaderboard_worst = p[5]

        except:
            self.battle_global_worst = (0,137001076284063744,382927393045741568)
            self.battle_individual_leaderboard_worst = {}
            self.battle_server_leaderboard_worst = {}


        #mines
        self.mines_rule_presets = {
            "normal": "1", "knight": "/01", "no-up": "10111111", "no_vert": "1011", "no_horiz": "1110", "orth": "01",
            "far-orth": "01/0010", "swath": "1/1", "doubled": "12", "taxicab": "12/0010", "horiz": "00001",
            "pawn": "22200000/001000000000000", "2-squares": "/1", "shifted-orth": "00010100/000000101",
            "queen": "12/10", "blind-down": "11110001", "precise": "12345678", "precise2": "12345678/9ABCDEFGHIJKLMNO",
            "shifted-normal": "00010100/0000011111", "zebra": "//0100", "giraffe": "///00010100",
            "antelope": "///010000", "gnu": "/01/001010", "bison": "//011011", "swath3": "1/1/1", "hill": "3/2/1",
            "3-squares": "//1", "4-squares": "///1", "swath4": "1/1/1/1", "5-squares": "////1", "swath5": "1/1/1/1/1"

        }


        #mastermind
        self.mm_games = {}


    def crop(self, im, new_width, new_height):
        width, height = im.size   # Get dimensions
        left = (width - new_width)/2
        top = (height - new_height)/2
        right = (width + new_width)/2
        bottom = (height + new_height)/2


        return im.crop((left, top, right, bottom))


    @commands.command(brief="Coolguy-ify an image")
    @commands.cooldown(1,10,type=commands.BucketType.user)
    async def coolguy(self, ctx, *id):
        if len(id) == 0:
            try:
                url = ctx.message.attachments[0].url
            except:
                return await ctx.send("Uh oh! You friccin moron! You need either an image or a url!")
        else:
            url = id[0]
            try:
                url = ctx.message.mentions[0].avatar_url
                if url == "": url = ctx.messages.mentions[0].default_avatar_url
            except:
                try:
                    user = self.bot.get_user(int(id[0]))
                    url = user.avatar_url
                    if url == "": url = user.default_avatar_url
                except:
                    url = id[0]

        url = url.replace(".webp",".png").replace(".webm",".png")

        urll = url.lower()
        if ".png" not in urll and ".jpg" not in urll and ".gif" not in urll:
            return await ctx.send("Uh oh! You friccin moron! That's not an image!")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                response = await resp.read()

        try:
            image = Image.open(BytesIO(response))
        except Image.DecompressionBombWarning:
            return await ctx.send("Uh oh! You friccin moron! That image is too big! Try a smaller one.")
        except:
            return await ctx.send("Uh oh! You friccin moron! That's not an image!")

        s = image.size

        ratio = max(s[0], s[1]) / min(s[0], s[1])

        if s[0] > s[1]:
            ns = [int(411 * ratio), 411]
        else:
            ns = [411, int(411 * ratio)]

        image = image.resize(ns, Image.BILINEAR)
        image = self.crop(image, 411, 411)

        if image.size != [411,411]:
            image = image.resize((411,411), Image.BILINEAR)

        out = Image.new("RGBA", [411, 411], (0, 0, 0, 0))

        coolguy = Image.open("cmdimages/coolguy.png").convert("RGBA")
        anticoolguy = Image.open("cmdimages/anticoolguy.png").convert("RGBA")

        out.paste(image, (0, 0), anticoolguy)
        out.paste(coolguy, (0, 0), coolguy)
        out.save("output.png")

        await ctx.send(file=discord.File(open("output.png", mode="rb")))

    @commands.command(brief="*ゴゴゴゴゴゴゴ*")
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    async def menacing(self, ctx, *id):
        if len(id) == 0:
            url = ctx.message.attachments[0].url
        else:
            url = id[0]
            try:
                url = ctx.message.mentions[0].avatar_url
                if url == "": url = ctx.messages.mentions[0].default_avatar_url
            except:
                try:
                    user = self.bot.get_user(int(id[0]))
                    url = user.avatar_url
                    if url == "": url = user.default_avatar_url
                except:
                    url = id[0]

        url = url.replace(".webp", ".png").replace(".webm", ".png")
        urll = url.lower()

        if ".png" not in urll and ".jpg" not in urll and ".gif" not in urll:
            return await ctx.send("Uh oh! You friccin moron! That's not an image!")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                response = await resp.read()

        try:
            image = Image.open(BytesIO(response))
        except Image.DecompressionBombWarning:
            return await ctx.send("Uh oh! You friccin moron! That image is too big! Try a smaller one.")
        except:
            return await ctx.send("Uh oh! You friccin moron! That's not an image!")

        s = image.size

        ratio = s[1] / s[0]

        if abs(ratio - 1) < 0.1:
            menacing = Image.open("cmdimages/menacing/square.png").convert("RGBA")
        elif ratio > 1:
            menacing = Image.open("cmdimages/menacing/tall.png").convert("RGBA")
        elif ratio < 1:
            menacing = Image.open("cmdimages/menacing/wide.png").convert("RGBA")

        menacing = menacing.resize((s[0],s[1]))



        '''
        if s[0] > s[1]:
            ns = [int(411 * ratio), 411]
        else:
            ns = [411, int(411 * ratio)]

        image = image.resize(ns, Image.BILINEAR)
        image = self.crop(image, 411, 411)

        if image.size != [411, 411]:
            image = image.resize((411, 411), Image.BILINEAR)
        '''

        out = Image.new("RGBA", [s[0],s[1]], (0, 0, 0, 0))


        out.paste(image, (0, 0))
        out.paste(menacing, (0, 0), menacing)
        out.save("output.png")

        await ctx.send(file=discord.File(open("output.png", mode="rb")))

    @commands.command(brief="Sends you a DM")
    async def dm(self,ctx, *, content):
        await ctx.author.send(content)

    @commands.command(brief="Magic 8-ball",name="8ball")
    async def ball(self,ctx, *, query):
        answers = ["It is certain","It is decidedly so","Without a doubt","Yes Definitely",
                   "You may rely on it","As I see it, yes","Most likely","Outlook good","Yes",
                   "Signs point to yes","Reply hazy try again","Ask again later","Better not tell you now",
                   "Cannot predict now","Concentrate and ask again","Don't count on it","My Reply is no",
                   "My sources say no","Outlook not so good","Very doubtful"]

        await ctx.send("**" + query + "**\n" + random.choice(answers))

    @commands.command(brief="View the source code!")
    async def code(self, ctx, *, command: str=None):
        source_url = 'https://github.com/Bazinga9000/Bazbot/'
        if command is None:
            return await ctx.send(f"**View Bazbot's source code here**\n{source_url}")

        obj = self.bot.get_command(command.replace('.', ' '))
        if obj is None:
            return await ctx.send('Could not find command.')

        # since we found the command we're looking for, presumably anyway, let's
        # try to access the code itself
        src = obj.callback.__code__
        lines, firstlineno = inspect.getsourcelines(src)
        if not obj.callback.__module__.startswith('discord'):
            # not a built-in command
            location = os.path.relpath(src.co_filename).replace('\\', '/')
            source_url = f'{source_url}tree/master'
        else:
            location = obj.callback.__module__.replace('.', '/') + '.py'
            source_url = 'https://github.com/Rapptz/discord.py/blob/rewrite'

        final_url = f'<{source_url}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>'
        await ctx.send(final_url)

    @commands.command(brief="Sends images",name="i")
    async def image(self, ctx, name : str):

        if name == "list":
            images = glob.glob("./images/*.png")
            await ctx.send("```\n" + " ".join(images).replace("./images\\","").replace(".png","") + "\n```")
        try:
            filename = "./images/" + name + ".png"
            await ctx.send(file=discord.File(open(filename, mode="rb")))
        except:
            try:
                filename = "./secretimages/" + name + ".png"
                await ctx.send(file=discord.File(open(filename, mode="rb")))
            except:
                return


    @commands.command(brief="Lists the servers Bazbot is in.")
    async def servers(self, ctx):
        guilds = self.bot.guilds
        await ctx.send("```" + "\nNumber of servers: "+str(len(list(guilds)))+
                       "\n"+"\n".join(["     "+x.name for x in guilds]).replace("```", "\\`\\`\\`") + "\n```")


    @commands.command(brief="Grades a person or object on the Glorious Rating Scale.")
    async def scales(self, ctx, *, entity: str):
        if entity.lower() in ["bazbot","bazbot9000","bazbot 9000","bazbot_9000","<@382925349144494080>"]:
            score = 4
        elif entity.lower() in ["baz","bazinga","bazinga9000","bazinga 9000","bazinga_9000","my creator","<@137001076284063744>"]:
            score = 4
        else:
            score = min(5,self.ratel(entity)//20)

        await ctx.send("**" + entity + "**",file=discord.File(open("./cmdimages/scales/" + str(score) + ".png",mode="rb")))

    @commands.command(brief="Rates a person or object")
    async def rate(self, ctx, *, entity : str):
        if entity.lower() in ["bazbot", "bazbot9000", "bazbot 9000", "bazbot_9000", "<@382925349144494080>"]:
            await ctx.send("I'm perfect and you know it.")
        elif entity.lower() in ["baz", "bazinga", "bazinga9000", "bazinga 9000", "bazinga_9000", "my creator",
                                "<@137001076284063744>"]:
            await ctx.send("I give my creator a **████/100**")
        elif entity.lower() in ["netneutrality","net neutrality"]:
            await ctx.send("I give Net Neutrality an **∞/100**\nCall your representatives my dudes.\nhttps://www.battleforthenet.com/")
        elif entity.lower() in ["ajitpai","pai","ajit pai"]:
            await ctx.send("I give FCC Chair Infamous “Cuckold Is Kinda Ok” Reese’s Mug Carrying Pussy With Legs Ajit Pai a **-∞/10**\n"
                           + "Call your representatives my dudes.\nhttps://www.battleforthenet.com/")
        else:
            score = self.ratel(entity)
            await ctx.send("I give " + entity + " a score of **" + str(score) + "/100**")


    def total(self,result):
        try:
            return sum(result)
        except:
            return result


    @commands.command(brief="Rolls some dice!",aliases=["die","dice"])
    async def roll(self,ctx,*,die : str):

        diestring = die.replace("--list","")

        try:
            result = dice.roll(diestring)
            result_max = dice.roll_max(diestring)
            result_min = dice.roll_min(diestring)
        except dice.ParseException:
            return await ctx.send("Uh oh! You friccin moron! That's not a valid formula!")
        except dice.TooManyDice:
            return await ctx.send("Uh oh! You friccin moron! That's too many dice!")


        message = "<@" + str(ctx.author.id) + ">, Your `" + diestring + "` yielded "

        if self.total(result) == self.total(result_max) and "w" not in diestring and "x" not in diestring:
            message += "**a perfect " + str(self.total(result)) + "**!"
        elif self.total(result) == self.total(result_min):
            message += "*a critical fail of " + str(self.total(result_min)) + ".*"
        else:
            message += str(self.total(result))


        if "--list" in die:
            message += " `" + str(result) + "`"

        await ctx.send(message)


    @commands.command(brief="Send a test missile alert.")
    async def missiletest(self,ctx):
        if random.randint(1,100) == 100:
            await ctx.send("Test missile alert sent!")
            await ctx.author.send("We good.")
        else:
            await ctx.send("Missile alert sent!")
            await ctx.author.send("BALLISTIC MISSILE THREAT INBOUND TO HAWAII. SEEK IMMEDIATE SHELTER. THIS IS NOT A DRILL.")
            await asyncio.sleep(38)
            await ctx.author.send("There is no missile threat or danger to the State of Hawaii. Repeat. False Alarm.")


    @commands.command(brief="Summon me to your servers")
    async def summon(self,ctx):
        await ctx.send("**Invite me to your discord servers by using the following link**\nhttps://discordapp.com/oauth2/authorize?&client_id=382925349144494080&scope=bot&permissions=0")


    @commands.command(brief="Randomly decide a binary outcome.",aliases=["yn"])
    @commands.cooldown(1,5,type=commands.BucketType.user)
    async def yesorno(self,ctx,*,question):
        mode = "mp4"

        if "--gif" in question:
            mode = "gif"
            question = question.replace("--gif","")

        images = ["./images/yes." + mode,
                  "./images/no." + mode,
                  "./images/maybe.mp4"]

        links = ["https://cdn.discordapp.com/attachments/191692762016382976/398267417027149826/images_yes.gif",
                 "https://cdn.discordapp.com/attachments/191692762016382976/398268253048143872/images_no.gif",
                 "maybe"]

        filenames = ["yes","no","hmmm"]

        file = random.randint(0,1)
        if random.randint(0,50) == 0: file = 2

        await ctx.send(question,file=discord.File(open(images[file],mode="rb"),filename=filenames[file] + "." + mode)) #For those with good upload speed
        #await ctx.send("**" + question + "**\n" + links[file]) For those with bad upload speed


    #everything regarding the help command was made by bottersnike and hanss
    def format_args(self, cmd):
        params = list(cmd.clean_params.items())
        p_str = ''
        for p in params:
            if p[1].default == p[1].empty:
                p_str += ' <{}>'.format(p[0])
            else:
                p_str += ' [{}]'.format(p[0])

        return p_str

    def format_commands(self, prefix, cmd, name=None):
        cmd_args = self.format_args(cmd)
        if not name: name = cmd.name
        name = name.replace('  ', ' ')
        d = '`{}{}{}`\n'.format(prefix,name,cmd_args)

        if type(cmd) == commands.core.Group:
            cmds = sorted(list(cmd.commands), key=lambda x: x.name)
            for subcmd in cmds:
                d += self.format_commands(prefix, subcmd, name='{} {}'.format(name,subcmd.name))

        return d

    def get_help(self, ctx, cmd, name=None):
        d = 'Help for command `{}`:\n'.format(cmd.name)
        d += '\n**Usage:**\n'

        d += self.format_commands(ctx.prefix, cmd, name=name)

        d += '\n**Description:**\n'
        d += '{}\n'.format('None' if cmd.brief is None else cmd.brief.strip())

        if cmd.checks:
            d += '\n**Checks:**'
            for check in cmd.checks:
                d += '\n{}'.format(check.__qualname__.split('.')[0])
            d += '\n'

        if cmd.aliases:
            d += '\n**Aliases:**'
            for alias in cmd.aliases:
                d += '\n`{}{}`'.format(ctx.prefix,alias)

            d += '\n'

        return d

    @commands.command()
    async def help(self, ctx, *args):
        '''This help message'''
        if len(args) == 0:
            cats = [cog for cog in self.bot.cogs]
            cats.sort()
            width = max([len(cat) for cat in cats]) + 2
            d = '**Categories:**\n'
            for cat in zip(cats[0::2], cats[1::2]):
                d += '**`{}`**{}**`{}`**\n'.format(cat[0], ' ' * int(2.3 * (width - len(cat[0]))), cat[1])
            if len(cats) % 2 == 1:
                d += '**`{}`**\n'.format(cats[-1])

            d += '\nUse `{0}help <category>` to list commands in a category.\n'.format(ctx.prefix)
            d += 'Use `{0}help <command>` to get in depth help for a command.\n'.format(ctx.prefix)

        elif len(args) == 1:
            cats = {cog.lower(): cog for cog in self.bot.cogs}
            if args[0].lower() in cats:
                cog_name = cats[args[0].lower()]
                d = 'Commands in category **`{}`**:\n'.format(cog_name)
                cmds = self.bot.get_cog(cog_name).get_commands()
                for cmd in sorted(list(cmds), key=lambda x: x.name):
                    d += '\n  `{}{}`'.format(ctx.prefix, cmd.name)

                    brief = cmd.brief
                    if brief is None and cmd.help is not None:
                        brief = cmd.help.split('\n')[0]

                    if brief is not None:
                        d += ' - {}'.format(brief)
                d += '\n'
            else:
                if args[0] not in ctx.bot.all_commands:
                    d = 'Command not found.'
                else:
                    cmd = ctx.bot.all_commands[args[0]]
                    d = self.get_help(ctx, cmd)
        else:
            d = ''
            cmd = ctx.bot
            cmd_name = ''
            for i in args:
                i = i.replace('@', '@\u200b')
                if cmd == ctx.bot and i in cmd.all_commands:
                    cmd = cmd.all_commands[i]
                    cmd_name += cmd.name + ' '
                elif type(cmd) == commands.Group and i in cmd.all_commands:
                    cmd = cmd.all_commands[i]
                    cmd_name += cmd.name + ' '
                else:
                    if cmd == ctx.bot:
                        d += 'Command not found.'
                    else:
                        d += 'No sub-command found.'.format(cmd.name, i)
                    break

            else:
                d = self.get_help(ctx, cmd, name=cmd_name)

        # d += '\n*Made by Bottersnike#3605 and hanss314#0128*'
        return await ctx.send(d)


    @commands.guild_only()
    @commands.command(brief="The World! Stop time!")
    async def theworld(self,ctx):
        try:
            x = self.ts[ctx.guild.id]
        except:
            self.ts[ctx.guild.id] = False



        if self.ts[ctx.guild.id]:
            return await ctx.send("Time is already stopped...")

        perms = [x for x in iter(ctx.channel.permissions_for(ctx.guild.me))]

        if not (perms[1][1] or perms[11][1]):
            return await ctx.send("I am not powerful enough to use this ability...")

        roles = []

        valid = ["mod","admin","owner","staff","dio","administrator","moderator"]

        for role in ctx.author.roles:
            if role.name == "@everyone":
                everyone = role


            roles.append(role.name.lower())

        if not any(x in valid for x in roles) and ctx.author != ctx.guild.owner:
            return await ctx.send("You are not powerful enough to use this ability...")

        self.ts[ctx.guild.id] = True

        ch = ctx.channel

        ov = ch.overwrites



        await ctx.send("***The World! Stop Time!***")
        await ctx.channel.set_permissions(self.bot.user, send_messages=True)
        await ctx.channel.set_permissions(ctx.author,send_messages=True)

        if ov == []:
            await ctx.channel.set_permissions(everyone,send_messages=False)


        for h in ov:
            if isinstance(h,discord.Role):
                await ctx.channel.set_permissions(h, send_messages=False)
            else:
                if h != self.bot.user: await ctx.channel.set_permissions(h,send_messages=False)


        await asyncio.sleep(5)

        await ctx.channel.set_permissions(ctx.author,overwrite=None)
        await ctx.channel.set_permissions(self.bot.user, overwrite=None)

        if ov == []:
            await ctx.channel.set_permissions(everyone, send_messages=True)

        for h in ov:
            await ctx.channel.set_permissions(h,overwrite=ov[h])


        await ctx.send("*Time has resumed.*")

        self.ts[ctx.guild.id] = False

    @commands.command(brief="Fixes the space time continuum in case something bad happens. **(DO NOT USE TO STOP TIME IN STOPPED TIME)**")
    async def crazydiamond(self,ctx):
        valid = ["mod", "admin", "owner", "staff", "josuke", "administrator", "moderator"]
        roles = []
        for role in ctx.author.roles:
            roles.append(role.name.lower())

        if not any(x in valid for x in roles) and ctx.author != ctx.guild.owner:
            return await ctx.send("You are not powerful enough to use this ability...")

        self.ts[ctx.guild.id] = False
        await ctx.send("The Space-Time Continuum has been repaired.\n*Disclaimer*\nDo not use this command to stop time within stopped time. It will end badly.")

    def subset(self,small,big):
        for item in small:
            if small.count(item) > big.count(item): return False

        return True

    @commands.command(brief="Spin the wheel of random digits and see if you get something cool.")
    @commands.cooldown(1,3,type=commands.BucketType.user)
    async def idpoker(self,ctx, *id):
        id = " ".join(id)
        if id == "message":
            handtype = "Message"
            sid = str(ctx.message.id)
        elif id == "user":
            handtype = "User"
            sid = str(ctx.author.id)
        else:
            try:
                handtype = "Provided"
                int(id)
                sid = str(id)
            except:
                handtype = "Random"
                sid = "".join([str(random.randint(0,9)) for i in range(18)])


        kinds = [len(list(g)) for k, g in itertools.groupby(sid)]
        kinds = [i for i in kinds if i != 1]
        kinds = tuple(sorted(kinds))


        names = {
            (): "High Card",
            (2,): "Pair",
            (2, 2): "Wide Pair",
            (2, 2, 2): "Tall Pair",
            (3,): "House",
            (2, 3): "Full House",
            (2, 2, 3): "Wide House",
            (2, 2, 2, 2): "Long Pair",
            (4,): "Dragon",
            (2, 2, 2, 3): "Tall House",
            (2, 4): "Full Dragon",
            (3, 3): "Mansion",
            (2, 2, 2, 2, 2): "Deep Pair",
            (2, 3, 3): "Full Mansion",
            (2, 2, 4): "Wide Dragon",
            (2, 2, 2, 2, 3): "Long House",
            (2, 2, 3, 3): "Wide Mansion",
            (5,): "Bronze",
            (3, 4): "Dragon House",
            (2, 2, 2, 4): "Tall Dragon",
            (2, 5): "Full Bronze",
            (2, 3, 4): "Full Dragon House",
            (2, 2, 2, 2, 2, 2): "Rare Pair",
            (2, 2, 5): "Wide Bronze",
            (2, 2, 2, 3, 3): "Tall Mansion",
            (2, 2, 3, 4): "Wide Dragon House",
            (3, 3, 3): "Villa",
            (2, 2, 2, 2, 2, 3): "Deep House",
            (2, 2, 2, 2, 4): "Long Dragon",
            (6,): "Silver",
            (3, 5): "Bronze House",
            (2, 6): "Full Silver",
            (2, 3, 3, 3): "Full Villa",
            (2, 2, 2, 5): "Tall Bronze",
            (2, 3, 5): "Full Bronze House",
            (4, 4): "Hydra",
            (3, 3, 4): "Dragon Mansion",
            (2, 4, 4): "Full Hydra",
            (2, 2, 6): "Wide Silver",
            (2, 2, 2, 3, 4): "Tall Dragon House",
            (2, 2, 2, 2, 2, 2, 2): "Great Pair",
            (2, 2, 2, 2, 3, 3): "Long Mansion",
            (2, 2, 3, 3, 3): "Wide Villa",
            (2, 3, 3, 4): "Full Dragon Mansion",
            (2, 2, 3, 5): "Wide Bronze House",
            (7,): "Gold",
            (3, 6): "Silver House",
            (4, 5): "Bronze Dragon",
            (2, 2, 2, 2, 5): "Long Bronze",
            (2, 2, 2, 2, 2, 4): "Deep Dragon",
            (2, 2, 4, 4): "Wide Hydra",
            (2, 7): "Full Gold",
            (2, 2, 2, 2, 2, 2, 3): "Rare House",
            (2, 2, 2, 6): "Tall Silver",
            (2, 4, 5): "Full Bronze Dragon",
            (2, 3, 6): "Full Silver House",
            (3, 3, 5): "Bronze Mansion",
            (3, 4, 4): "Hydra House",
            (2, 2, 3, 3, 4): "Wide Dragon Mansion",
            (2, 2, 7): "Wide Gold",
            (3, 3, 3, 3): "Castle",
            (2, 2, 2, 3, 5): "Tall Bronze House",
            (2, 2, 2, 2, 3, 4): "Long Dragon House",
            (2, 2, 2, 3, 3, 3): "Tall Villa",
            (8,): "Platinum",
            (2, 3, 3, 5): "Full Bronze Mansion",
            (2, 3, 4, 4): "Full Hydra House",
            (2, 2, 4, 5): "Wide Bronze Dragon",
            (2, 2, 3, 6): "Wide Silver House",
            (2, 2, 2, 4, 4): "Tall Hydra",
            (4, 6): "Silver Dragon",
            (3, 7): "Gold House",
            (2, 8): "Full Platinum",
            (2, 2, 2, 2, 2, 3, 3): "Deep Mansion",
            (2, 3, 3, 3, 3): "Full Castle",
            (2, 2, 2, 2, 6): "Long Silver",
            (5, 5): "Comet",
            (2, 2, 2, 2, 2, 2, 2, 2): "Rad Pair",
            (3, 4, 5): "Bronze Dragon House",
            (2, 2, 2, 2, 2, 5): "Deep Bronze",
            (3, 3, 3, 4): "Dragon Villa",
            (2, 4, 6): "Full Silver Dragon",
            (2, 2, 2, 7): "Tall Gold",
            (2, 3, 7): "Full Gold House",
            (3, 3, 6): "Silver Mansion",
            (2, 5, 5): "Full Comet",
            (2, 2, 2, 2, 2, 2, 4): "Rare Dragon",
            (2, 2, 8): "Wide Platinum",
            (2, 2, 3, 3, 5): "Wide Bronze Mansion",
            (2, 2, 3, 4, 4): "Wide Hydra House",
            (2, 2, 2, 3, 3, 4): "Tall Dragon Mansion",
            (2, 3, 4, 5): "Full Bronze Dragon House",
            (9,): "Diamond",
            (2, 2, 2, 4, 5): "Tall Bronze Dragon",
            (2, 2, 2, 3, 6): "Tall Silver House",
            (2, 3, 3, 3, 4): "Full Dragon Villa",
            (4, 4, 4): "Basilisk",
            (4, 7): "Gold Dragon",
            (3, 8): "Platinum House",
            (5, 6): "Onyx",
            (2, 2, 2, 2, 2, 2, 2, 3): "Great House",
            (2, 2, 2, 2, 3, 5): "Long Bronze House",
            (2, 3, 3, 6): "Full Silver Mansion",
            (2, 2, 4, 6): "Wide Silver Dragon",
            (2, 2, 3, 7): "Wide Gold House",
            (2, 9): "Full Diamond",
            (2, 2, 3, 3, 3, 3): "Wide Castle",
            (3, 3, 4, 4): "Hydra Mansion",
            (2, 2, 5, 5): "Wide Comet",
            (2, 2, 2, 2, 4, 4): "Long Hydra",
            (3, 4, 6): "Silver Dragon House",
            (2, 4, 7): "Full Gold Dragon",
            (2, 5, 6): "Full Onyx",
            (2, 3, 8): "Full Platinum House",
            (2, 2, 2, 2, 2, 3, 4): "Deep Dragon House",
            (3, 3, 3, 5): "Bronze Villa",
            (2, 2, 2, 2, 3, 3, 3): "Long Villa",
            (2, 2, 2, 2, 7): "Long Gold",
            (2, 4, 4, 4): "Full Basilisk",
            (2, 2, 2, 8): "Tall Platinum",
            (3, 5, 5): "Comet House",
            (3, 3, 7): "Gold Mansion",
            (2, 2, 2, 2, 2, 6): "Deep Silver",
            (4, 4, 5): "Bronze Hydra",
            (2, 2, 9): "Wide Diamond",
            (2, 2, 3, 4, 5): "Wide Bronze Dragon House",
            (10,): "Luna",
            (2, 3, 4, 6): "Full Silver Dragon House",
            (4, 8): "Platinum Dragon",
            (5, 7): "Topaz",
            (2, 2, 2, 2, 2, 2, 5): "Rare Bronze",
            (3, 9): "Diamond House",
            (3, 3, 3, 3, 3): "Fortress",
            (2, 2, 3, 3, 6): "Wide Silver Mansion",
            (2, 3, 3, 4, 4): "Full Hydra Mansion",
            (2, 10): "Full Luna",
            (2, 3, 3, 3, 5): "Full Bronze Villa",
            (2, 2, 3, 3, 3, 4): "Wide Dragon Villa",
            (3, 3, 4, 5): "Bronze Dragon Mansion",
            (2, 2, 2, 3, 7): "Tall Gold House",
            (2, 2, 2, 3, 3, 5): "Tall Bronze Mansion",
            (2, 3, 3, 7): "Full Gold Mansion",
            (2, 2, 4, 7): "Wide Gold Dragon",
            (2, 3, 5, 5): "Full Comet House",
            (2, 2, 5, 6): "Wide Onyx",
            (2, 2, 2, 4, 6): "Tall Silver Dragon",
            (2, 4, 4, 5): "Full Bronze Hydra",
            (2, 2, 2, 3, 4, 4): "Tall Hydra House",
            (2, 2, 3, 8): "Wide Platinum House",
            (6, 6): "Sin",
            (2, 2, 2, 2, 2, 2, 3, 3): "Rare Mansion",
            (3, 5, 6): "Onyx House",
            (2, 2, 2, 2, 3, 6): "Long Silver House",
            (2, 2, 2, 5, 5): "Tall Comet",
            (3, 4, 7): "Gold Dragon House",
            (2, 2, 4, 4, 4): "Wide Basilisk",
            (2, 4, 8): "Full Platinum Dragon",
            (2, 5, 7): "Full Topaz",
            (2, 2, 2, 2, 4, 5): "Long Bronze Dragon",
            (2, 3, 9): "Full Diamond House",
            (3, 4, 4, 4): "Basilisk House",
            (3, 3, 3, 6): "Silver Villa",
            (2, 2, 2, 9): "Tall Diamond",
            (2, 2, 2, 2, 2, 2, 2, 2, 2): "Fab Pair",
            (4, 4, 6): "Silver Hydra",
            (3, 3, 8): "Platinum Mansion",
            (2, 2, 2, 2, 8): "Long Platinum",
            (4, 5, 5): "Comet Dragon",
            (3, 3, 3, 3, 4): "Dragon Castle",
            (2, 6, 6): "Full Sin",
            (2, 2, 2, 2, 3, 3, 4): "Long Dragon Mansion",
            (2, 2, 10): "Wide Luna",
            (11,): "Terra",
            (2, 2, 2, 2, 2, 2, 2, 4): "Great Dragon",
            (2, 2, 2, 2, 2, 7): "Deep Gold",
            (5, 8): "Ruby",
            (4, 9): "Diamond Dragon",
            (3, 10): "Luna House",
            (2, 3, 3, 3, 3, 3): "Full Fortress",
            (6, 7): "Citrine",
            (2, 2, 2, 2, 2, 3, 5): "Deep Bronze House",
            (2, 11): "Full Terra",
            (2, 2, 2, 3, 3, 3, 3): "Tall Castle",
            (2, 3, 3, 4, 5): "Full Bronze Dragon Mansion",
            (2, 3, 4, 7): "Full Gold Dragon House",
            (2, 2, 3, 4, 6): "Wide Silver Dragon House",
            (2, 3, 5, 6): "Full Onyx House",
            (2, 2, 2, 2, 2, 4, 4): "Deep Hydra",
            (2, 2, 3, 3, 7): "Wide Gold Mansion",
            (2, 4, 4, 6): "Full Silver Hydra",
            (2, 2, 3, 5, 5): "Wide Comet House",
            (2, 2, 5, 7): "Wide Topaz",
            (2, 3, 3, 8): "Full Platinum Mansion",
            (2, 2, 4, 8): "Wide Platinum Dragon",
            (2, 2, 4, 4, 5): "Wide Bronze Hydra",
            (2, 4, 5, 5): "Full Comet Dragon",
            (3, 3, 4, 6): "Silver Dragon Mansion",
            (3, 4, 4, 5): "Bronze Hydra House",
            (2, 2, 3, 9): "Wide Diamond House",
            (3, 5, 7): "Topaz House",
            (2, 2, 2, 5, 6): "Tall Onyx",
            (2, 3, 4, 4, 4): "Full Basilisk House",
            (2, 2, 2, 3, 8): "Tall Platinum House",
            (3, 4, 8): "Platinum Dragon House",
            (2, 2, 2, 4, 7): "Tall Gold Dragon",
            (2, 5, 8): "Full Ruby",
            (4, 5, 6): "Onyx Dragon",
            (2, 4, 9): "Full Diamond Dragon",
            (2, 3, 3, 3, 6): "Full Silver Villa",
            (2, 6, 7): "Full Citrine",
            (2, 2, 2, 3, 4, 5): "Tall Bronze Dragon House",
            (2, 3, 10): "Full Luna House",
            (3, 3, 5, 5): "Comet Mansion",
            (2, 2, 6, 6): "Wide Sin",
            (2, 2, 3, 3, 4, 4): "Wide Hydra Mansion",
            (12,): "Sol",
            (2, 2, 2, 2, 2, 2, 6): "Rare Silver",
            (3, 6, 6): "Sin House",
            (4, 4, 7): "Gold Hydra",
            (3, 3, 9): "Diamond Mansion",
            (3, 3, 3, 7): "Gold Villa",
            (2, 2, 2, 3, 3, 6): "Tall Silver Mansion",
            (2, 2, 2, 10): "Tall Luna",
            (3, 3, 3, 4, 4): "Hydra Villa",
            (2, 2, 3, 3, 3, 5): "Wide Bronze Villa",
            (2, 2, 11): "Wide Terra",
            (2, 2, 2, 2, 9): "Long Diamond",
            (5, 9): "Amber",
            (4, 10): "Luna Dragon",
            (2, 3, 3, 3, 3, 4): "Full Dragon Castle",
            (3, 3, 3, 3, 5): "Bronze Castle",
            (2, 2, 2, 2, 3, 7): "Long Gold House",
            (6, 8): "Quartz",
            (3, 11): "Terra House",
            (2, 12): "Full Sol",
            (2, 2, 2, 2, 4, 6): "Long Silver Dragon",
            (5, 5, 5): "Meteor",
            (2, 2, 2, 4, 4, 4): "Tall Basilisk",
            (2, 2, 2, 2, 5, 5): "Long Comet",
            (4, 4, 4, 4): "Leviathan",
            (7, 7): "Opposition",
            (2, 3, 4, 8): "Full Platinum Dragon House",
            (2, 4, 5, 6): "Full Onyx Dragon",
            (2, 3, 5, 7): "Full Topaz House",
            (13,): "Galaxy",
            (2, 2, 2, 2, 2, 8): "Deep Platinum",
            (2, 4, 4, 7): "Full Gold Hydra",
            (2, 2, 5, 8): "Wide Ruby",
            (2, 3, 6, 6): "Full Sin House",
            (2, 2, 6, 7): "Wide Citrine",
            (3, 5, 8): "Ruby House",
            (2, 3, 4, 4, 5): "Full Bronze Hydra House",
            (2, 3, 3, 9): "Full Diamond Mansion",
            (3, 4, 4, 6): "Silver Hydra House",
            (2, 2, 4, 9): "Wide Diamond Dragon",
            (3, 6, 7): "Citrine House",
            (3, 4, 9): "Diamond Dragon House",
            (2, 5, 9): "Full Amber",
            (2, 2, 3, 10): "Wide Luna House",
            (2, 4, 10): "Full Luna Dragon",
            (2, 2, 3, 5, 6): "Wide Onyx House",
            (4, 5, 7): "Topaz Dragon",
            (3, 4, 5, 5): "Comet Dragon House",
            (2, 3, 3, 4, 6): "Full Silver Dragon Mansion",
            (3, 3, 5, 6): "Onyx Mansion",
            (2, 2, 3, 4, 7): "Wide Gold Dragon House",
            (2, 6, 8): "Full Quartz",
            (3, 3, 4, 7): "Gold Dragon Mansion",
            (2, 3, 11): "Full Terra House",
            (3, 3, 10): "Luna Mansion",
            (4, 6, 6): "Sin Dragon",
            (2, 2, 3, 3, 8): "Wide Platinum Mansion",
            (2, 2, 4, 5, 5): "Wide Comet Dragon",
            (2, 7, 7): "Full Opposition",
            (4, 4, 8): "Platinum Hydra",
            (2, 3, 3, 5, 5): "Full Comet Mansion",
            (2, 2, 12): "Wide Sol",
            (5, 5, 6): "Silver Comet",
            (2, 2, 4, 4, 6): "Wide Silver Hydra",
            (2, 5, 5, 5): "Full Meteor",
            (2, 2, 2, 11): "Tall Terra",
            (5, 10): "Bronze Luna",
            (4, 11): "Terra Dragon",
            (3, 3, 3, 4, 5): "Bronze Dragon Villa",
            (2, 3, 3, 3, 7): "Full Gold Villa",
            (2, 2, 2, 3, 9): "Tall Diamond House",
            (3, 3, 3, 8): "Platinum Villa",
            (6, 9): "Sapphire",
            (3, 12): "Sol House",
            (2, 2, 2, 5, 7): "Tall Topaz",
            (4, 4, 4, 5): "Bronze Basilisk",
            (7, 8): "Zircon",
            (2, 13): "Full Galaxy",
            (2, 2, 2, 4, 8): "Tall Platinum Dragon",
            (3, 3, 3, 3, 3, 3): "Palace",
            (3, 3, 4, 4, 4): "Basilisk Mansion",
            (2, 2, 2, 6, 6): "Tall Sin",
            (2, 4, 4, 4, 4): "Full Leviathan",
            (2, 2, 2, 2, 10): "Long Luna",
            (14,): "Heaven",
            (3, 3, 3, 3, 6): "Silver Castle",
            (2, 5, 10): "Full Bronze Luna",
            (2, 4, 11): "Full Terra Dragon",
            (3, 4, 5, 6): "Onyx Dragon House",
            (2, 3, 6, 7): "Full Citrine House",
            (2, 3, 4, 9): "Full Diamond Dragon House",
            (3, 6, 8): "Quartz House",
            (3, 5, 9): "Amber House",
            (2, 6, 9): "Full Sapphire",
            (4, 6, 7): "Citrine Dragon",
            (3, 4, 10): "Luna Dragon House",
            (2, 3, 12): "Full Sol House",
            (2, 4, 5, 7): "Full Topaz Dragon",
            (4, 5, 8): "Ruby Dragon",
            (2, 7, 8): "Full Zircon",
            (2, 3, 5, 8): "Full Ruby House",
            (2, 5, 5, 6): "Full Silver Comet",
            (3, 3, 5, 7): "Topaz Mansion",
            (3, 3, 4, 8): "Platinum Dragon Mansion",
            (2, 3, 3, 10): "Full Luna Mansion",
            (2, 2, 3, 11): "Wide Terra House",
            (5, 5, 7): "Gold Comet",
            (3, 7, 7): "Opposition House",
            (3, 3, 11): "Terra Mansion",
            (2, 2, 13): "Wide Galaxy",
            (6, 10): "Silver Luna",
            (5, 11): "Bronze Terra",
            (4, 12): "Sol Dragon",
            (3, 13): "Galaxy House",
            (2, 2, 5, 9): "Wide Amber",
            (4, 4, 9): "Diamond Hydra",
            (7, 9): "Opal",
            (2, 4, 6, 6): "Full Sin Dragon",
            (5, 6, 6): "Sin Bronze",
            (3, 4, 4, 7): "Gold Hydra House",
            (2, 4, 4, 8): "Full Platinum Hydra",
            (2, 2, 6, 8): "Wide Quartz",
            (2, 2, 4, 10): "Wide Luna Dragon",
            (2, 14): "Full Heaven",
            (4, 4, 5, 5): "Comet Hydra",
            (2, 2, 7, 7): "Wide Opposition",
            (8, 8): "Duality",
            (3, 3, 6, 6): "Sin Mansion",
            (3, 5, 5, 5): "Meteor House",
            (4, 4, 4, 6): "Silver Basilisk",
            (2, 2, 2, 12): "Tall Sol",
            (15,): "Cosmos",
            (3, 3, 3, 9): "Diamond Villa",
            (5, 6, 7): "Podium",
            (4, 6, 8): "Quartz Dragon",
            (3, 7, 8): "Zircon House",
            (3, 5, 10): "Bronze Luna House",
            (2, 6, 10): "Full Silver Luna",
            (3, 4, 11): "Terra Dragon House",
            (2, 5, 11): "Full Bronze Terra",
            (2, 4, 12): "Full Sol Dragon",
            (2, 3, 13): "Full Galaxy House",
            (7, 10): "Gold Luna",
            (6, 11): "Silver Terra",
            (5, 12): "Bronze Sol",
            (4, 13): "Galaxy Dragon",
            (3, 14): "Heaven House",
            (2, 15): "Full Cosmos",
            (4, 5, 9): "Amber Dragon",
            (3, 6, 9): "Sapphire House",
            (2, 7, 9): "Full Opal",
            (8, 9): "Pearl",
            (4, 7, 7): "Opposition Dragon",
            (5, 5, 8): "Platinum Comet",
            (2, 8, 8): "Full Duality",
            (4, 4, 10): "Luna Hydra",
            (3, 3, 12): "Sol Mansion",
            (2, 2, 14): "Wide Heaven",
            (16,): "Dimension",
            (6, 6, 6): "Devil",
            (8, 10): "Platinum Luna",
            (7, 11): "Gold Terra",
            (6, 12): "Silver Sol",
            (5, 13): "Bronze Galaxy",
            (4, 14): "Heaven Dragon",
            (3, 15): "Cosmos House",
            (2, 16): "Full Dimension",
            (17,): "Ascendant",
            (9, 9): "Yin-Yang",
            (18,): "Zenith",
        }

        ranks = [names[i] for i in names] #too lazy to do it twice

        hand = names[kinds]

        rank = ranks.index(hand)

        if hand == "High Card": kinds = [1]

        await ctx.send(ctx.author.name + ", Your " + handtype + " Hand is: `" + sid +
                       "`\n" + "Your hand is valued at `" + hand + "`" +
                       "\nHand Signature: `" + " ".join([str(i) for i in kinds]) + "`" +
                       "\nHand Rank: `" + str(len(ranks)-rank) + "`")


    @commands.command(brief="Get the nanosecond.")
    async def nanosecond(self,ctx):
        t = str(time.time_ns()%(10**9))
        await ctx.send("The current nanosecond is " + t)

    @commands.cooldown(1,2,type=commands.BucketType.user)
    @commands.command(aliases=["arrow"],brief="Use the power of The Arrow to generate a stand with a given name.")
    async def stand(self,ctx,*,name):
        power = random.choice("ABCDE")
        speed = random.choice("ABCDE")
        srange = random.choice("ABCDE")
        durab = random.choice("ABCDE")
        preci = random.choice("ABCDE")
        poten = random.choice("ABCDE")


        map = lambda x: "EDCBA".index(x)


        '''
        url = "http://allow-any-origin.appspot.com/http://powerlisting.wikia.com/wiki/Special:Random"


        html = urllib.request.urlopen(url)
        htmls = [i.decode() for i in html.readlines()]
        html.close()


        htmls = "".join(htmls)
        abilityv = htmls.index("<title>")
        ability = htmls[abilityv+7:].split("|")[0][:-1]

        #ability = "be patient"
        '''
        '''
        driver = webdriver.PhantomJS()
        driver.get("http://powerlisting.wikia.com/wiki/Special:Random")
        ability = driver.title.split("|")[0][:-1]
        src = driver.page_source
        desc = src[src.index("Capabilities") + 39:].split("</p>")[0][3:]
        '''

        ability = random.choice(stand_abilities)

        stand_score = sum(map(i) for i in (power,speed,srange,durab,preci,poten))

        color = 0xff0000
        if stand_score > 6: color = 0xff9900
        if stand_score > 12: color = 0xffff00
        if stand_score > 17: color = 0x00ff00
        if stand_score > 20: color = 0x0000ff
        if stand_score == 24: color = 0xff00ff

        '''
        ans = ""
        ans += "```\n"
        ans += "Stand Name: " + name + "\n"
        ans += "\n"
        ans += "Power: " + power + "\n"
        ans += "Speed: " + speed + "\n"
        ans += "Durability: " + durab + "\n"
        ans += "Precision: " + preci + "\n"
        ans += "Potential: " + poten + "\n"
        ans += "\n"
        ans += "Ability: " + ability + "\n"
        #ans += "Description: " + desc + "\n"
        ans += "```"
        '''
        embed = discord.Embed(title="Stand Name: " + name, color=color)
        embed.add_field(name="Power", value=power, inline=True)
        embed.add_field(name="Speed", value=speed, inline=True)
        embed.add_field(name="Range", value=srange, inline=True)
        embed.add_field(name="Durability", value=durab, inline=True)
        embed.add_field(name="Precision", value=preci, inline=True)
        embed.add_field(name="Potential", value=poten, inline=True)
        embed.add_field(name="Ability", value=ability, inline=True)
        ans = "**Description** http://powerlisting.wikia.com/wiki/" + ability.replace(" ","_")
        await ctx.send(ans,embed=embed)

    @commands.command(brief="See if you were saved or snapped by Thanos.")
    async def thanos(self,ctx):
        if ctx.author.id % 10 in [8,7,6,5,1]:
            return await ctx.send("You were saved by Thanos.")
        else:
            return await ctx.send("You were snapped by Thanos.")

    @commands.command(brief="View the givetake stats")
    async def gtstats(self, ctx, page=1):
        try:
            self.givetakeleaderboard[ctx.author.id]
        except:
            self.givetakeleaderboard[ctx.author.id] = 0

        leaderboard = self.givetakeleaderboard.items()

        try:
            p = int(page)
            if p < 1 or p > 1+len(leaderboard)//10:
                return await ctx.send("Uh oh! You friccin moron! That's an invalid Page!")
        except:
            return await ctx.send("Uh oh! You friccin moron! That's an invalid Page!")


        message = '**The Pot: {}**\n'.format(self.givetakescore)

        leaderboard = sorted(leaderboard,key=lambda x: x[1],reverse=True)
        your_rank = 1 + [i[0] for i in leaderboard].index(ctx.author.id)
        message += "Your Rank: #{} (Score of {})\n".format(your_rank, self.givetakeleaderboard[ctx.author.id])
        message += "Top 10:\n```"
        for q in range(10*(p-1), min(10*(p),len(leaderboard))):
            i = leaderboard[q]
            message += "#{}, {} - {}\n".format(q+1, self.bot.get_user(i[0]), i[1])

        message += "```"
        await ctx.send(message)

    @commands.check(lambda ctx: ctx.channel.id == 381950042770243584)
    @commands.cooldown(1,300,type=commands.BucketType.user)
    @commands.command(brief="A game of give and take",aliases=["gt"])
    async def givetake(self, ctx, option):
        try:
            self.givetakeleaderboard[ctx.author.id]
        except:
            self.givetakeleaderboard[ctx.author.id] = 0

        if option.lower() not in ["give","take"]:
            emsg = '''Uh oh! You friccin moron! The only valid options are `give` and `take`!
            `give` - Add 1 point to the Pot
            `take` - Add the entire pot to your score and reset the pot'''
            return await ctx.send(emsg)

        if option.lower() == "give":
            potdelta = 1 + numpy.random.binomial(self.givetakescore, 0.1)
            self.givetakescore += potdelta
            if potdelta == 1:
                await ctx.send("You have given the pot a point! It currently stands at {}!".format(self.givetakescore))
            else:
                await ctx.send("You have given the pot {} points! It currently stands at {}!".format(potdelta,self.givetakescore))

        elif option.lower() == "take":
            self.givetakeleaderboard[ctx.author.id] += self.givetakescore
            await ctx.send("You have taken the Pot for yourself! {} Points have been added to your score, which is now {}".format(self.givetakescore,self.givetakeleaderboard[ctx.author.id]))
            self.givetakescore = 0


        with open("givetake.pkl","wb") as f:
            pickle.dump((self.givetakescore,self.givetakeleaderboard),f)


    @commands.command(aliases=["onyan"],brief="Convert IPA text into Onyanthu's orthography.")
    async def onyanthu(self, ctx, *, ipa):
        stripped = ipa
        stripped.replace("/","")

        for i in onyan.character_translations:
            stripped = stripped.replace(i, onyan.character_translations[i])


        image = onyan.render(stripped)

        file = io.BytesIO()
        image.save(file, format="PNG")
        file.seek(0)

        return await ctx.send(file=discord.File(file, filename="onyanthu.png"))

    @commands.command(brief="Convert the current time into Onyanthu Base36-Time")
    async def otime(self, ctx, *, clocktime):
        emojis = "<:onyan0:510866552543903764> <:onyan1:510866552107827221> <:onyan2:510866552195776562> <:onyan3:510866552250302464> <:onyan4:510866552199970832> <:onyan5:510866552015421461> <:onyan6:510866555849015318> <:onyan7:510866552271142954> <:onyan8:510866552074010625> <:onyan9:510866552300503050> <:onyan10:510866552174804995> <:onyan11:510866552086593537> <:onyan12:510866552393039874> <:onyan13:510866552254365696> <:onyan14:510866552346640397> <:onyan15:510866551868489729> <:onyan16:510866552263016449> <:onyan17:510866551986061344> <:onyan18:510866552476794880> <:onyan19:510866552283987989> <:onyan20:510866552019746858> <:onyan21:510866551935598593> <:onyan22:510866552321605643> <:onyan23:510866552489508874> <:onyan24:510866552166285363> <:onyan25:510866552300503079> <:onyan26:510866552300634132> <:onyan27:510866552300765184> <:onyan28:510866552380456960> <:onyan29:510866552136925186> <:onyan30:510866552250433538> <:onyan31:510866552506023947> <:onyan32:510866552329863179> <:onyan33:510866552417943563> <:onyan34:510866552581652520> <:onyan35:510866552069947413>"
        emojis = emojis.split(" ")

        units = regex.match(r"([0-9:.h]*) ?([ap]?)m?",clocktime.lower())

        ctime = units[1].replace(".",":").replace("h",":").split(":")
        period = units[2]

        hours = (12 if period == "p" else 0) + int(ctime[0])
        minutes = int(ctime[1])

        seconds = int(ctime[2]) if len(ctime) >= 3 else 0

        if hours > 24 or minutes > 59 or seconds > 59:
            return await ctx.send("Uh oh! You friccin moron! That's an invalid time!")


        totalseconds = seconds + 60*minutes + 3600*hours

        onyanseconds = round(totalseconds * (46656/86400))
        oseconds = onyanseconds
        digits = []
        while onyanseconds != 0:
            digits.append(onyanseconds % 36)
            onyanseconds //= 36

        digits = digits[::-1]

        dstring = ":".join(str(i//6) + str(i%6) for i in digits)
        flag = clocktime[-1]

        if flag == "o":
            dstring = "".join(emojis[i] for i in digits)
        if flag == "d":
            dstring = ":".join(str(i) for i in digits)

        await ctx.send("The time is " + dstring)
        #await ctx.send([clocktime,units.group(1,2),period,hours,minutes,seconds,totalseconds,onyanseconds])

    def rule_to_ncf(self,rule):
        rings = rule.split("/")
        ring_size = lambda n: ((2*n)+1)**2 - ((2*n)-1)**2
        neighbors = []

        for n,ring in enumerate(rings):
            if ring == "": continue

            step = lambda: (position[0] + delta[0], position[1] + delta[1])
            outside = lambda x: abs(x[0]) > n+1 or abs(x[1]) > n+1

            value = lambda x: list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ").index(x)

            position = ((n+1),(n+1))
            delta = (0,-1)
            for i in range(ring_size(n+1)):
                v = value(ring[i%len(ring)])
                if v != 0:
                    neighbors.append((position,v))
                if outside(step()):
                    delta = (delta[1], -delta[0])
                position = step()

        return neighbors






    @commands.group("mines", brief="Create a minesweeper game in spoilers", invoke_without_command="true")
    @commands.cooldown(1,10,type=commands.BucketType.user)
    async def mines(self,ctx,height : int,width : int,mines : int, rule="normal", topology="square"):
        if mines > width*height:
            return await ctx.send("Uh oh! You friccin moron! That's too many mines!")

        if width > 80 or height > 30 or (width*height) > 400:
            return await ctx.send("Uh oh! You friccin moron! That's too big!")

        if width < 0 or height < 0 or mines < 0:
            return await ctx.send("Uh oh! You friccin moron! That's nonsensical!")

        r = rule if rule not in self.mines_rule_presets else self.mines_rule_presets[rule]

        if len(rule.split("/")) > 7:
            return await ctx.send("Uh oh! You friccin moron! Rules can have no more than 7 rings!")

        try:
            neighbor_list = self.rule_to_ncf(r)
        except:
            return await ctx.send("Uh oh! You friccin moron! That's an invalid rule!")

        aliases = {
            "cylinder" : "cyl",
            "projective" : "proj",
        }

        if topology in aliases: topology = aliases[topology]

        valid_topologies = ["square","torus","cyl","mobius","klein","proj","brick"]

        if topology not in valid_topologies:
            return await ctx.send("Uh oh! That's not a valid topology! The valid geometries are `{}`".format(", ".join(valid_topologies)))

        vertical_reflect = lambda x: set(((-i[0][0],i[0][1]),i[1]) for i in x)
        horizontal_reflect = lambda x: set(((i[0][0],-i[0][1]),i[1]) for i in x)

        if topology in ["mobius","klein","proj"] and set(neighbor_list) != vertical_reflect(neighbor_list):
            return await ctx.send("Uh oh! You friccin moron! Your rule isn't compatible with `{}` topology, as it does not have vertical symmetry.".format(topology))

        if topology == "proj" and set(neighbor_list) != horizontal_reflect(neighbor_list):
            return await ctx.send("Uh oh! You friccin moron! Your rule isn't compatible with `{}` topology, as it does not have horizontal symmetry.".format(topology))


        points = [(i,j) for i in range(height) for j in range(width)]
        random.shuffle(points)
        points = points[:mines]

        values = ['<:0_:671452548254793729>', '<:1_:671452547650945069>', '<:2_:671452547705208851>',
                  '<:3_:671452547717791744>', '<:4_:671452547717922848>', '<:5_:671452547776643082>',
                  '<:6_:671452547671916551>', '<:7_:671452547751477308>', '<:8_:671452547625517067>',
                  '<:9_:671452547570991125>', '<:10:671452547659333648>', '<:11:671452547801677884>',
                  '<:12:671452547461939211>', '<:13:671452547881631775>', '<:14:671452547965517827>',
                  '<:15:671452547881500692>', '<:16:671452547885695048>', '<:17:671452547680043069>',
                  '<:18:671452547596419083>', '<:19:671452547978100809>', '<:20:671452547935895602>',
                  '<:21:671452548393336836>', '<:22:671452548150067232>', '<:23:671452548452057160>',
                  '<:24:671452548602920971>', '<:25:671452552109359149>', '<:26:671452548615634946>',
                  '<:27:671452548460314634>', '<:28:671452548611309630>', '<:29:671452548670029824>',
                  '<:30:671452549282267143>', '<:31:671452548502388797>', '<:32:671452548657446953>',
                  '<:33:671452548250468353>', '<:34:671452548632281093>', '<:35:671452548657446932>',
                  '<:36:671452548250599445>', '<:37:671452548611178567>', '<:38:671452548439212073>',
                  '<:39:671452548682612749>', '<:40:671452548409983000>', '<:41:671452548775018517>',
                  '<:42:671452548854448178>', '<:43:671452548577624085>', '<:44:671452548816830468>',
                  '<:45:671452548686938115>', '<:46:671452548624023573>', '<:47:671452548837933056>',
                  '<:48:671452548946984980>', '<:49:671452548942659595>', '<:50:671452987293564939>',
                  '<:51:671452987415068687>', '<:52:671452987381645363>', '<:53:671452987478114314>',
                  '<:54:671452987461206049>', '<:55:671452986978861059>', '<:56:671452987628978176>',
                  '<:57:671452987205353563>', '<:58:671452986991443979>', '<:59:671452987280850952>',
                  '<:60:671452987213742081>', '<:61:671452987196964921>', '<:62:671452987196964870>',
                  '<:63:671452986836385853>', '<:64:671452987188576261>', '<:65:671452987193032725>',
                  '<:66:671452986849099803>', '<:67:671452987142438935>', '<:68:671452987146764325>',
                  '<:69:671452987100758047>', '<:70:671452987197227024>', '<:71:671452987255947274>',
                  '<:72:671452986735722537>', '<:73:671452986983186483>', '<:74:671452987205615644>',
                  '<:75:671452987297759251>', '<:76:671452987205615654>', '<:77:671452987914453060>',
                  '<:78:671452987188707368>', '<:79:671452987096563752>', '<:80:671452987180449847>',
                  '<:81:671452987448754177>', '<:82:671452986861682774>', '<:83:671452986849099784>',
                  '<:84:671452987243364373>', '<:85:671452986572275713>', '<:86:671452986740047898>',
                  '<:87:671452987184381952>', '<:88:671452986836385825>', '<:89:671452987666726952>',
                  '<:90:671452986307772476>', '<:91:671452986819608586>', '<:92:671452986660093958>',
                  '<:93:671452986907820074>', '<:94:671452986844905519>', '<:95:671452986643447818>',
                  '<:96:671452986433601537>', '<:97:671452986354172005>', '<:98:671452987100758036>',
                  '<:99:671452986639253525>']

        string = "Minesweeper: {}×{}, {} :bomb:, Rule `{}`, Topology `{}`\n".format(height,width,mines,rule, topology)

        def neighbors(r,c):
            n = []

            for p in neighbor_list:
                nr = r + p[0][0]
                nc = c + p[0][1]
                if 0 <= nr < height and 0 <= nc < width:
                    n.append([(nr,nc), p[1]])
                elif topology == "torus":
                    n.append([(nr % height, nc % width), p[1]])
                elif topology == "cyl":
                    if 0 <= nr < height:
                        n.append([(nr, nc % width), p[1]])
                elif topology == "mobius":
                    if 0 <= nr < height:
                        tr = nr%height if (nc // width) % 2 == 0 else height - 1 - (nr%height)
                        tc = nc % width
                        n.append([(tr,tc), p[1]])
                elif topology == "klein":
                    tr = nr % height if (nc // width) % 2 == 0 else height - 1 - (nr % height)
                    tc = nc % width
                    n.append([(tr, tc), p[1]])
                elif topology == "proj":
                    tr = nr % height if (nc // width) % 2 == 0 else height - 1 - (nr % height)
                    tc = nc % width if (nr // height) % 2 == 0 else width - 1 - (nc % width)
                    n.append([(tr, tc), p[1]])

                elif topology == "brick":
                    offset = (width//2) * (nr//height)
                    n.append([(nr % height, (nc - offset)%width), p[1]])
                #add shit for non-planar geomet here

            return n

        zeroes = []
        '''
        counts = []
        for i in range(height):
            c = []
            for j in range(width):
                if (i,j) in points:
                    c.append(-1)
                else:
                    count = 0
                    n = neighbors(i,j)
                    for p in n:
                        if p[0] in points:
                            count += p[1]
                    if count > 99:
                        return await ctx.send("Uh oh! You friccin moron! Your rule caused a square to detect more than 99 mines! Baz will eventually add a fallback for this, but not yet.")

                    if count == 0:
                        zeroes.append((i,j))
                    c.append(count)
            counts.append(c)
        '''
        counts = [[0 for i in range(width)] for j in range(height)]

        for p in points:
            counts[p[0]][p[1]] = -9999999
            for n in neighbors(*p):
                counts[n[0][0]][n[0][1]] += n[1]

        for i in range(height):
            for j in range(width):
                if counts[i][j] == 0:
                    zeroes.append((i,j))


        visibles = []
        try:
            to_sample = [random.choice(zeroes)]
        except:
            to_sample = []


        while len(to_sample) != 0:
            s = to_sample.pop()
            visibles.append(s)

            for n in neighbors(s[0],s[1]):
                if 0 <= n[0][0] < height and 0 <= n[0][1] < width:
                    if counts[n[0][0]][n[0][1]] == 0:
                        if n[0] not in visibles:
                            to_sample.append(n[0])
                    else:
                        visibles.append(n[0])

        for i in range(height):
            for j in range(width):
                x = counts[i][j]
                if x > 99:
                    return await ctx.send("Uh oh! You friccin moron! Your rule caused a square to detect more than 99 mines!")
                if x < 0:
                    string += "||<:bomb:671480425817833514>||"
                elif (i,j) in visibles:
                    string += values[x]
                else:
                    string += "||{}||".format(values[x])
            string += "\n"

        msgs = string.split("\n")
        message = ""
        for m in msgs:
            if len(message) + len(m) > 2000:
                await ctx.send(message)
                message = ""

            message += m + "\n"

        if message != "":
            await ctx.send("​" + message)

    @mines.command(brief="List all avaliable rule presets")
    async def presets(self, ctx):
        return await ctx.send("```\n" + ", ".join(self.mines_rule_presets.keys()) + "\n```")

    @commands.command(brief="Convert between multiples of the speed of light and warp factor.")
    async def warpspeed(self,ctx,unit : str,value : float):
        w_to_c = lambda x: x**(10/3) if x <= 9 else (9**(10/3))*((10-x)**(-10/27))
        c_to_w = lambda x: x**(3/10) if x <= 9**(10/3) else 10 - ((9**9)*(x**(-27/10)))


        if unit == "c":
            return await ctx.send("{}c is equal to Warp Factor {}".format(value,c_to_w(value)))
        elif unit == "w":
            if value > 10:
                return await ctx.send("Uh oh! You friccin moron! That's an invalid warp factor!")
            elif value == 10:
                return await ctx.send("Warp Factor 10.0 is equal to ∞c")
            else:
                return await ctx.send("Warp Factor {} is equal to {}c".format(value,w_to_c(value)))
        else:
            return await ctx.send("Uh oh! You friccin moron! The unit must be either `c` or `w`!")


    @commands.command(brief="Generates a scoring system where each rank gets differing numbers of points.")
    async def pointsystem(self,ctx, numplayers : int):
        if numplayers > 500:
            return await ctx.send("Uh oh! You friccin moron! That's too many players!")

        if numplayers < 2:
            return await ctx.send("Uh oh! You friccin moron! That's too few players!")
        scores = []
        current_score = -1

        halves = int(math.log(numplayers, 2))

        for i in range(numplayers):
            current_score += 1

            for j in range(2, halves):
                if i / numplayers >= (1 - 1 / (2 ** j)):
                    current_score += j - 1

            if i == numplayers - 1:
                current_score = int(current_score * 1.1)

            scores.append(current_score)


        if numplayers <= 12:
            message = "**Score Distribution**```\n"
            scores = scores[::-1]

            for i in range(numplayers):
                if scores[i] != 1:
                    message += "#{} gets {} points\n".format(i+1,scores[i])
                else:
                    message += "#{} gets 1 point\n".format(i+1)
            message = message[:-1] + "```"
            await ctx.send(message)
        else:
            message = "**Score Distribution**\n```" + " ".join(str(i) for i in scores[::-1]) + "\n```"
            await ctx.send(message)


    def dump_battles(self):
        with open("battle.pkl","wb+") as f:
            pickle.dump([self.battle_global_best, self.battle_individual_leaderboard, self.battle_server_leaderboard,
                         self.battle_global_worst, self.battle_individual_leaderboard_worst,
                         self.battle_server_leaderboard_worst],f)

    def individual_top(self,id):
        try:
            return self.battle_individual_leaderboard[id]
        except:
            self.battle_individual_leaderboard[id] = (0,0)
            self.dump_battles()
            return (0,"this should intentionally throw an exception")

    def server_top(self,id):
        try:
            return self.battle_server_leaderboard[id]
        except:
            self.battle_server_leaderboard[id] = (0,0)
            self.dump_battles()
            return (0,"this should also throw an exception")

    def individual_bottom(self,id):
        try:
            return self.battle_individual_leaderboard_worst[id]
        except:
            self.battle_individual_leaderboard_worst[id] = (math.inf,0)
            self.dump_battles()
            return (math.inf,"this should intentionally throw an exception")

    def server_bottom(self,id):
        try:
            return self.battle_server_leaderboard_worst[id]
        except:
            self.battle_server_leaderboard_worst[id] = (math.inf,0)
            self.dump_battles()
            return (math.inf,"this should also throw an exception")

    def get_name(self,id):
        try:
            return self.bot.get_user(id).name
        except:
            try:
                return self.bot.get_guild(id).name
            except:
                return str(id)

    @commands.guild_only()
    @commands.command(brief="Battle it out over the outcome of a pareto distribution.")
    @commands.cooldown(1,3,type=commands.BucketType.user)
    async def battle(self, ctx, *args):
        if len(args) == 0:
            current_score = numpy.random.pareto(1)

            hue = round(300 * (current_score / (current_score + 100)))

            color = hsluv.hsluv_to_rgb((hue,100,70))
            color = tuple(int(255*i) for i in color)
            color = discord.Colour.from_rgb(*color)

            embed = discord.Embed(title=":game_die: :crossed_swords: ", color=color)
            embed.add_field(name="Your Result:", value=str(current_score), inline=False)

            pb = self.individual_top(ctx.author.id)
            pw = self.individual_bottom(ctx.author.id)

            dump_flag = False
            if current_score > pb[0]:
                name = self.get_name(pb[1])
                embed.add_field(name="You beat your personal best!", value="Previously {} (Set on {})".format(pb[0],name), inline=True)
                self.battle_individual_leaderboard[ctx.author.id] = (current_score, ctx.guild.id)
                dump_flag = True

            if current_score < pw[0]:
                name = self.get_name(pw[1])
                embed.add_field(name="You \"beat\" your personal worst!", value="Previously {} (Set on {})".format(pw[0],name), inline=True)
                self.battle_individual_leaderboard_worst[ctx.author.id] = (current_score, ctx.guild.id)
                dump_flag = True

            sb = self.server_top(ctx.guild.id)
            sw = self.server_bottom(ctx.guild.id)
            if current_score > sb[0]:
                name = self.get_name(sb[1])

                embed.add_field(name="You beat the server's high score!",
                                value="Previously {} (Set by {})".format(sb[0],name), inline=True)
                self.battle_server_leaderboard[ctx.guild.id] = (current_score, ctx.author.id)
                dump_flag = True

            if current_score < sw[0]:
                name = self.get_name(sw[1])

                embed.add_field(name="You \"beat\" the server's low score!",
                                value="Previously {} (Set by {})".format(sw[0],name), inline=True)
                self.battle_server_leaderboard_worst[ctx.guild.id] = (current_score, ctx.author.id)
                dump_flag = True

            if current_score > self.battle_global_best[0]:
                uname = self.get_name(self.battle_global_best[1])
                sname = self.get_name(self.battle_global_best[2])

                embed.add_field(name="You beat the All-Time High Score!",
                                value="Previously {} (Set by {} on {})".format(self.battle_global_best[0],uname,sname),
                                inline=False)

                self.battle_global_best = (current_score, ctx.author.id, ctx.guild.id)
                dump_flag = True

            if current_score < self.battle_global_worst[0]:
                uname = self.get_name(self.battle_global_worst[1])
                sname = self.get_name(self.battle_global_worst[2])

                embed.add_field(name="You \"beat\" the All-Time Low Score!",
                                value="Previously {} (Set by {} on {})".format(self.battle_global_worst[0],uname,sname),
                                inline=False)

                self.battle_global_worst = (current_score, ctx.author.id, ctx.guild.id)
                dump_flag = True

            if dump_flag: self.dump_battles()

            embed.set_footer(text="Rolled by {}".format(self.get_name(ctx.author.id)))
            await ctx.send(embed=embed)
        else:
            if args[0] == "help":
                message = '''```
                b9!battle - roll the die and see what happens
                b9!battle help - shows this message
                b9!battle leaderboard - shows the leaderboard across all of Discord.
                b9!battle lowderboard - shows the lowderboard (worst scores) across all of Discord.
                (note: only the highest score of each person is present.)
                ``` 
                '''

                await ctx.send(message)
            if args[0] == "leaderboard":
                leaderboard = sorted(self.battle_individual_leaderboard.items(), key = lambda x: x[1][0], reverse=True)

                rank = 1 + leaderboard.index((ctx.author.id, self.battle_individual_leaderboard[ctx.author.id]))

                message = '''**Leaderboard**\n```\n'''
                for i in range(min(len(leaderboard),20)):
                    message += "#{} - {} - {}\n".format(i+1, self.get_name(leaderboard[i][0]),leaderboard[i][1][0])

                if rank >= 21:
                    message += "...\n"
                    message += "#{} - {} - {}\n".format(rank, self.get_name(leaderboard[rank-1][0]),leaderboard[rank-1][1][0])

                message += "```"

                await ctx.send(message)

            if args[0] == "lowderboard":
                leaderboard = sorted(self.battle_individual_leaderboard_worst.items(), key = lambda x: x[1][0])

                rank = 1 + leaderboard.index((ctx.author.id, self.battle_individual_leaderboard_worst[ctx.author.id]))

                message = '''**Lowderboard**\n```\n'''
                for i in range(min(len(leaderboard),20)):
                    message += "#{} - {} - {}\n".format(i+1, self.get_name(leaderboard[i][0]),leaderboard[i][1][0])

                if rank >= 21:
                    message += "...\n"
                    message += "#{} - {} - {}\n".format(rank, self.get_name(leaderboard[rank-1][0]),leaderboard[rank-1][1][0])

                message += "```"

                await ctx.send(message)


    def ratiocompare(self,value,categories):
        clist = sorted(categories.items(),key=lambda x: x[1])
        clist = sorted(clist, key=lambda x: max(abs(value/x[1]),abs(x[1]/value)))
        return (clist[0][0],value/clist[0][1])

    def colorize(self,im,rgb):
        for i in range(16):
            for j in range(16):
                p = im.getpixel((i,j))
                if p[-1] != 0:
                    im.putpixel((i,j),tuple([int(rgb[n] * (p[n]/255)) for n in range(3)] + [255]))
        return im

    @commands.command(brief="Procedurally generate a new minecraft ore.")
    @commands.cooldown(1,5,type=commands.BucketType.user)
    async def randomore(self, ctx):

        #Generate embed
        embed = discord.Embed()

        #generate name of ore
        initials = list('bcdfghjklmnprstvwxyz') + ['bl', 'br', 'ch', 'cl', 'cr', 'dr', 'fn', 'fl', 'fr', 'gl', 'gr', 'ph', 'pl',
                                                   'pr', 'sh', 'sk', 'sl', 'sm', 'sn', 'sp', 'spl', 'spr', 'st', 'str', 'sw', 'qu',
                                                   'th', 'tj','tr', 'tw', '']

        finals = list('bcdfgklmnprstvxz') + ['ch', 'ck', 'ct', 'ft', 'ld', 'lg', 'lk', 'lt', 'mp', 'nd', 'ng', 'nk', 'nt', 'ph', 'pt',
                                                 'rk', 'rt', 'sh', 'sk', 'sp', 'ss', 'st', 'th', '']

        vowels = ['a','e','i','o','u','ai','ay','ee', 'ea', 'y', 'ie', 'oa', 'ew']

        syllable = lambda n: "".join([random.choice(initials) + random.choice(vowels) + random.choice(finals) for _ in range(n)])

        syllable_count = random.choice([1,1,1,2,2,3])

        suffixes = ['ite','ium','ane','ine','ene','ate','lite','lith']
        suffixes.extend(['' for _ in suffixes])
        name = syllable(syllable_count) + random.choice(suffixes)

        embed.add_field(name="Ore Name", value=name, inline=False)

        #appearance
        rgb = tuple(random.randint(0,255) for i in range(3))
        embed.color = discord.Colour.from_rgb(*rgb)

        item = random.choice(os.listdir("./cmdimages/randomore/item")).replace(".png","")
        block_texture = random.choice(os.listdir("./cmdimages/randomore/block")).replace(".png","")
        ore_texture = random.choice(["coal_ore","lapis_ore","emerald_ore","quartz_ore"] + ["ore{}".format(i) for i in range(1,16)])

        #spawning block, rarity, and y-level spread if applicable
        spawnblock_to_rarity = {
            "stone": lambda: round(random.uniform(0.05, 1.5), 4),
            "diorite": lambda: round(random.uniform(0.05, 1.5), 4),
            "andesite": lambda: round(random.uniform(0.05, 1.5), 4),
            "granite": lambda: round(random.uniform(0.05, 1.5), 4),
            "dirt": lambda: round(random.uniform(0.1, 1.5), 4),
            "gravel": lambda: round(random.uniform(0.1, 1.5), 4),
            "sand": lambda: round(random.uniform(0.1, 1.5), 4),
            "red_sand": lambda: round(random.uniform(0.1, 1.5), 4),
            "soul_sand": lambda: round(random.uniform(0.1, 1.5), 4),
            "obsidian": lambda: round(random.uniform(1, 3), 4),
            "end_stone": lambda: round(random.uniform(0.5, 2), 4),
            "netherrack": lambda: round(random.uniform(0.01, 1.75), 4)
        }

        spawnblocks = list(spawnblock_to_rarity.keys())
        spawnblocks.extend(['stone' for i in spawnblocks])



        spawnblock = random.choice(spawnblocks)

        rarity = spawnblock_to_rarity[spawnblock]()

        if spawnblock == "stone":
            if random.random() < 0.2:
                bottom = random.randint(5,35)
                top = random.randint(75,135)
            else:
                bottom = random.randint(5,75)
                top = bottom + random.randint(7,30)

            rmessage = "Spawn - {}% of Stone between Y={} and Y={}".format(rarity,bottom,top)
        else:
            rmessage = "Spawn - {}% of {}".format(rarity,spawnblock.replace("_"," ").title())

        vein_bottom = random.randint(1,3)
        vein_top = vein_bottom + random.randint(1,10)

        rmessage += "\nVeins - {}-{} blocks".format(vein_bottom,vein_top)

        x = random.random()

        if x < 0.25:
            drop_bottom = random.randint(2,4)
            drop_top = drop_bottom + random.randint(1,3)
            rmessage += "\nDrop - {}-{} resource".format(drop_bottom,drop_top)
        elif x < 0.75:
            rmessage += "\nDrop - 1 resource"
        else:
            rmessage += "\nDrop - Raw ore"

        if x < 0.75:
            xp_bottom = random.randint(1,5)
            xp_top = xp_bottom + random.randint(1,5)
            rmessage += "\nMining XP - {}-{} points".format(xp_bottom,xp_top)
        else:
            rmessage += "\nSmelting XP - {} points".format(random.choice([1,1,1,1,2]))

        material = random.choice(["Wood","Stone","Iron","Diamond"])
        if spawnblock in ["stone","granite","diorite","andesite","obsidian","netherrack","end_stone"]:
            tooltype = "Pickaxe"
        else:
            tooltype = "Shovel"

        rmessage += "\nMineable by - {} {} or better.".format(material,tooltype)

        embed.add_field(name="Mining Information",value=rmessage,inline=False)

        #tools
        tmessage = ""

        can_make_tools = random.random() > 0.25
        if not can_make_tools:
            tmessage += "This ore cannot be crafted into tools"
        else:
            sword_attack_damage = random.randint(8,20)/2
            damage_comp = {
                "Wood" : 4,
                "Stone" : 5,
                "Iron" : 6,
                "Diamond" : 7,
            }
            closest_damage = self.ratiocompare(sword_attack_damage,damage_comp)

            tmessage += "Sword Damage - {} ({}× {})".format(sword_attack_damage,round(closest_damage[1],2),closest_damage[0])

            tool_durability = int(random.choice([32,131,250,250,250,250,1561,1561,2500]) * random.uniform(0.5,2))
            durab_comp = {
                "Gold" : 32,
                "Stone" : 131,
                "Iron" : 250,
                "Diamond" : 1561,
            }
            closest_durab = self.ratiocompare(tool_durability,durab_comp)
            tmessage += "\nDurability - {} ({}× {})".format(tool_durability,round(closest_durab[1],2),closest_durab[0])

            tool_speed = round(random.choice([4,6,6,6,8,8,12]) * random.uniform(0.75,1.5),1)
            speed_comp = {
                "Fists" : 1,
                "Wood" : 2,
                "Stone" : 4,
                "Iron" : 6,
                "Diamond" : 8,
                "Gold" : 12
            }
            closest_speed = self.ratiocompare(tool_speed,speed_comp)
            tmessage += "\nMining Speed Multiplier - {}× ({}× {})".format(tool_speed,round(closest_speed[1],2),
                                                                                                                closest_speed[0])
            ptypes = ["Stone","Iron","Diamond"]
            tmessage += "\nMining Level - {}".format(random.choice(ptypes))

            tool_enchantability = round(random.choice([5, 10, 10, 14, 14, 14, 15, 15, 15, 22]) * random.uniform(0.75,2.5))
            tool_ench_comp = {
                "Stone": 5,
                "Iron": 14,
                "Diamond": 10,
                "Gold": 22
            }

            closest_tool_enchantability = self.ratiocompare(tool_enchantability, tool_ench_comp)
            tmessage += "\nEnchantability - {} ({}× {})".format(tool_enchantability, round(closest_tool_enchantability[1], 2),
                                                                                          closest_tool_enchantability[0])
        embed.add_field(name="Tool Information", value=tmessage, inline=False)

        #armor
        amessage = ""
        can_make_armor = random.random() > 0.25
        if not can_make_armor:
            amessage += "This ore cannot be crafted into armor"
        else:
            prot_chest = random.randint(3,12)
            prot_leggings = max(1, prot_chest - random.randint(1, 5))
            prot_boots = max(1, prot_leggings - random.randint(1, 5))
            prot_helmet = max(1, prot_boots - random.randint(0,2))

            fullset_protection = prot_chest + prot_leggings + prot_boots + prot_helmet

            fsp_comp = {
                "Leather" : 7,
                "Chainmail" : 12,
                "Iron" : 15,
                "Diamond" : 20
            }

            closest_fsp = self.ratiocompare(fullset_protection,fsp_comp)

            pline = "Total Protection - {} points ({}× {})".format(fullset_protection,round(closest_fsp[1],2),closest_fsp[0])
            indivline = "\nPiece Protection - Helm {}, Chest {}, Legs {}, Boots {}".format(prot_helmet,prot_chest,prot_leggings,prot_boots)

            amessage += pline + indivline

            if random.random() < 0.25:
                armor_toughness = random.randint(1,4)
                amessage += "\nToughness - {} per piece".format(armor_toughness)


            dpu = random.choice([16.5,23,49,49,49,107.5]) * random.uniform(0.5,2.5)
            dpu_comp = {
                "Leather" : 16.5,
                "Gold" : 23,
                "Iron" : 49,
                "Diamond" : 107.5
            }

            closest_dpu = self.ratiocompare(dpu,dpu_comp)

            durab_helm = int(0.68 * 5 * dpu)
            durab_chest = int(0.61 * 8 * dpu)
            durab_leg = int(0.66 * 7 * dpu)
            durab_boots = int(4 * dpu)

            amessage += "\nDurability - Helm {}, Chest {}, Legs {}, Boots {} ({}× {})".format(durab_helm,durab_chest,
                                                                                              durab_leg,durab_boots,
                                                                                              round(closest_dpu[1],2),closest_dpu[0])

            armor_enchantability = round(random.choice([9, 10, 10, 12, 12, 14, 15, 25, 25]) * random.uniform(0.75,2.5))
            armor_ench_comp = {
                "Leather": 15,
                "Iron": 9,
                "Diamond": 10,
                "Chainmail": 12,
                "Gold": 25
            }

            closest_armor_enchantability = self.ratiocompare(armor_enchantability, armor_ench_comp)
            amessage += "\nEnchantability - {} ({}× {})".format(armor_enchantability,
                                                                                          round(closest_armor_enchantability[1], 2),
                                                                                          closest_armor_enchantability[0])

        embed.add_field(name="Armor Information", value=amessage, inline=False)


        #special characteristics
        if random.random() < 0.2:
            positive_effects = ["Speed","Haste","Strength","Instant Health","Jump Boost","Regeneration","Resistance",
                                "Fire Resistance","Water Breathing","Invisibility","Night Vision","Health Boost",
                                "Absorption","Saturation","Luck","Slow Falling","Conduit Power","Dolphin's Grace",
                                "Hero of the Village"]

            negative_effects = ["Slowness","Mining Fatigue","Instant Damage","Nausea","Blindness","Hunger","Weakness",
                                "Poison","Wither","Glowing","Bad Luck","Bad Omen"]

            single_potency_effects = ["Water Breathing","Invisibility","Night Vision","Blindness","Glowing"]

            positive_effect = random.choice(positive_effects) if random.random() < 0.75 else random.choice(negative_effects)
            negative_effect = random.choice(negative_effects) if random.random() < 0.75 else random.choice(positive_effects)

            random_time = lambda: random.choice(["10s", "10s", "10s", "10s", "30s", "30s", "30s", "45s", "45s", "1m","2m"])
            random_potency = lambda effect: " " + random.choice(["I","I","I","I","I","II","II","III"]) if effect not in single_potency_effects else ""

            spmessage = []

            #consumable
            if random.random() < 0.5:
                if random.random() < 0.5:
                    consume_bonus = "{} Hunger Points, {} Saturation Points".format(random.randint(6,14),random.randint(2,10))
                else:
                    if "Instant" in positive_effect:
                        consume_bonus = "{}{}".format(positive_effect,random_potency(positive_effect))
                    else:
                        consume_bonus = "{} of {}{}".format(random_time(),positive_effect,random_potency(positive_effect))

                spmessage.append("Effect of Consumption - {}".format(consume_bonus))

            #tool strike effect
            if random.random() < 0.75 and can_make_tools:
                if "Instant" in negative_effect:
                    hit_bonus = "{}{}".format(negative_effect, random_potency(negative_effect))
                else:
                    hit_bonus = "{} of {}{}".format(random_time(), negative_effect, random_potency(negative_effect))

                spmessage.append("Effect on Hit - {}".format(hit_bonus))


            #full set bonus
            if random.random() < 0.25 and can_make_armor:
                ni_positive = [i for i in positive_effects if "Instant" not in i]
                ni_negative = [i for i in negative_effects if "Instant" not in i]

                fs_effect = random.choice(ni_positive) if random.random() < 0.75 else random.choice(ni_negative)

                spmessage.append("Full Set Bonus - {}{}".format(fs_effect,random_potency(fs_effect)))

            embed.add_field(name="Special Abilities",value="\n".join(spmessage),inline=False)

        #create images
        iim = Image.open("./cmdimages/randomore/item/{}.png".format(item)).convert("RGBA")

        iim = self.colorize(iim,rgb)

        iim = iim.resize((64,64))

        bim = Image.open("./cmdimages/randomore/block/{}.png".format(block_texture)).convert("RGBA")
        bim = self.colorize(bim, rgb)
        bim = bim.resize((64,64))

        im = Image.new("RGBA",(160,64),(0,0,0,0))

        im.paste(iim,(0,0),iim)
        im.paste(bim,(80,0),bim)

        im.save("output.png")
        with open("output.png", mode="rb") as f:
            item_file = discord.File(f, filename="item.png")

        im = Image.open("./cmdimages/randomore/ore/{}.png".format(spawnblock)).convert("RGBA")
        ore_overlay = Image.open("./cmdimages/randomore/ore/{}.png".format(ore_texture)).convert("RGBA")

        ore_overlay = self.colorize(ore_overlay, rgb)

        im.paste(ore_overlay, (0,0), ore_overlay)
        im = im.resize((64, 64))

        im.save("output2.png")

        with open("output2.png",mode="rb") as f:
            ore_file = discord.File(f, filename="ore.png")

            embed.set_thumbnail(url="attachment://ore.png")
            embed.set_image(url="attachment://item.png")



            await ctx.send(embed=embed,files=[item_file, ore_file])

        try:
            os.remove("output2.png")
        except FileNotFoundError:
            pass



    @commands.group(aliases=['mm','mmind','masterm'],brief="Play a game of mastermind",invoke_without_command="true")
    async def mastermind(self, ctx, guess):
        if ctx.author.id not in self.mm_games:
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

        data = self.mm_games[ctx.author.id]
        password = data[0]
        moves = data[1]
        moves += 1
        guess = guess.upper()

        if guess == password:
            del self.mm_games[ctx.author.id]
            return await ctx.send("You are correct, the password is `{}`! It took you `{}` guesses to find it!".format(password,moves))

        correct_position = 0
        for i in range(len(guess)):
            if guess[i] == password[i]:
                correct_position += 1

        pw_multiset = collections.Counter(password)
        guess_multiset = collections.Counter(guess)

        correct_any = sum((pw_multiset & guess_multiset).values())

        incorrect_position = correct_any - correct_position

        await ctx.send("Guess #{} - {}\n"
                       "Correct Number, Incorrect Position: {}\n"
                       "Correct Number, Correct Position: {}\n".format(moves,guess,incorrect_position,correct_position))

        self.mm_games[ctx.author.id] = [password,moves]

    @mastermind.command(brief="create a game")
    async def create(self, ctx, length : int, alphabet : int):
        if ctx.author.id not in self.mm_games:
            alpha = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            if alphabet > len(alpha):
                return await ctx.send("Uh oh! You friccin moron! That's too many characters in your alphabet!")
            if alphabet < 2:
                return await ctx.send("Uh oh! You friccin moron! That's nonsensical!")
            if length > 100:
                return await ctx.send("Uh oh! You friccin moron! That's too long of a code!")
            string = "".join(random.choice(alpha[:alphabet]) for i in range(length))

            self.mm_games[ctx.author.id] = [
                string,
                0
            ]

            return await ctx.send("Game created!")
        else:
            return await ctx.send("Uh oh! You friccin moron! You're already in a game!")

    @mastermind.command(brief="leave your game")
    async def leave(self, ctx):
        if ctx.author.id in self.mm_games:
            del self.mm_games[ctx.author.id]
            return await ctx.send("You have left your game!")
        else:
            return await ctx.send("Uh oh! You friccin moron! You aren't in a game!")

    def draw_compass_text(self, draw, text, coords, font, fill):
        wfont, hfont = draw.textsize(text, font=font)
        c = (coords[0] - wfont // 2, coords[1] - hfont // 2)
        draw.text(c, text, fill=fill, font=font)

    @commands.command(brief="Generate a compass on which people can be placed")
    async def compass(self, ctx, top, bottom, left, right):
        cimg = Image.open("cmdimages/compass.png")
        draw = ImageDraw.Draw(cimg)

        font = ImageFont.truetype("cmdimages/anguleux.ttf",70)

        self.draw_compass_text(draw,top,(540,40),font,(0,0,0))
        self.draw_compass_text(draw,bottom,(540,1020),font,(0,0,0))
        cimg = cimg.rotate(-90)
        draw = ImageDraw.Draw(cimg)
        self.draw_compass_text(draw, left, (540, 40), font, (0, 0, 0))
        cimg = cimg.rotate(180)
        draw = ImageDraw.Draw(cimg)
        self.draw_compass_text(draw, right, (540, 40), font, (0, 0, 0))

        cimg = cimg.rotate(-90)
        cimg.save("output.png")
        await ctx.send(file=discord.File(open("output.png", mode="rb")))



    '''
    @commands.command(brief="Talk to the DeepTWOW Bots!")
    @commands.cooldown(1,8,type=commands.BucketType.user)
    async def deepbots(self,ctx,bot,*words):
        bots = ["alpha","beta","gamma","delta","epsilon","wau","zeta","eta","theta","iota","kappa","lambda","mu","nu","xi","omicron",
                "pi","qoppa","rho","sigma","tau","upsilon","phi","chi","psi","omega"]

        greek = "αβγδεϝζηθικλμνξοπϙρστυφχψω"

        b = bot.lower()
        if b not in bots:
            return await ctx.send("Uh oh! You friccin moron! That's not a bot!")


        bot_id = str(bots.index(b)+1)

        old_stdout = sys.stdout
        sys.stdout = TextIOWrapper(BytesIO(), sys.stdout.encoding)


        bot_file = "../DeepTWOW/rnn_tf Generation/saved/" + bot_id + "/bot.ckpt"

        # do something that writes to stdout or stdout.buffer
        command = 'python rnn_tf.py --input_file=training_responses_shuffled.txt --ckpt_file="' + bot_file + '" --test_prefix=" " --mode=talk'
        ans = subprocess.run(command, stdout=subprocess.PIPE).stdout.decode('utf-8')

        ans = ans.split("\n")[1:]
        ans = [i for i in ans if i != ""]
        await ctx.send("**Bot " + greek[int(bot_id)-1] + ":** " + random.choice(ans))
    '''



def setup(bot):
    bot.add_cog(Misc(bot))



'''

'''
