# AI 기업 9-factor 채점표

AI 기업을 아홉 항목으로 채점하는 프레임워크입니다. **판단자의 판단을 정해진 규칙으로 정리하고 검산합니다.** 코드가 기업을 평가해 주는 도구가 아닙니다.

앞의 다섯(① 네트워크 효과 · ② 신기술 게임체인저 · ③ Last Mover · ④ 호황 이후 비전 · ⑤ 아군 확보)은 더하고, 뒤의 넷(⑥ 가격 · ⑦ 순환금융 · ⑧ 비대칭 의존 · ⑨ 적자 깊이)은 뺍니다.

## 지금 상태 (2026-09-21)

| 항목 | 값 |
| --- | --- |
| 최신 실행 | `ai-scorecard-2026-09-obsreg` · 기준일 2026-09-02 · 규칙 v1.7 |
| 점수 지문 | `results_hash 4a3f6c05b206ef81…` |
| 리뷰 | 독립 세션 4영역 리뷰 9라운드 끝에 네 영역 pass (2026-09-17) |
| 승인 | 2026-09-17 사용자 승인. 그 뒤 **설명 문장과 화면 표시만** 고쳤고 점수 파일은 바이트 단위로 동일합니다. 초안이 바뀌어 승인 효력이 멈춘 **재승인 대기** 상태입니다 |
| 테스트 | `npm run test:scorecard` 797건 통과 |

조정총점은 alphabet 15 · amazon 15 · meta 15 · microsoft 14 · tsmc 10 · anthropic 10 · spacex-xai 9 · nvidia 9 · apple 8 · alibaba 7 · palantir 6 · tesla 5 · openai 4 · oracle 2 입니다.

## 아홉 항목은 어떻게 매겨지나

항목마다 틀이 잡힌 깊이가 다릅니다.

| 단계 | 항목 | 점수가 나오는 방식 |
| --- | --- | --- |
| 측정값만으로 계산 | ⑥ 가격 | 공시 숫자(매출·순이익·시가총액)를 규칙의 절대 구간에 넣습니다. 사람 판단이 들어가지 않습니다 |
| 측정값 + 사람 판단 | ⑨ 적자 깊이 | 영업손익·현금흐름은 공시에서, `현금흐름 추세` 같은 여덟 가지 판정은 사람이 넣습니다. 흑자 회사의 0점과 −1점은 사람이 고른 추세 한 칸으로 갈립니다 |
| 정해진 질문에 답하면 표가 환산 | ③ ⑤ ⑦ | ③ 은 네 기준의 통과·실패, ⑤ 는 동맹·적대 등급, ⑦ 은 두 축을 사람이 정하고 코드는 표로 환산만 합니다 |
| 점수를 직접 입력 | ① ② ④ ⑧ | 점수와 근거 문장을 통째로 적습니다. ② 는 규칙에 환산표가 있지만 이번 실행에서는 쓰이지 않았습니다 |

코드가 맡는 일은 셋입니다. 모든 기업에 **같은 잣대를 강제**하고, **산수 실수를 없애고**, 어떤 입력에서 어떤 점수가 나왔는지 **지문으로 묶어 추적**할 수 있게 합니다.

## 쓰는 법

```
plan → collect → research → calculate → draft → review → (사람) 승인 → build
```

실행 하나의 산출물은 `output/<run_id>/` 한 폴더에 모입니다. 아래 표의 명령은 모두 `uv run --frozen python -X utf8` 뒤에 붙여 실행합니다.

| 단계 | 명령 | 산출물 (`output/<run_id>/`) |
| --- | --- | --- |
| 실행 생성 | `scripts/scorecard_cli.py init <run_id> --rule v1.8 --as-of 2026-09-02 --title ... --request ...` | `plan.md`, `run.json`, `observations.json`, `judgments.json`, `sources.json` |
| 근거 수집 | `scripts/scorecard_cli.py collect <run_id> [--company a,b] [--kind news\|filings\|prices\|all] [--since YYYY-MM-DD]` | `evidence/candidates.json`, 이어서 후보를 골라 `evidence/evidence.json`·`triggers.json` |
| 리서치 | `scripts/scorecard_cli.py research <run_id>` | `research.md` (인용한 근거의 출처를 `sources.json` 에 등록) |
| 계산 | `scripts/scorecard_cli.py calculate <run_id>` | `results.json`, `preview.md` |
| 초안 | `scripts/scorecard_cli.py draft <run_id>` | `draft.md` |
| 리뷰 | `scripts/scorecard_cli.py review-template <run_id>` 뒤 독립 세션 4영역 리뷰 | `review.md`, `review-parts/` |
| 승인 | 사람이 승인 페이지에서 (아래 절) | `approval.json` |
| 빌드 | `scripts/build_report.py <run_id>` | `report.html`, `audit.md`, `scorecard/history.csv` |
| 상태 확인 | `scripts/scorecard_cli.py status <run_id>` · `scripts/scorecard_cli.py summary <run_id> --json` · `scripts/validate_report_contract.py <run_id>` | 단계별 완료 여부, 승인 페이지용 요약, 계약 위반 목록 |

Claude Code 에서는 `/score-plan`, `/score-collect`, `/score-research` 처럼 슬래시 명령으로도 부를 수 있습니다. 각 단계의 에이전트 작업 계약은 `.claude/skills/score-*/SKILL.md` 에 있습니다. 명령마다 인자는 `--help` 로 확인합니다.

run_id 는 `ai-scorecard-` 로 시작하고 `plan.md` frontmatter 의 `report_type: ai_scorecard` 로 분기합니다. 기준선 v1.5 는 `scripts/scorecard_cli.py import-baseline` 으로 원본에서 읽어 옵니다.

### 근거 계층

`collect` 는 뉴스·공시·가격 후보를 `evidence/candidates.json` 에 모읍니다. 에이전트가 관련 있는 후보만 `evidence/evidence.json` 에 후보(`candidate`) 상태로 올리고, 사람이 승인 페이지에서 확정(`confirmed`)하거나 거부합니다. 새 판단(`status: new`)은 확정된 근거만 인용합니다. 트리거(`triggers.json`)는 재채점 조건만 담고 미래 점수를 저장하지 않습니다. 공시가 `not_disclosed`(발행사가 공시하지 않음을 확인)인 것과 `unverified`(우리가 찾지 못함)인 것은 구분합니다.

가격은 `collect --kind prices` 가 yfinance 로 ⑥ `price`·`market_cap` 관측을 넣습니다. EPS 와 컨센서스는 받지 않습니다. 조회일이 종가일과 하루 넘게 다르면 벤더 시가총액을 쓰지 않고, ADR 시가총액은 벤더 값만 씁니다. 받아 온 원문은 `data/<company_id>/` 에 캐시되고(gitignore), `SCORECARD_DATA_ROOT` 환경변수로 위치를 바꿀 수 있습니다.

공시 수집(`--kind filings`)에는 `SEC_UA`(SEC 가 요구하는 식별 문자열, 이름과 연락처)가 필요합니다. 저장소 루트의 `.env` 파일에 `SEC_UA=이름 이메일` 한 줄을 적습니다. git worktree 에서 실행하면 그 워크트리 루트를 먼저 보고, 없으면 원본 체크아웃 루트의 `.env` 를 읽으므로 원본 폴더 한 곳에만 두면 됩니다. `.env` 는 gitignore 되어 커밋되지 않고, 보호 훅이 에이전트의 쓰기를 막습니다. 같은 이름의 환경변수가 있으면 그것이 먼저입니다.

### 승인 페이지

승인과 승인 취소는 사람만 합니다. 에이전트는 "승인 대기" 를 보고하고 멈춥니다.

1. 프로젝트 루트에서 `node server.js --approvals` 를 실행합니다. 터미널에 6자리 일회용 코드가 나옵니다.
2. 브라우저에서 `http://127.0.0.1:3000/approve/<run_id>` 를 엽니다.
3. 요약을 확인하고, 근거 후보를 확정하거나 거부합니다.
4. 터미널의 코드를 입력해 승인합니다. 필요하면 같은 페이지에서 취소합니다.

코드를 5번 틀리면 서버를 다시 띄워야 하고, 승인이 성공하면 서버는 내려갑니다. 근거를 확정하면 판단·결과·초안의 해시가 바뀌어 리뷰가 무효가 되므로, 에이전트에게 `calculate`·`draft`·`review` 를 다시 시킨 뒤 승인합니다.

**판단을 입력하는 명령은 아직 없습니다.** 지금 판단 데이터는 v1.5 채점표에서 기계로 읽어 온 것과 에이전트가 고친 것입니다.

## 파일은 네 종류입니다

| 종류 | 무엇 | 위치 |
| --- | --- | --- |
| 기준 | 무엇을 보고 몇 점을 줄지 | 사람용 `AI_company_analysis_factor/` (채점규칙 · 별표 A~J) · 기계용 `scorecard/rules/v1.7.json` (새 실행은 `v1.8.json`) |
| 입력 | 공시 숫자와 사람 판단, 근거 | `output/<run_id>/observations.json` · `judgments.json` · `sources.json` · `evidence/evidence.json` · `triggers.json` |
| 계산 | 입력에 기준을 적용하는 코드 | `scripts/scorecard/` (`calc_f6_params.py` · `calc_f9.py` · `calc_qual.py` · `render_*.py` · `validate.py`) |
| 지시 | 에이전트의 작업 순서와 금지 사항 | `AGENTS.md` · `.claude/skills/score-*` · `.claude/agents/` |

점수는 기준·입력·계산 셋만으로 결정됩니다. 지시 문서는 일하는 순서를 적은 안내서이고 점수에 영향을 주지 않습니다.

**사람용 규칙 문서는 v1.5 에 멈춰 있습니다.** v1.6·v1.7 의 변경은 기계용 JSON 과 결정 기록에만 있어, 별표 일부(⑥ 전체 · ⑦ 별표 I · ⑨ 게이트 · ② 의 5점 조건 · ⑤ 의 +2 조건)가 지금 점수와 다릅니다.

## 지문으로 묶여 있습니다

각 단계의 산출물에는 앞 단계 파일의 지문(sha256)이 기록됩니다. 승인 파일은 규칙·숫자·판단·실행 설정·점수·초안 여섯 개의 지문을 담습니다. 앞 단계가 한 글자라도 바뀌면 리뷰와 승인이 자동으로 무효가 됩니다. 근거 문장만 고쳐도 같습니다. 그래서 승인된 리포트는 **어떤 입력에서 나온 점수인지 나중에도 증명**할 수 있습니다.

리포트 본문에는 읽는 사람을 위한 내용만 싣습니다. 해시, 결정 번호(C-01~C-29), 긴장 번호, 리뷰 진행 기록, 정정 이력은 `output/<run_id>/audit.md` 에 있습니다.

## 가드레일

가드레일 훅은 `scripts/hooks/guard.py` 한 모듈에 있고, 훅 하나가 함수 하나입니다. 목록과 한계는 `scripts/hooks/README.md` 에 있습니다.

| 훅 (`guard.py` 함수) | 이벤트 | 역할 |
| --- | --- | --- |
| `block_dangerous_bash` | 셸 실행 전 | `rm -rf /`, `sudo`, 원격 스크립트 파이프 실행, 강제 push 차단 |
| `protect_sensitive_files` | 셸·파일 도구 실행 전 | 보호 목록(`.env*`, `.git/`, `.github/workflows/`, `docs/finance-style-guide.md`, `**/approval.json`, `scorecard/rules/v1.5~v1.7.json`, `scorecard/history.csv`, `scorecard/baseline/**`, 승인된 기준선·관측 실행 묶음 `output/ai-scorecard-2026-09-baseline/`·`output/ai-scorecard-2026-09-obsreg/`) 수정 차단. 셸 명령은 보호 경로가 쓰기 대상(리다이렉션 대상, 변경 동사 인자)일 때만 막고 읽기 명령의 언급은 통과시키며, `python`·`node`·`uv run python` 인터프리터 명령이 보호 경로를 담으면 막음. 승인 있는 실행에 대한 `scorecard_cli.py init … --force` 와 승인·취소 명령은 셸에서 차단 |
| `enforce_plan` | 셸·파일 도구 실행 전 | `output/<run_id>/` 단계 순서 강제, `report.html`·`audit.md` 직접 쓰기 차단, 빌드 전 리뷰 `pass` 요구, 다른 소유자의 실행 잠금이 있는 묶음 쓰기 차단 |
| `forbid_financial_advice` | 파일 도구 실행 전·후, 셸 실행 후 | `draft.md`·`judgments.json`·`evidence/*.json` 의 투자 권유·수익 보장 표현 차단. 셸 실행 뒤에는 무엇이 바뀌었는지 알 수 없으므로 대상 파일 전체를 다시 검사 |
| `remind_review` | 파일 도구 실행 후, 세션 종료 | 리뷰 입력이 바뀌었거나 리뷰 해시가 현재 산출물과 다르면 경고만 함 |
| `enforce_memory` | 파일 도구 실행 후 | `memory/_daily/`·`memory/topics/` 변경 뒤 `scripts/validate_memory.py` 실행, 실패하면 차단 |
| `inject_memory_context` | 프롬프트 제출 | 프롬프트에 맞는 `memory/topics/*.md` 를 문맥으로 주입 |

배선은 Claude Code 가 `.claude/settings.json`, Codex 가 `.codex/hooks.json` 입니다. 두 곳 모두 `uv run --frozen … python -X utf8 scripts/hooks/guard.py <훅이름>` 한 줄로 부릅니다.

훅은 둘째 방어선입니다. 첫째는 승인 해시 검증과 CLI 의 거부(에이전트 세션의 승인·취소 거부)이고, 훅은 도구 호출 밖의 동작을 막지 못합니다. 다만 임의 Python 을 실행할 수 있는 에이전트가 작정하면 첫 방어선도 우회할 수 있으므로, 최종 보증은 사람이 git 이력에서 승인 파일의 변경을 확인하는 것입니다.

## 이해상충

채점 대상에 Anthropic 이 들어 있고, 이 저장소의 작업 상당 부분을 Anthropic 의 Claude 가 수행했습니다. Anthropic 과 그 직접 경쟁사(OpenAI · Google)에 걸린 판단은 **Claude 가 아닌 세션이 재판정**하는 것을 원칙으로 합니다. 최종 승인은 항상 사용자가 합니다.

## 작업공간과 브랜치

Orca 작업공간은 폴더 복사본이 아니라 이 저장소의 git worktree 입니다. 커밋은 모두 이 저장소 하나에 있습니다.

| 브랜치 | 역할 |
| --- | --- |
| `HANSOLJJ/worker` | 코드·규칙·데이터를 실제로 고치는 곳 |
| `HANSOLJJ/설계진행` | 과제 분배와 검증 기록(`validation/`) |
| `HANSOLJJ/review-obsreg` | 독립 리뷰 기록(`reviews/_parts/`) |
| `HANSOLJJ/NTM-전망치조사` · `HANSOLJJ/C-13` · `HANSOLJJ/scarpper` | 자료 조사와 보조 검증 |

2026-09-21 에 위 브랜치를 `main` 으로 합쳤습니다. 같은 경로에 서로 다른 내용이 있던 C-13 의 네 파일은 `validation/*/c13/` 아래에 따로 보존했습니다.

## 다음에 정할 것

1. **사람용 v1.7 규칙 문서** — v1.5 원문에서 출발해 바뀐 자리만 `이전 → 지금` 으로 표시합니다. 규칙을 사람 말로 옮길 때마다 오류가 나왔으므로 독립 대조를 거칩니다.
2. **별표를 리포트에 싣기** — 본문이 별표를 46번 가리키지만 내용은 리포트에 없습니다.
3. **재승인과 정식 빌드** — 점수는 그대로이고 설명만 바뀌었습니다.
4. **기업 추가 명령** — `add-company` 로 레지스트리에 등록하고, `init --from-run` 으로 이전 실행을 이어받아 **새 기업만 조사**합니다. 기존 기업 불변은 `diff` 가 기계로 증명합니다. 계획 승인 완료, 구현 중입니다.
5. **규칙 폴더를 `v1.5/` · `v1.7/` 로 정리** — `scripts/scorecard/baseline_import.py` 와 테스트 둘이 지금 경로를 직접 참조하므로 경로 수정과 함께 해야 합니다.
6. **정성 판단의 입력 창구** — 에이전트가 질문별로 답·근거·출처를 조사해 제안하고, 사용자가 검토 화면에서 동의하거나 고치는 방식을 검토 중입니다.
7. **v1.8 방향** — 점수를 직접 입력하는 ① ② ④ ⑧ 을 ③ ⑤ ⑦ 처럼 정해진 질문으로 쪼개고, 질문마다 공시에서 잴 수 있는 값(고객 집중도 · 벤치마크 순위 · 출하 여부 · 수주잔고)을 붙입니다.

세부 미결 사항은 `docs/scorecard/open-items.md`, 도메인 명세는 `docs/scorecard/design-guideline.md`, 구조 지침은 `docs/scorecard/structure.md` 에 있습니다.

## 설치와 보조 명령

```bash
uv sync --frozen
npm run check
```

```bash
uv run --frozen python -X utf8 -m unittest discover -s tests -t .   # 채점표 테스트 (npm run test:scorecard)
uv run --frozen pytest -q                                           # pytest (npm run test:pytest)
npm run test:node                                                   # 승인 서버 테스트
uv run --frozen python -X utf8 scripts/validate_report_contract.py <run_id>   # 계약 검증
uv run --frozen python -X utf8 scripts/validate_memory.py                     # 작업 메모 검증
node server.js                                                      # output/ 로컬 미리보기 (http://localhost:3000/<run_id>/report.html)
node server.js --approvals                                          # 승인 페이지 (사람이 실행)
```

- 포트 3000 이 쓰이고 있으면 기존 프로세스를 끄지 말고 `PORT=<빈 포트>` 로 띄웁니다.
- Python 3.12+ 와 uv, `pyproject.toml` 의 PyYAML·yfinance, Node.js 18+, Claude CLI
- `SEC_UA`(공시 수집용, 루트 `.env` 또는 환경변수), `SCORECARD_DATA_ROOT`(수집 캐시 위치, 기본 `data/`), `SCORECARD_DOTENV`(`.env` 대신 읽을 파일, 빈 값이면 읽지 않음. 테스트가 쓴다)
