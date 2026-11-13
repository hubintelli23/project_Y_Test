#!/usr/bin/env python3
"""윤아린 루트 원고(txt, hwp2txt.py 로 추출) -> story/project_y_arin_route.csv, story/project_y_arin_dlc.csv
사용: python3 tools/arin_txt_to_csv.py <원고폴더>   (폴더 안: ch1..ch7.txt, ending.txt, epilogue.txt, dlc.txt)
 chapter_id : arin_ch1~7 / arin_h·s·b·t (엔딩) / arin_h_epi·s_epi·b_epi·t_epi (에필로그) / arin_dlc (후일담)
 episode_no : 각 chapter_id 안에서 1부터"""
import re, csv, sys, os, json, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPK = {'이현우':'lee_hyeonu','강지우':'kang_jiwoo','서하린':'seo_harin','최유나':'choi_yuna','윤아린':'yoon_arin','한서윤':'han_seoyun','이세라':'lee_sera',
       '백시은':'baek_sieun','강채아':'kang_chaea','민경훈':'min_gyeonghun','강이현':'kang_ihyeon','신태석':'shin_taeseok','차성재':'cha_seongjae'}
FIELDS = ['chapter_id','chapter_title','episode_no','episode_title','node_id','type','speaker','speaker_id','text','break_before','branch','route']
clean = lambda s: re.sub(r'[\u0000-\u0008\u000b-\u001f�]', '', s).strip()
strip_q = lambda s: re.sub(r'[“”"‘’]+$', '', re.sub(r'^[“”"‘’]+', '', s.strip())).strip()
RE_DLG = re.compile(r'^([^:：“”"\[\(]{1,12}?)\s*(?:\((독백|속마음|메시지)\))?\s*[:：]\s*(.+)$')
RE_EP = re.compile(r'^에피소드\s*(\d+)\s*[.—–-]\s*(.*)$')
RE_MARK = re.compile(r'^\[(장면 전환|회상 장면|장면|장소|회상|현재로 전환|현재)\s*[:：]\s*(.*)\]$')
RE_END = re.compile(r'^\[(에피소드\s*\d+\s*종료|[Cc]hapter\s*\d+\s*종료|.*(엔딩|에필로그|DLC).*종료|.*엔딩\s*[–-]\s*종료)\]$')
RE_CHOICE_S, RE_CHOICE_E = re.compile(r'^\[선택지\]$'), re.compile(r'^\[선택지 종료\]$')
SPEAKERS_OK = set(SPK) | {'외부 관계자','후배','할머니','할아버지','여성','남성','사회자','참가자','관람객','작품 설명','백서현','강도윤','아이'}

def convert(lines, cid, ctitle, rows, ep_start=1, ep_by_header=True):
    """lines : 이미 정리된 줄들. 'ep' 는 chapter_id 안에서 1부터."""
    ep, n, brk, cho, epname = 0, 0, True, None, ''
    for l in lines:
        if not l: continue
        m = RE_EP.match(l)
        if m: ep += 1; epname = m.group(2).strip(); n = 0; brk = True; continue
        if not ep or RE_END.match(l): continue
        if RE_CHOICE_S.match(l): cho = 0; continue
        if RE_CHOICE_E.match(l): cho = None; continue
        if cho is not None:
            cho += 1; n += 1
            rows.append(dict(chapter_id=cid, chapter_title=ctitle, episode_no=ep, episode_title=epname, node_id=f'{cid}_ep{ep}_choice{cho}', type='choice', speaker='', speaker_id='',
                             text=strip_q(re.sub(r'^\d+\.\s*', '', l)), break_before='', branch='', route='')); continue
        m = RE_MARK.match(l)
        if m:
            n += 1; rows.append(dict(chapter_id=cid, chapter_title=ctitle, episode_no=ep, episode_title=epname, node_id=f'{cid}_ep{ep}_{n:04d}', type='scene', speaker='', speaker_id='',
                                     text=m.group(2).strip(), break_before='', branch='', route='')); brk = True; continue
        n += 1
        d = RE_DLG.match(l)
        if d and d.group(1).strip() in SPEAKERS_OK:
            sp, tag, body = d.group(1).strip(), d.group(2), d.group(3).strip()
            t = 'message' if tag == '메시지' else 'dialogue'; text = strip_q(body)
            if re.match(r'^\[(.+)\]$', text) and t == 'dialogue': t, text = 'message', text[1:-1].strip()
        else: t, sp, text = 'narration', '', l
        if t == 'narration' and re.match(r'^\[폴더명\s*[:：]\s*(.+)\]$', l): t, text = 'system', l      # 화면에 뜨는 폴더명 등
        rows.append(dict(chapter_id=cid, chapter_title=ctitle, episode_no=ep, episode_title=epname, node_id=f'{cid}_ep{ep}_{n:04d}', type=t, speaker=sp, speaker_id=SPK.get(sp, ''),
                         text=text, break_before='TRUE' if brk else '', branch='', route=''))
        brk = False
    return ep

def load(p): return [clean(l) for l in open(p, encoding='utf-8', errors='replace').read().split('\n')]
def title_of(l):   # '챕터 1 — 0.8m, 낯선 거리…' / 'Chapter 6 — … (25세)' -> '0.8m, …'
    t = re.split(r'\s*[—–]\s*|\.\s+', l, maxsplit=1)[-1]; return re.sub(r'\s*\(\d+세\)\s*$', '', t).strip()

def main(d):
    route, dlc, meta = [], [], {'eps': [], 'scenes': [], 'choices': []}
    for i in range(1, 8):
        L = load(os.path.join(d, f'ch{i}.txt')); head = next(l for l in L if re.match(r'^(챕터|[Cc]hapter)\s*\d+', l))
        ep = convert(L[L.index(head)+1:], f'arin_ch{i}', title_of(head), route); meta['eps'].append((f'arin_ch{i}', title_of(head), ep))
    # 엔딩 / 에필로그: '1. 해피엔딩 — 제목' 단위로 나눔
    for fn, ids, suffix in (('ending.txt', ('h','s','b','t'), ''), ('epilogue.txt', ('h','s','b','t'), '_epi')):
        L = load(os.path.join(d, fn)); blocks, cur = [], None
        for l in L:
            m = re.match(r'^(\d)\.\s*(해피|새드|배드|히든 트루)\s*(엔딩|에필로그)\s*[—–-]\s*(.*)$', l)
            if m: cur = [m.group(4).strip(), []]; blocks.append(cur); continue
            if cur is not None: cur[1].append(l)
        assert len(blocks) == 4, (fn, len(blocks))
        for k, (title, body) in zip(ids, blocks):
            cid = f'arin_{k}{suffix}'; ep = convert(body, cid, title, route); meta['eps'].append((cid, title, ep))
    L = load(os.path.join(d, 'dlc.txt')); body = [l for l in L if l]
    ep = convert(body, 'arin_dlc', '후일담 · on & off', dlc); meta['eps'].append(('arin_dlc', '후일담 · on & off', ep))
    for fn, rows in (('project_y_arin_route.csv', route), ('project_y_arin_dlc.csv', dlc)):
        with open(os.path.join(ROOT, 'story', fn), 'w', encoding='utf-8-sig', newline='') as fp:
            w = csv.DictWriter(fp, fieldnames=FIELDS, lineterminator='\r\n'); w.writeheader(); w.writerows(rows)
        print(fn, len(rows), dict(collections.Counter(r['type'] for r in rows)))
    for r in route + dlc:
        if r['type'] == 'scene' and r['node_id'].endswith('_0001') is False: pass
    for c, t, e in meta['eps']: print(c, '|', t, '|', e, 'ep')
if __name__ == '__main__': main(sys.argv[1])
