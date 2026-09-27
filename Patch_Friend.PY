#!/usr/bin/env python3
"""Ajoute deux amis qui suivent le joueur dans sidi_runner.html.

Usage :  python patch_friends.py [chemin/vers/sidi_runner.html]
"""
import re
import shutil
import sys
from pathlib import Path

path = Path(sys.argv[1] if len(sys.argv) > 1 else "sidi_runner.html")
if not path.exists():
    sys.exit(f"Fichier introuvable : {path.resolve()}")

html = path.read_text(encoding="utf-8")
if "/*FRIENDS_PATCH*/" in html:
    sys.exit("Déjà patché, rien à faire.")

FRIEND_JS = """/*FRIENDS_PATCH*/
let friends = [];
function makeFriends(){
  friends = [
    {x: player.x-70,  y: player.y, w:30, h:46, color:"#f59e0b", name:"Yassine", off:65},
    {x: player.x-120, y: player.y, w:30, h:46, color:"#22c55e", name:"Nour",    off:110}
  ];
}
function updateFriends(){
  for(const f of friends){
    f.x += (player.x - f.off - f.x) * 0.08;
    f.y += (player.y - f.y) * 0.08;
  }
}
function drawFriends(){
  for(const f of friends){
    const sx = f.x - camera;
    ctx.fillStyle = f.color;   ctx.fillRect(sx, f.y, f.w, f.h);
    ctx.fillStyle = "#ffd7b5"; ctx.fillRect(sx+5, f.y-13, 20, 18);
    ctx.fillStyle = "#222";    ctx.fillRect(sx+9, f.y-8, 3, 3); ctx.fillRect(sx+16, f.y-8, 3, 3);
    ctx.fillStyle = "#fff";    ctx.font = "bold 12px Arial"; ctx.textAlign = "center";
    ctx.fillText(f.name, sx + f.w/2, f.y-19);
    ctx.textAlign = "left";
  }
}
"""

problems = []

def patch(label, pattern, repl, count=1):
    global html
    new, n = re.subn(pattern, repl, html, count=count, flags=re.S)
    if n == 0:
        problems.append(label)
    else:
        html = new

# 1) Fonctions des amis, juste avant loadLevel
patch("function loadLevel", r"(function\s+loadLevel\s*\()", lambda m: FRIEND_JS + "\n" + m.group(1))

# 2) Créer les amis juste après la création du joueur
patch("création du joueur (player={...};)",
      r"(player\s*=\s*\{[^}]*\}\s*;)", lambda m: m.group(1) + "\n  makeFriends();")

# 3) Mise à jour à chaque frame
patch("function update()", r"(function\s+update\s*\(\s*\)\s*\{)", lambda m: m.group(1) + "\n  updateFriends();")

# 4) Dessin des amis avant le joueur (appel, pas la définition)
patch("appel drawPlayer();", r"(?<!function )\bdrawPlayer\s*\(\s*\)\s*;", "drawFriends();\n  drawPlayer();")

# 5) Petit message dans l'interface (optionnel)
patch("function drawUI()", r"(function\s+drawUI\s*\(\s*\)\s*\{)",
      lambda m: m.group(1) + '\n  ctx.fillStyle="#fff"; ctx.font="bold 15px Arial"; ctx.fillText("Tes amis te suivent !", 18, 95);')

if problems:
    print("Patch NON appliqué. Repères introuvables :")
    for p in problems:
        print("  -", p)
    sys.exit(1)

shutil.copy(path, path.with_suffix(path.suffix + ".bak"))
path.write_text(html, encoding="utf-8")
print("Ajouté ! Sauvegarde :", path.with_suffix(path.suffix + ".bak").name)
