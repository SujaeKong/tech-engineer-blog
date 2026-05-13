"""v4: v3 + stopword 강화 + 조사 정규화 + per_cat 확장"""
import xlrd, json, re
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
    # v4 추가
    '빅데이터','IoT','PMO','BCP','UML','REST','SOA','블루그린','카나리','REDO','UNDO','체크포인트',
    '격리','정규형','정규화','반정규화','회복','트랜잭션','SQL','NoSQL','인덱스','오류','혼잡',
    '머신러닝','딥러닝','지능형','지능형 시스템','지능형 서비스','정보화','정보처리','정보보호',
    '거래','산업','상품','제품','마케팅','경영','경영전략','경영자','관리자','매니저',
    '프로세스','프로세서','파이프라인','파이프','데이터처리','데이터 처리','데이터 분석',
    'B-Tree','B+Tree','MMU','TLB','DMA','PoE','HDLC','SDH','PDH','IDS','IPS','SOC','SIEM','DNS',
    '머신','딥','심층','신경','신경망','텐서','벡터','벡터화','임베딩','드론','로봇',
    '안전','안정','신뢰','신뢰성','가용성','확장성','유연성','경량','경량화',
}

HANGUL_PATTERN = re.compile(r'[가-힣]{2,10}')
ENG_PATTERN = re.compile(r'\b[A-Z][A-Za-z0-9\-\./]{2,30}|\b[A-Z]{3,10}\b')
MIXED_PATTERN = re.compile(r'[A-Z][A-Za-z]*[가-힣]{2,8}|[가-힣]{2,8}[A-Z][A-Za-z]*')

# 조사 제거
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

records = []
for sheet_name, source in [('기출', 'past'), ('모의', 'mock'), ('합숙', 'camp')]:
    sh = WB.sheet_by_name(sheet_name)
    for r in range(1, sh.nrows):
        round_v = sh.cell_value(r, 0)
        q = sh.cell_value(r, 3)
        if not q or not round_v: continue
        meta = parse_round(round_v)
        if not meta: continue
        d = round_to_date(meta[1]) if meta[0] == 'round' else meta[1]
        records.append({'source': source, 'date': d, 'meta': meta, 'terms': extract_terms(q)})

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

W_SOURCE = {'past': 5.0, 'camp': 3.0, 'mock': 2.0}

def time_weight(target_date, rec_date):
    if rec_date >= target_date: return 0
    months = (target_date.year - rec_date.year)*12 + (target_date.month - rec_date.month)
    if months <= 6: return 4.0
    if months <= 12: return 2.5
    if months <= 24: return 1.5
    return 0.8

def predict(target_round):
    target_date = round_to_date(target_round)
    score = defaultdict(float)
    r6 = defaultdict(int); r12 = defaultdict(int)
    for rec in records:
        if rec['meta'][0]=='round' and rec['meta'][1]>=target_round: continue
        if rec['date']>=target_date: continue
        tw = time_weight(target_date, rec['date'])
        if tw == 0: continue
        w = tw * W_SOURCE[rec['source']]
        md = (target_date.year-rec['date'].year)*12 + (target_date.month-rec['date'].month)
        for t in rec['terms']:
            if t in HIGH_FREQ: continue
            score[t] += w
            if md <= 6: r6[t] += 1
            if md <= 12: r12[t] += 1
    for t in list(score.keys()):
        fs = first_seen.get(t)
        if fs is None: continue
        mf = (target_date.year-fs.year)*12 + (target_date.month-fs.month)
        if mf <= 12 and r6[t] >= 3: score[t] *= 3.0
        elif mf <= 24 and r12[t] >= 5: score[t] *= 1.5
    return score

CAT_HINTS = {
    '시스템구조': ['클라우드','컨테이너','쿠버','가용','분산','MSA','서버리스','데이터센터','HBM','CXL','RISC','뉴로모픽','병렬','MMU','데드락','교착','가상메모리','SLO','SRE','클러스터','액티브','액체냉각','DCI','NPU','TPU','뉴로'],
    'AI데이터분석': ['LLM','sLLM','트랜스포머','Transformer','RAG','멀티모달','생성형','파인튜닝','Agentic','에이전트','벡터DB','MLOps','LLMOps','파운데이션','GNN','MoE','메타모픽','커버리지','AGI','VAE','Attention','TTFT','TPOT','RLHF','PINN','DSLM','TEXT2SQL','임베딩','지식그래프','온톨로지','CAT','LangGraph','Reasoning','신뢰 가능'],
    'IT경영': ['ISP','EA','대가산정','대가 산정','디지털 전환','ITSM','RFP','ESG','터크만','TAM','조달','전자정부','테일러링','다크패턴','마이데이터','SaaS','정보보호 관리','PMO'],
    '소프트웨어공학': ['DevOps','DevSecOps','로우코드','LowCode','SBOM','플랫폼 엔지','재공학','역공학','무중단','SAFe','마이크로서비스','TDD','GitOps','형상관리','기술 부채','SOAP','벤치마크','Benchmark','SIL','HIL','샌드박스','Tailoring','Product Line','오픈소스 라이선스'],
    '정보보안': ['랜섬웨어','제로트러스트','OWASP','포렌식','침입','ISMS','APT','피싱','XDR','SASE','PQC','양자보안','MCP','프롬프트 인젝션','Inversion','PET','RaaS','BPFdoor','TLS','공급망 보안','N2SF','Rainbow','ECC','타원곡선','Criteria','TTPs','딥페이크','Deepfake','스푸핑','MAC','DAC','방화벽','SOAR','패스키','Passkey','Model DoS','Model Inversion'],
    '네트워크': ['5G','6G','SDN','NaaS','SD-WAN','QUIC','OSI','IGP','EGP','OSPF','MODBUS','Wi-Fi','802','촉각','Tactile','AI-RAN','AI-Native','IBN','Intent-Based','이동통신','Zero-touch','ZSM','ETSI'],
    '신기술융합': ['양자','디지털트윈','디지털 트윈','메타버스','자율주행','스마트시티','스마트 시티','스마트팩토리','XR','VR','MR','CBDC','자율운항','ADAS','ADS','안티드론','OPC UA','지오패트리','데이터 스페이스','휴머노이드','NFT'],
    '데이터베이스': ['벡터 DB','벡터DB','데이터레이크','OLAP','HNSW','IVF','SAGA','확장성 해싱','다차원','참조 무결성','오픈소스 DBMS','클러스터드','Data Lake','데이터 늪','데이터 가치'],
    'AI거버넌스': ['AI 거버넌스','AI거버넌스','AI 기본법','인공지능기본법','42001','AI RMF','EU AI Act','AI 윤리','윤리기준','RMF','신뢰 기반'],
}

def classify_term(term):
    for cat, hints in CAT_HINTS.items():
        for h in hints:
            if h in term: return cat
    return '기타'

def pick(score, n=30, per_cat=6):
    by_cat = defaultdict(list)
    for t, s in score.items():
        by_cat[classify_term(t)].append((t,s))
    for c in by_cat: by_cat[c].sort(key=lambda x:-x[1])
    result = []
    for c, items in by_cat.items():
        if c == '기타': continue
        result.extend(items[:per_cat])
    result.sort(key=lambda x:-x[1])
    return result[:n]

def actual_terms(T):
    sh = WB.sheet_by_name('기출')
    a = set()
    for r in range(1, sh.nrows):
        if sh.cell_value(r,0) == float(T):
            for t in extract_terms(sh.cell_value(r,3)):
                if t not in HIGH_FREQ: a.add(t)
    return a

print('=== v4 백테스트 ===')
results = []
for T in [135, 136, 137, 138]:
    score = predict(T)
    top = pick(score, n=30, per_cat=6)
    pred = [t for t,_ in top]
    actual = actual_terms(T)
    hits = [t for t in pred if t in actual]
    # 변별력: 카테고리 '기타' 제외 + 길이 4자+
    valuable = [h for h in hits if len(h) >= 4 and classify_term(h) != '기타']
    print(f'\n--- {T}회 ---')
    print(f'  적중: {len(hits)}/30 ({len(hits)/30*100:.1f}%) / 변별력 적중: {len(valuable)}')
    print(f'  변별력 적중 키워드: {valuable[:20]}')
    print(f'  예측 TOP10: {pred[:10]}')
    results.append({'round': T, 'hit_rate': len(hits)/30, 'valuable_hits': valuable, 'all_hits': hits, 'pred': pred})

avg = sum(r['hit_rate'] for r in results) / len(results)
avg_val = sum(len(r['valuable_hits']) for r in results) / len(results)
print(f'\n=== v4 적중률: {avg*100:.1f}% (변별력 키워드 평균 {avg_val:.1f}/30) ===')
print('v1: 22% / v2: 45%(도메인) / v3: 22%(변별력) / v4 목표: 변별력↑')

with open('predictor_v4_result.json','w',encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
