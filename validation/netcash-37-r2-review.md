# MERGE-MAIN 완료 + NETCASH-37 라운드 2 검토

- 검토일. 2026-09-11.
- 대상. worker `5613ac2`(머지) · `e0eebfb`(NETCASH-37 R2).
- 판정. **머지 `pass`. NETCASH-37 R2 는 `pass` + 정정 2건.**

## 머지 — 전수 재현

| 확인 | 결과 |
|---|---|
| `HEAD..main` | 0건 |
| AGENTS.md blob | `9e3f860` — **main 과 동일 해시** |
| `e0eebfb` ancestor | 포함 |
| 테스트 | **258건 직접 실행, OK** (245 + `test_scorecard_net_cash.py` 13건) |

세 파일 해결을 전부 눈으로 확인했다. 지침대로다.

### 충돌이 아니던 자리를 같이 고친 것

제가 "귀하 판단에 맡깁니다" 로 넘긴 줄이다. 고치는 쪽이 맞았다.

```
print("Generated files:" if report_type_for(args.slug) == "ai_scorecard" else "Price chart JSON:")
```

**git 이 충돌로 세운 자리와 실제로 깨진 자리가 다르다.** hero 가 선택 사항이 된 순간 `image_path is not None` 이 유형 판별을 못 하게 됐고, 그 줄은 충돌 표시가 없었을 뿐 같은 원인으로 이미 틀려 있었다. **충돌 목록을 다 처리했다고 머지가 끝난 것이 아니다** — 오늘 NTM 이 "충돌 0 이 머지 성공이 아니다" 를 찾은 것과 같은 축의 다른 면이다.

## 후속 셋 — 전부 들어 있다

| 지시 | 위치 |
|---|---|
| alibaba 시장성 기준 재등록 | `alibaba.net_cash.nc37` verified 49,838,648,884 · `securities_scope` include/exclude |
| `net_cash` 정의 명문화 | `status: working_definition` · `provenance.kind: legacy_reverse_engineered` · `rejected_candidates` 4 · `supersede` |
| 6.4 범위 | `f6.net_cash.scope_separation` **과** `f9.g3_cash_scope` 두 자리 |

**두 자리에 적은 것이 맞다.** `why_here` 에 이유가 있다 — 6.4 를 고치러 온 사람이 P2 를 같이 고치는 것과 P2 를 고치러 온 사람이 6.4 를 끌어오는 것, **양방향**을 막아야 한다.

## 점수에 닿는지 직접 확인했다

**등록만 하고 소비되지 않는 경우를 의심했는데 아니었다.**

```
alibaba   (270,000 − 49,839) / 148,401 = 1.484   밴드 0~8    P2 0
          legacy 17.5B 였으면 1.700              같은 밴드
nvidia    17.831                                 밴드 8~20
          legacy 23.6B 였으면 17.813             같은 밴드
```

**값은 바뀌었고 밴드를 안 넘었다.** 순위 불변이 설명된다. 14/14 완주 유지.

중복 관측(`*.v15` legacy 와 `*.nc37` verified 공존)은 `ObsLookup.get` 이 `verified`(2) > `legacy_unverified`(1) 로 정렬해 처리한다. **대체 표시가 `note` 자유 서술에만 있어 의심했으나 실제 선택은 `status` 로 이뤄진다.** 선언이 소비자를 갖는 쪽이다.

## 정정 1 — `definition` 한 줄이 실제 계산과 모순

```
policies.f6.net_cash.definition
  "현금및현금성자산 + 유가증권 전체(단기·비유동) − 총차입금 − 리스부채(유동+비유동)"
                      ~~~~~~~~~~~
securities_scope.criterion  "유가증권은 시장성 있는 것에 한한다"
components.excluded         지분법 투자 · 전략적 지분투자 · 제한 현금
```

**실제 계산은 후자를 따랐다.** alibaba 에서 지분법 206,803 + 비상장 130,447 RMB백만을 뺐다. 넣었으면 49.8B 가 아니라 약 98.7B 다 — **"전체" 라고 적힌 정의로 계산하면 두 배 틀린다.**

```
rules/v1.7.json        1곳  ← 원천
observations.json     10곳  basis.definition
results.json          11곳  P2.net_cash_definition.definition
scripts/.../rules.py   1곳  docstring
```

**기업마다 `results.json` 에 박혀 나가는 유일한 정의 문장이다.** 한 줄만 읽고 계산하는 사람이 있다는 전제로 고쳐야 한다.

**오늘 `private_note` 대 `private_bands` 와 같은 모양이고 방향만 반대다.** 그때는 일반 규칙을 고치고 개별 note 를 안 맞췄고, 이번엔 개별 기준(`securities_scope`)을 새로 세우고 요약 한 줄을 안 맞췄다.

## 정정 2 — docstring 숫자가 한 라운드 전

```
rules.py  "12개사 중 6개사가 반올림 이내로 맞고"
evidence.matched.count  →  7   (palantir·spacex-xai 가 R2 에서 들어옴)
```

라운드 1 은 5, R2 는 7, docstring 은 6. **어느 라운드도 아니다.**

## worker 가 자체 발견한 것 둘

- **palantir 는 차입금 결측이 아니라 0 이다.** MCAP-36 이 결측으로 뒀는데, 2026-06-30 사실 44건 전수에 차입 부채가 없고 비유동부채 258,098천이 리스 211,400 + 이연수익 33,722 + 기타 12,439 로 전액 설명된다. **결측과 0 을 가른 것**이고 합계로 검산했다.
- **nvidia 만기 버킷 이중계상.** C-13 이 `만기 1년 이내 공정가치` 41,000 을 현금에 더해 6,857 이 이중계상됐다. 만기 버킷은 대차대조표 줄이 아니고 현금성자산으로 분류된 증권까지 포함한다.

**spacex-xai 일치가 경계의 가장 강한 증거다.** 서로 독립인 두 정정(금융리스 1,079 제외 · 제한현금 830 제외 + 시장성 증권 6,487 추가)이 동시에 들어가야 60,301 이 나오고 legacy 60,300 과 100만 달러 차이다.

## 후속

| 건 | 처리 |
|---|---|
| **`definition` 한 줄** | worker — 원천 1곳 수정 후 재실행, 파생 21곳은 손대지 않는다 |
| **docstring 숫자** | worker — `evidence.matched.count` 참조 권장 |
| apple·palantir `net_cash` | NTM 리스 태깅 공백 조사 중 |
| `market_cap` | legacy 유지. 허용된 가격 원천 없음 |
| amazon·nvidia·tsmc·alibaba legacy 불일치 4건 | 원인 미상. 규칙에 `open_questions` 로 등재됨 |
