import discord
from discord.ext import commands

class CC():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Soon™")
    async def cc(self, ctx, *args):
        if ctx.author.id != 137001076284063744 or ctx.guild is not None:
            puzzles_completed = 22
            unfinished = 29 - puzzles_completed
            return await ctx.send("[" + "█" * puzzles_completed + "░" * unfinished + "]")

        if len(args) != 0 and ctx.guild is not None:
            return await ctx.send("Uh oh! You friccin moron! You can only submit answers via DM!")
        await ctx.send(args)

def setup(bot):
    bot.add_cog(CC(bot))
