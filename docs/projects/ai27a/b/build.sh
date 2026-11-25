#!/bin/bash
# ai27a full build: render (4 procs) -> concat -> mix -> 2-pass H.264 10 Mbit/s -> ../ai27a.mp4
set -e; cd "$(dirname "$0")"
NF=$(python3 -c "import json;print(3+int(round(json.load(open('timeline.json'))['tot']*25)))")
mkdir -p parts; rm -f parts/*.mkv; Q=$(( (NF+3)/4 ))
for k in 0 1 2 3; do python3 r.py $((k*Q)) $(((k+1)*Q)) parts/p$k.mkv & done; wait
printf "file 'p0.mkv'\nfile 'p1.mkv'\nfile 'p2.mkv'\nfile 'p3.mkv'\n" > parts/list.txt
ffmpeg -v error -y -f concat -safe 0 -i parts/list.txt -c copy parts/master.mkv
python3 mix.py
cd parts
ffmpeg -v error -y -i master.mkv -c:v libx264 -preset slow -profile:v high -pix_fmt yuv420p -g 50 -b:v 10M -maxrate 15M -bufsize 20M -pass 1 -an -f null /dev/null
ffmpeg -v error -y -i master.mkv -c:v libx264 -preset slow -profile:v high -pix_fmt yuv420p -g 50 -b:v 10M -maxrate 15M -bufsize 20M -pass 2 -an v.mp4
ffmpeg -v error -y -i v.mp4 -i ../mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart ../../ai27a.mp4
ffprobe -v error -show_entries format=duration,bit_rate -of csv=p=0 ../../ai27a.mp4
