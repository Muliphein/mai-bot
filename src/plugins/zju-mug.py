import random
import re

from collections import defaultdict
from PIL import Image
from nonebot import on_command, on_message, on_notice, require, get_driver, on_regex
from re import escape
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Message, Event, Bot
from nonebot.adapters.cqhttp import MessageSegment
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from src.libraries.image import *
from random import randint
import time
import csv

bot_choice_pool = {}

random_choice = on_regex("^[前昨今明后]天(.+)还是(.+)", priority=50)


@random_choice.handle()
async def _(bot: Bot, event: Event, state: T_State):
    #grp = re.match("今天(.+)还是(.+)", str(event.get_message())).groups()
    global bot_choice_pool
    pid = event.group_id if event.message_type == 'group' else event.get_user_id()
    bot_choice_pool[pid] = str(event.get_message())[2:].split("还是")
    choice_pool = bot_choice_pool[pid]
    if choice_pool[0] == choice_pool[1]:
        x = '？'
    else:
        x = random.choice(choice_pool)
        choice_pool.remove(x)
    x = escape(x)
    await random_choice.finish(Message([
        MessageSegment.reply(event.message_id),
        MessageSegment("text", {
            "text": f"{x}" })
        ])
    )

another_choice = on_regex(".*你再想想.*", priority=51)


@another_choice.handle()
async def _(bot: Bot, event: Event, state: T_State):
    #grp = re.match("今天(.+)还是(.+)", str(event.get_message())).groups()
    #grp = str(event.get_message())[2:].split("还是")
    # print(str(event.get_message()))
    # if(len(str(event.get_message()))==4):
    global bot_choice_pool
    pid = event.group_id if event.message_type == 'group' else event.get_user_id()
    if pid not in bot_choice_pool:
        bot_choice_pool[pid] = []
    choice_pool = bot_choice_pool[pid]
    if len(choice_pool) == 0:
        x = random.choice(['我没的想了', '都让我想完了', '爬'])
    else:
        x = random.choice(choice_pool)
        choice_pool.remove(x)
    await another_choice.finish(Message([
        MessageSegment.reply(event.message_id), 
        MessageSegment("text", {
            "text": f"{x}"
        })]))

yesquestion = on_regex("是.*吧", priority=52)


@yesquestion.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global bot_choice_pool
    pid = event.group_id if event.message_type == 'group' else event.get_user_id()
    bot_choice_pool[pid] = ['是的', '不是']
    choice_pool = bot_choice_pool[pid]
    x = random.choice(choice_pool)
    choice_pool.remove(x)
    msg = str(event.get_message())
    if (msg.find('嘉然') != -1 or msg.find('嘉心糖') != -1):
        x = x+'捏'
    await yesquestion.finish(Message([
        MessageSegment.reply(event.message_id), 
        MessageSegment("text", {
            "text": f"{x}"
        })]))

food_list = defaultdict(list)
f = open('src/static/foodlist.csv', 'r', encoding='utf-8-sig')
tmp = f.readlines()
f.close()
for t in tmp:
    arr = t.strip().split(',')
    for i in range(1, len(arr)):
        if arr[i] != "":
            food_list[arr[0]].append(arr[i])
# print(food_list)

eatwut = on_regex("(.*)[前昨今明后]天(.*)不*[吃喝][啥(什么)]", priority=53)


@eatwut.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global bot_choice_pool
    msg = str(event.get_message())
    if (msg.find('前天') != -1 or msg.find('昨天') != -1):
        x = '这种事你怎么问我'
    elif (msg.find('不吃啥') != -1 or msg.find('不吃什么') != -1):
        x = '爬'
    else:
        p = random.random()
        if p <= 0.0114514:
            x = '你稍稍，肖恩先吃'
        elif p >= (1-0.0114514):
            x = '？建议你请我吃一顿'
        else:
            if msg[-2:] == '什么':
                loc = msg[2:-3]
            else:
                loc = msg[2:-2]
            if loc not in food_list:
                loc = 'default'
            pid = event.group_id if event.message_type == 'group' else event.get_user_id()
            bot_choice_pool[pid] = list.copy(food_list[loc])
            choice_pool = bot_choice_pool[pid]
            x = random.choice(choice_pool)
            choice_pool.remove(x)

    await eatwut.finish(Message([
        MessageSegment.reply(event.message_id), 
        MessageSegment("text", {
            "text": f"{x}"
        })]))


aliases_map = None
aliases_version = None

def query_aliases_name(str):
    if str in aliases_map.keys():
        return aliases_map[str]
    else:
        return '不知道喵'

def init_aliases_chart():
    global aliases_map
    if aliases_map is None:
        aliases_map = {}
        with open('src/static/main.csv')  as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                if row[0].isdigit():
                    true_name = row[1]
                    true_id = row[0]
                    for idx in range(0, len(row)):
                        aliases_map [row[idx]] = (true_id, true_name)


random_choice = on_regex("(.+)是什么歌", priority=50)


@random_choice.handle()
async def _(bot: Bot, event: Event, state: T_State):
    pid = event.group_id if event.message_type == 'group' else event.get_user_id()
    init_aliases_chart()
    alias_name = query_aliases_name(str(event.get_message())[:-4])
    await random_choice.finish(Message([
        MessageSegment.reply(event.message_id), 
        MessageSegment("text", {
            "text": f"{alias_name}"
        })]))


repeat = on_message(priority=99)

@repeat.handle()
async def _(bot: Bot, event: Event, state: T_State):
    r = random.random()
    date_d = int(time.strftime("%d", time.localtime(time.time())))
    date_m = int(time.strftime("%m", time.localtime(time.time())))
    date_y = int(time.strftime("%Y", time.localtime(time.time())))
    
    if r <= 0.0114514:
        await repeat.finish(event.get_message())
