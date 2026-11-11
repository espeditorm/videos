---
name: studio-dito-videos
description: Studio Dito video machine. Use when the user says "make a video: [topic], [length]" (1-10 min) or asks for a Studio Dito / explainer video. Turns a topic into a finished 1920x1080 flat-vector animated explainer MP4 with narration, music, SFX and thumbnail, using the frozen channel DNA in dna.json and the tested engine in engine/.
---

# Studio Dito — video machine

One line starts a video: **`make a video: [topic], [length]`** (length 1-10 min).

Everything lives next to this file:
- `dna.json` — the channel identity. **Frozen.** Never reroll channel traits unless the user says "reroll X".
- `engine/` — tested code (see *Engine map*). Fix bugs here, never in one video's files, and log the fix under *Engine notes*.
- `library/` — style frames, host sheets/sprites/rig, home study plate + stings, fonts, `log.json` of every video.
- `work/<slug>/` — per-video scratch (gitignored). Final deliverables go to `library/videos/<slug>/`.

The user wants **minimum work on their side**: never ask them to download, upload or copy files. Only stop for the two approvals below (script + picks; and anything that spends money/credits beyond the Canva flow they already approved).

---

## Channel DNA (frozen, seed 8737978303937417221)

| Trait | Value |
|---|---|
| Palette | **Dusk Arcade**: deep plum `#4a2545`, muted cyan `#6fb3b8`, dusty magenta `#b5578a`, midnight blue `#1c2340`, warm butter yellow `#f2d17a` |
| Code colours | ink `#1c2340`, alert `#ce222d`, warm `#eb9147`, highlight `#eae43e`, success `#26b06b`, dark `#1c2340`, headline A `#b35388`, headline B `#407d81`, label `#8b8f9c`, card `#fcf3de`, transition `#f9eac3` |
| Characters | Big round heads, dot eyes, small bodies; each main character a different flat skin tone |
| Font | Archivo Black (`library/fonts/ArchivoBlack.woff2`), ALL CAPS on cards and signs |
| Cards | square-offset: radius 4, hard 8 px offset shadow in dark |
| HUD | top-right |
| Tag | label with a small triangle pointer, no line |
| Text entry | word-by-word pop, 28 units/s (34 for short tags) |
| Motion | **Punchy**: squash & stretch on every arrival (1.25x by 0.8x, settles in 0.2 s), kick 0.16 |
| Camera | slow 2-4% pushes and pans |
| Shot transition | vertical push, 0.25 s, whoosh 0.02 s before; ~1 in 6 a hard cut on a beat |
| Chapter transition | big paint swipe in transition fill, 0.2 s cover + 0.2 s clear |
| Narrator | gravelly older storyteller → **Kokoro `am_onyx`**, speed 1.0 (≈170 wpm) |
| Music | warm orchestral strings |
| Pace | **9 places/min**, something new every **2.04 s** |
| Host | recurring host: opens and closes every video, pops in once per chapter |
| Intro sting | host walks into the study and presents the title on the board (2.8 s) |
| Outro sting | paint swipe → study; signature motif in its final state + channel name on the board + host waves (3.6 s) |

**The host** (paste word for word into every host sheet): *a friendly older storyteller with a very big round head and a small body, two black dot eyes, small dusty magenta cheek dots, warm medium-brown skin, a short neat grey beard, short curly grey-black hair, round warm butter-yellow glasses, a muted cyan cardigan over a cream shirt, a deep plum bow tie, midnight-blue trousers, cream sneakers.* Sheets: `library/host/sheets/`, sprites (named): `library/host/sprites/` (+`expr/`, `poses/`), rig: `library/host/rig/` (`RIG.host`).

---

## Tools and routes (as set up)

- **Images: Canva `generate-image`** with `imageReferences` (Canva media ids). Figma Weave's free runs are used up — do not use it unless the user upgrades.
  Reference media ids (in `library/host/host.json`): style frames `MAHamU4K1j8`, `MAHambS6rXI`, `MAHamT3CFFY`; host base `MAHamQg_hfg`, expressions `MAHamcZYTDY`, poses `MAHamZfOEv8`; home study `MAHamnEm6hY`.
  Local files for upload: `library/style/frame{1,2,3}_*.png`.
- **Getting full-size files out of Canva (approved by the user, do it yourself):** generate-image only returns a 200 px preview. Use the helper design **`DAHammcJevY` ("Studio Dito – export")**:
  1. `read-design` with `open_transaction:true` → transaction id.
  2. `edit-design` `add_page` (one per image, title = file name) → `read-design` `design_content` for the new page ids.
  3. `edit-design` `insert_fill` (asset id, top 0, left 0, width 1920, height 1080) — several in one call is fine.
  4. `edit-design` `finalize:"commit"` (the user approved this flow once for all future runs).
  5. `export-design` png, `pages:[…]`, width 1920, height 1080, lossless, pro → curl the URLs into `library/…` / `work/<slug>/art/`.
  Native Canva size is 1680x944; export upsamples to 1920x1080 (fine for plates; quad tiles therefore stay ≤1.25x zoom).
- **Voice:** Kokoro (`work/models/kokoro-v1.0.onnx`, `voices-v1.0.bin`; re-download from the kokoro-onnx GitHub release `model-files-v1.0` if missing) + faster-whisper for word times (`small.en` for English, multilingual `small` otherwise).
  - **English** scripts: `--voice am_onyx --lang en-us`.
  - **Portuguese (pt-BR)** scripts: `--voice pm_alex --lang pt-br` (male, ~175 wpm). Kokoro reads English names with Portuguese phonemes, so keep `script.txt` as written (on-screen spelling) and feed the voice a `script_tts.txt` with phonetic respellings, e.g. `Black Mirror→Bléqui Mírror`, `Hated in the Nation→Rêitid in dê Nêichon`, `hacker→réquer`, `hackeou→réqueou`, `indoor→índór`, `MIT→ême-i-tê`; write numbers/fractions out in words. Whisper then hears the real English words. Expected diff noise: whisper writes "pra" as "para".
  - On-screen text follows the script language (HUD labels: `window.HUD_LABELS={date:'DATA:',place:'LOCAL:'}`).
- **Music:** Pixabay is blocked (403) and Mixkit listing pages refuse automated clients — do not try to get around that. Use `engine/music.py` (synthesized warm string beds, seeded per video: `--mood calm|tense|bright`). If the user supplies tracks, drop them in `library/music/` and pass them to `audio.py --music`.
- **SFX:** `engine/audio.py` synthesizes pop/tick/whoosh/thud/hit/ding/boing tuned to Punchy. Real files placed in `library/sfx/<name>.wav|mp3` override the synth automatically.
- **Python deps** (install if missing, tell the user): `opencv-python-headless faster-whisper kokoro-onnx soundfile numpy pillow`. Playwright + Chromium are preinstalled globally: run node scripts with `NODE_PATH=$(npm root -g)`.

---

## Every video

### 0. Inputs
Ask (only if not given): topic, length 1-10 min, and whether they have a script. Then:
- `python3 engine/roll_dna.py video` → script shape, hook type, signature motif, accent, thumbnail layout (already filtered against the last 5 entries of `library/log.json`).
- If they have no script, write it from the topic with those traits.

### 1. Length plan (show it with the script)
- Words = minutes × 175. Places = minutes × 9 (≈30% hero plates, rest from quad tiles, 4 per quad).
- Main characters: 1-2 under 3 min, 2-3 above (host not counted).
- Chapters: <2 min none (beats every 15-20 s); 2-5 min 3-4; 5-10 min 5-8.
- Images ≈ 1 min 12, 3 min 25, 5 min 40, 10 min 70 (Canva quota, no cash cost).
- Voice: one take <3 min, else chunks at chapter breaks (voice.py already splits on `---`).
- Render: one page <3 min, else `render_parallel.py --parts 5`.
- Over 5 min: spread motif + host pop-ins evenly.
- Total runtime = 2.8 s intro + narration + 3.6 s outro.

**Show the script, the per-video picks and these numbers. Wait for OK before any art.**

### 2. Art (Canva, batches, contact sheet after each)
Every prompt starts with the style core **word for word**:
> Flat vector illustration in exactly the same art style as the reference images: NO outlines or line art anywhere, every shape is a flat solid colour fill with at most one slightly darker flat shade for form, simple geometric shapes, crisp clean edges, no gradients, no texture, no painterly lighting. Muted modern palette: deep plum, muted cyan, dusty magenta, midnight blue, warm butter yellow. Characters are big round heads, dot eyes, small bodies. No text, no letters, no numbers, no logos.

then one setting line: "The setting is [time, place]: [materials, light sources], nothing from other eras unless asked." Always pass 2-3 style frames (and the host/character base sheet for sheets) as `imageReferences`, `aspectRatio: LANDSCAPE_16_9`.
- **Hero plates**: `EMPTY: no people, no characters, no animals.` Straight-on, open floor in the middle, blank signs/boards/screens/pages. ≥2 plates built around the signature motif.
- **Quad plates**: "The image is a 2x2 grid of FOUR completely separate scenes, each filling exactly one quarter of the image (each quarter is itself a 16:9 picture), divided by perfectly straight thin pure-white gutters, one vertical down the exact centre and one horizontal across the exact centre." + TOP-LEFT/TOP-RIGHT/BOTTOM-LEFT/BOTTOM-RIGHT. Split with `engine/quad.py`. Object close-ups make great tiles.
- **Main characters**: one fixed description each (age, hair, face, skin tone, every clothing item in palette colours) pasted word for word into every sheet. Base sheet (6 views: armless front neutral, armless front 2nd emotion, side walking right, back, 2 script poses), expression sheet (6 armless fronts), pose sheet (6 poses with props). Base sheet goes back in as reference.
- **Everyone else**: role sheets 4-6 people in their shot poses, crowd sheets 8-10 small figures, prop sheets.
- Every sheet: "on a solid flat chroma green background (#00B140) with lots of empty green space between figures; nothing touches, nothing on any character or object is green, full bodies, nothing cut off by the edges". (Palette has no green near #00B140 → green key.)
- **Thumbnail**: thumbnail layout from the roll, same characters, richer saturated lighting, extreme emotions, top quarter empty, no text, base sheets as references.
- Check every plate is EMPTY before cutting. Canva may ignore "no arms": check fronts; regenerate if arms are drawn out from the body.

### 3. Cutouts and rig
- `python3 engine/cutout.py sheet.png outdir --names a,b,c` → named sprites + `_contact.png` (show it).
- Armless fronts → puppets: `python3 engine/rig.py front.png work/<slug>/ name` (appends to `work/<slug>/rig.js`; check `name_rigdebug.png`: red neck line under the beard, yellow sockets at the shoulders, cyan eye boxes on the dots).
- Side/back/pose sprites stay whole (`ENG.figure`).
- Measure blank boards/screens: `python3 engine/grid.py plate.png grid.png 50`.

### 4. Voice
Script file: chapters separated by a line `---`. `python3 engine/voice.py script.txt work/<slug> --voice am_onyx --offset 2.8` → `voice.wav` (0.3 s lead-in, pauses >0.24 s cut to 0.16 s, 0.5 s at chapter breaks), `words.js`, `voice_report.json`. Check `match` ≥ 0.95 and read the diffs (numbers are normalised; anything else is a misread → fix spelling in the script and re-run).

### 5. Shots
- `work/<slug>/assets.json` maps image names → paths. `python3 engine/page.py work/<slug> work/<slug>/assets.json work/<slug>/shots_ch1.js …` builds `index.html` (dna.js, host rig, words.js, player.js, stings.js are added automatically; `home`, `host_*` assets too).
- Shot files set `window.END` and `window.BUILD=function(){…}`. Inside BUILD:
  - `STING.intro(0,'TITLE')` first. Build the voice with `--offset 2.8` so the narration (and every WORDS time) starts after the intro.
  - `S('exact words', (t,sh)=>{…}, {occ:n, cut:'hard'})` starts a shot 0.08 s before the phrase. One function per shot, one file per chapter.
  - `CHAPTER('first words of chapter')` → paint swipe.
  - In a shot: `ENG.plate(t,sh,'plateName',[z,fx,fy],[z,fx,fy],()=>{ …plate-space drawing… })` (slow push; zoom ≤1.25 on quad tiles, deeper only on hero plates); characters `ENG.puppet(t,'name',{x,y,h,t0,hop,flip,seed,talk:[[s,e]],pose:[[t,'rest'],[t2,'point']…]})` / `ENG.figure(t,'sprite',{x,y,h,t0,walk:{from,to,t0,t1},hop,dark})`.
  - Kit (`ENG.G`): `write` (on a plate's blank board), `board`, `hud(t,t0,'date'|'place',value,slot)`, `tag(t,t0,x,y,label,{side,fill})`, `number`, `redX`, `stamp`, `banner` (episode accent leads), `bubble`, `qmark`, `bang`, `puff`, `speedLines`, `vignette`, `tint`. Register sound once in BUILD with `ENG.ev(t,name,gain)` / `G.*Events`.
  - Poses: down rest hips point present shrug up head chin hold wave stop cheer.
  - Every character on screen acts on its line; the host pops in once per chapter; the motif appears at least once per chapter; something new every ≤2.04 s; new place every ≈6.7 s; never hold a still > 1 s.
  - `STING.outro(tEnd,{motif:(t,t0)=>{…final state…}})` last; `window.END = tEnd + STING.OUTRO`.
- Night shots: pass `dark:k` to figures/puppets.

### 6. Check before the full render
Contact sheet per chapter, one frame every 2 s (`ffmpeg -vf fps=0.5,scale=480:270,tile=4x4` on a quick `--blur 1` render, or screenshots via seek). Fix: empty/overflowing signs, text over a face, black plate edges, floating feet, two shots in a row in the same place, any gap > 4.1 s with nothing new, anything off-DNA (font, colours, card style, transitions).

### 7. Render and mix
- `NODE_PATH=$(npm root -g) node engine/render.js work/<slug>/index.html work/<slug>/picture.mp4` (30 fps, 4 motion-blur subframes over half a frame, CRF 17). ≈6 s of wall time per video second per page → over 3 min use `python3 engine/render_parallel.py … --parts 5 --end END`.
- Music: `python3 engine/music.py work/<slug>/bed1.wav <secs> --seed N --mood calm` (2-3 beds, different moods; crossfade at big beats via `--chapters`).
- `python3 engine/audio.py voice.wav picture.events.json mix.wav --dur END --music bed1.wav,bed2.wav --chapters t1,t2` → ducked music, SFX on peaks, gate report, two-pass loudnorm −14 LUFS / −1 dBTP. `gate_ok` must be true.
- `ffmpeg -i picture.mp4 -i mix.wav -c:v copy -c:a aac -b:a 192k -shortest final.mp4`.
- Scan for single-frame jumps (`ffmpeg -vf "select='gt(scene,0.4)',showinfo"`) and confirm each is a planned cut.

### 8. Deliver
Copy `final.mp4` + `thumbnail.png` to `library/videos/<slug>/`, send both to the user, append `{topic,length,date,slug,picks}` to `library/log.json`, commit and push.

---

## Engine map
| File | Does |
|---|---|
| `engine/roll_dna.py` | `channel` / `video` rolls from os.urandom; colour derivation + contrast/hue checks; clash rules |
| `engine/dna_card.py` | one-screen DNA card PNG |
| `engine/cutout.py` | border-connected chroma key (+ strict pass for enclosed key pockets), 2 px soft band with G clamp, grouping, names, contact sheet |
| `engine/quad.py` | 2x2 quad split on the white gutters → four 1920x1080 tiles |
| `engine/rig.py` | neck split, sockets, eye boxes, skin/sleeve colours, collar inpaint, `rig.js`, debug overlay |
| `engine/grid.py` | measuring grid over a plate |
| `engine/player.js` | the canvas engine: seek(t)/READY/END/EV, motion primitives, camera, kit, puppets (IK arms, breathing, nods, blinks), transitions |
| `engine/stings.js` | intro/outro stings on the home study (`library/stings/home.json`) |
| `engine/page.py` | builds a video's `index.html` |
| `engine/render.js` / `render_parallel.py` | frame-exact rendering to H.264 |
| `engine/voice.py` | Kokoro → pause trim → whisper word times → `words.js` + diff |
| `engine/music.py` | synthesized warm-strings beds |
| `engine/audio.py` | SFX bus, ducking, gate, loudnorm |

Look test: `library/looktest/looktest.mp4` (`work/looktest/shots.js` is the reference shot file). Stings sample: `library/stings/stings_sample.mp4` (`work/stings/shots.js`).

## Engine notes (bugs fixed — keep adding)
- audio.py: loudnorm (linear) left true peak at −0.6 dB → a limiter at 0.84 now follows it (−1.2 dBTP measured). Music at `--music-db -24` passed the gate (16.4 dB); −19 failed (11.8 dB).
- render.js: `waitForFunction(fn, arg, options)` — the timeout must be the 3rd argument (passing it 2nd silently kept the 30 s default and killed a parallel render). BOOT's event pass now runs at 10 fps, not every frame.
- Phrase lookup (`at()`) is accent-insensitive and splits hyphenated words ("abelhas-robôs" → two tokens); anchor shots on words whisper actually printed (check `words.js`), e.g. respelled words come back as whisper heard them.
- Rig eye finder: blobs must be small (<16% of head width), round, filled, and ringed by skin — goggles/hair at the sides of a face were picked as eyes before.
- Intro title wraps after hyphens, so a single long hyphenated word still fills the board.
- Banner takes `{color, textColor}`: a light accent (butter) needs ink text; white caps only on headline A/B.
- Shot helper pattern (see `work/abelhas-robos/shots.js`): `shot(phrase, plate, camA, camB, inner, overlay, {shake:[t,A], cut:'hard'})` and `fly(t, sprite, {t0,t1,h,path,seed})` for insects/drones — copy them into new shot files.
- People behind furniture (podiums, desks): clip the figure above the furniture top (`behind(yCut, fn)`).
- faster-whisper + installed PyAV: `decode_audio` breaks (`metadata_errors`) → voice.py feeds a 16 kHz float array.
- Rig: eye dots are ~(46,44,58) inside glasses → dark threshold is relative to skin; skin is picked from warm pixels (hair is grey-blue).
- Cutout: green pockets enclosed between head and shoulders survive a border-only key → strict second pass (dom > 70, within 55 of key) for blobs ≥30 px.
- Rig inpaint used RGB hidden under alpha=0 (green) → rig zeroes RGB where alpha is 0 and limits the collar band to the neck's own width.
- Arms for this big-head build: L1 0.145, L2 0.135, thickness 0.05 of figure height (thinner looks like twigs). When the arm hangs at rest it merges with the cardigan sleeve colour — that is fine.
- Screen-space stamps don't follow the camera: place them on empty floor or on a board, never over a character (look test had it over the host's face).
- Fonts: Google's CSS lists latin-ext first; the engine font file must be the **latin** subset.
- `.gitignore` drops `*.png` and `*.wav` repo-wide; `library/**.png` is re-included; music beds and voice are regenerated per video.
