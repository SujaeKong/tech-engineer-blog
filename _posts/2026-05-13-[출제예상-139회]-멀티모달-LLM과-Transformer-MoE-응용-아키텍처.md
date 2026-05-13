---
layout: post
title: "[출제예상 139회] 멀티모달 LLM과 Transformer/MoE 응용 아키텍처"
date: 2026-05-13 10:03:00 +0900
categories: AI데이터분석
tags: [exam-prediction, 139회대비, 멀티모달, Transformer, MoE, LLM, Self-Attention, 출제예상]
source_url: ""
---

> **139회 출제 예상 토픽 #4** — v6 알고리즘 점수 93.4 + 44.3 + 50.5 (5·37·26위 통합)
> 선정 근거: ① 135회 Multimodal LLM 단답·138회 Self-Attention 단답 출제 → 통합 논술 미출제, ② 134회 멀티모달 인공지능 응용 4교시 논술 이후 138회 휴지, ③ 137회 MoE 단답 출제 + 멀티모달 데이터 품질검증 표준(TTAK) 발표
{: .prompt-info }

## 1. 출제 트렌드 (110~138회)

| 회차 | 유형 | 출제 형태 |
|------|------|-----------|
| 134회 | 응용 4교시 | 멀티모달 인공지능 (개념·구성·기술) |
| 135회 | 관리 1교시 | Multimodal LLM 단답 |
| 135회 | 응용 2교시 | TTAK 멀티모달 데이터 품질검증 |
| 137회 | 응용 1교시 | 멀티모달 기술요소 |
| 137회 | 관리 1교시 | Transformer + MoE 단답 |
| 138회 | 응용 1교시 | Self-Attention 메커니즘 |
| 138회 | 응용 1교시 | TTFT vs TPOT |

**인사이트**: 단답·부분 논술 분산 출제 → **139회 멀티모달 LLM 아키텍처 + Transformer/MoE 응용 통합 논술 유력**

## 2. 개념·정의

### Transformer
> Self-Attention 메커니즘 기반 시퀀스 처리 모델. RNN/LSTM의 순차 처리 한계를 극복하고 **병렬 학습**과 **장거리 의존성**을 동시에 해결.

### MoE (Mixture of Experts)
> 입력별로 활성화될 **전문가(Expert) 서브 네트워크**를 라우터가 선택해 호출하는 sparse 활성화 모델. 총 파라미터는 크지만 실제 계산량은 일부만 사용 → **추론 효율↑**.

### 멀티모달 LLM
> 텍스트·이미지·음성·비디오 등 **이종 모달리티**를 통합 표현 공간에 정렬해 추론하는 LLM. 대표: GPT-4o, Gemini, Claude 3.5 Sonnet, LLaVA.

## 3. 아키텍처 (멀티모달 + Transformer + MoE)

```
┌──────────────────────────────────────────────────────────────┐
│              [입력 모달리티]                                    │
│   Text         Image          Audio          Video           │
│    │            │              │              │              │
│  Tokenizer    ViT/CLIP      Wav2Vec       VideoMAE          │
│    │            │              │              │              │
│    └────────────┴──────────────┴──────────────┘              │
│                          │                                    │
│                  ┌───────▼───────┐                            │
│                  │ Modality Align │ (Q-Former, Cross-Attn)   │
│                  └───────┬───────┘                            │
└──────────────────────────┼────────────────────────────────────┘
                           │
            ┌──────────────▼──────────────┐
            │   Unified Embedding Space   │
            └──────────────┬──────────────┘
                           │
       ┌───────────────────▼──────────────────┐
       │   Transformer Decoder (with MoE)     │
       │  ┌──────────────────────────────┐    │
       │  │ Multi-Head Self-Attention    │    │
       │  ├──────────────────────────────┤    │
       │  │ Router → Expert 1/2/.../N    │    │
       │  │   (Top-K 활성, sparse)       │    │
       │  ├──────────────────────────────┤    │
       │  │ Add & Norm + FeedForward     │    │
       │  └──────────────────────────────┘    │
       │            × L layers                │
       └───────────────┬──────────────────────┘
                       │
              ┌────────▼─────────┐
              │ Output (Text/    │
              │  Image/Action)   │
              └──────────────────┘
```

## 4. 핵심 기술요소

### 4.1 Self-Attention (138회 출제)

수식: `Attention(Q, K, V) = softmax(QKᵀ / √d_k) V`

| 구성 | 역할 |
|------|------|
| Query (Q) | "무엇을 찾을까" — 현재 토큰의 질의 |
| Key (K) | "내가 무엇을 가졌나" — 각 토큰의 키 |
| Value (V) | "실제 정보" — 출력에 반영될 값 |
| Scale `1/√d_k` | gradient 안정화 |
| Multi-Head | 다양한 표현 공간에서 병렬 어텐션 |

### 4.2 MoE 핵심 메커니즘

- **Router (Gating Network)**: 입력 토큰별 Top-K 전문가 선택
- **Sparse 활성**: 전체 N 전문가 중 K개만 활성 (예: 8개 중 2개)
- **Load Balancing Loss**: 전문가 간 부하 균형 보장
- **Expert Parallelism**: 전문가별 GPU 분산

| 구분 | Dense Transformer | MoE Transformer |
|------|-------------------|-----------------|
| 파라미터 | 전체 활성 | 일부만 활성 |
| 계산량 | 전체 | 일부 (sparse) |
| 모델 크기 | 작음 | 큼 |
| 추론 속도 | 느림 | 빠름 (동일 품질 기준) |
| 학습 난이도 | 보통 | Router 학습 어려움 |

### 4.3 멀티모달 정렬(Alignment) 기법

| 기법 | 설명 | 대표 모델 |
|------|------|-----------|
| Early Fusion | 입력 단계에서 결합 | Flamingo |
| Late Fusion | 출력 직전 결합 | CLIP |
| Cross-Attention | 모달리티 간 어텐션 | BLIP-2 |
| Q-Former | 학습 가능 query로 압축 | BLIP-2, MiniGPT-4 |
| Native Multimodal | 처음부터 통합 학습 | GPT-4o, Gemini |

### 4.4 추론 성능 지표 (138회 출제)

- **TTFT** (Time To First Token): 첫 토큰까지의 지연 — 사용자 체감 응답성
- **TPOT** (Time Per Output Token): 출력 토큰당 시간 — 처리량 지표
- **Throughput**: 초당 토큰 수 (전체 사용자)
- **Context Length**: 최대 입력 길이 (1M+ 등장)

## 5. 운영 고려사항

### 5.1 멀티모달 LLM 도입 단계
1. **유스케이스 정의** (Q&A·검색·생성)
2. **데이터 품질 검증** (TTAK.KO-10.1558)
3. **모델 선정** (Open vs Closed, 크기, 멀티모달 지원)
4. **파인튜닝/RAG** (도메인 특화)
5. **추론 인프라** (GPU·KV Cache·배치)
6. **평가·모니터링** (정확도·환각·편향)

### 5.2 비용·성능 트레이드오프

| 항목 | Dense | MoE | 멀티모달 |
|------|-------|-----|---------|
| 학습 비용 | 보통 | 매우 큼 | 매우 큼 |
| 추론 비용 | 비례 | 일부만 | 모달리티별 |
| 메모리 | 활성 파라미터 × 정밀도 | 전체 파라미터 보관 | 인코더별 추가 |
| 최적화 | Quantization·KV Cache | Expert Caching | 모달리티 분리 |

### 5.3 멀티모달 데이터 품질(TTAK 표준)
- **정확성**: 라벨링 신뢰도, 모달 간 일치
- **완전성**: 누락 모달 비율
- **다양성**: 도메인·언어·문화 커버리지
- **공정성**: 편향·차별 검출
- **시기성**: 최신성·업데이트 주기

## 6. 25점 답안 키워드

### 단답형(10점)
- **Self-Attention**: Q·K·V, softmax(QKᵀ/√d) V
- **MoE**: Router·Top-K·Sparse 활성·Load Balancing
- **멀티모달 정렬**: Cross-Attention, Q-Former
- **TTFT/TPOT**: 응답성·처리량 지표
- **품질**: TTAK 5요소 (정확·완전·다양·공정·시기)

### 논술형(25점) 답안 구조

**[서론]** 멀티모달 LLM 등장 + GPT-4o/Gemini 사례 + 산업 도입

**[본론 1] Transformer 기반 멀티모달 아키텍처**
- 모달리티별 인코더 + Alignment(Q-Former·Cross-Attn)
- Unified Embedding Space
- Self-Attention 메커니즘 (Q·K·V)

**[본론 2] MoE 응용**
- Router + Sparse 활성 + Load Balancing
- Dense vs MoE 비교 + Expert Parallelism
- 추론 효율 (TTFT·TPOT 개선)

**[본론 3] 운영 및 품질**
- TTAK 멀티모달 데이터 품질 5요소
- 비용·정확도 트레이드오프
- 환각·편향·공정성 평가

**[결론]** 산업 적용 사례 + 신뢰성·거버넌스 방향

## 7. 출제 가능 변형 문제

- "멀티모달 LLM의 아키텍처를 Transformer 기반으로 설명하고 MoE 적용 시 효과를 기술하시오."
- "Self-Attention 메커니즘의 수식과 Multi-Head Attention의 필요성을 설명하시오."
- "TTFT와 TPOT의 차이를 설명하고 LLM 추론 최적화 방안을 제시하시오."
- "TTAK 멀티모달 데이터 품질검증 방법의 5요소와 검증 절차를 설명하시오."

## 8. 관련 자료

- [기출 검색: 멀티모달](https://kpcitpe-search.pages.dev/?q=멀티모달)
- [기출 검색: MoE](https://kpcitpe-search.pages.dev/?q=MoE)
- 본 블로그 — [전북대 멀티 LLM 생성형AI 캠퍼스 확산과 멀티모델 라우팅 운영 아키텍처](/tech-engineer-blog/posts/전북대-멀티-LLM-생성형AI-캠퍼스-확산과-멀티모델-라우팅-운영-아키텍처/)
- Vaswani et al. — Attention Is All You Need (2017)
- TTAK.KO-10.1558 — 생성형 인공지능 학습 멀티모달 데이터 품질검증

## 9. 핵심 두음 (3개)

| 두음 | 원어 | 답안 활용 |
|------|------|-----------|
| **QKV** | Query·Key·Value | Self-Attention 핵심 |
| **라스부** | Router·Sparse·Load Balancing | MoE 3대 메커니즘 |
| **정완다공시** | 정확·완전·다양·공정·시기 | TTAK 품질 5요소 |

> **답안 팁**: "QKV"는 영문 그대로 외워서 답안에 수식과 함께 쓰면 즉시 점수 — Q·K·V 의미 한 줄씩 설명만 추가
{: .prompt-tip }
