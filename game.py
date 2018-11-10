import pygame
from pygame.locals import *
from random import randint
import sqlite3
import datetime

pygame.init()

conn = sqlite3.connect("database.db")
try:
    conn.execute("create table coins (number int)")
    conn.execute("insert into coins (number) values (0)")
    conn.commit()
except:
    pass
try:
    conn.execute("create table upgrades (id int, name str, status int, price int)")
    conn.execute("insert into upgrades (id, name, status, price) values (1, 'price per word', 1, 10)")
    conn.execute("insert into upgrades (id, name, status, price) values (2, 'slave typer', 0, 20)")
    conn.execute("insert into upgrades (id, name, status, price) values (3, 'coder', 0, 50)")
    conn.commit()
except:
    pass
try:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    conn.execute("create table player (price_per_word int, words_per_minute int, last_online string)")
    sql = "insert into player (price_per_word, words_per_minute, last_online) values (1, 0, '" + str(now) + "')"
    conn.execute(sql)
    conn.commit()
except:
    pass
cursor = conn.cursor()

window_size = [500, 500]

window = pygame.display.set_mode(window_size)

anim_location = "./sprites/coin/"
animation = []
for i in range(9):
    sprite = pygame.image.load(anim_location + "goldCoin" + str(i+1) + ".png")
    sprite = pygame.transform.scale(sprite, (50, 50))
    animation.append(sprite)

BLACK = (0, 0, 0)

def get_from_db(select, from_, where=None, value=None, string=False):
    if where == None:
        sql = "select " + select + " from " + from_
    else:
        if string == False:
            sql = "select " + select + " from " + from_ + " where " + where + "=" + value
        else:
            sql = "select " + select + " from " + from_ + " where " + where + "= '" + value + "'"
    cursor.execute(sql)
    result = cursor.fetchall()
    return result[0][0]

def generate_word():
    word_list = open("words.txt", "r")
    words = word_list.readlines()
    word_list.close()
    num = randint(0, len(words) - 1)
    return words[num][:-1]

def get_upgrade(id, cursor):
    cursor.execute("select * from Upgrades where id=?", str(id))
    result = cursor.fetchall()
    return result[0]

def get_last_id(cursor):
    cursor.execute("select * from Upgrades order by id desc limit 1")
    result = cursor.fetchall()
    return result[0][0]

def update(typed_word, word_to_type, coins, anim_num):
    window.fill((255, 255, 255))

    font = pygame.font.SysFont("serif", 36)
    upgrade_font = pygame.font.SysFont("serif", 18)
    stats_font = pygame.font.SysFont("serif", 24)

    rendered_word_to_type = font.render(word_to_type, False, BLACK)
    window.blit(rendered_word_to_type, (50, 50))

    rendered_typed_word = font.render(typed_word, False, BLACK)
    window.blit(rendered_typed_word, (50, 100))

    rendered_coins = font.render(str(int(coins)), False, BLACK)
    rendered_coins_rect = rendered_coins.get_rect()
    rendered_coins_rect.right = 450
    rendered_coins_rect.top = 5
    window.blit(rendered_coins, rendered_coins_rect)

    window.blit(animation[anim_num], (window_size[1] - 50, 0))

    thead = [
        upgrade_font.render("Upgrade", False, BLACK),
        upgrade_font.render("Status", False, BLACK),
        upgrade_font.render("Price", False, BLACK)
    ]
    thead_rect = []
    for i in range(len(thead)):
        thead_rect.append(thead[i].get_rect())
        thead_rect[i].top = 70
    thead_rect[0].right = 350
    thead_rect[1].right = 435
    thead_rect[2].right = 490
    for i in range(len(thead)):
        window.blit(thead[i], thead_rect[i])

    global upgrade_rect
    for i in range(get_last_id(cursor)):
        upgrade = list(get_upgrade(i+1, cursor))
        for j in range(len(upgrade) - 1):
            upgrade[j] = upgrade_font.render(str(upgrade[j+1]), False, BLACK)
            upgrade_rect.append(upgrade[j].get_rect())
            upgrade_rect[j].top = 120 + i * 15
        upgrade_rect[0].right = 350
        upgrade_rect[1].right = 435
        upgrade_rect[2].right = 490
        for j in range(len(upgrade) - 1):
            window.blit(upgrade[j], upgrade_rect[j])

    rendered_price_per_word = stats_font.render("Price per word: " + str(price_per_word), False, BLACK)
    rect = rendered_price_per_word.get_rect()
    rect.left = 0
    rect.top = 450
    window.blit(rendered_price_per_word, rect)
    rendered_words_per_minute = stats_font.render("Words per minute: " + str(words_per_minute), False, BLACK)
    rect = rendered_words_per_minute.get_rect()
    rect.right = 500
    rect.top = 450
    window.blit(rendered_words_per_minute, rect)

    pygame.display.update()

def buy_upgrade(upgrade, coins, conn):
    cursor.execute("select Status, Price from Upgrades where Name=?", [upgrade])
    result = cursor.fetchall()
    curr_status = result[0][0]
    status = curr_status + 1
    curr_price = result[0][1]
    conn.execute("update Coins set Number=? where Number=?", [coins - curr_price, coins])
    price = round(curr_price * 1.5)
    conn.execute("update Upgrades set Status=?, Price=? where Name=?", [str(status), str(price), str(upgrade)])
    conn.commit()

typed_word = ""
typed = True
run = True
anim_num = 0
clock = pygame.time.Clock()
price_per_word = get_from_db(select="price_per_word", from_="Player")
upgrade_rect = []
words_per_minute = get_from_db(select="words_per_minute", from_="Player")
increase_coins = USEREVENT + 1

last_online = get_from_db(select="last_online", from_="Player")
format = "%Y-%m-%d %H:%M"
last_online = datetime.datetime.strptime(last_online, format)
now = datetime.datetime.strptime(now, format)
time_since_last_online = round( abs( (last_online - now).total_seconds()/60 ) )
coins = get_from_db(select="Number", from_="Coins")
conn.execute("update Coins set Number=?", [coins + time_since_last_online * words_per_minute])
conn.commit()

pygame.time.set_timer(increase_coins, 1000)

while run:
    clock.tick(10)

    coins = get_from_db(select="Number", from_="Coins")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            now = now.strftime(format)
            conn.execute("update Player set last_online=?", [now])
            conn.commit()
        if event.type == pygame.KEYDOWN:
            if pygame.K_a <= event.key <= pygame.K_z:
                char = chr(event.key)
                typed_word += char
            if event.key == pygame.K_BACKSPACE:
                typed_word = typed_word[:-1]
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] > upgrade_rect[0].left:
                if mouse_pos[1] > 120 and mouse_pos[1] < 120 + 1 * 15:
                    price = get_from_db(select="price", from_="Upgrades", where="Name", value="price per word", string=True)
                    if coins >= price:
                        buy_upgrade("price per word", coins, conn)
                        conn.execute("update Player set price_per_word=?", [price_per_word + 1])
                        conn.commit()
                        price_per_word += 1
                if mouse_pos[1] > 120 + 1 * 15 and mouse_pos[1] < 120 + 2 * 15:
                    price = get_from_db(select="price", from_="Upgrades", where="Name", value="slave typer", string=True)
                    if coins >= price:
                        buy_upgrade("slave typer", coins, conn)
                        conn.execute("update Player set words_per_minute=?", [words_per_minute + 1])
                        conn.commit()
                        words_per_minute += 1
                if mouse_pos[1] > 120 + 2 * 15 and mouse_pos[1] < 120 + 3 * 15:
                    price = get_from_db(select="price", from_="Upgrades", where="Name", value="coder", string=True)
                    if coins >= price:
                        buy_upgrade("coder", coins, conn)
                        conn.execute("update Player set words_per_minute=?", [words_per_minute + 3])
                        conn.commit()
                        words_per_minute += 3
        if event.type == increase_coins:
            conn.execute("update Coins set Number=? where Number=?", [coins + words_per_minute / 60 * price_per_word, coins])
            conn.commit()

    if typed:
        word_to_type = generate_word()
        typed = False

    if typed_word == word_to_type:
        typed_word = ""
        conn.execute("update Coins set Number=? where Number=?", [coins + price_per_word, coins])
        conn.commit()
        word_to_type = generate_word()

    if anim_num < 8:
        anim_num += 1
    else:
        anim_num = 0

    update(typed_word, word_to_type, coins, anim_num)
