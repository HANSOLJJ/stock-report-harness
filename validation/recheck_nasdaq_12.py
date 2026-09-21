# 제출 커밋의 12개사 Nasdaq 분기 원자료와 조사 증거를 독립 대조한다.
import json
from decimal import Decimal
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent.parent
SUBDIR = 'validation/consensus-source-2026-09-09/'


def read_json(repo, commit, path):
    data = subprocess.check_output(['git', '-C', str(repo), 'show', f'{commit}:{SUBDIR}{path}'])
    return json.loads(data.decode('utf-8-sig'))


def check_rows(rows, observations):
    by_period = {r['fiscalEnd']: r for r in rows}
    assert len(observations) == 4
    selected = []
    for obs in observations:
        raw = by_period[obs['period']]
        for key, raw_key in [('mean', 'consensusEPSForecast'), ('min', 'lowEPSForecast'),
                             ('max', 'highEPSForecast'), ('count', 'noOfEstimates')]:
            assert obs[key] == raw[raw_key], (obs, raw)
        assert raw['lowEPSForecast'] <= raw['consensusEPSForecast'] <= raw['highEPSForecast']
        assert isinstance(raw['noOfEstimates'], int) and not isinstance(raw['noOfEstimates'], bool)
        assert raw['noOfEstimates'] > 0
        selected.append(raw)
    months = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
    indexes = [int(r['fiscalEnd'].split()[1]) * 12 + months.index(r['fiscalEnd'].split()[0]) for r in selected]
    assert all(b - a == 3 for a, b in zip(indexes, indexes[1:]))
    return selected, str(sum(Decimal(str(r['consensusEPSForecast'])) for r in selected))


def main():
    out = []
    ntm_repo = next(BASE.glob('NTM-*'))
    ntm = read_json(ntm_repo, 'a74c15e', 'evidence.json')
    for company in ntm['companies']:
        cid = company['company_id']
        source = company['sources']['nasdaq_api']
        raw = read_json(ntm_repo, 'a74c15e', f'raw/nasdaq-{cid}-earnings_forecast.json')
        observations = [{'period': x['period_label_vendor'], 'mean': x['mean'], 'min': x['min'],
                         'max': x['max'], 'count': x['estimate_count']} for x in source['observations']]
        rows, total = check_rows(raw['data']['quarterlyForecast']['rows'], observations)
        out.append({'company': cid, 'commit': 'a74c15e', 'rows': rows, 'sum': total,
                    'source_as_of': raw['data']['quarterlyForecast']['asOf']})
    c13_repo = BASE / 'C-13'
    c13 = read_json(c13_repo, '5187e92', 'evidence.json')
    for cid, ticker in [('tsmc', 'tsm'), ('alibaba', 'baba')]:
        source = c13['listed_companies'][cid]['sources_investigated']['nasdaq_api']
        raw = read_json(c13_repo, '5187e92', f'raw/nasdaq-{ticker}-earnings_forecast.json')
        raw_rows = raw['data']['quarterlyForecast']['rows'][:4]
        entries = list(source['quarters_data'].values())
        assert len(entries) == 4
        observations = [{'period': r['fiscalEnd'], 'mean': x['mean'], 'min': x['min'],
                         'max': x['max'], 'count': x['count']} for r, x in zip(raw_rows, entries)]
        rows, total = check_rows(raw_rows, observations)
        assert Decimal(total) == Decimal(str(c13['listed_companies'][cid]['nasdaq_4q_sum']))
        out.append({'company': cid, 'commit': '5187e92', 'rows': rows, 'sum': total,
                    'source_as_of': raw['data']['quarterlyForecast']['asOf']})
    assert len(out) == 12
    result = {'status': 'pass_for_snapshot_values_only', 'companies': out,
              'scope': '48 quarterly values/ranges/counts, 3-month label continuity and sums. Not live re-fetch, official fiscal-date or scoring eligibility verification.'}
    (ROOT / 'nasdaq-12-recheck-evidence.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('PASS: 12 companies / 48 quarter rows. Values, ranges, counts, label continuity, sums.')
    print('Source asOf missing:', sum(x['source_as_of'] is None for x in out), '/ 12')
    for item in out:
        print(item['company'], item['sum'])


if __name__ == '__main__':
    main()
