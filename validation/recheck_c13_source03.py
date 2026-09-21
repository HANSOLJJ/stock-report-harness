# C13-SOURCE-03 제출 커밋의 테스트와 적격성 근거 차이를 읽기 전용으로 재현한다.
import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent / 'C-13'
COMMIT = '20c7d14'
PREFIX = 'validation/consensus-source-2026-09-09/'


def read(path, commit=COMMIT):
    return subprocess.check_output(['git', '-C', str(REPO), 'show', f'{commit}:{PREFIX}{path}'])


def main():
    code = read('verify_sources.py').decode('utf-8-sig')
    namespace = {'__name__': 'independent_review', '__file__': str(REPO / PREFIX / 'verify_sources.py')}
    exec(compile(code, '20c7d14/verify_sources.py', 'exec'), namespace)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        namespace['run_unit_tests']()
    assert log.getvalue().count('PASS]') == 11
    evidence = json.loads(read('evidence.json'))
    observations = []
    for cid, ticker in [('tsmc', 'tsm'), ('alibaba', 'baba')]:
        source = evidence['listed_companies'][cid]['sources_investigated']['nasdaq_api']
        raw = json.loads(read(f'raw/nasdaq-{ticker}-earnings_forecast.json'))
        evaluated = namespace['evaluate_quarterly_single_source'](
            source['quarters_available'], source['quarters_data'])
        assert evaluated['all_4q_fulfilled'] is True
        assert evaluated['scoring_eligible'] is False
        assert source['evaluation']['scoring_eligible'] is True
        assert raw['data']['quarterlyForecast']['asOf'] is None
        for row, entry in zip(raw['data']['quarterlyForecast']['rows'][:4], source['quarters_data'].values()):
            for k, rk in [('mean', 'consensusEPSForecast'), ('min', 'lowEPSForecast'),
                          ('max', 'highEPSForecast'), ('count', 'noOfEstimates')]:
                assert entry[k] == row[rk]
        observations.append({'company': cid, 'reported_eligible': True,
                             'without_asserted_metadata': evaluated, 'source_as_of': None})
    files = subprocess.check_output(['git', '-C', str(REPO), 'ls-tree', '-r', '--name-only', COMMIT, '--', PREFIX + 'raw/']).decode().splitlines()
    integrity = []
    for path in files:
        relative = path.removeprefix(PREFIX)
        current, prior = read(relative), read(relative, '5187e92')
        assert current == prior
        integrity.append({'file': path, 'sha256': hashlib.sha256(current).hexdigest(), 'unchanged_from': '5187e92'})
    result = {'reviewed_commit': COMMIT, 'verdict': 'needs_fix', 'unit_tests_passed': 11,
              'unit_test_log': log.getvalue().splitlines(), 'observations': observations,
              'raw_integrity': integrity,
              'scope': 'Frozen commit read only; source unit tests and 8 EPS rows rerun. Metadata booleans do not establish external proof. Raw comparison covers these 6 files only, not worker or entire repository.'}
    (ROOT / 'c13-source03-review-evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'PASS: 11 submitted unit tests; 8 quarter rows; {len(integrity)} raw files unchanged.')
    print('REVIEW: needs_fix. asOf null in both sources; eligibility depends on asserted metadata.')


if __name__ == '__main__':
    main()
