import json
import random

import pyxel

import renderer
from audio import setup_sounds
from constants import HEIGHT, JUMP_BUTTON_RECT, SAVE_FILE, WIDTH
from entities import Gap, Hazard, Player, Star
from mini_games import MINI_GAME_CLASSES


class RunnerGame:
    def __init__(self) -> None:
        pyxel.init(WIDTH, HEIGHT, title="Uru Tiny Dots", fps=60)
        pyxel.mouse(True)
        self.high_scores = self.load_high_scores()
        self.game_choices = [
            {"id": "tiny_runner", "name": "Tiny Runner", "enabled": True},
            {"id": "tiny_defender", "name": "Tiny Defender", "enabled": True},
            {"id": "sky_tower", "name": "Sky Tower", "enabled": True},
            {"id": "pixel_dungeon", "name": "Pixel Dungeon", "enabled": True},
            {"id": "box_master", "name": "Box Master", "enabled": True},
            {"id": "color_burst", "name": "Color Burst", "enabled": True},
            {"id": "laser_logic", "name": "Laser Logic", "enabled": True},
            {"id": "switch_maze", "name": "Switch Maze", "enabled": True},
            {"id": "bomb_technician", "name": "Bomb Technician", "enabled": True},
            {"id": "tiny_fishing", "name": "Tiny Fishing", "enabled": True},
        ]
        self.game_over_choices = ["RETRY", "TITLE"]
        self.pause_choices = ["RESUME", "RETRY", "TITLE"]
        self.selected_game_index = self.first_enabled_game_index()
        self.selected_game_over_index = 0
        self.selected_pause_index = 0
        self.paused = False
        self.screen = "title"
        self.active_game = None
        self.current_game_id = "tiny_runner"
        self.high_score = self.high_scores.get(self.current_game_id, 0)
        self.stars = [Star(random.randrange(WIDTH), random.randrange(8, 70), random.uniform(0.15, 0.6)) for _ in range(36)]
        setup_sounds()
        self.reset(start_bgm=False)
        self.play_bgm("title")
        pyxel.run(self.update, self.draw)

    def reset(self, start_bgm: bool = True) -> None:
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
        self.selected_game_over_index = 0
        self.selected_pause_index = 0
        self.paused = False
        self.bgm_mode = ""
        self.jump_button_rect = JUMP_BUTTON_RECT
        self.last_pattern = ""
        if start_bgm:
            self.play_bgm("tiny_runner")
        else:
            pyxel.stop()

    def first_enabled_game_index(self) -> int:
        for index, choice in enumerate(self.game_choices):
            if choice["enabled"]:
                return index
        return 0

    def load_high_scores(self) -> dict[str, int]:
        try:
            data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError, json.JSONDecodeError, TypeError):
            return {}

        if isinstance(data, dict) and isinstance(data.get("high_scores"), dict):
            try:
                return {str(key): int(value) for key, value in data["high_scores"].items()}
            except (TypeError, ValueError):
                return {}
        if isinstance(data, dict) and "high_score" in data:
            try:
                return {"tiny_runner": int(data.get("high_score", 0))}
            except (TypeError, ValueError):
                return {}
        return {}

    def save_high_scores(self) -> None:
        SAVE_FILE.write_text(json.dumps({"high_scores": self.high_scores}, indent=2), encoding="utf-8")

    def set_current_game(self, game_id: str) -> None:
        self.current_game_id = game_id
        self.high_score = self.high_scores.get(game_id, 0)

    def record_score(self, score: int) -> None:
        self.score = score
        if score > self.high_scores.get(self.current_game_id, 0):
            self.high_scores[self.current_game_id] = score
            self.high_score = score
            self.save_high_scores()

    def play_bgm(self, mode: str) -> None:
        if self.bgm_mode == mode:
            return
        bgm_musics = {"title": 2, "tiny_runner": 3, "sky_tower": 4, "tiny_runner_invincible": 5}
        bgm_sounds = {"tiny_defender": 22, "pixel_dungeon": 24, "box_master": 25, "color_burst": 26, "laser_logic": 27, "switch_maze": 28, "bomb_technician": 29, "tiny_fishing": 30}
        self.bgm_mode = mode
        pyxel.stop()
        if mode in bgm_musics:
            pyxel.playm(bgm_musics[mode], loop=True)
        else:
            pyxel.play(2, bgm_sounds.get(mode, 20), loop=True)

    def update(self) -> None:
        if self.screen == "title":
            self.update_title()
            return

        if self.game_over:
            self.update_game_over()
            return

        if self.paused:
            self.update_pause()
            return

        if self.pause_pressed():
            self.paused = True
            self.selected_pause_index = 0
            return

        if self.active_game is not None:
            self.active_game.update()
            self.score = self.active_game.score
            return

        # 崖の上では着地させず、落下したらゲームオーバーにする。
        has_ground = self.has_ground_at(self.player.x + self.player.w / 2)
        self.player.update(has_ground, self.jump_pressed())
        if self.player.y > HEIGHT + 10:
            self.end_game()
            return

        self.play_bgm("tiny_runner_invincible" if self.player.invincible_timer else "tiny_runner")
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
        if self.action_pressed():
            return True

        return False

    def left_down(self) -> bool:
        return pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)

    def right_down(self) -> bool:
        return pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)

    def up_pressed(self) -> bool:
        return pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_W) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP)

    def down_pressed(self) -> bool:
        return pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_S) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)

    def left_pressed(self) -> bool:
        return pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_A) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)

    def right_pressed(self) -> bool:
        return pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)

    def action_down(self) -> bool:
        return (
            pyxel.btn(pyxel.KEY_SPACE)
            or pyxel.btn(pyxel.KEY_Z)
            or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A)
            or pyxel.btn(pyxel.GAMEPAD1_BUTTON_B)
            or pyxel.btn(pyxel.GAMEPAD1_BUTTON_X)
            or pyxel.btn(pyxel.GAMEPAD1_BUTTON_Y)
        )

    def action_pressed(self) -> bool:
        return (
            pyxel.btnp(pyxel.KEY_SPACE)
            or pyxel.btnp(pyxel.KEY_Z)
            or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
            or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B)
            or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X)
            or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y)
        )

    def confirm_pressed(self) -> bool:
        return pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START) or self.action_pressed()

    def pause_pressed(self) -> bool:
        return pyxel.btnp(pyxel.KEY_P) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_BACK)

    def update_title(self) -> None:
        if self.up_pressed() or self.left_pressed():
            self.move_title_selection(-1)
        if self.down_pressed() or self.right_pressed():
            self.move_title_selection(1)

        for index, _choice in enumerate(self.game_choices):
            x, y, w, h = self.title_choice_rect(index)
            if x <= pyxel.mouse_x <= x + w and y <= pyxel.mouse_y <= y + h:
                if self.game_choices[index]["enabled"]:
                    self.selected_game_index = index
                    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                        self.start_selected_game()
                break

        if self.confirm_pressed():
            self.start_selected_game()

    def move_title_selection(self, direction: int) -> None:
        index = self.selected_game_index
        for _ in self.game_choices:
            index = (index + direction) % len(self.game_choices)
            if self.game_choices[index]["enabled"]:
                self.selected_game_index = index
                return

    def start_selected_game(self) -> None:
        choice = self.game_choices[self.selected_game_index]
        if not choice["enabled"]:
            return
        self.set_current_game(choice["id"])
        self.screen = "game"
        self.paused = False
        if self.current_game_id == "tiny_runner":
            self.active_game = None
            self.reset()
        else:
            self.active_game = MINI_GAME_CLASSES[self.current_game_id](self)
            self.score = 0
            self.game_over = False
            self.game_over_timer = 0
            self.selected_game_over_index = 0
            self.selected_pause_index = 0
            self.bgm_mode = ""
            self.play_bgm(self.current_game_id)

    def title_choice_rect(self, index: int) -> tuple[int, int, int, int]:
        return 18 + (index % 2) * 80, 36 + (index // 2) * 16, 74, 13

    def update_game_over(self) -> None:
        self.game_over_timer += 1

        if (
            self.left_pressed()
            or self.up_pressed()
        ):
            self.move_game_over_selection(-1)
        if (
            self.right_pressed()
            or self.down_pressed()
        ):
            self.move_game_over_selection(1)

        for index, _choice in enumerate(self.game_over_choices):
            x, y, w, h = self.game_over_choice_rect(index)
            if x <= pyxel.mouse_x <= x + w and y <= pyxel.mouse_y <= y + h:
                self.selected_game_over_index = index
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.select_game_over_choice()
                break

        if pyxel.btnp(pyxel.KEY_R):
            self.selected_game_over_index = 0
            self.select_game_over_choice()
        elif pyxel.btnp(pyxel.KEY_T):
            self.selected_game_over_index = 1
            self.select_game_over_choice()
        elif self.confirm_pressed():
            self.select_game_over_choice()

    def move_game_over_selection(self, direction: int) -> None:
        self.selected_game_over_index = (self.selected_game_over_index + direction) % len(self.game_over_choices)

    def update_pause(self) -> None:
        if self.pause_pressed():
            self.paused = False
            return

        if (
            self.left_pressed()
            or self.up_pressed()
        ):
            self.move_pause_selection(-1)
        if (
            self.right_pressed()
            or self.down_pressed()
        ):
            self.move_pause_selection(1)

        for index, _choice in enumerate(self.pause_choices):
            x, y, w, h = self.pause_choice_rect(index)
            if x <= pyxel.mouse_x <= x + w and y <= pyxel.mouse_y <= y + h:
                self.selected_pause_index = index
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.select_pause_choice()
                break

        if self.confirm_pressed():
            self.select_pause_choice()

    def move_pause_selection(self, direction: int) -> None:
        self.selected_pause_index = (self.selected_pause_index + direction) % len(self.pause_choices)

    def select_pause_choice(self) -> None:
        if self.selected_pause_index == 0:
            self.paused = False
        elif self.selected_pause_index == 1:
            self.start_selected_game()
        else:
            self.return_to_title()

    def select_game_over_choice(self) -> None:
        if self.selected_game_over_index == 0:
            self.start_selected_game()
        else:
            self.return_to_title()

    def return_to_title(self) -> None:
        self.screen = "title"
        self.active_game = None
        self.reset(start_bgm=False)
        self.play_bgm("title")

    def game_over_choice_rect(self, index: int) -> tuple[int, int, int, int]:
        return 45 + index * 54, 78, 48, 13

    def pause_choice_rect(self, index: int) -> tuple[int, int, int, int]:
        return 34 + index * 42, 75, 38, 13

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
        self.bgm_mode = ""
        pyxel.play(1, 3)
        self.record_score(self.score)

    def has_ground_at(self, x: float) -> bool:
        return not any(gap.x <= x <= gap.x + gap.w for gap in self.gaps)

    @staticmethod
    def overlap(ax: float, ay: float, aw: int, ah: int, bx: float, by: float, bw: int, bh: int) -> bool:
        return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah

    def draw(self) -> None:
        renderer.draw(self)
