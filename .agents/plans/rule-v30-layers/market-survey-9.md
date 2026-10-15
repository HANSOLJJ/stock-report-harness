# 나머지 9개사 시장 조사 (2026-10-15, 기준일 2026-10-14)

대상: amazon, microsoft, meta, nvidia, oracle, tesla, palantir, alibaba, openai. 매출 줄은 SEC 공시(sec-get 캐시)에서 읽었고, 시장 출처는 Sonnet 조사원 여덟이 본문을 열어 확인했다. 결론을 가르는 값은 조율 에이전트가 다시 열었다. 예상 D·E 는 실제 `calc_market.market_position`(3a3ed80 반영)에 정의표 초안과 원문 값을 넣어 대조했다("calc"). 조사원 메모는 세션 스크래치 `markets-survey\` 아래에 있다(세션이 끝나면 사라진다).

제약: WebSearch 한도 200회가 중간에 소진돼 EV·BESS·게임·전자상거래 일부는 "못 찾아봄"이다(찾지 못함이 아님). newzoo.com 은 도구 차단, musicbusinessworldwide.com 은 Cloudflare 확인 화면, CNBC 는 접근 거부, Focus2Move 는 봇 확인 화면이라 모두 우회하지 않았다.

## 결론

- 지금 기준만으로 값이 나오는 것은 기존 정의표로 들어오는 사업뿐이다.
- 새 정의표로 값이 나오려면 사용자 결정이 필요한 것: StatCounter AI 챗봇, StatCounter 데스크톱 OS, IDC XR, JustWatch, 연간 시장(Gartner 반도체·IaaS, Apps Run The World).
- 기준에 맞는 무료 정기 출처를 못 찾은 것: 광고 매출, 전자상거래, 퀵커머스, 게임, EV, BESS, 데이터센터 가속기, 소비자 오피스, IT 서비스, DBMS, Palantir 정부·상업 AI 플랫폼.

## 기존 정의표로 들어오는 사업 (calc)

| 회사 | 사업 | 시장 | D | E |
|---|---|---|---|---|
| amazon | AWS | cloud_infra | 3 | 0 (28 대 30%) |
| microsoft | Server products and cloud | cloud_infra | 2 | 1.0 (20 대 20%, 반올림 낮은 쪽) |
| oracle | Cloud infrastructure | cloud_infra | 0 | 미확인 |
| alibaba | Cloud Intelligence | cloud_infra | 0 | 미확인 |
| microsoft | Search advertising(Bing) | search_engines | 2 | 2.71 (4.73 대 4.01%) |
| microsoft | LinkedIn | social_media | 0 (6위) | 1.88 |
| meta | Advertising | social_media | 4 | 0 (79.13 대 82.38%) |
| microsoft | Windows and Devices | pcs | 0 (IDC 상위 5 밖) | 미확인 |
| amazon | Subscription services | tv_viewing | 0 (8위) | 2.67 (4.37 대 3.60%) |

amazon 태블릿·meta 웨어러블은 별도 매출 줄이 없다.

## 새 정의표 후보

| 시장 id 후보 | 출처 | 단위 | 예상(calc) | 걸리는 점 |
|---|---|---|---|---|
| ai_chatbots | StatCounter AI Chatbot 분기 CSV(2025-04 시작) | 챗봇에서 추적 사이트로 간 유입 점유율, 6개 이름 | openai D4·E0(79.39 대 81.57), alphabet D2·E4(10.64 대 2.44), microsoft D0·E0, anthropic D0·E3.15, xAI·Meta 미확인(목록 밖·제외) | 규칙문 "공시 없는 시장의 설문·중계 서비스는 참고"에 걸리는지. 유입 측정이라 앱 안 이용·구독·API 는 재지 않는다. 최근 분기 값은 45일 동안 수정될 수 있다 |
| xr_headsets_glasses | IDC 2Q26 블로그(2026-09-16), 2Q25 보도자료 | XR 헤드셋+안경 출하 | meta D4·E4(68.7 대 60.6), alibaba D1·E 미확인 | Counterpoint XR(72→54%)·Omdia(71.3→48.2%)는 하락. 안경 비중에 따라 방향이 반대 |
| desktop_os | StatCounter 데스크톱 OS 분기 | 웹 사용 점유율 | microsoft D4·E0(79.35→69.81), apple(OS X+macOS) D2·E4, alphabet D0·E2.23 | Windows 줄을 PC 출하로 읽을지 사용량으로 읽을지. 같은 분기 IDC PC 출하와 크게 다르다 |
| us_svod | JustWatch 미국 SVOD 분기(전재 기사만) | 이용자 관심 행동 | amazon D1·E0(Disney 합산) 또는 D2·E0, apple D0·E4 | JustWatch 자체 페이지 404, Amazon 구독 줄은 Prime 회비 중심 |
| semiconductors(연간) | Gartner 반도체 매출 상위 10 | 반도체 전체 매출 점유율 | nvidia D3·E4(15.8 대 11.7), apple D0·E 미확인 | 메모리·모바일 포함 전체 시장, Gartner NVIDIA 값은 공시 매출의 약 58%, 잠정→확정 사이 순위 변동 전례 |
| enterprise_apps, erp(연간) | Apps Run The World | 소프트웨어 매출 점유율 | microsoft 앱 D3·E1.6, oracle 앱 D0·E1.96, oracle ERP D 미확인·E1.91, microsoft ERP D0·E1.94, openai D 미확인·E2.67, anthropic D 미확인·E2.55 | ARTW 를 조사기관으로 칠지, 값이 자체 모형, 한 줄이 여러 시장으로 갈림 |
| iaas(연간) | Gartner IaaS 2024 연간 | IaaS 만, 상위 5 | alibaba D0·E1.2, oracle D0·E 미확인 | Synergy(cloud_infra)와 단위가 달라 "같은 시장은 같은 정의"에 어긋난다 |

## 기존 정의표 사실 정정

- `cloud_infra.json` 의 Omdia 대체 출처 설명("점유율은 본문 차트 이미지에 있어 값은 읽지 않았다")이 틀리다. 4Q25 호(2026-03-26) 본문에 상위 3곳이 글자로 있다(AWS 32%, Azure 22%, Google Cloud 12%). 최신 호가 아직 4Q25 라 대체 출처로 쓰면 세 분기 늦고 값도 Synergy 와 크게 다르다.
- Synergy 부분은 원문과 맞다.

## 사용자 결정 거리 (조사 보고 C절)

1. 사용량 시장을 매출 줄의 시장으로 어디까지 쓰는가(선례: YouTube 광고→Nielsen 시청, X 광고→StatCounter 소셜). AI 챗봇이 "설문·중계는 참고" 문언에 걸리는지는 따로.
2. Windows and Devices: PC 출하(D0·E 미확인) 대 데스크톱 OS 사용량(D4·E0).
3. Reality Labs: IDC(E4) 대 Counterpoint·Omdia(E 하락) 대 기존 웨어러블(D0·E 미확인). 점수를 본 뒤 고르는 여지가 된다.
4. Amazon Subscription services: tv_viewing 대 JustWatch 대 미확인.
5. 연간·반기·누적 자료의 허용 범위. 순위만 글자이고 점유율이 이미지인 출처는 D 도 못 낸다.
6. 상위 N 목록 밖 = D0 의 한계: 목록이 그 사업의 시장이 아닐 때(Alibaba 와 미국 소매), 분류 때문에 빠졌을 수 있을 때(ARTW 와 Palantir), 상위 3만 이름을 드는 자료(eMarketer).
7. "조사기관의 무료 정기 통계"로 인정할 범위(ARTW, ECDB, JustWatch 전재, Syntun, QuestMobile, IDC 블로그, 유료 보고서 초록 한 줄).
8. Tesla: Counterpoint BEV 표가 본문과 모순(표 Tesla 13%·1위, 본문은 BYD 선두·Tesla 약 12%). 표 그대로 D3·E0, 행을 바로잡아 읽으면 D2·E1.0, 또는 출처를 버림.
9. 한 매출 줄이 여러 시장에 닿을 때(Oracle Cloud applications, Dynamics, NVIDIA Data Center, Reality Labs, Alibaba 고객관리).
10. Alibaba: 2026-06 분기 세그먼트 재편(재작성 표가 한 분기뿐), 클라우드는 Synergy 로 D0·E 미확인인데 다른 출처는 값을 냄, 20-F 가 경쟁자 이름을 꼽지 않음.
11. 같은 시리즈의 과거치가 고쳐진 경우(IDC Ethernet 2Q25 NVIDIA 25.9% → 함의 약 11.9%) 1년 전 값을 최초 발표로 볼지 현재 시리즈로 볼지.
12. 회사 공시 경쟁자 길은 Oracle·NVIDIA 만 이름을 꼽고 둘 다 같은 단위의 줄이 없다.

## 회사별 요약

- **Amazon**: AWS D3·E0. 온라인 스토어(36.8%)·3P(23.7%)·광고(9.8%)는 전년 값이 없거나 지역이 달라 미확인. 구독(6.8%)은 결정 4.
- **Microsoft**: 클라우드 D2·E1.0, Bing D2·E2.71, LinkedIn D0·E1.88. M365 Commercial(30.7%)은 ARTW 인정 시 D3·E1.6. Windows 는 결정 2. XBOX·M365 Consumer·서비스는 미확인.
- **Meta**: 광고(97.5%) → social_media D4·E0. Reality Labs(1.0%)는 결정 3.
- **NVIDIA**: Data Center(91.7%)는 Gartner 반도체 전체를 쓰면 D3·E4, 아니면 미확인. Edge Computing 은 값이 이미지라 미확인.
- **Oracle**: 클라우드 인프라 D0·E 미확인. Cloud applications(22.7%)는 ARTW 인정 시 값이 나옴. 지원·라이선스·서비스는 미확인. 하드웨어는 IDC 서버 상위 5 밖(D0).
- **Tesla**: 자동차(70.1%)는 결정 8. 에너지(12.4%)는 값이 이미지라 미확인.
- **Palantir**: ARTW 정부는 순위만 무료, 상업은 상위 25 밖이나 분류 확인 못 함. 사실상 미확인.
- **Alibaba**: 클라우드 D0·E 미확인. 나머지 줄은 회사 단위 값이 없어 미확인.
- **OpenAI**: 소비자는 ai_chatbots 인정 시 D4·E0. 기업·API 는 ARTW 인정 시 D 미확인·E2.67. 매출 구성 비중은 공식 발표에 금액이 없다(유출 재무제표 보도는 등급을 가르는 수치로 쓰지 않는다).
