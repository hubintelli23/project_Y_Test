#!/usr/bin/env python3
"""flow/flow_assets.csv 의 bgm 칸을 장소·장면 규칙으로 다시 채웁니다. (bg·char·cg·set 칸은 건드리지 않습니다)
- 공통/서브 루트: 에피소드 기본곡 유지 + 동아리방 → bgm_club, 카페 → bgm_cafe (재회 곡이 깔린 에피소드는 그대로) + 히로인 이름이 제목에 나오는 에피소드는 해당 테마곡
- 강지우 루트: 챕터 기본곡 theme_jiwoo (챕터 7·엔딩 공통 사건은 bgm_reunion) + 장면 장소별 곡(해바라기밭·작업실·집·유치원·전시관·사무실·해안가·노을 거리·웨딩·동아리·카페)
  + 엔딩/에필로그는 엔딩 곡(wedding / end_sad / end_bad / end_true) 이 장소보다 우선
- 강지우 과거 회상(jiwoo_fb*): 대본 파일이 없어 각 에피소드 첫 줄(…_ep#_0001)에만 지정
사용: python3 tools/apply_bgm.py        ※ flow_assets.csv 에서 bgm 칸을 직접 고친 뒤에는 다시 돌리지 마세요(덮어씁니다)."""
import csv, json, re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rd = lambda p: list(csv.DictReader(open(p, encoding='utf-8-sig')))
meta = json.load(open(os.path.join(ROOT, 'tools', 'jiwoo_meta.json'), encoding='utf-8'))
path = os.path.join(ROOT, 'flow', 'flow_assets.csv')
rows = rd(path); fields = list(rows[0].keys())
mp3 = lambda n: n + '.mp3'
# ---------- 공통/서브 루트 ----------
THEME_EP = {'ch1_ep3': 'theme_jiwoo', 'ch5_ep2': 'theme_jiwoo', 'ch3_ep2': 'theme_arin', 'ch5_ep4': 'theme_arin', 'ch5_ep3': 'theme_yuna'}   # 제목에 히로인 이름이 나오는 에피소드
STRONG = {'bgm_reunion.mp3', 'theme_jiwoo.mp3', 'theme_arin.mp3', 'theme_yuna.mp3'}
LOC_BY_BG = {'bg_club_room.webp': 'bgm_club.mp3', 'bg_cafe.webp': 'bgm_cafe.mp3'}
base = ''
for r in rows:
    if r['node_id'].startswith('jiwoo_'): continue
    ep = re.match(r'^(.+_ep\d+)', r['node_id']).group(1)
    if r['bgm']:                                           # 에피소드 첫 줄: 기본곡 갱신 (원래 칸의 값)
        base = mp3(THEME_EP[ep]) if ep in THEME_EP and r['node_id'].endswith('_0001') else r['bgm']
    r['bgm'] = base if base in STRONG else (LOC_BY_BG.get(r['bg']) or base)
# ---------- 강지우 루트 ----------
BASE = {'jiwoo_ch7': 'bgm_reunion', 'jiwoo_end': 'bgm_reunion'}
ENDING = {'jiwoo_h': 'bgm_wedding', 'jiwoo_h_epi': 'bgm_wedding', 'jiwoo_s': 'bgm_end_sad', 'jiwoo_s_epi': 'bgm_end_sad',
          'jiwoo_b': 'bgm_end_bad', 'jiwoo_b_epi': 'bgm_end_bad', 'jiwoo_t': 'bgm_end_true', 'jiwoo_t_epi': 'bgm_end_true'}
LOC = [('해바라기밭', 'bgm_sunflower'), ('웨딩홀|결혼식장|예식장|신부 대기실|신랑 대기실', 'bgm_wedding'), ('작업 공간|작업실', 'bgm_studio'),
       ('지우의 집|두 사람의 집|현우의 집|침실|거실|주방', 'bgm_home_warm'), ('유치원', 'bgm_kindergarten'), ('전시관|전시회장|전시', 'bgm_exhibition'),
       ('NEXTFRAME|사무실|본사', 'bgm_office'), ('해안가|차량', 'bgm_road_coast'), ('동아리|AFOCA', 'bgm_club'), ('카페|서점', 'bgm_cafe')]
EVE = r'저녁|해 질|해질|노을'
def loc_bgm(loc):
    for pat, b in LOC:
        if re.search(pat, loc): return b
    if re.search(r'거리|주택가|귀갓길|헤어지는 길|벤치|약속 장소|쉼터', loc) and re.search(EVE, loc): return 'bgm_street_evening'
    return ''
def chapter_base(ch):
    return BASE.get(ch, 'theme_jiwoo')
order = {}
for f in ('project_y_jiwoo_route.csv', 'project_y_jiwoo_dlc.csv'):
    for r in rd(os.path.join(ROOT, 'story', f)): order[r['node_id']] = (len(order), r['chapter_id'])
jw = {r['node_id']: r for r in rows if r['node_id'].startswith('jiwoo_') and not r['node_id'].startswith('jiwoo_fb')}
scenes = {s[0]: s[1] for s in meta['scenes']}
firsts = {e['first']: e['chapter_id'] for e in meta['eps']}
# 모든 에피소드 첫 줄 + 장면 첫 줄을 후보로, 곡이 바뀌는 지점에만 지정
cands = sorted(set(firsts) | set(scenes), key=lambda k: order.get(k, (10**9,))[0])
prev = ''
for nid in cands:
    ch = order[nid][1]
    want = ENDING.get(ch) or loc_bgm(scenes.get(nid, '')) or (chapter_base(ch) if nid in firsts else '')
    if nid in firsts and not (ENDING.get(ch) or loc_bgm(scenes.get(nid, ''))): want = chapter_base(ch)
    if not want:                                           # 장소 규칙에 안 걸린 장면: 이전 장소곡에서 기본곡으로 복귀
        want = ENDING.get(ch) or chapter_base(ch)
    if want != prev or nid in firsts:
        if nid not in jw: jw[nid] = dict(node_id=nid, bg='', char='', bgm='', cg='', set=''); rows.append(jw[nid])
        jw[nid]['bgm'] = mp3(want)
        prev = want
# ---------- 과거 회상 (대본 파일이 없어 첫 줄만) ----------
FB = {1: 'bgm_flashback_school', 2: 'bgm_flashback_school', 3: 'bgm_flashback_secret', 4: 'bgm_flashback_rooftop'}
have = {r['node_id']: r for r in rows}
for n, b in FB.items():
    for e in (1, 2, 3):
        nid = f'jiwoo_fb{n}_ep{e}_0001'
        if nid not in have: rows.append(dict(node_id=nid, bg='', char='', bgm='', cg='', set='')); have[nid] = rows[-1]
        have[nid]['bgm'] = mp3(b)
# 순서 정리: 공통/서브 → 강지우(대본 순서) → 회상
def key(r):
    n = r['node_id']
    if n.startswith('jiwoo_fb'): return (2, n)
    if n in order: return (1, order[n][0])
    return (0, 0)
base_rows = [r for r in rows if key(r)[0] == 0]; rest = sorted([r for r in rows if key(r)[0] != 0], key=key)
rows = base_rows + rest
with open(path, 'w', encoding='utf-8-sig', newline='') as fp:
    w = csv.DictWriter(fp, fieldnames=fields, lineterminator='\r\n'); w.writeheader(); w.writerows(rows)
import collections
used = collections.Counter(r['bgm'] for r in rows if r['bgm'])
missing = [b for b in used if not os.path.exists(os.path.join(ROOT, 'bgm', b))]
print('rows', len(rows)); print(used.most_common()); print('파일 없는 곡:', missing)
