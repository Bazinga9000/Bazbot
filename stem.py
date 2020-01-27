import discord
from discord.ext import commands
from random import *
from sympy import *
from sympy import core
import cmath
import colorsys
import matplotlib.pyplot as plt
from mpmath import cplot
import re
import pint
import math
import numpy
import scipy
from scipy import special
from scipy import misc
from decimal import Decimal
import asyncio
ureg = pint.UnitRegistry("./units.txt")

import rpn_math
import importlib

x, t, z, nu = symbols('x t z nu')
e = math.e
pi = math.pi


mods = ["numpy","math"]


molarmasses = [1.01, 4.0, 6.94, 9.01, 10.81, 12.01, 14.01, 16.0, 19.0, 20.18, 22.99, 24.3, 26.98, 28.09, 30.97, 32.06,
               35.45, 39.95, 39.1, 40.08, 44.96, 47.87, 50.94, 52.0, 54.94, 55.84, 58.93, 58.69, 63.55, 65.38, 69.72,
               72.63, 74.92, 78.97, 79.9, 83.8, 85.47, 87.62, 88.91, 91.22, 92.91, 95.95, 98.0, 101.07, 102.91, 106.42,
               107.87, 112.41, 114.82, 118.71, 121.76, 127.6, 126.9, 131.29, 132.91, 137.33, 138.91, 140.12, 140.91,
               144.24, 145.0, 150.36, 151.96, 157.25, 158.93, 162.5, 164.93, 167.26, 168.93, 173.04, 174.97, 178.49,
               180.95, 183.84, 186.21, 190.23, 192.22, 195.08, 196.97, 200.59, 204.38, 207.2, 208.98, 209.0, 210.0,
               222.0, 223.0, 226.0, 227.0, 232.04, 231.04, 238.03, 237.0, 244.0, 243.0, 247.0, 247.0, 251.0, 252.0,
               257.0, 258.0, 259.0, 266.0, 267.0, 268.0, 269.0, 270.0, 269.0, 278.0, 281.0, 282.0, 285.0, 286.0,
               289.0, 289.0, 293.0, 294.0, 294.0]
elems = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al',
    'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe',
    'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr',
    'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn',
    'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm',
    'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W',
    'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn',
    'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf',
    'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds',
    'Rg', 'Cn', 'Nh', 'Fl', 'Ms', 'Lv', 'Ts', 'Og']

def formulaparenremover(formula):
    parengroups = [""]

    parens = False

    text = formula

    if "(" not in text: return text

    for char in text:
        if char == "(":
            parens = True
        elif char == ")":
            parens = False

        if parens:
            parengroups[-1] += char
        else:
            if parengroups[-1] != "":
                if re.match(r'[0-9]', char) or char == ")":
                    parengroups[-1] += char
                else:
                    parengroups.append("")


    uppg = parengroups[:]

    for i in range(len(parengroups)):
        g = parengroups[i]

        gs = g.rsplit(")",1)

        gc = gs[0][1:]

        try:
            gm = gs[1]
        except:
            gm = "1"

        parengroups[i] = "(" + formulaparenremover(gc) + ")" + gm


    for i in range(len(parengroups)):
        group = parengroups[i]
        ogroup = uppg[i]

        text = text.replace(ogroup, "")

        split = group.split(")")
        compound = split[0].replace("(", "")
        try:
            mult = int(split[1])
        except:
            mult = 1

        text += compound * mult

    return text

def getcomps(compound):
    comp = formulaparenremover(compound)

    comp = re.sub(r'(\(.+\))([0-9]+)', r'\1 * int(\2)', comp)
    tuple = re.findall(r'([A-Z][a-z]*)(\d*)', comp)

    for i in range(len(tuple)):
        j = tuple[i]

        if j[1] == "":
            tuple[i] = (j[0], 1)
        else:
            tuple[i] = (j[0], int(j[1]))

    complists = []

    for part in tuple:
        if part[0] in [i[0] for i in complists]:
            complists[[i[0] for i in complists].index(part[0])][1] += part[1]
        else:
            complists.append([part[0], part[1]])

    return complists


class Stem(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        importlib.reload(rpn_math)


    @commands.command(brief="Factors numbers")
    async def factor(self, ctx, n : int):

        x = factorint(n,15000)

        exponents = {"1" : "¹", "2" : "²", "3" : "³", "4" : "⁴", "5" : "⁵",
                         "6" : "⁶", "7" : "⁷", "8" : "⁸", "9" : "⁹", "0" : "⁰"}

        exponentify = lambda x: "".join([exponents[i] for i in str(x)]) if str(x) != "1" else ""

        factors = sorted(x.items())

        strings = [str(f[0]) + exponentify(f[1]) for f in factors]

        answers = "`" +  " * ".join(strings) + "`"

        if not isprime(max(x)):
            answers += " *(Warning! Last term not factored!)*"

        await ctx.send(answers)


    @commands.command(brief="Convert Units")
    async def convert(self, ctx, num : float, original : str, new : str):
        try:
            x = Decimal(num) * ureg(original)

            try:
                y = x.to(new)
                await ctx.send(y)
            except pint.UndefinedUnitError:
                await ctx.send("Uh oh! You friccin moron! `" + new + "` isn't a unit!")
            except:
                await ctx.send("Uh oh! You friccin moron! You can't convert `" + original + "` to `" + new + "`!")
        except pint.UndefinedUnitError:
            await ctx.send("Uh oh! You friccin moron! `" + original + "` isn't a unit!")

    @commands.command(brief="Get the Molar Mass of a Compound")
    async def molarmass(self, ctx, compound):

        complists = getcomps(compound)

        molarmass = 0

        if complists == []:
            await ctx.send("Uh oh! You friccin moron! `" + compound + "` isn't an element!")
            return

        for e in complists:
            try:
                molarmass += (molarmasses[elems.index(e[0])]) * e[1]
            except:
                await ctx.send("Uh oh! You friccin moron! `" + e[0] + "` isn't an element!")
                return


        await ctx.send("The Molar Mass of `" + compound.replace("`","").replace("*","") + "` is **" + str(round(molarmass, 2)) + "** grams per mol.")


    @commands.command(brief="Get the mass of a certain amount of a compound, in grams.")
    async def massof(self,ctx, moles : float,compound):
        complists = getcomps(compound)

        molarmass = 0

        if complists == []:
            await ctx.send("Uh oh! You friccin moron! `" + compound + "` isn't an element!")
            return

        for e in complists:
            try:
                molarmass += (molarmasses[elems.index(e[0])]) * e[1]
            except:
                await ctx.send("Uh oh! You friccin moron! `" + e[0] + "` isn't an element!")
                return


        molarmass = round(molarmass,2)

        mass = molarmass * moles

        await ctx.send("The Mass of `" + str(moles) + " mol` of `" + compound + "` is `" + str(mass) + "g`")



    @commands.command(brief="Do math!")
    async def math(self,ctx, *, expr):

        if expr in ["list","listops","operators","oplist"]:
            oplist = self.operators[:-1]
            oplist = [o[0] for o in oplist]
            for op in ["-u","^-","**-"]:
                oplist.remove(op)
            return await ctx.send("```\n" + " ".join(oplist) + "\n```")


        try:
            loop = asyncio.get_event_loop()
            coroutine = loop.run_in_executor(None, rpn_math.evaluate_expr, expr)
            task = asyncio.wait_for(coroutine, 5)
            answer = await task

            if len(answer) == 1:
                await ctx.send(rpn_math.format_answer(answer.pop()))
            elif len(answer) > 1:
                await ctx.send("**More than one number left on the stack.**\n" + ", ".join([rpn_math.format_answer(i) for i in answer]))
            else:
                await ctx.send("**Nothing on the stack.**")

        except asyncio.TimeoutError:
            await ctx.send("Uh oh! You friccin moron! That took too long to evaluate!")
        except ZeroDivisionError:
            await ctx.send("Uh oh! You friccin moron! You tried to divide by zero!")
        except OverflowError:
            await ctx.send("∞")
        except rpn_math.BadType as e:
            await ctx.send("Uh oh! You friccin moron! " + str(e))
        except rpn_math.TooManyArguments as e:
            await ctx.send("Uh oh! You friccin moron! " + str(e))
        except ValueError:
            await ctx.send("Uh oh! You friccin moron! You tried an operation that's undefined!")
        except IndexError:
            await ctx.send("Uh oh! You friccin moron! Your operations have the wrong number of arguments!")
        except rpn_math.BadArgument as e:
            return await ctx.send("Uh oh! You friccin moron! " + str(e) + " is an invalid operator!")
        except rpn_math.ThreatOnMyLife as e:
            return await ctx.send(str(e))



    '''
    @commands.command(brief="Graphs your functions for you [Args: x scale, y scale, functions (separated by \"|\")]")
    async def graph(self, ctx, xs : float, ys : float, *, functions):
        plt.style.use('dark_background')

        fig, ax = plt.subplots()

        x = symbols("x")

        arr = np.linspace(-1 * xs, 1 * xs, 100000)
        ax.set_ylim(-1 * ys, 1 * ys)

        inf_threshold = 10 * ys

        for f in functions:
            g = f.replace("e", "2.718281828459045")
            g = g.replace("pi", "3.141592653589793")
            l = lambdify(x, sympify(g), modules=mods)

            out = np.array(l(arr))

            out[out > inf_threshold] = np.inf
            out[out < -inf_threshold] = -1 * np.inf

            plt.plot(arr, out)

        string = "Graph of: " + ", ".join([i.replace(" ", "") for i in functions])
        ax.set(title=string)
        ax.grid()

        fig.savefig("output.png")
        self.bot.upload("output.png")
    '''

def setup(bot):
    bot.add_cog(Stem(bot))