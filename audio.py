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
    pyxel.sounds[20].set("c3e3g3rg3e3c3rf3a3c4rc4a3f3r", "t", "3330333033303330", "n", 18)
    pyxel.sounds[21].set("c2rg2ra2rg2rf2rg2re2rc2r", "p", "5040504050405040", "n", 18)
    pyxel.sounds[22].set("c3d3e3g3a3g3e3d3f3g3a3c4b3a3g3e3", "s", "2334433223344332", "n", 14)
    pyxel.sounds[23].set("c2c2g2g2a2a2g2rf2f2g2g2e2e2c2r", "t", "3434343034343430", "n", 14)
    pyxel.sounds[24].set("e3g3b3c4d4b3g3e3f3a3c4d4e4d4c4a3", "p", "2233443322334433", "n", 16)
    pyxel.sounds[25].set("c3re3rg3r", "p", "505050", "n", 9)
    pyxel.sounds[26].set("c3d3e3g3e3d3", "s", "444444", "n", 6)
    pyxel.sounds[27].set("c2f2a2c3a2f2", "t", "344443", "n", 11)
    pyxel.sounds[28].set("c2rg2rc3r", "n", "606060", "f", 12)
    pyxel.sounds[29].set("f2g2a2c3a2g2", "p", "333444", "n", 7)
    pyxel.sounds[30].set("c3e3d3g3e3a3", "s", "343454", "n", 10)
    pyxel.sounds[31].set("a3c4e4a4g4e4c4a3f3a3c4f4e4c4a3f3", "s", "3344554433445544", "n", 10)

    # BGM は SE とチャンネルを分けて、ジャンプ音で曲が途切れにくくする。
    pyxel.musics[0].set([], [], [10, 11], [12])
    pyxel.musics[1].set([], [], [13, 14, 15, 14], [12])
    pyxel.musics[2].set([20], [21], [], [])
    pyxel.musics[3].set([22], [23], [], [])
    pyxel.musics[4].set([24], [23], [], [])
    pyxel.musics[5].set([31], [23], [], [])
