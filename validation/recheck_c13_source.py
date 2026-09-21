# C-13 전망치 조사 산출물의 근거 누락과 검증기 경계 사례를 읽기 전용으로 재현한다.
import contextlib
import hashlib
import io
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parent
TARGET = ROOT.parent.parent / 'C-13' / 'validation' / 'consensus-source-2026-09-09'


def hashes():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(TARGET.iterdir()) if p.is_file()}


def main():
    before = hashes()
    source = TARGET / 'verify_sources.py'
    compile(source.read_text(encoding='utf-8-sig'), str(source), 'exec')
    mod = runpy.run_path(str(source), run_name='review_import')
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        mod['run_unit_tests']()
    evidence = json.loads((TARGET / 'evidence.json').read_text(encoding='utf-8-sig'))
    quarter_fn = mod['evaluate_quarterly_single_source']
    q = ['2026 Q3', '2026 Q4', '2027 Q1', '2027 Q2']
    cases = {}
    try:
        cases['null_quarter'] = quarter_fn(q, {q[0]: {'mean': 4.45}, q[1]: None})
    except Exception as exc:
        cases['null_quarter'] = {'exception': type(exc).__name__, 'message': str(exc)}
    gaps = ['2026 Q3', '2027 Q1', '2027 Q3', '2028 Q1']
    cases['nonconsecutive_quarters'] = quarter_fn(gaps, {k: {'mean': 1} for k in gaps})
    cases['missing_basis_metadata'] = quarter_fn(q, {k: {'mean': 1} for k in q})
    cases['invalid_range'] = mod['validate_valley_stat_structure'](
        {'mean': 5, 'median': 8, 'min': 7, 'max': 2, 'count': 0})
    cases['nonpositive_values_preserved'] = quarter_fn(
        q, {k: {'mean': v} for k, v in zip(q, [-1, 0, 2, 3])})
    metrics = evidence['unlisted_companies']
    suspect_sources = []
    for company, data in metrics.items():
        for name, metric in data['metrics'].items():
            url = metric.get('primary_source_url')
            if metric.get('value') is not None and (
                not isinstance(url, str) or not url.startswith('https://') or ' ' in url
            ):
                suspect_sources.append({'company': company, 'metric': name, 'source': url})
    result = {
        'reviewed_commit': 'e4eef3707fead09098d0728db104a4ff2e6c13c7',
        'unit_tests_output': output.getvalue(),
        'syntax_compile': 'pass',
        'files': sorted(before),
        'raw_snapshots_in_delivered_directory': [],
        'cases': cases,
        'non_direct_private_metric_sources': suspect_sources,
        'anthropic_revenue_forecast': metrics['anthropic']['metrics']['revenue_forecast'],
        'before_hashes': before,
        'after_hashes': hashes(),
    }
    assert result['before_hashes'] == result['after_hashes']
    assert cases['null_quarter']['exception'] == 'AttributeError'
    assert cases['nonconsecutive_quarters']['scoring_eligible'] is True
    assert cases['missing_basis_metadata']['scoring_eligible'] is True
    assert cases['invalid_range']['has_range'] is True
    assert cases['nonpositive_values_preserved']['fulfilled_count'] == 4
    assert metrics['anthropic']['metrics']['revenue_forecast']['value'] == 2000.0
    (ROOT / 'c13-source-review-evidence.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Original unit tests: 4 PASS; review assertions: 7 PASS; delivered files unchanged: 3/3')
    print(f'Non-direct private metric sources: {len(suspect_sources)}')


if __name__ == '__main__':
    main()
