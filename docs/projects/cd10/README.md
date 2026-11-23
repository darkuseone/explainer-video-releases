# cd10 — «Нейросеть рисует пикселями, код — формулами» (черновик, 2026-11-23)

- `script.md`, `voice.txt` — сценарий и текст озвучки (ElevenLabs eleven_v4, NIKITA, 1 дубль, 958 кредитов; flow `hi7lUyxTXoqj6RaBCmuJ`, session `GuaJIOoXx7YU1bn6DWAo`, generation `TeT1ekHbSQ64y3QBtbII`, сырая длина 63,76 с — свежая ссылка на mp3 через `creative_get_flow_run_status`).
- `b/` — рендер (Pillow, 25 fps, 1080x1920):
  - `r.py` — сцены: хук (раздвоение аватара: пиксели/линии), зум «пиксели vs формула», диффузия (шум→картинка, 1 048 576 точек), код SVG печатается и рисует + билборд, правка «голубая луна» (нейросеть перерисовывает / код меняет 1 строку), 3D-слои «картинка ожила», фотограф vs чертёжник, финал с аватаром на фоне кода и превращением в `<svg>`. Обложка = 3 первых кадра (звук сдвигать на 0,12 с). Читает `timeline.json` (phrases, words, tot, avatar).
  - `scene.py` — векторная сцена «ночные горы + луна» (рендер при любом зуме) и «нейро»-растр; `edge.py` — line-art; `lib.py` — шрифты из `docs/fonts`, утилиты.
  - `align.py` — выравнивание текста по аудио без ASR (паузы по RMS + DP по слогам): `python3 align.py vo.wav timeline.json ../voice.txt`. `est_tl.py` — оценочный таймлайн для превью.
  - Превью: `python3 r.py png out.png 0.5,3,10`; рендер: `python3 r.py <f0> <f1> out.mkv`.
- Аватар: сегменты — фраза 1 (хук) и фразы 8–9 (финал), ~13 с; Avatar 6 Pro (если тариф не пустит — Turbo), `motionExpressiveness: less`, без улыбки; crop карточки `CROP=(150,250,1050,1290)` подобран по ref_markus.png — проверить по реальному клипу. В timeline.json добавить `avatar={segs:[{t0,t1,src0}],n,lag}` и кадры в `b/av/fNNNN.jpg`.
- Музыка: `audio/music/UwUT4EHqjTdgbYIRgFA8.mp3` (ещё не использовалась, 50 с, затухание с ~46 с). SFX из `audio/sfx` (whoosh, glitch, typing, tick, warm/*).
- Не сделано: озвучка не скачана (сеть сессии), паузы/темп 1,06, выравнивание, аватар, микс, экспорт, publish.txt.
