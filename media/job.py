# br10 job 3: fetch the HeyGen avatar clip (hook + ending).
import sys, os, urllib.request
out=sys.argv[1]; os.makedirs(out,exist_ok=True)
U='https://files2.heygen.ai/aws_pacific/avatar_tmp/5ea17ba885e746c1a2967bb87a775601/dc31cea50e3e0f6f5881131db7551052.mp4?Expires=1795637892&Signature=AJ1L11khj7CFAMxA3RazynR3BowJnIDNT4N5gCTGg3WryRypIROix6p5IRx3ChviUxO9~zGIpqewioyS3hAFnwcltfeYcaLn1spAYbss-ajWtycwbu2SBx5yoyGP0Ovd-UOumh1MeMefpE-OunZfRN-S5ZePdPy8417ykEThG2Hnb3BawiDqrFhedJDZqmGHBMT4cdxCwu659Zl1vl0xUFNR8TLHMBBpJZ4Xlt1OcNqwG1UjZnu30xMY8kBcnVSJxfzhNK2bacYcdTa6kqUXSaej~WNlpYxcMjh3Nv-FY16MRuNodBLNOJ0qRwzitT2y7at~LUYXBkz43lA9eDr1Kg__&Key-Pair-Id=K3TSZ3KU01LY58'
with urllib.request.urlopen(urllib.request.Request(U,headers={'User-Agent':'Mozilla/5.0'}),timeout=300) as r: open(os.path.join(out,'avatar_br10.mp4'),'wb').write(r.read())
