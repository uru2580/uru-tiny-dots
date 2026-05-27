import json
import random

import pyxel

import renderer
from audio import setup_sounds
from constants import HEIGHT, JUMP_BUTTON_RECT, SAVE_FILE, WIDTH
from entities import Gap, Hazard, Player, Star


class RunnerGame:
    def __init__(self) -> None:
        pyxel.init(WIDTH, HEIGHT, title="Uru Tiny Dots", fps=60)
        pyxel.mouse(True)
        self.high_score = self.load_high_score()
        self.stars = [Star(random.randrange(WIDTH), random.randrange(8, 70), random.uniform(0.15, 0.6)) for _ in range(36)]
        setup_sounds()
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self) -> None:
        self.player = Player()
        self.hazards: list[Hazard] = []
        self.gaps: list[Gap] = []
        self.items: list[tuple[float, float]] = []
        self.score = 0
        self.combo = 0
        self.combo_timer = 0
        self.distance = 0.0
        self.speed = 2.4
        self.spawn_timer = 70
        self.item_timer = 420
        self.ground_scroll = 0.0
        self.game_over = False
        self.game_over_timer = 0
        self.bgm_mode = ""
        self.jump_button_rect = JUMP_BUTTON_RECT
        self.last_pattern = ""
        self.play_bgm("normal")

    def load_high_score(self) -> int:
        try:
            return int(json.loads(SAVE_FILE.read_text(encoding="utf-8")).get("high_score", 0))
        except (FileNotFoundError, ValueError, json.JSONDecodeError, TypeError):
            return 0

    def save_high_score(self) -> None:
        SAVE_FILE.write_text(json.dumps({"high_score": self.high_score}, indent=2), encoding="utf-8")

    def play_bgm(self, mode: str) -> None:
        if self.bgm_mode == mode:
            return
        self.bgm_mode = mode
        pyxel.playm(1 if mode == "invincible" else 0, loop=True)

    def update(self) -> None:
        if self.game_over:
            self.game_over_timer += 1
            if self.jump_pressed() or pyxel.btnp(pyxel.KEY_R):
                self.reset()
            return

        # 崖の上では着地させず、落下したらゲームオーバーにする。
        has_ground = self.has_ground_at(self.player.x + self.player.w / 2)
        self.player.update(has_ground, self.jump_pressed())
        if self.player.y > HEIGHT + 10:
            self.end_game()
            return

        self.play_bgm("invincible" if self.player.invincible_timer else "normal")
        self.distance += self.speed
        self.score = int(self.distance / 4) + self.combo * 50
        self.speed = min(5.2, 2.4 + self.distance / 7000)
        self.ground_scroll = (self.ground_scroll + self.speed) % 16

        self.update_spawns()
        self.update_gaps()
        self.update_hazards()
        self.update_items()

        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

    def jump_pressed(self) -> bool:
        keyboard = pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
        if keyboard:
            return True

        x, y, w, h = self.jump_button_rect
        mouse_hit = x <= pyxel.mouse_x <= x + w and y <= pyxel.mouse_y <= y + h
        return mouse_hit and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)

    def update_spawns(self) -> None:
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            if self.distance > 550 and random.random() < 0.22:
                self.gaps.append(Gap(WIDTH + 12, random.randint(28, 44), random.uniform(0.96, 1.08)))
                self.spawn_timer = random.randint(70, 116)
            else:
                self.spawn_hazard_pattern(WIDTH + 8)
                self.spawn_timer = random.randint(50, 98)

        self.item_timer -= 1
        if self.item_timer <= 0:
            self.items.append((WIDTH + 8, random.choice([58, 70, 82])))
            self.item_timer = random.randint(430, 620)

    def spawn_hazard_pattern(self, x: int) -> None:
        patterns = [
            ("double_stomp", [("stomp", 0, 10, 10, 11), ("stomp", 28, 10, 10, 11)]),
            ("block_stomp", [("solid", 0, 12, 18, 8), ("stomp", 26, 10, 10, 11)]),
            ("spike_block", [("spikes", 0, 26, 9, 10), ("solid", 38, 14, 18, 8)]),
            ("duck_then_stomp", [("overhead", 0, 22, 10, 2), ("stomp", 38, 10, 10, 11)]),
            ("block_duck", [("solid", 0, 12, 18, 8), ("overhead", 22, 22, 10, 2)]),
            ("mixed_air", [("stomp", 0, 10, 10, 11), ("tall", 28, 9, 26, 2), ("flyer", 58, 12, 10, 14)]),
            ("jump_trap", [("stomp", 0, 10, 10, 11), ("jumper", 34, 14, 12, 8)]),
            ("air_lane", [("jumper", 0, 14, 12, 8), ("spikes", 34, 22, 9, 10)]),
        ]
        candidates = [pattern for pattern in patterns if pattern[0] != self.last_pattern]
        name, specs = random.choice(candidates)
        self.last_pattern = name

        # 同じパターンでも位置と速度を揺らして、毎回少し違う避け方にする。
        drift = random.randint(-5, 8)
        spacing_jitter = random.randint(-8, 10)
        for index, (kind, offset, w, h, color) in enumerate(specs):
            speed_mul = random.uniform(0.92, 1.18)
            y_offset = random.randint(-5, 5) if kind in ("flyer", "jumper", "overhead") else 0
            self.hazards.append(Hazard(x + offset + drift + index * spacing_jitter, w, h, kind, color, speed_mul, y_offset))

    def update_gaps(self) -> None:
        kept = []
        for gap in self.gaps:
            gap.x -= self.speed * gap.speed_mul
            if gap.x + gap.w >= 0:
                kept.append(gap)
        self.gaps = kept

    def update_hazards(self) -> None:
        px, py, pw, ph = self.player.rect()
        kept = []
        for hazard in self.hazards:
            hazard.x -= self.speed * hazard.speed_mul
            if hazard.x + hazard.w < 0:
                continue

            hit = self.overlap(px, py, pw, ph, hazard.x, hazard.y, hazard.w, hazard.h)
            if hit and self.player.invincible_timer <= 0:
                stomped = hazard.kind == "stomp" and self.player.vy > 0 and py + ph <= hazard.y + 6
                if stomped:
                    self.combo += 1
                    self.combo_timer = 150
                    self.player.vy = -5.0
                    self.player.flash_timer = 12
                    pyxel.play(1, 2)
                    continue
                self.end_game()
                return
            kept.append(hazard)
        self.hazards = kept

    def update_items(self) -> None:
        px, py, pw, ph = self.player.rect()
        kept = []
        for x, y in self.items:
            x -= self.speed
            if x < -8:
                continue
            if self.overlap(px, py, pw, ph, x - 4, y - 4, 8, 8):
                self.player.invincible_timer = 240
                self.player.flash_timer = 30
                pyxel.play(1, 2)
            else:
                kept.append((x, y))
        self.items = kept

    def end_game(self) -> None:
        self.game_over = True
        self.game_over_timer = 0
        pyxel.stop()
        pyxel.play(1, 3)
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

    def has_ground_at(self, x: float) -> bool:
        return not any(gap.x <= x <= gap.x + gap.w for gap in self.gaps)

    @staticmethod
    def overlap(ax: float, ay: float, aw: int, ah: int, bx: float, by: float, bw: int, bh: int) -> bool:
        return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah

    def draw(self) -> None:
        renderer.draw(self)
