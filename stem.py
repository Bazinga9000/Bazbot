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

class TooManyArguments(Exception):
    def __init__(self,op):
        self.op = op

    def __str__(self):
        return str(self.op + " doesn't support that amount arguments!")



class BadArgument(Exception):
    def __init__(self,op):
        self.op = op

    def __str__(self):
        return str(self.op)

class ThreatOnMyLife(Exception):
    def __init__(self,op,value):
        self.op = op
        self.value = value

    def __str__(self):
        return "Your attempt to invoke {} with `{}` as an argument has been detected as a potential threat on my life. Cease such action or be destroyed".format(self.op,self.value)

class BadType(Exception):
    def __init__(self,op,value,type):
        self.op = op
        self.value = value
        self.type = type
        self.typemap = {int : "int", Decimal : "decimal", numpy.complex128 : "complex", complex : "complex",
                        tuple : "tuple"}

    def __str__(self):
        return str(self.op + " doesn't support `" + str(self.typemap[self.type]) + "`! (You gave it `" + str(self.value) + "`)")


class Stem(commands.Cog):
    def __init__(self,bot):
        self.bot = bot


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


    def litparse(self,literal):
        try:
            return int(str(literal)) #int
        except:
            pass

        try:
            return Decimal(str(literal)) #float
        except:
            pass

        try:
            return complex(literal) #complex
        except:
            pass

        return complex(literal.replace("i","j")) #complex with i instead of j

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
                if len(opstack) == 0: raise MismatchedParenthesis
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
                    output.append(self.litparse(token))
                except:
                    raise BadArgument(token)


        for i in range(len(opstack)):
            if opstack[-1] == "(": raise MismatchedParenthesis
            output.append(opstack.pop())


        return output

    def ban(self, op, arg, types):
        if isinstance(arg,types):
            raise BadType(op,arg,type(arg))


    def sympyconvert(self,arg):
        try:
            return Decimal(float(arg))
        except:
            return complex(arg)

    def listify(self, t):
        return list(map(self.listify, t)) if isinstance(t, (list, tuple)) else t

    def parserpn(self, rpn):

        stack = []

        for token in rpn:
            stack = [Decimal(i) if isinstance(i,float) else i for i in stack]

            if token not in [i[0] for i in self.operators]:
                stack.append(token)

            else:
                if token == "+":
                    a = stack.pop()
                    b = stack.pop()
                    stack.append(a + b)

                if token == "-":
                    a = stack.pop()
                    b = stack.pop()
                    stack.append(b - a)

                if token == "-u":
                    stack.append(-stack.pop())

                if token == "*":
                    a = stack.pop()
                    b = stack.pop()
                    if a > 10**1000:
                        raise ThreatOnMyLife("*",a)
                    if b > 10**1000:
                        raise ThreatOnMyLife("*",b)

                    stack.append(a * b)

                if token == "%":
                    a = stack.pop()
                    b = stack.pop()

                    self.ban("%",a,(complex))
                    self.ban("%",b,(complex))

                    stack.append(b % a)

                if token == "/":
                    a = stack.pop()
                    b = stack.pop()
                    stack.append(b / a)

                if token in ["^","**"]:
                    a = stack.pop()
                    b = stack.pop()

                    if isinstance(a,complex):
                        if a.real > 10**100:
                            raise ThreatOnMyLife(token,a)
                    else:
                        if a > 10**100:
                            raise ThreatOnMyLife(token,a)

                    if isinstance(b,complex):
                        if b.real > 200:
                            raise ThreatOnMyLife(token,b)
                    else:
                        if b > 200:
                            raise ThreatOnMyLife(token,b)

                    try:
                        stack.append(math.pow(b,a))
                    except:
                        stack.append(cmath.exp(float(a) * cmath.log(b)))

                if token in ["^-","**-"]:
                    a = stack.pop()
                    b = stack.pop()

                    if isinstance(a,complex):
                        if a.real < -10**100:
                            raise ThreatOnMyLife(token.replace("-",""),-a)
                    else:
                        if a < -10**100:
                            raise ThreatOnMyLife(token.replace("-",""),-a)

                    if isinstance(b,complex):
                        if b.real < -200:
                            raise ThreatOnMyLife(token.replace("-",""),-b)
                    else:
                        if b < -200:
                            raise ThreatOnMyLife(token.replace("-",""),-b)

                    stack.append(math.pow(b,-a))

                if token == "sqrt":
                    a = stack.pop()
                    try:
                        assert not isinstance(a,complex)
                        stack.append(math.sqrt(a))
                    except:
                        stack.append(cmath.sqrt(a))

                if token == "ln":
                    stack.append(cmath.log(stack.pop()))

                if token == "log":
                    a = stack.pop()
                    if isinstance(a,tuple):
                        b = a[0]
                        c = a[1]
                        try:
                            stack.append(math.log(b,c))
                        except:
                            stack.append(cmath.log(b,c))
                    else:
                        try:
                            stack.append(math.log(a))
                        except:
                            stack.append(cmath.log(a))


                if token == ",":
                    a = stack.pop()
                    b = stack.pop()

                    if isinstance(a,tuple):
                        stack.append((b,) + a)
                    else:
                        stack.append((b,a))


                if token == "and":
                    a = stack.pop()
                    b = stack.pop()

                    self.ban("and",a,(complex,Decimal,tuple))
                    self.ban("and",b,(complex,Decimal,tuple))

                    stack.append(int(a) & int(b))

                if token == "xor":
                    a = stack.pop()
                    b = stack.pop()

                    self.ban("xor",a,(complex,Decimal,tuple))
                    self.ban("xor",b,(complex,Decimal,tuple))

                    stack.append(int(a) ^ int(b))

                if token == "or":
                    a = stack.pop()
                    b = stack.pop()

                    self.ban("or",a,(complex,Decimal,tuple))
                    self.ban("or",b,(complex,Decimal,tuple))

                    stack.append(int(a) | int(b))

                if token == "not":
                    a = stack.pop()

                    self.ban("not",a,(complex,Decimal,tuple))

                    stack.append(~int(a))

                if token == "!":
                    a = stack.pop()

                    self.ban("!",a,(complex))

                    if a > 200:
                        raise ThreatOnMyLife("!",a)

                    if isinstance(a,int):
                        stack.append(math.factorial(a))
                    else:
                        stack.append(math.gamma(a + 1))

                if token == "choose":
                    t = stack.pop()

                    a = t[0]
                    b = t[1]

                    self.ban("choose", a, (complex, Decimal))
                    self.ban("choose", b, (complex, Decimal))

                    stack.append(scipy.misc.comb(a,b,exact=True))

                if token == "perm":
                    t = stack.pop()

                    a = t[0]
                    b = t[1]

                    self.ban("perm", a, (complex, Decimal))
                    self.ban("perm", b, (complex, Decimal))

                    stack.append(scipy.special.perm(a,b,exact=True))

                if token == "sin":
                    stack.append(math.sin(stack.pop()))

                if token == "cos":
                    stack.append(math.cos(stack.pop()))

                if token == "tan":
                    stack.append(math.tan(stack.pop()))

                if token == "csc":
                    stack.append(1 / math.sin(stack.pop()))

                if token == "sec":
                    stack.append(1 / math.cos(stack.pop()))

                if token == "cot":
                    stack.append(1 / math.tan(stack.pop()))

                if token == "deg":
                    a = stack.pop()
                    self.ban("deg", a, (complex))

                    stack.append(math.radians(a))

                if token == "rad":
                    a = stack.pop()
                    self.ban("rad", a, (complex))

                    stack.append(math.degrees(a))

                if token == "asin":
                    stack.append(math.asin(stack.pop()))

                if token == "acos":
                    stack.append(math.asin(stack.pop()))

                if token == "atan":
                    stack.append(math.asin(stack.pop()))

                if token == "acsc":
                    stack.append(math.asin(1 / stack.pop()))

                if token == "asec":
                    stack.append(math.acos(1 / stack.pop()))

                if token == "acot":
                    stack.append(math.atan(1 / stack.pop()))

                if token == "sinh":
                    stack.append(math.sinh(stack.pop()))

                if token == "cosh":
                    stack.append(math.cosh(stack.pop()))

                if token == "tanh":
                    stack.append(math.tanh(stack.pop()))

                if token == "csch":
                    stack.append(1 / math.sinh(stack.pop()))

                if token == "sech":
                    stack.append(1 / math.cosh(stack.pop()))

                if token == "coth":
                    stack.append(1 / math.tanh(stack.pop()))

                if token == "asinh":
                    stack.append(math.asinh(stack.pop()))

                if token == "acosh":
                    stack.append(math.acosh(stack.pop()))

                if token == "atanh":
                    stack.append(math.atanh(stack.pop()))

                if token == "acsch":
                    stack.append(math.asinh(1 / stack.pop()))

                if token == "asech":
                    stack.append(math.acosh(1 / stack.pop()))

                if token == "acoth":
                    stack.append(math.atanh(1 / stack.pop()))

                if token == "swap":
                    a = stack.pop()
                    b = stack.pop()
                    stack.append(a)
                    stack.append(b)

                if token == "drop":
                    stack.pop()

                if token == "flat":
                    a = stack.pop()
                    self.ban("flat",a,(complex,Decimal,int))

                    for i in a:
                        stack.append(i)

                if token == "solve":
                    x = Symbol('x')
                    a = stack.pop()

                    self.ban("solve",a,(complex,Decimal,int))

                    polynomial = 0

                    if len(a) > 10: raise TooManyArguments("solve")

                    t = reversed(a)

                    for degree,coeff in enumerate(t):
                        polynomial += coeff * (x ** degree)

                    solns = solve(polynomial,x)
                    solns = [self.sympyconvert(N(i)) for i in solns]
                    stack.append(tuple(solns))

                if token == "pi":
                    stack.append(numpy.pi)

                if token == "e":
                    stack.append(numpy.e)


                if token == "[":
                    a = stack.pop()

                    if isinstance(a,tuple):
                        a = [i for i in a]
                    else:
                        a = [a]

                    print([type(i) for i in a])
                    stack.append(numpy.array(self.listify(a)))

                if token == ";":
                    a = stack.pop()
                    b = stack.pop()

                    print(a,b)

                    if isinstance(b,tuple):
                        a = tuple(a)
                        b = tuple(b)
                        if isinstance(b[0],tuple):
                            b = list(b)
                            b.append(a)
                            stack.append(tuple(b))
                        else:
                            stack.append((b,a))
                    else:
                        stack.append(((b,), (a,)))


                if token == "T":
                    stack.append(numpy.transpose(stack.pop()))

                if token == "det":
                    stack.append(numpy.linalg.det(stack.pop()))

                if token == "lsolve":
                    t = stack.pop()
                    a = t[0]
                    b = t[1]
                    solns = numpy.linalg.solve(a,b)
                    stack.append([[self.litparse(i[0])] for i in solns])




        return stack

    def format_answer(self,answer):
        print(type(answer))
        if isinstance(answer,tuple): return str(tuple([self.format_answer(i) for i in answer])).replace("'","")
        if type(answer) in [list,numpy.array,numpy.ndarray]:
            return "[" + " ".join([self.format_answer(i) for i in answer]).replace("'","") + "]"
        if isinstance(answer,complex):
            if answer.imag == 0:
                return self.format_answer(Decimal(answer.real))
            else:
                return str(answer).replace("j","i")[1:-1]
        if answer == int(answer):
            return str(int(answer))
        else:
            return str(answer)

    def partition(self,string,op):
        parts = list(string.partition(op))

        for i in range(len(string)):
            parts[-1] = list(parts[-1].partition(op))
            parts = flatten(parts)

        return parts


    @commands.command(brief="Do math!")
    async def math(self,ctx, *, expr):

        self.operators = [

            #Basic Operators
            ["+",     5, False], #add
            ["-",     5, False], #subtract
            ["-u",  6.5, False], #unary subtract   (lower than exp)
            ["*",     6, False], #multiply
            ["/",     6, False], #divide
            ["%",     6, False], #modulo
            ["^",     8, True],  #exponent
            ["**",    8, True],  #also exponent
            ["^-",    8, True],  #exponent, but the power is negative (really hacky but it works)
            ["**-",   8, True],  #see above
            ["sqrt",  9, True],  #square root
            ["ln",    9, True],  #natural log
            ["log",   9, True],  #logbase
            [",",     1, True],  #comma (for tuple creation)


            #logical operators
            ["and",   4, False], #bitwise and
            ["xor",   3, False], #bitwise xor
            ["or",    2, False], #bitwise or
            ["not",   7, False], #bitwise not
            #combinatorics
            ["!",     9, True],  #factorial
            ["choose",9, True],  #n choose k
            ["perm",  9, True],  #n perm k

            #Trig
            ["sin",   9, True],  #sine
            ["cos",   9, True],  #cosine
            ["tan",   9, True],  #tangent
            ["csc",   9, True],  #cosecant
            ["sec",   9, True],  #secant
            ["cot",   9, True],  #cotangent
            ["deg",   9, True],  #convert to radians
            ["rad",   9, True],  #convert to degrees
            #Inverse Trig
            ["asin",  9, True],  # sine
            ["acos",  9, True],  # cosine
            ["atan",  9, True],  # tangent
            ["acsc",  9, True],  # cosecant
            ["asec",  9, True],  # secant
            ["acot",  9, True],  # cotangent
            #Hyperbolic Trig
            ["sinh",  9, True],  #hyperbolic sine
            ["cosh",  9, True],  #hyperbolic cosine
            ["tanh",  9, True],  #hyperbolic tangent
            ["csch",  9, True],  #hyperbolic cosecant
            ["sech",  9, True],  #hyperbolic secant
            ["coth",  9, True],  #hyperbolic cotangent
            #Inverse Hyperbolic Trig
            ["asinh", 9, True],  #hyperbolic sine
            ["acosh", 9, True],  #hyperbolic cosine
            ["atanh", 9, True],  #hyperbolic tangent
            ["acsch", 9, True],  #hyperbolic cosecant
            ["asech", 9, True],  #hyperbolic secant
            ["acoth", 9, True],  #hyperbolic cotangent
            #special
            ["solve", 9, True],  #solve any polynomial
            #stack operations
            ["swap", 10, True],  #swap first two elements on stack
            ["drop", 10, True],  #drop bottom element
            ["flat", 10, True],  #flatten a tuple


            # matrix ops
            [";",     0, False], #semicolon (for multidimensional tuple creation)
            ["T",     9, False], #transpose
            ["det",   9, False], #determinant
            ["lsolve",9, False], #solve systems of linear eq
            #constants
            ["pi",   11, True],  #constant pi
            ["e",    11, True],  #constant e

            ["[",  9998, True],  #slightly less mighty left bracket
            ["(",  9999, True]   #almighty left parenthesis
        ]


        if expr in ["list","listops","operators","oplist"]:
            oplist = self.operators[:-1]
            oplist = [o[0] for o in oplist]
            for op in ["-u","^-","**-"]:
                oplist.remove(op)
            return await ctx.send("```\n" + " ".join(oplist) + "\n```")


        ops = sorted([o[0] for o in self.operators],key=lambda x: -len(x))
        ops.append(")")

        tokens = [expr.replace(" ","").replace("[","[(").replace("]",")")]


        for op in ops:
            tokens = flatten([self.partition(t,op) if t not in ops else t for t in tokens])
            tokens = [i for i in tokens if i != ""]
        tokens = [i for i in tokens if i != ""]

        tokens = [token.replace("i","j") if token not in ops else token for token in tokens]


        #negative handling
        for i in range(len(tokens)-1,-1,-1):
            token = tokens[i]

            if token == "-":
                if i == 0:
                    tokens[0] = "-u"
                else:
                    nexttoken = tokens[i+1]
                    prevtoken = tokens[i-1]
                    if prevtoken != ")":
                        if prevtoken in ops:
                            tokens[i] = "-u"
                            tokens[i] = tokens[i+1]
                            tokens[i+1] = "-u"




        #print(tokens)
        #await ctx.send(" ".join(tokens)) #PRINT TOKENS

        try:
            rpn = self.infix_to_postfix(tokens)
        except MismatchedParenthesis:
            return await ctx.send("Uh oh! You friccin moron! You have mismatched parenthesis!")


        #await ctx.send(" ".join([str(i) for i in rpn])) #PRINT RPN

        try:
            loop = asyncio.get_event_loop()
            coroutine = loop.run_in_executor(None, self.parserpn, rpn)
            task = asyncio.wait_for(coroutine, 5)
            try:
                answer = await task
            except BadArgument as e:
                return await ctx.send("Uh oh! You friccin moron! " + str(e) + " is an invalid operator!")
            except ThreatOnMyLife as e:
                return await ctx.send(str(e))

            if len(answer) == 1:
                await ctx.send(self.format_answer(answer.pop()))
            elif len(answer) > 1:
                await ctx.send("**More than one number left on the stack.**\n" + ", ".join([self.format_answer(i) for i in answer]))
            else:
                await ctx.send("**Nothing on the stack.**")
        except asyncio.TimeoutError:
            await ctx.send("Uh oh! You friccin moron! That took too long to evaluate!")
        except ZeroDivisionError:
            await ctx.send("Uh oh! You friccin moron! You tried to divide by zero!")
        except OverflowError:
            await ctx.send("Uh oh! You friccin moron! Your calculation overflowed!")
        except BadType as e:
            await ctx.send("Uh oh! You friccin moron! " + str(e))
        except TooManyArguments as e:
            await ctx.send("Uh oh! You friccin moron! " + str(e))
        except ValueError:
            await ctx.send("Uh oh! You friccin moron! You tried an operation that's undefined!")
        except IndexError:
            await ctx.send("Uh oh! You friccin moron! Your operations have the wrong number of arguments!")



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