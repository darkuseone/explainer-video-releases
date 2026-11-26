# ai27a — AI 2027 («Он угадал 2026-й ещё в 2021-м»)

Готовый ролик: релиз `ai27a` (mp4 + publish.txt). 1080×1920, 25 fps, H.264 10 Мбит/с, −14 LUFS.
- `voice.txt` — текст для TTS с ударениями; `voice_final.txt` — что реально звучит после локальных вырезок (абзацы = фразы).
- `v/` — raw.mp3, vo.wav (trim.py → вырезки cutwav → rubberband ×1,07/1,08 → тёплая цепочка → loudnorm), words_asr.json, av.wav/av_meta.json.
- `b/` — timeline.json (docs/scripts/align_disp.py), r.py (сцены), mix.py, build.sh. Общий движок: docs/scripts/ai27eng.py, ai27prep.py, ai27mix.py.
