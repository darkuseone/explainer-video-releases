# earshot SFX (MIT)

Звуки сгенерированы кодом инструментом earshot v0.4 (https://github.com/Leonxlnx/earshot, MIT). Без записей, без Mixkit — можно держать в публичном репо и использовать на YouTube/TikTok/Instagram.

- `onc10v2/kit.json` — пресет `launch` + своя роль `glitch` (glitch/mid).
- `onc10v2/kit.lock.json` — замеренные onset/peak/end и l50_lufs каждой дорожки.
- Перерендер: `earshot kit render kit.json --out <dir>` (детерминированно).
- Расстановка/сведение: `docs/projects/onc10v2/mix2.py`, cue-лист `cues.json`.
