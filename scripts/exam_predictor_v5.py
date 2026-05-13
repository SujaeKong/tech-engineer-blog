"""v5: v4 + 블로그 신호 + 유형 가중치 + 직전 디스카운트 + 유사 머지 + 분류 보강"""
import xlrd, json, re, glob, os
from collections import defaultdict, Counter
from datetime import date

WB = xlrd.open_workbook('kpc_exam.xls')

STOPWORDS = {
    '정보','시스템','관리','데이터','기술','서비스','방법','절차','개념','정의','다음','설명','사항',
    '활용','구성','요소','특징','종류','기능','적용','분석','모델','기반','환경','통한','위한','대한',
    '비교','차이점','장단점','장점','단점','사례','내용','문제','구분','형태','수행','이용','제공',
    '기존','신규','관련','등을','등의','등에','등이','등과','사용','구현','목적','대상','대해','대하여',
    '소프트웨어','하드웨어','네트워크','보안','품질','테스트','프로젝트','컴퓨터','컴퓨팅','컴퓨','인터넷',
    '운영','개발','설계','구축','분석','평가','측정','지표','범위','효과','효율','성능','속성','구조',
    '기관','기업','조직','국가','한국','국내','국외','기준','지침','규정','법령','제도','정책','전략',
    '계획','수립','체계','체제','방안','대응','검토','지원','수준','단계','과정','학습','이해','진행',
    '시점','상태','상황','요구','조건','종류','구분','순서','단위','용어','용도','용량','범주','분류',
    '주요','일반','특별','전체','부분','외부','내부','중심','기본','기초','고급','상위','하위','중간',
    '대규모','대형','소형','중소','중요','새로운','효과적','효율적','전문','전문가','참여','참조',
    '입력','출력','전송','수신','발신','처리','저장','관리','연계','연동','연결','구간','노드','링크',
    'AI','IT','SW','HW','DB','ML','DL','API','OS','GPU','CPU','UI','UX','RPA',
    'Data','Model','System','Service','Cloud','Smart','Digital','Network','Information','Architecture',
    '인공지능','클라우드','디지털','메모리','프로토콜','플랫폼','거버넌스','감리','통신',
    '운영체제','데이터베이스','개인정보','요구사항','블록체인','컨테이너','쿠버네티스','애자일',
    '암호','암호화','패턴','제어','분산','이중화','이중','시각화','시뮬레이션',
    '학습','훈련','추론','예측','탐지','감지','인식','검증','검출','평가','측정','지표','기준',
    '아키텍처','아키텍쳐','프레임워크','모듈','패키지','라이브러리','컴포넌트','인터페이스',
    '취약점','대응책','대응 책','보안 강화','보안 위협','위협 요소',
    '빅데이터','IoT','PMO','BCP','UML','REST','SOA','블루그린','카나리','REDO','UNDO','체크포인트',
    '격리','정규형','정규화','반정규화','회복','트랜잭션','SQL','NoSQL','인덱스','오류','혼잡',
    '머신러닝','딥러닝','지능형','정보화','정보처리','정보보호',
    '거래','산업','상품','제품','마케팅','경영','경영전략','경영자','관리자','매니저',
    '프로세스','프로세서','파이프라인','파이프','데이터처리','데이터 처리','데이터 분석',
    'B-Tree','B+Tree','MMU','TLB','DMA','PoE','HDLC','SDH','PDH','IDS','IPS','SOC','SIEM','DNS',
    '머신','딥','심층','신경','신경망','텐서','벡터','벡터화','임베딩','드론','로봇',
    '안전','안정','신뢰','신뢰성','가용성','확장성','유연성','경량','경량화',
}

HANGUL_PATTERN = re.compile(r'[가-힣]{2,10}')
ENG_PATTERN = re.compile(r'\b[A-Z][A-Za-z0-9\-\./]{2,30}|\b[A-Z]{3,10}\b')
MIXED_PATTERN = re.compile(r'[A-Z][A-Za-z]*[가-힣]{2,8}|[가-힣]{2,8}[A-Z][A-Za-z]*')
JOSA = '은는이가을를에서의로와과한할하여하고하며부터까지에게도조차마저'

def strip_josa(w):
    if len(w) > 3 and w[-1] in JOSA:
        return w[:-1]
    return w

def extract_terms(text):
    terms = set()
    for m in HANGUL_PATTERN.findall(text):
        m = strip_josa(m)
        if m in STOPWORDS: continue
        if len(m) >= 4: terms.add(m)
    hangul_seqs = re.findall(r'[가-힣]{2,}(?:\s+[가-힣]{2,}){1,2}', text)
    for seq in hangul_seqs:
        parts = [strip_josa(p) for p in seq.split()]
        if not all(p in STOPWORDS for p in parts[:2]):
            bigram = ' '.join(parts[:2])
            if 4 < len(bigram) <= 25 and bigram not in STOPWORDS:
                terms.add(bigram)
            if len(parts) >= 3:
                trigram = ' '.join(parts[:3])
                if 6 < len(trigram) <= 30 and trigram not in STOPWORDS:
                    terms.add(trigram)
    for m in ENG_PATTERN.findall(text):
        if len(m) >= 3 and m.upper() not in {'AND','THE','FOR','WITH','THIS','THAT'} and m not in STOPWORDS:
            terms.add(m)
    for m in MIXED_PATTERN.findall(text):
        if m not in STOPWORDS:
            terms.add(m)
    return terms

def round_to_date(rnd):
    months = [2, 11, 8, 5]
    diff = 138 - rnd
    month = months[diff % 4]
    year = 2026 - (diff // 4) - (1 if (diff % 4) > 0 else 0)
    return date(year, month, 15)

def parse_round(s):
    s = str(s)
    m = re.search(r'(\d{4})\.(\d{1,2})', s)
    if m:
        return ('group', date(int(m.group(1)), int(m.group(2)), 15))
    try:
        return ('round', int(float(s)))
    except: return None

# === 데이터 로드 ===
print('xls 로드...')
records = []
for sheet_name, source in [('기출', 'past'), ('모의', 'mock'), ('합숙', 'camp')]:
    sh = WB.sheet_by_name(sheet_name)
    for r in range(1, sh.nrows):
        round_v = sh.cell_value(r, 0)
        ptype = sh.cell_value(r, 2)
        q = sh.cell_value(r, 3)
        if not q or not round_v: continue
        meta = parse_round(round_v)
        if not meta: continue
        d = round_to_date(meta[1]) if meta[0]=='round' else meta[1]
        # type: 1=단답, 2=논술 (기출), 모의/합숙은 다양
        try:
            ptype_i = int(ptype) if ptype else 0
        except:
            ptype_i = 0
        records.append({'source': source, 'date': d, 'meta': meta, 'type': ptype_i, 'terms': extract_terms(q)})
print(f'xls 레코드: {len(records)}')

# === 블로그 포스트 신호 ===
print('블로그 포스트 신호 추출...')
blog_records = []
post_files = glob.glob('/Users/sujaekong/tech-engineer-blog/_posts/*.md')
for path in post_files:
    name = os.path.basename(path)
    # 2026-05-13-제목.md
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})-(.+)\.md', name)
    if not m: continue
    d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    title = m.group(4).replace('-', ' ')
    terms = extract_terms(title)
    if terms:
        blog_records.append({'date': d, 'terms': terms})
print(f'블로그 레코드: {len(blog_records)}')

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

# === 가중치 ===
W_SOURCE = {'past': 5.0, 'camp': 3.0, 'mock': 2.0}
W_TYPE = {1: 0.8, 2: 1.3, 0: 1.0}  # 논술이 더 중요 (25점)
W_BLOG_PER_HIT = 1.5  # 블로그 등장 1회당 가산

def time_weight(target_date, rec_date):
    if rec_date >= target_date: return 0
    months = (target_date.year - rec_date.year)*12 + (target_date.month - rec_date.month)
    if months <= 6: return 4.0
    if months <= 12: return 2.5
    if months <= 24: return 1.5
    return 0.8

def predict_v5(target_round):
    target_date = round_to_date(target_round)
    score = defaultdict(float)
    r6 = defaultdict(int); r12 = defaultdict(int)
    # 직전 회차 출제 키워드
    prev_round_essay = set()  # 직전 회차 논술(유형 2)
    prev_round_short = set()  # 직전 회차 단답(유형 1)
    for rec in records:
        if rec['meta'][0]=='round' and rec['meta'][1]==target_round-1:
            if rec['type'] == 2:
                prev_round_essay |= rec['terms']
            elif rec['type'] == 1:
                prev_round_short |= rec['terms']

    for rec in records:
        if rec['meta'][0]=='round' and rec['meta'][1]>=target_round: continue
        if rec['date']>=target_date: continue
        tw = time_weight(target_date, rec['date'])
        if tw == 0: continue
        w = tw * W_SOURCE[rec['source']] * W_TYPE.get(rec['type'], 1.0)
        md = (target_date.year-rec['date'].year)*12 + (target_date.month-rec['date'].month)
        for t in rec['terms']:
            if t in HIGH_FREQ: continue
            score[t] += w
            if md <= 6: r6[t] += 1
            if md <= 12: r12[t] += 1

    # 블로그 신호 (시간가중)
    for rec in blog_records:
        if rec['date'] >= target_date: continue
        tw = time_weight(target_date, rec['date'])
        if tw == 0: continue
        for t in rec['terms']:
            if t in HIGH_FREQ: continue
            if t in score:  # 이미 xls 데이터에 등장한 키워드만 보강
                score[t] += W_BLOG_PER_HIT * tw

    # 신생 보너스
    for t in list(score.keys()):
        fs = first_seen.get(t)
        if fs is None: continue
        mf = (target_date.year-fs.year)*12 + (target_date.month-fs.month)
        if mf <= 12 and r6[t] >= 3: score[t] *= 3.0
        elif mf <= 24 and r12[t] >= 5: score[t] *= 1.5

    # 직전 회차 디스카운트
    for t in list(score.keys()):
        if t in prev_round_essay:
            score[t] *= 0.4  # 논술로 나왔으면 다음 회차 가능성↓
        elif t in prev_round_short:
            score[t] *= 0.7  # 단답만 나왔으면 논술 가능성↑ (디스카운트 약하게)

    return score

CAT_HINTS = {
    '시스템구조': ['클라우드','컨테이너','쿠버','가용','분산','MSA','서버리스','데이터센터','HBM','CXL','RISC','뉴로모픽','병렬','MMU','데드락','교착','가상메모리','SLO','SRE','클러스터','액티브','액체냉각','DCI','NPU','TPU','뉴로','은행가','Banker','파이프라인 해저드','우선순위 역전','Priority Inv','시스템 콜','시스템콜'],
    'AI데이터분석': ['LLM','sLLM','트랜스포머','Transformer','RAG','멀티모달','생성형','파인튜닝','Agentic','에이전트','벡터DB','MLOps','LLMOps','파운데이션','GNN','MoE','메타모픽','커버리지','AGI','VAE','Attention','TTFT','TPOT','RLHF','PINN','DSLM','TEXT2SQL','임베딩','지식그래프','온톨로지','CAT','LangGraph','Reasoning','신뢰 가능','데이터 관측','Observability','Data Swamp','프롬프트 엔지'],
    'IT경영': ['ISP','EA','대가산정','대가 산정','디지털 전환','ITSM','RFP','ESG','터크만','TAM','조달','전자정부','테일러링','다크패턴','마이데이터','SaaS','정보보호 관리','AX','AI Transformation','협상에 의한 계약','조달청'],
    '소프트웨어공학': ['DevOps','DevSecOps','로우코드','LowCode','SBOM','플랫폼 엔지','재공학','역공학','무중단','SAFe','마이크로서비스','TDD','GitOps','형상관리','기술 부채','SOAP','벤치마크','Benchmark','SIL','HIL','샌드박스','Tailoring','Product Line','오픈소스 라이선스','SSPL','BSL','품질 인증','SP 인증','블랙박스','화이트박스'],
    '정보보안': ['랜섬웨어','제로트러스트','OWASP','포렌식','침입','ISMS','APT','피싱','XDR','SASE','PQC','양자보안','MCP','프롬프트 인젝션','Inversion','PET','RaaS','BPFdoor','TLS','공급망 보안','N2SF','Rainbow','ECC','타원곡선','Criteria','Common Criteria','TTPs','딥페이크','Deepfake','스푸핑','MAC','DAC','방화벽','SOAR','패스키','Passkey','Model DoS','Model Inversion','클라우드 네이티브 보안','Secure OS','보안 운영체제'],
    '네트워크': ['5G','6G','SDN','NaaS','SD-WAN','QUIC','OSI','IGP','EGP','OSPF','MODBUS','Wi-Fi','802','촉각','Tactile','AI-RAN','AI-Native','IBN','Intent-Based','이동통신','Zero-touch','ZSM','ETSI','채널용량','샤논','오류 제어','혼잡 제어','슬라이딩 윈도우'],
    '신기술융합': ['양자','디지털트윈','디지털 트윈','메타버스','자율주행','스마트시티','스마트 시티','스마트팩토리','XR','VR','MR','CBDC','자율운항','ADAS','ADS','안티드론','OPC UA','지오패트리','데이터 스페이스','휴머노이드','NFT','스마트선박'],
    '데이터베이스': ['벡터 DB','벡터DB','데이터레이크','OLAP','HNSW','IVF','SAGA','확장성 해싱','다차원','참조 무결성','오픈소스 DBMS','클러스터드','Data Lake','데이터 늪','데이터 가치','수평분할','수직분할','데이터 분할'],
    'AI거버넌스': ['AI 거버넌스','AI거버넌스','AI 기본법','인공지능기본법','42001','AI RMF','EU AI Act','AI 윤리','윤리기준','RMF','신뢰 기반','범용 AI','General-Purpose AI','초거대 AI'],
}

def classify_term(term):
    for cat, hints in CAT_HINTS.items():
        for h in hints:
            if h in term: return cat
    return '기타'

# === 유사 키워드 머지 ===
def merge_similar(scored_items):
    """부분문자열 관계 중 더 긴 게 점수 ≥ 짧은 거의 70%면 짧은 거 제거"""
    items = sorted(scored_items, key=lambda x: (-len(x[0]), -x[1]))
    keep = []
    used = set()
    for t, s in items:
        if t in used: continue
        # 더 짧은 부분문자열로 이미 들어간 게 있으면 머지
        absorb = False
        for kt, ks in keep:
            if t in kt and len(t) < len(kt):
                # 더 짧은 t는 더 긴 kt에 포함됨 → t는 버림 (단 t가 압도적으로 점수 높지 않으면)
                if s <= ks * 1.5:
                    absorb = True
                    break
        if not absorb:
            keep.append((t, s))
            used.add(t)
    return keep

def pick_balanced(score, n=30, per_cat=6):
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

print('\n=== v5 백테스트 ===')
results = []
for T in [135, 136, 137, 138]:
    # 블로그 포스트가 부족한 시기엔 신호 약함을 감안 (블로그 시작이 2026.04 정도)
    score = predict_v5(T)
    top = pick_balanced(score, n=30, per_cat=6)
    pred = [t for t,_ in top]
    actual = actual_terms(T)
    hits = [t for t in pred if t in actual]
    valuable = [h for h in hits if len(h) >= 4 and classify_term(h) != '기타']
    print(f'\n--- {T}회 ---')
    print(f'  적중: {len(hits)}/30 ({len(hits)/30*100:.1f}%) / 변별력: {len(valuable)}')
    print(f'  변별력 적중: {valuable[:20]}')
    print(f'  예측 TOP10: {pred[:10]}')
    results.append({'round': T, 'hit_rate': len(hits)/30, 'valuable_hits': valuable, 'all_hits': hits, 'pred': pred})

avg = sum(r['hit_rate'] for r in results) / len(results)
avg_val = sum(len(r['valuable_hits']) for r in results) / len(results)
print(f'\n=== v5 적중률: {avg*100:.1f}% (변별력 {avg_val:.1f}/30) ===')
print('비교: v4 변별력 4.0 / v5 변별력 목표 >4')

with open('predictor_v5_result.json','w',encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
