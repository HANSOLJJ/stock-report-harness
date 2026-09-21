# Anthropic 및 OpenAI 원자료 수집 및 _raw 보존 스크립트
import os
import json
import urllib.request
import sys

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

raw_dir = os.path.join(os.path.dirname(__file__), '_raw')
os.makedirs(raw_dir, exist_ok=True)

def fetch_and_save(url, filename, is_binary=False):
    target = os.path.join(raw_dir, filename)
    print(f"Fetching {url} -> {target}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            content = resp.read()
            if is_binary:
                with open(target, 'wb') as f:
                    f.write(content)
            else:
                with open(target, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(content.decode('utf-8', errors='ignore'))
            print(f"  Saved {len(content)} bytes.")
    except Exception as e:
        print(f"  Error fetching {url}: {e}")

def save_baseline_slices():
    # 1. observations.json slice
    obs_path = os.path.join('..', 'worker', 'scorecard', 'baseline', 'v1.5', 'observations.json')
    if os.path.exists(obs_path):
        with open(obs_path, 'r', encoding='utf-8') as f:
            obs = json.load(f)
        slice_items = [it for it in obs.get('items', []) if it.get('company_id') in ['anthropic', 'openai']]
        out_path = os.path.join(raw_dir, 'baseline_v15_unlisted_observations.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'schema': obs.get('schema'), 'run_id': obs.get('run_id'), 'as_of': obs.get('as_of'), 'items': slice_items}, f, indent=2, ensure_ascii=False)
        print(f"Saved baseline observations slice ({len(slice_items)} items) -> {out_path}")

    # 2. scores.json slice
    sc_path = os.path.join('..', 'worker', 'scorecard', 'baseline', 'v1.5', 'scores.json')
    if os.path.exists(sc_path):
        with open(sc_path, 'r', encoding='utf-8') as f:
            sc = json.load(f)
        slice_comps = [c for c in sc.get('companies', []) if c.get('company_id') in ['anthropic', 'openai']]
        out_path = os.path.join(raw_dir, 'baseline_v15_unlisted_scores.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'schema': sc.get('schema'), 'baseline_id': sc.get('baseline_id'), 'as_of': sc.get('as_of'), 'companies': slice_comps}, f, indent=2, ensure_ascii=False)
        print(f"Saved baseline scores slice ({len(slice_comps)} companies) -> {out_path}")

if __name__ == '__main__':
    # Robots.txt
    fetch_and_save('https://www.anthropic.com/robots.txt', 'anthropic_robots.txt')
    fetch_and_save('https://openai.com/robots.txt', 'openai_robots.txt')

    # Terms of Service
    fetch_and_save('https://www.anthropic.com/legal/commercial-terms', 'anthropic_commercial_terms.html')
    fetch_and_save('https://openai.com/policies/terms-of-use/', 'openai_terms_of_use.html')

    # Official Announcements
    fetch_and_save('https://www.anthropic.com/news/series-h', 'anthropic_series_h_official_2026-05-28.html')
    fetch_and_save('https://openai.com/index/accelerating-the-next-phase-ai/', 'openai_accelerating_official_2026-03-31.html')

    # Baseline slices
    save_baseline_slices()
