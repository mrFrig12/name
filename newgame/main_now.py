enemy_coif = 30
player_coif = 30
player_hp = 200
enemy_hp = 200
player_coif_damage = 5
enemy_coif_damage = 0.5


import time
import json
import pygame as pg
import os
import sys
import random
import pygame_menu
import pygame_menu.themes

os.chdir("C:\\Users\\Администратор-ПК\\Desktop\\newgame")
pg.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 550
CHARACTER_HEIGHT = 480
CHARACTER_WIDTH = 350

FPS = 60

font = pg.font.Font(None, 40)

def load_image(file, width, height):
    image = pg.image.load(file)#.convert_alpha()
    image = pg.transform.scale(image, (width, height))
    return image

def text_render(text):
    return font.render(str(text), True, "black")



class Fireball(pg.sprite.Sprite):
    def __init__(self, coord, side, power, folder):
        super().__init__()
        self.side = side
        self.power = power
        self.image = load_image(f"images\\{folder}\\magicball.png", 200, 150)
        self.speed = -4
        if side:
            self.speed = 4
            self.image = pg.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.topleft = coord

    def update(self):
        self.rect.x += self.speed
        if not(-50 < self.rect.x < SCREEN_WIDTH):
            self.kill()


class Enemy_fireball(Fireball):
    def __init__(self, coord, side, power, folder):
        super().__init__(coord, side, power, folder)
        self.image = load_image("images/{}/magicball.png".format(folder), 200, 150)
        if side:
            self.image = pg.transform.flip(self.image, True, False)


class Enemy(pg.sprite.Sprite):
    def __init__(self, folder):
        super().__init__()

        self.gun = True
        self.fireballs = pg.sprite.Group()
        self.folder = folder
        self.load_animations()

        self.image = self.idle_animation_right[0]
        self.current_image = 0
        self.current_animation = self.idle_animation_left
        self.health = enemy_hp

        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)

        self.timer = pg.time.get_ticks()
        self.interval = 300
        self.side = 0
        self.animation_mode = True

        self.magic_balls = pg.sprite.Group()

        self.attack_mode = False
        self.attack_interval = 500

        self.move_interval = 800
        self.move_duration = 0
        self.direction = 0
        self.move_timer = pg.time.get_ticks()

        self.charge_power = 0

    def load_animations(self):
        self.idle_animation_right = [load_image(f"images/{self.folder}/idle{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)
                                     for i in range(1, 4)]

        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]

        self.move_animation_right = [load_image(f"images/{self.folder}/move{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)
                                     for i in range(1, 5)]

        self.move_animation_left = [pg.transform.flip(image, True, False) for image in self.move_animation_right]

        self.attack = [load_image(f"images/{self.folder}/attack.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.attack.append(pg.transform.flip(self.attack[0], True, False))

    def update(self, player):
        self.handle_attack_mode(player)
        self.handle_movement()
        self.handle_animation()

    def handle_attack_mode(self, player):
        if not self.attack_mode:
            attack_probability = 1
            if player.charge_mode:
                attack_probability += 2
            if random.randint(1, 100) <= attack_probability:
                self.attack_mode = True
                self.charge_power = random.randint(1,100)//attack_probability
                self.side = 0 if player.rect.centerx < self.rect.centerx else 1
                self.animation_mode = False
                self.image = self.attack[not self.side]

        if self.attack_mode:
            if pg.time.get_ticks() - self.timer > self.attack_interval:
                self.attack_mode = False
                self.timer = pg.time.get_ticks()
                self.gun = True

    def handle_movement(self):
        if self.attack_mode:
            return

        now = pg.time.get_ticks() # взять количество тиков

        if now - self.move_timer < self.move_duration:
            self.animation_mode = True # включить режим анимации
            self.rect.x += self.direction # подвинуть по X координате на direction
            self.current_animation = self.move_animation_left if self.direction == -1 else self.move_animation_right
        else:
            if random.randint(1, 100) == 1 and now - self.move_timer > self.move_interval:
                self.move_timer = pg.time.get_ticks()
                self.move_duration = random.randint(400, 1500) # случайное число от 400 до 1500
                self.direction = random.choice([-1, 1])
            else:
                self.animation_mode = True # включить режим анимации
                self.current_animation = self.idle_animation_left if self.side == "left" else self.idle_animation_right

        if self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        elif self.rect.left <= 0:
            self.rect.left = 0

    def handle_animation(self):
        if self.animation_mode and not self.attack_mode:
            if pg.time.get_ticks() - self.timer >= self.interval:
                self.current_image += 1
                if self.current_image == len(self.current_animation):
                    self.current_image = 0
                try:
                    self.image = self.current_animation[self.current_image]
                except:
                    self.current_image = 0
                self.timer = pg.time.get_ticks()
                
        if self.attack_mode and self.gun:
            self.gun = False
            self.attack_interval = self.charge_power * enemy_coif
            fireball_pos = self.rect.topright if self.side else self.rect.topleft
            self.fireballs.add(Enemy_fireball(fireball_pos, self.side, self.charge_power, self.folder))
            self.charge_power = 0
            self.image = self.attack[not self.side]
            self.timer = pg.time.get_ticks()


class Player(pg.sprite.Sprite):
    def __init__(self, folder, mode, st_pos=100):
        super().__init__()
        self.folder = folder
        self.load_animation()
        print(mode)
        self.mode = mode
        self.folder_coif = 2 if folder == "fire wizard" else 1

        self.image = self.idle_animation_right[0]
        self.current_image = 0
        self.current_animation = self.idle_animation_right
        self.health = player_hp

        self.rect = self.image.get_rect()
        self.rect.center = (st_pos, SCREEN_HEIGHT // 2)

        self.timer = pg.time.get_ticks()
        self.attack_timer = pg.time.get_ticks()
        self.interval = 200
        self.side = 1 # 1 right 0 left
        self.animation_mode = True

        self.charge_power = 0
        self.charge_indicator = pg.Surface((self.charge_power, 10))
        self.charge_indicator.fill("red")
        self.charge_mode = False

        self.attack_mode = False
        self.attack_interval = 500
        self.fireballs = pg.sprite.Group()
        self.gun = False

    def load_animation(self):
        self.idle_animation_right = [load_image("images/{}/idle{}.png".format(self.folder, x+1), CHARACTER_WIDTH, CHARACTER_HEIGHT) for x in range(3)]
        self.idle_animation_left = [pg.transform.flip(self.idle_animation_right[x], True, False) for x in range(3)]
        self.movement_animation_right = [load_image("images/{}/move{}.png".format(self.folder,x+1), CHARACTER_WIDTH, CHARACTER_HEIGHT) for x in range(3)]
        self.movement_animation_left = [pg.transform.flip(self.movement_animation_right[x], True, False) for x in range(3)]
        self.charge = [load_image(f"images/{self.folder}/charge.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.charge.append(pg.transform.flip(self.charge[0], True, False))
        self.attack = [load_image(f"images/{self.folder}/attack.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.attack.append(pg.transform.flip(self.attack[0], True, False))
        self.down = [load_image(f"images/{self.folder}/down.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.down.append(pg.transform.flip(self.down[0], True, False))

    def handle_attack_mode(self):
        if self.attack_mode:
            if pg.time.get_ticks() - self.attack_timer >= self.attack_interval:
                self.attack_mode = False
                self.attack_timer = pg.time.get_ticks()

    def handle_movement(self):
        if self.attack_mode:
            return
        keys = pg.key.get_pressed()
        if keys[self.mode[0]]: # right
            self.direction = 1
            self.side = 1
        elif keys[self.mode[1]]:
            self.direction = - 1
            self.side = 0
        elif keys[self.mode[2]]:
            self.animation_mode = False
            self.image = self.charge[not self.side]
            self.charge_mode = True
        else:
            self.direction = 0
            self.charge_mode = False
            self.animation_mode = True
        if not self.charge_mode:
            self.rect.x += self.direction
        if self.side:
            self.current_animation = self.movement_animation_right if self.direction else self.idle_animation_right
        else:
            self.current_animation = self.movement_animation_left if self.direction else self.idle_animation_left

        if self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        elif self.rect.left <= 0:
            self.rect.left = 0

    def update(self):
        self.handle_attack_mode()
        self.handle_movement()
        self.handle_animation()

    def handle_animation(self):
        if not self.charge_mode and self.charge_power > 0:
            self.attack_mode = True
            self.gun = True
        if self.animation_mode and not self.attack_mode:
            if pg.time.get_ticks() - self.timer >= self.interval:
                self.current_image += 1
                if self.current_image == len(self.current_animation):
                    self.current_image = 0
                self.image = self.current_animation[self.current_image]
                self.timer = pg.time.get_ticks()

        if self.charge_mode:
            self.direction = 0
            self.charge_power += 1
            self.charge_indicator = pg.Surface((self.charge_power, 10))
            self.charge_indicator.fill("red")
            if self.charge_power == 100:
                self.attack_mode = True
                self.gun = True

        if self.attack_mode and self.gun:
            self.gun = False
            self.attack_interval = self.charge_power * player_coif
            fireball_pos = self.rect.topright if self.side else self.rect.topleft
            fireball_pos = list(fireball_pos)
            fireball_pos[0] -= 150 if self.side else 0
            if pg.K_UP in self.mode:
                self.fireballs.add(Enemy_fireball(fireball_pos, self.side, self.charge_power, self.folder))
            else:
                self.fireballs.add(Fireball(fireball_pos, self.side, self.charge_power, self.folder))
            self.charge_power = 0
            self.charge_mode = False
            self.image = self.attack[not self.side]
            self.attack_timer = pg.time.get_ticks()


class Menu:

    def __init__(self, surface):
        self.surface = surface
        self.menu = pygame_menu.Menu(
            title="Menu",
            width=900,
            height=550,
            theme=pygame_menu.themes.THEME_SOLARIZED
        )
        self.menu.add.label("One player")
        self.menu.add.selector("Enemy", [("Маг молний", 0),("Маг земли", 1)], onchange=self.set_enemy)
        self.menu.add.button("Play", self.start_one_player_game)
        self.menu.add.label("Two players")
        self.menu.add.selector("Left", [("Маг молний", 0),("Маг земли", 1), ("Маг огня", 2)], onchange=self.set_left_player)#, #onchange=self.select)
        self.menu.add.selector("Right", [("Маг молний", 0),("Маг земли", 1), ("Маг огня", 2)], onchange=self.set_right_player)#, #onchange=self.)
        self.menu.add.button("Play", self.start_two_player_game)
        self.menu.add.button("exit", exit)
        self.enemy = "lightning wizard"
        self.now_enemy = None
        self.clock = pg.time.Clock()
        self.players = ["lightning wizard", "earth monk", "fire wizard"]
        self.left_player = self.players[0]
        self.right_player = self.players[0]

        self.run()
    
    def set_enemy(self, select, value):
        self.enemy = self.players[value]

    def set_left_player(self, selected, value):
        self.left_player = self.players[value]

    def set_right_player(self, selected, value):
        self.right_player = self.players[value]

    def start_one_player_game(self):
        Game((self.enemy,))

    def start_two_player_game(self):
        Game((self.left_player, self.right_player))

    def run(self):
        self.menu.mainloop(self.surface)

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Битва магов")
class Game:
    def __init__(self, enemy):
        
        self.background = load_image("images/background.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        if len(enemy) == 1:
            self.player = Player("fire wizard", [pg.K_r, pg.K_a, pg.K_SPACE])
            self.enemy = Enemy(enemy[0])
            self.istwo = False
        else:
            self.player = Player(enemy[1], [pg.K_d, pg.K_a, pg.K_SPACE])
            self.istwo = True
            self.enemy = Player(enemy[0], [pg.K_RIGHT, pg.K_LEFT, pg.K_UP], 800)
        self.is_ranning = True
        self.clock = pg.time.Clock()
        self.run()

    def run(self):
        while self.is_ranning:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.is_ranning = False

    def fireball_collide(self, fireballs, Who, power_coif):
        with open("save_rect.json", "w") as file:
            data = {"rect": [Who.rect.x, Who.rect.y, Who.rect.width, Who.rect.height]}
            json.dump(data, file)
        for ball in fireballs:
            with open("save_rect.json", "r") as file:
                g = json.load(file)
                g = g["rect"]
                g = pg.rect.Rect(g[0],g[1],g[2],g[3])
            g.width *= 1
            g.width = int(g.width)
            if g.colliderect(ball):
                Who.health -= ball.power*power_coif
                fireballs.remove(ball)
                break

    def win(self, who, mode):
        if not mode:
            if who == self.player:
                text = "Player died"
            else:
                text = "Player win"
        else:
            if who == self.player:
                text = "Player in left corner win"
            else:
                text = "Player in right corner win"
        text = font.render(text, True, (200,200,200))
        self.is_ranning = False
        run = True
        while run:
            screen.blit(text, (250,250))
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    0/0
                if any(pg.key.get_pressed()) or any(pg.mouse.get_pressed()):
                    run = False
            pg.display.flip()

    def update(self):
        self.player.update()
        self.player.fireballs.update()
        print(self.player)
        if self.istwo:
            self.enemy.update()
        else:
            self.enemy.update(self.player)
        self.enemy.fireballs.update()
        self.fireball_collide(self.player.fireballs, self.enemy, player_coif_damage)
        self.fireball_collide(self.enemy.fireballs, self.player, enemy_coif_damage)
        if self.enemy.health <= 0:
            self.win(self.enemy, self.istwo)
        elif self.player.health <= 0:
            self.win(self.enemy, self.istwo)
        
    def draw(self):
        screen.blit(self.background, (0, 0))
        screen.blit(self.player.image, self.player.rect)
        self.player.fireballs.draw(screen)
        screen.blit(self.enemy.image, self.enemy.rect)
        self.enemy.fireballs.draw(screen)
        pg.draw.rect(screen, (0,0,0), (4,20,player_hp+4, 24))
        pg.draw.rect(screen, (0,0,0), (SCREEN_WIDTH - enemy_hp -6,20,player_hp+4, 24))
        pg.draw.rect(screen, (10,200,20), (6,22,self.player.health, 20))
        pg.draw.rect(screen, (10,200,20), (SCREEN_WIDTH - enemy_hp -4,22,self.enemy.health, 20))
        pg.display.flip()


if __name__ == "__main__":
    Menu(screen)