import discord
from discord.ext import commands
import json
import shlex
import random

class Tags():
    def __init__(self, bot):
        self.bot = bot
        self.tags = self.get_tags()
        self.dump_tags()

    def parenparse(self, text):
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

    def evaluate(self, args, vars, ctx):
        result = " ".join(args)

        variables = vars

        command = args[0]


        if len(args) > 1:
            params = args[1:]
        else:
            params = []


        if command == "choose":

            result = random.choice(params)

        elif command == "randint":

            result = random.randint(int(params[0]),int(params[1]))

        elif command == "var":

            variables[params[0]] = params[1]
            result = params[1]

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
            result = variables[command]

        return result, variables

    def tagscript(self, tag, ctx):
        blocks = self.parenparse(tag[1])
        vars = tag[4]

        parsedstring = ""

        for block in blocks:
            if block.startswith("[") and block.endswith("]"):
                args = shlex.split(block[1:-1])
                try:
                    res, vars = self.evaluate(args,vars,ctx)
                    parsedstring += res
                except:
                    parsedstring += "�"


            else:
                parsedstring += block

        tag[4] = vars
        return parsedstring

    def get_tags(self):
        with open("tags.txt","r+") as f:
            try:
                return json.load(f)
            except:
                return []

    def dump_tags(self):
        json.dump(self.tags,open("tags.txt", "w"))

    def getservertags(self,id):
        return [p for p in self.tags if p[3] == id]



    @commands.group(brief="Tag System",invoke_without_command=True)
    async def tag(self,ctx, name : str):

        if ctx.author.bot: return

        valid_tags = self.getservertags(ctx.guild.id)
        names = [t[0] for t in valid_tags]
        try:
            index = names.index(name)
        except:
            await ctx.send("Uh oh! You friccin moron! That tag doesn't exist!")
            return
        else:
            tag = valid_tags[index]
            tag[-1] += 1
            await ctx.send(self.tagscript(tag,ctx))
            self.dump_tags()

    @tag.command(brief="Create a tag!")
    async def create(self, ctx, name: str, *, text: str):

        if name in ["create", "edit", "delete", "info"]:
            await ctx.send("Uh oh! You friccin moron! That can't be a tag!")
            return

        if name in [t[0] for t in self.getservertags(ctx.guild.id)]:
            await ctx.send("Uh oh! You friccin moron! Someone already made the `" + name + "` tag!")
        elif len(name) > 30:
            await ctx.send("Uh oh! You friccin moron! That name is too long!")
        elif "`" in name or "\n" in name:
            await ctx.send("Uh oh! You friccin moron! That name contains an invalid character!")
        else:
            self.tags.append([name, text, [ctx.author.name, ctx.author.id], ctx.guild.id, {}, 0])
            self.dump_tags()
            await ctx.send(ctx.author.name + ", Your tag has been created!")


    @tag.command(brief="List tags!")
    async def list(self, ctx, page : int):
        valid_tags = self.getservertags(ctx.guild.id)

        if page < 1:
            await ctx.send("Uh oh! You friccin moron! That's an invalid page number!")
            return

        tagcount = len(valid_tags)

        if 10 * (page - 1)> tagcount:
            await ctx.send("Uh oh! You friccin moron! You don't have that many tags!")
            return

        text = "```\n"

        valid_tags = sorted(valid_tags,key=lambda x: x[-1])[::-1]

        for i in range(10):
            try:
                j = 10*(page-1) + i
                tag = valid_tags[j]

                text += str(j+1) + ") " + tag[0] + " (Used " + str(tag[-1]) + " times)\n"


            except:
                continue

        text += "```"
        await ctx.send(text)

    @tag.command(brief="Edit a tag you own!")
    async def edit(self, ctx, name : str, *, text : str):

        if name in ["create", "edit", "delete", "info"]:
            await ctx.send("Uh oh! You friccin moron! That can't be a tag!")
            return

        valid_tags = self.getservertags(ctx.guild.id)
        names = [t[0] for t in valid_tags]

        try:
            ind = names.index(name)
            tag = valid_tags[ind]
        except:
            await ctx.send("Uh oh! You friccin moron! That tag doesn't exist!")
            return

        if tag[2][1] != ctx.author.id:
            await ctx.send("Uh oh! You friccin moron! That tag isn't yours!")
            return
        else:
            master_index = self.tags.index(tag)
            self.tags[master_index][1] = text
            self.dump_tags()
            await ctx.send("Tag edited!")

    @tag.command(brief="Delete a tag you own!")
    async def delete(self, ctx, name : str):

        if name in ["create", "edit", "delete", "info"]:
            await ctx.send("Uh oh! You friccin moron! That can't be a tag!")
            return

        valid_tags = self.getservertags(ctx.guild.id)
        names = [t[0] for t in valid_tags]

        try:
            ind = names.index(name)
            tag = valid_tags[ind]
        except:
            await ctx.send("Uh oh! You friccin moron! That tag doesn't exist!")
            return

        if tag[2][1] != ctx.author.id:
            await ctx.send("Uh oh! You friccin moron! That tag isn't yours!")
            return
        else:
            master_index = self.tags.index(tag)
            del self.tags[master_index]
            self.dump_tags()
            await ctx.send("Tag deleted!")

    @tag.command(brief="Get info on a tag!")
    async def info(self,ctx, name : str):

        if name in ["create", "edit", "delete", "info"]:
            await ctx.send("Uh oh! You friccin moron! That can't be a tag!")
            return

        valid_tags = sorted(self.getservertags(ctx.guild.id),key=lambda x: x[-1])[::-1]
        names = [t[0] for t in valid_tags]
        try:
            index = names.index(name)
        except:
            await ctx.send("Uh oh! You friccin moron! That tag doesn't exist!")
            return
        else:
            tag = valid_tags[index]
            message = "**Info on Tag `" + name + "`**\n\n"
            message += "Raw Output: `" + tag[1] + "`\n"
            message += "Creator: *" + tag[2][0] + "*\n"
            message += "Used " + str(tag[-1]) + " times (Ranked #" + str(index+1) + "/" + str(len(valid_tags)) + ")"

            await ctx.send(message)


def setup(bot):
    bot.add_cog(Tags(bot))
