#!/usr/bin/env python3
"""공통 배드엔딩 원고(txt, hwp2txt.py 로 추출) -> story/project_y_bad_main.csv, project_y_bad_sub.csv
사용: python3 tools/badend_txt_to_csv.py <main.txt> <sub.txt>
 main : 초점이 깨진 렌즈 (chapter_id=common_bad_main)   sub : 프레임 밖의 우리 (chapter_id=common_bad_sub)
 에피소드 번호는 챕터와 상관없이 1부터 이어서 매깁니다 (노드 하나가 순서대로 이어 재생하기 때문)"""
import re, csv, sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPK = {'이현우':'lee_hyeonu','강지우':'kang_jiwoo','서하린':'seo_harin','최유나':'choi_yuna','윤아린':'yoon_arin','한서윤':'han_seoyun','이세라':'lee_sera',
       '백시은':'baek_sieun','강채아':'kang_chaea','민경훈':'min_gyeonghun'}
NAMES = '|'.join(sorted(SPK, key=len, reverse=True))
RE_DLG = re.compile(r'^(%s)\s*(?:\((?:독백|속마음)\))?\s*[:：]\s*(.+)$' % NAMES)
RE_CH = re.compile(r'^Chapter\s*(\d+)\.\s*(.*)$'); RE_EP = re.compile(r'^에피소드\s*(\d+)\.\s*(.*)$')
RE_SCENE_NO = re.compile(r'^장면\s*\d+\.')
RE_MARK = re.compile(r'^\[(장면|장면 전환|회상 장면|회상|회상 종료|현재로 전환|현재 장면|마지막 장면)\s*[:：]?\s*(.*)\]$')
RE_END = re.compile(r'^\[(에피소드 \d+ 종료|Chapter \d+ 종료|.*엔딩\s*[-–—].*)\]$')
clean = lambda s: re.sub(r'[\u0000-\u0008\u000b-\u001f�]', '', s).strip()
strip_q = lambda s: re.sub(r'[“”"‘’]+$', '', re.sub(r'^[“”"‘’]+', '', s.strip())).strip()
FIELDS = ['chapter_id','chapter_title','episode_no','episode_title','node_id','type','speaker','speaker_id','text','break_before','branch','route']
def convert(path, cid, title_mark):
    L = [clean(l) for l in open(path, encoding='utf-8', errors='replace').read().split('\n')]
    rows, scenes, chtitle, ep, n, brk, last = [], [], '', 0, 0, True, None
    for l in L[1:]:
        if not l: continue
        if title_mark and re.match(title_mark, l): continue
        m = RE_CH.match(l)
        if m: chtitle = m.group(2).strip(); continue
        m = RE_EP.match(l)
        if m: ep += 1; epname = m.group(2).strip(); n = 0; brk = True; continue
        if RE_SCENE_NO.match(l) or l == 'Us Beyond the Frame': continue
        if RE_END.match(l): continue
        m = RE_MARK.match(l)
        if m:
            kind = m.group(1)
            if kind == '회상 종료': brk = True; continue
            if ep: scenes.append((f'{cid}_ep{ep}_{n+1:04d}', f'{kind}: {m.group(2)}', ep)); brk = True
            continue
        if not ep: continue
        n += 1
        d = RE_DLG.match(l)
        if d:
            body = d.group(2).strip(); mm = re.match(r'^\[(.+)\]$', body)
            t, text = ('message', mm.group(1).strip()) if mm else ('dialogue', strip_q(body)); sp = d.group(1)
        else: t, sp, text = 'narration', '', l
        rows.append(dict(chapter_id=cid, chapter_title=chtitle, episode_no=ep, episode_title=epname, node_id=f'{cid}_ep{ep}_{n:04d}', type=t, speaker=sp,
                         speaker_id=SPK.get(sp, ''), text=text, break_before='TRUE' if brk else '', branch='', route=''))
        brk = False
    return rows, scenes
out = {}
for key, path, cid, tm in (('main', sys.argv[1], 'common_bad_main', r'^(.*딩 – 초점|초점이 깨진)'), ('sub', sys.argv[2], 'common_bad_sub', r'^(인 2인|.*프레임 밖의 우리$)')):
    rows, scenes = convert(path, cid, tm)
    with open(os.path.join(ROOT, 'story', f'project_y_bad_{key}.csv'), 'w', encoding='utf-8-sig', newline='') as fp:
        w = csv.DictWriter(fp, fieldnames=FIELDS, lineterminator='\r\n'); w.writeheader(); w.writerows(rows)
    out[key] = scenes
    import collections
    print(key, len(rows), 'rows', dict(collections.Counter(r['type'] for r in rows)), 'episodes', sorted({(r['episode_no'], r['chapter_title'], r['episode_title']) for r in rows}))
json.dump(out, open(os.path.join(ROOT, 'tools', 'badend_scenes.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
