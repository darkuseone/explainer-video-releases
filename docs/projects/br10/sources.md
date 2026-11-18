# br10: источники фото, видео и звука

## Фото (Wikimedia Commons, в ролике в кадре с подписью источника)
- `File:CERN Computer Center 04.jpg` — CC BY-SA 4.0 (кадр «сервер»).
- `File:Meyrin-CERN.jpg` — CC0 (ЦЕРН с воздуха; также картинка внутри окна Mosaic).
- `File:Tim Berners-Lee CP 2.jpg` — CC BY 2.0 (Тим Бернерс-Ли; кадрирован; также картинка внутри окна Mosaic).
- `File:Ginevra, centro visitatori del cern, primo server della storia` — CC BY 3.0 (подлинник предложения под стеклом).
- `File:First Web Server.jpg` — CC BY-SA 3.0 (первый веб-сервер NeXT; картинка внутри окна Mosaic).
- `File:Marc Andreessen-9.jpg` — CC BY 2.0.
- `File:CHM Artifacts Boxed Netscape Navigator (2273126105).jpg` — CC BY 2.0 (коробка Netscape; кадр «Netscape» и «разбитое стекло»).
Авторы указаны на страницах файлов Commons (поле Artist в `media` индексе: релиз media-br10, index.json).

## Видео
- NASA, «NHQ_2019_0626_Earth Views from the ISS» (public domain по правилам NASA) — фон кадра «жмёшь на ссылку». Взят из уже скачанного набора dim10 (пре-релиз media-dim10, nv01).
- Ролики с Commons (набор текста, светодиоды модема) скачать не удалось: Wikimedia отвечала 429 «слишком много запросов» с раннера GitHub. Заменены кадрами NASA и графикой.

## Реконструкции и графика (нарисованы кодом для ролика)
- Обложка «Information Management: A Proposal» с пометкой «Vague but exciting...» — реконструкция, не скан (подлинник в архиве ЦЕРН).
- Окна Mosaic, Internet Explorer, рабочий стол Windows 95 — стилизация, без логотипов.
- 3D (Three.js): глобус ссылок → куб NeXT с наклейкой, схема загрузки страницы (DNS → сервер → HTML → отрисовка; адрес 203.0.113.7 — документационный диапазон TEST-NET-3), объёмная диаграмма доли Chrome.
- График IPO Netscape: точки $28 (размещение), $75 (пик), $58,25 (закрытие) по Wikipedia «Netscape»; форма линии внутри дня схематичная.

## Голос, аватар, звук
- ElevenLabs eleven_v4, голос NIKITA, 1 дубль, 1039 кредитов. Паузы сжаты в тишине, темп 1,07 (rubberband).
- HeyGen Avatar V, look 54172d7a5b2946ed8a592dee955fb0c7, один клип 11,6 с (начало + конец), 9 кредитов (414 → 405).
- Музыка: `audio/music/CuIAqvgYvYSIBrRdLAub.mp3` (библиотека, ElevenLabs, Tesla), склейка через 6 тактов назад, брейк трека попадает на «И знаешь, что смешно?».
- SFX из `audio/sfx/` (whoosh, impact, bolt9, nuk10, eif10, warm, ui, riser). Звук модема синтезирован кодом в `mix.py`.

## Шрифты
- Unbounded и Caveat (OFL, Google Fonts через npm @expo-google-fonts), JetBrains Mono (репо), Liberation Sans/Serif (системные) — ретро-окна.
