#!/usr/bin/env python3
"""story/*.csv 를 읽어 flow/flow_assets.csv (배경·BGM 지정표) 초안을 만듭니다.
- 에피소드(또는 분기) 첫 줄에 배경/BGM 을 지정하고, 지문에 장소 단어가 나오면 그 줄에서 배경을 바꿉니다.
- 결과는 '초안'입니다. flow_assets.csv 를 열어 node_id 줄의 bg / bgm / char / cg 칸을 자유롭게 고치세요.
- 직접 고친 뒤에는 이 스크립트를 다시 돌리지 마세요(덮어씁니다).  사용: python3 tools/build_assets.py
"""
import csv, re, glob, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG = {  # 장소 단어 -> img/ 파일 (먼저 맞는 규칙이 우선)
 'bg_noticeboard.webp': r'게시판|공고|포스터',
 'bg_playground_dusk.webp': r'운동장|트랙',
 'bg_club_room.webp': r'동아리실|동아리 방',
 'bg_lecture_hall.webp': r'강의실|강의동|교수님',
 'bg_campus_plaza.webp': r'광장|분수대',
 'bg_garden.webp': r'정원|화단|온실',
 'bg_cafe.webp': r'카페|아포카|커피 향|테이블',
 'bg_room.webp': r'자취방|내 방|방 안|침대|방에 돌아|방으로 돌아',
 'bg_street_dusk.webp': r'노을|해 질|해질|저녁 거리|골목|퇴근길',
 'bg_hall_wood.webp': r'복도|로비|계단',
 'bg_cherry_road.webp': r'벚꽃길|벚나무|벚꽃 잎|벚꽃이|벚꽃 아래|꽃잎이',
 'bg_campus_path.webp': r'산책로|캠퍼스 길|교정|도서관 앞|도서관 뒤',
}
BGM_DAILY, BGM_CAFE, BGM_REUNION = 'bgm_prologue_daily.mp3', 'bgm_cafe.mp3', 'bgm_reunion.mp3'
def bgm_for(ch, ep):
    k = (ch, ep)
    if k in {('prologue','5'),('ch2','5'),('ch2','6'),('ch3','5'),('ch3','6'),('ch5','6'),('subprologue','2'),('ch8','3')}: return BGM_REUNION
    if ch in ('subprologue','ch6','ch7','ch8') or k in {('ch4','3'),('ch4','4'),('ch4','5')}: return BGM_CAFE
    return BGM_DAILY
def detect(text):
    for f, pat in BG.items():
        if re.search(pat, text): return f
    return ''
rows = []
for f in sorted(glob.glob(os.path.join(ROOT,'story','*.csv'))):
    rows += list(csv.DictReader(open(f, encoding='utf-8-sig')))
groups = collections.OrderedDict()
for r in rows:
    groups.setdefault((r['chapter_id'], r['episode_no'], r['branch']), []).append(r)
out, cur_bg, main_state = [], 'bg_cherry_road.webp', {}
for (ch, ep, br), rs in groups.items():
    if br and (ch, ep) in main_state: cur_bg = main_state[(ch, ep)]
    bgm = bgm_for(ch, ep)
    first_hint = ''
    for r in rs[:10]:
        if r['type'] == 'narration': first_hint = first_hint or detect(r['text'])
    bg = first_hint or cur_bg
    cur_bg = bg
    out.append({'node_id': rs[0]['node_id'], 'bg': bg, 'char': '', 'bgm': bgm, 'cg': '', 'set': ''})
    last_change = 0
    for i, r in enumerate(rs[1:], 1):
        if r['type'] != 'narration' or i - last_change < 8: continue
        d = detect(r['text'])
        if d and d != cur_bg:
            cur_bg = d; last_change = i
            out.append({'node_id': r['node_id'], 'bg': d, 'char': '', 'bgm': '', 'cg': '', 'set': ''})
    if not br: main_state[(ch, ep)] = cur_bg
path = os.path.join(ROOT, 'flow', 'flow_assets.csv')
with open(path, 'w', encoding='utf-8-sig', newline='') as fp:
    w = csv.DictWriter(fp, fieldnames=['node_id','bg','char','bgm','cg','set']); w.writeheader(); w.writerows(out)
print('wrote', path, len(out), 'rows;', collections.Counter(o['bg'] for o in out if o['bg']).most_common())
