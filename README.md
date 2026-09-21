# 주식 리포트 하네스

<p align="center">
  <img src="sample.png" width="380" alt="삼성전자 리포트 예시" />
</p>

자연어 한 줄이면 Toss 스타일 종목 리포트가 나옵니다.

```
/stock-goal 삼성전자 1년 분석
```

Claude Code를 열고 위 명령을 입력하면, 계획 → 리서치 → 원고 → 히어로 이미지 → 4-way 리뷰 → 빌드까지 자동으로 진행되어 검증된 HTML 리포트가 생성됩니다.

이 저장소에는 파이프라인이 둘 있습니다. 종목 리포트(`stock-*`)와 [AI 기업 9-factor 채점표](#ai-기업-9-factor-채점표-ai_scorecard)(`score-*`)입니다. 채점표의 현재 상태와 다음에 정할 것은 아래 채점표 절에 있습니다.

`plan/<slug>.md`가 후속 단계의 단일 기준 문서이며, 모든 산출물은 같은 `slug`의 선행 파일을 참조합니다.

## 파이프라인

```text
/stock-plan <요청>      → plan/<slug>.md
/stock-research <slug> → research/<slug>.md + 원자료 JSON
/stock-draft <slug>    → drafts/<slug>.md
/stock-image <slug>    → hero 후보 3개 + selected-image.json
/stock-review <slug>   → reviews/<slug>.md
/stock-build <slug>    → scripts/build_report.py가 output/<slug>.html + price-chart JSON 생성
```

<!-- 2026-09-07 hero 선택 사항 변경 전: 빌드는 `review status: pass`, 선택된 hero 이미지, yfinance 가격 차트, frontmatter/섹션 정합성을 -->
빌드는 `review status: pass`, yfinance 가격 차트, frontmatter/섹션 정합성을
`scripts/validate_report_contract.py`로 모두 통과해야 성공합니다. hero 이미지는 선택 사항이며 있을 때만 함께 검증합니다.

### End-to-end skill: `stock-goal`

단계별 명령 대신 Claude Code의 `stock-goal` skill을 사용하면 자연어 요청 하나로 전체 파이프라인을 순차 실행합니다.

```text
stock-goal: 삼성전자 최근 30일 분석 리포트 생성
→ plan → research → draft → image → review → build
→ output/<slug>.html
```

`stock-goal`은 각 `/stock-*` 단계의 계약을 그대로 따릅니다. 선행 산출물이 없으면 먼저 만들고, review가 `needs_fix`이면 수정 후 재리뷰 루프를 돌며, 동일 차단 이슈가 반복되면 `blocked`로 멈춥니다. 최종 보고에는 생성 산출물 목록, HTML 경로, 프리뷰 URL, 파이프라인 중 발생한 이슈가 포함됩니다.

## 주요 디렉터리

```text
.claude/commands/      slash command 정의
.claude/skills/        단계별/엔드투엔드 실행 계약
.claude/agents/        review용 subagent
.claude/hooks/         Claude Code 훅 기반 가드레일
plan/                  계획서
research/              리서치 결과
drafts/                원고
reviews/               4-way 리뷰
output/                최종 HTML 및 assets
docs/                  스타일·출력·이미지 명세
design/                최종 HTML 렌더링 디자인 계약
scripts/               보조/검증 스크립트
server.js              output 미리보기 서버
```

## 디자인 문서 로직

- 리포트 UI의 기준 문서는 `design/toss_design.md`입니다. 색상, 타이포그래피, 간격, 컴포넌트, 차트 스타일, 한국 주식 색상 규칙(상승=빨강, 하락=파랑)을 정의합니다.
- `scripts/build_report.py`는 이 디자인 문서를 코드로 옮긴 deterministic renderer입니다. build 단계에서 새 디자인 판단을 즉흥적으로 추가하지 않고, draft/research 내용을 승인된 시각 규칙으로만 렌더링합니다.
- 디자인 변경 순서는 `design/toss_design.md` 갱신 → `scripts/build_report.py` 반영 → 필요 시 `sample/skhynix.html`/`docs/output-spec.md` 동기화 → `npm run check` 및 리포트 build/validate입니다.
- `sample/skhynix.html`은 참고 composition입니다. 문서와 예시가 충돌하면 `design/toss_design.md`를 우선합니다.
- review의 `report-designer` 관점은 생성 HTML이 디자인 문서의 모바일 shell, hero 이미지 배치, price chart 스타일, References/footnote 배치 원칙을 지키는지 확인합니다.

## 단계별 핵심 계약

### Plan

- 필수 출력: `plan/<slug>.md`
- 필수 frontmatter: `slug`, `topic`, `request`, `output_type`, `audience`, `ticker`, `period_start`, `period_end`, `chart_required`, `price_data_source`, `price_data_interval`, `created_at`, `assumptions`
- 기간이 없으면 최근 6개월을 기본값으로 두고 `assumptions`에 기록합니다.

### Research

- plan의 `ticker`, `period_start`, `period_end`를 기준으로 작성합니다.
- 가격 데이터 요구는 yfinance 일봉(`interval=1d`)입니다.
- 종목 관련 요청은 최신 뉴스 최소 100건을 수집·분류·분석합니다.
- 기사 원문 URL이 없으면 조작하지 않고 fallback 여부를 표시합니다.

### Draft

- 필수 출력: `drafts/<slug>.md`
- plan과 research를 근거로 작성하고 `plan_source`, `research_source`를 남깁니다.
- H1은 정확히 1개입니다.
- 필수 섹션: `## 개요`, `## 배경`, `## 메커니즘`, `## 영향과 적용`, `## References`
- 가격 차트는 데이터 배열 대신 `price-chart` 블록으로 선언합니다.
- 투자 권유, 수익 보장, 매매 지시 표현은 금지합니다.

### Image

- `python3 scripts/run_stock_image_codex.py <slug>`가 Codex CLI를 열어 `imagegen` skill / built-in `image_gen`으로 hero 후보 3개를 만들고 평가·선택 기록을 남깁니다.
- 필수 출력: `output/assets/<slug>-hero-v1~v3.*`, score JSON, image manifest, `selected-image.json`
- 이미지에는 텍스트, 숫자, 티커, 로고, 워터마크, UI 스크린샷을 넣지 않습니다.
- image manifest는 `status: complete`, `generation_method: codex-cli-imagegen`, `generated_with`를 포함해야 하며, procedural/Pillow/SVG/placeholder 방식은 build 검증에서 실패합니다.
- `selected-image.json`은 최소 `slug`, `selected_candidate`, `image_path` 또는 `selected_image`, `reason`, `generated_with`를 포함합니다. 경로는 `assets/<file>.png` 또는 `output/assets/<file>.png`처럼 resolver가 찾을 수 있는 값으로 둡니다.
- 이미지 생성 도구가 없으면 prompt 파일과 blocked manifest만 남기고 build로 진행하지 않습니다.

`selected-image.json` 예시:

```json
{
  "slug": "<slug>",
  "selected_candidate": 2,
  "image_path": "assets/<slug>-hero-v2.png",
  "reason": "리포트 결론과 가장 잘 맞음",
  "generated_with": "Codex CLI $imagegen / built-in image_gen"
}
```

### Review

- 별도 관점의 4-way review를 수행합니다.
- 리뷰어: `fact-checker`, `report-designer`, `content-editor`, Codex independent review
- 필수 출력: `reviews/<slug>.md`
- `status`는 `pass | needs_fix | blocked` 중 하나입니다.
- 리뷰 작성 후 `python3 scripts/validate_report_contract.py <slug>`를 실행해 계약을 통과해야 합니다.
- `needs_fix`이면 선행 단계 수정 후 같은 slug로 다시 review합니다.

### Build

<!-- 2026-09-07 hero 선택 사항 변경 전: - 필수 입력: plan, research, draft, pass review, selected hero image -->
- 필수 입력: plan, research, draft, pass review (selected hero image는 선택 사항)
- 필수 출력: `output/<slug>.html`, `output/assets/<slug>-price-chart-v*.json`
- 빌드는 수동 HTML 작성이 아니라 `python3 scripts/build_report.py <slug>`로 수행합니다.
- 빌더는 yfinance 1일봉 가격 JSON을 생성/갱신하고, Markdown/frontmatter를 파싱해 HTML 템플릿을 렌더링합니다.
- HTML 템플릿은 `design/toss_design.md`의 Toss 스타일을 따르며, `sample/skhynix.html`은 참고용 예시입니다.
- 빌드 완료 후 `python3 scripts/validate_report_contract.py <slug> --require-html --require-price-chart`를 통과해야 합니다.
- 최종 HTML 본문에는 `[S1]`, `[N1]` 같은 검증용 인라인 표식을 남기지 않습니다.
- 하단에 투자 유의 문구를 포함합니다.

## 훅 기반 가드레일

이 저장소는 Claude Code 프로젝트 훅으로 반복 실패를 사전에 차단합니다. 훅 설정은 `.claude/settings.json`에 있으며, 각 스크립트는 `.claude/hooks/` 아래에서 단일 책임으로 동작합니다.

| 훅 | 이벤트 | 역할 |
| --- | --- | --- |
| `block-dangerous-bash.sh` | `PreToolUse(Bash)` | `rm -rf /`, `sudo`, `curl ... | sh`, `git push --force/-f` 등 되돌리기 어려운 명령 차단 |
| `protect-sensitive-files.sh` | `PreToolUse(Bash/Write/Edit/MultiEdit)` | `.env*`, `.git/`, `.github/workflows/`, `docs/finance-style-guide.md`, `docs/output-spec.md` 수정 차단 |
| `forbid-financial-advice.sh` | `PreToolUse`, `PostToolUse` | draft/HTML의 투자 권유, 수익 보장, FOMO 표현 차단 |
| `enforce-plan.sh` | `PreToolUse` | `plan → research → draft → image → review → build` 선행 산출물 순서 강제 |
| `enforce-citations.sh` | `PreToolUse`, `PostToolUse` | draft 숫자 주장에 `[S1]`, `[N1]`, `[P1]`류 출처 표식 요구 |
| `remind-review.sh` | `PostToolUse`, `Stop` | draft 변경 후 최신 4-way `pass` review가 없으면 세션 종료 차단 |
| `inject-memory-context.sh` | `UserPromptSubmit` | 요청 도메인에 맞는 memory topic 자동 주입 |
| `enforce-memory.sh` | `PostToolUse` | memory 파일 변경 후 `python3 scripts/validate_memory.py` 실행 |

주의: 이 훅들은 Claude Code 에이전트가 이 프로젝트 설정을 읽을 때 자동 적용됩니다. Codex/OMX 런타임의 별도 도구 호출에는 같은 `.claude/settings.json` 훅이 자동으로 걸리지 않으므로 별도 연결이 필요합니다.

## 보조 명령

초기 설치:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
npm run check
```

계약 검증:

```bash
python3 scripts/validate_report_contract.py <slug>
python3 scripts/validate_report_contract.py <slug> --require-html --require-price-chart
```

deterministic build:

```bash
python3 scripts/build_report.py <slug>
```

이미지 단계:

```bash
python3 scripts/run_stock_image_codex.py <slug>
python3 scripts/run_stock_image_codex.py <slug> --dry-run  # Codex 프롬프트 확인용
```

최신 뉴스 5건 추출:

```bash
python3 scripts/news_latest5.py output/assets/<slug>-*-latest100.json --format markdown
```

메모리 검증:

```bash
python3 scripts/validate_memory.py
```

로컬 미리보기:

```bash
node server.js
# 콘솔에 최신 리포트 URL과 전체 HTML 리포트 목록이 표시됩니다.
# 예: Report URL: http://localhost:3000/samsung-electronics-recent-1y-2026-05.html
```

특정 리포트 링크를 우선 표시하려면 slug 또는 html 파일명을 넘깁니다.

```bash
node server.js samsung-electronics-recent-1y-2026-05
# Report URL: http://localhost:3000/samsung-electronics-recent-1y-2026-05.html
```

## AI 기업 9-factor 채점표 (ai_scorecard)

같은 하네스 안에서 AI 기업 14개사를 아홉 항목으로 채점합니다. 앞의 다섯 항목(① 네트워크 효과 · ② 신기술 게임체인저 · ③ Last Mover · ④ 호황 이후 비전 · ⑤ 아군 확보)은 더하고, 뒤의 네 항목(⑥ 가격 · ⑦ 순환금융 · ⑧ 비대칭 의존 · ⑨ 적자 깊이)은 뺍니다.

### 현재 상태 (2026-09-21)

| 항목 | 값 |
| --- | --- |
| 최신 실행 | `ai-scorecard-2026-09-obsreg` (기준일 2026-09-02, 규칙 v1.7) |
| 조정총점 | alphabet 15 · amazon 15 · meta 15 · microsoft 14 · tsmc 10 · anthropic 10 · spacex-xai 9 · nvidia 9 · apple 8 · alibaba 7 · palantir 6 · tesla 5 · openai 4 · oracle 2 |
| 점수 지문 | `results_hash 4a3f6c05b206ef81…` |
| 리뷰 | 독립 세션 4영역 리뷰 9라운드를 거쳐 네 영역 모두 pass (2026-09-17) |
| 승인 | 2026-09-17 사용자 승인. 그 뒤 **설명 문장과 화면 표시만** 고쳤고 점수 파일은 바이트 단위로 동일합니다. 다만 초안이 바뀌어 승인과 리뷰의 효력이 멈춘 상태이며 **재승인 대기**입니다. |
| 테스트 | `npm run test:scorecard` 797건 통과 |

### 아홉 항목은 어떻게 매겨지나

이 채점표는 코드가 기업을 평가하는 도구가 아닙니다. **판단자의 판단을 정해진 규칙으로 정리하고 검산하는 도구**입니다. 항목마다 틀이 잡힌 깊이가 다릅니다.

| 단계 | 항목 | 점수가 나오는 방식 |
| --- | --- | --- |
| 측정값만으로 계산 | ⑥ 가격 | 공시 숫자(매출·순이익·시가총액)를 구간에 넣습니다. 사람 판단이 들어가지 않습니다. |
| 측정값 + 사람 판단 | ⑨ 적자 깊이 | 영업손익·현금흐름은 공시에서, `현금흐름 추세` 같은 여덟 가지 판정은 사람이 넣습니다. 흑자 회사의 0점과 -1점은 사람이 고른 추세 한 칸으로 갈립니다. |
| 정해진 질문에 답하면 표가 환산 | ③ ⑤ ⑦ | ③ 은 네 기준의 통과·실패, ⑤ 는 동맹·적대 등급, ⑦ 은 두 축을 사람이 정하고 코드는 표로 환산만 합니다. |
| 점수를 직접 입력 | ① ② ④ ⑧ | 점수와 근거 문장을 통째로 적습니다. ② 는 규칙에 환산표가 있지만 이번 실행에서는 쓰이지 않았습니다. |

코드가 맡는 일은 셋입니다. 모든 회사에 같은 잣대를 강제하고, 산수 실수를 없애고, 어떤 입력에서 어떤 점수가 나왔는지 지문으로 묶어 추적할 수 있게 합니다.

### 파일은 네 종류입니다

| 종류 | 무엇 | 위치 |
| --- | --- | --- |
| 기준 | 무엇을 보고 몇 점을 줄지 | 사람용 `AI_company_analysis_factor/` (채점규칙 · 별표 A~J) · 기계용 `scorecard/rules/v1.7.json` |
| 입력 | 공시 숫자와 사람 판단 | `scorecard/runs/<slug>/observations.json` · `judgments.json` · `sources.json` |
| 계산 | 입력에 기준을 적용하는 코드 | `scripts/scorecard/` (`calc_f6_params.py` · `calc_f9.py` · `calc_qual.py` · `render_*.py` · `validate.py`) |
| 지시 | 에이전트의 작업 순서와 금지 사항 | `AGENTS.md` · `.claude/skills/score-*` · `.claude/agents/` |

점수는 기준·입력·계산 셋만으로 결정됩니다. 지시 문서는 일하는 순서를 적은 안내서이고 점수에 영향을 주지 않습니다.

**사람용 규칙 문서는 v1.5 에 멈춰 있습니다.** v1.6·v1.7 의 변경은 기계용 JSON 과 결정 기록에만 있어, 별표 일부(⑥ 전체 · ⑦ 별표 I · ⑨ 게이트 · ② 의 5점 조건 · ⑤ 의 +2 조건)가 지금 점수와 다릅니다.

### 단계와 명령

```
plan → research → calculate → draft → review → (사용자 승인) → build
```

| 단계 | 명령 | 산출물 |
| --- | --- | --- |
| 실행 생성 | `python scripts/scorecard_cli.py init <slug> --as-of 2026-09-02 --title ... --request ...` | `plan/<slug>.md`, `scorecard/runs/<slug>/{run,observations,judgments,sources}.json` |
| 리서치 | `python scripts/scorecard_cli.py research <slug>` | `research/<slug>.md` |
| 계산 | `python scripts/scorecard_cli.py calculate <slug>` | `results.json`, `preview.md` |
| 초안 | `python scripts/scorecard_cli.py draft <slug>` | `drafts/<slug>.md` |
| 리뷰 | `python scripts/scorecard_cli.py review-template <slug>` 뒤 독립 세션 4영역 리뷰 | `reviews/<slug>.md` |
| 승인 | `python scripts/scorecard_cli.py approve <slug> --by <이름>` (사용자만 실행) | `approval.json` |
| 빌드 | `python scripts/build_report.py <slug>` | `output/<slug>.html`, `output/<slug>-audit.md`, `scorecard/history.csv` |
| 상태 확인 | `python scripts/scorecard_cli.py status <slug>` · `python scripts/validate_report_contract.py <slug>` | 단계별 완료 여부와 계약 위반 목록 |

- slug 는 `ai-scorecard-` 로 시작하고 plan frontmatter 의 `report_type: ai_scorecard` 로 분기합니다. 기존 주식 리포트 계약은 바뀌지 않습니다.
- 기준선 v1.5 는 `python scripts/scorecard_cli.py import-baseline` 으로 원본 HTML·MD 에서 읽어 옵니다.
- **판단을 입력하는 명령은 아직 없습니다.** 지금 판단 데이터는 v1.5 채점표를 기계로 읽어 온 것과 에이전트가 고친 것입니다.

### 지문으로 묶여 있습니다

각 단계의 산출물에는 앞 단계 파일의 지문(해시)이 기록됩니다. 승인 파일은 규칙·숫자·판단·실행 설정·점수·초안 여섯 개의 지문을 담습니다. 앞 단계가 한 글자라도 바뀌면 리뷰와 승인이 자동으로 무효가 됩니다. 근거 문장만 고쳐도 같습니다. 그래서 승인된 리포트는 어떤 입력에서 나온 점수인지 나중에도 증명할 수 있습니다.

리포트 본문에는 읽는 사람을 위한 내용만 싣습니다. 해시, 결정 번호(C-01~C-29), 긴장 번호, 리뷰 진행 기록, 정정 이력은 `output/<slug>-audit.md` 에 있습니다.

### 이해상충

채점 대상에 Anthropic 이 들어 있고, 이 저장소의 작업 상당 부분을 Anthropic 의 Claude 가 수행했습니다. Anthropic 과 그 직접 경쟁사(OpenAI · Google)에 걸린 판단은 Claude 가 아닌 세션이 재판정하는 것을 원칙으로 합니다. 최종 승인은 항상 사용자가 합니다.

### 작업공간과 브랜치

Orca 작업공간은 폴더 복사본이 아니라 이 저장소의 git worktree 입니다. 커밋은 모두 이 저장소 하나에 있습니다.

| 브랜치 | 역할 |
| --- | --- |
| `HANSOLJJ/worker` | 코드·규칙·데이터를 실제로 고치는 곳 |
| `HANSOLJJ/설계진행` | 과제 분배와 검증 기록(`validation/`) |
| `HANSOLJJ/review-obsreg` | 독립 리뷰 기록(`reviews/_parts/`) |
| `HANSOLJJ/NTM-전망치조사` · `HANSOLJJ/C-13` · `HANSOLJJ/scarpper` | 자료 조사와 보조 검증 |

2026-09-21 에 위 브랜치를 `main` 으로 합쳤습니다. 같은 경로에 서로 다른 내용이 있던 C-13 의 네 파일은 `validation/*/c13/` 아래에 따로 보존했습니다.

### 다음에 정할 것

1. **사람용 v1.7 규칙 문서** — v1.5 원문에서 출발해 바뀐 자리만 `이전 → 지금` 으로 표시합니다. 규칙을 사람 말로 옮길 때마다 오류가 나왔으므로 독립 대조를 거칩니다.
2. **별표를 리포트에 싣기** — 본문이 별표를 46번 가리키지만 내용은 리포트에 없습니다.
3. **재승인과 정식 빌드** — 점수는 그대로이고 설명만 바뀌었습니다.
4. **규칙 폴더를 `v1.5/` · `v1.7/` 로 정리** — `scripts/scorecard/baseline_import.py` 와 테스트 둘이 지금 경로를 직접 참조하므로 경로 수정과 함께 해야 합니다.
5. **정성 판단의 입력 창구** — 에이전트가 질문별로 답·근거·출처를 조사해 제안하고, 사용자가 검토 화면에서 동의하거나 고치는 방식을 검토 중입니다. 판단을 고치면 리뷰와 승인을 새로 받아야 하므로 새 실행에서 씁니다.
6. **v1.8 방향** — 점수를 직접 입력하는 ① ② ④ ⑧ 을 ③ ⑤ ⑦ 처럼 정해진 질문으로 쪼개고, 질문마다 공시에서 잴 수 있는 값(고객 집중도 · 벤치마크 순위 · 출하 여부 · 수주잔고)을 붙입니다.

세부 미결 사항은 `docs/scorecard/open-items.md`, 도메인 명세는 `docs/scorecard/design-guideline.md`, 구조 지침은 `docs/scorecard/structure.md` 에 있습니다.

## 의존 도구
- Python 3.11+, `requirements.txt`의 yfinance/Markdown/PyYAML, Node.js 18+, Claude/Codex CLI
- 선택 도구: jq(수동 JSON 점검용)
- Node 미리보기/검증 스크립트: `npm run check`, `npm run test`, `npm start -- <slug>`
