import random
import arcade
from arcade.examples.snow import MyGame
from pyglet.math import Vec2
from constants import *

class Explosion(arcade.Sprite):
    def __init__(self, texture_list):
        super().__init__()

        # Explosion
        self.textures = texture_list
        self.current_texture = 0

    def update(self):
        super().update()
        self.current_texture += 1

        if self.current_texture < len(self.textures):
            self.set_texture(self.current_texture)
        else:
            self.kill()


class MenuView(arcade.View):
    music = arcade.load_sound('Sprite/On My Way.wav',False)
    arcade.play_sound(music,0.5,0.0,True)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        self.clear()

        arcade.draw_text(f"{SCREEN_TITLE}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.BLACK, font_size=50,
                         anchor_x="center")

        arcade.draw_text("Clique com o mouse para jogar", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 75,
                         arcade.color.GRAY, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game = MyGame()
        game.setup()
        self.window.show_view(game)


class MyGame(arcade.View):
    def __init__(self):
        super().__init__()

        self.player_list = None
        self.enemy_list = None
        self.player_bullet_list = None
        self.enemy_bullet_list = None
        self.shield_list = None
        self.explosions_list = None

        self.camera_sprites = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera_gui = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Background
        self.background = arcade.load_texture("Sprite/Background.jpg")

        # Estado do jogo
        self.game_state = PLAY_GAME

        # set up dos Inimigos
        self.enemy_count = 5
        self.enemy_diff = 5
        self.enemy_reload = 10

        # set up do Player
        self.player_sprite = None
        self.player_life = 1
        self.score = 0

        # set up timer
        self.total_time = 0
        # Enemy movement
        self.enemy_change_x = -ENEMY_SPEED

        # Don't show the mouse cursor
        self.window.set_mouse_visible(False)

        # Load sounds. Sounds from kenney.nl
        self.gun_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.hit_sound = arcade.load_sound(":resources:sounds/hit5.wav")

        # arcade.configure_logging()

        # player move
        self.player_x = 100
        self.player_y = 100
        self.player_spd = PLAYER_SPD
        self.right = False
        self.left = False
        self.up = False
        self.down = False
        self.turbo = False

        # Explosion Gif
        self.explosion_texture_list = []

        columns = 4
        count = 16
        sprite_width = 60
        sprite_height = 60
        file_name = "Sprite/Explosion.png"

        self.explosion_texture_list = arcade.load_spritesheet(file_name, sprite_width, sprite_height, columns, count)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def setup_level_one(self):
        for i in range(self.enemy_diff):
            enemy = arcade.Sprite("Sprite/spr_enemy.png")
            enemy.scale = SPRITE_SCALING_enemy

            enemy.center_x = SCREEN_WIDTH - enemy.width
            enemy.center_y = SCREEN_HEIGHT - enemy.height

            self.enemy_list.append(enemy)
            self.enemy_count += 1

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            pause = PauseView(self)
            self.window.show_view(pause)

        if self.game_state != 1:
            if key == arcade.key.UP or key == arcade.key.W:
                self.up = True
            elif key == arcade.key.DOWN or key == arcade.key.S:
                self.down = True
            elif key == arcade.key.LEFT or key == arcade.key.A:
                self.left = True
            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.right = True
            elif key == arcade.key.LALT:
                self.turbo = True

            if key == arcade.key.SPACE:
                if len(self.player_bullet_list) < MAX_PLAYER_BULLETS:
                    arcade.play_sound(self.gun_sound)

                    bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", SPRITE_SCALING_LASER)

                    bullet.angle = 90

                    bullet.change_y = BULLET_SPEED

                    bullet.center_x = self.player_sprite.center_x
                    bullet.bottom = self.player_sprite.top

                    self.player_bullet_list.append(bullet)

    def on_key_release(self, key, modifiers):
        if self.game_state != 1:
            if key == arcade.key.UP or key == arcade.key.W:
                self.up = False
            elif key == arcade.key.DOWN or key == arcade.key.S:
                self.down = False
            elif key == arcade.key.LEFT or key == arcade.key.A:
                self.left = False
            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.right = False
            if key == arcade.key.LALT:
                self.turbo = False

    def update_enemies(self):
        for enemy in self.enemy_list:
            enemy.center_y -= ENEMY_MOVE_DOWN_AMOUNT

    def allow_enemies_to_fire(self):
        x_spawn = []
        for enemy in self.enemy_list:
            chance = 4 + len(self.enemy_list) * 4

            if random.randrange(chance) == 0 and enemy.center_x not in x_spawn and self.enemy_reload >= 10:
                bullet = arcade.Sprite(":resources:images/space_shooter/laserRed01.png", SPRITE_SCALING_LASER)

                bullet.angle = 180

                bullet.change_y = -BULLET_SPEED

                bullet.center_x = enemy.center_x
                bullet.top = enemy.bottom

                self.enemy_bullet_list.append(bullet)

                self.enemy_reload = 0

                x_spawn.append(enemy.center_x)

        self.enemy_reload += 1

    def process_enemy_bullets(self):

        self.enemy_bullet_list.update()

        for bullet in self.enemy_bullet_list:
            if arcade.check_for_collision_with_list(self.player_sprite, self.enemy_bullet_list):
                self.game_state = GAME_OVER

            if bullet.top < 0:
                bullet.remove_from_sprite_lists()

        for bullet in self.enemy_bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.player_list)

            if len(hit_list) > 0:
                explosion = Explosion(self.explosion_texture_list)

                explosion.center_x = hit_list[0].center_x
                explosion.center_y = hit_list[0].center_y

                self.explosions_list.append(explosion)

                explosion.update()

                bullet.remove_from_sprite_lists()
                self.player_list[0].remove_from_sprite_lists()

    def process_player_bullets(self):
        self.player_bullet_list.update()

        for bullet in self.player_bullet_list:

            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)

            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            for enemy in hit_list:
                if len(hit_list) > 0:
                    explosion = Explosion(self.explosion_texture_list)

                    explosion.center_x = hit_list[0].center_x
                    explosion.center_y = hit_list[0].center_y

                    self.explosions_list.append(explosion)

                    explosion.update()

                    enemy.remove_from_sprite_lists()

                self.score += 1

                # Hit Sound
                arcade.play_sound(self.hit_sound)

            if bullet.bottom > SCREEN_HEIGHT:
                bullet.remove_from_sprite_lists()

    def process_collision(self):
        self.player_list.update()
        self.enemy_list.update()

        for player in self.player_list:

            hit_list = arcade.check_for_collision_with_list(player, self.enemy_list)

            if len(hit_list) > 0:
                explosion = Explosion(self.explosion_texture_list)

                explosion.center_x = hit_list[0].center_x
                explosion.center_y = hit_list[0].center_y

                self.explosions_list.append(explosion)

                explosion.update()

                for enemy in self.enemy_list:
                    hit = arcade.check_for_collision_with_list(enemy, self.player_list)

                    if len(hit) > 0:
                        explosion = Explosion(self.explosion_texture_list)

                        explosion.center_x = hit[0].center_x
                        explosion.center_y = hit[0].center_y

                        self.explosions_list.append(explosion)

                        explosion.update()

                        enemy.remove_from_sprite_lists()

                player.remove_from_sprite_lists()

                self.game_state = GAME_OVER

    def on_draw(self):
        self.clear()

        arcade.draw_texture_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        arcade.draw_texture_rectangle(SCREEN_WIDTH, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        arcade.draw_texture_rectangle(0, SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        arcade.draw_texture_rectangle(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)

        self.enemy_list.draw()
        self.player_bullet_list.draw()
        self.enemy_bullet_list.draw()
        self.shield_list.draw()
        self.player_list.draw()
        self.explosions_list.draw()

        arcade.draw_text(f"Score: {self.score}", 10, 20, arcade.color.WHITE, 14)

        if self.game_state == GAME_OVER:
            arcade.draw_text("GAME OVER", 180, 300, arcade.color.WHITE, 55)
            arcade.draw_text("Press Esc and Them Enter To Restart", 125, 260, arcade.color.WHITE, 25)
            self.window.set_mouse_visible(True)

    def setup(self):
        self.game_state = PLAY_GAME

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player_bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.explosions_list = arcade.SpriteList()
        self.shield_list = arcade.SpriteList(is_static=True)

        # Set up the player
        self.score = 0

        self.player_sprite = arcade.Sprite("Sprite/spr_player.png", SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = 400
        self.player_sprite.center_y = 100
        self.player_list.append(self.player_sprite)

        # self.setup_level_one()

    def on_update(self, delta_time):
        if self.turbo:
            self.player_spd = 650
        else:
            self.player_spd = PLAYER_SPD
        if self.right:
            self.player_sprite.center_x += self.player_spd * delta_time
        if self.left:
            self.player_sprite.center_x -= self.player_spd * delta_time
        if self.up:
            self.player_sprite.center_y += self.player_spd * delta_time
        if self.down:
            self.player_sprite.center_y -= self.player_spd * delta_time

        self.total_time += delta_time

        self.explosions_list.update()
        self.allow_enemies_to_fire()
        self.process_enemy_bullets()
        self.process_player_bullets()
        self.process_collision()

        if self.total_time > self.enemy_diff and self.score < 20:
            for i in range(self.enemy_count):

                enemy = arcade.Sprite("Sprite/spr_enemy.png", SPRITE_SCALING_enemy)

                enemy_placed_successfully = False

                while not enemy_placed_successfully:
                    enemy.center_x = random.randrange(SCREEN_WIDTH)
                    enemy.center_y = random.randrange(SCREEN_HEIGHT) + 500

                    enemy_hit_list = arcade.check_for_collision_with_list(enemy, self.enemy_list)

                    if len(enemy_hit_list) == 0:
                        enemy_placed_successfully = True

                self.enemy_list.append(enemy)

            self.total_time = 0.0
            self.enemy_diff -= 0.005

        if self.score >= 20:
            self.game_state = WIN_GAME

        self.update_enemies()

        if self.game_state == GAME_OVER:
            return

        if self.game_state == WIN_GAME:
            win = VictoryView(self)
            self.window.show_view(win)


class PauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view

    def on_show_view(self):
        arcade.set_background_color(arcade.color.ORANGE)

    def on_draw(self):
        self.clear()

        player_sprite = self.game_view.player_sprite
        player_sprite.draw()

        arcade.draw_lrtb_rectangle_filled(left=player_sprite.left,
                                          right=player_sprite.right,
                                          top=player_sprite.top,
                                          bottom=player_sprite.bottom,
                                          color=arcade.color.ORANGE + (200,))

        arcade.draw_text("PAUSED", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50,
                         arcade.color.BLACK, font_size=50, anchor_x="center")

        # Show tip to return or reset
        arcade.draw_text("Press Esc. to return",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")
        arcade.draw_text("Press Enter to reset",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2 - 30,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.game_view)
        elif key == arcade.key.ENTER:
            game = MyGame()
            game.setup()
            self.window.show_view(game)

class VictoryView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view

    def on_draw(self):
        self.clear()

        player_sprite = self.game_view.player_sprite
        player_sprite.draw()

        arcade.draw_text("You Win, The aliance win this battle", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50,
                         arcade.color.WHITE, font_size=30, anchor_x="center")

        arcade.draw_text("But not the war", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 5,
                         arcade.color.RED, font_size=25, anchor_x="center")

        arcade.draw_text("To play again press Enter", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 80,
                         arcade.color.WHITE, font_size=25, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            game = MyGame()
            game.setup()
            self.window.show_view(game)

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start = MenuView()
    window.show_view(start)
    arcade.run()


if __name__ == "__main__":
    main()
