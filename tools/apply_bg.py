#!/usr/bin/env python3
"""새 배경 이미지(Bg1) → img/*.webp 변환 + flow/flow_assets.csv 의 bg 칸 재배정.
- 대상: 강지우 루트(jiwoo_*) 와 공통 배드엔딩(common_bad_*) 의 장면 장소·시간대 (tools/jiwoo_meta.json / badend_scenes.json)
- 새 이미지에 맞는 장소가 없으면 기존 배경을 그대로 둡니다. 공통 루트(prologue~ch8)는 장소 정보가 없어 건드리지 않습니다.
사용: python3 tools/apply_bg.py [원본폴더]   (원본폴더 기본: ../bg_in/Bg1)  ※ apply_bgm.py · badend_flow.py 다음에 실행하세요."""
import csv, json, os, re, sys
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', '..', 'bg_in', 'Bg1')
# 파일명(한글) → 배포용 영문 이름
NAMES = {
 '지하문서보관함':'archive_basement','넥스트프레임 외관':'nextframe_outside','해질녁옥상':'rooftop_dusk','동네공원오후':'park_afternoon',
 '해질녁작은쉼터':'shelter_dusk','중학교교실낮':'mid_class_day','해바라기밤':'sunflower_night','지우집 저녁':'jiwoo_home_eve',
 '넥스트프레임본사내부':'nextframe_inside','저녁거실':'living_eve','운동장점심':'ground_noon','실내예식장낮':'wedding_hall',
 '마감후카페밤':'cafe_night','방과후옥상':'rooftop_after','해바라기오후':'sunflower_day','신부대기실':'bride_room',
 '거리벤치오후늦게':'street_bench','중학교교실노을':'mid_class_dusk','고등학교오후':'high_afternoon','사진 전시회장 오전_오후':'exhibition',
 '점심학생식당':'student_cafeteria','고등학교정문':'high_gate','유리온실':'glass_greenhouse','해안가휴계공간오후늦게':'coast_rest',
 '정문오후저녁무렵':'univ_gate','작업실밤':'studio_night','인근서점':'bookstore','해안가도로오후늦게':'coast_road',
 '해바라기 해질녘':'sunflower_dusk','유치원앞':'kinder_front','고등학교오전':'high_morning','유치원활동실':'kinder_room',
 '급식실점심':'school_lunch','고등학교교실오전':'high_class','동네거리오전':'town_street','대학가식당':'campus_diner',
 '계단창고오후':'stair_storage','고등학교가을':'high_autumn','야외정원오전':'outdoor_garden','오전침실':'bedroom_morning',
 '차량오후':'car_afternoon','밤 주방':'kitchen_night','작업실낯':'studio_day'}
def convert():
    img = os.path.join(ROOT, 'img'); n = 0
    for f in sorted(os.listdir(SRC)):
        k = os.path.splitext(f)[0]
        if k not in NAMES: print('이름표 없음:', f); continue
        im = Image.open(os.path.join(SRC, f)).convert('RGB')
        if im.width > 1280: im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
        im.save(os.path.join(img, f'bg_{NAMES[k]}.webp'), 'WEBP', quality=82, method=6); n += 1
    print('변환', n, '장')
W = lambda k: f'bg_{k}.webp'
def pick(loc):
    """'장면: 장소 / 시간' 문자열 → 새 배경 파일명 (없으면 '')"""
    L = loc.split(':', 1)[-1] if not loc.startswith('장면 전환') and not loc.startswith('장면 1') else loc.split(':', 1)[-1]
    place, _, tm = L.partition('/'); full = L
    night = bool(re.search(r'밤|새벽|오전 3시', full)); dusk = bool(re.search(r'저녁|해 질|해질|해가 기울|노을', full))
    morning = bool(re.search(r'오전|아침', full))
    if re.search(r'신부 대기실', full): return W('bride_room')
    if re.search(r'신랑 대기실', full): return W('bride_room')
    if re.search(r'유리 온실', full): return W('glass_greenhouse')
    if re.search(r'실내 예식장|결혼식장', full): return W('wedding_hall')
    if re.search(r'야외 정원', full): return W('outdoor_garden')
    if re.search(r'전시회장|전시관', full): return W('exhibition')
    if re.search(r'NEXTFRAME 본사|NEXTFRAME 사무실', full): return W('nextframe_inside')
    if re.search(r'유치원 활동실', full): return W('kinder_room')
    if re.search(r'유치원 앞', full): return W('kinder_front')
    if re.search(r'인근 서점', full): return W('bookstore')
    if re.search(r'학생식당', full): return W('student_cafeteria')
    if re.search(r'정문', full): return W('univ_gate')
    if re.search(r'차량 내부', full): return W('car_afternoon')
    if re.search(r'해바라기', full): return W('sunflower_night') if night else W('sunflower_dusk') if dusk else W('sunflower_day')
    if re.search(r'동네 공원', full): return W('park_afternoon')
    if re.search(r'동네 거리', full): return W('town_street')
    if re.search(r'침실', full): return W('bedroom_morning')
    if re.search(r'주방', full): return W('kitchen_night')
    if re.search(r'거실', full): return W('living_eve')
    if re.search(r'지우의 집', full): return W('jiwoo_home_eve')
    if re.search(r'두 사람의 집', full): return W('living_eve')
    if re.search(r'작업 공간|작업실', full): return W('studio_night') if (night or dusk) else W('studio_day')
    if re.search(r'작은 쉼터|인근 쉼터', full): return W('shelter_dusk') if dusk else W('street_bench')
    if re.search(r'카페 뷰파인더', full) and night: return W('cafe_night')
    return ''
def pick_fb(loc):   # 강지우 과거 회상(중·고등학교) 장소 → 배경
    hs = '고등학교' in loc or loc.startswith(('점심시간 / 교실', '방과 후 / 교실'))
    dusk = bool(re.search(r'저녁|해 질|노을', loc))
    if '지하 문서' in loc: return W('archive_basement')
    if '계단 창고' in loc: return W('stair_storage')
    if '옥상' in loc: return W('rooftop_dusk') if dusk else W('rooftop_after')
    if '급식실' in loc: return W('school_lunch')
    if '운동장' in loc: return W('ground_noon')
    if '정문' in loc: return W('high_gate')
    if '교실' in loc: return W('high_class') if hs else (W('mid_class_dusk') if dusk else W('mid_class_day'))
    if loc.startswith('서운고등학교 /') or loc.startswith('서운고등학교 / '): return W('high_afternoon')
    if loc.startswith('서운고등학교'): return W('high_autumn') if '가을' in loc else W('high_afternoon')
    return ''
def apply_fb(rows, fields):
    p = os.path.join(ROOT, 'story', 'project_y_jiwoo_flashback.csv')
    if not os.path.exists(p): return 0
    st = list(csv.DictReader(open(p, encoding='utf-8-sig'))); by = {r['node_id']: r for r in rows}; n = 0; cur = ''; ep = None
    for r in st:
        key = (r['chapter_id'], r['episode_no'])
        if key != ep:   # 에피소드 첫 줄: 앞 장면이 없으면 학교 기본 배경
            ep = key; cur = ''
            if r['type'] != 'scene' or not pick_fb(r['text']):
                b = W('mid_class_day') if r['chapter_id'] in ('jiwoo_fb1', 'jiwoo_fb2') else W('high_class')
                a = by.setdefault(r['node_id'], dict.fromkeys(fields, '') | {'node_id': r['node_id']}); a['bg'] = b; cur = b; n += 1
        if r['type'] == 'scene':
            b = pick_fb(r['text'])
            if b and b != cur:
                a = by.get(r['node_id']) or (dict.fromkeys(fields, '') | {'node_id': r['node_id']}); a['bg'] = b; by[r['node_id']] = a; cur = b; n += 1
    ids = {x['node_id'] for x in rows}; rows.extend(v for k, v in by.items() if k not in ids)
    return n
def main():
    convert()
    meta = json.load(open(os.path.join(ROOT, 'tools', 'jiwoo_meta.json'), encoding='utf-8'))
    bad = json.load(open(os.path.join(ROOT, 'tools', 'badend_scenes.json'), encoding='utf-8'))
    locs = {}
    for nid, loc, *_ in meta['scenes']: locs[nid] = loc
    for k in bad:
        for nid, loc, *_ in bad[k]: locs.setdefault(nid, loc)
    path = os.path.join(ROOT, 'flow', 'flow_assets.csv')
    rows = list(csv.DictReader(open(path, encoding='utf-8-sig'))); fields = list(rows[0].keys()); ch = 0; used = {}
    for r in rows:
        loc = locs.get(r['node_id'])
        if not loc or not r['bg']: continue
        b = pick(loc)
        if b and b != r['bg']: r['bg'] = b; ch += 1; used[b] = used.get(b, 0) + 1
    fb = apply_fb(rows, fields); print('과거 회상 배경 지정', fb, '곳')
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    print('배경 교체', ch, '곳'); [print(' ', k, v) for k, v in sorted(used.items())]
    allbg = {os.path.basename(f) for f in os.listdir(os.path.join(ROOT, 'img'))}
    never = sorted(f for f in allbg if f.startswith('bg_') and f not in {r['bg'] for r in rows})
    print('아직 쓰이지 않는 배경:', ', '.join(never))
if __name__ == '__main__': main()
