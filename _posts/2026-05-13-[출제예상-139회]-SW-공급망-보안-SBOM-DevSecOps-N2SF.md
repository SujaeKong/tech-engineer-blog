---
layout: post
title: "[출제예상 139회] SW 공급망 보안 — SBOM·DevSecOps·N2SF 통합"
date: 2026-05-13 10:08:00 +0900
categories: 소프트웨어공학
tags: [exam-prediction, 139회대비, SBOM, DevSecOps, 공급망보안, N2SF, SLSA, 출제예상]
source_url: ""
---

> **139회 출제 예상 토픽 #9** — v6 알고리즘 점수 43.7(SBOM) + 47.9(DevOps) 통합
> 선정 근거: ① 134회 SBOM 단답·관리 3교시 SBOM 논술 후 138회 미출제, ② 136회 공급망 보안+제로트러스트 출제 → AI 모델 공급망까지 확장 출제 유력, ③ EU CRA·미국 EO 14028 등 글로벌 SBOM 의무화 트렌드
{: .prompt-info }

## 1. 출제 트렌드 (110~138회)

| 회차 | 유형 | 출제 형태 |
|------|------|-----------|
| 134회 | 응용 1교시 | SBOM 단답 |
| 134회 | 관리 3교시 | SBOM 기반 오픈소스 SW 관리 |
| 134회 | 응용 3교시 | 오픈소스 라이선스 폐쇄형 전환(SSPL·BSL) |
| 135회 | 관리 2교시 | CI/CD DevSecOps |
| 136회 | 관리 4교시 | 공급망 보안 + 제로트러스트 공급망 아키텍처 |
| 137회 | 관리 3교시 | N2SF (국가 망 보안체계) |

**인사이트**: SBOM 단답·DevSecOps·공급망 분산 출제 → **139회 SW 공급망 보안 통합 논술 (SBOM + DevSecOps + AI 모델 공급망) 유력**

## 2. 개념·정의

### SW 공급망 보안
> 코드·라이브러리·빌드·배포·운영 **전 생애주기**에 걸친 위협을 통합 통제하는 보안 체계.

### SBOM (Software Bill of Materials)
> SW 구성요소(라이브러리·의존성·라이선스) 인벤토리. **SPDX·CycloneDX** 두 표준 포맷이 대표.

### DevSecOps
> DevOps 파이프라인에 보안을 **좌측 이동(Shift-Left)** 통합. 코드 → 빌드 → 배포 전 단계 자동 검증.

### SLSA (Supply-chain Levels for Software Artifacts)
> Google 주도, OSSF가 표준화. 빌드 무결성 4단계 성숙도 모델.

## 3. 통합 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│                  [개발자 / 외부 코드]                          │
│  Git Push → PR → Code Review                                 │
└─────────────────────────┬────────────────────────────────────┘
                          │
              ┌───────────▼──────────────┐
              │  보안 검증 게이트(Shift-Left)│
              │  - SAST (정적 분석)         │
              │  - SCA (의존성 취약점)      │
              │  - 시크릿 스캔              │
              │  - 라이선스 검증            │
              │  - SBOM 생성·검증           │
              └───────────┬──────────────┘
                          │
              ┌───────────▼──────────────┐
              │   CI 빌드 (SLSA L3+)      │
              │  - 격리 빌드 환경          │
              │  - 빌드 출처 증명(Provenance)│
              │  - 서명(Sigstore·cosign)   │
              └───────────┬──────────────┘
                          │
              ┌───────────▼──────────────┐
              │   레지스트리·아티팩트     │
              │  - 컨테이너 이미지 서명    │
              │  - SBOM 첨부              │
              │  - 무결성 검증            │
              └───────────┬──────────────┘
                          │
              ┌───────────▼──────────────┐
              │   배포(CD) + Runtime      │
              │  - 정책 시행 (OPA/Kyverno)│
              │  - DAST·IAST 운영 검증   │
              │  - RASP·런타임 보호       │
              └───────────┬──────────────┘
                          │
              ┌───────────▼──────────────┐
              │   모니터링·대응           │
              │  - 취약점 알림(CVE 매칭)  │
              │  - SBOM 기반 영향 분석   │
              │  - 패치·핫픽스 자동화    │
              └──────────────────────────┘
```

## 4. 핵심 기술요소

### 4.1 SBOM 표준 포맷

| 포맷 | 주관 | 특징 |
|------|------|------|
| **SPDX** (ISO/IEC 5962) | Linux Foundation | 라이선스 중심, 가장 광범위 |
| **CycloneDX** | OWASP | 보안 취약점 통합, BOM Exchange |
| **SWID** (ISO/IEC 19770-2) | ISO | SW 식별 태그 |

### 4.2 SBOM 핵심 데이터 요소 (NTIA Minimum)
- 공급자 이름
- 컴포넌트 이름
- 버전
- 고유 식별자(PURL·CPE)
- 의존 관계
- SBOM 작성자
- 타임스탬프

### 4.3 DevSecOps 파이프라인 보안 검증

| 단계 | 도구 | 목적 |
|------|------|------|
| **Code** | Pre-commit hook | 시크릿·린트 |
| **SAST** | SonarQube·Snyk·Semgrep | 정적 코드 취약점 |
| **SCA** | Snyk·Dependabot·Trivy | 의존성 CVE |
| **시크릿** | GitGuardian·TruffleHog | 노출 탐지 |
| **IaC 보안** | Checkov·tfsec | 인프라 코드 |
| **컨테이너** | Trivy·Grype·Clair | 이미지 스캔 |
| **DAST** | OWASP ZAP·Burp | 동적 분석 |
| **IAST** | Contrast·Synopsys | 런타임 인터랙티브 |
| **RASP** | Imperva·Contrast | 런타임 보호 |

### 4.4 SLSA 4 성숙도

| Level | 요구 |
|-------|------|
| L1 | 빌드 자동화, Provenance 존재 |
| L2 | 빌드 호스트 신뢰, Provenance 인증 |
| L3 | 격리 빌드, Hermetic, Tamper-resistant |
| L4 | 두 명의 검토자, 재현 가능 빌드 |

### 4.5 AI 모델 공급망 (신생 영역)
- **AI BOM (AIBOM)**: 학습 데이터·모델 가중치·파인튜닝 이력
- **모델 카드(Model Card)**: 데이터·성능·한계 명세
- **데이터 시트(Datasheet)**: 데이터셋 출처·라이선스
- **위협**: 데이터 오염(Poisoning), 백도어 모델, 가중치 변조

## 5. 운영 고려사항

### 5.1 글로벌 규제 동향

| 규제 | 발효 | 요구사항 |
|------|------|---------|
| **미국 EO 14028** | 2021 | 연방기관 납품 SW SBOM 의무 |
| **EU CRA** (Cyber Resilience Act) | 2024 | EU 시장 SW 보안 의무·SBOM |
| **한국 N2SF** | 2025 | 공공기관 공급망 통제 |
| **NIST SSDF** | 표준 | Secure SW Development Framework |

### 5.2 도입 단계
1. **자산 식별** — 코드·라이브러리·컨테이너·모델 인벤토리
2. **SBOM 자동 생성** — CI에서 syft·CycloneDX CLI
3. **취약점 매칭** — CVE DB·VEX·EPSS 우선순위
4. **빌드 출처 증명** — Sigstore·cosign 서명
5. **정책 시행** — 게이트키퍼·OPA·Kyverno
6. **사고 대응** — SBOM 기반 영향 범위 자동 분석

### 5.3 오픈소스 라이선스 위협 (134회 출제)
- **폐쇄형 전환**: SSPL(MongoDB)·BSL(HashiCorp)·Elastic License
- **대응**: 라이선스 호환성 검토, 대체 OSS 후보 확보, 포크 전략

## 6. 25점 답안 키워드

### 단답형(10점)
- **SBOM**: SPDX·CycloneDX·SWID 3표준
- **NTIA 최소요소**: 공급자·이름·버전·식별자·의존·작성자·타임스탬프
- **DevSecOps**: SAST·SCA·DAST·IAST·RASP
- **SLSA**: 빌드 무결성 4단계 (L1~L4)
- **AI공급망**: AIBOM·Model Card·Datasheet

### 논술형(25점) 답안 구조

**[서론]** Log4Shell·SolarWinds 사례 + 규제 흐름 (EO 14028·CRA·N2SF)

**[본론 1] SBOM 표준과 운영**
- SPDX vs CycloneDX
- NTIA 최소 요소
- 자동 생성·관리

**[본론 2] DevSecOps 파이프라인**
- Shift-Left + 단계별 보안 검증
- SAST·SCA·DAST·IAST·RASP 9도구 매트릭스
- SLSA 4단계 성숙도

**[본론 3] AI 모델 공급망 (신생)**
- AIBOM·Model Card·Datasheet
- 데이터 오염·백도어 모델 위협
- 모델 서명·출처 증명

**[결론]** N2SF 등 규제 준수 + 운영 자동화 + 글로벌 정합성

## 7. 출제 가능 변형 문제

- "SW 공급망 보안의 위협과 SBOM 기반 통합 대응 방안을 설명하시오."
- "DevSecOps 파이프라인의 보안 검증 단계(SAST·SCA·DAST·IAST·RASP)를 비교 설명하시오."
- "SLSA(Supply-chain Levels for Software Artifacts)의 4단계 성숙도와 적용 방안을 기술하시오."
- "AI 모델 공급망 보안에서 AIBOM·Model Card의 역할과 데이터 오염 대응 방안을 제시하시오."

## 8. 관련 자료

- [기출 검색: SBOM](https://kpcitpe-search.pages.dev/?q=SBOM)
- [기출 검색: 공급망 보안](https://kpcitpe-search.pages.dev/?q=공급망)
- 본 블로그 — [미 국방부 AI 7개사 기밀업무 계약과 군사 AI 공급망 거버넌스](/tech-engineer-blog/posts/미-국방부-AI-7개사-기밀업무-계약과-군사-AI-공급망-거버넌스/)
- CISA — [SBOM Resources](https://www.cisa.gov/sbom)
- SLSA — [Supply-chain Levels for Software Artifacts](https://slsa.dev/)
- OWASP — [CycloneDX](https://cyclonedx.org/)

## 9. 핵심 두음 (3개)

| 두음 | 원어 | 답안 활용 |
|------|------|-----------|
| **SAST-SCA-DAST-IAST-RASP** | 정적·의존성·동적·인터랙티브·런타임 | DevSecOps 5도구 |
| **SPDX-CycloneDX-SWID** | Linux F.·OWASP·ISO | SBOM 3표준 |
| **EO-CRA-N2SF** | 미국·EU·한국 | 글로벌 공급망 규제 3축 |

> **답안 팁**: "Shift-Left 5단계 보안 검증 (SAST-SCA-DAST-IAST-RASP)" 1문장으로 본론 1 도입 + 표 한 개로 25점 키워드 즉시 확보
{: .prompt-tip }
