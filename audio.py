import pyxel


def setup_sounds() -> None:
    # 0-3 は SE、10 以降は BGM 用の短いフレーズ。
    pyxel.sounds[0].set("c3e3g3c4", "t", "7653", "n", 8)
    pyxel.sounds[1].set("c2c1", "n", "76", "f", 12)
    pyxel.sounds[2].set("g3c4e4g4", "s", "4321", "n", 10)
    pyxel.sounds[3].set("f2b1f1", "n", "765", "f", 18)
    pyxel.sounds[10].set("c2g2c3g2", "p", "5544", "n", 12)
    pyxel.sounds[11].set("e3g3a3g3", "s", "4433", "n", 12)
    pyxel.sounds[12].set("c1rc1r", "n", "5050", "f", 12)
    pyxel.sounds[13].set("c3e3g3b3", "t", "3333", "n", 8)
    pyxel.sounds[14].set("g3b3d4g4", "s", "3332", "n", 8)
    pyxel.sounds[15].set("c4d4e4g4", "t", "4332", "n", 6)

    # BGM は SE とチャンネルを分けて、ジャンプ音で曲が途切れにくくする。
    pyxel.musics[0].set([], [], [10, 11], [12])
    pyxel.musics[1].set([], [], [13, 14, 15, 14], [12])
