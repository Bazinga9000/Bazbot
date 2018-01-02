import discord
from discord.ext import commands
import Botzinga_9000.FastMandelbrot as md
from random import *
from sympy import *
import numpy as np
import cmath
import colorsys
import matplotlib.pyplot as plt
from mpmath import cplot
import re
import pint
import shlex
import math
import numpy

ureg = pint.UnitRegistry()


x, t, z, nu = symbols('x t z nu')
e = math.e
pi = math.pi


mods = ["numpy","math"]


molarmasses = [1.01, 4.0, 6.94, 9.01, 10.81, 12.01, 14.01, 16.0, 19.0, 20.18, 22.99, 24.3, 26.98, 28.09, 30.97, 32.06, 35.45, 39.95, 39.1, 40.08, 44.96, 47.87, 50.94, 52.0, 54.94, 55.84, 58.93, 58.69, 63.55, 65.38, 69.72, 72.63, 74.92, 78.97, 79.9, 83.8, 85.47, 87.62, 88.91, 91.22, 92.91, 95.95, 98.0, 101.07, 102.91, 106.42, 107.87, 112.41, 114.82, 118.71, 121.76, 127.6, 126.9, 131.29, 132.91, 137.33, 138.91, 140.12, 140.91, 144.24, 145.0, 150.36, 151.96, 157.25, 158.93, 162.5, 164.93, 167.26, 168.93, 173.04, 174.97, 178.49, 180.95, 183.84, 186.21, 190.23, 192.22, 195.08, 196.97, 200.59, 204.38, 207.2, 208.98, 209.0, 210.0, 222.0, 223.0, 226.0, 227.0, 232.04, 231.04, 238.03, 237.0, 244.0, 243.0, 247.0, 247.0, 251.0, 252.0, 257.0, 258.0, 259.0, 266.0, 267.0, 268.0, 269.0, 270.0, 269.0, 278.0, 281.0, 282.0, 285.0, 286.0, 289.0, 289.0, 293.0, 294.0, 294.0]
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

class MismatchedParenthesis(Exception):
    pass

class BadArgument(Exception):
    def __init__(self,value):
        self.value = value

    def __str__(self):
        return str(self.value)

class NoComplex(Exception):
    def __init__(self,value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Stem():
    def __init__(self,bot):
        self.bot = bot
        self.cmaps = ['Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r', 'BuPu', 'BuPu_r', 'CMRmap',
         'CMRmap_r', 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Greens', 'Greens_r', 'Greys', 'Greys_r', 'OrRd', 'OrRd_r',
         'Oranges', 'Oranges_r', 'PRGn', 'PRGn_r', 'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r', 'Pastel2', 'Pastel2_r',
         'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn', 'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r', 'PuRd', 'PuRd_r', 'Purples',
         'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r', 'RdPu', 'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r',
         'Reds', 'Reds_r', 'Set1', 'Set1_r', 'Set2', 'Set2_r', 'Set3', 'Set3_r', 'Spectral', 'Spectral_r', 'Vega10',
         'Vega10_r', 'Vega20', 'Vega20_r', 'Vega20b', 'Vega20b_r', 'Vega20c', 'Vega20c_r', 'Wistia', 'Wistia_r',
         'YlGn', 'YlGnBu', 'YlGnBu_r', 'YlGn_r', 'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 'afmhot', 'afmhot_r',
         'autumn', 'autumn_r', 'binary', 'binary_r', 'bone', 'bone_r', 'brg', 'brg_r', 'bwr', 'bwr_r', 'cool',
         'cool_r', 'coolwarm', 'coolwarm_r', 'copper', 'copper_r', 'cubehelix', 'cubehelix_r', 'flag', 'flag_r',
         'gist_earth', 'gist_earth_r', 'gist_gray', 'gist_gray_r', 'gist_heat', 'gist_heat_r', 'gist_ncar',
         'gist_ncar_r', 'gist_rainbow', 'gist_rainbow_r', 'gist_stern', 'gist_stern_r', 'gist_yarg', 'gist_yarg_r',
         'gnuplot', 'gnuplot2', 'gnuplot2_r', 'gnuplot_r', 'gray', 'gray_r', 'hot', 'hot_r', 'hsv', 'hsv_r',
         'inferno', 'inferno_r', 'jet', 'jet_r', 'magma', 'magma_r', 'nipy_spectral', 'nipy_spectral_r', 'ocean',
         'ocean_r', 'pink', 'pink_r', 'plasma', 'plasma_r', 'prism', 'prism_r', 'rainbow', 'rainbow_r', 'seismic',
         'seismic_r', 'spectral', 'spectral_r', 'spring', 'spring_r', 'summer', 'summer_r', 'tab10', 'tab10_r',
         'tab20', 'tab20_r', 'tab20b', 'tab20b_r', 'tab20c', 'tab20c_r', 'terrain', 'terrain_r', 'viridis',
         'viridis_r', 'winter', 'winter_r']

    @commands.command(brief="Lists colormaps for use with b9!mandelbrot")
    async def listcolormaps(self,ctx):
        await ctx.send(str(self.cmaps))

    @commands.command(brief="Plot the mandelbrot set!")
    @commands.cooldown(1,10,type=commands.BucketType.user)
    async def mandelbrot(self, ctx, cx : float, cy : float, r : float, p : int, colormap : str):
        if colormap == "random":
            cmap = choice(self.cmaps)
        elif colormap not in self.cmaps:
            await ctx.send("Uh oh! You friccin moron! `" + colormap + "` isn't a valid colormap! Use `b9!listcolormaps` to find the colormaps!")
            return
        else:
            cmap = colormap


        try:
            md.render(cx, cy, r, p, cmap)
        except:
            await ctx.send("Uh oh it broke. Go yell at baz.")
            return

        await ctx.send(file=discord.File(open("output.png",mode="rb"),filename="output.png"))

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
            x = num * ureg(original)

            try:
                y = x.to(ureg(new))
                await ctx.send(str(round(y,8)))
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


    def infix_to_postfix(self,tokens):
        ops = [o[0] for o in self.operators]
        precs = [o[1] for o in self.operators]
        assoc = [o[2] for o in self.operators] #true = right associative

        getprec = lambda x: precs[ops.index(x)]
        getassoc = lambda x: assoc[ops.index(x)]


        output = []
        opstack = []

        for token in tokens:
            if token == "(":
                opstack.append("(")
                continue
            elif token == ")":
                while opstack[-1] != "(":
                    output.append(opstack.pop())
                    if len(opstack) == 0: raise MismatchedParenthesis

                opstack.pop()
            elif token in ops:
                if len(opstack) == 0:
                    opstack.append(token)
                    continue

                while len(opstack) != 0:
                    valid = False

                    if getprec(opstack[-1]) > getprec(token): valid = True
                    if not getassoc(token) and getprec(opstack[-1]) == getprec(token): valid = True
                    if opstack[-1] == "(": valid = False

                    if not valid: break


                    output.append(opstack.pop())


                opstack.append(token)

            else:
                try:
                    output.append(complex(token))
                except:
                    raise BadArgument(token)


        for i in range(len(opstack)):
            output.append(opstack.pop())


        return output

    def parserpn(self, rpn):

        stack = []

        for token in rpn:
            if isinstance(token, complex):
                stack.append(token)

            else:
                if token == "+":
                    a = stack.pop()
                    b = stack.pop()
                    stack.append(a+b)

                if token == "-":

                    if len(stack) >= 2:
                        a = stack.pop()
                        b = stack.pop()
                        stack.append(b-a)
                    else:
                        stack.append(-stack.pop())

                if token == "*":
                    a = stack.pop()
                    b = stack.pop()
                    stack.append(a*b)

                if token == "%":
                    a = stack.pop()
                    b = stack.pop()

                    if a.imag != 0 or b.imag != 0:
                        raise NoComplex("%")
                    else:
                        a = a.real
                        b = b.real
                        stack.append(complex(b%a))

                if token == "/":
                    a = stack.pop()
                    b = stack.pop()
                    stack.append(b/a)

                if token == "^":
                    a = stack.pop()
                    b = stack.pop()
                    stack.append(b**a)

                if token == "sqrt":
                    a = stack.pop()
                    stack.append(numpy.sqrt(a))

                if token == "log10":
                    stack.append(cmath.log10(stack.pop()))

                if token == "ln":
                    stack.append(cmath.log(stack.pop()))

                if token == "log":
                    a = stack.pop()
                    b = stack.pop()

                    stack.append(cmath.log(a,b))

                if token == "!":
                    a = stack.pop()

                    if a.imag != 0 :
                        raise NoComplex("!")
                    else:
                        a = a.real
                        stack.append(complex(numpy.math.gamma(a + 1)))

                if token == "sin":
                    stack.append(numpy.sin(stack.pop()))

                if token == "cos":
                    stack.append(numpy.cos(stack.pop()))

                if token == "tan":
                    stack.append(numpy.tan(stack.pop()))

                if token == "csc":
                    stack.append(1 / numpy.sin(stack.pop()))

                if token == "sec":
                    stack.append(1 / numpy.cos(stack.pop()))

                if token == "cot":
                    stack.append(1 / numpy.tan(stack.pop()))

                if token == "asin":
                    stack.append(numpy.arcsin(stack.pop()))

                if token == "acos":
                    stack.append(numpy.arccos(stack.pop()))

                if token == "atan":
                    stack.append(numpy.arctan(stack.pop()))

                if token == "acsc":
                    stack.append(1 / numpy.arcsin(stack.pop()))

                if token == "asec":
                    stack.append(1 / numpy.arccos(stack.pop()))

                if token == "acot":
                    stack.append(1 / numpy.arctan(stack.pop()))

                if token == "sinh":
                    stack.append(numpy.sinh(stack.pop()))

                if token == "cosh":
                    stack.append(numpy.cosh(stack.pop()))

                if token == "tanh":
                    stack.append(numpy.tanh(stack.pop()))

                if token == "csch":
                    stack.append(1 / numpy.sinh(stack.pop()))

                if token == "sech":
                    stack.append(1 / numpy.cosh(stack.pop()))

                if token == "coth":
                    stack.append(1 / numpy.tanh(stack.pop()))

                if token == "asinh":
                    stack.append(numpy.arcsinh(stack.pop()))

                if token == "acosh":
                    stack.append(numpy.arccosh(stack.pop()))

                if token == "atanh":
                    stack.append(numpy.arctanh(stack.pop()))

                if token == "acsch":
                    stack.append(1 / numpy.arcsinh(stack.pop()))

                if token == "asech":
                    stack.append(1 / numpy.arccosh(stack.pop()))

                if token == "acoth":
                    stack.append(1 / numpy.arctanh(stack.pop()))



                if token == "pi":
                    stack.append(numpy.pi)

                if token == "e":
                    stack.append(numpy.e)



        return stack


    def format_answer(self,answer):
        if answer.imag == 0:
            answer = answer.real
            if answer == float(answer): answer = float(answer)
            if answer == int(answer): answer = int(answer)

        return str(answer).replace("j", "i")



    @commands.command(brief="Do math!")
    async def math(self,ctx, *, expr):

        self.operators = [

            #Basic Operators
            ["+",    2, False], #add
            ["-",    2, False], #subtract
            ["*",    3, False], #multiply
            ["/",    3, False], #divide
            ["%",    3, False], #modulo
            ["^",    4, True],  #exponent
            ["**",   4, True],  #also exponent
            ["sqrt", 5, True],  #square root
            ["log10",5, True],  #common log
            ["ln",   5, True],  #natural log
            ["log",  5, True],  #logbase
            ["!",    5, False], #factorial
            #Trig
            ["sin",  5, True],  #sine
            ["cos",  5, True],  #cosine
            ["tan",  5, True],  #tangent
            ["csc",  5, True],  #cosecant
            ["sec",  5, True],  #secant
            ["cot",  5, True],  #cotangent
            #Inverse Trig
            ["asin", 5, True],  # sine
            ["acos", 5, True],  # cosine
            ["atan", 5, True],  # tangent
            ["acsc", 5, True],  # cosecant
            ["asec", 5, True],  # secant
            ["acot", 5, True],  # cotangent
            #Hyperbolic Trig
            ["sinh", 5, True],  #hyperbolic sine
            ["cosh", 5, True],  #hyperbolic cosine
            ["tanh", 5, True],  #hyperbolic tangent
            ["csch", 5, True],  #hyperbolic cosecant
            ["sech", 5, True],  #hyperbolic secant
            ["coth", 5, True],  #hyperbolic cotangent
            #Inverse Hyperbolic Trig
            ["asinh",5, True],  # hyperbolic sine
            ["acosh",5, True],  # hyperbolic cosine
            ["atanh",5, True],  # hyperbolic tangent
            ["acsch",5, True],  # hyperbolic cosecant
            ["asech",5, True],  # hyperbolic secant
            ["acoth",5, True],  # hyperbolic cotangent
            #constants
            ["pi",   7, True],  #constant pi
            ["e",    7, True],  #constant e

            ["(", 9999, True]   #almighty left parenthesis
        ]


        if expr == "list" or expr == "listops":
            return await ctx.send("```\n" + " ".join([o[0] for o in self.operators[:-1]]) + "\n```")

        expression = expr

        for op in sorted([o[0] for o in self.operators],key=lambda x: -len(x)):
            if op != "-":
                expression = expression.replace(op," " + op + " ")

            expression = expression.replace("-"," -")

        expression = expr.replace("(", " ( ").replace(")", " ) ").replace("i", "j").replace(",", " ")


        for op in ["pi","sin","sinh","asin","asinh"]:
            expression = expression.replace(op.replace("i","j"),op)


        tokens = shlex.split(expression)

        try:
            rpn = self.infix_to_postfix(tokens)
        except MismatchedParenthesis:
            return await ctx.send("Uh oh! You friccin moron! You have mismatched parenthesis!")
        except BadArgument as e:
            return await ctx.send("Uh oh! You friccin moron! " + str(e) + " is an invalid operator!")

        #await ctx.send(" ".join([str(i) for i in rpn]))

        try:
            answer = self.parserpn(rpn)

            if len(answer) == 1:
                await ctx.send(self.format_answer(answer.pop()))
            elif len(answer) > 1:
                await ctx.send("**More than one number left on the stack.**\n" + ", ".join([self.format_answer(i) for i in answer]))
            else:
                await ctx.send("**Nothing on the stack.**")

        except ZeroDivisionError:
            await ctx.send("Uh oh! You friccin moron! You tried to divide by zero!")
        except OverflowError:
            await ctx.send("Uh oh! You friccin moron! Your calculation overflowed!")
        except NoComplex as e:
            await ctx.send("Uh oh! You friccin moron! `" + str(e) + "` doesn't support complex numbers!")
        except ValueError:
            await ctx.send("Uh oh! You friccin moron! You tried an operation that's undefined!")



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