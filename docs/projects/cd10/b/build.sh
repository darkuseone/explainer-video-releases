#!/bin/bash
# Полная сборка cd10. Запуск из docs/projects/cd10/b:  ./build.sh /path/to/av.mp4
set -e
cd "$(dirname "$0")"
python3 prep_av.py "$1"
NF=$(python3 -c "import json;print(3+int(round(json.load(open('timeline.json'))['tot']*25)))")
mkdir -p parts; rm -f parts/*.mkv
Q=$(( (NF+3)/4 ))
for k in 0 1 2 3; do a=$((k*Q)); b=$(( (k+1)*Q )); python3 r.py r $a $b parts/p$k.mkv & done; wait
printf "file 'p0.mkv'\nfile 'p1.mkv'\nfile 'p2.mkv'\nfile 'p3.mkv'\n" > parts/list.txt
ffmpeg -v error -y -f concat -safe 0 -i parts/list.txt -c copy parts/v.mkv
python3 mix.py
ffmpeg -v error -y -i parts/v.mkv -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart ../kod-cd10.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 ../kod-cd10.mp4
