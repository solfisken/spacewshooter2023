from typing import Any
import pygame
import random
from pygame.locals import *

from pygame.sprite import Group

pygame.init()

print(pygame.ver)

# create window
screen = pygame.display.set_mode((800, 600))

# colors
red = (255, 0, 0)
white = (255, 255, 255)
green = (0, 200, 0)


class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y

        self.lives = 3
        self.score = 0
        self.shield_active = False

        # ship
        image = pygame.image.load(
            "/home/kvb/src/Hack2023/SpaceShooter/images/spaceship.png"
        )
        image_scale = 40 / image.get_rect().width
        new_width = int(image.get_rect().width * image_scale)
        new_height = int(image.get_rect().height * image_scale)
        scaled_size = (new_width, new_height)
        self.image = pygame.transform.scale(image, scaled_size)

        self.rect = self.image.get_rect()

        # for damage
        self.invincibility_frames = 0
        damage_image = pygame.image.load(
            "/home/kvb/src/Hack2023/SpaceShooter/images/damage.png"
        )
        image_scale = 80 / damage_image.get_rect().width
        new_width = damage_image.get_rect().width * image_scale
        new_height = damage_image.get_rect().height * image_scale
        scaled_size = (new_width, new_height)
        self.damage_image = pygame.transform.scale(damage_image, scaled_size)

    def activate_shield(self, duration=5000):
        if not self.shield_active:  # Activate shield only if not already active
            self.shield_active = True
            self.shield_end_time = pygame.time.get_ticks() + duration
            self.original_image = self.image.copy()  # Save the original image
            self.image.set_alpha(128)

    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y

        if self.invincibility_frames > 0:
            self.invincibility_frames -= 1

        if self.invincibility_frames < 0:
            self.invincibility_frames = 0

        if self.shield_active and pygame.time.get_ticks() > self.shield_end_time:
            self.shield_active = False
            self.image.set_alpha(255)
            self.image = self.original_image

    def draw_damage(self):
        if self.invincibility_frames > 0:
            damage_x = self.x - self.image.get_width() / 3
            damage_y = self.y - self.image.get_height() / 2
            screen.blit(self.damage_image, (damage_x, damage_y))


class Rock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y

        # rand color, size and number for image
        color = random.choice(["brown", "grey"])
        size = random.choice(["big", "small"])
        number = random.randint(1, 2)
        self.image = pygame.image.load(
            f"/home/kvb/src/Hack2023/SpaceShooter/images/rock/{color}_{size}_{number}.png"
        )

        # hits and score
        if size == "big":
            self.hits = 3
            self.points = 5
        else:
            self.hits = 1
            self.points = 2

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        # move rock down the screen
        self.rect.y += 1

        # collision with ship
        if pygame.sprite.spritecollide(self, spaceship_group, False):
            if not spaceship.shield_active:
                self.kill()
                # loose life in spaceship is hit
                if spaceship.invincibility_frames == 0:
                    spaceship.lives -= 1
                    print(f"Lives decreased: {spaceship.lives}")
                    # show dmg for 50 frames
                    spaceship.invincibility_frames = 50
            else:
                pass

        # collision with bullets
        if pygame.sprite.spritecollide(self, bullets_group, True):
            self.hits -= 1
            # add score
            if self.hits == 0:
                spaceship.score += self.points

        # remove rock if hits 0
        if self.hits == 0:
            self.kill()

        # remove rock if off screen
        if self.rect.top > 600:
            self.kill()


class Shootingenemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # load the enemy ship image
        image = pygame.image.load(
            "/home/kvb/src/Hack2023/SpaceShooter/images/enemy/enemy.png"
        )
        # match size spaceship
        image_scale = spaceship.rect.width / image.get_rect().width

        # scale the enemy ship image
        new_width = int(image.get_rect().width * image_scale)
        new_height = int(image.get_rect().height * image_scale)
        scaled_size = (new_width, new_height)
        self.image = pygame.transform.scale(image, scaled_size)

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.last_shot = pygame.time.get_ticks()
        self.shot_interval = 1000
        self.hits = 3

    def update(self):
        self.rect.y += 1
        # shoot bullets
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shot_interval:
            self.last_shot = current_time

            enemy_bullet = Enemybullet(self.rect.centerx, self.rect.bottom)
            enemy_bullets_group.add(enemy_bullet)

        # collision with bullets
        if pygame.sprite.spritecollide(self, bullets_group, True):
            self.hits -= 1
            if self.hits == 0:
                self.kill()
                spaceship.score += 10

        # collision with ship
        if pygame.sprite.spritecollide(self, spaceship_group, False):
            if not spaceship.shield_active:
                self.kill()
                spaceship.lives -= 1
                print(f"Lives decreased: {spaceship.lives}")
            else:
                pass

        # remove ship if off screen
        if self.rect.top > 600:
            self.kill()


class Enemybullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.rect = Rect(x - 2, y, 4, 8)

    def draw(self):
        for w in range(self.rect.width):
            for h in range(self.rect.height):
                screen.set_at((self.rect.x + w, self.rect.y + h), green)

    def update(self):
        # bullet shoots down the screen
        self.rect.y += 5
        # display/remove bullet
        if self.rect.bottom > 0:
            self.draw()
        else:
            self.kill()
        # hit ship with bullet
        if pygame.sprite.spritecollide(spaceship, enemy_bullets_group, True):
            if not spaceship.shield_active:
                spaceship.lives -= 1
                print(f"Lives decreased: {spaceship.lives}")
            else:
                pass


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.rect = Rect(x - 2, y, 4, 8)

    def draw(self):
        for w in range(self.rect.width):
            for h in range(self.rect.height):
                screen.set_at((self.rect.x + w, self.rect.y + h), red)

    def update(self):
        # bullet shoots up the screen
        self.rect.y -= 5
        # display/remove bullet
        if self.rect.bottom > 0:
            self.draw()
        else:
            self.kill()


class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type="shield"):
        pygame.sprite.Sprite.__init__(self)
        self.powerup_type = powerup_type
        if powerup_type == "shield":
            self.image = pygame.image.load(
                "/home/kvb/src/Hack2023/SpaceShooter/images/powerup/shield_blue.png"
            )
        else:
            self.image = pygame.image.load(
                "/home/kvb/src/Hack2023/SpaceShooter/images/powerup/pill_red.png"
            )
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        # move powerup down screen
        self.rect.y += 1

        # collision with ship
        if pygame.sprite.spritecollide(self, spaceship_group, dokill=False):
            self.kill()
            if self.powerup_type == "shield":
                spaceship.activate_shield()
                print()  # Activate shield
            else:
                spaceship.lives += 1  # Increment lives
                print(f"Lives increased: {spaceship.lives}")

        # remove powerup off screen
        if self.rect.top > 600:
            self.kill()


# create sprite groups
spaceship_group = pygame.sprite.Group()
rock_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
powerup_group = pygame.sprite.Group()
shooting_enemies_group = pygame.sprite.Group()
enemy_bullets_group = pygame.sprite.Group()

# background
bg = pygame.image.load("/home/kvb/src/Hack2023/SpaceShooter/images/background.jpg")


# create Spaceship
Spaceship_x = 375
Spaceship_y = 550
spaceship = Spaceship(Spaceship_x, Spaceship_y)
spaceship_group.add(spaceship)

# bullets
bullet_cooldown = 200
last_bullet = pygame.time.get_ticks() - bullet_cooldown


# score text
def write_screentext(str, color, x, y):
    font = pygame.font.Font("freesansbold.ttf", 16)
    text = font.render(str, True, color)
    text_rect = text.get_rect()
    text_rect.center = (x, y)
    screen.blit(text, text_rect)


# enemies
def create_rock():
    rock_x = random.randint(50, 750 - 50)
    rock_y = 0
    rock = Rock(rock_x, rock_y)
    rock_group.add(rock)


create_rock()


# shooting enemies
def create_shooting_enemy():
    shooting_enemy_x = random.randint(50, 750 - 50)
    shooting_enemy_y = 0
    shooting_enemy = Shootingenemy(shooting_enemy_x, shooting_enemy_y)
    shooting_enemies_group.add(shooting_enemy)


# powerup
def create_powerup():
    powerup_x = random.randint(50, 750 - 50)
    powerup_y = 0
    powerup_type = random.choice(["shield", "life"])
    powerup = Powerup(powerup_x, powerup_y, powerup_type)
    powerup_group.add(powerup)


create_powerup()


# game loop
clock = pygame.time.Clock()
fps = 60
running = True
gameover = False
loop_ctr = 0
while running:
    loop_ctr += 1
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # move player
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and spaceship.rect.left > 0:
        spaceship.x -= 5
    if keys[pygame.K_RIGHT] and spaceship.rect.right < 800:
        spaceship.x += 5

    # shoot bullets
    if keys[pygame.K_SPACE]:
        # cooldown
        current_time = pygame.time.get_ticks()
        if current_time - last_bullet > bullet_cooldown:
            last_bullet = current_time
            bullet = Bullet(spaceship.rect.centerx, spaceship.rect.y)
            bullets_group.add(bullet)

    # background
    for bg_x in range(0, 800, 800):
        for bg_y in range(0, 600, 600):
            screen.blit(bg, (bg_x, bg_y))

    # move/draw spaceship
    spaceship_group.update()
    spaceship_group.draw(screen)

    # move/draw shooting enemies
    shooting_enemies_group.update()
    shooting_enemies_group.draw(screen)

    # move/draw enemy bullets
    enemy_bullets_group.update()

    # draw powerup
    powerup_group.update()
    powerup_group.draw(screen)

    # draw damage
    spaceship.draw_damage()

    # move/draw bullets
    bullets_group.update()

    # move/draw rocks
    rock_group.update()

    if loop_ctr % (10 * fps) == 0:
        create_shooting_enemy()

    # create new rock at 1 second intervals
    if loop_ctr % 100 == 0:
        create_rock()

    # create new powerup at 1 minute intervals
    if loop_ctr % 2000 == 0:
        create_powerup()

    # move enemies
    rock_group.update()
    rock_group.draw(screen)

    # draw score and lives
    write_screentext(f"Score: {spaceship.score}", white, 50, 10)
    write_screentext(f"Lives: {spaceship.lives}", white, 750, 10)

    pygame.display.update()

    # check for game over
    if spaceship.lives == 0:
        gameover = True

    while gameover:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                gameover = False

        gameover_text = "GAME OVER"
        write_screentext(gameover_text, white, 400, 300)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            # reset game
            rock_group.empty()
            bullets_group.empty()
            spaceship_group.empty()
            powerup_group.empty()
            enemy_bullets_group.empty()
            shooting_enemies_group.empty()

            spaceship = Spaceship(Spaceship_x, Spaceship_y)
            spaceship_group.add(spaceship)

            gameover = False
        elif keys[pygame.K_q]:
            running = False
            gameover = False

        pygame.display.update()

# exit the game
pygame.quit()
