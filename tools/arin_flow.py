#!/usr/bin/env python3
"""윤아린 루트 대본(story/project_y_arin_route.csv)을 순서도(flow_nodes·flow_edges)에 연결합니다. (여러 번 실행해도 같은 결과)
 ARIN → 챕터 1~7 에피소드 → ARIN_PICK(선택지 4) → ARIN_END_ROUTE → 해피/새드/배드/히든 엔딩 → 각 에필로그 → 공통 에필로그
 선택지 번호(arin_pick): 1 해피 · 2 새드 · 3 배드 · 4 히든·진   (조건·잠금 문구는 freetime_flow.py 가 입힙니다)
 후일담 DLC 노드(ARIN_DLC)는 이미 있고, 대본은 story/project_y_arin_dlc.csv (chapter_id=arin_dlc)"""
import csv, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); F = lambda n: os.path.join(ROOT, 'flow', n)
rd = lambda p: list(csv.DictReader(open(p, encoding='utf-8-sig')))
def wr(p, rows, fields):
    with open(p, 'w', encoding='utf-8-sig', newline='') as fp:
        w = csv.DictWriter(fp, fieldnames=fields, lineterminator='\r\n'); w.writeheader(); w.writerows(rows)
nodes, edges = rd(F('flow_nodes.csv')), rd(F('flow_edges.csv')); nf, ef = list(nodes[0].keys()), list(edges[0].keys())
blank = lambda fs, **kw: {**{c: '' for c in fs}, **kw}
story = rd(os.path.join(ROOT, 'story', 'project_y_arin_route.csv'))
eps = collections.OrderedDict(); ctitle = {}; etitle = {}
for r in story:
    eps.setdefault(r['chapter_id'], set()).add(int(r['episode_no'])); ctitle[r['chapter_id']] = r['chapter_title']; etitle[(r['chapter_id'], int(r['episode_no']))] = r['episode_title']
AGE = {1: 20, 2: 21, 3: 22, 4: 23, 5: 24, 6: 25, 7: 26}
# 기존 아린 노드/연결 정리 (플레이스홀더 포함)
drop_n = {n['node_id'] for n in nodes if n['node_id'].startswith('ARIN_') and n['node_id'] != 'ARIN_DLC'}
nodes = [n for n in nodes if n['node_id'] not in drop_n]
edges = [e for e in edges if not (e['from_id'].startswith('ARIN') and e['from_id'] != 'ARIN_DLC') and not (e['to_id'].startswith('ARIN_') and e['to_id'] != 'ARIN_DLC')]
for n in nodes:
    if n['node_id'] == 'ARIN': n['note'] = '윤아린 루트 · 챕터 1~7 → 선택의 순간 → 엔딩 4종 → 에필로그'
def addn(**kw): nodes.append(blank(nf, **kw))
def adde(a, b, label='', cond='', setv=''): edges.append(blank(ef, from_id=a, to_id=b, label=label, condition=cond, kind='next', set=setv))
prev = 'ARIN'
for c in range(1, 8):
    cid = f'arin_ch{c}'
    for k in sorted(eps[cid]):
        nid = f'ARIN_C{c}_EP{k}'
        addn(node_id=nid, type='scene', group='ROUTE', route='ARIN', title=f'챕터 {c} · {ctitle[cid]}', subtitle=f'{etitle[(cid, k)]} · 현우 {AGE[c]}세', age=str(AGE[c]), script_id=f'ARIN_CH{c}_EP{k}')
        adde(prev, nid); prev = nid
addn(node_id='ARIN_PICK', type='choice', group='ROUTE', route='ARIN', title='선택의 순간'); adde(prev, 'ARIN_PICK')
addn(node_id='ARIN_END_ROUTE', type='check', group='ROUTE', route='ARIN', title='윤아린 엔딩 분기', note='ARIN_PICK 에서 고른 번호(arin_pick)로 엔딩이 갈립니다: 1 해피 · 2 새드 · 3 배드 · 4 히든·진')
choices = [r['text'] for r in story if r['type'] == 'choice']
assert len(choices) == 4
for i, t in enumerate(choices, 1): adde('ARIN_PICK', 'ARIN_END_ROUTE', t, setv=f'arin_pick={i}')
KIND = {'h': ('happy', '해피 엔딩'), 's': ('sad', '새드 엔딩'), 'b': ('bad', '배드 엔딩'), 't': ('true', '히든·진 엔딩')}
for i, k in enumerate('hsbt', 1):
    e, nm = KIND[k]
    addn(node_id=f'ARIN_{k.upper()}', type='ending', group='ENDING', route='ARIN', ending=e, title=nm, subtitle=ctitle[f'arin_{k}'], script_id=f'ARIN_{k.upper()}')
    addn(node_id=f'ARIN_{k.upper()}_EPI', type='epilogue', group='ENDING', route='ARIN', ending=e, title=nm + ' 에필로그', subtitle=ctitle[f'arin_{k}_epi'], script_id=f'ARIN_{k.upper()}_EPI')
    adde('ARIN_END_ROUTE', f'ARIN_{k.upper()}', cond=f'arin_pick=={i}'); adde(f'ARIN_{k.upper()}', f'ARIN_{k.upper()}_EPI'); adde(f'ARIN_{k.upper()}_EPI', 'COMMON_EPILOGUE')
wr(F('flow_nodes.csv'), nodes, nf); wr(F('flow_edges.csv'), edges, ef)
print('아린 노드', sum(1 for n in nodes if n['node_id'].startswith('ARIN')), '/ 전체 nodes', len(nodes), 'edges', len(edges))
