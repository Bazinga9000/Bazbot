import discord
from discord.ext import commands
import Botzinga_9000.textcommands as c
import importlib


class Text():


    def __init__(self, bot):
        self.bot = bot
        self.tfuncs = {"mario" : c.mario}
        importlib.reload(c)

    @commands.command(brief="Find out if the bot is alive.")
    async def areyoualive(self,ctx):
        await ctx.send(file=discord.File(open("./images/barbaric.png",mode="rb"),filename="barbaric.png"))

    @commands.command(brief="Makes Mario 64 Text")
    async def mario(self, ctx, *, text : str):
        await ctx.send(c.mario(text))

    @commands.command(brief="E l o n g a t e s text")
    async def elongate(self, ctx, *, text : str):
        await ctx.send(c.elongate(text))

    @commands.command(brief="Turns text into binary")
    async def bin(self, ctx, *, text : str):
        await ctx.send(c.bin(text))

    @commands.command(brief="Ｍａｋｅｓ   ｔｅｘｔ   ｆｕｌｌｗｉｄｔｈ")
    async def fullwidth(self, ctx, *, text : str):
        await ctx.send(c.fullwidth(text))

    @commands.command(brief="Turns text into wingdings (🕈✋☠☝👎✋☠☝💧)")
    async def dings(self, ctx, *, text : str):
        await ctx.send("```" + "\n" + c.dings(text) + "\n```")

    @commands.command(brief="Randomly applies other text manipulation commands")
    async def mash(self, ctx, *, text : str):
        await ctx.send(c.mash(text))

    @commands.command(brief="Reveres text")
    async def reverse(self, ctx, *, text : str):
        await ctx.send(c.reverse(text))

    @commands.command(brief="Converts text into the NATO Phonetic Alphabet")
    async def nato(self, ctx, *, text : str):
        await ctx.send(c.nato(text))

    @commands.command(brief="Turns binary to text")
    async def unbin(self, ctx, *, text : str):
        try:
            msg = c.unbin(text)
            await ctx.send(msg)
        except ValueError:
            await ctx.send("Uh oh! You friccin moron! That's not valid binary!")

    @commands.command(brief="Randomly scrambles text")
    async def scramble(self, ctx, *, text : str):
        await ctx.send(c.scramble(text))

    @commands.command(brief="Turns text into hexadecimal")
    async def hex(self, ctx, *, text : str):
        await ctx.send(c.hex(text))

    @commands.command(brief="Turns hexadecimal into text")
    async def unhex(self, ctx, *, text : str):
        await ctx.send(c.unhex(text))

    @commands.command(brief="𝕮𝔬𝔫𝔳𝔢𝔯𝔱𝔰 𝔱𝔢𝔵𝔱 𝔱𝔬 𝔉𝔯𝔞𝔨𝔱𝔲𝔯")
    async def fraktur(self, ctx, *, text : str):
        await ctx.send(c.fraktur(text))

    @commands.command(brief="ℂ𝕠𝕟𝕧𝕖𝕣𝕥𝕤 𝕥𝕖𝕩𝕥 𝕥𝕠 𝕓𝕝𝕒𝕔𝕜𝕓𝕠𝕒𝕣𝕕 𝕓𝕠𝕝𝕕")
    async def blackboard(self, ctx, *, text : str):
        await ctx.send(c.blackboard(text))

    @commands.command(brief="𝒞ℴ𝓃𝓋ℯ𝓇𝓉𝓈 𝓉ℯ𝓍𝓉 𝓉ℴ 𝒻𝒶𝓃𝒸𝓎 𝓈𝒸𝓇𝒾𝓅𝓉")
    async def script(self, ctx, *, text : str):
        await ctx.send(c.script(text))

    @commands.command(brief="Creates random text of a given length")
    async def cthulu(self, ctx, length : int):
        await ctx.send(c.cthulu(length))

    @commands.command(brief="Encrypts text using a Rotation Cipher")
    async def rot(self, ctx, shift : int, *, text : str):
        await ctx.send(c.rot(text,shift))

    @commands.command(brief="Encrypts text using a Vigenere Cipher")
    async def vigenere(self, ctx, key : str, *, text : str):
        await ctx.send(c.vigenere(text,key))

    @commands.command(brief="Adds random spaces to text")
    async def randspace(self, ctx, *, text):
        await ctx.send(c.randspace(text))

    @commands.command(brief="Chain text commands together",aliases=["text"])
    async def chain(self,ctx,*, text):
        try:
            await ctx.send(c.chain(text))
        except c.BadArguments:
            await ctx.send("Uh oh! You friccin moron! Your arguments are wrong!")
        except c.NoCommand:
            await ctx.send("Uh oh! You friccin moron! You tried to chain a command that doesn't exist!")

def setup(bot):
    bot.add_cog(Text(bot))