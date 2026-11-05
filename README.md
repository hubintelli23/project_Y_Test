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
