# 결정 기록

- 2026-10-01 사용자: "나중에" 로 분류한 5건(V2-9, N-1, N-3, N-4, V2-12)을 빼고 나머지 6건을 고친다.
- 2026-10-01 사용자: V2-6 은 가격과 시가총액 기준일이 하루 어긋나도 상관없어 닫는다.
- V2-7: 이미 같은 SRC-YF 출처로 기록된 회사는 시세를 다시 받지 않고 skipped_existing 으로 낸다. 출처 항목은 첫 url·accessed_at 을 두고 publisher_url 에 티커를 덧붙이며 재조회 시각은 note 에 남긴다. 기존 테스트 둘의 failed 기대를 바꿨다.
- V2-10: 되돌리기는 BaseException 으로 넓혔다(Ctrl+C 도 되돌린다). 값 종류 검사는 스키마 공통 검증이 아니라 judge 입력 경로에만 넣었다. 기존 판단 파일에 영향을 주지 않기 위해서다.
- V2-11: revision_history 에 선택 키 session(agent|human)을 더했다. 기존 이력에는 없으므로 선택 키다. summary 의 judgments 에 last_revision_session 을 더해 summary 계약 픽스처(tests/node/fixtures/summary.sample.json)도 바꿨다. judge·confirm 은 다른 소유자 잠금을 먼저 검사(write=False)하고 성공한 뒤에 기록한다.
- V2-13: 승인 모드(enabled)에서만 6자리 숫자 코드를 요구한다. 꺼진 서버는 코드 없이 만든다.
- N-2: import_baseline 본체가 out_dir 이름(v1.5)으로 protect_baseline_consumers 를 부른다. stages 가 baseline_import 를 import 하므로 함수 안에서 가져온다. CLI 의 중복 호출은 뺐다(경고 두 번 방지).
- V2-8: 샌드박스만 고치면 test_collect_news 등 샌드박스를 안 쓰는 파일이 남아, 여섯 파일이 각자 SCORECARD_DOTENV 를 비우게 했다.
