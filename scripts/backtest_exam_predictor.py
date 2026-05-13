import xlrd, json, re
from collections import defaultdict

# 핫 키워드 화이트리스트 import
import sys
sys.path.insert(0, '.')
from integrated_trend2 import HOT_KEYWORDS, parse_round

ALL_HOT = []
for cat, kws in HOT_KEYWORDS.items():
    for kw in kws:
        ALL_HOT.append((cat, kw))

def classify(q):
    return [(cat, kw) for cat, kw in ALL_HOT if kw in q]

WB = xlrd.open_workbook('kpc_exam.xls')

# === 회차 → 시험 시점 매핑 (138=2026.02 기준 역산) ===
def round_to_yearmonth(rnd):
    # 138 = 2026.02 (Feb), 137=2025.11, 136=2025.08, 135=2025.05, 134=2025.02
    # 회차마다 분기씩 역행. 138 → diff=0 → 2026.02
    months = [2, 11, 8, 5]  # diff %4
    diff = 138 - rnd
    month = months[diff % 4]
    year = 2026 - (diff // 4) - (1 if (diff % 4) > 0 else 0)
    # 보정: 138→(0,0)→2026.02, 137→(1,1)→2025.11, 138-(4)=134→2025.02 OK
    return (year, month)

# 검증
for r in [134, 135, 136, 137, 138]:
    print(f'{r}회 → {round_to_yearmonth(r)}')

# === 데이터 로드 ===
records = []
for sheet_name, source in [('기출', 'past'), ('모의', 'mock'), ('합숙', 'camp')]:
    sh = WB.sheet_by_name(sheet_name)
    for r in range(1, sh.nrows):
        round_v = sh.cell_value(r, 0)
        q = sh.cell_value(r, 3)
        if not q or not round_v: continue
        meta = parse_round(round_v)
        records.append({'source': source, 'meta': meta, 'q': q})

# === 백테스트: 회차 T 예측 ===
def predict_for_round(T, top_n=30):
    """T 회차 시험 직전 시점의 데이터로 예측"""
    test_year, test_month = round_to_yearmonth(T)
    # T 시험일 이전 데이터만
    available = []
    for rec in records:
        if rec['meta'][0] == 'round':
            if rec['meta'][1] < T:  # 이전 기출만
                available.append(rec)
        elif rec['meta'][0] == 'group':
            y, m = rec['meta'][1], rec['meta'][2]
            if (y, m) < (test_year, test_month):
                available.append(rec)

    # 점수
    W_SOURCE = {'past': 5.0, 'camp': 3.0, 'mock': 2.0}
    W_RECENT = 1.5
    def is_recent_for(rec, T):
        if rec['meta'][0] == 'round': return rec['meta'][1] >= (T - 9)
        if rec['meta'][0] == 'group':
            return (rec['meta'][1], rec['meta'][2]) >= (test_year - 2, test_month)
        return False
    kw_score = defaultdict(float)
    for rec in available:
        w = W_SOURCE[rec['source']]
        if is_recent_for(rec, T): w *= W_RECENT
        seen = set()
        for cat, kw in classify(rec['q']):
            if kw in seen: continue
            seen.add(kw)
            kw_score[kw] += w
    return sorted(kw_score.items(), key=lambda x: -x[1])[:top_n]

def actual_keywords(T):
    """T 회차에 실제 출제된 키워드"""
    sh = WB.sheet_by_name('기출')
    actual = set()
    for r in range(1, sh.nrows):
        if sh.cell_value(r,0) == float(T):
            q = sh.cell_value(r,3)
            for cat, kw in classify(q):
                actual.add(kw)
    return actual

# === 백테스트 실행 ===
results = []
for T in [135, 136, 137, 138]:
    pred = predict_for_round(T, top_n=30)
    actual = actual_keywords(T)
    pred_kws = [kw for kw, _ in pred]
    hits = [kw for kw in pred_kws if kw in actual]
    print(f'\n=== {T}회 백테스트 ===')
    print(f'  실제 출제 핫키워드: {len(actual)}개')
    print(f'  예측 TOP 30 중 적중: {len(hits)}개 ({len(hits)/30*100:.1f}%)')
    print(f'  적중 키워드: {hits[:20]}')
    missed_top10 = [kw for kw in pred_kws[:10] if kw not in actual]
    print(f'  TOP10 빗나간 것: {missed_top10}')
    # 미발견 핫(실제 출제 - 예측 외)
    missed_real = [kw for kw in actual if kw not in pred_kws]
    print(f'  실제 출제됐는데 예측 못함: {missed_real[:15]}')
    results.append({
        'round': T,
        'pred_top30': pred_kws,
        'actual_hot': sorted(list(actual)),
        'hits': hits,
        'hit_rate': len(hits)/30,
    })

# 평균 적중률
avg = sum(r['hit_rate'] for r in results) / len(results)
print(f'\n=== 평균 TOP 30 적중률: {avg*100:.1f}% ===')

# 랜덤 기준선 (전체 HOT 키워드 중 30개 무작위 선택 시 기댓값)
total_kw = len(set(kw for _, kw in ALL_HOT))
avg_actual = sum(len(actual_keywords(t)) for t in [135,136,137,138]) / 4
random_baseline = avg_actual / total_kw * 30
print(f'랜덤 기준선 TOP 30 기댓값: {random_baseline:.1f}개 ({random_baseline/30*100:.1f}%)')

with open('backtest_result.json','w',encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('저장: /tmp/backtest_result.json')
