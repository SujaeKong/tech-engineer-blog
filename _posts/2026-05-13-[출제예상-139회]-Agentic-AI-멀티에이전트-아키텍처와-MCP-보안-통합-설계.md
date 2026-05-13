---
layout: post
title: "[출제예상 139회] Agentic AI 멀티에이전트 아키텍처와 MCP 보안 통합 설계"
date: 2026-05-13 10:00:00 +0900
categories: AI데이터분석
tags: [exam-prediction, 139회대비, Agentic-AI, MCP, 멀티에이전트, LangGraph, AI보안, OWASP, 출제예상]
source_url: ""
---

> **139회 출제 예상 토픽 #1** — v6 알고리즘 점수 131.2 (전체 1위)
> 1번 토픽으로 선정된 근거: ① 138회 응용 단답으로만 출제 → 통합 논술 유력, ② 137회 MCP 단답 출제 → MCP 보안 이슈 연계 부각, ③ 최근 6개월 모의·합숙·뉴스 빈도 급증, ④ 138회 미통합형 출제, ⑤ 산업 도입 사례 폭발적 증가
{: .prompt-info }

## 1. 출제 트렌드 분석 (110~138회)

다음 표는 Agentic AI 관련 출제 이력이다.

| 회차 | 유형 | 출제 형태 | 비중 |
|------|------|-----------|------|
| 136회 | 관리 1교시 단답 | Agentic AI 개념 | 10점 |
| 137회 | 관리 2교시 논술 | MCP(Model Context Protocol) 보안 취약점 및 대응 | 25점 |
| 138회 | 응용 단답 | Self-Attention, TTFT/TPOT, Model DoS | 분산 출제 |
| 138회 | 응용 2교시 | LLM 서버·클라우드·엣지 OWASP LLM 보안 위협 | 25점 |

**핵심 인사이트**:
- 136회 단답 → 137회 MCP 부분 논술 → 138회 LLM 보안 종합 → **139회 Agentic AI 통합 논술이 자연스러운 흐름**
- 137회 MCP 보안은 "단일 프로토콜 관점", 139회에서는 **멀티에이전트 아키텍처 + MCP 통합 보안**으로 확장 출제 유력

## 2. 개념·정의

### Agentic AI (자율 에이전트 AI)
> LLM이 단순 응답을 넘어, **자율적으로 목표를 인식·계획·도구 호출·반성**하면서 다단계 작업을 수행하는 AI 시스템.

기존 RAG 기반 챗봇이 "질문-답변 1회성"이라면, Agentic AI는 "목표-계획-실행-검증-재계획" 루프로 복합 과제를 자율 처리한다.

### MCP (Model Context Protocol)
> Anthropic이 제안한 **LLM과 외부 도구·데이터 소스 간 표준 통신 프로토콜**. JSON-RPC 기반으로 도구 호출(Tool Use), 리소스 접근, 프롬프트 템플릿을 표준화.

## 3. 멀티에이전트 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                    Orchestrator Agent (Planner)                  │
│   ① 목표 분해 → ② 에이전트 라우팅 → ③ 결과 통합 → ④ 반성       │
└────────┬────────────────────┬──────────────────┬────────────────┘
         │                    │                  │
   ┌─────▼──────┐      ┌──────▼──────┐    ┌──────▼──────┐
   │ Worker A   │      │ Worker B    │    │ Worker C    │
   │ (검색·RAG) │      │ (코드 실행) │    │ (외부 API)  │
   └─────┬──────┘      └──────┬──────┘    └──────┬──────┘
         │                    │                  │
         └────────┬───────────┴──────────────────┘
                  │
         ┌────────▼─────────────────────────────┐
         │   MCP Gateway (보안·인증·로깅)         │
         │   - OAuth 2.1 / mTLS                  │
         │   - 권한 스코프·도구 허용목록          │
         │   - 요청 검증·감사 로그                │
         └────────┬─────────────────────────────┘
                  │
         ┌────────▼─────────────────────────────┐
         │   외부 도구·데이터 소스                │
         │   DB · 파일시스템 · SaaS · 사내 API   │
         └──────────────────────────────────────┘

        [공통 메모리]                  [거버넌스]
        Short-term · Long-term         정책·감사·평가
        Vector Store · Episodic        Human-in-the-loop
```

### 핵심 구성요소

> 🔑 **두음: 오워게메반사** (Orchestrator·Worker·Gateway·Memory·Reflection·사람검토)
{: .prompt-tip }

- **O**rchestrator(Planner): 사용자 목표를 하위 작업으로 분해, 적합한 워커 에이전트 선정, 결과 검증·재계획
- **W**orker Agents: 도메인 특화 (검색·RAG·코드 실행·외부 API 호출 등)
- **G**ateway (MCP): 모든 도구 호출의 단일 진입점. 인증·인가·로깅·정책 강제
- **M**emory (Shared): 단기(컨텍스트 윈도우)·장기(벡터 DB)·일화(Episodic) 메모리
- **R**eflection Loop: 결과 자기평가 → 재시도·수정·종료 판단
- **H**uman-in-the-Loop: 고위험 작업(결제·삭제·외부 발신)은 사람 승인 게이트

## 4. 핵심 기술요소

### 4.1 에이전트 패턴

| 패턴 | 설명 | 대표 프레임워크 |
|------|------|-----------------|
| ReAct | Reasoning + Acting 교차 실행 | LangChain |
| Plan-and-Execute | 계획 수립 → 일괄 실행 → 재계획 | LangGraph |
| Reflexion | 결과 자기평가·재시도 | DSPy |
| Multi-agent Collaboration | 역할 분담·메시지 패싱 | AutoGen, CrewAI |
| Tree of Thoughts | 다중 경로 탐색·선택 | 연구 단계 |

### 4.2 MCP 프로토콜 구조

```
Client (LLM 호스트)              Server (도구/리소스 제공자)
       │                                  │
       │── initialize ────────────────────▶│
       │◀──── capabilities ───────────────│
       │── tools/list ────────────────────▶│
       │◀──── [tool definitions] ─────────│
       │── tools/call(name, args) ───────▶│
       │◀──── result / error ─────────────│
       │── resources/read(uri) ───────────▶│
       │◀──── content ────────────────────│
       │── prompts/get(name) ─────────────▶│
       │◀──── template ───────────────────│
```

- **Transport**: stdio (로컬) / HTTP+SSE (원격) / WebSocket
- **Message Format**: JSON-RPC 2.0
- **Primitives (3종)**: Tools(함수)·Resources(읽기 데이터)·Prompts(템플릿)
- **Capabilities Negotiation**: 클라이언트·서버 기능 협상

### 4.3 통신 보안 (OWASP LLM Top 10 매핑)

> 🔑 **두음: 프부과시벡환무** (프롬프트·부적절출력·과한권한·시스템유출·벡터유출·환각·무한소비)
> 영어: **PI-IO-EA-SP-VE-MI-UC**
{: .prompt-tip }

| OWASP LLM 위험 | Agentic AI에서의 발현 | 통제 방안 |
|----------------|----------------------|----------|
| LLM01 **P**rompt Injection (프) | 도구 응답에 악성 지시 삽입 | 출력 sanitize, 시스템/사용자 분리 |
| LLM02 **I**nsecure Output (부) | 코드 실행·SQL 자동 실행 | 샌드박스, allowlist |
| LLM06 **E**xcessive Agency (과) | 에이전트의 과도한 권한 | 최소권한, 도구 스코프 제한 |
| LLM07 **S**ystem Prompt Leak (시) | 시스템 프롬프트 노출 | 프롬프트 캡슐화, 로깅 분리 |
| LLM08 **V**ector Embedding Weak (벡) | 메모리 데이터 유출 | 임베딩 암호화, RBAC |
| LLM09 **M**isinformation (환) | 환각 결과 자율 실행 | 출처 검증, 임계치 게이트 |
| LLM10 **U**nbounded Consumption (무) | 무한 루프·재귀 호출 | 토큰·시간·비용 한도 |

## 5. MCP 보안 위협과 대응

### 5.1 주요 위협 (137회 출제 + 확장)

> 🔑 **두음: 악도권세공** (악의서버·도구인젝션·권한상승·세션탈취·공급망)
{: .prompt-tip }

- **악**의적 MCP 서버: 사용자가 알지 못하는 도구를 등록 → 데이터 탈취
- **도**구 응답 인젝션: 도구가 LLM에 악성 지시문 반환 → 후속 행동 조작 (Tool-based Prompt Injection)
- **권**한 상승: 한 도구로 얻은 정보로 다른 도구 호출 권한 획득 (Confused Deputy)
- **세**션 탈취: MCP Gateway의 토큰·쿠키 유출
- **공**급망 공격: 신뢰하지 못하는 MCP 서버 패키지 (npm·PyPI) 설치

### 5.2 통제 아키텍처

```
[사용자]
   │ (OAuth 2.1 + PKCE)
   ▼
[MCP Host / LLM Client]
   │  ─ 정책 엔진(OPA/Cedar)
   │  ─ 도구 allowlist
   │  ─ 사용자 확인 다이얼로그
   ▼
[MCP Gateway]
   │  ─ mTLS 종단 인증
   │  ─ 요청·응답 검증(스키마·시맨틱)
   │  ─ 속도·비용 제한
   │  ─ 감사 로그 (SIEM 연동)
   ▼
[MCP Server]  (도구별 분리, 컨테이너 샌드박스)
   │  ─ 최소권한 IAM 자격
   │  ─ 시크릿 vault 연동
   │  ─ 출력 sanitize
   ▼
[외부 시스템]
```

## 6. 25점 답안 키워드

### 단답형(10점) 답안 키워드
- **정의**: 자율적 목표 인식·계획·도구 호출·반성 루프 수행 AI
- **구성**: Orchestrator·Worker·Memory·Reflection·HITL
- **MCP**: Anthropic 표준, JSON-RPC, Tools/Resources/Prompts 3-Primitive
- **위험**: Excessive Agency, Tool Injection, Confused Deputy
- **거버넌스**: 최소권한, 감사, 사람 승인 게이트

### 논술형(25점) 답안 구조

**[서론]**
- Agentic AI의 등장 배경 (LLM 자율 행동 확산, 산업 도입 사례)
- 정의 및 기존 RAG·챗봇과 차별점

**[본론 1] 멀티에이전트 시스템 아키텍처**
- Orchestrator-Worker 계층 구조
- 에이전트 패턴 (ReAct·Plan-and-Execute·Multi-agent)
- 공통 메모리·반성 루프·HITL

**[본론 2] MCP 통신 보안**
- MCP 프로토콜 구조 (3-Primitive, 메시지 형식)
- 위협 모델 (OWASP LLM 매핑, Tool Injection, Excessive Agency)
- 통제 아키텍처 (Gateway·정책 엔진·샌드박스)

**[본론 3] 거버넌스 및 운영**
- 인공지능기본법(2026.01)·ISO/IEC 42001·AI RMF 적용
- 감사·평가·HITL·비용 한도
- 사례 (코드 자동화·고객지원·산업 AIoT 멀티에이전트)

**[결론]**
- 자율성과 안전성의 균형 (Excessive Agency 통제)
- 향후 표준화 방향 (MCP·A2A·NIST AI Agent 가이드)

## 7. 출제 가능 변형 문제

- "Agentic AI 시스템의 멀티에이전트 아키텍처와 MCP 통신 보안에 대해 설명하시오."
- "MCP(Model Context Protocol) 기반 LLM 도구 호출에서 발생할 수 있는 보안 위협 5가지와 대응 방안을 제시하시오."
- "Agentic AI 도입 시 OWASP LLM Top 10 관점에서 Excessive Agency 위험을 분석하고 통제 방안을 기술하시오."
- "공공기관이 Agentic AI를 도입할 때 인공지능기본법·ISO/IEC 42001·AI RMF 관점에서 거버넌스 체계를 설계하시오."

## 8. 관련 자료

### 본 블로그 관련 포스트
- [KERI 자율제조 AI 멀티에이전트와 산업 분산 에이전트 시스템 아키텍처](/tech-engineer-blog/posts/KERI-자율제조-AI-멀티에이전트와-산업-분산-에이전트-시스템-아키텍처/)
- [솔트룩스 온톨로지 파운드리 공개와 산업형 LLM 지식그래프 RAG 아키텍처](/tech-engineer-blog/posts/솔트룩스-온톨로지-파운드리-공개와-산업형-LLM-지식그래프-RAG-아키텍처/)

### 외부 자료
- [기출 검색: Agentic AI](https://kpcitpe-search.pages.dev/?q=Agentic){:target="_blank"}
- [기출 검색: MCP](https://kpcitpe-search.pages.dev/?q=MCP){:target="_blank"}
- Anthropic — [Model Context Protocol Specification](https://modelcontextprotocol.io/){:target="_blank"}
- OWASP — [LLM Top 10 for Generative AI 2025](https://genai.owasp.org/){:target="_blank"}

> **변형 출제 대비 추가 학습 권장 키워드**: ReAct, LangGraph, AutoGen, A2A 프로토콜, NIST AI Agent Guide, Confused Deputy, Excessive Agency, Reflexion, Plan-and-Execute, OPA/Cedar 정책 엔진
{: .prompt-tip }

## 9. 핵심 두음 (3개만)

답안 본론의 뼈대로 직접 쓸 수 있는 핵심 두음만 정리했다.

| 두음 | 원어 | 답안 활용 |
|------|------|-----------|
| **오워게메반사** | Orchestrator·Worker·Gateway·Memory·Reflection·HITL | 본론 1 (아키텍처) 6요소 |
| **프부과시벡환무** | Prompt Injection·Insecure Output·Excessive Agency·System Prompt Leak·Vector Embedding·Misinformation·Unbounded Consumption | 본론 2 (OWASP LLM Top10 매핑) |
| **악도권세공** | 악의서버·도구인젝션·권한상승·세션탈취·공급망 | 본론 2 보강 (MCP 보안 위협 5) |

> **답안 팁**: 본론 각 단락 첫 문장에 두음 키워드를 그대로 풀어 쓰면 채점자가 구조를 즉시 파악한다. 두음에 없는 항목은 변형 출제에서 추가 점수 요소.
{: .prompt-tip }
