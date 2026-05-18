"""v7: v6 + 카테고리 쿼터 강제 + CS 기본기 후보풀 + N-1 단답 통합 부스트 + 시사 신규 부스트 + 종목 필터"""
import xlrd, json, re, glob, os
from collections import defaultdict, Counter
from datetime import date
import sys
sys.path.insert(0, 'scripts')
from exam_predictor_v5 import (extract_terms, round_to_date, parse_round, CAT_HINTS,
                                STOPWORDS, classify_term, merge_similar)

WB = xlrd.open_workbook('kpc_exam.xls')

records = []
camp_round_map = {}
for sheet_name, source in [('기출', 'past'), ('모의', 'mock'), ('합숙', 'camp')]:
    sh = WB.sheet_by_name(sheet_name)
    for r in range(1, sh.nrows):
        round_v = sh.cell_value(r, 0)
        ptype_v = sh.cell_value(r, 1)  # 종목 (관리/응용)
        kyo = sh.cell_value(r, 2)
        q = sh.cell_value(r, 3)
        memo = sh.cell_value(r, 4) if sh.ncols > 4 else ''
        if not q or not round_v: continue
        meta = parse_round(round_v)
        if not meta: continue
        d = round_to_date(meta[1]) if meta[0]=='round' else meta[1]
        try: kyo_i = int(kyo) if isinstance(kyo, float) else 0
        except: kyo_i = 0
        target_round = None
        if source == 'camp' and memo:
            m = re.search(r'(\d{2,3})회', str(memo))
            if m:
                target_round = int(m.group(1))
                camp_round_map[str(round_v)] = target_round
        records.append({
            'source': source, 'date': d, 'meta': meta,
            'type': kyo_i, 'subject': str(ptype_v) if ptype_v else '',
            'terms': extract_terms(q), 'target_round': target_round,
        })
print(f'레코드: {len(records)}, 합숙→회차 매핑: {len(camp_round_map)}')

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

# === v7 신규: CS 기본기 영구 후보풀 ===
CS_BASIC_POOL = [
    '가상메모리', '동기화', '뮤텍스', '세마포어', '모니터', '데드락', '교착상태',
    '은행가', '우선순위 역전', '페이징', '페이지 교체', '단편화',
    '소프트웨어 테스트', '화이트박스', '블랙박스', '경계값', '동등분할', '동등 분할',
    '맥케이브', '순환복잡도', '리팩토링', '코드스멜', '코드 스멜', '기술부채', '기술 부채',
    '무중단 배포', 'Blue-Green', 'Canary', '카나리',
    '서브네팅', '슈퍼네팅', 'VLSM', 'CIDR', 'OSPF',
    'WBS', '위험관리', 'PMBOK', '부정적 위험', '공공 SLA', 'SLA',
    '분산 데이터베이스', '투명성', '정규화', '데이터 레이크', '데이터 스웜프',
    '이진 탐색', '이진탐색', '라우팅 테이블',
    '엣지 컴퓨팅', '엣지컴퓨팅',
    '과적합', '과소적합', '이상치', '편향',
    '대수의 법칙', '중심극한정리',
]

# === v7 신규: 시사 신규 키워드 후보풀 (출제 이력 0이어도 부스트) ===
TRENDY_NEW_POOL = [
    'Wi-Fi 7', 'WiFi 7', 'CTEM', 'TurboQuant', 'RAFT',
    'Advanced RAG', 'Modular RAG', 'sLLM', 'AI Act', '인공지능기본법',
    '데이터 자산화', '데이터 가치평가', 'VPP', '가상발전소',
    'AI Native', 'AI-Native', 'GNN', '강화학습',
]

# === v7 신규: 카테고리 쿼터 (Top-10 카드 슬롯) ===
QUOTA_CARDS = {
    'AI데이터분석': 2,
    'AI거버넌스': 1,
    '시스템구조': 3,    # OS 통합 카드 슬롯 확보 (동기화/데드락/가상메모리)
    '소프트웨어공학': 1,
    '정보보안': 1,
    'IT경영': 1,
    '네트워크': 1,
    '데이터베이스': 0,
    '신기술융합': 0,
}
QUOTA_KEYWORDS = {
    'AI데이터분석': 8,
    'AI거버넌스': 3,
    '시스템구조': 6,
    '소프트웨어공학': 4,
    '정보보안': 4,
    'IT경영': 3,
    '네트워크': 3,
    '데이터베이스': 2,
    '신기술융합': 2,
}

W_SOURCE = {'past': 5.0, 'camp': 5.0, 'mock': 1.5}
W_TYPE = {1: 0.8, 2: 1.3, 0: 1.0}

def time_weight(target_date, rec_date):
    if rec_date >= target_date: return 0
    months = (target_date.year - rec_date.year)*12 + (target_date.month - rec_date.month)
    if months <= 6: return 5.0
    if months <= 12: return 3.0
    if months <= 24: return 1.5
    return 0.5

def predict_v7(target_round):
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
        bonus = 1.0
        if rec['source']=='camp' and rec['target_round']:
            if rec['target_round'] == target_round:
                bonus = 1.5
        w = tw * W_SOURCE[rec['source']] * W_TYPE.get(rec['type'], 1.0) * bonus
        md = (target_date.year-rec['date'].year)*12 + (target_date.month-rec['date'].month)
        for t in rec['terms']:
            if t in HIGH_FREQ: continue
            score[t] += w
            if md <= 6: r6[t] += 1
            if md <= 12: r12[t] += 1

    for rec in blog_records:
        if rec['date'] >= target_date: continue
        tw = time_weight(target_date, rec['date'])
        if tw == 0: continue
        for t in rec['terms']:
            if t in HIGH_FREQ: continue
            if t in score:
                score[t] += 2.0 * tw

    for t in list(score.keys()):
        fs = first_seen.get(t)
        if fs is None: continue
        mf = (target_date.year-fs.year)*12 + (target_date.month-fs.month)
        if mf <= 12 and r6[t] >= 3: score[t] *= 3.5
        elif mf <= 24 and r12[t] >= 5: score[t] *= 1.8

    # v6: 디스카운트만 / v7: 단답은 통합 논술 부스트로 전환
    for t in list(score.keys()):
        if t in prev_essay: score[t] *= 0.3
        elif t in prev_short: score[t] *= 1.25  # v6는 0.7 디스카운트 → v7은 부스트
        if t in prev2_any: score[t] *= 0.85

    # v7 신규: CS 기본기 후보풀 부스트 (1.5 → 2.5로 강화)
    boosted_cs = set()
    for kw in CS_BASIC_POOL:
        for t in list(score.keys()):
            if kw in t or t in kw:
                if t not in boosted_cs:
                    score[t] *= 2.5
                    boosted_cs.add(t)

    # v7 신규: 시사 신규 키워드 부스트 (출제 이력 0인 신규 키워드 보강)
    boosted_new = set()
    for kw in TRENDY_NEW_POOL:
        kw_low = kw.lower()
        for t in list(score.keys()):
            if kw_low in t.lower() or t.lower() in kw_low:
                if t not in boosted_new:
                    score[t] *= 1.5
                    boosted_new.add(t)

    return score

def pick_with_quota(score, quota, total):
    items = list(score.items())
    items = merge_similar(items)
    by_cat = defaultdict(list)
    for t, s in items:
        c = classify_term(t)
        if c == '기타': continue
        by_cat[c].append((t, s))
    for c in by_cat: by_cat[c].sort(key=lambda x: -x[1])

    result = []
    used = set()
    for c, q in quota.items():
        if q == 0: continue
        for t, s in by_cat.get(c, [])[:q]:
            if t in used: continue
            result.append((t, s))
            used.add(t)

    if len(result) < total:
        rest = [(t, s) for t, s in items if t not in used and classify_term(t) != '기타']
        rest.sort(key=lambda x: -x[1])
        for t, s in rest[:total - len(result)]:
            result.append((t, s))
            used.add(t)

    result.sort(key=lambda x: -x[1])
    return result[:total]

def actual_terms(T, subject_filter=None):
    sh = WB.sheet_by_name('기출')
    a = set()
    for r in range(1, sh.nrows):
        if sh.cell_value(r,0) != float(T): continue
        if subject_filter and str(sh.cell_value(r,1)) != subject_filter: continue
        for t in extract_terms(sh.cell_value(r,3)):
            if t not in HIGH_FREQ: a.add(t)
    return a

print('\n=== v7 백테스트 (Top-30 키워드, 정보관리 종목만) ===')
results = []
for T in [135, 136, 137, 138, 139]:
    score = predict_v7(T)
    top = pick_with_quota(score, QUOTA_KEYWORDS, total=30)
    pred = [t for t,_ in top]
    actual = actual_terms(T, subject_filter='관리')
    hits = [t for t in pred if t in actual]
    valuable = [h for h in hits if len(h) >= 4 and classify_term(h) != '기타']
    print(f'\n--- {T}회 (관리) ---')
    print(f'  적중: {len(hits)}/30 ({len(hits)/30*100:.1f}%) / 변별력: {len(valuable)}')
    print(f'  변별력: {valuable[:20]}')
    print(f'  예측 TOP10: {pred[:10]}')
    results.append({'round': T, 'hit_rate': len(hits)/30, 'valuable': valuable, 'pred': pred})

avg = sum(r['hit_rate'] for r in results) / len(results)
avg_val = sum(len(r['valuable']) for r in results) / len(results)
print(f'\n=== v7 평균 적중률: {avg*100:.1f}% / 변별력 {avg_val:.1f}/30 ===')

print('\n=== v7 카드 후보 Top-10 (139회 기준) ===')
score139 = predict_v7(139)
cards = pick_with_quota(score139, QUOTA_CARDS, total=10)
for i, (t, s) in enumerate(cards, 1):
    print(f'  {i}. [{classify_term(t)}] {t} ({s:.2f})')

with open('_data/predictor_v7_result.json','w',encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
