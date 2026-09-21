# 자산 포트폴리오 프로젝트

## 개요
개인 자산 포트폴리오 추적 웹 앱. **단일 HTML 파일**로 동작하며 모든 데이터는 브라우저 localStorage에 저장됨. CPI / M2 / USD-KRW 환율 등 거시지표와 비교하여 **실질 자산 변화 추적**하는 것이 핵심 목적.

## 파일 구조
- `자산_포트폴리오.html` — 메인 앱 (UI + 로직 + 스타일 단일 파일, ~4600줄)
- `proxy_server.py` — 로컬 CORS 프록시 (BLS/FRED 등 외부 API 우회용)
- `Portfolio_Launcher.vbs`, `Stop_Server.vbs`, `start_server.bat` — Windows 실행/종료 스크립트
- `portfolio_YYYY-MM-DD.json` — 스냅샷 백업 파일들
- `portfolio_backup.json` — 최신 백업

## 외부 의존성 (CDN)
- Chart.js 4.4.1
- chartjs-chart-treemap 3.1.0

## 자산 분류
```js
const ASSET_TYPES = ['현금', '주식', '채권', '금', '원자재', '부동산', '암호화폐'];
```

## 거시지표 추적
이력 스냅샷 저장 시 자동 수집:
- **CPI** — BLS Consumer Price Index (시리즈 `CUUR0000SA0`)
- **M2** — FRED M2 Money Supply (시리즈 `M2SL`)
- **USD/KRW 환율** — 그 시점 환율

## 금 가격 fetch (KRX vs COMEX 괴리)
`fetchAndApplyGoldPrice()` (line ~4505) 는 **Yahoo `GC=F` (COMEX 금 선물 USD/oz)** 을 fetch 후 환산:
```js
krwPerGram = round((usdPerOz * usdKrwRate) / 31.1034768)
```

**KRX 금현물 실제 종가와 1,000~1,500원/g 정도 차이** 발생 (한국 김치 프리미엄, 자체 수급/유동성). 예: COMEX 환산 218,800원/g 일 때 KRX 종가 220,140원/g.

**의도된 동작** — 구조적 한계로 받아들이고 이력 일관성(COMEX 환산값 기준 연속 트래킹) 유지에 우선순위. 사용자 확인 완료.

대안 (필요 시):
- **KRX Data Marketplace JSON** — `POST https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd` body `bld=dbms/MDC/STAT/standard/MDCSTAT16101&trdDd=YYYYMMDD`. 종목코드 `04020000` = 금현물 1g. 장 마감 후 종가만 제공. OTP 쿠키 필요 가능성. proxy_server.py에 `data.krx.co.kr` allowlist 추가 필요.
- **pykrx** Python 라이브러리가 위를 래핑함. 브라우저용 아님.
- 실시간 KRX 시세는 유료 데이터상품.

세 지표 모두 **절대값 / 누적변화 / YoY** 표시. 뉴스 헤드라인과 매칭되는 것은 YoY 수치라 같이 노출하는 것이 중요 (예: CPI 컬럼에 절대값 + 첫 스냅샷 대비 누적 % + YoY %).

## 이력 차트 (History Chart)
이력 탭의 라인 차트는 **거시 환경 비교 전용**으로 단순화됨. 5개 라인:
1. **총자산 (명목 USD)** — 검정, 굵게
2. **실질 자산 (CPI 보정)** — 청록
3. **CPI 기준선** — 빨강 점선
4. **M2 통화공급 기준선** — 보라 점선
5. **USD/KRW 환율** — 주황 점선 (정규화 모드에서만)

**자산타입별 라인은 의도적으로 제거**됨. 자산타입 분해는 종목별 트리맵 + 이력 테이블에서 더 정확하게 확인 가능하므로 이력 차트는 환경 비교에만 집중.

### 차트 표시 모드 (정규화 vs 절대값)
차트 위 우측 "표시 모드" 토글로 두 모드 전환:

- **절대값 (USD)** — Y축 $ 단위. 환율 라인은 단위 불일치(KRW)로 자동 숨김.
- **정규화 (%)** — 모든 라인이 첫 스냅샷 = 0% 기준으로 변환. 비중 무관 성과 비교 가능. 환율도 같이 노출. **기본값**.

모드는 `state.historyChartMode`로 localStorage에 영구 저장됨.

### Legend 가시성 보존
모드 토글 시 차트를 destroy/recreate하기 때문에 legend 선택 상태가 리셋되는 문제가 있었음. `renderCharts._histPrevVis`로 destroy 직전 상태를 라벨 기준으로 저장하고, 새 데이터셋 생성 시 복원함. 라벨 매칭은 ` (USD)` 접미사를 stripping하여 모드 간 stable key 사용.

```js
const visFor = (label, defaultHidden) => {
  const key = label.replace(/\s*\(USD\)$/, '');
  if (prevVis.hasOwnProperty(key)) return !prevVis[key];
  return defaultHidden;
};
```

## State 마이그레이션 패턴
`loadState()`에서 누락된 필드 기본값을 채워주는 패턴. 새 필드 추가 시 다음과 같이 추가:

```js
if (s.historyChartMode === undefined) s.historyChartMode = 'normalized';
```

기존 사용자의 저장된 선택은 절대 덮어쓰지 않음 — `=== undefined` 체크로 신규 사용자만 새 기본값 적용.

## 주요 작업 시 주의사항

### 숫자 표기
- **한국식 만/억 단위 사용**: "4억", "1,400만"
- 영어식 축약 금지: "400M", "14M" 등 사용 안 함
- USD는 `$112.5k` 같은 표기 OK

### 단일 파일 구조 유지
- HTML + CSS + JS 모두 `자산_포트폴리오.html` 한 파일에
- CSS/JS 분리하지 않음 (file:// 프로토콜로도 작동해야 함)

### 데이터 영속성
- 모든 상태는 `localStorage` (`STORAGE_KEY`). 백업은 JSON export/import만 가능.
- 차트 visibility는 영속화 안 함 (인메모리만 — `renderCharts._histPrevVis`)

### 차트 재렌더링
```js
Object.values(charts).forEach(c => c?.destroy?.());
charts = {};
// ... 새로 생성
```

### 주요 함수
- `renderCharts()` — 모든 차트 재렌더링 진입점
- `setChartMode(mode)` — 이력 차트 모드 토글
- `usdLineOpts(rawMap)` / `normLineOpts(rawMap)` — 차트 옵션 (절대값/정규화)
- `loadState()` / `saveState()` — localStorage 입출력 + 마이그레이션

## 검증 방법
JS 문법 체크가 필요할 때:
```bash
# 인라인 <script> 추출 후 node --check
python3 -c "..." > extracted.js && node --check extracted.js
```

---

# AI 기업 9-factor 채점표 — 운영 룰 (채점 관련 요청 시 필독)

"채점", "점수", "factor", "재채점", "트리거", 기업명+점수 언급 등 **채점표 관련 요청이 오면 아래를 그대로 따른다.** 이 룰은 채점 문서 자체보다 우선한다.

## 파일 4개 + 도구 2개

| 파일 | 역할 | 바뀌는 주기 |
|---|---|---|
| `AI기업_채점규칙_vX.Y.md` | 9 factor 정의 · 별표 A~F · ⑥ 구간표(NTM PER) · ⑨ 서열표(2단계 게이트) · 체크리스트 17 · ③ 사다리 판정표 · ① 채널 매핑 | 📐 규칙 개정 때만 → 버전업 + 소급 |
| `AI기업_채점표_vX.Y.md` | 순위표 · 기업별 상세(불릿) · 원자료(3-1a 가격/3-1b 실적) · 해석 · 트리거 | 분기마다 새 버전 |
| `AI기업_채점표_vX.Y.html` | 친구용 대시보드 — `D` 배열이 단일 진실, KPI·산점도·순위는 자동 계산 | 채점표와 동시 |
| `AI기업_채점표_운영이력.md` | 감사 기록 · 변동 분류(📈📐🔧📏) · 갱신 절차 · **버전표** · 긴장 목록 | 누적 |
| `채점이력.csv` | 분기×기업×F1~F9 시계열 | 점수 바뀔 때마다 |
| `check_채점표.py` | 산술·MD↔HTML 동기·구조·표기 검사 | **저장 전 매번 실행** |

## 채점 전 — 반드시 이 순서로 읽는다

1. **규칙 파일** 전체 — 특히 체크리스트 17개, 별표 E(비AI 사업은 ①·③수익모델·④에서만), ⑥ 구간표(NTM PER 단일, 예외 없음), ⑨ 서열표
2. **운영이력** — 버전표 최신 행(현재 버전·기준선), 남은 판단 긴장 목록(현재 6건)
3. **채점표** 트리거 표 — 이번에 확인할 이벤트가 등록돼 있는지
4. 해당 기업 카드 — **현재 점수와 근거를 읽은 뒤에** 새 정보를 대조

읽지 않고 채점하면 반드시 재발하는 오류: 이중 계상(체크리스트 1), 같은 잣대 불일치(3), Arena 단독(②), 조달을 동맹으로(15), 검색 없이 "미등재" 단정(긴장 #3 사례), 예외 오버라이드 신설(⑥ NVIDIA 사례).

## 점수를 바꿀 때 — 반드시 이 순서로 고친다

1. **변동 유형 먼저 분류** — 📈실적 / 📐규칙 / 🔧정정 / 📏경계통과. 📐면 규칙 파일 버전업 + 전 기업 소급 검토
2. 채점표 MD: 순위표 행 → 카드 헤딩·한 줄 요약·해당 factor 불릿 → 해석·트리거
3. HTML: `D` 배열의 `s`/`t`/`rank`/`tag`/`r`/`rt` — 텍스트 하드코딩 금지(KPI·순위·산점도는 자동)
4. CSV: 해당 분기 행의 F값·과점·함정·조정·변동사유·출처
5. 운영이력: 버전표에 한 행(같은 날 여러 번이면 그 행에 누적), 긴장 목록 갱신
6. `python3 check_채점표.py` → 전부 통과 확인. HTML은 `node --check` + 산점도 겹침 시뮬레이션
7. 사용자에게 **바뀐 점수·사유·순위 변동**만 보고 (파일 내용 재설명 금지)

## 절대 규칙

- 규칙 요약을 채점표에 복제하지 않는다 (규칙은 한 곳에만)
- 구간표·서열표 결과를 다른 지표로 올리거나 내리지 않는다 (예외 금지)
- "미등재·없음·미출시" 같은 부재 주장은 **검색 후에만**
- 근거 문자열은 ` · ` 구분 — HTML이 자동 불릿화하므로 `<b>`·괄호 균형 유지
- 통화는 $M/$B/$T, 한국식 억/조 금지 · "상회/하회" (비트/미스 금지) · "vs" 금지
- 참고 기업(현재 Moonshot)은 MD 순위표에 *참고* 행만, HTML 카드 없음
- 같은 날 반복 수정은 버전 올리지 않고 같은 버전 행에 누적. 새 분기 = 새 마이너 버전(실적만) 또는 메이저(규칙 변경)

## 현재 상태 (2026-09-02)

v1.5 · 14개사(참고 1) · 기준선 = v1.5 · Meta 16 단독 1위 · 다음 재채점 2026-11 (분기 실적 후)

## Imported Claude Cowork project instructions

자산 포트폴리오 상시 업데이트 및 나의 목표에 맞는 
수치 가시화
