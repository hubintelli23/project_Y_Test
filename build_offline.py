#!/usr/bin/env python3
"""index.html + flow/*.csv + story/*.csv 를 합쳐 index_offline.html 한 파일을 만듭니다.
웹 서버 없이 파일로 바로 열 때(휴대폰 파일 앱 등) 스토리가 안 불러와지는 문제를 피하는 용도입니다.
이미지/BGM 은 img/ chars/ bgm/ 폴더를 같은 위치에 두면 그대로 나옵니다.  사용: python3 tools/build_offline.py"""
import os, glob, json
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html = open(os.path.join(R, 'index.html'), encoding='utf-8').read()
story = {}
for f in sorted(glob.glob(os.path.join(R, 'story', '*.csv'))):
    story['story/' + os.path.basename(f)] = open(f, encoding='utf-8-sig').read()
tag = '/* STORY_EMBED */\nconst STORY_EMBED = ' + json.dumps(story, ensure_ascii=False) + ';\n'
html = html.replace('const EMBED = ', tag + 'const EMBED = ', 1)
open(os.path.join(R, 'index_offline.html'), 'w', encoding='utf-8').write(html)
print('wrote index_offline.html', round(len(html) / 1e6, 2), 'MB')
