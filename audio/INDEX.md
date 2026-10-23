# Аудиобиблиотека (музыка, подложки, SFX)

Здесь собраны все звуки, которые нашлись на рабочей машине в `/workspace` и `/home/box`. Дубли убраны по SHA-1, колонка «копий» показывает, сколько одинаковых файлов было найдено. WAV больше 3 МБ пересохранены в FLAC без потерь.

**Что сюда не входит:**
- озвучка (голос Markus, сырые дубли, сегменты для HeyGen, превью голосов ElevenLabs);
- финальные миксы и стемы роликов (mix, master, st_*, qc_pack);
- чужая песня из скилла last30days;
- тестовые файлы библиотек.

Колонка «ролики» заполнена автоматически: имя файла искалось в скриптах сведения каждого проекта. Если стоит «—», совпадений не нашлось. Это не значит, что файл точно нигде не использовался. Колонка «лицензия» указана только там, где она где-то записана, остальное честно помечено как неизвестное. Описания для Tesla и pixel взяты из каталогов и манифестов, у остальных файлов описания нет.

Скрипты синтеза лежат в `synth/`. Это `earshot/forge` (банк из 201 кодогенерируемого SFX, лицензия MIT, источник github.com/Leonxlnx/earshot; файлы `fit_*` в этой библиотеке сделаны на нём) и `cinetic/audio` (synth, kit, score, master; MIT, github.com/Leonxlnx/cinetic). Как рендерить без torch, описано в `docs/VIDEO_PIPELINE.md`, раздел 5.5. Скрипты, которыми синтезировали halluc/sfx, halluc/v2/sfx2 и universe93/b/sfx, на машине не нашлись.

| файл | длит., с | что это | ролики | источник | лицензия | копий |
|---|---|---|---|---|---|---|
| `beds/bed.flac` | 46.60 | — | universe93, Redshift-shorts | не записано (на машине: universe93/b/sfx) | неизвестно | 1 |
| `beds/bed1.mp3` | 178.97 | — | — | не записано (на машине: tmp/audit/wosv/assets/music) | неизвестно | 6 |
| `beds/bed1__assets.mp3` | 176.30 | — | — | не записано (на машине: tmp/Pawn-stories/assets/music) | неизвестно | 1 |
| `beds/bed2.mp3` | 175.27 | — | — | не записано (на машине: tmp/audit/wosv/assets/music) | неизвестно | 6 |
| `beds/bed2__assets.mp3` | 161.66 | — | — | не записано (на машине: tmp/Pawn-stories/assets/music) | неизвестно | 1 |
| `beds/bed3.mp3` | 166.18 | — | — | не записано (на машине: tmp/audit/wosv/assets/music) | неизвестно | 6 |
| `beds/bed3__assets.mp3` | 164.86 | — | — | не записано (на машине: tmp/Pawn-stories/assets/music) | неизвестно | 1 |
| `beds/bed4.mp3` | 158.83 | — | — | не записано (на машине: tmp/audit/wosv/assets/music) | неизвестно | 6 |
| `beds/bed4__assets.mp3` | 176.14 | — | — | не записано (на машине: tmp/Pawn-stories/assets/music) | неизвестно | 1 |
| `beds/bed5.mp3` | 176.54 | — | — | не записано (на машине: tmp/audit/wosv/assets/music) | неизвестно | 6 |
| `beds/bed5__assets.mp3` | 176.88 | — | — | не записано (на машине: tmp/Pawn-stories/assets/music) | неизвестно | 1 |
| `beds/bed_raw.flac` | 46.60 | — | — | не записано (на машине: universe93/b/sfx) | неизвестно | 1 |
| `beds/data_sonification_low.m4a` | 70.00 | — | Redshift-shorts | Redshift-shorts, music_manifest.json: «предоставлено заказчиком» | неизвестно (предоставлено заказчиком) | 13 |
| `beds/data_sonification_strings.m4a` | 70.00 | — | Redshift-shorts | Redshift-shorts, music_manifest.json: «предоставлено заказчиком» | неизвестно (предоставлено заказчиком) | 13 |
| `beds/m2_season_bed_lofi_toy_piano.mp3` | 45.00 | Сезонный музыкальный бед: лоу-фай, игрушечное пианино. Заменяет процедурный лоу-фай пилота. Петля 9–42 с (ровная энергия | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `beds/pad.flac` | 21.07 | — | — | не записано (на машине: exoplanet_explainer/proj/public) | неизвестно | 1 |
| `music/CuIAqvgYvYSIBrRdLAub.mp3` | 50.04 | Dark cinematic electronic 124 BPM (ElevenLabs music, Tesla) | tesla | ElevenLabs (генерация, Tesla) | ElevenLabs — коммерческое использование по подписке | 1 |
| `music/UwUT4EHqjTdgbYIRgFA8.mp3` | 50.04 | Тот же промпт, альтернативный дубль | — | ElevenLabs (генерация, Tesla) | ElevenLabs — коммерческое использование по подписке | 1 |
| `music/earth_from_orbit.m4a` | 70.00 | — | Redshift-shorts | Redshift-shorts, music_manifest.json: «предоставлено заказчиком» | неизвестно (предоставлено заказчиком) | 13 |
| `music/gravitational_pull.m4a` | 70.00 | — | Redshift-shorts | Redshift-shorts, music_manifest.json: «предоставлено заказчиком» | неизвестно (предоставлено заказчиком) | 13 |
| `music/integrated-melodic-tech-mix.wav` | 12.00 | — | — | Redshift-shorts/assets (sfx) | не записана | 1 |
| `music/interstellar_distance.m4a` | 70.00 | — | Redshift-shorts | Redshift-shorts, music_manifest.json: «предоставлено заказчиком» | неизвестно (предоставлено заказчиком) | 13 |
| `music/late_night_research.m4a` | 70.00 | — | Redshift-shorts | Redshift-shorts, music_manifest.json: «предоставлено заказчиком» | неизвестно (предоставлено заказчиком) | 13 |
| `music/lofi_toy_piano_procedural.wav` | 16.30 | — | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `music/m1_newsreel_to_lofi.mp3` | 16.03 | Главная тема: медный стинг кинохроники → лоу-фай. Используется только брасс 2,9–6,95 с (после интро трек почти пустой —  | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 2 |
| `music/m3_chase_loop.mp3` | 40.03 | Сезонный трек погони/слэпстика, петля: 120 BPM (доля 0,5 с, такт 2 с), ровная энергия от начала до конца, без интро и фи | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `music/music.flac` | 21.07 | — | tesla, v6, v3 | не записано (на машине: exoplanet_explainer/proj/public) | неизвестно | 1 |
| `music/music_0.mp3` | 54.00 | — | v3 | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `music/music_1.mp3` | 54.02 | — | v3 | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `music/music_C0t6.mp3` | 48.02 | — | — | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `music/music_rusk.mp3` | 48.02 | — | v6 | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `music/musicf.flac` | 48.00 | — | v6 | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `music/musicf_0.flac` | 53.96 | — | — | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 2 |
| `music/musicf_1.flac` | 54.00 | — | — | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 2 |
| `music/neural_data.m4a` | 70.00 | — | Redshift-shorts | Redshift-shorts, music_manifest.json: «предоставлено заказчиком» | неизвестно (предоставлено заказчиком) | 13 |
| `music/synapse_wonder.m4a` | 70.00 | — | Redshift-shorts | Redshift-shorts, music_manifest.json: «предоставлено заказчиком» | неизвестно (предоставлено заказчиком) | 13 |
| `music/wonder_and_scale.m4a` | 70.00 | — | Redshift-shorts | Redshift-shorts, music_manifest.json: «предоставлено заказчиком» | неизвестно (предоставлено заказчиком) | 13 |
| `sfx/ambient/9RAHSu9s7685zOWMjMec.mp3` | 1.04 | Industrial fan spin-up | tesla | ElevenLabs (генерация, Tesla) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/ambient/ambient_space_engine_04.ogg` | 5.00 | Sci-Fi Sounds: spaceEngineLow_002 | — | Kenney, «Sci-Fi Sounds: spaceEngineLow_002», https://kenney.nl/assets/sci-fi-sounds | CC0 1.0 | 1 |
| `sfx/ambient/oven_hum.wav` | 6.00 | — | universe93 | не записано (на машине: universe93/b/sfx) | неизвестно | 1 |
| `sfx/ambient/s01_wind_howl.mp3` | 6.03 | Вой ветра / зимний экстерьер | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 2 |
| `sfx/ambient/s02_film_crackle.mp3` | 3.53 | Треск киноплёнки | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 2 |
| `sfx/ambient/s03_neon_buzz.mp3` | 3.03 | Гудение неона (питч вниз = гул счётчика) | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 2 |
| `sfx/crowd/gasp_0.mp3` | 1.04 | — | tesla | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/crowd/gasp_1.mp3` | 1.04 | — | tesla | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/crowd/ooh_0.mp3` | 1.04 | — | tesla | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/crowd/ooh_1.mp3` | 2.04 | — | — | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/foley/coin_pickup.wav` | 1.20 | — | Redshift-shorts | Redshift-shorts/assets (sfx) | не записана | 13 |
| `sfx/foley/electric_airflow.wav` | 2.00 | — | Redshift-shorts | Redshift-shorts/assets (sfx) | не записана | 13 |
| `sfx/foley/electric_spark.wav` | 0.70 | — | Redshift-shorts | Redshift-shorts/assets (sfx) | не записана | 13 |
| `sfx/foley/hat_open.wav` | 0.74 | — | Redshift-shorts | Redshift-shorts/assets (sfx) | не записана | 13 |
| `sfx/foley/m4c_drum_roll.mp3` | 2.25 | Барабанная дробь перед твистом (часть M4, сделана как SFX) | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/foley/n01_hammer_drill.mp3` | 1.04 | Перфоратор за стеной, короткая очередь 0,89 с (глухой вариант = lowpass в mix.py) | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/foley/n02_plaster_crumble.mp3` | 1.04 | Осыпание штукатурки (тихий исходник, peak −16,8 dB; в миксе ×5,5) | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/foley/n03_calendar_tear.mp3` | 2.04 | Отрыв листа отрывного календаря | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/foley/n05_instant_freeze.mp3` | 1.52 | Мгновенная заморозка: треск льда + стеклянный «дзынь» | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/foley/n06_lift_jolt.mp3` | 2.04 | Лифт: резкий рывок, металлический удар-остановка, дребезг тросов | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/foley/n06b_lift_doors.mp3` | 1.80 | Лифт: створки разъезжаются (лязг + удар); в ep03 и на открытие, и (тише) на закрытие | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/foley/n07_lift_buttons.mp3` | 2.51 | Кнопки лифта: щелчки 0,01/0,20/0,39/0,61/1,06/1,27/1,57 с, электронный бип 1,98–2,3 с + треск интеркома; режется на отде | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/foley/n08_phone_ring_hangup.mp3` | 3.53 | Входящий звонок (0–0,95 с) + короткие гудки «сброшено» (2,05–2,75 с) | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/foley/n10_card_fire.mp3` | 3.03 | Вспышка пламени (карта вспыхивает с «вжух») + живой треск костра | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/foley/n11_mouse_squeak.mp3` | 0.84 | Мультяшный писк мыши (два писка 0,10 и 0,37 с) | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/foley/n18_plug_pull.mp3` | 0.84 | Вилка выдёргивается из розетки: щелчок + искра | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/foley/n19_fabric_drag.mp3` | 1.52 | Ткань: свист/шуршание пледа, волочение по полу | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/foley/n20_phone_shutter.mp3` | 1.04 | Щелчок затвора камеры телефона | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/foley/n20_phone_shutter_take1.mp3` | 0.63 | — | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/foley/rumble_air.wav` | 1.69 | — | Redshift-shorts | Redshift-shorts/assets (sfx) | не записана | 13 |
| `sfx/foley/s05_teeth_chatter.mp3` | 1.52 | Стук зубов | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 2 |
| `sfx/foley/s06_cat_sneeze_icicle.mp3` | 1.80 | Чих кота + «дзынь» сосульки (реверс «дзынь» = отрастание) | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 2 |
| `sfx/foley/sfx-production.wav` | 5.00 | — | — | Redshift-shorts/assets (sfx) | не записана | 13 |
| `sfx/foley/stretch.wav` | 1.20 | — | universe93 | не записано (на машине: universe93/b/sfx) | неизвестно | 1 |
| `sfx/foley/vpn-sfx.wav` | 7.00 | — | — | Redshift-shorts/assets (sfx) | не записана | 13 |
| `sfx/foley/w.wav` | 1.35 | — | exoplanet_v7, depth2d, lhc, universe93, moon, neutron, nuke, tesla, v6, v3, gta6, Redshift-shorts | не записано (на машине: ext/sfx_test) | неизвестно | 1 |
| `sfx/impact/KnLiHTf7KA8kvRmDvmPn.mp3` | 1.04 | EV launch whoosh A | tesla | ElevenLabs (генерация, Tesla) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/impact/NHBDDvqpCaW9WbuWrNiv.mp3` | 2.04 | Sub-bass drop с обратным свеллом | tesla | ElevenLabs (генерация, Tesla) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/impact/Xa1m6CjuTEQUAop1bAuy.mp3` | 1.04 | EV launch whoosh B | tesla | ElevenLabs (генерация, Tesla) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/impact/b1pjosiK7LynySnEDUgS.mp3` | 2.04 | Thruster burst B | tesla | ElevenLabs (генерация, Tesla) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/impact/boing.wav` | 0.60 | — | universe93 | не записано (на машине: universe93/b/sfx) | неизвестно | 1 |
| `sfx/impact/boom.wav` | 1.20 | — | — | не записано (на машине: exoplanet_explainer/proj/public) | неизвестно | 1 |
| `sfx/impact/ckpS5uwPp56pvLCtTQoL.mp3` | 1.04 | Cold-gas thruster burst A | tesla | ElevenLabs (генерация, Tesla) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/impact/deflate.wav` | 1.00 | — | universe93 | не записано (на машине: universe93/b/sfx) | неизвестно | 1 |
| `sfx/impact/drop1.wav` | 1.14 | — | halluc, exoplanet_v7, neutron | не записано (на машине: halluc/sfx) | неизвестно | 2 |
| `sfx/impact/fit_hit_bamboo_tok.wav` | 0.17 | — | nuke | earshot bank (код-синтез, github.com/Leonxlnx/earshot) | MIT (код); звук сгенерирован локально | 1 |
| `sfx/impact/glitch_hit.wav` | 0.34 | — | lhc, neutron, nuke | не записано (на машине: halluc/v2/sfx2) | неизвестно | 1 |
| `sfx/impact/heart.flac` | 50.83 | — | halluc, exoplanet_v7 | не записано (на машине: halluc) | неизвестно | 1 |
| `sfx/impact/hit_conga.wav` | 0.07 | — | Redshift-shorts | Redshift-shorts/assets (sfx) | не записана | 13 |
| `sfx/impact/hit_punch.wav` | 0.50 | — | Redshift-shorts | Redshift-shorts/assets (sfx) | не записана | 13 |
| `sfx/impact/hit_silence.wav` | 0.55 | — | Redshift-shorts | Redshift-shorts/assets (sfx) | не записана | 13 |
| `sfx/impact/hit_thud.wav` | 0.62 | — | Redshift-shorts | Redshift-shorts/assets (sfx) | не записана | 13 |
| `sfx/impact/hook_hit.wav` | 0.67 | — | halluc, exoplanet_v7, depth2d, lhc, universe93, moon, neutron, nuke | не записано (на машине: halluc/sfx) | неизвестно | 3 |
| `sfx/impact/impact_0.mp3` | 0.52 | — | tesla | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/impact/impact_0__audio.mp3` | 1.04 | — | tesla | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/impact/impact_1.mp3` | 3.03 | — | tesla | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/impact/impact_1__audio.mp3` | 2.04 | — | tesla | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/impact/m4a_twist_sting.mp3` | 2.04 | Стинг-твист (тарелка + туба), сделан как SFX вместо отдельного музыкального трека M4 — экономия | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/impact/n02b_sticker_slap.mp3` | 1.04 | Шлепок наклейки (атака 0–0,3 с) | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/impact/n04_door_knock.mp3` | 1.52 | Стук в дверь: 4 сухих удара (0,10/0,35/0,65/0,95 с), в ep02 используются 3 | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/impact/n04_door_knock_take1.mp3` | 2.04 | — | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/impact/n21_sign_crash.mp3` | 1.52 | Мультяшный грохот: металлическая табличка падает, лязг, дребезг, финальный удар | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/impact/plop.wav` | 0.25 | — | universe93 | не записано (на машине: universe93/b/sfx) | неизвестно | 1 |
| `sfx/impact/pro_tap_knock.wav` | 0.09 | — | halluc, exoplanet_v7, lhc, universe93 | не записано (на машине: halluc/v2/sfx2) | неизвестно | 1 |
| `sfx/impact/stamp1.wav` | 0.99 | — | halluc, exoplanet_v7, depth2d, lhc, universe93, moon, neutron, nuke | не записано (на машине: halluc/sfx) | неизвестно | 1 |
| `sfx/impact/stamp_0.mp3` | 2.04 | — | tesla | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/impact/stamp_0__audio.mp3` | 1.04 | — | tesla | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/impact/stinger_bell_heavy_05.ogg` | 1.48 | Impact Sounds: impactBell_heavy_000 | gta6 | Kenney, «Impact Sounds: impactBell_heavy_000», https://kenney.nl/assets/impact-sounds | CC0 1.0 | 1 |
| `sfx/impact/stinger_metal_heavy_04.ogg` | 0.36 | Impact Sounds: impactMetal_heavy_001 | universe93, gta6 | Kenney, «Impact Sounds: impactMetal_heavy_001», https://kenney.nl/assets/impact-sounds | CC0 1.0 | 1 |
| `sfx/impact/tFvhqu7pbYD4imCcgIPp.mp3` | 14.03 | Tense cinematic riser 14 c | tesla | ElevenLabs (генерация, Tesla) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/impact/thock.wav` | 0.45 | — | halluc, exoplanet_v7, depth2d, lhc, universe93, neutron | не записано (на машине: halluc/sfx) | неизвестно | 2 |
| `sfx/impact/twist_hit.wav` | 1.31 | — | halluc, exoplanet_v7, depth2d, lhc, universe93, moon, neutron, nuke | не записано (на машине: halluc/sfx) | неизвестно | 2 |
| `sfx/impact/zn4SikKHDo59ctCp69Im.mp3` | 0.52 | Sub-bass drop impact, короткий | tesla | ElevenLabs (генерация, Tesla) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/riser/pro_riser_air_gate.wav` | 1.20 | — | lhc, universe93, moon | не записано (на машине: halluc/v2/sfx2) | неизвестно | 1 |
| `sfx/riser/riser1.wav` | 1.30 | — | halluc, exoplanet_v7, depth2d | не записано (на машине: halluc/sfx) | неизвестно | 1 |
| `sfx/riser/riser_0.mp3` | 2.04 | — | — | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/riser/riser_0__audio.mp3` | 4.05 | — | — | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/riser/riser_1.mp3` | 14.03 | — | — | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/riser/riser_forcefield_04.ogg` | 0.95 | Sci-Fi Sounds: forceField_001 | gta6 | Kenney, «Sci-Fi Sounds: forceField_001», https://kenney.nl/assets/sci-fi-sounds | CC0 1.0 | 1 |
| `sfx/riser/riser_tension.wav` | 2.80 | — | depth2d, moon, neutron, nuke | не записано (на машине: halluc/v2/sfx2) | неизвестно | 1 |
| `sfx/riser/swell_0.mp3` | 2.04 | — | — | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/ui/87144WDaapBvmVES3R9y.mp3` | 2.04 | Digital glitch B | tesla | ElevenLabs (генерация, Tesla) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/ui/RfX9NkwHXVNvcQqj2BQv.mp3` | 2.04 | Digital glitch / HUD blips A | tesla | ElevenLabs (генерация, Tesla) | ElevenLabs — коммерческое использование по подписке | 1 |
| `sfx/ui/chime.wav` | 1.00 | — | — | не записано (на машине: exoplanet_explainer/proj/public) | неизвестно | 1 |
| `sfx/ui/chime_0.mp3` | 1.04 | — | — | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/ui/chime_kalimba_e.wav` | 1.55 | — | Redshift-shorts | Redshift-shorts/assets (sfx) | не записана | 13 |
| `sfx/ui/chime_kalimba_g.wav` | 1.50 | — | Redshift-shorts | Redshift-shorts/assets (sfx) | не записана | 13 |
| `sfx/ui/click1.wav` | 0.05 | — | halluc, universe93 | не записано (на машине: halluc/sfx) | неизвестно | 1 |
| `sfx/ui/click_claves.wav` | 0.06 | — | Redshift-shorts | Redshift-shorts/assets (sfx) | не записана | 13 |
| `sfx/ui/click_wood.wav` | 0.06 | — | Redshift-shorts | Redshift-shorts/assets (sfx) | не записана | 13 |
| `sfx/ui/counter_0.mp3` | 1.04 | — | — | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/ui/ding1.wav` | 0.36 | — | halluc, exoplanet_v7, depth2d, lhc, universe93, moon, neutron, nuke | не записано (на машине: halluc/sfx) | неизвестно | 1 |
| `sfx/ui/ding2.wav` | 0.27 | — | lhc, universe93, neutron, nuke | не записано (на машине: halluc/sfx) | неизвестно | 1 |
| `sfx/ui/dl1.wav` | 1.79 | — | — | не записано (на машине: halluc/sfx) | неизвестно | 2 |
| `sfx/ui/fit_click_floss_lid.wav` | 0.13 | — | — | earshot bank (код-синтез, github.com/Leonxlnx/earshot) | MIT (код); звук сгенерирован локально | 1 |
| `sfx/ui/fit_land.light_finger_phone.wav` | 0.33 | — | halluc, exoplanet_v7 | earshot bank (код-синтез, github.com/Leonxlnx/earshot) | MIT (код); звук сгенерирован локально | 1 |
| `sfx/ui/fit_land.light_finger_wood.wav` | 0.34 | — | halluc, exoplanet_v7, depth2d, lhc, nuke | earshot bank (код-синтез, github.com/Leonxlnx/earshot) | MIT (код); звук сгенерирован локально | 1 |
| `sfx/ui/fit_land.light_fingertip_book.wav` | 0.38 | — | — | earshot bank (код-синтез, github.com/Leonxlnx/earshot) | MIT (код); звук сгенерирован локально | 1 |
| `sfx/ui/fit_pop_lip_pop.wav` | 0.22 | — | halluc, exoplanet_v7, depth2d, lhc, universe93 | earshot bank (код-синтез, github.com/Leonxlnx/earshot) | MIT (код); звук сгенерирован локально | 1 |
| `sfx/ui/gl1.wav` | 0.49 | — | — | не записано (на машине: halluc/sfx) | неизвестно | 2 |
| `sfx/ui/glitch_0.mp3` | 1.04 | — | — | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/ui/logo1.wav` | 1.07 | — | lhc | не записано (на машине: halluc/sfx) | неизвестно | 1 |
| `sfx/ui/notify_m5.wav` | 1.70 | — | depth2d, lhc, moon | не записано (на машине: halluc/v2/sfx2) | неизвестно | 1 |
| `sfx/ui/particles_0.mp3` | 0.52 | — | — | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/ui/photon.wav` | 1.60 | — | universe93 | не записано (на машине: universe93/b/sfx) | неизвестно | 1 |
| `sfx/ui/pop1.wav` | 0.10 | — | halluc, depth2d, lhc, moon, neutron, nuke | не записано (на машине: halluc/sfx) | неизвестно | 1 |
| `sfx/ui/pop2.wav` | 0.15 | — | halluc, depth2d, lhc, moon, neutron | не записано (на машине: halluc/sfx) | неизвестно | 1 |
| `sfx/ui/pro_glitch_standard.wav` | 0.71 | — | halluc, exoplanet_v7, depth2d | не записано (на машине: halluc/v2/sfx2) | неизвестно | 1 |
| `sfx/ui/pro_typing_key_soft.wav` | 0.07 | — | depth2d, lhc, neutron | не записано (на машине: halluc/v2/sfx2) | неизвестно | 1 |
| `sfx/ui/s04_speaker_chime.mp3` | 1.04 | Перезвон колонки (реверс = выключение/перезагрузка) | pixel | ElevenLabs (генерация, flow 9Y1LlE9RXp3c7NL9UpuK, проект pixel) | ElevenLabs — коммерческое использование по подписке | 2 |
| `sfx/ui/shimmer_0.mp3` | 0.52 | — | tesla | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/ui/snap_clap.wav` | 0.23 | — | Redshift-shorts | Redshift-shorts/assets (sfx) | не записана | 13 |
| `sfx/ui/sub_click.wav` | 0.19 | — | halluc, exoplanet_v7, depth2d, lhc, universe93, moon, neutron, nuke | не записано (на машине: halluc/sfx) | неизвестно | 2 |
| `sfx/ui/tick1.wav` | 0.04 | — | — | не записано (на машине: halluc/sfx) | неизвестно | 1 |
| `sfx/ui/tick2.wav` | 0.04 | — | halluc | не записано (на машине: halluc/sfx) | неизвестно | 2 |
| `sfx/ui/tick3.wav` | 0.03 | — | — | не записано (на машине: halluc/sfx) | неизвестно | 1 |
| `sfx/ui/tick4.wav` | 0.14 | — | — | не записано (на машине: halluc/sfx) | неизвестно | 1 |
| `sfx/ui/tone67.wav` | 0.50 | — | universe93 | не записано (на машине: universe93/b/sfx) | неизвестно | 1 |
| `sfx/ui/tone73.wav` | 0.50 | — | universe93 | не записано (на машине: universe93/b/sfx) | неизвестно | 1 |
| `sfx/ui/ui_0.mp3` | 1.04 | — | tesla | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/ui/ui_1.mp3` | 2.04 | — | tesla | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/ui/ui_glitch_04.ogg` | 0.02 | Interface Sounds: glitch_001 | — | Kenney, «Interface Sounds: glitch_001», https://kenney.nl/assets/interface-sounds | CC0 1.0 | 1 |
| `sfx/ui/ui_maximize_06.ogg` | 0.21 | Interface Sounds: maximize_003 | gta6 | Kenney, «Interface Sounds: maximize_003», https://kenney.nl/assets/interface-sounds | CC0 1.0 | 1 |
| `sfx/ui/ui_tick_05.ogg` | 0.02 | Interface Sounds: tick_002 | gta6 | Kenney, «Interface Sounds: tick_002», https://kenney.nl/assets/interface-sounds | CC0 1.0 | 1 |
| `sfx/ui/ui_tick_05__sfx_library.ogg` | 0.02 | Interface Sounds: tick_002 | gta6 | Kenney, «Interface Sounds: tick_002», https://kenney.nl/assets/interface-sounds | CC0 1.0 | 1 |
| `sfx/whoosh/pro_whoosh_big_long.wav` | 1.12 | — | lhc, moon, neutron | не записано (на машине: halluc/v2/sfx2) | неизвестно | 1 |
| `sfx/whoosh/swipe_flick.wav` | 0.57 | — | halluc, exoplanet_v7, depth2d, lhc, universe93, moon, neutron, nuke | не записано (на машине: halluc/v2/sfx2) | неизвестно | 1 |
| `sfx/whoosh/swipe_paper.wav` | 0.77 | — | halluc, exoplanet_v7, depth2d, lhc, universe93, moon, neutron, nuke | не записано (на машине: halluc/v2/sfx2) | неизвестно | 1 |
| `sfx/whoosh/w1.wav` | 0.54 | — | halluc | не записано (на машине: halluc/sfx) | неизвестно | 1 |
| `sfx/whoosh/w2.wav` | 1.06 | — | halluc | не записано (на машине: halluc/sfx) | неизвестно | 2 |
| `sfx/whoosh/w3.wav` | 0.74 | — | halluc | не записано (на машине: halluc/sfx) | неизвестно | 1 |
| `sfx/whoosh/w4.wav` | 0.48 | — | halluc | не записано (на машине: halluc/sfx) | неизвестно | 2 |
| `sfx/whoosh/whoosh.wav` | 1.40 | — | Redshift-shorts | не записано (на машине: exoplanet_explainer/proj/public) | неизвестно | 1 |
| `sfx/whoosh/whoosh_0.mp3` | 1.04 | — | tesla | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/whoosh/whoosh_0__audio.mp3` | 2.04 | — | tesla | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/whoosh/whoosh_1.mp3` | 2.04 | — | tesla | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/whoosh/whoosh_1__audio.mp3` | 1.04 | — | tesla | exoplanet (phoenix-planet) v3–v6; по каталогу — генерации ElevenLabs, промпты не сохранены | неизвестно точно | 1 |
| `sfx/whoosh/whoosh_cinematic.wav` | 2.00 | — | Redshift-shorts | Redshift-shorts/assets (sfx) | не записана | 13 |
| `sfx/whoosh/whoosh_double.wav` | 0.73 | — | Redshift-shorts | Redshift-shorts/assets (sfx) | не записана | 13 |
| `sfx/whoosh/whoosh_fast_heavy.wav` | 0.77 | — | halluc, exoplanet_v7, depth2d, lhc, universe93, moon, neutron, nuke | не записано (на машине: halluc/v2/sfx2) | неизвестно | 1 |
| `sfx/whoosh/whoosh_sharp.wav` | 1.10 | — | Redshift-shorts | Redshift-shorts/assets (sfx) | не записана | 13 |
| `sfx/whoosh/whoosh_soft.wav` | 1.10 | — | Redshift-shorts | Redshift-shorts/assets (sfx) | не записана | 13 |

## Не положено: Mixkit

Лицензия Mixkit запрещает распространять файлы как библиотеку, а этот репозиторий публичный. Эти файлы нужно скачивать заново по ссылке и класть в `/workspace/exoplanet_explainer/sfx_library/` (музыка nuke — `music/cyberpunk_04_144bpm.mp3`).

| файл | ссылка |
|---|---|
| ambient_scifi_computer_01.wav | https://assets.mixkit.co/active_storage/sfx/2507/2507.wav |
| ambient_tech_hum_02.wav | https://assets.mixkit.co/active_storage/sfx/2133/2133.wav |
| ambient_low_drone_03.wav | https://assets.mixkit.co/active_storage/sfx/2745/2745.wav |
| riser_trailer_01.wav | https://assets.mixkit.co/active_storage/sfx/790/790.wav |
| riser_synth_02.wav | https://assets.mixkit.co/active_storage/sfx/645/645.wav |
| riser_space_stutter_03.mp3 | https://assets.mixkit.co/active_storage/sfx/1144/1144-preview.mp3 |
| stinger_big_cinematic_02.mp3 | https://assets.mixkit.co/active_storage/sfx/788/788-preview.mp3 |
| stinger_quick_zoom_03.wav | https://assets.mixkit.co/active_storage/sfx/772/772.wav |
| stinger_intro_impact_01.wav | https://assets.mixkit.co/active_storage/sfx/2902/2902.wav |
| ui_small_glitch_02.wav | https://assets.mixkit.co/active_storage/sfx/2595/2595.wav |
| ui_tech_select_03.wav | https://assets.mixkit.co/active_storage/sfx/3124/3124.wav |
| ui_hightech_bleep_01.wav | https://assets.mixkit.co/active_storage/sfx/2521/2521.wav |
| whoosh_vacuum_02.wav | https://assets.mixkit.co/active_storage/sfx/1465/1465.wav |
| whoosh_windy_01.wav | https://assets.mixkit.co/active_storage/sfx/1474/1474.wav |
| whoosh_magic_sweep_03.wav | https://assets.mixkit.co/active_storage/sfx/2638/2638.wav |
| whoosh_cinematic_fast_04.wav | https://assets.mixkit.co/active_storage/sfx/1492/1492.wav |
| cyberpunk_02_99bpm.mp3 | https://assets.mixkit.co/music/140/140.mp3 |
| cyberpunk_01_144bpm.mp3 | https://assets.mixkit.co/music/141/141.mp3 |
| cyberpunk_05_136bpm.mp3 | https://assets.mixkit.co/music/464/464.mp3 |
| cyberpunk_03_123bpm.mp3 | https://assets.mixkit.co/music/395/395.mp3 |
| cyberpunk_04_144bpm.mp3 | https://assets.mixkit.co/music/117/117.mp3 |

| `sfx/bolt9/bass_hit_sub.wav` | 1.20 | саб-удар под цифры | bolt9 | синтез, `synth/synth_bolt.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/bolt9/hum_static_bed.wav` | 6.00 | статический гул-подложка | bolt9 | синтез, `synth/synth_bolt.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/bolt9/leader_step_1.wav` | 0.12 | ступенчатый лидер, шаг 1 | bolt9 | синтез, `synth/synth_bolt.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/bolt9/leader_step_2.wav` | 0.12 | ступенчатый лидер, шаг 2 | bolt9 | синтез, `synth/synth_bolt.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/bolt9/leader_step_3.wav` | 0.12 | ступенчатый лидер, шаг 3 | bolt9 | синтез, `synth/synth_bolt.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/bolt9/thunder_crack_close.wav` | 4.50 | близкий удар грома | bolt9 | синтез, `synth/synth_bolt.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/bolt9/thunder_roll_far.wav` | 5.00 | дальний раскат | bolt9 | синтез, `synth/synth_bolt.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/bolt9/zap_electric.wav` | 0.90 | электрический разряд | bolt9 | синтез, `synth/synth_bolt.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/uran9/orbit_sweep.wav` | 1.40 | свип по орбите | uran9 | синтез, `synth/synth_uran.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/uran9/party_horn_sad.wav` | 1.10 | грустная дудка-пищалка | uran9 | синтез, `synth/synth_uran.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/uran9/planet_chime.wav` | 1.60 | космический перезвон на планету | uran9 | синтез, `synth/synth_uran.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/uran9/space_drone_bed.wav` | 8.00 | космический дрон-подложка | uran9 | синтез, `synth/synth_uran.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/uran9/year_tick.wav` | 0.06 | тик счётчика лет | uran9 | синтез, `synth/synth_uran.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/hum9/air_flow.wav` | 1.60 | поток воздуха через нос | hum9 | синтез, `synth/synth_hum.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/hum9/bagpipe_sad.wav` | 1.50 | грустная сдувающаяся волынка | hum9 | синтез, `synth/synth_hum.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/hum9/cheek_squeak.wav` | 0.70 | резиновый скрип надутых щёк | hum9 | синтез, `synth/synth_hum.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/hum9/flag_flap.wav` | 0.50 | хлопок флага | hum9 | синтез, `synth/synth_hum.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/hum9/hum_choke.wav` | 3.00 | носовое «ммм», которое глохнет | hum9 | синтез, `synth/synth_hum.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/hum9/pressure_rise.wav` | 3.40 | нарастание давления | hum9 | синтез, `synth/synth_hum.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/hum9/sniff_block.wav` | 0.60 | шмыг заложенным носом | hum9 | синтез, `synth/synth_hum.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/eif9/browser_click.wav` | 0.25 | клик и загрузка страницы | eif9 | синтез, `synth/synth_eif.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/eif9/calc_beep.wav` | 0.09 | бип калькулятора | eif9 | синтез, `synth/synth_eif.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/eif9/frost_crack.wav` | 0.50 | морозный треск | eif9 | синтез, `synth/synth_eif.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/eif9/heat_shimmer.wav` | 2.00 | жаркое марево, воздушный свип | eif9 | синтез, `synth/synth_eif.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/eif9/metal_groan.wav` | 1.80 | стон нагретого металла | eif9 | синтез, `synth/synth_eif.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/eif9/rivet_ping.wav` | 1.20 | звон заклёпки | eif9 | синтез, `synth/synth_eif.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/eif9/sun_sweep.wav` | 2.40 | тёплый свип солнца по кругу | eif9 | синтез, `synth/synth_eif.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/eif10/arrow_swish.wav` | 0.60 | свист стрелки | eif10 | синтез, `synth/synth_eif10.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/eif10/glass_shatter.wav` | 1.30 | разбитое стекло, осколки | eif10 | синтез, `synth/synth_eif10.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/eif10/heartbeat_pair.wav` | 1.00 | сдвоенный удар сердца (перед твистом) | eif10 | синтез, `synth/synth_eif10.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/eif10/lean_creak.wav` | 1.60 | скрип наклоняющейся конструкции | eif10 | синтез, `synth/synth_eif10.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/eif10/tape_ratchet.wav` | 1.20 | трещотка рулетки | eif10 | синтез, `synth/synth_eif10.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/eif10/thermo_rise.wav` | 1.30 | рост столбика термометра | eif10 | синтез, `synth/synth_eif10.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/pos10/annih_flash.wav` | 1.20 | вспышка аннигиляции | pos10 | синтез, `synth/synth_pos10.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/pos10/pair_capture.wav` | 1.00 | захват электрона позитроном | pos10 | синтез, `synth/synth_pos10.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/pos10/field_hum.wav` | 1.60 | гул поля ловушки | pos10 | синтез, `synth/synth_pos10.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/pos10/electron_strip.wav` | 0.80 | срыв электрона с позитрония | pos10 | синтез, `synth/synth_pos10.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/pos10/cold_crystal.wav` | 1.60 | холодный кристальный звон | pos10 | синтез, `synth/synth_pos10.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/pos10/level_drop.wav` | 1.60 | падение на нижний уровень | pos10 | синтез, `synth/synth_pos10.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/pos10/quantum_ping.wav` | 1.20 | квантовый пинг | pos10 | синтез, `synth/synth_pos10.py` | собственный (сгенерировано кодом) | 1 |
| `sfx/pos10/stealth_slide.wav` | 1.30 | тихое скольжение (проход тайком) | pos10 | синтез, `synth/synth_pos10.py` | собственный (сгенерировано кодом) | 1 |
