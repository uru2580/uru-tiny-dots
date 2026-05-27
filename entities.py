from dataclasses import dataclass

import pyxel

from constants import GROUND_Y


@dataclass
class Hazard:
    x: float
    w: int
    h: int
    kind: str
    color: int
    speed_mul: float = 1.0
    y_offset: int = 0

    @property
    def y(self) -> int:
        # 種類ごとに通る高さを変えて、ジャンプ/スライディングの判断を作る。
        if self.kind == "overhead":
            return GROUND_Y - 30 + self.y_offset
        if self.kind == "flyer":
            return GROUND_Y - 46 + self.y_offset
        if self.kind == "jumper":
            return GROUND_Y - 60 + self.y_offset
        return GROUND_Y - self.h + self.y_offset


@dataclass
class Gap:
    x: float
    w: int
    speed_mul: float = 1.0


@dataclass
class Star:
    x: float
    y: float
    speed: float


class Player:
    def __init__(self) -> None:
        self.x = 40
        self.y = GROUND_Y - 14
        self.w = 10
        self.h = 14
        self.vy = 0.0
        self.jumps_left = 2
        self.sliding = False
        self.grounded = True
        self.invincible_timer = 0
        self.flash_timer = 0

    @property
    def on_ground(self) -> bool:
        return self.grounded and self.y >= GROUND_Y - self.h - 0.1

    def rect(self) -> tuple[float, float, int, int]:
        if self.sliding:
            return self.x - 1, self.y + 3, self.w + 4, self.h
        return self.x, self.y, self.w, self.h

    def update(self, has_ground: bool, jump_pressed: bool) -> None:
        wants_slide = pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S)
        self.sliding = wants_slide and self.on_ground
        self.h = 8 if self.sliding else 14

        # 足元に地面がある時だけ、着地とジャンプ回数リセットを行う。
        if has_ground and self.y >= GROUND_Y - self.h - 0.1:
            self.y = GROUND_Y - self.h
            self.vy = min(0, self.vy)
            self.jumps_left = 2
            self.grounded = True
        else:
            self.grounded = False

        if jump_pressed:
            self.jump()

        self.vy += 0.48
        self.y += self.vy

        if has_ground and self.y > GROUND_Y - self.h:
            self.y = GROUND_Y - self.h
            self.vy = 0
            self.grounded = True

        self.invincible_timer = max(0, self.invincible_timer - 1)
        self.flash_timer = max(0, self.flash_timer - 1)

    def jump(self) -> None:
        if self.jumps_left <= 0 or self.sliding:
            return
        self.vy = -7.0 if self.jumps_left == 2 else -6.2
        self.jumps_left -= 1
        self.sliding = False
        pyxel.play(0, 0)
