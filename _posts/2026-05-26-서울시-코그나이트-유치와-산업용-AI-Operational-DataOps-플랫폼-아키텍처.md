---
layout: post
title: "서울시 코그나이트 유치와 산업용 AI Operational DataOps 플랫폼 아키텍처"
date: 2026-05-26
categories: 시스템구조
tags: [산업용AI, IndustrialDataOps, Cognite, OT통합, 디지털트윈, AIoT, IndustrialAI, 데이터컨텍스트화, 자산모델, MES연계]
source_url: ""
---

## 1. 뉴스 요약

2026-05-24 케이에스피뉴스·네이트 등 복수 매체가 "**서울시, 美 산업용 AI 기업 코그나이트(Cognite) 유치…서울 제조업 AI 전환 본격화**"를 보도했다. 핵심은 ① 노르웨이 출신 글로벌 **산업용 AI/Industrial DataOps 전문 기업 코그나이트**의 한국 거점이 서울에 설치되고, ② 서울시는 이를 **제조·에너지·플랜트 AI 전환의 마중물**로 삼는 MOU를 체결했으며, ③ 단순 사무 AI가 아니라 **OT(운영기술) 영역의 시계열·자산 데이터 컨텍스트화**가 핵심이라는 점이다. 이는 ① **OPC UA·MQTT 등 OT 프로토콜과 IT 데이터 레이크 통합**, ② **디지털 트윈 + AI 추론**의 표준화, ③ **PI/Historian·MES·ERP·CMMS 분산 데이터를 단일 자산 모델로 연결**하는 산업 특화 데이터 플랫폼 흐름의 연장선이다. 동일 시기 **K-스마트수산업 AX(2026-05-21)**, **BPA HD현대삼호 항만 AIoT 예지보전(2026-05-05)**, **KERI 자율제조 멀티에이전트(2026-05-07)** 가 모두 같은 방향으로 수렴한다. 기술사 시스템구조 영역에서 **산업용 AI 플랫폼·OT/IT 컨버전스·디지털 트윈 통합 아키텍처**는 출제 비중이 높은 핵심 토픽으로, 본 회차(139회) 출제 가능성이 있다.

## 2. 핵심 개념

### 산업용 AI 플랫폼(Industrial AI Platform) 개요

| 항목 | 내용 |
|---|---|
| 정의 | OT 현장 데이터를 IT 데이터 모델과 결합해 산업 자산 단위로 AI 추론·운영 의사결정을 지원하는 플랫폼 |
| 대표 사례 | Cognite Data Fusion, AVEVA PI System+CONNECT, Siemens Industrial Edge, GE Digital Predix |
| 핵심 기능 | 데이터 컨텍스트화, 자산 그래프, 디지털 트윈, AIoT 예지보전, 운영 LLM 코파일럿 |
| 데이터 소스 | DCS·PLC·SCADA·Historian·MES·ERP·CMMS·QMS·도면·P&ID |
| 도입 도메인 | 정유·석유화학·발전·플랜트·제조·물류·해양·수자원 |

### 산업용 AI 플랫폼 4-Layer 아키텍처

| 계층 | 구성요소 | 역할 |
|---|---|---|
| Edge·OT 수집 | OPC UA, MQTT, Modbus, Historian Bridge | 현장 신호·이벤트·시계열 수집과 게이트웨이 보안 |
| Industrial DataOps | Data Contextualization, Asset Graph, Time Series Store | 분산 IT/OT 데이터를 자산 단위 컨텍스트로 통합 |
| Twin·AI 서비스 | Digital Twin, 이상탐지·예지보전, 운영 LLM 코파일럿 | 자산 상태 시뮬레이션·예측·자연어 운영 질의 |
| 운영 통합 | MES·ERP·CMMS·EAM 연계, 작업지시·정비 워크플로 | AI 인사이트의 액션화·KPI 환류 |

### IT 데이터 플랫폼 vs Industrial DataOps

| 구분 | IT 데이터 플랫폼(레이크하우스) | Industrial DataOps |
|---|---|---|
| 데이터 특성 | 트랜잭션·로그·사용자 이벤트 | 시계열·센서·자산·도면·태그 |
| 시간 해상도 | 분·시간 단위 배치 + 스트림 | 밀리초·초 단위 고주파 시계열 |
| 핵심 모델 | 스타·디멘션, 데이터 메시 | Asset Graph + Time Series + 3D/도면 결합 |
| 거버넌스 | DataHub·Atlas 카탈로그 | 자산 계층·태그 표준(ISA-95, CFIHOS) |
| AI 활용 | 추천·분석·LLM 검색 | 예지보전·이상탐지·운영 의사결정·LLM 운영 코파일럿 |
| 통합 대상 | DW·BI·CRM·마케팅 | DCS·PLC·SCADA·MES·ERP·CMMS |

## 3. 기술사 출제 포인트

### 개념 정의와 필요성

- **산업용 AI 플랫폼**: 현장 OT 데이터의 **자산 컨텍스트화(Contextualization)** 를 통해 디지털 트윈과 AI 모델이 동일한 의미 계층에서 동작하도록 만드는 산업 특화 데이터·AI 운영 플랫폼
- **필요성**: ① 데이터의 80%가 시계열·도면·문서 등 비정형 OT 자산 데이터, ② 분산된 MES·ERP·Historian 사일로로 인한 의사결정 지연, ③ 생성형 AI/에이전트가 활용할 **현장 도메인 그라운딩**(자산·태그·이력) 필요, ④ ESG·탄소·안전 KPI를 위한 운영 데이터 통합 의무

### 기존 방식과의 비교

- **수동 통합 ETL**: 사일로별 일회성 추출 → 유지보수 폭발, 컨텍스트 손실
- **단일 SCADA 확장**: 벤더 종속·확장성 한계, AI 서비스 결합 어려움
- **데이터 레이크 직접 적재**: 의미 컨텍스트 부재로 모델 일반화 실패, "데이터 늪(Swamp)" 위험
- **Industrial DataOps**: 자산·태그·이벤트를 그래프 형태로 컨텍스트화 → AI/LLM이 운영 의미를 그라운딩

### 아키텍처 구성요소

- **데이터 컨텍스트화 엔진**: 시계열·도면·문서·3D·태그 매칭, 엔티티 해소, 룰·임베딩 기반 매핑
- **Asset Graph(자산 그래프)**: ISA-95 계층(Enterprise→Site→Area→Unit→Equipment) 기반 노드·관계 모델
- **시계열 저장소**: 압축·다운샘플링·재구성, 고카디널리티 태그 처리
- **디지털 트윈 런타임**: 3D/2D 도면 + 실시간 센서 + 시뮬레이션 모델 결합
- **AI/ML 서비스**: 이상탐지·잔존수명(RUL)·소프트센서·강화학습 운영 최적화
- **운영 LLM 코파일럿**: 자산 그래프 RAG, 도면·이력·정비 지식 통합 자연어 질의
- **외부 연계**: MES·ERP·CMMS·EAM 워크플로 연동, 작업지시 자동 생성
- **거버넌스**: 데이터 소유권·라이선스, 사이버보안(IEC 62443), 변경관리

### 도입 시 고려사항

- **표준화**: ISA-95, CFIHOS, OPC UA Companion Spec, ISO 14224 등 산업 표준 채택
- **사이버보안**: IEC 62443·KISA 피지컬 AI 보안모델·OT/IT 경계 분리, 데이터 단방향 흐름
- **데이터 주권**: 공정 데이터 해외 이전 제한, **소버린 클라우드/온프레미스** 옵션 필수
- **조직**: 운영기술 엔지니어 + 데이터 엔지니어 + AI 엔지니어 **3자 협업 운영 모델**
- **단계적 확산**: Pilot Unit → Site → Multi-Site → Enterprise 스케일링, 가치 검증 지표 사전 정의
- **AI 거버넌스**: AI기본법·ISO/IEC 42001 적용, 안전 임계값·휴먼 인 더 루프 설계
- **공급망**: 모델·데이터셋 SBOM/MBOM, 외부 모델 변경 시 영향평가

## 4. 관련 토픽 연계

- [디지털 트윈과 산업 AI 융합 아키텍처](/tech-engineer-blog/posts/디지털-트윈과-산업-AI-융합-아키텍처/) — 디지털 트윈과 AI 통합의 기본 아키텍처
- [BPA HD현대삼호 AI 항만하역장비 고도화와 산업 AIoT 예지보전 시스템 아키텍처](/tech-engineer-blog/posts/BPA-HD현대삼호-AI-항만하역장비-고도화와-산업-AIoT-예지보전-시스템-아키텍처/) — AIoT 예지보전 사례
- [KERI 자율제조 AI 멀티에이전트와 산업 분산 에이전트 시스템 아키텍처](/tech-engineer-blog/posts/KERI-자율제조-AI-멀티에이전트와-산업-분산-에이전트-시스템-아키텍처/) — 자율제조 멀티에이전트 운영
- [범용 AI 이상탐지 플랫폼과 발전설비 AIOps 아키텍처](/tech-engineer-blog/posts/범용-AI-이상탐지-플랫폼과-발전설비-AIOps-아키텍처/) — 산업 이상탐지 플랫폼 설계
- [KISA 피지컬 AI 보안모델과 제조 OT 보안](/tech-engineer-blog/posts/KISA-피지컬-AI-보안모델과-제조-OT-보안/) — 산업 AI 플랫폼의 OT 보안 요건
- [소버린 AI와 제조 AX 전략](/tech-engineer-blog/posts/소버린-AI와-제조-AX-전략/) — 산업 데이터 주권과 소버린 AI
- [데이터 레이크하우스 아키텍처와 분석 플랫폼 진화](/tech-engineer-blog/posts/데이터-레이크하우스-아키텍처와-분석-플랫폼-진화/) — 일반 IT 데이터 플랫폼과의 비교
