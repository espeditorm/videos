#!/usr/bin/env python3
"""Grid overlay to measure blank boards/screens on a plate: grid.py plate.png out.png [step=100]"""
import sys; from PIL import Image, ImageDraw
im=Image.open(sys.argv[1]).convert('RGB'); st=int(sys.argv[3]) if len(sys.argv)>3 else 100; d=ImageDraw.Draw(im)
for x in range(0,im.width,st): d.line([(x,0),(x,im.height)],fill=(255,0,255),width=1); d.text((x+3,3),str(x),fill=(255,255,0))
for y in range(0,im.height,st): d.line([(0,y),(im.width,y)],fill=(255,0,255),width=1); d.text((3,y+3),str(y),fill=(255,255,0))
im.save(sys.argv[2])
