# br10 job 7: publish the finished video + publish text as GitHub release "br10".
import subprocess, shutil, os, sys
out=sys.argv[1]; os.makedirs(out,exist_ok=True)
subprocess.run('gh release view br10 >/dev/null 2>&1 || gh release create br10 --title "Весь веб в одном компьютере (br10)" --notes "Shorts 56,6 с: как работает браузер и откуда он взялся. Ролик и текст для публикации."',shell=True,check=True)
subprocess.run(['gh','release','upload','br10','media/brauzer-br10.mp4','media/brauzer-br10_publish.txt','--clobber'],check=True)
