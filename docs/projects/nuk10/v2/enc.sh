b=$1; M=/workspace/nuk10/out/master.mkv
ffmpeg -v error -y -i $M -c:v libx264 -preset slow -profile:v high -pix_fmt yuv420p -b:v ${b}k -maxrate $((b*3/2))k -bufsize $((b*2))k -g 50 -pass 1 -passlogfile p$b -an -f null /dev/null
ffmpeg -v error -y -i $M -c:v libx264 -preset slow -profile:v high -pix_fmt yuv420p -b:v ${b}k -maxrate $((b*3/2))k -bufsize $((b*2))k -g 50 -pass 2 -passlogfile p$b -an v$b.mp4
F=/workspace/tools/ffmpeg-7.0.2-amd64-static/ffmpeg
$F -v error -i v$b.mp4 -i $M -lavfi "[0:v]setpts=PTS-STARTPTS,format=yuv420p[d];[1:v]setpts=PTS-STARTPTS,format=yuv420p[r];[d][r]libvmaf=n_threads=4:log_fmt=json:log_path=vmaf$b.json" -f null - 
python3 -c "
import json;d=json.load(open('vmaf$b.json'));p=d['pooled_metrics']['vmaf'];import numpy as np;v=[f['metrics']['vmaf'] for f in d['frames']]
print('$b',round(p['mean'],2),'min',round(p['min'],2),'p1',round(float(np.percentile(v,1)),2),'harm',round(p['harmonic_mean'],2))" > res$b.txt
