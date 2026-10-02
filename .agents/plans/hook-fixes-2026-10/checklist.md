# 체크리스트

- [x] 1. 투자 권유 검사 범위(`_advice_kind`·`_evidence_text`·draft 인용 절 제외) + 테스트
- [x] 2. 저장소 메모리 폐지
  - [x] 교훈 3줄을 AGENTS.md·score-review 스킬로 이전, AGENTS.md `Memory System` 절 교체
  - [x] `memory/`·`docs/memory-system.md`·`scripts/validate_memory.py` 삭제
  - [x] guard.py 의 메모리 훅 2개와 주입 코드 삭제, 배선 두 파일, package.json, 테스트
- [x] 3. 체크아웃 인식 경로 판정 + 차단 문구 축약 + 테스트(`tests/test_hooks_checkouts.py`)
- [x] 4. 빌드 검사(`_build_targets`) + 테스트, TODO 의 해당 항목 삭제
- [x] 5. 위험 git 명령·홈 폴더 삭제 차단 + 테스트
- [x] 6. 빌드 성공 시 잠금 삭제 + 테스트, 원본의 낡은 잠금 삭제
- [x] 7. 문서(훅 설명서·README·guide·structure·TODO)
- [x] 탐침 재실행으로 전후 비교
- [x] 전체 테스트(파이썬·노드)
- [ ] 원본 main 에 반영
- [ ] fork 로 push (사용자 지시가 있을 때)
