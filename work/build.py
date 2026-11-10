# Junta fonte + tempos das palavras num único video.html
import base64, json
src = open("src/video.src.html", encoding="utf-8").read()
font = base64.b64encode(open("assets/fonts/X7n64b87HvSqjb_WIi2yDCRwoQ_k7367_DWu89U.woff2", "rb").read()).decode()
words = json.load(open("audio/palavras.json", encoding="utf-8"))
open("video.html", "w", encoding="utf-8").write(src.replace("__FONT__", font).replace("__WORDS__", json.dumps(words, ensure_ascii=False)))
print("ok")
