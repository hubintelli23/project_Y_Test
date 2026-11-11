#!/usr/bin/env python3
"""flow/*.csv 를 index.html 의 EMBED(내장 대체본)에 다시 넣습니다. flow 파일을 고친 뒤 실행하세요. (서버에서 CSV 를 못 읽을 때만 쓰이는 비상용 사본)"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = {'nodes':'flow_nodes.csv','edges':'flow_edges.csv','scripts':'flow_scripts.csv','routes':'flow_routes.csv','cg':'flow_cg.csv','assets':'flow_assets.csv',
         'stats':'flow_stats.csv','actions':'flow_actions.csv','heroines':'flow_heroines.csv','freetime':'flow_freetime.csv','items':'flow_items.csv'}
emb = {k: open(os.path.join(ROOT, 'flow', f), encoding='utf-8-sig').read().replace('\r\n', '\n') for k, f in FILES.items()}
p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
a = s.index('const EMBED = {'); b = s.index('\n};\n', a) + 4
s = s[:a] + 'const EMBED = ' + json.dumps(emb, ensure_ascii=False, indent=1) + ';\n' + s[b:]
open(p, 'w', encoding='utf-8').write(s); print('EMBED 갱신:', ', '.join(FILES))
