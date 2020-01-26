import numpy, scipy, sympy
import math

numpy.seterr(over="raise",under="raise")

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

class BadType(Exception):
    def __init__(self,op,value,type):
        self.op = op
        self.value = value
        self.type = type
        self.typemap = {int : "int", numpy.float64 : "float", numpy.complex128 : "complex", complex : "complex",
                        tuple : "tuple"}

    def __str__(self):
        return str(self.op + " doesn't support `" + str(self.typemap[self.type]) + "`! (You gave it `" + str(self.value) + "`)")


class ThreatOnMyLife(Exception):
    def __init__(self,op,value):
        self.op = op
        self.value = value

    def __str__(self):
        return "Your attempt to invoke {} with `{}` as an argument has been detected as a potential threat on my life. Cease such action or be destroyed".format(self.op,self.value)


def litparse(literal):
    try:
        return int(literal)  # int
    except:
        pass

    try:
        float(literal) #throws exception if the value is actually a complex number
        return numpy.fromstring(str(literal),dtype=numpy.float64,sep=" ")[0]  # float
    except:
        pass

    try:
        #this is always a pure imaginary number, so i can resort to this hacky bullshit
        if literal == "j": return numpy.complex128(0+1j)
        return numpy.multiply(numpy.fromstring(str(literal),dtype=numpy.float64,sep=" ")[0],0+1j)  # complex
    except:
        raise BadArgument(literal)


operators = [
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

def flatten(l):
    flist = []

    for i in l:
        if isinstance(i,list):
            for j in flatten(i):
                flist.append(j)
        else:
            flist.append(i)

    return flist

def partition(string, op):
    parts = list(string.partition(op))

    for i in range(len(string)):
        parts[-1] = list(parts[-1].partition(op))
        parts = flatten(parts)

    return parts


def tokenize(expr):
    ops = sorted([o[0] for o in operators], key=lambda x: -len(x))
    ops.append(")")

    tokens = [expr.replace(" ", "").replace("[", "[(").replace("]", ")")]

    for op in ops:
        tokens = flatten([partition(t, op) if t not in ops else t for t in tokens])
        tokens = [i for i in tokens if i != ""]
    tokens = [i for i in tokens if i != ""]

    tokens = [token.replace("i", "j") if token not in ops else token for token in tokens]

    # negative handling
    for i in range(len(tokens) - 1, -1, -1):
        token = tokens[i]

        if token == "-":
            if i == 0:
                tokens[0] = "-u"
            else:
                nexttoken = tokens[i + 1]
                prevtoken = tokens[i - 1]
                if prevtoken != ")":
                    if prevtoken in ops:
                        tokens[i] = "-u"
                        tokens[i] = tokens[i + 1]
                        tokens[i + 1] = "-u"

    return tokens


def tokens_to_postfix(tokens):
    ops = [o[0] for o in operators]
    precs = [o[1] for o in operators]
    assoc = [o[2] for o in operators]  # true = right associative

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
                output.append(litparse(token))
            except:
                raise BadArgument(token)

    for i in range(len(opstack)):
        if opstack[-1] == "(": raise MismatchedParenthesis
        output.append(opstack.pop())

    return output

def to_rpn(expr):
    return tokens_to_postfix(tokenize(expr))


def limit(op,value,threshold,is_upper_bound):
    comp = numpy.float64(value) if type(value) in [int,t_float] else numpy.abs(value) * numpy.sign(value.real)

    if is_upper_bound:
        flag = comp > numpy.float64(threshold)
    else:
        flag = comp < numpy.float64(threshold)

    if flag:
        raise ThreatOnMyLife(op,value)

def blacklist(op, value, typelist):
    for t in typelist:
        if isinstance(value,t):
            raise BadType(op,value,type(value))


def whitelist(op, value, typelist):
    if type(value) not in typelist:
        raise BadType(op,value,type(value))

t_float = numpy.float64
t_complex = numpy.complex128

def sympyconvert(n):
    return litparse(str(n))


def listify(t):
    return list(map(listify, t)) if isinstance(t, (list, tuple)) else t

def parserpn(rpn):
    stack = []

    for token in rpn:
        if token not in [i[0] for i in operators]:
            stack.append(token)

        else:
            if token == "+":
                a = stack.pop()
                b = stack.pop()
                stack.append(numpy.add(a,b))

            if token == "-":
                a = stack.pop()
                b = stack.pop()
                stack.append(numpy.subtract(b,a))

            if token == "-u":
                stack.append(-stack.pop())

            if token == "*":
                a = stack.pop()
                b = stack.pop()

                stack.append(numpy.multiply(a,b))

            if token == "%":
                a = stack.pop()
                b = stack.pop()

                blacklist("%",a,[t_complex])
                blacklist("%",b,[t_complex])

                stack.append(numpy.remainder(b,a))

            if token == "/":
                a = stack.pop()
                b = stack.pop()
                stack.append(numpy.divide(b,a))

            if token in ["^", "**"]:
                a = stack.pop()
                b = stack.pop()

                #limit(token,a,500,True)
                #limit(token,b,10**100,True)

                #integers get a promotion
                if isinstance(a,int): a = numpy.float64(a)
                if isinstance(b,int): b = numpy.float64(b)

                try:
                    stack.append(numpy.power(b,a))
                except:
                    stack.append(numpy.inf)

            if token in ["^-", "**-"]:
                a = stack.pop()
                b = stack.pop()

                #limit(token,a,-500,False)
                #limit(token,b,10**100,True)

                # integers get a promotion
                if isinstance(a, int): a = numpy.float64(a)
                if isinstance(b, int): b = numpy.float64(b)

                stack.append(numpy.power(b,-a))

            if token == "sqrt":
                a = stack.pop()
                stack.append(numpy.sqrt(a))

            if token == "ln":
                stack.append(numpy.log(a))

            if token == "log":
                a = stack.pop()
                if isinstance(a, tuple):
                    b = a[0]
                    c = a[1]
                    stack.append(numpy.log(b)/numpy.log(c))
                else:
                    stack.append(numpy.log(a))

            if token == ",":
                a = stack.pop()
                b = stack.pop()

                if isinstance(a, tuple):
                    stack.append((b,) + a)
                else:
                    stack.append((b, a))

            if token == "and":
                a = stack.pop()
                b = stack.pop()

                whitelist("and",a,[int])
                whitelist("and",b,[int])

                stack.append(numpy.bitwise_and(a,b))

            if token == "xor":
                a = stack.pop()
                b = stack.pop()

                whitelist("xor",a,[int])
                whitelist("xor",b,[int])

                stack.append(numpy.bitwise_xor(a,b))

            if token == "or":
                a = stack.pop()
                b = stack.pop()

                whitelist("or",a,[int])
                whitelist("or",b,[int])

                stack.append(numpy.bitwise_or(a,b))

            if token == "not":
                a = stack.pop()

                whitelist("not",a,[int])

                stack.append(numpy.bitwise_not(a))

            if token == "!":
                a = stack.pop()

                #limit("!",a,200,True)
                stack.append(scipy.special.factorial(a))

            if token == "choose":
                t = stack.pop()

                a = t[0]
                b = t[1]

                #limit("choose",a,200,True)
                #limit("choose",b,200,True)

                whitelist("choose",a,[int])
                whitelist("choose",b,[int])

                stack.append(scipy.special.comb(a, b))

            if token == "perm":
                t = stack.pop()

                a = t[0]
                b = t[1]

                #limit("perm",a,200,True)
                #limit("perm",b,200,True)

                whitelist("perm",a,[int])
                whitelist("perm",b,[int])

                stack.append(scipy.special.perm(a, b))

            if token == "sin":
                stack.append(numpy.sin(stack.pop()))

            if token == "cos":
                stack.append(numpy.cos(stack.pop()))

            if token == "tan":
                stack.append(numpy.tan(stack.pop()))

            if token == "csc":
                stack.append(numpy.divide(1,numpy.sin(stack.pop())))

            if token == "sec":
                stack.append(numpy.divide(1,numpy.cos(stack.pop())))

            if token == "cot":
                stack.append(numpy.divide(1,numpy.tan(stack.pop())))

            if token == "deg":
                a = stack.pop()
                blacklist("deg",a,[t_complex])

                stack.append(numpy.radians(a))

            if token == "rad":
                a = stack.pop()
                blacklist("deg",a,[t_complex])
                stack.append(numpy.degrees(a))

            if token == "asin":
                stack.append(numpy.arcsin(stack.pop()))

            if token == "acos":
                stack.append(numpy.arccos(stack.pop()))

            if token == "atan":
                stack.append(numpy.arctan(stack.pop()))

            if token == "acsc":
                stack.append(numpy.arcsin(1 / stack.pop()))

            if token == "asec":
                stack.append(numpy.arccos(1 / stack.pop()))

            if token == "acot":
                stack.append(numpy.arctan(1 / stack.pop()))

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
                stack.append(numpy.arcsinh(1 / stack.pop()))

            if token == "asech":
                stack.append(numpy.arccosh(1 / stack.pop()))

            if token == "acoth":
                stack.append(numpy.arctanh(1 / stack.pop()))

            if token == "swap":
                a = stack.pop()
                b = stack.pop()
                stack.append(a)
                stack.append(b)

            if token == "drop":
                stack.pop()

            if token == "flat":
                a = stack.pop()
                whitelist("flat",a,[tuple])
                for i in a:
                    stack.append(i)

            if token == "solve":
                x = sympy.Symbol('x')
                a = stack.pop()

                whitelist("solve",a,[tuple])

                polynomial = 0

                if len(a) > 10: raise TooManyArguments("solve")

                t = reversed(a)

                for degree, coeff in enumerate(t):
                    polynomial += coeff * (x ** degree)

                solns = sympy.solve(polynomial, x)
                solns = [sympyconvert(sympy.N(i)) for i in solns]
                stack.append(tuple(solns))

            if token == "pi":
                stack.append(numpy.pi)

            if token == "e":
                stack.append(numpy.e)

            if token == "[":
                a = stack.pop()

                if isinstance(a, tuple):
                    a = [i for i in a]
                else:
                    a = [a]

                stack.append(numpy.array(listify(a)))

            if token == ";":
                a = stack.pop()
                b = stack.pop()


                if isinstance(b, tuple):
                    a = tuple(a)
                    b = tuple(b)
                    if isinstance(b[0], tuple):
                        b = list(b)
                        b.append(a)
                        stack.append(tuple(b))
                    else:
                        stack.append((b, a))
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
                solns = numpy.linalg.solve(a, b)
                stack.append([[litparse(i)] for i in solns])

    return stack


def format_answer(answer):
    if isinstance(answer,tuple): return str(tuple([format_answer(i) for i in answer])).replace("'","")
    if type(answer) in [list,numpy.array,numpy.ndarray]:
        try:
            if numpy.isinf(answer):
                if answer > 0:return "∞"
                return "-∞"
        except:
            pass

        if len(answer) == 1:
            return format_answer(answer[0])
        return "[" + " ".join([format_answer(i) for i in answer]).replace("'","") + "]"
    if isinstance(answer,t_complex):
        if answer.imag == 0:
            return format_answer(answer.real)
        else:
            return str(answer).replace("j","i").replace("[","").replace("]","")
    if isinstance(answer,t_float):
        if numpy.isinf(answer):
            if answer > 0:return "∞"
            return "-∞"

    if answer == int(answer):
        return str(int(answer))
    else:
        return str(answer)



def evaluate_expr(expr):
    return parserpn(to_rpn(expr))

