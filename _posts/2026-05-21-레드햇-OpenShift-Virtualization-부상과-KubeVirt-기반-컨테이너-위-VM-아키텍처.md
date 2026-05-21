---
layout: post
title: "레드햇 OpenShift Virtualization 부상과 KubeVirt 기반 컨테이너 위 VM 아키텍처"
date: 2026-05-21
categories: 시스템구조
tags: [OpenShift, KubeVirt, 컨테이너가상화, 쿠버네티스, VMware대체, 클라우드네이티브, HCI, StackRox, KubeCon, 시스템아키텍처]
source_url: ""
---

## 1. 뉴스 요약

2026-05-19~20 KubeCon 오스틴 2026 컨퍼런스 전후로 컨테이너·가상화 통합 아키텍처 뉴스가 다수 보도됐다. 핵심은 ① **레드햇 CTO 인터뷰(지디넷코리아, 2026-05-20)** "**OpenShift Virtualization은 VMware 대체 그 이상이며 AI 인프라의 핵심**"이라는 발언으로, 브로드컴 인수 후 VMware 라이선스 정책 변화에 따른 **컨테이너 위 VM 워크로드 통합(KubeVirt)** 흐름을 정면으로 부각했다. ② **StackRox 쿠버네티스 보안 v3(StorageReview, 2026-05-19)** 출시로 컨테이너 워크로드와 VM 워크로드를 동일한 쿠버네티스 제어 평면에서 보호하는 **CNAPP(Cloud-Native Application Protection Platform)** 흐름이 강화됐다. ③ **HPE 컨테이너 플랫폼 발표(StorageReview, 2026-05-19)**와 **KubeCon 오스틴 뉴스 비트(StorageReview, 2026-05-19)**도 같은 맥락에서 컨테이너·VM 통합 운영을 중심 의제로 다뤘다. 이는 **기존 분리 운영되던 컨테이너(쿠버네티스)와 가상화(VMware vSphere) 인프라가 단일 쿠버네티스 제어 평면으로 수렴**하는 시스템 아키텍처 전환을 의미한다. 기술사 시험 시스템구조 영역에서 **가상화·컨테이너·쿠버네티스·HCI·클라우드 네이티브 아키텍처**는 출제 비중 최상위(19%) 단골 주제로, 본 회차(139회) 출제 가능성이 매우 높다.

## 2. 핵심 개념

### OpenShift Virtualization / KubeVirt 개요

| 항목 | 내용 |
|---|---|
| 정의 | 쿠버네티스 CRD(Custom Resource Definition)로 VM을 컨테이너처럼 선언적으로 관리하는 가상화 계층 |
| 기반 기술 | KubeVirt(CNCF 인큐베이팅) + QEMU/KVM + libvirt |
| 제어 평면 | 쿠버네티스 API 단일화(컨테이너·VM 동일 kubectl) |
| 스토리지 | CSI(Container Storage Interface) 기반 PV/PVC |
| 네트워크 | Multus·CNI 다중 인터페이스, SR-IOV 지원 |
| 라이브 마이그레이션 | 노드 간 무중단 이전, vMotion 대체 |
| 시사적 부상 배경 | 브로드컴-VMware 라이선스 정책 변화, AI/GPU 워크로드 통합 |

### 기존 가상화 vs 컨테이너 위 가상화(KubeVirt)

| 구분 | 기존 vSphere/Hyper-V | OpenShift Virtualization/KubeVirt |
|---|---|---|
| 제어 평면 | vCenter·SCVMM(별도) | 쿠버네티스 API(통합) |
| 워크로드 | VM 중심 | VM + 컨테이너 동시 |
| 운영 | vMotion·DRS·HA(전용) | Live Migration·HPA·Pod Topology |
| 자동화 | Terraform/PowerCLI | Helm·Operator·GitOps(Argo CD) |
| 라이선스 | 코어 기반 유료 | 오픈소스(KubeVirt) + 상용 지원 |
| AI 워크로드 통합 | GPU 패스스루(별도 구성) | CDI·GPU Operator 통합 |
| 클라우드 네이티브 | 제한적 | Native(Operator·CRD) |

### KubeVirt 기반 컨테이너·VM 통합 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│ ① 사용자/운영자 계층                                          │
│   kubectl·oc·OpenShift Console·GitOps(Argo CD/Flux)          │
├──────────────────────────────────────────────────────────────┤
│ ② 쿠버네티스 제어 평면(Control Plane)                         │
│   API Server·Scheduler·Controller Manager·etcd               │
│   Operators: KubeVirt·CDI·GPU Operator·Multus·StackRox       │
├──────────────────────────────────────────────────────────────┤
│ ③ 워크로드 계층(Workload)                                     │
│  ┌─────────────────────┐  ┌──────────────────────────────┐   │
│  │ Container Pod       │  │ VirtualMachine CRD           │   │
│  │ (마이크로서비스·AI) │  │ (Legacy OS·Windows·DB·GPU VM)│   │
│  └─────────────────────┘  └──────────────────────────────┘   │
├──────────────────────────────────────────────────────────────┤
│ ④ 노드/하이퍼바이저 계층(Worker Node)                         │
│   kubelet·CRI-O/containerd·virt-launcher·QEMU/KVM            │
│   GPU: NVIDIA GPU Operator·MIG·SR-IOV                        │
├──────────────────────────────────────────────────────────────┤
│ ⑤ 스토리지·네트워크 계층                                      │
│   CSI: ODF/Ceph·Portworx·Trident                             │
│   CNI: OVN-Kubernetes·Multus·Calico·SR-IOV                   │
├──────────────────────────────────────────────────────────────┤
│ ⑥ 보안·관측 계층(CNAPP/CWPP)                                  │
│   StackRox v3·Falco·OPA Gatekeeper·Prometheus·OpenTelemetry  │
└──────────────────────────────────────────────────────────────┘
```

### StackRox v3와 컨테이너·VM 통합 보안(CNAPP)

| 통제 영역 | 주요 기능 | 적용 워크로드 |
|---|---|---|
| 취약점 관리 | 이미지 스캔·VM OS 스캔 | Container + VM |
| 런타임 보호 | eBPF 기반 행위 탐지·이상 프로세스 차단 | Container + VM |
| 네트워크 정책 | NetworkPolicy 시각화·자동 생성 | 통합 제어 |
| 컴플라이언스 | NIST 800-53·PCI-DSS·CIS Benchmark | 통합 보고 |
| 공급망 보안 | SBOM·Sigstore·Cosign 서명 검증 | 이미지·VM 디스크 |

## 3. 기술사 출제 포인트

- **OpenShift Virtualization·KubeVirt**의 정의, 등장 배경(VMware 라이선스 정책 변화), 기술 구성
- **컨테이너 vs VM 가상화**의 본질적 차이와 컨테이너 위 VM 통합이 필요한 이유
- **쿠버네티스 CRD·Operator·CSI·CNI** 등 클라우드 네이티브 핵심 구성요소
- **하이퍼바이저(Type-1/Type-2)와 KVM/QEMU·libvirt**의 동작 원리
- **HCI(Hyper-Converged Infrastructure)** 개념과 OpenShift Data Foundation/Ceph 연계
- **라이브 마이그레이션(vMotion vs KubeVirt Live Migration)** 비교
- **CNAPP·CWPP(Cloud Workload Protection Platform)** 통합 보안 모델과 StackRox 아키텍처
- **GPU 가상화**(NVIDIA MIG·SR-IOV)와 AI 워크로드 통합 운영
- **GitOps·Operator 패턴**(Argo CD·OLM) 기반 선언적 인프라 관리
- **VMware 대체 전환 시 고려사항**(라이선스·운영 인력 재교육·기존 자산 호환·네트워크 정책 마이그레이션)

## 4. 관련 토픽 연계

- 컨테이너 위 VM 워크로드 보안은 [출제예상 139회: 제로트러스트 성숙도 2.0과 SASE N2SF 통합 보안 아키텍처](/tech-engineer-blog/posts/출제예상-139회-제로트러스트-성숙도-20과-SASE-N2SF-통합-보안-아키텍처/)의 워크로드 식별·정책 통제와 직접 연결된다.
- KubeVirt 기반 통합 운영의 공급망 보안은 [출제예상 139회: SW 공급망 보안 SBOM DevSecOps N2SF](/tech-engineer-blog/posts/출제예상-139회-SW-공급망-보안-SBOM-DevSecOps-N2SF/)에서 본 SBOM·서명 검증과 함께 봐야 한다.
- AI/GPU 워크로드 통합 운영은 [AI 데이터센터 인프라 병목과 GPU 전력 스토리지 스케일링 아키텍처](/tech-engineer-blog/posts/AI-데이터센터-인프라-병목과-GPU-전력-스토리지-스케일링-아키텍처/)에서 다룬 GPU·전력·스토리지 스케일링과 직결된다.
- 운영체제 동기화·스케줄링 등 시스템 기반 이론은 [출제예상 139회: 운영체제 동기화 통합 데드락 은행가 우선순위역전](/tech-engineer-blog/posts/출제예상-139회-운영체제-동기화-통합-데드락-은행가-우선순위역전/)과 함께 정리하면 시스템구조 영역 전반을 폭넓게 커버할 수 있다.
