"""v7-multi: v7 로직 + 다중 소스(KPC + ITPE 파이널라운드) 병합.
기출은 공통 1벌로 dedupe, 모의/합숙/파이널라운드는 학원별 source 태깅.
로컬 _posts 블로그 신호 사용. 결과: _data/exam_predict_140.json (top50 카드 후보).
사용: python3 scripts/exam_predictor_140.py [target_round]
"""
import xlrd, json, re, glob, os, sys
from collections import defaultdict, Counter
from datetime import date, timedelta
# v5는 __main__ 가드가 없어 import 시 백테스트(O(n^2))가 실행되므로,
# 순수 함수/상수 슬라이스만 exec해서 재사용한다 (모듈 하단 실행 회피).
_v5 = open('scripts/exam_predictor_v5.py', encoding='utf-8').read().split('\n')
_ns = {'re': re, 'date': date, 'defaultdict': defaultdict, 'Counter': Counter,
       'xlrd': xlrd, 'glob': glob, 'os': os, 'json': json}
exec('\n'.join(_v5[0:89]), _ns)     # STOPWORDS/패턴/extract_terms/round_to_date/parse_round
exec('\n'.join(_v5[205:244]), _ns)  # CAT_HINTS/classify_term/merge_similar
extract_terms = _ns['extract_terms']; round_to_date = _ns['round_to_date']
parse_round = _ns['parse_round']; classify_term = _ns['classify_term']
merge_similar = _ns['merge_similar']

FILES = [
    # (경로, 학원, [(시트, source)])  ※기출은 첫 파일에서만 로드(공통 dedupe)
    ('kpc_exam.xls', 'KPC', [('기출', 'past'), ('모의', 'mock'), ('합숙', 'camp')]),
    ('fr_exam.xls',  'ITPE', [('모의고사', 'mock'), ('파이널라운드', 'camp')]),
]

def infer_target(d):
    """캠프/파이널라운드 날짜 d 기준 '다음 시험 회차' 추정 (해당 시즌 대비)."""
    best = None
    for R in range(130, 151):
        rd = round_to_date(R)
        if rd >= d - timedelta(days=20):
            best = R; break
    return best

records = []
seen_past = set()
for path, academy, sheets in FILES:
    if not os.path.exists(path):
        print(f'  (없음) {path}'); continue
    wb = xlrd.open_workbook(path)
    for sn, source in sheets:
        try:
            sh = wb.sheet_by_name(sn)
        except Exception:
            continue
        n = 0
        for r in range(1, sh.nrows):
            round_v = sh.cell_value(r, 0)
            ptype = sh.cell_value(r, 2)
            q = sh.cell_value(r, 3)
            memo = sh.cell_value(r, 4) if sh.ncols > 4 else ''
            if not q or not round_v:
                continue
            meta = parse_round(round_v)
            if not meta:
                continue
            d = round_to_date(meta[1]) if meta[0] == 'round' else meta[1]
            # 기출 공통 dedupe
            if source == 'past':
                key = (str(round_v), str(ptype), str(q)[:40])
                if key in seen_past:
                    continue
                seen_past.add(key)
            try:
                ptype_i = int(ptype) if isinstance(ptype, float) else 0
            except Exception:
                ptype_i = 0
            target_round = None
            if source == 'camp':
                m = re.search(r'(\d{2,3})회', str(memo))
                if m:
                    target_round = int(m.group(1))
                else:
                    target_round = infer_target(d)  # 파이널라운드(memo 없음) 보완
            records.append({
                'source': source, 'academy': academy, 'date': d, 'meta': meta,
                'type': ptype_i, 'terms': extract_terms(q), 'target_round': target_round,
            })
            n += 1
        print(f'  [{academy}::{sn}] {n}행 로드 (source={source})')
print(f'총 레코드: {len(records)} (기출 dedupe 후)')

# 블로그 신호 (로컬)
blog_records = []
for path in glob.glob('_posts/*.md'):
    name = os.path.basename(path)
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})-(.+)\.md', name)
    if not m:
        continue
    d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    terms = extract_terms(m.group(4).replace('-', ' '))
    if terms:
        blog_records.append({'date': d, 'terms': terms})
print(f'블로그 레코드: {len(blog_records)}')

all_terms = Counter()
for r in records:
    for t in r['terms']:
        all_terms[t] += 1
# 소스가 2배로 늘었으므로 임계도 비례 상향(생성 단어 과필터 방지)
HIGH_FREQ = set(t for t, c in all_terms.items() if c > 450)

first_seen = {}
for r in records:
    for t in r['terms']:
        if t in HIGH_FREQ:
            continue
        if t not in first_seen or r['date'] < first_seen[t]:
            first_seen[t] = r['date']

CS_BASIC_POOL = [
    '가상메모리', '동기화', '뮤텍스', '세마포어', '모니터', '데드락', '교착상태',
    '은행가', '우선순위 역전', '페이징', '페이지 교체', '단편화',
    '소프트웨어 테스트', '화이트박스', '블랙박스', '경계값', '동등분할', '동등 분할',
    '맥케이브', '순환복잡도', '리팩토링', '코드스멜', '코드 스멜', '기술부채', '기술 부채',
    '무중단 배포', 'Blue-Green', 'Canary', '카나리',
    '서브네팅', '슈퍼네팅', 'VLSM', 'CIDR', 'OSPF',
    'WBS', '위험관리', 'PMBOK', '부정적 위험', '공공 SLA', 'SLA',
    '분산 데이터베이스', '투명성', '정규화', '데이터 레이크', '데이터 스웜프',
    '이진 탐색', '이진탐색', '라우팅 테이블', '엣지 컴퓨팅', '엣지컴퓨팅',
    '과적합', '과소적합', '이상치', '편향', '대수의 법칙', '중심극한정리',
]
TRENDY_NEW_POOL = [
    'Wi-Fi 7', 'WiFi 7', 'CTEM', 'TurboQuant', 'RAFT',
    'Advanced RAG', 'Modular RAG', 'sLLM', 'AI Act', '인공지능기본법',
    '데이터 자산화', '데이터 가치평가', 'VPP', '가상발전소',
    'AI Native', 'AI-Native', 'GNN', '강화학습',
    # 140 대비 2026 H2 신규 시사 보강
    'CNAPP', '컨피덴셜', '오픈웨이트', '소버린', '칩렛', 'eBPF', 'GPUOps',
    '월드모델', '피지컬 AI', '온디바이스', 'HBM', '디지털 트윈',
]
QUOTA_CARDS = {
    'AI데이터분석': 2, 'AI거버넌스': 1, '시스템구조': 3, '소프트웨어공학': 1,
    '정보보안': 1, 'IT경영': 1, '네트워크': 1, '데이터베이스': 0, '신기술융합': 0,
}
QUOTA_KEYWORDS = {
    'AI데이터분석': 8, 'AI거버넌스': 3, '시스템구조': 6, '소프트웨어공학': 4,
    '정보보안': 4, 'IT경영': 3, '네트워크': 3, '데이터베이스': 2, '신기술융합': 2,
}
W_SOURCE = {'past': 5.0, 'camp': 5.0, 'mock': 1.5}
W_TYPE = {1: 0.8, 2: 1.3, 0: 1.0}

# === 최근 출제 배제: 기술사는 직전 회차 토픽을 연속 출제하지 않음 ===
# 137~139회 관리 기출에 나온 용어를 회차별 감점(최근일수록 강하게).
def _tested_terms(rounds):
    wb = xlrd.open_workbook('kpc_exam.xls'); sh = wb.sheet_by_name('기출')
    m = {}
    for r in range(1, sh.nrows):
        rv = sh.cell_value(r, 0)
        if not isinstance(rv, float): continue
        R = int(rv)
        if R not in rounds: continue
        if str(sh.cell_value(r, 1)) != '관리': continue
        for t in extract_terms(sh.cell_value(r, 3)):
            m[t] = max(m.get(t, 0), R)   # 가장 최근 출제 회차 기록
    return m
RECENT_TESTED = _tested_terms({137, 138, 139})
RECENT_PENALTY = {139: 0.08, 138: 0.20, 137: 0.45}  # 최근일수록 강한 감점

def time_weight(target_date, rec_date):
    if rec_date >= target_date:
        return 0
    months = (target_date.year - rec_date.year) * 12 + (target_date.month - rec_date.month)
    if months <= 6: return 5.0
    if months <= 12: return 3.0
    if months <= 24: return 1.5
    return 0.5

def predict(target_round):
    target_date = round_to_date(target_round)
    score = defaultdict(float)
    r6 = defaultdict(int); r12 = defaultdict(int)
    prev_essay = set(); prev_short = set()
    for rec in records:
        if rec['meta'][0] == 'round' and rec['meta'][1] == target_round - 1:
            if rec['type'] == 2: prev_essay |= rec['terms']
            elif rec['type'] == 1: prev_short |= rec['terms']
    prev2_any = set()
    for rec in records:
        if rec['meta'][0] == 'round' and target_round - 3 <= rec['meta'][1] <= target_round - 2:
            prev2_any |= rec['terms']

    for rec in records:
        if rec['meta'][0] == 'round' and rec['meta'][1] >= target_round: continue
        if rec['date'] >= target_date: continue
        tw = time_weight(target_date, rec['date'])
        if tw == 0: continue
        bonus = 1.0
        if rec['source'] == 'camp' and rec['target_round'] == target_round:
            bonus = 1.5  # 해당 회차 대비 합숙/파이널라운드 강가중
        w = tw * W_SOURCE[rec['source']] * W_TYPE.get(rec['type'], 1.0) * bonus
        md = (target_date.year - rec['date'].year) * 12 + (target_date.month - rec['date'].month)
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
        mf = (target_date.year - fs.year) * 12 + (target_date.month - fs.month)
        if mf <= 12 and r6[t] >= 3: score[t] *= 3.5
        elif mf <= 24 and r12[t] >= 5: score[t] *= 1.8

    for t in list(score.keys()):
        if t in prev_essay: score[t] *= 0.3
        elif t in prev_short: score[t] *= 1.25
        if t in prev2_any: score[t] *= 0.85

    boosted = set()
    for kw in CS_BASIC_POOL:
        for t in list(score.keys()):
            if (kw in t or t in kw) and t not in boosted:
                score[t] *= 2.5; boosted.add(t)
    boosted2 = set()
    for kw in TRENDY_NEW_POOL:
        kl = kw.lower()
        for t in list(score.keys()):
            if (kl in t.lower() or t.lower() in kl) and t not in boosted2:
                score[t] *= 1.5; boosted2.add(t)

    # 최근 출제(137~139) 강한 감점 — 직전 회차 토픽 연속 출제 회피
    if target_round == 140:
        for t in list(score.keys()):
            R = RECENT_TESTED.get(t)
            if R:
                score[t] *= RECENT_PENALTY[R]
    return score

def pick_with_quota(score, quota, total):
    # merge_similar가 O(n^2)이므로 상위 점수 500개로 프루닝 후 병합 (상위 50만 필요)
    pruned = sorted(score.items(), key=lambda x: -x[1])[:500]
    items = merge_similar(pruned)
    by_cat = defaultdict(list)
    for t, s in items:
        c = classify_term(t)
        if c == '기타': continue
        by_cat[c].append((t, s))
    for c in by_cat: by_cat[c].sort(key=lambda x: -x[1])
    result, used = [], set()
    for c, q in quota.items():
        if q == 0: continue
        for t, s in by_cat.get(c, [])[:q]:
            if t in used: continue
            result.append((t, s)); used.add(t)
    if len(result) < total:
        rest = [(t, s) for t, s in items if t not in used and classify_term(t) != '기타']
        rest.sort(key=lambda x: -x[1])
        for t, s in rest[:total - len(result)]:
            result.append((t, s)); used.add(t)
    result.sort(key=lambda x: -x[1])
    return result[:total]

def actual_terms(T, subject_filter='관리'):
    wb = xlrd.open_workbook('kpc_exam.xls'); sh = wb.sheet_by_name('기출')
    a = set()
    for r in range(1, sh.nrows):
        if sh.cell_value(r, 0) != float(T): continue
        if subject_filter and str(sh.cell_value(r, 1)) != subject_filter: continue
        for t in extract_terms(sh.cell_value(r, 3)):
            if t not in HIGH_FREQ: a.add(t)
    return a

# 백테스트 (검증: v7과 동일 프로토콜, 다중소스)
print('\n=== v7-multi 백테스트 (Top-30, 정보관리) ===')
bt = []
for T in [135, 136, 137, 138, 139]:
    sc = predict(T)
    pred = [t for t, _ in pick_with_quota(sc, QUOTA_KEYWORDS, 30)]
    actual = actual_terms(T)
    hits = [t for t in pred if t in actual]
    val = [h for h in hits if len(h) >= 4 and classify_term(h) != '기타']
    print(f'  {T}회: 적중 {len(hits)}/30 ({len(hits)/30*100:.1f}%) 변별력 {len(val)} | {val[:12]}')
    bt.append({'round': T, 'hit_rate': len(hits) / 30, 'valuable': val})
avg = sum(r['hit_rate'] for r in bt) / len(bt)
print(f'  === 평균 적중률 {avg*100:.1f}% ===')

# 140 예측
TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 140
sc = predict(TARGET)
top50 = pick_with_quota(sc, QUOTA_KEYWORDS, 50)
out = {
    'target_round': TARGET,
    'predicted_date': str(date.today()),
    'algorithm': 'v7-multi (KPC+ITPE)',
    'backtest_avg_hit': round(avg, 4),
    'sources': ['KPC기출(공통)', 'KPC모의', 'KPC합숙', 'ITPE모의고사', 'ITPE파이널라운드', '블로그시사'],
    'top50': [{'rank': i + 1, 'keyword': t, 'category': classify_term(t), 'score': round(s, 2)}
              for i, (t, s) in enumerate(top50)],
}
with open('_data/exam_predict_140.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(f'\n=== {TARGET}회 카드 후보 Top-10 (카테고리 쿼터 적용) ===')
for i, (t, s) in enumerate(pick_with_quota(sc, QUOTA_CARDS, 10), 1):
    print(f'  {i:2}. [{classify_term(t)}] {t} ({s:.1f})')
print(f'\n=== {TARGET}회 top50 상위 25 (쿼터 미적용, 순수 점수순) ===')
for c in out['top50'][:25]:
    print(f"  {c['rank']:2}. [{c['category']}] {c['keyword']} ({c['score']})")
print('\n_data/exam_predict_140.json 저장 완료')
