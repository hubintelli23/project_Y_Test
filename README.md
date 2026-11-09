# 우리들의 시간 · Project Y — 수정본 사용법

## 폴더 구조
- index.html : 게임 본체 (flow/ · story/ · img/ · chars/ · bgm/ · cg/ 를 읽음)
- index_offline.html : 서버 없이 파일로 열 때 쓰는 단일 파일판 (tools/build_offline.py 로 생성)
- flow/ : 순서도 CSV (nodes, edges, scripts, routes, cg, assets)
- story/ : 스토리 대본 CSV
- tools/ : build_assets.py(배경·BGM 초안 생성), build_offline.py(오프라인판 생성)

## 조작 · 단축키
- 오토: 화면 버튼 또는 A 키 / 대기 시간은 설정 > '오토 대기 시간' (0.5~15초)
- 스킵: 버튼 또는 S 키 (기본은 읽은 문장만, 설정에서 변경)
- 테스트 모드: ` (백틱) 또는 F2 / 휴대폰은 타이틀 글자 3연타 / 켜지면 좌하단에 배지 표시

## 후일담 DLC
- 각 히로인의 히든·진 엔딩(XXX_T)을 끝까지 플레이해 장면을 빠져나가면 XXX_T_done 플래그가 저장되어 해금됩니다.
- DLC 대본: story/project_y_<루트소문자>_dlc.csv (예: project_y_jiwoo_dlc.csv), chapter_id 를 jiwoo_dlc 로, episode_no 를 1,2,3… 로 쓰면 자동 연결됩니다.

## 배경 · BGM · CG 지정
- flow/flow_assets.csv 의 node_id 줄에 bg(img/ 파일), bgm(bgm/ 파일), char(chars/ 파일, - 는 숨김), cg(cg_id), set 을 적습니다. 비워 두면 이전 상태 유지.
- 현재 파일은 build_assets.py 가 만든 초안입니다. 직접 고친 뒤에는 build_assets.py 를 다시 돌리지 마세요.
- CG: cg/ 폴더에 이미지 → flow/flow_cg.csv 등록 → flow_assets.csv 의 cg 칸에 cg_id.

## 스토리 파일 규칙
- 에피소드 하나 = chapter_id + episode_no (+ branch) → script_id (예: ch8 / 3 / A → CH8_EP3_A)
- 루트 대본 추가 시 story/project_y_<jiwoo|arin|yuna|sera|seoyun|harin|si|ch>_route.csv 로 저장

## 강지우 루트 (원고 → CSV)
- story/project_y_jiwoo_route.csv : 챕터 1~7 + 선택의 갈림길 + 엔딩 공통 사건 + 해피/새드/배드/히든 엔딩 + 각 엔딩 에필로그
- story/project_y_jiwoo_dlc.csv : 후일담 DLC (EP1~3)
- 흐름: JIWOO → 챕터1~7 → 선택(JIWOO_PICK) → 엔딩 공통 사건 → 엔딩 분기 → 엔딩 → 엔딩 에필로그 → 공통 에필로그
- 선택지 → 엔딩 연결(임시): 1 해피 · 2 새드 · 3 배드 · 4 히든·진. 바꾸려면 flow_edges.csv 의 JIWOO_END_ROUTE 줄 condition(jiwoo_pick==N) 수정
- 후일담 DLC 는 히든 엔딩 에필로그(JIWOO_T_EPI)까지 끝내면 해금
- 연결에 쓴 도구: tools/hwp2txt.py(HWP→텍스트), tools/jiwoo_txt_to_csv.py(텍스트→CSV), tools/jiwoo_flow.py(순서도·배경 지정표 연결)
- flow_edges.csv 에 set 칸이 생겼습니다: 선택지를 고르면 변수를 기록합니다 (예: jiwoo_pick=4)

## 자유시간 · 스탯 시스템
- 챕터 1 ~ 4 끝마다 자유시간(FT_1 ~ 4)이 열립니다. 행동력 6 · 운동/공부/외모 관리/데이트/휴식 (공통 루트 건너뛰기를 쓰면 FT_QUICK 에서 행동력 24를 한 번에 배분)
- 데이터(숫자는 모두 CSV에서 조절): flow_stats.csv(스탯 정의·초기값) / flow_actions.csv(행동 효과·데이트 장소) / flow_heroines.csv(난이도 보정·루트 진입 조건) / flow_freetime.csv(세션별 행동력)
- 호감도 보정: 지우 ×1.2, 아린·유나 ×1.0, 세라 ×0.8 + 연락 안 하면 감쇠 + 대화 조건, 서윤 ×0.6 + 변동폭 극대화 + 스트레스 60 이상 데이트 시 결정적 실수(관계 경색), 하린 고정 폭 + 숨겨진 신용/경계
- 공통 배드엔딩(COMMON_BAD) 진입: 스트레스 ≥ 80 / 루트 선택 가능한 히로인 0명 / 회피(avoid) ≥ 3  → flow_edges.csv 의 RELATION_CHECK 줄 condition 에서 수정
- 메인 피사체 선택(MAIN_PICK)과 각 루트의 엔딩 선택지는 스탯이 모자라면 잠금 사유와 함께 흐리게 표시됩니다 (테스트 모드에서는 모두 선택 가능). 새드·배드는 항상 선택 가능
- 서하린 히든 엔딩에는 스토리 특수 이벤트가 필요합니다: 원고의 장면 줄 set 칸이나 선택지 edge 의 set 칸에 harin_event=1 을 적으면 충족됩니다
- 스탯 확인: 게임 화면 '스탯' 버튼 / 도구: tools/freetime_flow.py (순서도 연결), tools/embed_flow.py (flow CSV → index.html 내장본 갱신)

## BGM (bgm/ 폴더)
- 곡 28개: 타이틀·일상·카페·재회(기존) + 동아리, 히로인 테마 8곡, 회상 3곡, 장소 곡(해바라기밭·작업실·집·유치원·전시관·사무실·해안가·노을 거리), 웨딩·새드·배드·트루 엔딩
- 지정은 flow_assets.csv 의 bgm 칸 (tools/apply_bgm.py 가 초안 생성 · 직접 고친 뒤에는 다시 돌리지 마세요)
- 강지우 과거 회상(jiwoo_fb1~4)은 대본 파일이 없어 각 에피소드 첫 줄(…_ep#_0001)에만 지정했습니다
