#!/usr/bin/env python3
"""윤아린 루트 장면(tools/arin_scenes.json: 장소→배경·BGM 배정)을 flow/flow_assets.csv 에 연결합니다. (여러 번 실행해도 같은 결과)
 대본의 '장면' 줄(scene)에 순서대로 맞춰 bg·bgm 을 적고, 에피소드 첫 장면은 항상 적습니다. 빈 칸=이전 유지."""
import csv, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALIAS = {'bg_exhibition_hall': 'bg_exhibition', 'bg_lounge_night': 'bg_lounge_dusk'}   # 아직 없는 이미지는 비슷한 배경으로 대체
scenes = json.load(open(os.path.join(ROOT, 'tools', 'arin_scenes.json'), encoding='utf-8'))
rows = []
for f in ('project_y_arin_route', 'project_y_arin_dlc'):
    rows += [r for r in csv.DictReader(open(os.path.join(ROOT, 'story', f + '.csv'), encoding='utf-8-sig')) if r['type'] == 'scene']
p = os.path.join(ROOT, 'flow', 'flow_assets.csv')
old = list(csv.DictReader(open(p, encoding='utf-8-sig'))); fields = list(old[0].keys())
old = [r for r in old if not r['node_id'].startswith('arin_')]
import collections
cs = collections.OrderedDict(); js = collections.OrderedDict()
for r in rows: cs.setdefault(r['node_id'].rsplit('_', 1)[0], []).append(r)
for x in scenes: js.setdefault((x['chapter'], x['ep']), []).append(x)
assert len(cs) == len(js)
pairs = []                                   # (대본 장면 줄, 배정표 장면)
for (ep, rs), ss in zip(cs.items(), js.values()):
    if len(rs) == len(ss): pairs += list(zip(rs, ss))                 # 장면 수가 같으면 순서대로
    else:                                                              # 다르면 장소 이름으로 맞추고, 못 맞춘 보조 장면은 건너뜀
        k = 0
        for r in rs:
            if k < len(ss) and ss[k]['place'] in r['text']: pairs.append((r, ss[k])); k += 1
        assert k == len(ss), ep
out = []; lastbg = lastbgm = None; lastep = None
for r, s in pairs:
    ep = r['node_id'].rsplit('_', 1)[0]
    bg = ALIAS.get(s['bgfile'], s['bgfile']) + '.webp'; bgm = s['bgm'] + '.mp3'
    first = ep != lastep; lastep = ep
    out.append({'node_id': r['node_id'], 'bg': bg if (first or bg != lastbg) else '', 'bgm': bgm if (first or bgm != lastbgm) else '', 'char': '', 'cg': '', 'set': ''})
    lastbg, lastbgm = bg, bgm
with open(p, 'w', encoding='utf-8-sig', newline='') as fp:
    w = csv.DictWriter(fp, fieldnames=fields, lineterminator='\r\n'); w.writeheader()
    w.writerows(old + [{c: o.get(c, '') for c in fields} for o in out])
print('아린 장면 cue', len(out), '/ assets 전체', len(old) + len(out))
