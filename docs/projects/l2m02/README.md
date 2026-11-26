# l2m02 — «Lineage 2 из нулевых на айфоне» (2026-11-25)

Готовый ролик: релиз `l2m02` (mp4 + publish.txt). 57,6 с, 1080×1920, 25 fps, H.264 High 10 Мбит/с, AAC 256k, −14,0 LUFS.

- `script.md` — утверждённый сценарий и план; `voice.txt` — текст озвучки с ударениями; `publish.txt`, `sources.md`.
- `v/` — `raw.mp3` (ElevenLabs), `vo.wav` (паузы сжаты `cd10/b/trim.py`, rubberband ×1,07, тёплая цепочка, loudnorm), `words_asr.json` (faster-whisper medium), `av.wav/av_meta.json` — сегменты для HeyGen.
- `b/` — `prep.py` (шоты из TikTok @l2meta_net → `shots/`), `mktl.py` (ASR → `timeline.json`), `r.py` (рендер), `mix.py` (голос + музыка + SFX → `mix.wav`), `build.sh` (полная сборка).
- Аватар HeyGen Avatar 6 Pro, 13,7 с (хук + финал), кадры в `b/av/` (не в git; скачать по video_id из sources.md и `ffmpeg -vf fps=25`).
- Исходники шотов не в git: TikTok @l2meta_net, id в `sources.md`.
