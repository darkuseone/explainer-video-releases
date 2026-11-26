# HANDOFF: ролик cd10 «Нейросеть рисует пикселями, а код формулами» (2026-11-23)

Ветка: `claude/project-thread-ektagw`. Проект: `docs/projects/cd10/`. Правила пайплайна: `docs/VIDEO_PIPELINE.md` (там уже раздел HeyGen Avatar 6, PR #3 влит в main).

## Что готово
- Сценарий и текст: `script.md`, `voice.txt`.
- Озвучка ElevenLabs (eleven_v4, NIKITA, 1 дубль, 958 кредитов) — **НЕ перегенерировать**. Flow `hi7lUyxTXoqj6RaBCmuJ`, session `GuaJIOoXx7YU1bn6DWAo`, generation `TeT1ekHbSQ64y3QBtbII` (свежая ссылка: `creative_get_flow_run_status`). Копия: Google Drive fileId `1LkTfeoQaz2CdJCD0TREd1qAZi-ViH6gM`, в репо `v/raw.mp3`.
- Обработанная озвучка `v/vo.wav` (и `v/vo.mp3`): паузы сжаты (`b/trim.py`), темп ×1,07 (rubberband), тёплая цепочка, loudnorm −13,8 LUFS. **50,93 с.**
- Тайминги слов: `b/timeline.json` (`b/align.py`, без ASR).
- Аватар HeyGen **Avatar 6 Pro**, 1080p, 9:16, motion `less`, промпт без улыбки — **УЖЕ сгенерирован, не перегенерировать** (списано 11 кредитов, остаток 363). video_id `a2debe4e1ffb2eb894598cf703110610`. Клип 16,3 с: склейка двух сегментов озвучки (`v/av.mp3`, разметка `v/av_meta.json`: хук 0–6,93 с и финал 42,03–50,93 с). Копия на Google Drive fileId `1qyAjK1QF2hs1krkzsd7DKn2gEA2IO835` (>10 МБ).
- Рендер (Pillow, 25 fps, 1080×1920): `b/r.py` + `scene.py`, `lib.py`, `edge.py`. Все сцены написаны и проверены на превью; средние сцены без аватара рендерились без ошибок.
- Звук: `b/mix.py` → `b/mix.wav` (голос + музыка из библиотеки `audio/music/UwUT4EHqjTdgbYIRgFA8.mp3` с дакингом + SFX из `audio/sfx`), −13,7 LUFS. Уже в репо.
- Тексты для публикации: `docs/projects/cd10/publish.txt`.

## На чём остановились
Клип аватара не скачивался в облачной сессии (прокси закрыл `files2.heygen.ai`). Осталось:
1. Скачать клип: HeyGen `get_video` с `a2debe4e1ffb2eb894598cf703110610` → `video_url` → `curl -L -o /tmp/av.mp4 "<video_url>"`.
2. Проверить кроп карточки: `CROP=(150,250,1050,1290)` в `b/r.py` подобран по фото. Сделать `python3 r.py png /tmp/p.png -1,1,3,44,48` и посмотреть, что лицо и микрофон в карточке целиком. Если нет — поправить CROP.
3. Проверить, что Markus не улыбается (кадры `b/av/`). Если где-то улыбка, эти кадры не ставить.
4. Собрать: `cd docs/projects/cd10/b && ./build.sh /tmp/av.mp4` (prep_av.py → кадры `b/av/` + блок avatar в timeline.json; рендер в 4 потока; склейка; mix.py; экспорт `docs/projects/cd10/kod-cd10.mp4`, H.264 CRF 17 + AAC 192k).
5. Липсинк: проверить 5–10 слов (п/б/м) в хуке и финале; при сдвиге перезапустить `python3 prep_av.py /tmp/av.mp4 0.02` (второй аргумент — lag в секундах) и пересобрать. Измеренный lag Avatar 6 записать в VIDEO_PIPELINE.md раздел 4.
6. Выложить: `gh release create media-cd10 docs/projects/cd10/kod-cd10.mp4 -R darkuseone/explainer-video-releases -t "Нейросеть рисует пикселями, а код формулами" -n "cd10"` (или через GitHub MCP). Ссылка: `https://github.com/darkuseone/explainer-video-releases/releases/download/media-cd10/kod-cd10.mp4`. mp4 в git не коммитить.
7. Отчёт пользователю: ссылка, длина (~51 с), кредиты (HeyGen 11, ElevenLabs 958 на озвучку), PR #3 (инструкция Avatar 6).

## Правила пользователя (обязательно)
- Вау-хук в первую секунду (уже: карточка с аватаром раскалывается на пиксели/линии, двойники, частицы). Статичная надпись не висит на лице.
- Субтитры белые с тёмной обводкой, ключевые слова жёлтые `#FFD34D`, **не фиолетовые**.
- Аватар только в начале и в конце, **не улыбается**.
- Музыка только из библиотеки репо, новую не генерировать.
- **Никаких платных генераций** без прямой просьбы: ни озвучки, ни аватара, ни музыки, ни картинок. Озвучка всегда одним дублем.
- Обложка вшита первыми 3 кадрами (`cover()` в r.py, звук сдвинут на 0,12 с — уже в mix.py).
- Темп озвучки +5–7%, паузы сжатые, как в «Измерениях».
- Пользователь пишет по-русски, отвечать коротко, по делу.
