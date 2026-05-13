import xlrd, json, re
from collections import Counter, defaultdict

WB = xlrd.open_workbook('kpc_exam.xls')

# === 핫 키워드 화이트리스트 (출제 트렌드 후보만) ===
HOT_KEYWORDS = {
    # AI/데이터분석
    'AI데이터분석': [
        'Agentic AI','에이전틱','MCP','Model Context Protocol','LLMOps','MLOps',
        'sLLM','RAG','Fine Tuning','파인튜닝','Self-Attention','Transformer','트랜스포머',
        'MoE','Mixture of Experts','GNN','Graph Neural','멀티모달','Multimodal',
        'TTFT','TPOT','PINN','DSLM','AGI','ANI','VAE','강화학습',
        '메타모픽','뉴런 커버리지','데이터 관측','Observability','Data Swamp',
        'TEXT2SQL','임베딩','지식그래프','온톨로지','파운데이션','RLHF',
        '프롬프트 엔지니어링','AI 디지털교과서','초거대 AI','범용 AI','General-Purpose AI',
        '데이터 어노테이션','자기회귀','이동평균','베이즈','연관 규칙','VAE','PINN',
    ],
    # 정보보안
    '정보보안': [
        '제로트러스트','Zero Trust','PQC','양자내성','QKD','양자키',
        'OWASP LLM','프롬프트 인젝션','Model Inversion','Model DoS',
        'PET','Privacy Enhanc','ISMS-P','RaaS','BPFdoor','MCP 보안',
        'N2SF','국가 망 보안','TLS 1.3','TLS1.3','SBOM','공급망 보안','공급망보안',
        '딥페이크','Deepfake','CC ','Common Criteria','TTPs','타원곡선','ECC',
        '단방향 해시','Rainbow','암호문 공격','XDR','SASE','SOAR','SIEM',
        '클라우드 네이티브 보안','보안 운영체제','Secure OS','SOC','APT',
        '안티드론','패스키','Passkey','경계 기반 보안','perimeter','MCP(',
    ],
    # 시스템구조
    '시스템구조': [
        'HBM','CXL','RISC-V','NPU','뉴로모픽','FRAM','SSD','TPU',
        '멀티 GPU','멀티GPU','GPU','TPU','서버리스','쿠버네티스','Kubernetes',
        '멀티클라우드','MultiCloud','클라우드 네이티브',
        'FTS','Fault Tolerant','HA(','HA ','DR(','DR ','이중화','액티브-액티브','Active-Active',
        '멀티리전','Multi-Region','SLO','SLA','에러 버짓','에러버짓','SRE',
        'AIaaS','지능형 엣지','엣지 컴퓨팅','Edge','DCI','데이터센터',
        '플랫폼 엔지니어링','Platform Engineering','액체냉각','병렬 컴퓨팅',
        '인터미턴트','Intermittent','파이프라인 해저드','MMU','TLB','DMA',
        '데드락','교착','우선순위 역전','Priority Inv','시스템 콜','시스템콜',
        '가상메모리','가상 메모리','은행가 알고리즘','Banker',
        '뉴로모픽','폰 노이만','RISC','캐시 일관성','캐시 쓰기',
    ],
    # 네트워크
    '네트워크': [
        '6G','AI-Native','AI-RAN','IBN','Intent-Based','Zero-touch','ZSM',
        'Wi-Fi 7','IEEE 802','5G','QUIC','SD-WAN','SDN','NaaS',
        'IGP','EGP','OSPF','BGP','MODBUS','OPC UA','촉각 인터넷','Tactile',
        'OSI 7','HDLC','PoE','슬라이딩 윈도우','오류 제어','혼잡 제어',
        'DNS','DNS 보안','채널용량','샤논','PDH','SDH','디지털 계위',
    ],
    # IT경영
    'IT경영': [
        'AI 거버넌스','AI거버넌스','AI 기본법','인공지능기본법','ISO/IEC 42001','AI RMF',
        'CAT','AI 신뢰성','AI 윤리','EU AI Act',
        'ESG','AX','AI Transformation','DX','디지털 전환','디지털전환',
        'ISP','EA(','EA ','대가산정','대가 산정','감리',
        '다크패턴','마이데이터','전자정부','SaaS 가이드라인','디지털서비스',
        '터크만','TAM-SAM','조달청','PMO','전자정부사업관리',
        '소프트웨어 사업 영향평가','SP 인증','SP인증','RFP','협상에 의한 계약',
    ],
    # 소프트웨어공학
    '소프트웨어공학': [
        'DevSecOps','DevOps','로우코드','Low Code','LowCode','SBOM',
        '플랫폼 엔지니어링','테일러링','Tailoring','재공학','역공학',
        '무중단 배포','Zero Downtime','블루그린','카나리',
        '메타모픽','애자일','SAFe','마이크로서비스','MSA',
        'CI/CD','GitOps','SP 인증','SP인증','품질 인증',
        '제품계열','Product Line','형상관리','요구사항 추적',
        '기술 부채','오픈소스 라이선스','SSPL','BSL','MIT','BSD',
        '디자인 패턴','프록시 디자인','Strategy','SOA','REST','SOAP',
        'PoC','Benchmark','벤치마크','파일럿','동적 테스트','정적 테스트',
        'SIL','HIL','샌드박스','화이트박스','블랙박스',
    ],
    # 신기술융합
    '신기술융합': [
        '양자기술','양자컴퓨팅','양자 머신러닝','디지털트윈','디지털 트윈',
        '메타버스','자율주행','ADAS','ADS','자율운항선박','자율운항',
        '안티드론','드론','로봇','휴머노이드',
        'OPC UA','스마트시티','스마트 시티','스마트팩토리','스마트 팩토리',
        '스마트선박','스마트 선박','CBDC','블록체인','NFT',
        'XR','AR','VR','MR','패스키','Passkey',
        '지오패트리','데이터 스페이스','Data Space',
    ],
    # 데이터베이스
    '데이터베이스': [
        '벡터DB','벡터 DB','HNSW','IVF','벡터 데이터베이스',
        '확장성 해싱','다차원 색인','반정규화',
        '격리 수준','격리수준','분산 데이터베이스','SAGA',
        '회복','체크포인트','REDO','UNDO','로깅',
        'B-Tree','B+Tree','참조 무결성','오픈소스 DBMS',
        '데이터 가치평가','데이터 거래','데이터 늪','Data Lake','데이터레이크',
        '트랜잭션 격리','클러스터드 인덱스',
    ],
}

ALL_HOT = []
for cat, kws in HOT_KEYWORDS.items():
    for kw in kws:
        ALL_HOT.append((cat, kw))

def classify(q):
    hits = []
    for cat, kw in ALL_HOT:
        if kw in q:
            hits.append((cat, kw))
    return hits

def parse_round(s):
    s = str(s)
    m = re.search(r'(\d{4})\.(\d{1,2})', s)
    if m:
        return ('group', int(m.group(1)), int(m.group(2)))
    try:
        return ('round', int(float(s)))
    except:
        return ('unknown',)

def is_recent(meta):
    if meta[0] == 'round':
        return meta[1] >= 130
    if meta[0] == 'group':
        return meta[1] >= 2024
    return False

records = []
for sheet_name, source in [('기출', 'past'), ('모의', 'mock'), ('합숙', 'camp')]:
    sh = WB.sheet_by_name(sheet_name)
    for r in range(1, sh.nrows):
        round_v = sh.cell_value(r, 0)
        q = sh.cell_value(r, 3)
        if not q or not round_v: continue
        meta = parse_round(round_v)
        records.append({'source': source, 'meta': meta, 'q': q})

W_SOURCE = {'past': 5.0, 'camp': 3.0, 'mock': 2.0}
W_RECENT = 1.5

kw_score = defaultdict(float)
kw_cat = {}
kw_hits = defaultdict(lambda: {'past': 0, 'camp': 0, 'mock': 0, 'recent': 0, 'past_recent': 0})

for rec in records:
    w = W_SOURCE[rec['source']]
    recent = is_recent(rec['meta'])
    if recent: w *= W_RECENT
    seen = set()
    for cat, kw in classify(rec['q']):
        if kw in seen: continue
        seen.add(kw)
        kw_score[kw] += w
        kw_cat[kw] = cat
        kw_hits[kw][rec['source']] += 1
        if recent:
            kw_hits[kw]['recent'] += 1
            if rec['source'] == 'past':
                kw_hits[kw]['past_recent'] += 1

# 138회에서 이미 출제된 키워드는 다음 회차 중복 출제 가능성 낮음 → 디스카운트
# 138회 기출 키워드 추출
sh = WB.sheet_by_name('기출')
kw_in_138 = set()
for r in range(1, sh.nrows):
    if sh.cell_value(r,0) == 138.0:
        q = sh.cell_value(r,3)
        for cat, kw in classify(q):
            kw_in_138.add(kw)

# 138회 출제 키워드 표시
for kw in kw_score:
    kw_hits[kw]['in_138'] = 1 if kw in kw_in_138 else 0

top = sorted(kw_score.items(), key=lambda x: -x[1])[:60]
print(f'\n=== 통합 핫 키워드 TOP 60 ({len(kw_score)}개 후보) ===')
print(f'{"키워드":<28} {"카테고리":<12} {"점수":>7}  past/camp/mock | recent/past_recent | 138')
print('-' * 110)
for kw, sc in top:
    h = kw_hits[kw]
    flag138 = '★' if h['in_138'] else ''
    print(f'{kw:<28} {kw_cat[kw]:<12} {sc:>7.1f}  {h["past"]:>3}/{h["camp"]:>3}/{h["mock"]:>3} | {h["recent"]:>3}/{h["past_recent"]:>3} | {flag138}')

# 카테고리별 점수
cat_score = defaultdict(float)
for kw, sc in kw_score.items():
    cat_score[kw_cat[kw]] += sc
print('\n=== 카테고리별 통합 점수 (HOT 키워드 기준) ===')
total = sum(cat_score.values())
for c, s in sorted(cat_score.items(), key=lambda x: -x[1]):
    print(f'  {c:<12} {s:>8.1f}  ({s/total*100:.1f}%)')

# 저장
result = {
    'meta': {'generated': '2026-05-13', 'weights': {'source': W_SOURCE, 'recent_boost': W_RECENT}},
    'top_keywords': [
        {'keyword': kw, 'category': kw_cat[kw], 'score': round(sc, 2),
         'past': kw_hits[kw]['past'], 'camp': kw_hits[kw]['camp'], 'mock': kw_hits[kw]['mock'],
         'recent': kw_hits[kw]['recent'], 'past_recent': kw_hits[kw]['past_recent'],
         'in_138': kw_hits[kw]['in_138']}
        for kw, sc in top
    ],
    'category_scores': {c: round(s, 2) for c, s in sorted(cat_score.items(), key=lambda x: -x[1])}
}
with open('integrated_trend.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print('\n저장: /tmp/integrated_trend.json')
