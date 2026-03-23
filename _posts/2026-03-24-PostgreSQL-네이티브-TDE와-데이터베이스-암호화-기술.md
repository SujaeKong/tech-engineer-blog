---
layout: post
title: "PostgreSQL 네이티브 TDE와 데이터베이스 암호화 핵심 기술"
date: 2026-03-24
categories: 데이터베이스
tags: [TDE, PostgreSQL, 암호화, DB보안, 투명암호화]
source_url: ""
---

## 1. 뉴스 요약

EDB(EnterpriseDB)가 PostgreSQL 기반의 데이터베이스 보안 기술인 '네이티브 TDE(Transparent Data Encryption)'를 공개했다. 네이티브 TDE는 애플리케이션 수정 없이 데이터베이스 수준에서 저장 데이터를 자동 암호화하는 기술로, 기존 서드파티 솔루션 대비 성능 오버헤드를 최소화하면서도 규제 준수(Compliance) 요건을 충족할 수 있다. 오픈소스 PostgreSQL 생태계에서 엔터프라이즈급 보안 기능이 네이티브로 제공된다는 점에서 주목받고 있다.

## 2. 핵심 개념

### TDE(Transparent Data Encryption)
- **정의**: 데이터베이스에 저장되는 데이터를 디스크 수준에서 자동으로 암호화/복호화하는 기술
- **투명성**: 애플리케이션 코드 변경 없이 DBMS 엔진 레벨에서 처리
- **암호화 대상**: 데이터 파일, 임시 파일, 리두 로그, 백업 파일 등 At-Rest 데이터 전체

### 암호화 계층 구조

| 계층 | 방식 | 특징 |
|------|------|------|
| 애플리케이션 레벨 | 컬럼 단위 암호화 | 세밀한 제어, 높은 개발 비용 |
| DBMS 레벨 (TDE) | 테이블스페이스/테이블 단위 | 투명성, 인덱스 활용 가능 |
| 파일시스템 레벨 | 볼륨/디스크 암호화 | OS 의존, DB 인식 불가 |

### 키 관리 아키텍처
- **2-Tier Key 구조**: MEK(Master Encryption Key) + DEK(Data Encryption Key)
- **MEK**: 외부 KMS(Key Management System)에서 관리
- **DEK**: MEK로 암호화되어 DB 내부에 저장, 실제 데이터 암호화에 사용
- **키 순환(Key Rotation)**: 서비스 중단 없이 주기적 키 교체 지원

## 3. 기술사 출제 포인트

### 예상 문제
1. **TDE(Transparent Data Encryption)의 개념과 암호화 계층별 비교를 설명하시오**
2. **데이터베이스 암호화 방식(컬럼 레벨, TDE, 파일시스템 레벨)의 장단점을 비교하시오**
3. **개인정보보호법 준수를 위한 DB 암호화 아키텍처를 설계하시오**

### 답안 구성 가이드
- TDE 정의 → 동작 원리(암호화/복호화 흐름) → 키 관리 체계 → 성능 영향 → 타 방식 비교
- 법적 요건(개인정보보호법, 정보통신망법)과 연계하여 암호화 대상 및 범위 명시
- 키 관리의 중요성: KMS 연동, 키 순환, 접근제어, 감사 로그

## 4. 관련 토픽 연계

- **DB 접근제어**: TDE + DAM(Database Activity Monitoring) + 접근제어 통합 보안 체계
- **개인정보 비식별화**: 암호화 vs 가명처리 vs 익명처리 비교
- **클라우드 DB 보안**: AWS RDS TDE, Azure TDE 등 CSP별 구현 차이
- **키 관리 시스템(KMS)**: HSM(Hardware Security Module) 기반 키 관리 아키텍처
- **데이터 거버넌스**: 암호화 정책 수립과 데이터 분류체계(Classification)
