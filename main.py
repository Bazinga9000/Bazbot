from discord.ext import commands
import re as rgx
import discord
from io import TextIOWrapper, BytesIO
import sys,traceback

#for eval() and exec()
from random import *
from sympy import *
import math

x, t, z, nu = symbols('x t z nu')
e = math.e
pi = math.pi


owner = lambda ctx: ctx.author.id == 137001076284063744
tracebackt = True


description = '''Bazinga_9000's Fancy Robot
It does cool things I guess,
Get rekt milo.
'''

# this specifies what extensions to load when the bot starts up
startup_extensions = ["textmanipulation","stem","misc","tags","boardgame","uno","dos"]

bot = commands.Bot(command_prefix='b9!', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')




def gettraceback(exception):
    if not tracebackt: return
    lines = traceback.format_exception(type(exception), exception, exception.__traceback__)
    print(''.join(lines))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send("You can't do that!")
    elif isinstance(error, commands.errors.CommandOnCooldown):
        return await ctx.send(ctx.author.name + ", you need to put a handle on your stallions. This command can only be used every " + str(error.cooldown.per) + "sec!")
    elif isinstance(error, commands.errors.CommandNotFound):
        pass
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        e = str(error)
        arg = e.split(" ")[0]

        await ctx.send("Uh oh! You friccin moron! You forgot the `" + arg + "`!")
    elif isinstance(error, commands.UserInputError):
        e = ' '.join(error.args)
        error_data = rgx.findall('Converting to \"(.*)\" failed for parameter \"(.*)\"\.', e)
        if not error_data:
            await ctx.send('Error: {}'.format(' '.join(error.args)))
            gettraceback(error)
        else:
            await ctx.send("Uh oh! You friccin moron! `{1}` isn't an `{0}`!".format(*error_data[0]))
    elif isinstance(error, commands.CommandInvokeError):
        o = error.original
        so = str(o)
        if isinstance(o,discord.HTTPException):
            if "Must be 2000 or fewer in length" in so:
                await ctx.send("Uh oh! You friccin moron! That message is too long!")
            elif "FORBIDDEN" in so:
                await ctx.send("Uh oh! I don't have permissions for this!")
        else:
            await ctx.send("Error: {}".format(' '.join(error.args)))
            gettraceback(error)
    else:
        await ctx.send("Error: {}".format(' '.join(error.args)))
        gettraceback(error)


@bot.command()
@commands.check(owner)
async def toggletb(ctx):
    global tracebackt
    if tracebackt:
        tracebackt = False
        await ctx.send("Traceback has been turned off!")
    else:
        tracebackt = True
        await ctx.send("Traceback has been turned on!")

@bot.command()
@commands.check(owner)
async def load(ctx, extension_name : str):
    """Loads an extension."""

    try:
        bot.load_extension(extension_name)
        await ctx.send("{} loaded.".format(extension_name))
    except (AttributeError, ImportError) as e:
        await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return

@bot.command()
@commands.check(owner)
async def unload(ctx, extension_name : str):
    """Unloads an extension."""

    try:
        bot.unload_extension(extension_name)
        await ctx.send("{} unloaded.".format(extension_name))
    except:
        return

@bot.command(brief="Reload all the commands")
@commands.check(owner)
async def reload(ctx):


    excount = len(startup_extensions)
    loaded = 0
    for extension in startup_extensions:
        try:
            bot.unload_extension(extension)
            bot.load_extension(extension)
            loaded += 1
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    await ctx.send(str(loaded) + "/" + str(excount) + " Extensions Reloaded.")


@bot.command(name="eval",brief="evaluate some code")
@commands.check(owner)
async def _eval(ctx,*,code : str):

    try:
        ans = eval(code)
        error = 0
    except Exception as err:
        error = 1
        ans = str(err)
    finally:

        embed = discord.Embed(color=[0x00ff00,0xff0000][error])
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Code", value=("```Python\n" + code + "\n```")
        , inline = False)
        embed.add_field(name=["Result","Error"][error], value=("```\n" + str(ans) + "\n```")
        , inline = True)
        await ctx.send(embed=embed)

@bot.command(name="exec",brief="execute some code")
@commands.check(owner)
async def _exec(ctx,*,code : str):

    text = code

    if code.startswith("```Python"):
        text = text.replace("```Python","```")

    text = text[:-3]

    lines = text.split("```")[1].splitlines()
    runningcode = "\n".join(lines)[1:]

    # setup the environment
    old_stdout = sys.stdout
    sys.stdout = TextIOWrapper(BytesIO(), sys.stdout.encoding)

    # do something that writes to stdout or stdout.buffer

    try:
        exec(runningcode)
        sys.stdout.seek(0)  # jump to the start
        ans = sys.stdout.read()  # read output
        error = 0
    except Exception as e:
        ans = str(e)
        error = 1
    finally:
        # restore stdout
        sys.stdout.close()
        sys.stdout = old_stdout

        embed = discord.Embed(color=[0x00ff00,0xff0000][error])
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Code", value=("```Python\n" + runningcode + "\n```")
        , inline = False)
        embed.add_field(name=["Result","Error"][error], value=("```\n" + str(ans) + "\n```")
        , inline = True)
        await ctx.send(embed=embed)


if __name__ == "__main__":

    bot.remove_command('help')

    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

with open("token.txt") as file:
    token = file.read()
bot.run(token)