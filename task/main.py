import time

import pygame
import random

pygame.init()
pygame.mixer.init()

import os
os.chdir("C:\\Users\\Администратор-ПК\\Desktop\\piano tiles")

# константы
# здесь записан порядок нот и их длительность для каждой песни
SIZE = (400, 600)

CHRISTMAS_TREE_NOTES = ["c4", "a4", "a4", "g4", "a4", "f4", "c4", "c4", "c4", "a4", "a4", "a-4", "g4", "c5",
                        "c5", "d4", "d4", "a-4", "a-4", "a4", "g4", "f4", "c4", "a4", "a4", "g4", "a4", "f4"]
CHRISTMAS_TREE_DURATION = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2,
                           1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2]

BIRCH_NOTES = ["a4", "a4", "a4", "a4", "g4", "f4", "f4", "e4", "d4",
               "a4", "a4", "c5", "a4", "g4", "g4", "f4", "f4", "e4", "d4",
               "e4", "f4", "g4", "f4", "f4", "e4", "d4",
               "e4", "f4", "g4", "f4", "f4", "e4", "d4"]
BIRCH_DURATION = [1, 1, 1, 1, 2, 1, 1, 2, 2,
                  1, 1, 1, 1, 1, 1, 1, 1, 2, 2,
                  2, 1, 2, 1, 1, 2, 2,
                  2, 1, 2, 1, 1, 2, 2]

MORNING_NOTES = ["c5", "a4", "g4", "f4", "g4", "a4", "c5", "a4", "f4", "g4", "a4", "g4", "a4", "c5", "a4",
                 "c5", "d5", "a4", "d5", "c5", "a4", "f4", "c4", "a3", "g3", "f3", ]
MORNING_DURATION = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2]


class Tile(pygame.sprite.Sprite):
    # загрузка всех картинок для плиток
    short_tile = pygame.image.load("short_tile.png")
    short_tile = pygame.transform.scale(short_tile, (SIZE[0] // 4, SIZE[1] // 3.5))
    short_tile_pressed = pygame.image.load("short_tile_pressed.png")
    short_tile_pressed = pygame.transform.scale(short_tile_pressed, (SIZE[0] // 4, SIZE[1] // 3.5))

    long_tile = pygame.image.load("long_tile.png")
    long_tile = pygame.transform.scale(long_tile, (SIZE[0] // 4, SIZE[1] // 2.2))
    long_tile_pressed = pygame.image.load("long_tile_pressed.png")
    long_tile_pressed = pygame.transform.scale(long_tile_pressed, (SIZE[0] // 4, SIZE[1] // 2.2))

    def __init__(self, long=False):
        '''
        Класс плитки может создавать их двух разных размеров: короткие и длинные.
        Если нужно создать длинную плитку, параметр long должен иметь значение True. По умолчанию плитки короткие.

        Длинная плитка имеет дополнительную переменную count - это сколько тиков уже прошло до того,
        как она посчитается сыгранной. Пока это время не прошло, длинную плитку нужно зажимать мышкой.
        '''
        super().__init__()

        if long:
            self.long = True
            self.image = Tile.long_tile
            self.count = 0
        else:
            self.long = False
            self.image = Tile.short_tile

        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, 3) * SIZE[0] // 4  # создаём плитку на случайной дорожке
        self.rect.y = -SIZE[1]

        # если плитка соприкосается с другими плитками, переставить её на свободную дорожку
        while pygame.sprite.spritecollide(self, screen_notes, False):
            self.rect.x = random.randint(0, 3) * SIZE[0] // 4

        self.played = False

    def update(self):
        self.rect.y += 1

        # ставим длинные плитки в начальный цвет, чтобы если их перестали нажимать слишком рано,
        # они не застыли в нажатом положении
        if self.long and self.count > 0 and not self.played:
            self.image = Tile.long_tile

        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            if self.rect.collidepoint(mouse_pos):
                self.press()

        if self.rect.y >= SIZE[1]:  # если плитка за пределами окна, она удаляется
            self.kill()

    def press(self):
        # нота плитки проигрывается если
        # 1. она на была проиграна раньше
        # 2. это длинная плитка и она ещё не отыграла ни одного тика
        # 3. это короткая плитка
        if not self.played:
            if self.long and self.count == 0:
                play_note()
            if not self.long:
                play_note()

        if self.long:
            # каждые несколько тиков при нажатии на длинную плитку её цвет меняется
            # когда нужное количество тиков пройдёт, то она навсегда поменяет цвет
            # и будет считаться нажатой

            self.count += 1
            if self.count % 5 == 0 and self.count * 2 < 255:
                self.image = Tile.long_tile_pressed
            else:
                self.image = Tile.long_tile
            if self.count >= 120:
                self.image = Tile.long_tile_pressed
                self.played = True
        else:
            # короткие плитки сразу меняют цвет и считаются сыгранными
            self.image = Tile.short_tile_pressed
            self.played = True

songs = []
class Song:
      # здесь будет хранится список всех доступных песен

    def __init__(self, name, notes, duration, rect, interval=0.5):
        self.name = name
        self.notes = notes
        self.duration = duration
        self.color = "red"
        self.rect = pygame.Rect(rect)
        self.interval = interval

        self.text = f1.render(self.name, True, pygame.Color("white"))
        songs.append(self)


screen = pygame.display.set_mode(SIZE)

fps = 500
clock = pygame.time.Clock()

next_note = 0  # номер ноты, которую нужно сыграть следующей
sound = None  # звук, который сейчас играет

pygame.mixer.music.set_volume(0.3)


def play_note():
    global next_note, sound
    if next_note > 0:
        # sound: pygame.mixer.Sound
        sound.fadeout(1000)

    sound = pygame.mixer.Sound(f"Sounds/{playing_song.notes[next_note]}.ogg")
    sound.play()
    next_note += 1

f1 = pygame.font.Font(None, 38)

# создание песен
song1 = Song("В лесу родилась ёлочка", CHRISTMAS_TREE_NOTES, CHRISTMAS_TREE_DURATION, (20, 100, 360, 45))
song2 = Song("Во поле береза стояла", BIRCH_NOTES, BIRCH_DURATION, (20, 200, 360, 45), interval=0.7)
song3 = Song("Утро", MORNING_NOTES, MORNING_DURATION, (20, 300, 360, 45))

background_menu = pygame.image.load("menu.png")
background_menu = pygame.transform.scale(background_menu, SIZE)

is_play = False

# ВРЕМЕННЫЙ КОД для запуска без меню
screen_notes = pygame.sprite.Group()
created_notes = 0
next_note = 0
timer = time.time()
mode = "menu"
playing_song = song1
is_play = True

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            # если игра не идёт, при клике переход в меню
            if not is_play and mode == "play":
                if event.button == 1:
                    mode = "menu"
    
    if mode == "menu":
        is_play = True

        if isinstance(sound, pygame.mixer.Sound):
            sound.stop()

        screen.blit(background_menu, (0,0))
        
        for song in songs:
            if song.rect.collidepoint(pygame.mouse.get_pos()):
                song.color = (0, 200, 0)
            else:
                song.color = (100,100,100)
        y = 1
        for song in songs:
            pygame.draw.rect(screen, song.color, song.rect, 3)
            screen.blit(song.text, (30, 100 * y + 5))
            y += 1
        for song in songs:
            if song.rect.collidepoint(pygame.mouse.get_pos()) and \
                pygame.mouse.get_pressed()[0]:
                    playing_song = song
                    mode = "play"
                    screen_notes = pygame.sprite.Group()
                    created_notes = 0
                    next_note = 0
                    timer = time.time()

        
    if mode == "play":
        if is_play:
            if created_notes < len(playing_song.notes) and \
                time.time() - timer >= playing_song.duration[created_notes] * playing_song.interval:
                if playing_song.duration[created_notes] == 1:
                    x = Tile()
                    screen_notes.add(x)
                else:
                    x = Tile(True)
                    screen_notes.add(x)
                timer = time.time()
                created_notes += 1
            screen_notes.update()

        screen.fill(pygame.Color("white"))

        for i in range(4):  # отрисовка дорожек
                pygame.draw.line(screen, pygame.Color("black"), (i * 100, 0), (i * 100, 600))

                pygame.draw.line(screen, pygame.Color("red"), (0, 500), (400, 500), 5)

                screen_notes.draw(screen, (0,0))


        # если была нажата последняя нота в песне и она сыграна до конца, то это победа
        if next_note == len(playing_song.notes):
            for note in screen_notes:
                if not note.played:
                    break
            else:
                text = f1.render("ПОБЕДА", True, pygame.Color("green"))
                text_rect = text.get_rect(center=(SIZE[0] // 2, SIZE[1] // 2))
                screen.blit(text, text_rect)
                is_play = False
        
        if pygame.mouse.get_pressed()[2]:
            mode = "menu"

        for note in screen_notes:
            if note.rect.y > 500 and not note.played:
                text = f1.render("проигрыш".upper(), True, (200, 20, 20))
                screen.blit(text, (120,200))
                is_play = False
    pygame.display.flip()
    clock.tick(fps)