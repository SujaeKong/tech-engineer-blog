"""v6: v5 + 출제진(합숙) 가중치 강화 + per_cat 확장 + 합숙 메타데이터 활용"""
import xlrd, json, re, glob, os
from collections import defaultdict, Counter
from datetime import date

# v5에서 공통 부분 import
import sys
sys.path.insert(0, '.')
from v5_predictor import (extract_terms, round_to_date, parse_round, CAT_HINTS,
                          STOPWORDS, classify_term, merge_similar, HANGUL_PATTERN,
                          ENG_PATTERN, MIXED_PATTERN, strip_josa)

WB = xlrd.open_workbook('kpc_exam.xls')

# === 데이터 로드 + 합숙 메타데이터 분석 ===
records = []
camp_round_map = {}  # 합숙 그룹 → 대비 회차 (E열에서 추출)
for sheet_name, source in [('기출', 'past'), ('모의', 'mock'), ('합숙', 'camp')]:
    sh = WB.sheet_by_name(sheet_name)
    for r in range(1, sh.nrows):
        round_v = sh.cell_value(r, 0)
        ptype = sh.cell_value(r, 2)
        q = sh.cell_value(r, 3)
        memo = sh.cell_value(r, 4) if sh.ncols > 4 else ''
        if not q or not round_v: continue
        meta = parse_round(round_v)
        if not meta: continue
        d = round_to_date(meta[1]) if meta[0]=='round' else meta[1]
        try: ptype_i = int(ptype) if isinstance(ptype, float) else 0
        except: ptype_i = 0

        # 합숙 메타에서 회차 대비 정보 추출
        target_round = None
        if source == 'camp' and memo:
            m = re.search(r'(\d{2,3})회', str(memo))
            if m:
                target_round = int(m.group(1))
                camp_round_map[str(round_v)] = target_round

        records.append({
            'source': source, 'date': d, 'meta': meta, 'type': ptype_i,
            'terms': extract_terms(q), 'target_round': target_round
        })

print(f'레코드: {len(records)}, 합숙→회차 매핑: {len(camp_round_map)}')

# === 블로그 신호 ===
blog_records = []
for path in glob.glob('/Users/sujaekong/tech-engineer-blog/_posts/*.md'):
    name = os.path.basename(path)
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})-(.+)\.md', name)
    if not m: continue
    d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    title = m.group(4).replace('-', ' ')
    terms = extract_terms(title)
    if terms: blog_records.append({'date': d, 'terms': terms})

all_terms = Counter()
for r in records:
    for t in r['terms']: all_terms[t] += 1
HIGH_FREQ = set(t for t, c in all_terms.items() if c > 300)

first_seen = {}
for r in records:
    for t in r['terms']:
        if t in HIGH_FREQ: continue
        if t not in first_seen or r['date'] < first_seen[t]:
            first_seen[t] = r['date']

# === v6 가중치 강화 ===
W_SOURCE = {'past': 5.0, 'camp': 5.0, 'mock': 1.5}  # 합숙 ×5 (출제진 작성)
W_TYPE = {1: 0.8, 2: 1.3, 0: 1.0}

def time_weight(target_date, rec_date):
    if rec_date >= target_date: return 0
    months = (target_date.year - rec_date.year)*12 + (target_date.month - rec_date.month)
    if months <= 6: return 5.0  # 최근 6mo 더 강화
    if months <= 12: return 3.0
    if months <= 24: return 1.5
    return 0.5

def predict_v6(target_round):
    target_date = round_to_date(target_round)
    score = defaultdict(float)
    r6 = defaultdict(int); r12 = defaultdict(int)
    prev_essay = set(); prev_short = set()
    for rec in records:
        if rec['meta'][0]=='round' and rec['meta'][1]==target_round-1:
            if rec['type'] == 2: prev_essay |= rec['terms']
            elif rec['type'] == 1: prev_short |= rec['terms']
    prev2_any = set()
    for rec in records:
        if rec['meta'][0]=='round' and target_round-3 <= rec['meta'][1] <= target_round-2:
            prev2_any |= rec['terms']

    for rec in records:
        if rec['meta'][0]=='round' and rec['meta'][1]>=target_round: continue
        if rec['date']>=target_date: continue
        tw = time_weight(target_date, rec['date'])
        if tw == 0: continue
        # 합숙 메타 회차 보너스: 'N회 대비'인 합숙은 N-1, N 시점에 출제 직전이라 가치↑
        bonus = 1.0
        if rec['source']=='camp' and rec['target_round']:
            if rec['target_round'] == target_round:
                bonus = 1.5  # 정확히 target_round 대비면 +50%
        w = tw * W_SOURCE[rec['source']] * W_TYPE.get(rec['type'], 1.0) * bonus
        md = (target_date.year-rec['date'].year)*12 + (target_date.month-rec['date'].month)
        for t in rec['terms']:
            if t in HIGH_FREQ: continue
            score[t] += w
            if md <= 6: r6[t] += 1
            if md <= 12: r12[t] += 1

    # 블로그
    for rec in blog_records:
        if rec['date'] >= target_date: continue
        tw = time_weight(target_date, rec['date'])
        if tw == 0: continue
        for t in rec['terms']:
            if t in HIGH_FREQ: continue
            if t in score:
                score[t] += 2.0 * tw  # 블로그 가중↑

    # 신생 보너스 강화
    for t in list(score.keys()):
        fs = first_seen.get(t)
        if fs is None: continue
        mf = (target_date.year-fs.year)*12 + (target_date.month-fs.month)
        if mf <= 12 and r6[t] >= 3: score[t] *= 3.5  # 신생 ×3.5
        elif mf <= 24 and r12[t] >= 5: score[t] *= 1.8

    # 직전 출제 디스카운트
    for t in list(score.keys()):
        if t in prev_essay: score[t] *= 0.3
        elif t in prev_short: score[t] *= 0.7
        if t in prev2_any: score[t] *= 0.85

    return score

def pick_balanced(score, n=30, per_cat=8):
    items = list(score.items())
    items = merge_similar(items)
    by_cat = defaultdict(list)
    for t, s in items:
        by_cat[classify_term(t)].append((t, s))
    for c in by_cat: by_cat[c].sort(key=lambda x: -x[1])
    result = []
    for c, lst in by_cat.items():
        if c == '기타': continue
        result.extend(lst[:per_cat])
    result.sort(key=lambda x: -x[1])
    return result[:n]

def actual_terms(T):
    sh = WB.sheet_by_name('기출')
    a = set()
    for r in range(1, sh.nrows):
        if sh.cell_value(r,0) == float(T):
            for t in extract_terms(sh.cell_value(r,3)):
                if t not in HIGH_FREQ: a.add(t)
    return a

print('\n=== v6 백테스트 ===')
results = []
for T in [135, 136, 137, 138]:
    score = predict_v6(T)
    top = pick_balanced(score, n=30, per_cat=8)
    pred = [t for t,_ in top]
    actual = actual_terms(T)
    hits = [t for t in pred if t in actual]
    valuable = [h for h in hits if len(h) >= 4 and classify_term(h) != '기타']
    print(f'\n--- {T}회 ---')
    print(f'  적중: {len(hits)}/30 ({len(hits)/30*100:.1f}%) / 변별력: {len(valuable)}')
    print(f'  변별력: {valuable[:25]}')
    print(f'  예측 TOP10: {pred[:10]}')
    results.append({'round': T, 'hit_rate': len(hits)/30, 'valuable': valuable, 'pred': pred})

avg = sum(r['hit_rate'] for r in results) / len(results)
avg_val = sum(len(r['valuable']) for r in results) / len(results)
print(f'\n=== v6 적중률: {avg*100:.1f}% / 변별력 {avg_val:.1f}/30 ===')
print('비교: v4 변별력 4.0 / v5 변별력 4.0 / v6 목표 >4')

with open('predictor_v6_result.json','w',encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
