F="[1]volume=-29.9dB[b];[0]asplit[v][sc];[b][sc]sidechaincompress=threshold=0.03:ratio=3:attack=20:release=350[bd];[v][bd][2]amix=inputs=3:normalize=0,pan=stereo|c0=c0|c1=c0[m]"
ffmpeg -v error -y -i audio/vo59.wav -i audio/bed.wav -i $1 -filter_complex "$F" -map "[m]" -c:a pcm_f32le /tmp/pre.wav
I=$(ffmpeg -i /tmp/pre.wav -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | awk '{print $2}')
G=$(python3 -c "print(-13.85-($I))")
ffmpeg -v error -y -i /tmp/pre.wav -af "volume=${G}dB,alimiter=limit=0.84:level=false:attack=3:release=60" -c:a pcm_s16le $2
echo pre $I gain $G
