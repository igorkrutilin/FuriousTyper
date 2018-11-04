import pygame
import random

pygame.init()

window_size = [500, 500]

window = pygame.display.set_mode(window_size)

def update(typed_word, word_to_type):
    window.fill((255, 255, 255))

    font = pygame.font.SysFont("serif", 36)

    rendered_typed_word = font.render(typed_word, False, (0, 0, 0))
    window.blit(rendered_typed_word, (100, 100))

    rendered_word_to_type = font.render(word_to_type, False, (0, 0, 0))
    window.blit(rendered_word_to_type, (100, 50))

    pygame.display.update()

def generate_word_to_type():
    word_list = open("words.txt", "r")
    words = word_list.readlines()
    num = random.randint(0, len(words) - 1)
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
        word_to_type = generate_word_to_type()
        typed = False

    if typed_word == word_to_type:
        typed_word = ""
        typed = True

    update(typed_word, word_to_type)
