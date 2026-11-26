# usage: python3 prep_av.py av.mp4  -> b/av/fNNNN.jpg (25 fps) + avatar block in timeline.json
import sys,json,subprocess,os,glob
B=os.path.dirname(os.path.abspath(__file__)); src=sys.argv[1]; lag=float(sys.argv[2]) if len(sys.argv)>2 else 0.0
os.makedirs(B+'/av',exist_ok=True)
for f in glob.glob(B+'/av/*.jpg'): os.remove(f)
subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-vf','fps=25,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920','-q:v','2',B+'/av/f%04d.jpg'],check=True)
n=len(glob.glob(B+'/av/*.jpg'))
tl=json.load(open(B+'/timeline.json')); segs=json.load(open(B+'/../v/av_meta.json'))
tl['avatar']={'segs':segs,'n':n,'lag':lag}; json.dump(tl,open(B+'/timeline.json','w'),ensure_ascii=False)
print('frames',n,'segs',segs)
