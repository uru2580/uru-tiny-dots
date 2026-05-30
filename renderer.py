import math
import random

import pyxel

from constants import GROUND_Y, HEIGHT, WIDTH


def draw(game) -> None:
    if game.screen == "title":
        draw_title(game)
        return

    if game.active_game is not None:
        game.active_game.draw()
        if game.paused:
            draw_pause(game)
            return
        if game.game_over:
            draw_game_over(game)
        return

    draw_background(game)
    draw_ground(game)
    draw_items(game)
    draw_hazards(game)
    draw_player(game)
    draw_hud(game)
    if game.paused:
        draw_pause(game)
        return
    if game.game_over:
        draw_game_over(game)


def draw_title(game) -> None:
    draw_background(game)
    pyxel.rect(0, 92, WIDTH, HEIGHT - 92, 0)
    pyxel.text(57, 17, "URU TINY DOTS", 10)
    pyxel.text(52, 30, "SELECT A GAME", 7)

    for index, choice in enumerate(game.game_choices):
        x, y, w, h = game.title_choice_rect(index)
        enabled = choice["enabled"]
        selected = index == game.selected_game_index
        fill = 5 if selected and enabled else 1
        edge = 10 if selected and enabled else 6 if enabled else 13
        text_color = 7 if enabled else 13
        label = choice["name"]

        pyxel.rect(x, y, w, h, fill)
        pyxel.rectb(x, y, w, h, edge)
        if selected and enabled:
            pyxel.tri(x - 8, y + 3, x - 8, y + 9, x - 3, y + 6, 10)
        pyxel.text(x + 4, y + 4, label[:11], text_color)
        if not enabled:
            pyxel.text(x + w - 24, y + 4, "LOCK", 13)

    selected = game.game_choices[game.selected_game_index]
    hi = game.high_scores.get(selected["id"], 0)
    pyxel.text(35, 118, f"HI {hi:05}  DPAD SELECT  A START", 6)


def draw_pause(game) -> None:
    pyxel.rect(28, 38, 136, 58, 0)
    pyxel.rectb(28, 38, 136, 58, 10)
    pyxel.text(81, 48, "PAUSE", 10)
    pyxel.text(54, 60, f"SCORE {game.score:05}", 7)

    for index, choice in enumerate(game.pause_choices):
        x, y, w, h = game.pause_choice_rect(index)
        selected = index == game.selected_pause_index
        fill = 5 if selected else 1
        edge = 10 if selected else 6
        text_color = 7 if selected else 6
        pyxel.rect(x, y, w, h, fill)
        pyxel.rectb(x, y, w, h, edge)
        pyxel.text(x + 4, y + 4, choice[:6], text_color)

    pyxel.text(42, 91, "START RESUME  A SELECT", 6)


def draw_background(game) -> None:
    # sin 波で昼と夜をなめらかに切り替える。
    cycle = (math.sin(pyxel.frame_count / 420) + 1) / 2
    sky = 12 if cycle > 0.55 else 1
    pyxel.cls(sky)
    sun_y = int(20 + cycle * 14)
    moon_y = int(26 + (1 - cycle) * 10)
    if cycle > 0.55:
        pyxel.circ(160, sun_y, 9, 10)
        pyxel.circ(158, sun_y - 2, 6, 9)
    else:
        for star in game.stars:
            star.x -= star.speed
            if star.x < 0:
                star.x = WIDTH
                star.y = random.randrange(8, 70)
            pyxel.pset(int(star.x), int(star.y), 7)
        pyxel.circ(160, moon_y, 8, 7)
        pyxel.circ(164, moon_y - 2, 7, sky)

    for i in range(4):
        x = (i * 62 - int(game.distance / 18) % 62) - 20
        pyxel.rect(x, 72, 38, 32, 5)
        pyxel.rect(x + 8, 62, 14, 42, 5)
        pyxel.rect(x + 28, 82, 24, 22, 5)


def draw_ground(game) -> None:
    for x in range(0, WIDTH, 4):
        if not game.has_ground_at(x + 2):
            continue
        pyxel.rect(x, GROUND_Y, 4, HEIGHT - GROUND_Y, 3)
        pyxel.line(x, GROUND_Y, x + 3, GROUND_Y, 11)

    for gap in game.gaps:
        gx = int(gap.x)
        if -gap.w < gx < WIDTH:
            pyxel.line(gx, GROUND_Y, gx, HEIGHT, 0)
            pyxel.line(gx + gap.w, GROUND_Y, gx + gap.w, HEIGHT, 0)
            pyxel.rect(gx + 1, GROUND_Y + 5, max(0, gap.w - 1), HEIGHT - GROUND_Y - 5, 0)

    for x in range(-16, WIDTH + 16, 16):
        sx = x - int(game.ground_scroll)
        if game.has_ground_at(sx + 4):
            pyxel.rect(sx, GROUND_Y + 7, 8, 2, 4)
            pyxel.pset(sx + 12, GROUND_Y + 15, 9)


def draw_player(game) -> None:
    player = game.player
    if player.invincible_timer and pyxel.frame_count % 6 < 3:
        suit = 10
    elif player.flash_timer:
        suit = 7
    else:
        suit = 9
    x = int(player.x)
    y = int(player.y)
    skin = 15
    hair = 4
    shoe = 5
    if player.sliding:
        pyxel.rect(x - 3, y + 5, 15, 5, suit)
        pyxel.circ(x + 9, y + 4, 4, skin)
        pyxel.rect(x + 5, y + 1, 7, 3, hair)
        pyxel.pset(x + 10, y + 4, 0)
        pyxel.rect(x - 5, y + 8, 6, 3, shoe)
        pyxel.rect(x + 9, y + 9, 7, 2, shoe)
    else:
        step = 1 if pyxel.frame_count // 5 % 2 == 0 and player.on_ground else -1
        pyxel.circ(x + 5, y + 3, 4, skin)
        pyxel.rect(x + 2, y, 7, 3, hair)
        pyxel.pset(x + 7, y + 3, 0)
        pyxel.rect(x + 2, y + 7, 7, 7, suit)
        pyxel.line(x + 2, y + 9, x - 2, y + 11 + step, skin)
        pyxel.line(x + 9, y + 9, x + 13, y + 11 - step, skin)
        pyxel.line(x + 4, y + 14, x + 2, y + 18 + step, shoe)
        pyxel.line(x + 7, y + 14, x + 10, y + 18 - step, shoe)
        pyxel.pset(x + 1, y + 4, 8)


def draw_hazards(game) -> None:
    for hazard in game.hazards:
        x = int(hazard.x)
        y = int(hazard.y)
        if hazard.kind == "stomp":
            pyxel.rect(x, y + 2, hazard.w, hazard.h - 2, hazard.color)
            pyxel.circ(x + 3, y + 2, 3, hazard.color)
            pyxel.circ(x + 7, y + 2, 3, hazard.color)
            pyxel.pset(x + 2, y + 3, 0)
            pyxel.pset(x + 7, y + 3, 0)
        elif hazard.kind == "spikes":
            for sx in range(x, x + hazard.w, 7):
                pyxel.tri(sx, y + hazard.h, sx + 3, y, sx + 7, y + hazard.h, hazard.color)
        elif hazard.kind == "overhead":
            pyxel.rect(x, y, hazard.w, hazard.h, hazard.color)
            pyxel.rect(x + 3, y + hazard.h, 3, 7, hazard.color)
            pyxel.rect(x + hazard.w - 6, y + hazard.h, 3, 7, hazard.color)
        elif hazard.kind == "flyer":
            wing = 2 if pyxel.frame_count // 4 % 2 == 0 else -1
            pyxel.circ(x + 5, y + 5, 5, hazard.color)
            pyxel.tri(x, y + 5, x - 6, y + wing, x + 1, y + 8, 7)
            pyxel.tri(x + 10, y + 5, x + 16, y + wing, x + 9, y + 8, 7)
            pyxel.pset(x + 7, y + 4, 0)
        elif hazard.kind == "jumper":
            bob = 1 if pyxel.frame_count // 8 % 2 == 0 else -1
            pyxel.circ(x + 7, y + 6 + bob, 6, hazard.color)
            pyxel.rect(x + 2, y + 10 + bob, 10, 4, hazard.color)
            pyxel.line(x + 2, y + 6 + bob, x - 4, y + 2, 10)
            pyxel.line(x + 12, y + 6 + bob, x + 18, y + 2, 10)
            pyxel.pset(x + 5, y + 5 + bob, 0)
            pyxel.pset(x + 9, y + 5 + bob, 0)
        else:
            pyxel.rect(x, y, hazard.w, hazard.h, hazard.color)
            pyxel.line(x, y, x + hazard.w - 1, y + hazard.h - 1, 0)


def draw_items(game) -> None:
    for x, y in game.items:
        pulse = 1 if pyxel.frame_count % 20 < 10 else 0
        pyxel.circ(int(x), int(y), 4 + pulse, 10)
        pyxel.circ(int(x), int(y), 2, 7)


def draw_hud(game) -> None:
    pyxel.text(5, 5, f"SCORE {game.score:05}", 7)
    pyxel.text(5, 14, f"HI {game.high_score:05}", 6)
    if game.combo > 1:
        pyxel.text(124, 5, f"COMBO x{game.combo}", 10)
    if game.player.invincible_timer:
        pyxel.text(122, 14, "INVINCIBLE", 10)
    draw_jump_button(game)


def draw_jump_button(game) -> None:
    x, y, w, h = game.jump_button_rect
    pressed = x <= pyxel.mouse_x <= x + w and y <= pyxel.mouse_y <= y + h and pyxel.btn(pyxel.MOUSE_BUTTON_LEFT)
    fill = 6 if pressed else 1
    edge = 10 if pressed else 7
    pyxel.rect(x, y, w, h, fill)
    pyxel.rectb(x, y, w, h, edge)
    pyxel.tri(x + 8, y + 11, x + 15, y + 5, x + 22, y + 11, edge)
    pyxel.text(x + 6, y + 14, "JMP", edge)


def draw_game_over(game) -> None:
    shake = 1 if game.game_over_timer < 24 and game.game_over_timer % 4 < 2 else 0
    pyxel.rect(30 + shake, 34, 132, 62, 0)
    pyxel.rectb(30 + shake, 34, 132, 62, 8)
    pyxel.text(70 + shake, 45, "GAME OVER", 8)
    pyxel.text(55 + shake, 58, f"SCORE {game.score:05}", 7)
    pyxel.text(55 + shake, 68, f"HIGH  {game.high_score:05}", 10)

    for index, choice in enumerate(game.game_over_choices):
        x, y, w, h = game.game_over_choice_rect(index)
        selected = index == game.selected_game_over_index
        fill = 5 if selected else 1
        edge = 10 if selected else 6
        text_color = 7 if selected else 6
        pyxel.rect(x + shake, y, w, h, fill)
        pyxel.rectb(x + shake, y, w, h, edge)
        pyxel.text(x + shake + 10, y + 4, choice, text_color)

    pyxel.text(42 + shake, 91, "DPAD SELECT  A DECIDE", 6)
