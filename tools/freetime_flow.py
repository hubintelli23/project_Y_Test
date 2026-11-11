#!/usr/bin/env python3
"""자유시간·스탯 시스템을 flow/ 의 nodes·edges 에 연결합니다. (여러 번 실행해도 같은 결과)
- 챕터 1~4 끝마다 자유시간(FT_1~4) 삽입, 공통 루트 건너뛰기는 일괄 자유시간(FT_QUICK)으로 연결
- 공통 배드엔딩 진입 조건 · 메인 피사체 선택지 잠금 · 히로인별 엔딩 선택지 조건을 스탯으로 연결
- 연결(edge)에 lock(잠금 사유 문구)·toast(진입 안내 문구) 칸이 생깁니다"""
import csv, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); F = lambda n: os.path.join(ROOT, 'flow', n)
rd = lambda p: list(csv.DictReader(open(p, encoding='utf-8-sig')))
def wr(p, rows, fields):
    with open(p, 'w', encoding='utf-8-sig', newline='') as fp:
        w = csv.DictWriter(fp, fieldnames=fields, lineterminator='\r\n'); w.writeheader(); w.writerows(rows)
nodes, edges, hero = rd(F('flow_nodes.csv')), rd(F('flow_edges.csv')), {h['id']: h for h in rd(F('flow_heroines.csv'))}
ses = {r['node_id']: r for r in rd(F('flow_freetime.csv'))}
nf, ef = list(nodes[0].keys()), list(edges[0].keys())
for c in ('lock', 'toast'):
    if c not in ef: ef.append(c)
blank = lambda fs, **kw: {**{c: '' for c in fs}, **kw}
N = {n['node_id']: n for n in nodes}
# ---- 1) 자유시간 노드 + 챕터 사이 연결
for nid, r in ses.items():
    if nid in N: nodes.remove(N[nid])
    nodes.append(blank(nf, node_id=nid, type='freetime', group='COMMON', title=r['title'], subtitle=r['subtitle'], note='자유시간 · 행동력은 flow_freetime.csv'))
N = {n['node_id']: n for n in nodes}
ft_edges = [('CH1_EP6', 'FT_1', 'CH2_EP1'), ('CH2_EP6', 'FT_2', 'CH3_EP1'), ('CH3_EP6', 'FT_3', 'CH4_EP1'), ('CH4_EP6', 'FT_4', 'CH5_EP1')]
drop = {(a, b) for a, _, b in ft_edges} | {(a, ft) for a, ft, _ in ft_edges} | {(ft, b) for _, ft, b in ft_edges} | {('FT_QUICK', 'RELATION_CHECK')}
edges = [e for e in edges if (e['from_id'], e['to_id']) not in drop]
def adde(a, b, label='', cond='', setv='', lock='', toast=''):
    edges.append(blank(ef, from_id=a, to_id=b, label=label, condition=cond, kind='next', set=setv, lock=lock, toast=toast))
for a, ft, b in ft_edges: adde(a, ft); adde(ft, b)
adde('FT_QUICK', 'RELATION_CHECK')
N['CH1_EP1']['skip_to'] = 'FT_QUICK'          # 공통 루트 건너뛰기 → 일괄 자유시간 (스탯 없이 건너뛰어 루트가 잠기는 일을 막음)
# ---- 2) 공통 배드엔딩 진입 조건 (RELATION_CHECK)
edges = [e for e in edges if e['from_id'] != 'RELATION_CHECK']
adde('RELATION_CHECK', 'COMMON_BAD', '번아웃 · 스트레스 85 이상', 'stress>=85', toast='스트레스가 한계에 달했다…')
adde('RELATION_CHECK', 'COMMON_BAD', '핵심 수집 요소 누적 미획득 4개 이상', 'stress<85 && missed_core>=4', toast='놓친 순간들이 너무 많았다…')
adde('RELATION_CHECK', 'COMMON_BAD', '개인 루트 진입 실패 (AP 소진)', 'stress<85 && missed_core<4 && pick_count==0', toast='아무와도 가까워지지 못한 채 시간이 흘렀다…')
adde('RELATION_CHECK', 'MAIN_PICK', '메인 루트 진행 조건 충족', 'stress<85 && missed_core<4 && pick_count>0')
N['RELATION_CHECK']['note'] = '공통 배드엔딩(초점이 깨진 렌즈) 조건: 스트레스≥85 / 핵심 수집 요소 누적 미획득 missed_core≥4 / 자유시간 종료 후에도 개인 루트 진입 조건 미충족. 수치는 condition 에서 조절'
# ---- 3) 메인 피사체 선택지: 스탯 미달이면 잠금 표시
MAIN = ['jiwoo', 'arin', 'yuna', 'sera', 'seoyun', 'harin']
edges = [e for e in edges if e['from_id'] != 'MAIN_PICK']
for h in MAIN:
    adde('MAIN_PICK', h.upper(), f"{hero[h]['name']} 루트", f'can_{h}', lock=hero[h]['lock_text'] + ' 필요')
# ---- 4) 히로인별 엔딩 선택지 (해피·히든은 스탯 조건, 새드·배드는 항상 선택 가능)
RULE = {   # (해피 조건, 해피 잠금문구), (히든·진 조건, 문구)
 'ARIN':   (('aff_arin>=60 && knowledge>=45', '호감도 60 · 지식 45'), ('aff_arin>=80 && knowledge>=60', '호감도 80 · 지식 60')),
 'YUNA':   (('aff_yuna>=60', '호감도 60'), ('aff_yuna>=80 && charm>=50', '호감도 80 · 매력 50')),
 'SERA':   (('aff_sera>=55 && (knowledge>=45 || charm>=45)', '호감도 55 · (지식 또는 매력 45)'), ('aff_sera>=70 && (knowledge>=50 || charm>=50) && stamina>=35', '호감도 70 · (지식 또는 매력 50) · 체력 35')),
 'SEOYUN': (('aff_seoyun>=50 && !fail_seoyun && stamina>=30', '호감도 50 · 체력 30 · 관계 경색 없음'), ('aff_seoyun>=65 && !fail_seoyun && knowledge>=40 && stamina>=35', '호감도 65 · 지식 40 · 체력 35 · 관계 경색 없음')),
 'HARIN':  (('aff_harin>=36 && h_trust>=50 && h_alert<=50 && stamina>=40', '숨겨진 조건'), ('aff_harin>=42 && h_trust>=70 && h_alert<=50 && stamina>=50 && harin_event', '숨겨진 조건 · 스토리 특수 이벤트')),
}
for r, ((hc, hl), (tc, tl)) in RULE.items():
    for e in edges:
        if e['from_id'] == r and e['to_id'] == f'{r}_H': e['condition'], e['lock'] = hc + ' && stress<70', hl + ' · 스트레스 70 미만 필요'
        if e['from_id'] == r and e['to_id'] == f'{r}_T': e['condition'], e['lock'] = tc + ' && stress<50', tl + ' · 스트레스 50 미만 필요'
for e in edges:   # 강지우: 선택지 번호 1(해피)·4(히든)
    if e['from_id'] == 'JIWOO_PICK' and e['set'] == 'jiwoo_pick=1': e['condition'], e['lock'] = 'aff_jiwoo>=40 && stress<70', '호감도 40 · 스트레스 70 미만 필요'
    if e['from_id'] == 'JIWOO_PICK' and e['set'] == 'jiwoo_pick=4': e['condition'], e['lock'] = 'aff_jiwoo>=70 && knowledge>=50 && stress<50', '호감도 70 · 지식 50 · 스트레스 50 미만 필요'
wr(F('flow_nodes.csv'), nodes, nf); wr(F('flow_edges.csv'), edges, ef)
print('nodes', len(nodes), 'edges', len(edges))
