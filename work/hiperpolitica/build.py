# Junta fonte + bibliotecas + tempos das palavras num único video.html
import base64, json, re
src = open("src/video.src.html", encoding="utf-8").read()
while "//@include " in src:   # includes aninhados (ex.: cenas.js inclui lib_char.js)
    src = re.sub(r'//@include (\S+)', lambda m: open("src/" + m.group(1), encoding="utf-8").read(), src)
font = base64.b64encode(open("../assets/fonts/X7n64b87HvSqjb_WIi2yDCRwoQ_k7367_DWu89U.woff2", "rb").read()).decode()
words = json.load(open("audio/palavras.json", encoding="utf-8"))
open("video.html", "w", encoding="utf-8").write(src.replace("__FONT__", font).replace("__WORDS__", json.dumps(words, ensure_ascii=False)))
print("ok")
