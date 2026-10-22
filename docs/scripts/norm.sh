n=$1
ffmpeg -i pre.wav -af loudnorm=I=-13.8:TP=-1.2:LRA=9:print_format=json -f null - 2>&1 > /dev/null | cat > ln.raw 2>&1
ffmpeg -i pre.wav -af loudnorm=I=-13.8:TP=-1.2:LRA=9:print_format=json -f null - 2>ln.raw
v(){ grep "\"$1\"" ln.raw | sed 's/.*: "\(.*\)".*/\1/'; }
ffmpeg -v error -y -i pre.wav -af "loudnorm=I=-13.8:TP=-1.2:LRA=9:measured_I=$(v input_i):measured_TP=$(v input_tp):measured_LRA=$(v input_lra):measured_thresh=$(v input_thresh):offset=$(v target_offset):linear=true" -ar 48000 vo.wav
