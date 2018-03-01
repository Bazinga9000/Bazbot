import discord
from discord.ext import commands
import json
import shlex
import random
import pickle
import numpy
import sys, traceback


def get_money():
    try:
        with open('money.pkl', 'rb') as f:
            return pickle.load(f)
    except:
        return {}


money = get_money()

def dump_money():
    try:
        with open('money.pkl', 'wb') as f:
            pickle.dump(money, f)
    except Exception as e:
        print("PICKLING ERROR: " + str(e))
        return

    with open('backupmoney.pkl', 'wb') as f:
        pickle.dump(money, f)


def add_amount(id, amount):
    try:
        money[id] += amount
    except:
        money[id] = 100 + amount

    dump_money()

def get_amount(id):
    try:
        return money[id]
    except:
        money[id] = 100
        dump_money()
        return 100


def set_amount(id, amount):
    money[id] = amount


class Money():
    def __init__(self, bot):
        self.bot = bot
        self.money = get_money()
        dump_money()


    @commands.command(brief="Check your money amount.",aliases=["money"])
    async def getmoney(self,ctx):
        await ctx.send("**You have ∰" + str(get_amount(ctx.author.id)) + "**")


    @commands.command(brief="Add or remove money.")
    async def addmoney(self,ctx,amount : int,id : int):
        if ctx.author.id != 137001076284063744:
            return await ctx.send("You can't do that!")

        add_amount(id,amount)
        await ctx.send("**Given ∰" + str(amount) + " to <@" + str(id) + ">!**")


    @commands.command(brief="Get some money if you're out.")
    async def bankrupt(self,ctx):
        amount = get_amount(ctx.author.id)
        
        if amount != 0:
            return await ctx.send("Hey, you have money! What are you trying to pull here?")
        else:
            set_amount(ctx.author.id,100)
            return await ctx.send("A mysterious benefactor has granted you ∰100")

    @commands.command(brief="See the richest of the rich!")
    async def richlist(self,ctx,page : int = 1):
        get_amount(ctx.author.id) #ensure you're on the list

        richlist = money.items()
        richlist = sorted(richlist,key=lambda x: x[1])[::-1]

        if page < 1:
            await ctx.send("Uh oh! You friccin moron! That's an invalid page number!")
            return

        personcount = len(richlist)

        if 10 * (page - 1) > personcount:
            await ctx.send("Uh oh! You friccin moron! There aren't that many people with money!")
            return

        text = "```\n"

        for i in range(10):
            try:
                j = 10 * (page - 1) + i
                person = richlist[j]

                text += str(j + 1) + ") " + self.bot.get_user(person[0]).name + " - ∰" + str(person[1]) + "\n"


            except:
                continue

        text += "```\n"
        amt = get_amount(ctx.author.id)
        text += "You are #" + str(richlist.index((ctx.author.id,amt)) + 1) + "/" + str(len(richlist)) + " (∰" + str(amt) + ")"
        await ctx.send(text)

    '''
    @commands.command(brief="Add or remove money.")
    async def reset(self,ctx, *, verif):
        if ctx.author.id != 137001076284063744:
            return await ctx.send("You can't do that!")

        if verif == "yes i am absolutely sure":
            for person in money:
                money[person] = 100

        dump_money()
    '''

def setup(bot):
    bot.add_cog(Money(bot))
