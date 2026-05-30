import random

import pyxel

from constants import HEIGHT, WIDTH


def hit(ax, ay, aw, ah, bx, by, bw, bh) -> bool:
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def pressed_action() -> bool:
    return pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)


def pressed_confirm() -> bool:
    return pressed_action() or pyxel.btnp(pyxel.KEY_RETURN)


class MiniGame:
    title = ""
    help = ""

    def __init__(self, host) -> None:
        self.host = host
        self.score = 0

    def finish(self, score: int | None = None) -> None:
        if score is not None:
            self.score = score
        self.host.score = self.score
        self.host.end_game()

    def hud(self, extra: str = "") -> None:
        pyxel.text(4, 4, self.title, 7)
        pyxel.text(4, 13, f"SC {self.score:05}", 7)
        pyxel.text(136, 4, f"HI {self.host.high_score:05}", 6)
        if extra:
            pyxel.text(4, 116, extra, 6)


class TinyDefender(MiniGame):
    title = "Tiny Defender"

    def __init__(self, host) -> None:
        super().__init__(host)
        self.x = 18
        self.y = 64
        self.hp = 3
        self.inv = 0
        self.wave = 1
        self.cooldown = 0
        self.fire_delay = 12
        self.pierce_timer = 0
        self.bullets = []
        self.enemies = []
        self.items = []
        self.spawn_timer = 20

    def update(self) -> None:
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W):
            self.y -= 2
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S):
            self.y += 2
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
            self.x -= 2
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
            self.x += 2
        self.x = max(4, min(68, self.x))
        self.y = max(22, min(112, self.y))
        self.cooldown = max(0, self.cooldown - 1)
        self.inv = max(0, self.inv - 1)
        self.pierce_timer = max(0, self.pierce_timer - 1)
        if pyxel.btn(pyxel.KEY_SPACE) and self.cooldown == 0:
            self.bullets.append([self.x + 8, self.y + 2, 4 if self.pierce_timer else 1])
            self.cooldown = self.fire_delay
            pyxel.play(0, 0)

        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            boss = self.wave % 10 == 0 and not any(e[4] == "boss" for e in self.enemies)
            if boss:
                self.enemies.append([170, 44, 2.0, 28, "boss"])
                self.spawn_timer = 180
            else:
                kind = "heavy" if random.random() < 0.25 else "grunt"
                hp = 3 if kind == "heavy" else 1
                self.enemies.append([190, random.randint(24, 108), random.uniform(0.7, 1.4), hp, kind])
                self.spawn_timer = max(12, 42 - self.wave)

        for bullet in self.bullets:
            bullet[0] += 4
        self.bullets = [b for b in self.bullets if b[0] < WIDTH]

        kept = []
        for enemy in self.enemies:
            enemy[0] -= enemy[2]
            enemy[1] += 0.7 if pyxel.frame_count // 30 % 2 == 0 else -0.7
            enemy_w = 22 if enemy[4] == "boss" else 10
            enemy_h = 18 if enemy[4] == "boss" else 8
            for bullet in list(self.bullets):
                if hit(bullet[0], bullet[1], 4, 2, enemy[0], enemy[1], enemy_w, enemy_h):
                    enemy[3] -= 1
                    bullet[2] -= 1
                    if bullet[2] <= 0:
                        self.bullets.remove(bullet)
            if enemy[3] <= 0:
                gain = 1000 if enemy[4] == "boss" else 300 if enemy[4] == "heavy" else 100
                self.score += gain
                self.wave += 1
                if random.random() < 0.23:
                    self.items.append([enemy[0], enemy[1], random.choice(["rapid", "pierce", "heal"])])
                pyxel.play(1, 2)
                continue
            if hit(self.x, self.y, 8, 6, enemy[0], enemy[1], enemy_w, enemy_h) and self.inv == 0:
                self.hp -= 1
                self.inv = 70
                pyxel.play(1, 3)
                if self.hp <= 0:
                    self.finish()
                    return
            if enemy[0] > -30:
                kept.append(enemy)
        self.enemies = kept

        for item in list(self.items):
            item[0] -= 1.2
            if hit(self.x, self.y, 8, 6, item[0], item[1], 6, 6):
                if item[2] == "rapid":
                    self.fire_delay = 6
                elif item[2] == "pierce":
                    self.pierce_timer = 600
                else:
                    self.hp = min(3, self.hp + 1)
                self.items.remove(item)

    def draw(self) -> None:
        pyxel.cls(0)
        for x in range(0, WIDTH, 16):
            pyxel.pset((x - pyxel.frame_count // 2) % WIDTH, 20 + x % 88, 13)
        self.hud(f"HP {self.hp}  WAVE {self.wave}  ARROWS MOVE SPACE SHOT")
        if self.inv and pyxel.frame_count % 6 < 3:
            pass
        else:
            pyxel.tri(self.x, self.y + 3, self.x + 9, self.y, self.x + 9, self.y + 7, 11)
        for bullet in self.bullets:
            pyxel.rect(bullet[0], bullet[1], 5, 2, 10)
        for x, y, _speed, hp, kind in self.enemies:
            if kind == "boss":
                pyxel.rect(x, y, 22, 18, 8)
                pyxel.text(x + 5, y + 6, str(hp), 7)
            else:
                pyxel.circ(x + 4, y + 4, 5, 9 if kind == "heavy" else 4)
        for x, y, kind in self.items:
            pyxel.rect(x, y, 6, 6, 10 if kind == "pierce" else 11 if kind == "rapid" else 8)


class SkyTower(MiniGame):
    title = "Sky Tower"

    def __init__(self, host) -> None:
        super().__init__(host)
        self.x = 90.0
        self.y = 92.0
        self.vy = 0.0
        self.camera = 0.0
        self.best_height = 0
        self.jump_boost = False
        self.jetpack = 0
        self.inv = 0
        self.platforms = [[80, 110, 34, "normal", 0]]
        y = 110
        for _ in range(12):
            y -= random.randint(26, 34)
            self.platforms.append([random.randint(8, 150), y, random.randint(24, 38), random.choice(["normal", "move", "fade"]), 0])
        self.items = []

    def update(self) -> None:
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
            self.x -= 2
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
            self.x += 2
        self.x %= WIDTH
        if pressed_action() and self.jetpack > 0:
            self.vy = -5.5
            self.jetpack -= 1
        self.vy += 0.28
        self.y += self.vy
        self.inv = max(0, self.inv - 1)

        for p in self.platforms:
            if p[3] == "move":
                p[0] += 1.2 if pyxel.frame_count // 45 % 2 == 0 else -1.2
            if self.vy > 0 and hit(self.x, self.y, 8, 10, p[0], p[1], p[2], 4):
                self.y = p[1] - 10
                self.vy = -7.2 if self.jump_boost else -5.8
                self.jump_boost = False
                if p[3] == "fade":
                    p[4] = 1

        self.platforms = [p for p in self.platforms if p[4] == 0]
        if self.y - self.camera < 42:
            self.camera = self.y - 42
        top = min(p[1] for p in self.platforms)
        while top > self.camera - 80:
            top -= random.randint(28, 38)
            self.platforms.append([random.randint(8, 150), top, random.randint(22, 36), random.choice(["normal", "move", "fade"]), 0])
            if random.random() < 0.18:
                self.items.append([random.randint(12, 172), top - 10, random.choice(["jump", "jet", "inv"])])
        self.score = max(self.score, int(max(0, 110 - self.y) * 3))
        for item in list(self.items):
            if hit(self.x, self.y, 8, 10, item[0], item[1], 6, 6):
                if item[2] == "jump":
                    self.jump_boost = True
                elif item[2] == "jet":
                    self.jetpack = 45
                else:
                    self.inv = 360
                self.items.remove(item)
        if self.y - self.camera > HEIGHT + 20:
            self.finish()

    def draw(self) -> None:
        pyxel.cls(1)
        self.hud("ARROWS MOVE SPACE JET")
        pyxel.rect(self.x, self.y - self.camera, 8, 10, 10 if self.inv else 7)
        for x, y, w, kind, _gone in self.platforms:
            color = {"normal": 11, "move": 12, "fade": 6}[kind]
            pyxel.rect(x, y - self.camera, w, 4, color)
        for x, y, kind in self.items:
            pyxel.circ(x, y - self.camera, 3, 10 if kind == "jump" else 9 if kind == "jet" else 14)


class PixelDungeon(MiniGame):
    title = "Pixel Dungeon"

    def __init__(self, host) -> None:
        super().__init__(host)
        self.floor = 1
        self.hp = 12
        self.atk = 3
        self.defense = 0
        self.make_floor()

    def make_floor(self) -> None:
        self.grid = [["#" if x in (0, 19) or y in (0, 19) else "." for x in range(20)] for y in range(20)]
        for _ in range(55):
            self.grid[random.randint(1, 18)][random.randint(1, 18)] = "#"
        self.px, self.py = 1, 1
        self.grid[18][18] = ">"
        self.enemies = []
        for _ in range(4 + self.floor):
            self.enemies.append([random.randint(2, 18), random.randint(2, 18), random.choice([3, 5, 4])])
        self.items = [[random.randint(2, 18), random.randint(2, 18), random.choice(["p", "s", "d"])] for _ in range(5)]

    def update(self) -> None:
        dx = (pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D)) - (pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_A))
        dy = (pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_S)) - (pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_W))
        if dx == 0 and dy == 0:
            return
        nx, ny = self.px + dx, self.py + dy
        for e in list(self.enemies):
            if e[0] == nx and e[1] == ny:
                e[2] -= max(1, self.atk)
                if e[2] <= 0:
                    self.score += 100
                    self.enemies.remove(e)
                self.enemy_turn()
                return
        if self.grid[ny][nx] != "#":
            self.px, self.py = nx, ny
        for item in list(self.items):
            if item[0] == self.px and item[1] == self.py:
                if item[2] == "p":
                    self.hp = min(18, self.hp + 5)
                elif item[2] == "s":
                    self.atk += 1
                else:
                    self.defense += 1
                self.items.remove(item)
        if self.grid[self.py][self.px] == ">":
            self.score += 1000
            self.floor += 1
            if self.floor > 5:
                self.finish(self.score + self.hp * 100)
                return
            self.make_floor()
        self.enemy_turn()

    def enemy_turn(self) -> None:
        for e in self.enemies:
            dx = 1 if self.px > e[0] else -1 if self.px < e[0] else 0
            dy = 1 if self.py > e[1] else -1 if self.py < e[1] else 0
            if abs(self.px - e[0]) + abs(self.py - e[1]) == 1:
                self.hp -= max(1, 2 - self.defense)
                if self.hp <= 0:
                    self.finish()
                    return
            elif self.grid[e[1] + dy][e[0] + dx] != "#" and random.random() < 0.65:
                e[0] += dx
                e[1] += dy

    def draw(self) -> None:
        pyxel.cls(0)
        self.hud(f"F{self.floor} HP{self.hp} ATK{self.atk} DEF{self.defense}")
        ox, oy, s = 46, 18, 5
        for y in range(20):
            for x in range(20):
                c = 5 if self.grid[y][x] == "#" else 1
                if self.grid[y][x] == ">":
                    c = 10
                pyxel.rect(ox + x * s, oy + y * s, s - 1, s - 1, c)
        for x, y, kind in self.items:
            pyxel.rect(ox + x * s, oy + y * s, 3, 3, 8 if kind == "p" else 11 if kind == "s" else 12)
        for x, y, _hp in self.enemies:
            pyxel.rect(ox + x * s, oy + y * s, 4, 4, 9)
        pyxel.rect(ox + self.px * s, oy + self.py * s, 4, 4, 7)


class BoxMaster(MiniGame):
    title = "Box Master"

    def __init__(self, host) -> None:
        super().__init__(host)
        self.stage = 0
        self.load_stage()

    def load_stage(self) -> None:
        w, h = 9, 7
        self.walls = {(x, y) for x in range(w) for y in range(h) if x in (0, w - 1) or y in (0, h - 1)}
        self.player = [1, 1]
        offset = self.stage % 2
        self.boxes = {(3 + offset, 2), (3 + offset, 4)}
        self.goals = {(6, 2), (6, 4)}
        self.stage += 1

    def update(self) -> None:
        dx = (pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D)) - (pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_A))
        dy = (pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_S)) - (pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_W))
        if dx == 0 and dy == 0:
            return
        nx, ny = self.player[0] + dx, self.player[1] + dy
        if (nx, ny) in self.walls:
            return
        if (nx, ny) in self.boxes:
            bx, by = nx + dx, ny + dy
            if (bx, by) in self.walls or (bx, by) in self.boxes:
                return
            self.boxes.remove((nx, ny))
            self.boxes.add((bx, by))
        self.player = [nx, ny]
        if self.boxes <= self.goals:
            self.score = self.stage
            if self.stage >= 20:
                self.finish(self.score)
            else:
                self.load_stage()

    def draw(self) -> None:
        pyxel.cls(0)
        self.hud(f"STAGE {self.stage}/20  PUSH BOXES")
        ox, oy, s = 48, 25, 12
        for y in range(7):
            for x in range(9):
                pyxel.rectb(ox + x * s, oy + y * s, s, s, 1)
        for x, y in self.walls:
            pyxel.rect(ox + x * s, oy + y * s, s, s, 5)
        for x, y in self.goals:
            pyxel.circb(ox + x * s + 6, oy + y * s + 6, 4, 10)
        for x, y in self.boxes:
            pyxel.rect(ox + x * s + 2, oy + y * s + 2, 8, 8, 4)
        pyxel.rect(ox + self.player[0] * s + 3, oy + self.player[1] * s + 3, 6, 6, 7)


class ColorBurst(MiniGame):
    title = "Color Burst"

    def __init__(self, host) -> None:
        super().__init__(host)
        self.colors = [8, 12, 11, 10, 2]
        self.grid = [[random.randrange(5) for _ in range(8)] for _ in range(8)]
        self.cx = 0
        self.cy = 0

    def group(self, x, y):
        target = self.grid[y][x]
        if target is None:
            return []
        found, stack = set(), [(x, y)]
        while stack:
            x, y = stack.pop()
            if (x, y) in found or not (0 <= x < 8 and 0 <= y < 8) or self.grid[y][x] != target:
                continue
            found.add((x, y))
            stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return list(found)

    def update(self) -> None:
        self.cx = (self.cx + (pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D)) - (pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_A))) % 8
        self.cy = (self.cy + (pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_S)) - (pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_W))) % 8
        if pressed_confirm():
            cells = self.group(self.cx, self.cy)
            if len(cells) >= 2:
                for x, y in cells:
                    self.grid[y][x] = None
                self.score += len(cells) * len(cells) * 10
                for x in range(8):
                    col = [self.grid[y][x] for y in range(8) if self.grid[y][x] is not None]
                    col = [random.randrange(5) for _ in range(8 - len(col))] + col
                    for y in range(8):
                        self.grid[y][x] = col[y]
        if not any(len(self.group(x, y)) >= 2 for y in range(8) for x in range(8)):
            self.finish()

    def draw(self) -> None:
        pyxel.cls(1)
        self.hud("ARROWS SELECT  SPACE BURST")
        ox, oy, s = 48, 22, 10
        for y in range(8):
            for x in range(8):
                pyxel.rect(ox + x * s, oy + y * s, 8, 8, self.colors[self.grid[y][x]])
        pyxel.rectb(ox + self.cx * s - 1, oy + self.cy * s - 1, 10, 10, 7)


class LaserLogic(MiniGame):
    title = "Laser Logic"

    def __init__(self, host) -> None:
        super().__init__(host)
        self.stage = 1
        self.cx = 3
        self.cy = 3
        self.grid = {}
        self.path = []

    def update(self) -> None:
        self.cx = max(0, min(9, self.cx + (pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D)) - (pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_A))))
        self.cy = max(0, min(5, self.cy + (pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_S)) - (pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_W))))
        if pressed_action():
            key = (self.cx, self.cy)
            self.grid[key] = {None: "/", "/": "\\", "\\": "+", "+": None}[self.grid.get(key)]
            if self.grid[key] is None:
                del self.grid[key]
        if pyxel.btnp(pyxel.KEY_RETURN):
            if self.trace():
                self.score = self.stage
                self.stage += 1
                self.grid = {}
                if self.stage > 30:
                    self.finish(self.score)

    def trace(self) -> bool:
        x, y, dx, dy = 0, self.stage % 6, 1, 0
        goal = (9, (self.stage * 2) % 6)
        self.path = []
        for _ in range(80):
            self.path.append((x, y))
            if (x, y) == goal:
                return True
            tile = self.grid.get((x, y))
            if tile == "/":
                dx, dy = -dy, -dx
            elif tile == "\\":
                dx, dy = dy, dx
            elif tile == "+":
                dx, dy = dy or dx, dx if dy else dy
            x += dx
            y += dy
            if not (0 <= x < 10 and 0 <= y < 6):
                return False
        return False

    def draw(self) -> None:
        pyxel.cls(0)
        self.hud(f"STAGE {self.stage}/30  SPACE MIRROR ENTER FIRE")
        ox, oy, s = 36, 30, 12
        source = (0, self.stage % 6)
        goal = (9, (self.stage * 2) % 6)
        for y in range(6):
            for x in range(10):
                pyxel.rectb(ox + x * s, oy + y * s, s, s, 5)
        pyxel.rect(ox + source[0] * s + 3, oy + source[1] * s + 3, 6, 6, 8)
        pyxel.rect(ox + goal[0] * s + 3, oy + goal[1] * s + 3, 6, 6, 10)
        for x, y in self.path:
            pyxel.pset(ox + x * s + 6, oy + y * s + 6, 10)
        for (x, y), tile in self.grid.items():
            pyxel.text(ox + x * s + 3, oy + y * s + 3, tile, 7)
        pyxel.rectb(ox + self.cx * s - 1, oy + self.cy * s - 1, s + 2, s + 2, 7)


class SwitchMaze(MiniGame):
    title = "Switch Maze"

    def __init__(self, host) -> None:
        super().__init__(host)
        self.stage = 1
        self.px = 1
        self.py = 1
        self.open_color = 8

    def update(self) -> None:
        dx = (pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D)) - (pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_A))
        dy = (pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_S)) - (pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_W))
        nx, ny = self.px + dx, self.py + dy
        if dx or dy:
            color_wall = self.wall_color(nx, ny)
            if color_wall == 0 or color_wall == self.open_color:
                self.px, self.py = nx, ny
            if (self.px, self.py) in [(2, 2), (5, 4), (8, 2)]:
                self.open_color = { (2, 2): 8, (5, 4): 12, (8, 2): 11 }[(self.px, self.py)]
            if self.px == 10 and self.py == 6:
                self.score = self.stage
                self.stage += 1
                self.px, self.py = 1, 1
                if self.stage > 20:
                    self.finish(self.score)

    def wall_color(self, x, y) -> int:
        if x < 0 or x > 11 or y < 0 or y > 7:
            return 5
        if x in (0, 11) or y in (0, 7):
            return 5
        if (x + y + self.stage) % 5 == 0:
            return [8, 12, 11][(x + self.stage) % 3]
        return 0

    def draw(self) -> None:
        pyxel.cls(1)
        self.hud(f"STAGE {self.stage}/20  OPEN COLOR {self.open_color}")
        ox, oy, s = 26, 24, 12
        for y in range(8):
            for x in range(12):
                c = self.wall_color(x, y)
                if c:
                    pyxel.rect(ox + x * s, oy + y * s, s, s, c if c == self.open_color else 5)
                pyxel.rectb(ox + x * s, oy + y * s, s, s, 13)
        for pos, c in [((2, 2), 8), ((5, 4), 12), ((8, 2), 11)]:
            pyxel.circ(ox + pos[0] * s + 6, oy + pos[1] * s + 6, 4, c)
        pyxel.rect(ox + 10 * s + 3, oy + 6 * s + 3, 6, 6, 10)
        pyxel.rect(ox + self.px * s + 3, oy + self.py * s + 3, 6, 6, 7)


class BombTechnician(MiniGame):
    title = "Bomb Technician"

    def __init__(self, host) -> None:
        super().__init__(host)
        self.selected = 0
        self.new_bomb()

    def new_bomb(self) -> None:
        self.timer = 30 * 60
        self.target = random.randrange(4)
        self.labels = random.sample(["RED", "BLUE", "GREEN", "YELL"], 4)

    def update(self) -> None:
        self.timer -= 1
        self.selected = (self.selected + (pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D)) - (pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_A))) % 4
        if pressed_confirm():
            if self.selected == self.target:
                self.score += 1
                self.new_bomb()
            else:
                self.finish()
        if self.timer <= 0:
            self.finish()

    def draw(self) -> None:
        pyxel.cls(0)
        self.hud("LEFT/RIGHT SELECT  SPACE CUT")
        pyxel.text(64, 30, f"TIME {self.timer // 60:02}", 8 if self.timer < 600 else 7)
        pyxel.text(45, 44, f"HINT: CUT #{self.target + 1}", 10)
        for i, label in enumerate(self.labels):
            x = 28 + i * 38
            pyxel.rect(x, 70, 30, 14, [8, 12, 11, 10][i])
            pyxel.rectb(x, 70, 30, 14, 7 if i == self.selected else 5)
            pyxel.text(x + 4, 75, label[:4], 0)


class TinyFishing(MiniGame):
    title = "Tiny Fishing"

    def __init__(self, host) -> None:
        super().__init__(host)
        self.hook_x = 96
        self.hook_y = 22
        self.casting = False
        self.depth_speed = 1.5
        self.rod = 1
        self.fish = []
        self.book = set()

    def update(self) -> None:
        if not self.casting:
            if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
                self.hook_x -= 2
            if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
                self.hook_x += 2
            if pressed_action():
                self.casting = True
            if random.random() < 0.03:
                self.fish.append([random.randint(6, 180), random.randint(50, 116), random.choice(["MEDAKA", "FUNA", "TROUT", "BASS", "KING", "ANCIENT"])])
        else:
            self.hook_y += self.depth_speed
            if self.hook_y > 120:
                self.casting = False
                self.hook_y = 22
            for f in list(self.fish):
                f[0] += 0.8 if pyxel.frame_count // 45 % 2 == 0 else -0.8
                if hit(self.hook_x, self.hook_y, 4, 4, f[0], f[1], 8, 4):
                    values = {"MEDAKA": 20, "FUNA": 40, "TROUT": 80, "BASS": 120, "KING": 300, "ANCIENT": 600}
                    self.score += values[f[2]]
                    self.book.add(f[2])
                    self.fish.remove(f)
                    self.casting = False
                    self.hook_y = 22
                    if self.score > 500 and self.rod < 2:
                        self.rod = 2
                        self.depth_speed = 2.1
                    if len(self.book) == 6:
                        self.finish(self.score + 1000)
                    break
        if pyxel.btnp(pyxel.KEY_T):
            self.finish()

    def draw(self) -> None:
        pyxel.cls(12)
        pyxel.rect(0, 38, WIDTH, HEIGHT - 38, 1)
        self.hud(f"BOOK {len(self.book)}/6  SPACE CAST  T END")
        pyxel.line(self.hook_x, 20, self.hook_x, self.hook_y, 7)
        pyxel.rect(self.hook_x - 1, self.hook_y, 3, 4, 7)
        for x, y, kind in self.fish:
            color = {"MEDAKA": 6, "FUNA": 4, "TROUT": 8, "BASS": 3, "KING": 10, "ANCIENT": 2}[kind]
            pyxel.elli(x, y, 8, 4, color)


MINI_GAME_CLASSES = {
    "tiny_defender": TinyDefender,
    "sky_tower": SkyTower,
    "pixel_dungeon": PixelDungeon,
    "box_master": BoxMaster,
    "color_burst": ColorBurst,
    "laser_logic": LaserLogic,
    "switch_maze": SwitchMaze,
    "bomb_technician": BombTechnician,
    "tiny_fishing": TinyFishing,
}
