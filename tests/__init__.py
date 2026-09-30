# unittest discover 가 tests/ 를 패키지로 임포트하기 위한 마커
import os

# 2026-09-30: 사용자의 실제 .env(SEC_UA 등)를 테스트가 읽지 않게 한다. 하위 프로세스(CLI 종단 테스트)도 이 값을 물려받는다.
# 빈 문자열이면 evidence_lib.read_local_setting 이 .env 를 읽지 않는다. .env 를 시험하는 테스트는 이 값을 직접 바꾼다.
os.environ["SCORECARD_DOTENV"] = ""
