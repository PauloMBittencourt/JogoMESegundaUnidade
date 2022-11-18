import random
import arcade
from arcade.examples.snow import MyGame

from constants import *


class MenuView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

        arcade.set_viewport(0, self.window.width, 0, self.window.height)

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


class MyGame(arcade.Window):

    def __init__(self):
        super().__init__()

        self.player_list = None
        self.enemy_list = None
        self.player_bullet_list = None
        self.enemy_bullet_list = None
        self.shield_list = None

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
        self.set_mouse_visible(False)

        # Load sounds. Sounds from kenney.nl
        self.gun_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.hit_sound = arcade.load_sound(":resources:sounds/hit5.wav")

        # arcade.configure_logging()

        # player move
        self.player_x = 100
        self.player_y = 100
        self.right = False
        self.left = False
        self.up = False
        self.down = False

        arcade.set_background_color(arcade.color.AMAZON)
    def setup_level_one(self):
        for i in range(self.enemy_diff):
            enemy = arcade.Sprite("Sprite/enemySpaceship2.png")
            enemy.scale = SPRITE_SCALING_enemy

            enemy.center_x = SCREEN_WIDTH - enemy.width
            enemy.center_y = SCREEN_HEIGHT - enemy.height

            self.enemy_list.append(enemy)
            self.enemy_count += 1

    def setup(self):
        self.game_state = PLAY_GAME

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player_bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.shield_list = arcade.SpriteList(is_static=True)

        # Set up the player
        self.score = 0

        self.player_sprite = arcade.Sprite("Sprite/playerSpaceship.png", SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = 400
        self.player_sprite.center_y = 100
        self.player_list.append(self.player_sprite)

        self.setup_level_one()

    def on_draw(self):
        self.clear()

        arcade.draw_texture_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)

        self.enemy_list.draw()
        self.player_bullet_list.draw()
        self.enemy_bullet_list.draw()
        self.shield_list.draw()
        self.player_list.draw()

        arcade.draw_text(f"Score: {self.score}", 10, 20, arcade.color.WHITE, 14)

        arcade.draw_text(f"Enemy count {self.enemy_count}", 500, 300, arcade.color.WHITE, 14)

        if self.game_state == GAME_OVER:
            arcade.draw_text("GAME OVER", 180, 300, arcade.color.WHITE, 55)
            self.set_mouse_visible(True)

    def on_key_press(self, key, modifiers):
        if self.game_state != 1:
            if key == arcade.key.UP or key == arcade.key.W:
                self.up = True
            elif key == arcade.key.DOWN or key == arcade.key.S:
                self.down = True
            elif key == arcade.key.LEFT or key == arcade.key.A:
                self.left = True
            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.right = True

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

        # Move the bullets
        self.enemy_bullet_list.update()

        # Loop through each bullet
        for bullet in self.enemy_bullet_list:
            # Check this bullet to see if it hit a shield
            hit_list = arcade.check_for_collision_with_list(bullet, self.shield_list)

            # If it did, get rid of the bullet and shield blocks
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()
                for shield in hit_list:
                    shield.remove_from_sprite_lists()
                continue

            # See if the player got hit with a bullet
            if arcade.check_for_collision_with_list(self.player_sprite, self.enemy_bullet_list):
                self.game_state = GAME_OVER

            # If the bullet falls off the screen get rid of it
            if bullet.top < 0:
                bullet.remove_from_sprite_lists()

    def process_player_bullets(self):

        # Move the bullets
        self.player_bullet_list.update()

        # Loop through each bullet
        for bullet in self.player_bullet_list:

            # Check this bullet to see if it hit a enemy
            hit_list = arcade.check_for_collision_with_list(bullet, self.shield_list)
            # If it did, get rid of the bullet
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()
                for shield in hit_list:
                    shield.remove_from_sprite_lists()
                continue

            # Check this bullet to see if it hit a enemy
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)

            # If it did, get rid of the bullet
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            # For every enemy we hit, add to the score and remove the enemy
            for enemy in hit_list:
                enemy.remove_from_sprite_lists()
                self.score += 1

                # Hit Sound
                arcade.play_sound(self.hit_sound)

            # If the bullet flies off-screen, remove it.
            if bullet.bottom > SCREEN_HEIGHT:
                bullet.remove_from_sprite_lists()

    def on_update(self, delta_time):
        if self.right:
            self.player_sprite.center_x += PLAYER_SPD * delta_time
        if self.left:
            self.player_sprite.center_x -= PLAYER_SPD * delta_time
        if self.up:
            self.player_sprite.center_y += PLAYER_SPD * delta_time
        if self.down:
            self.player_sprite.center_y -= PLAYER_SPD * delta_time

        if self.game_state == GAME_OVER:
            return

        self.total_time += delta_time

        self.allow_enemies_to_fire()
        self.process_enemy_bullets()
        self.process_player_bullets()

        # if len(self.enemy_list) == 0:
        #   self.setup_level_one()

        if self.total_time > self.enemy_diff and self.score < 10:
            for i in range(self.enemy_count):

                enemy = arcade.Sprite("Sprite/enemySpaceship2.png", SPRITE_SCALING_enemy)

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

        self.update_enemies()


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

        # draw an orange filter over him
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
        if key == arcade.key.ESCAPE:  # resume game
            self.window.show_view(self.game_view)
        elif key == arcade.key.ENTER:  # reset game
            game = MyGame()
            self.window.show_view(game)


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start = MenuView()
    window.show_view(start)
    arcade.run()


if __name__ == "__main__":
    main()
