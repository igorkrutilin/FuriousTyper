import pygame
from random import randint
import sqlite3

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

def get_coin_number(cursor):
    cursor.execute("select Number from Coins")
    result = cursor.fetchall()
    coins = result[0][0]

    return coins

def generate_word():
    word_list = open("words.txt", "r")
    words = word_list.readlines()
    word_list.close()
    num = randint(0, len(words) - 1)
    return words[num][:-1]

def get_upgrade(id, cursor):
    cursor.execute("select * from upgrades where id=?", str(id))
    result = cursor.fetchall()
    return result[0]

def update(typed_word, word_to_type, coins, anim_num):
    window.fill((255, 255, 255))

    font = pygame.font.SysFont("serif", 36)
    upgrade_font = pygame.font.SysFont("serif", 18)

    rendered_word_to_type = font.render(word_to_type, False, (0, 0, 0))
    window.blit(rendered_word_to_type, (50, 50))

    rendered_typed_word = font.render(typed_word, False, (0, 0, 0))
    window.blit(rendered_typed_word, (50, 100))

    rendered_coins = font.render(str(coins), False, (0, 0, 0))
    rendered_coins_rect = rendered_coins.get_rect()
    rendered_coins_rect.right = 450
    rendered_coins_rect.top = 5
    window.blit(rendered_coins, rendered_coins_rect)

    window.blit(animation[anim_num], (window_size[1] - 50, 0))

    thead = [
        upgrade_font.render("Upgrade", False, (0, 0, 0)),
        upgrade_font.render("Status", False, (0, 0, 0)),
        upgrade_font.render("Price", False, (0, 0, 0))
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

    upgrade = list(get_upgrade(1, cursor))
    global upgrade_rect
    upgrade_rect = []
    for i in range(len(upgrade) - 1):
        upgrade[i] = upgrade_font.render(str(upgrade[i+1]), False, (0, 0, 0))
        upgrade_rect.append(upgrade[i].get_rect())
        upgrade_rect[i].top = 120
    upgrade_rect[0].right = 350
    upgrade_rect[1].right = 435
    upgrade_rect[2].right = 490
    for i in range(len(upgrade) - 1):
        window.blit(upgrade[i], upgrade_rect[i])

    pygame.display.update()

def buy_upgrade(upgrade, coins, conn, cursor):
    cursor.execute("select Status, Price from Upgrades where Name=?", [upgrade])
    result = cursor.fetchall()
    curr_status = result[0][0]
    status = curr_status + 1
    curr_price = result[0][1]
    conn.execute("update Coins set Number=? where Number=?", [coins - curr_price, coins])
    price = round(curr_price * 1.5)
    conn.execute("update Upgrades set Status=?, Price=? where Name=?", [str(status), str(price), str(upgrade)])
    conn.commit()

def get_price(upgrade, cursor):
    cursor.execute("select Price from Upgrades where Name=?", [upgrade])
    result = cursor.fetchall()
    return result[0][0]

typed_word = ""
typed = True
run = True
anim_num = 0
clock = pygame.time.Clock()
price_per_word = 1

while run:
    clock.tick(10)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if pygame.K_a <= event.key <= pygame.K_z:
                char = chr(event.key)
                typed_word += char
            if event.key == pygame.K_BACKSPACE:
                typed_word = typed_word[:-1]
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for upgrade in upgrade_rect:
                # проверяем, кликнул ли игрок на апгрейд
                if mouse_pos[0] > upgrade.left and mouse_pos[1] > upgrade.top and mouse_pos[1] < upgrade.bottom:
                    price = get_price("price per word", cursor)
                    # проверяем, хватает ли игроку денег на апгрейд
                    if coins >= price:
                        buy_upgrade("price per word", coins, conn, cursor)
                        price_per_word += 1

    if typed:
        word_to_type = generate_word()
        typed = False

    coins = get_coin_number(cursor)

    if typed_word == word_to_type:
        typed_word = ""
        # change_coin_number(coins, "+", price_per_word, conn)
        conn.execute("update Coins set Number=? where Number=?", [coins + price_per_word, coins])
        word_to_type = generate_word()

    if anim_num < 8:
        anim_num += 1
    else:
        anim_num = 0

    update(typed_word, word_to_type, coins, anim_num)
