#!/usr/bin/env python3
"""공통 배드엔딩 2종(메인: 초점이 깨진 렌즈 / 서브: 프레임 밖의 우리)을 flow/ 에 연결합니다. (여러 번 실행해도 같은 결과 · freetime_flow.py 다음에 실행)
- 메인: COMMON_BAD 가 story/project_y_bad_main.csv 를 재생 (기존 자리표시 장면 CB21·CB_REL·CB_BREAK·CB26 은 원고로 대체되어 삭제)
- 서브: 서브 루트 끝(CH8_EP3)에 서브 자유시간(FT_SUB)과 판정(SUB_CHECK)을 넣고, 스트레스 85 이상 / 개인 루트 진입 실패 시 COMMON_BAD_SUB
- 현재 진행 중인 그룹은 REPLAY_CHOICE 의 set 칸(grp_sub=0/1)으로 기록 → 스트레스 85 즉시 배드엔딩도 그룹에 맞는 쪽으로 갑니다
- 데이터: flow_stats(스탯·서브 호감도) / flow_heroines(group 칸) / flow_freetime(group 칸) / flow_actions(휴식 -35)"""
import csv, json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); F = lambda n: os.path.join(ROOT, 'flow', n)
rd = lambda p: list(csv.DictReader(open(p, encoding='utf-8-sig')))
def wr(p, rows, fields):
    with open(p, 'w', encoding='utf-8-sig', newline='') as fp:
        w = csv.DictWriter(fp, fieldnames=fields, lineterminator='\r\n'); w.writeheader(); w.writerows(rows)
def load(n):
    r = rd(F(n)); return r, list(r[0].keys())
blank = lambda fs, **kw: {**{c: '' for c in fs}, **kw}
# ---------- 스탯 / 행동 / 히로인 / 자유시간 ----------
stats, sf = load('flow_stats.csv')
for r in stats:
    if r['id'] == 'stress': r['start'] = '20'                                   # 초기 스트레스 20
for sid, lab in (('aff_si', '백시은 호감도'), ('aff_ch', '강채아 호감도')):
    if not any(r['id'] == sid for r in stats): stats.append(blank(sf, id=sid, label=lab, group='aff', start=0, min=0, max=100, hidden=''))
wr(F('flow_stats.csv'), stats, sf)
act, af = load('flow_actions.csv')
for r in act:
    if r['id'] == 'rest': r['effects'] = 'stress-35;fatigue-25'                 # 휴식: 스트레스 -35
wr(F('flow_actions.csv'), act, af)
hero, hf = load('flow_heroines.csv')
if 'group' not in hf: hf.append('group')
for r in hero: r.setdefault('group', 'main'); r['group'] = r['group'] or 'main'
hero = [r for r in hero if r['id'] not in ('si', 'ch')]
hero.append(blank(hf, id='si', name='백시은', aff_var='aff_si', difficulty='서브', mult=1.0, variance=0, decay=0, crash_stress=0, fixed_gain=0, trust_gain=0, alert_gain=0, alert_decay=0,
                  likes='cafe:1.4;park:1.0;library:0.9', unlock='aff_si>=20', lock_text='호감도 20 이상', group='sub'))
hero.append(blank(hf, id='ch', name='강채아', aff_var='aff_ch', difficulty='서브', mult=1.0, variance=0, decay=0, crash_stress=0, fixed_gain=0, trust_gain=0, alert_gain=0, alert_decay=0,
                  likes='park:1.3;cinema:1.1;cafe:1.0', unlock='aff_ch>=20', lock_text='호감도 20 이상', group='sub'))
wr(F('flow_heroines.csv'), hero, hf)
ft, ff = load('flow_freetime.csv')
if 'group' not in ff: ff.append('group')
for r in ft: r['group'] = r.get('group') or 'main'
ft = [r for r in ft if r['node_id'] != 'FT_SUB']
ft.append(blank(ff, node_id='FT_SUB', ap=6, title='자유시간 · 서브', subtitle='서브 히로인 루트 진입 전', group='sub'))
wr(F('flow_freetime.csv'), ft, ff)
# ---------- 순서도 ----------
nodes, nf = load('flow_nodes.csv'); edges, ef = load('flow_edges.csv')
DROP = {'CB21', 'CB_REL', 'CB_BREAK', 'CB26', 'FT_SUB', 'SUB_CHECK', 'COMMON_BAD_SUB'}
nodes = [n for n in nodes if n['node_id'] not in DROP]
edges = [e for e in edges if not (e['from_id'] in DROP or e['to_id'] in DROP or e['from_id'] == 'COMMON_BAD' or e['from_id'] == 'SUB_PICK' and False)]
N = {n['node_id']: n for n in nodes}
N['COMMON_BAD'].update(title='초점이 깨진 렌즈 (Out of Focus)', subtitle='메인 히로인 공통 배드 엔딩', script_id='COMMON_BAD_MAIN',
                       note='진입: 스트레스 85 이상(즉시) / 핵심 수집 요소 미획득 4개 이상 / 자유시간 종료 후 개인 루트 진입 실패')
nodes.append(blank(nf, node_id='COMMON_BAD_SUB', type='ending', group='COMMON_BAD', ending='bad', title='프레임 밖의 우리 (Us Beyond the Frame)', subtitle='서브 히로인 공통 배드 엔딩',
                   script_id='COMMON_BAD_SUB', note='진입: 스트레스 85 이상(즉시) / 서브 자유시간 종료 후 개인 루트 진입 실패'))
nodes.append(blank(nf, node_id='FT_SUB', type='freetime', group='COMMON', title='자유시간 · 서브', subtitle='서브 히로인 루트 진입 전', note='자유시간 · 행동력은 flow_freetime.csv'))
nodes.append(blank(nf, node_id='SUB_CHECK', type='check', group='COMMON', title='서브 루트 진입 판정',
                   note='스트레스 85 이상 또는 자유시간 종료 후에도 백시은·강채아 루트 진입 조건 미충족이면 공통 배드엔딩(프레임 밖의 우리)'))
def adde(a, b, label='', cond='', setv='', lock='', toast=''):
    edges.append(blank(ef, from_id=a, to_id=b, label=label, condition=cond, kind='next', set=setv, lock=lock, toast=toast))
adde('COMMON_BAD', 'CB_END'); adde('COMMON_BAD_SUB', 'CB_END')
# 회차 경로: 그룹 기록
for e in edges:
    if e['from_id'] == 'REPLAY_CHOICE' and e['to_id'] == 'CH1_EP1': e['set'] = 'grp_sub=0'
    if e['from_id'] == 'REPLAY_CHOICE' and e['to_id'] == 'SUBPROLOGUE_EP1': e['set'] = 'grp_sub=1'
# 서브 루트 끝: 자유시간 → 판정 → 선택
edges = [e for e in edges if not (e['from_id'] == 'CH8_EP3' and e['to_id'] == 'SUB_PICK')]
adde('CH8_EP3', 'FT_SUB'); adde('FT_SUB', 'SUB_CHECK')
adde('SUB_CHECK', 'COMMON_BAD_SUB', '번아웃 · 스트레스 85 이상', 'stress>=85', toast='스트레스가 한계에 달했다…')
adde('SUB_CHECK', 'COMMON_BAD_SUB', '개인 루트 진입 실패 (AP 소진)', 'stress<85 && pick_count==0', toast='누구의 곁에도 남지 못한 채 시간이 흘렀다…')
adde('SUB_CHECK', 'SUB_PICK', '서브 루트 진행 조건 충족', 'stress<85 && pick_count>0')
for e in edges:
    if e['from_id'] == 'SUB_PICK' and e['to_id'] == 'SI_START': e['condition'], e['lock'] = 'can_si', '호감도 20 이상 필요'
    if e['from_id'] == 'SUB_PICK' and e['to_id'] == 'CH_START': e['condition'], e['lock'] = 'can_ch', '호감도 20 이상 필요'
wr(F('flow_nodes.csv'), nodes, nf); wr(F('flow_edges.csv'), edges, ef)
# ---------- 배경·BGM ----------
sc = json.load(open(os.path.join(ROOT, 'tools', 'badend_scenes.json'), encoding='utf-8'))
assets, asf = load('flow_assets.csv')
assets = [a for a in assets if not a['node_id'].startswith(('common_bad_main', 'common_bad_sub'))]
def bg_for(loc):
    L = loc.split(':', 1)[-1]; dusk = bool(re.search(r'저녁|해 질|해질|해가 기울|노을', L))
    if re.search(r'반지하|자취방|이현우의 방|방\b', L): return 'bg_room.webp'
    if re.search(r'동아리|AFOCA|암실|사진 실습', L): return 'bg_club_room.webp'
    if re.search(r'카페|뷰파인더', L): return 'bg_cafe.webp'
    if re.search(r'공사 현장', L): return 'bg_campus_plaza.webp'
    if re.search(r'캠퍼스|벤치|산책로', L): return 'bg_street_dusk.webp' if dusk else 'bg_campus_path.webp'
    return ''
BGM = {'main': 'bgm_end_bad.mp3', 'sub': 'bgm_end_sad.mp3'}
for key, cid in (('main', 'common_bad_main'), ('sub', 'common_bad_sub')):
    rows = list(csv.DictReader(open(os.path.join(ROOT, 'story', f'project_y_bad_{key}.csv'), encoding='utf-8-sig')))
    first = rows[0]['node_id']; cues = {first: dict(bgm=BGM[key])}; cur = ''
    for nid, loc, ep in sc[key]:
        b = bg_for(loc); bgm = ''
        if key == 'sub': bgm = 'bgm_flashback_school.mp3' if loc.startswith('회상:') else BGM['sub']
        if b and b != cur or nid == first or bgm: cues.setdefault(nid, {}).update(({'bg': b} if b and b != cur else {}), **({'bgm': bgm} if bgm else {}))
        if b: cur = b
    order = {r['node_id']: i for i, r in enumerate(rows)}
    last_bgm = ''
    for nid in sorted(cues, key=lambda k: order.get(k, 10**9)):
        c = cues[nid]; bgm = c.get('bgm', '')
        if bgm == last_bgm and nid != first: bgm = ''
        if bgm: last_bgm = bgm
        assets.append(blank(asf, node_id=nid, bg=c.get('bg', ''), bgm=bgm))
wr(F('flow_assets.csv'), assets, asf)
print('nodes', len(nodes), 'edges', len(edges), 'assets', len(assets))
