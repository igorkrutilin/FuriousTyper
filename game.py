import pygame
from random import randint
import sqlite3

pygame.init()

conn = sqlite3.connect("database.db")
try:
    conn.execute("create table coins (number int)")
    conn.execute("insert into coins (number) values (0)")
except:
    pass
cursor = conn.cursor()

window_size = [500, 500]

window = pygame.display.set_mode(window_size)

def get_coin_number(cursor):
    cursor.execute("select Number from Coins")
    result = cursor.fetchall()
    coins = result[0][0]

    return coins

def change_coin_number(coins, operation, number, conn):
    if operation == "+":
        coins += number
    conn.execute("delete from coins")
    conn.execute("insert into coins (number) values (" + str(coins) + ")")
    conn.commit()

def update(typed_word, word_to_type, coins):
    window.fill((255, 255, 255))

    font = pygame.font.SysFont("serif", 36)

    rendered_word_to_type = font.render(word_to_type, False, (0, 0, 0))
    window.blit(rendered_word_to_type, (100, 50))

    rendered_typed_word = font.render(typed_word, False, (0, 0, 0))
    window.blit(rendered_typed_word, (100, 100))

    rendered_coins = font.render(str(coins), False, (0, 0, 0))
    window.blit(rendered_coins, (450, 20))

    pygame.display.update()

def generate_word():
    word_list = open("words.txt", "r")
    words = word_list.readlines()
    word_list.close()
    num = randint(0, len(words) - 1)
    return words[num][:-1]

typed_word = ""
typed = True
run = True

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if pygame.K_a <= event.key <= pygame.K_z:
                char = chr(event.key)
                typed_word += char
            if event.key == pygame.K_BACKSPACE:
                typed_word = typed_word[:-1]

    if typed:
        word_to_type = generate_word()
        typed = False

    coins = get_coin_number(cursor)

    if typed_word == word_to_type:
        typed_word = ""
        coins = change_coin_number(coins, "+", 1, conn)
        word_to_type = generate_word()

    update(typed_word, word_to_type, coins)
