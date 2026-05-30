# !/bin/bash

pyxel package . main.py
pyxel app2html uru-tiny-dots.pyxapp

mkdir -p docs

mv uru-tiny-dots.html docs/index.html

git switch main
git add .
git commit -m "deploy web version"
git push origin main