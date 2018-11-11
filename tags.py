import discord
from discord.ext import commands
import json
import shlex
import random
import pickle
import numpy
import math
import asyncio
import sys, traceback

class Tag:
    def __init__(self,name,command,authorname,authorid,guildid,var={},ucount=0):
        self.name = name
        self.command = command
        self.aname = authorname
        self.aid = authorid
        self.guild = guildid
        self.vars = var
        self.usecount = ucount


    def iscommand(self, x):
        return bool(x.startswith("[") and x.endswith("]"))

    def blockify(self, text):
        splits = [""]

        level = 0

        for i in text:
            if i == "[":
                if level == 0:
                    splits.append("")
                level += 1

            splits[-1] += i

            if i == "]":
                level -= 1
                if level < 0:
                    raise ValueError
                elif level == 0:
                    splits.append("")

        return splits

    def commandsplit(self,text):

        splits = self.blockify(text)

        results = []

        for split in splits:
            if self.iscommand(split):
                results.append(split)
            else:
                for i in shlex.split(split):
                    results.append(i)

        return results

    def litparse(self, literal, ctx):
        try:
            return int(str(literal)) #int
        except:
            pass

        try:
            return float(literal) #float
        except:
            pass

        try:
            return complex(literal) #complex
        except:
            pass

        try:
            return complex(literal.replace("i","j")) #complex with i instead of j
        except:
            pass

        if literal in ["True","False"]:
            return {"True" : True, "False" : False}[literal] #bool

        if self.iscommand(literal):
            try:
                return self.evaluate(literal[1:-1],ctx) #command
            except:
                return "�" #the you fucked up character
        else:
            return literal #string

    def evaluate(self,cmd,ctx):
        result = cmd


        args = self.commandsplit(cmd)

        variables = self.vars

        command = args[0]

        if len(args) > 1:
            params = args[1:]
        else:
            params = []


        l = lambda x: self.litparse(x,ctx)


        ###RANDOMNESS
        if command == "choose":
            result = random.choice(params)

        elif command == "randint":
            result = random.randint(l(params[0]),l(params[1]))

        elif command == "pareto":
            result = numpy.random.pareto(l(params[0]))

        elif command == "normal":
            result = numpy.random.normal(l(params[0]),l(params[1]))

        elif command == "uniform":
            result = numpy.random.uniform(l(params[0]),l(params[1]))


        ###CONTROL FLOW AND SHIT
        elif command == "var":

            self.vars[params[0]] = l(params[1])
            result = ""

        elif command == "if":
            if l(params[0]):
                result = l(params[1])
            else:
                if len(params) == 2:
                    pass
                else:
                    result = l(params[2])

        elif command == "code":

            result = ""

            for p in params:

                if self.iscommand(p):
                    try:
                        res = l(p)
                        result += str(res)
                    except Exception as e:
                        # ex_type, ex, tb = sys.exc_info()
                        # print(e)
                        # traceback.print_tb(tb)
                        result += "�"
                        # del tb
                else:
                    result += str(p)

        ###MATHEMATICS AND SHIT
        elif command == "math":
            stack = []

            operations = ["+","-","*","/","^","%","sqrt","log","sin","cos","tan","pi","=","!=",">","<",">=","<="]

            constants = {"pi" : numpy.math.pi, "π" : numpy.math.pi, "e" : numpy.math.e}

            for q in params:

                p = l(q)

                if p not in operations:
                    stack.append(p)
                elif p in constants:
                    stack.append(constants[p])
                else:
                    if p == "+":
                        r = stack.pop() + stack.pop()
                    elif p == "-":
                        a = stack.pop()
                        b = stack.pop()
                        r = b-a
                    elif p == "*":
                        r = stack.pop() * stack.pop()
                    elif p == "/":
                        r = (1/stack.pop()) * stack.pop()
                    elif p == "^":
                        a = stack.pop()
                        b = stack.pop()
                        r = math.pow(b,a)
                    elif p == "%":
                        a = stack.pop()
                        b = stack.pop()
                        r = b%a
                    elif p == "sqrt":
                        r = numpy.math.sqrt(stack.pop())
                    elif p == "log":
                        a = stack.pop()
                        b = stack.pop()
                        r = numpy.math.log(a,b)
                    elif p == "sin":
                        r = numpy.math.sin(stack.pop())
                    elif p == "cos":
                        r = numpy.math.cos(stack.pop())
                    elif p == "tan":
                        r = numpy.math.tan(stack.pop())

                    elif p == "=":
                        r = bool(stack.pop() == stack.pop())
                    elif p == "!=":
                        r = bool(stack.pop() != stack.pop())

                    #"baz, these following inequalities are backwards!"
                    #i hear you cry.
                    #
                    #but fear not. the stack.pop() calls are in reverse order, since that's the only way
                    #i can grab both of the top two items. (a > b) is the same as (b < a)

                    elif p == ">":
                        r = bool(stack.pop() < stack.pop())
                    elif p == "<":
                        r = bool(stack.pop() > stack.pop())
                    elif p == ">=":
                        r = bool(stack.pop() <= stack.pop())
                    elif p == "<=":
                        r = bool(stack.pop() <= stack.pop())

                    stack.append(r)

            result = stack[0]

        elif command == "round":
            result = round(l(params[0]),l(params[1]))

        ###CONTEXT
        elif command == "username":
            result = ctx.author.name

        elif command == "channel":
            result = ctx.channel.name

        elif command == "server":
            result = ctx.guild.name

        elif command == "userid":
            result = ctx.user.id

        elif command == "channelid":
            result = ctx.channel.id

        elif command == "serverid":
            result = ctx.guild.id

        elif command in variables:
            result = self.vars[command]

        return result


    def get(self, ctx):
        blocks = self.blockify(self.command)

        parsedstring = ""

        for block in blocks:
            if self.iscommand(block):
                try:
                    res = self.evaluate(block[1:-1],ctx)
                    parsedstring += str(res)
                except Exception as e:
                    #ex_type, ex, tb = sys.exc_info()
                    #print(e)
                    #traceback.print_tb(tb)
                    parsedstring += "�"
                    #del tb

            else:
                parsedstring += block
        return parsedstring

class Tags():
    def __init__(self, bot):
        self.bot = bot
        self.tags = self.get_tags()
        self.dump_tags()
        self.banned_tags = ["create", "edit", "delete", "info", "update"]


    def update_tags(self):
        self.tags = [Tag(t.name,t.command,t.aname,t.aid,t.guild,t.vars,t.usecount) for t in self.tags]
        self.dump_tags()

    def get_tags(self):
        try:
            with open('tags.pkl', 'rb') as f:
                return pickle.load(f)
        except:
            return []

    def dump_tags(self):
        try:
            with open('tags.pkl', 'wb') as f:
                pickle.dump(self.tags, f)
        except Exception as e:
            print("PICKLING ERROR: " + str(e))
            return

        with open('backuptags.pkl', 'wb') as f:
            pickle.dump(self.tags, f)


    def getservertags(self,id):
        return [p for p in self.tags if p.guild == id]


    @commands.guild_only()
    @commands.group(brief="Tag System",invoke_without_command=True)
    @commands.cooldown(1,4,type=commands.BucketType.user)
    async def tag(self,ctx, name : str):
        if ctx.author.bot: return

        valid_tags = self.getservertags(ctx.guild.id)
        names = [t.name for t in valid_tags]
        try:
            index = names.index(name)
        except:
            await ctx.send("Uh oh! You friccin moron! That tag doesn't exist!")
            return
        else:
            tag = valid_tags[index]
            tag.usecount += 1
            loop = asyncio.get_event_loop()
            coroutine = loop.run_in_executor(None, tag.get, ctx)
            task = asyncio.wait_for(coroutine, 5)
            try:
                answer = await task
                await ctx.send(answer)
                self.dump_tags()
            except asyncio.TimeoutError:
                await ctx.send("Uh oh! You friccin moron! That took too long!")

    @commands.guild_only()
    @tag.command(brief="Create a tag!")
    async def create(self, ctx, name: str, *, text: str):

        if name in self.banned_tags:
            await ctx.send("Uh oh! You friccin moron! That can't be a tag!")
            return

        id = ctx.guild.id


        if name in [t.name for t in self.getservertags(id)]:
            await ctx.send("Uh oh! You friccin moron! Someone already made the `" + name + "` tag!")
        elif len(name) > 30:
            await ctx.send("Uh oh! You friccin moron! That name is too long!")
        elif "`" in name or "\n" in name:
            await ctx.send("Uh oh! You friccin moron! That name contains an invalid character!")
        else:
            self.tags.append(Tag(name,text,ctx.author.name,ctx.author.id,id))
            self.dump_tags()
            await ctx.send(ctx.author.name + ", Your tag has been created!")

    @commands.guild_only()
    @tag.command(brief="List tags!")
    async def list(self, ctx, page : int = 1):
        valid_tags = self.getservertags(ctx.guild.id)

        if page < 1:
            await ctx.send("Uh oh! You friccin moron! That's an invalid page number!")
            return

        tagcount = len(valid_tags)

        if 10 * (page - 1)> tagcount:
            await ctx.send("Uh oh! You friccin moron! You don't have that many tags!")
            return

        text = "```\n"

        valid_tags = sorted(valid_tags,key=lambda x: x.usecount)[::-1]

        for i in range(10):
            try:
                j = 10*(page-1) + i
                tag = valid_tags[j]

                text += str(j+1) + ") " + tag.name + " (Used " + str(tag.usecount) + " times)\n"


            except:
                continue

        text += "```"
        await ctx.send(text)

    @commands.guild_only()
    @tag.command(brief="Edit a tag you own!")
    async def edit(self, ctx, name : str, *, text : str):

        if name in self.banned_tags:
            await ctx.send("Uh oh! You friccin moron! That can't be a tag!")
            return

        valid_tags = self.getservertags(ctx.guild.id)
        names = [t.name for t in valid_tags]

        try:
            ind = names.index(name)
            tag = valid_tags[ind]
        except:
            await ctx.send("Uh oh! You friccin moron! That tag doesn't exist!")
            return

        if tag.aid != ctx.author.id:
            await ctx.send("Uh oh! You friccin moron! That tag isn't yours!")
            return
        else:
            master_index = self.tags.index(tag)
            self.tags[master_index].command = text
            self.dump_tags()
            await ctx.send("Tag edited!")

    @commands.guild_only()
    @tag.command(brief="Delete a tag you own!")
    async def delete(self, ctx, name: str):

        if name in self.banned_tags:
            await ctx.send("Uh oh! You friccin moron! That can't be a tag!")
            return

        valid_tags = self.getservertags(ctx.guild.id)
        names = [t.name for t in valid_tags]

        try:
            ind = names.index(name)
            tag = valid_tags[ind]
        except:
            await ctx.send("Uh oh! You friccin moron! That tag doesn't exist!")
            return

        if tag.aid != ctx.author.id:
            await ctx.send("Uh oh! You friccin moron! That tag isn't yours!")
            return
        else:
            master_index = self.tags.index(tag)
            del self.tags[master_index]
            self.dump_tags()
            await ctx.send("Tag deleted!")

    @commands.guild_only()
    @tag.command(brief="Delete a tag you own!")
    async def nuke(self, ctx, name: str):

        if name in self.banned_tags:
            await ctx.send("Uh oh! You friccin moron! That can't be a tag!")
            return


        if ctx.author.id != 137001076284063744:
            return await ctx.send("You can't do that!")

        valid_tags = self.getservertags(ctx.guild.id)
        names = [t.name for t in valid_tags]

        try:
            ind = names.index(name)
            tag = valid_tags[ind]
        except:
            await ctx.send("Uh oh! You friccin moron! That tag doesn't exist!")
            return

        else:
            master_index = self.tags.index(tag)
            del self.tags[master_index]
            self.dump_tags()
            await ctx.send("Tag deleted!")

    @commands.guild_only()
    @tag.command(brief="Get info on a tag!")
    async def info(self,ctx, name : str):
        if name in self.banned_tags:
            await ctx.send("Uh oh! You friccin moron! That can't be a tag!")
            return

        valid_tags = sorted(self.getservertags(ctx.guild.id),key=lambda x: x.usecount)[::-1]
        names = [t.name for t in valid_tags]
        try:
            index = names.index(name)
        except:
            await ctx.send("Uh oh! You friccin moron! That tag doesn't exist!")
            return
        else:
            tag = valid_tags[index]
            message = "**Info on Tag `" + name + "`**\n\n"
            message += "Raw Output: `" + tag.command + "`\n"
            message += "Creator: *" + tag.aname + "*\n"
            message += "Used " + str(tag.usecount) + " times (Ranked #" + str(index+1) + "/" + str(len(valid_tags)) + ")"

            await ctx.send(message)


    @tag.command(brief="Update tags to implement new commands into them.")
    @commands.check(lambda ctx: ctx.author.id == 137001076284063744)
    async def update(self,ctx):
        self.update_tags()
        await ctx.send("Updated!")


def setup(bot):
    bot.add_cog(Tags(bot))
