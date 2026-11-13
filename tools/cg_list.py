#!/usr/bin/env python3
"""이벤트 CG 도감 목록(flow/flow_cg.csv)을 만듭니다. 이미 있는 줄(직접 쓴 제목·파일명)은 그대로 두고, 없는 칸만 채웁니다.
 구성: 메인 히로인 공통 9 + 서브 히로인 공통 9 + 메인 6명 x 8 + 서브 2명 x 4 = 74장
 (공통 칸의 route 는 COMMON_MAIN / COMMON_SUB — 도감에서 '메인 히로인 공통' / '서브 히로인 공통' 으로 표시)
 CG 파일은 cg/ 폴더에 넣고 이 CSV 의 file 칸에 파일명을 적은 뒤, 대본·flow_assets.csv 의 cg 칸에 cg_id 를 적으면 해금됩니다."""
import csv, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); p = os.path.join(ROOT, 'flow', 'flow_cg.csv')
old = list(csv.DictReader(open(p, encoding='utf-8-sig'))); fields = ['cg_id', 'title', 'route', 'file', 'note']
have = {r['cg_id']: r for r in old}
SPEC = [('COMMON_MAIN', 'main_common', '메인 히로인 공통', 9), ('COMMON_SUB', 'sub_common', '서브 히로인 공통', 9),
        ('JIWOO', 'jiwoo', '강지우', 8), ('ARIN', 'arin', '윤아린', 8), ('YUNA', 'yuna', '최유나', 8), ('SERA', 'sera', '이세라', 8), ('SEOYUN', 'seoyun', '한서윤', 8), ('HARIN', 'harin', '서하린', 8),
        ('SI', 'si', '백시은', 4), ('CH', 'ch', '강채아', 4)]
rows = []
for route, key, nm, n in SPEC:
    for i in range(1, n + 1):
        cid = f'cg_{key}_{i:02d}'
        rows.append(have.get(cid) or {'cg_id': cid, 'title': f'{nm} CG {i}', 'route': route, 'file': '', 'note': '미제작'})
ids = {r['cg_id'] for r in rows}; rows += [r for r in old if r['cg_id'] not in ids]      # 목록 밖에 직접 추가한 줄은 유지
with open(p, 'w', encoding='utf-8-sig', newline='') as fp:
    w = csv.DictWriter(fp, fieldnames=fields, lineterminator='\r\n'); w.writeheader(); w.writerows([{c: r.get(c, '') for c in fields} for r in rows])
print('CG 칸', len(rows))
