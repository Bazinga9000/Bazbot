import discord
from discord.ext import commands
from sympy import *
import hashlib
import math
import dice
import glob
import random
import pickle
from PIL import Image
import aiohttp
from io import BytesIO

x, t, z, nu = symbols('x t z nu')
e = math.e
pi = math.pi


class Misc():
    def __init__(self, bot):
        self.bot = bot
        self.ratel = lambda x: int(hashlib.sha256(x.lower().encode('utf-8')).hexdigest(),16) % 101

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

        url = url.replace(".webp",".png").replace(".webm",".png")

        if ".png" not in url and ".jpg" not in url and ".gif" not in url:
            return await ctx.send("Uh oh! You friccin moron! That's not an image!")

        with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                response = await resp.read()

        try:
            image = Image.open(BytesIO(response))
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
    async def code(self,ctx):
        await ctx.send("**View Bazbot's source code here**\nhttps://github.com/Bazinga9000/Bazbot")

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
            score = 5
        elif entity.lower() in ["baz","bazinga","bazinga9000","bazinga 9000","bazinga_9000","my creator","<@137001076284063744>"]:
            score = 5
        else:
            score = min(5,self.ratel(entity)//20)

        await ctx.send("**" + entity + "**",file=discord.File(open("./scales/" + str(score) + ".png",mode="rb")))

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




    @commands.command(brief="Summon me to your servers")
    async def summon(self,ctx):
        await ctx.send("**Invite me to your discord servers by using the following link**\nhttps://discordapp.com/oauth2/authorize?&client_id=382925349144494080&scope=bot&permissions=0")


    @commands.command(brief="Randomly decide a binary outcome.")
    async def yesorno(self,ctx, *question):
        await ctx.send(" ".join(question),file=discord.File(open(random.choice(["./images/yes.gif","./images/no.gif"]),mode="rb")))

    #everything below this line (except setup()) was made by bottersnike and hanss
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
                cmds = self.bot.get_cog_commands(cog_name)
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




def setup(bot):
    bot.add_cog(Misc(bot))
