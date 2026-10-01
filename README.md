# AI 기업 9-factor 채점표

AI 기업을 아홉 항목으로 채점하는 프레임워크입니다. **판단자의 판단을 정해진 규칙으로 정리하고 검산합니다.** 코드가 기업을 평가해 주는 도구가 아닙니다.

앞의 다섯(① 네트워크 효과 · ② 신기술 게임체인저 · ③ Last Mover · ④ 호황 이후 비전 · ⑤ 아군 확보)은 더하고, 뒤의 넷(⑥ 가격 · ⑦ 순환금융 · ⑧ 비대칭 의존 · ⑨ 적자 깊이)은 뺍니다.

## 지금 상태 (2026-10-01)

| 항목 | 값 |
| --- | --- |
| 최신 실행 | `ai-scorecard-2026-09-obsreg` · 기준일 2026-09-02 · 규칙 v1.7 · 묶음 `output/ai-scorecard-2026-09-obsreg/` |
| 점수 지문 | `results_hash 4a3f6c05b206ef81…` |
| 리뷰 | 독립 세션 4영역 리뷰 9라운드 끝에 네 영역 pass (2026-09-17) |
| 승인 | 2026-09-21 사용자 재승인. 승인 유효(`status` 의 `approval_valid: true`) |
| 다음 실행 준비 | 규칙 v1.8, 근거 수집(`collect`: 구글 뉴스·SEC 공시·yfinance 가격), 승인 페이지(`node server.js --approvals`)의 근거 확정·판단 수정, 근거 선별 평가 표본 38건(`tests/fixtures/evidence/`, 라벨 대기) |
| 테스트 | `npm run test:scorecard` 1146건 통과(원자료가 없는 워크트리에서는 13건 건너뜀), `npm run test:node` 15건 통과 |

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
| 판단 수정 | 사람이 승인 페이지 8절에서, 명령은 `scripts/scorecard_cli.py judge <run_id> --company <id> --factor F1..F9 …` (아래 「판단 수정」) | `judgments.json` 의 `revision_history` |
| 승인 | 사람이 승인 페이지에서 (아래 절) | `approval.json` |
| 빌드 | `scripts/build_report.py <run_id>` | `report.html`, `audit.md`, `scorecard/history.csv` |
| 상태 확인 | `scripts/scorecard_cli.py status <run_id>` · `scripts/scorecard_cli.py summary <run_id> --json` · `scripts/validate_report_contract.py <run_id>` | 단계별 완료 여부, 승인 페이지용 요약, 계약 위반 목록 |

Claude Code 에서는 `/score-plan`, `/score-collect`, `/score-research` 처럼 슬래시 명령으로도 부를 수 있습니다. 각 단계의 에이전트 작업 계약은 `.claude/skills/score-*/SKILL.md` 에 있습니다. 명령마다 인자는 `--help` 로 확인합니다.

run_id 는 `ai-scorecard-` 로 시작하고 `plan.md` frontmatter 의 `report_type: ai_scorecard` 로 분기합니다. 기준선 v1.5 는 `scripts/scorecard_cli.py import-baseline` 으로 원본에서 읽어 옵니다.

### 근거 계층

`collect` 는 뉴스·공시·가격 후보를 `evidence/candidates.json` 에 모읍니다. 에이전트가 관련 있는 후보만 `evidence/evidence.json` 에 후보(`candidate`) 상태로 올리고, 사람이 승인 페이지에서 확정(`confirmed`)하거나 거부합니다. 새 판단(`status: new`)은 확정된 근거만 인용합니다. 트리거(`triggers.json`)는 재채점 조건만 담고 미래 점수를 저장하지 않습니다. 공시가 `not_disclosed`(발행사가 공시하지 않음을 확인)인 것과 `unverified`(우리가 찾지 못함)인 것은 구분합니다.

가격은 `collect --kind prices` 가 yfinance 로 ⑥ `price`·`market_cap` 관측을 넣습니다. EPS 와 컨센서스는 받지 않습니다. 조회일이 종가일과 하루 넘게 다르면 벤더 시가총액을 쓰지 않고, ADR 시가총액은 벤더 값만 씁니다. 종가가 NaN 인 날은 건너뛰고 기준일 이하의 직전 확정 종가와 그 날짜를 기록하며, 건너뛴 날짜는 수집 요약에 남습니다. 가격 실패는 **회사 단위**입니다. 조회·관측 생성·중복(같은 기업·지표·기준일)·검증이 한 회사에서 실패하면 그 회사만 `failed` 로 남고 나머지는 기록되므로, 부분 실패 뒤 다시 돌리면 빠진 회사만 들어갑니다. 받아 온 원문은 `data/<company_id>/` 에 캐시되고(gitignore), `SCORECARD_DATA_ROOT` 환경변수로 위치를 바꿀 수 있습니다.

공시 수집(`--kind filings`)에는 `SEC_UA`(SEC 가 요구하는 식별 문자열, 이름과 연락처)가 필요합니다. 저장소 루트의 `.env` 파일에 `SEC_UA=이름 이메일` 한 줄을 적되 **영문으로** 씁니다(HTTP 머리글 제약이라 영문 밖 글자가 있으면 값을 보이지 않고 오류를 냅니다). 뉴스 수집의 요청 식별자도 같은 검사를 거칩니다. 공시를 모을 때만 이 값을 읽으며, 문제가 있으면 그 회사의 공시가 `failed` 로 남고 가격은 영향이 없습니다. git worktree 에서 실행하면 그 워크트리 루트를 먼저 보고, 없으면 원본 체크아웃 루트의 `.env` 를 읽으므로 원본 폴더 한 곳에만 두면 됩니다. `.env` 는 gitignore 되어 커밋되지 않고, 보호 훅이 에이전트의 쓰기를 막습니다. 같은 이름의 환경변수가 있으면 그것이 먼저입니다.

뉴스 질의는 기본이 표시명과 티커입니다. `Meta` 나 `Oracle` 처럼 일반 단어와 겹치는 이름은 `scorecard/companies.json` 의 기업 줄에 `news_queries`(문자열 배열)를 두어 질의를 좁힙니다. 지금 meta(`Meta Platforms`·`META stock`), oracle(`Oracle Corporation`·`ORCL`), apple(`Apple Inc`·`AAPL`)에 들어 있습니다. 같은 파일에 상장 12개사의 SEC CIK(`cik`)도 기입돼 있고, 비상장 anthropic·openai 는 없습니다. 티커에서 CIK 를 다시 확인하려면 `scripts/scorecard_cli.py resolve-cik [--company id] [--apply] [--json]` 를 씁니다. `--apply` 는 확인된(`resolved`) 것만 레지스트리에 쓰고, `--json` 은 표 대신 `{rows, applied}` 한 줄을 냅니다. 두 키는 수집기만 읽으므로 점수 지문(`results_hash`)은 바뀌지 않습니다.

### 승인 페이지

승인과 승인 취소는 사람만 합니다. 에이전트는 "승인 대기" 를 보고하고 멈춥니다.

1. 프로젝트 루트에서 `node server.js --approvals` 를 실행합니다. 터미널에 6자리 일회용 코드가 나옵니다.
2. 브라우저에서 `http://127.0.0.1:3000/approve/<run_id>` 를 엽니다.
3. 요약을 확인하고, 근거 후보를 확정하거나 거부합니다.
4. 판단을 고쳐야 하면 8절 「정성 판단 수정」에서 고칩니다(아래).
5. 터미널의 코드를 입력해 승인합니다. 필요하면 같은 페이지에서 취소합니다.

코드를 5번 틀리면 서버를 다시 띄워야 하고, 승인이 성공하면 서버는 내려갑니다. 근거를 확정하거나 판단을 고치면 판단·결과·초안의 해시가 바뀌어 리뷰가 무효가 되므로, 에이전트에게 `calculate`·`draft`·`review` 를 다시 시킨 뒤 승인합니다.

#### 판단 수정

사람이 승인 페이지 8절에서 정성 판단의 **입력**을 고칩니다. 점수를 덮어쓰지 않고, 입력을 고치면 점수는 규칙이 다시 계산합니다.

1. `http://127.0.0.1:3000/approve/<run_id>?factor=F3` 처럼 factor 를 고르면 그 factor 의 모든 기업 판단이 나란히 보입니다. **같은 factor 의 다른 기업 판단을 함께 보고** 잣대가 같은지 확인한 뒤 고칩니다(체크리스트 Q03).
2. 기업을 고르면(`&company=<id>`) 판정 종류에 맞는 입력란이 나옵니다. 근거 문장, 사유, 이름을 적고 터미널의 코드를 넣어 제출합니다. 이전 값은 판단 안의 `revision_history` 에 남고, `status: new`·검토자·검토일이 갱신됩니다.
3. 해시가 바뀌었다는 안내가 나오면 에이전트에게 `calculate`·`draft`·`review` 를 다시 시킵니다. 리뷰가 `pass` 가 된 뒤 새로고침해 승인합니다.

| factor | 고칠 수 있는 것 |
| --- | --- |
| ① ④ ⑧ | 점수(`score`)와 근거 문장 |
| ③ | 네 기준(`criteria`: imitation · revenue_model · acceleration · door_closed)과 근거 문장 |
| ⑤ | 등급(`grade`: A 0~2, H 0~−3)과 근거 문장 |
| ⑦ | 매트릭스(`matrix`: funding_dependent_share · own_money_returns)와 근거 문장 |
| ⑨ | 게이트 입력(`gate_inputs`: fcf_trend · bep_retreat · buffer_erosion · direction_A·B · coverage_comparable · operating_result_reviewed)과 근거 문장 |
| ② ⑥ | 대상이 아닙니다 |

③ ⑤ ⑦ ⑨ 는 점수 칸을 고칠 수 없고 판정 재료만 바뀝니다. 점수를 직접 고치는 길은 없습니다. 명령줄 `scripts/scorecard_cli.py judge <run_id> --company <id> --factor F1..F9 (--set key=value … | --evidence "문장" … | --json 파일) --reason "…" --by <이름>` 도 같은 일을 하며, 에이전트가 판단 수정을 제안할 때 쓰는 길입니다(승인 페이지는 사람 이름과 코드를 받아 이 명령을 부릅니다). 새 판단(`status: new`)은 확정된 근거만 인용합니다.

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
| `protect_sensitive_files` | 셸·파일 도구 실행 전 | 보호 목록(`.env*`, `.git/`, `.github/workflows/`, `docs/finance-style-guide.md`, `**/approval.json`, `scorecard/rules/v1.5~v1.7.json`, `scorecard/history.csv`, `scorecard/baseline/**`, 승인된 기준선·관측 실행 묶음 `output/ai-scorecard-2026-09-baseline/`·`output/ai-scorecard-2026-09-obsreg/`) 수정 차단. 셸 명령은 보호 경로가 쓰기 대상일 때만 막고 읽기 명령의 언급은 통과시킴. 쓰기 대상은 리다이렉션 대상, 변경 동사(`rm`·`mv`·`tee`·`sed -i` 등)와 PowerShell cmdlet(`Set-Content`·`Add-Content`·`Out-File`·`Remove-Item`·`Move-Item`·`New-Item`·`Rename-Item`·`Clear-Content` 와 기본 별칭)의 경로 인자, 복사(`cp`·`Copy-Item`)의 목적지, `find … -delete`·`-exec`, `xargs <변경 동사>`, 보호 경로와 맞는 글롭이며, 보호 경로를 품은 상위 폴더 삭제·이동(`rm -rf output`)도 막음. `python`·`node`·`uv run python` 인터프리터 명령이 보호 경로를 담으면 막음. 승인 있는 실행에 대한 `scorecard_cli.py init … --force` 와 승인·취소 명령은 셸에서 차단 |
| `enforce_plan` | 셸·파일 도구 실행 전 | `output/<run_id>/` 단계 순서 강제, `report.html`·`audit.md` 직접 쓰기 차단, 빌드 전 리뷰 `pass` 요구, 다른 소유자의 실행 잠금이 있는 묶음 쓰기 차단 |
| `forbid_financial_advice` | 파일 도구 실행 전·후, 셸 실행 후 | `draft.md`·`judgments.json`·`evidence/*.json` 의 투자 권유·수익 보장 표현 차단. 셸 실행 뒤에는 무엇이 바뀌었는지 알 수 없으므로 대상 파일 전체를 다시 검사 |
| `remind_review` | 파일 도구 실행 후, 세션 종료 | 리뷰 입력이 바뀌었거나 리뷰 해시가 현재 산출물과 다르면 경고만 함 |
| `enforce_memory` | 파일 도구 실행 후 | `memory/_daily/`·`memory/topics/` 변경 뒤 `scripts/validate_memory.py` 실행, 실패하면 차단 |
| `inject_memory_context` | 프롬프트 제출 | 프롬프트에 맞는 `memory/topics/*.md` 를 문맥으로 주입 |

배선은 Claude Code 가 `.claude/settings.json`, Codex 가 `.codex/hooks.json` 입니다. 두 곳 모두 `uv run --frozen … python -X utf8 scripts/hooks/guard.py <훅이름>` 한 줄로 부릅니다.

훅은 둘째 방어선입니다. 첫째는 승인 해시 검증과 `scorecard.stages` 의 `approve`·`revoke` 함수 본체가 하는 거부입니다. 이 거부는 CLI 로 부르든 import 로 부르든 같은 판정(`agent_session_markers`)을 거치고, 환경변수 표지(`CLAUDECODE`·`CLAUDE_CODE_ENTRYPOINT`·`ORCA_AGENT_LAUNCH_TOKEN`·`AI_AGENT`, Muse 세션의 `MUSE_TOOL_USE_ID`)가 하나라도 있으면 에이전트 세션으로 봅니다. 승인 있는 실행에 대한 `init --force` 도 에이전트 세션이면 `init_run` 이 거부합니다. 훅은 도구 호출 밖의 동작을 막지 못합니다. 다만 임의 Python 을 실행할 수 있는 에이전트가 작정하면 첫 방어선도 우회할 수 있으므로, 최종 보증은 사람이 git 이력에서 승인 파일의 변경을 확인하는 것입니다.

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
6. **정성 판단의 제안 흐름** — 고치는 창구(`judge`, 승인 페이지 8절)는 생겼습니다. 에이전트가 질문별로 답·근거·출처를 조사해 제안하고 사용자가 검토 화면에서 동의하는 앞단은 아직 검토 중입니다.
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
