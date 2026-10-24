# dna10: источники и проверка фактов

| Утверждение в ролике | Источник | Примечание |
|---|---|---|
| 4 буквы А, Т, Г, Ц; 2 бита на букву | Базовая информатика: log2(4)=2 | — |
| ~3 млрд букв, ~750 МБ | Nurk et al., Science 2022 (T2T-CHM13, 3,055 Гб); 3·10⁹ × 2 бит / 8 = 750 МБ | гаплоидный геном |
| «Меньше, чем игра на телефоне» | многие мобильные игры занимают 2+ ГБ | на экране: «многие мобильные игры весят 2+ ГБ» |
| Код читается тройками, 64 комбинации, 1 «старт» (ATG/AUG), 3 «стоп» (TAA, TAG, TGA) | Стандартный генетический код, NCBI Genetic Codes table 1 | — |
| Рибосома — «процессор» | метафора: рибосома транслирует мРНК в белок | метафора |
| Белки кодирует ~1,5% | NHGRI, ENCODE / Lander et al. 2001 | — |
| Совпадение с любым человеком 99,9% | NHGRI Genetics Fact Sheet | по однонуклеотидной идентичности |
| Ошибки копирования = баги, клетка чинит | Kunkel, JBC 2004 «DNA replication fidelity» (~10⁻⁹–10⁻¹⁰ на основание после репарации) | цифра вырезана из ролика ради длины |
| Нет программиста, писала эволюция; не двоичный; триллионы клеток одновременно | общепринято; «триллионы» вместо «30 трлн», т.к. большинство клеток — эритроциты без ядра | — |

## Сокращение дубля
Дубль eleven_v4 вышел 71,5 с. Из него по паузам вырезаны два предложения целиком (без перегенерации):
«Остальное — переключатели, настройки и старые копии.» и «Клетка сама их чинит, и остаётся примерно одна ошибка на миллиард букв.»
Затем rubberband -T 1.05 и выравнивание пауз: итог 57,49 с.

## Футаж (Pexels License)
- 34862899 1080x1920 Nicola Narracci https://www.pexels.com/video/abstract-blue-dna-strand-animation-34862899/
- 34862096 1080x1920 Nicola Narracci https://www.pexels.com/video/vibrant-spinning-dna-helix-animation-34862096/
- 6804121 2732x1440 cottonbro studio https://www.pexels.com/video/running-codes-on-a-computer-6804121/
- 7989667 1080x1920 Mikhail Nilov https://www.pexels.com/video/a-man-typing-on-the-laptop-7989667/
- 12893579 1080x1920 Mizuno K https://www.pexels.com/video/hands-typing-on-laptop-keyboard-12893579/
- 35460855 1080x1920 Nicola Narracci https://www.pexels.com/video/abstract-blue-and-purple-cells-under-microscope-35460855/
- 7047796 1080x1920 Tima Miroshnichenko https://www.pexels.com/video/video-of-a-man-playing-on-cellphone-7047796/
- 31767898 1920x1080 Dominik Zítka https://www.pexels.com/video/scientist-using-pipette-in-laboratory-setting-31767898/
- 4122942 1920x1080 Shrijana Shrestha https://www.pexels.com/video/people-walking-at-a-street-during-nighttime-4122942/
- 7140928 3840x2160 MrColo https://www.pexels.com/video/close-up-of-a-cpu-7140928/
- 9837848 1920x1080 TSGLY HA https://www.pexels.com/video/close-up-on-whirling-dna-strand-9837848/
- 30162924 1920x1080 Nicola Narracci https://www.pexels.com/video/green-binary-code-looping-animation-30162924/

## Аудио
- Голос: ElevenLabs eleven_v4, NIKITA (7fU3YUxRrVGjNaZ5dzEH), один дубль.
- Аватар: HeyGen Avatar V, look 54172d7a5b2946ed8a592dee955fb0c7, один клип 6,6 с (video_id 6f58f7dbe675766352122cdd0893b177).
- SFX: earshot kit (preset crisp), список в audio/cues.json. Музыкальная подложка: собственный синтез numpy (audio/bed_dna10.wav), −19 дБ под голосом.
