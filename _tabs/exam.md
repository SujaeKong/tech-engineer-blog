---
layout: page
icon: fas fa-graduation-cap
order: 2
title: 출제예상
---

> 정보관리기술사 회차별 출제 예상 토픽 시리즈입니다. **110~138회 기출 + 모의/합숙 + 최근 뉴스 트렌드**를 v6 알고리즘으로 분석해 회차별 핵심 토픽을 선정합니다.
{: .prompt-info }

## 산출 방식

1. **데이터 통합**: KPC 기출 2,699문제 + 모의 5,881문제 + 합숙 3,578문제 (총 12,158문제)
2. **자동 키워드 추출**: 한글 명사구 + 영문 약어 + 한영 혼합어 N-gram
3. **가중치**: 출처(기출 ×5, 합숙 ×5, 모의 ×1.5) × 시점(6mo ×5, 1y ×3, 2y ×1.5) × 유형(논술 ×1.3)
4. **신생 보너스**: 12개월 내 첫등장 + 최근 6개월 3회 이상 → ×3.5
5. **직전 회차 디스카운트**: 정확 출제 ×0.3, 단답만 ×0.7
6. **인적 큐레이션**: 카테고리 균형 + 통합 토픽 그룹핑

## 백테스트 검증 (135~138회)

| 회차 | TOP10 신생 토픽 캐치 | 실제 출제 적중 |
|------|---------------------|----------------|
| 136 | Agentic AI, 제로트러스트, OWASP, SBOM | ✅ Agentic AI / 제로트러스트 / OWASP |
| 137 | MCP, RAG, OWASP, Agentic AI | ✅ MCP, RAG, Transformer |
| 138 | Agentic, 제로트러스트, OWASP, Inversion | ✅ OWASP, Model Inversion, ISMS-P |

> 변별력 적중률 평균 4.5/30. 측정 가능한 알고리즘 신뢰도 확보.
{: .prompt-tip }

---

## 회차별 출제 예상 토픽

{% assign exam_posts = site.posts | where_exp: "post", "post.tags contains 'exam-prediction'" | sort: 'date' | reverse %}

{% if exam_posts.size == 0 %}
포스트 준비 중입니다.
{% else %}

{% assign rounds = exam_posts | map: 'tags' | uniq %}

### 139회 대비 (2026-08 시행 예정)
{% for post in exam_posts %}
  {% if post.tags contains '139회대비' %}
- [{{ post.title }}]({{ post.url | relative_url }}) — `{{ post.categories | first }}`
  {% endif %}
{% endfor %}

{% endif %}

---

## 알고리즘·데이터 출처

- **기출 데이터**: [KPC 정보관리기술사 검색](https://kpcitpe-search.pages.dev/){:target="_blank"}
- **소스코드**: [GitHub 저장소](https://github.com/SujaeKong/tech-engineer-blog){:target="_blank"} — `scripts/exam_predictor_v6.py`
- **예측 결과 JSON**: `_data/exam_predict_139.json` (재현 가능)

## 시리즈 운영 사이클

| 단계 | 시점 | 작업 |
|------|------|------|
| ① 트렌드 분석 | 시험 2~3개월 전 | xls 최신화 + 110~N회 빈출 분석 |
| ② 토픽 선정 | 동시 | 10개 출제 예상 토픽 선정 |
| ③ 포스트 작성 | 1~2주 | 10건 시리즈 포스팅 |
| ④ 시험 후 회고 | 시험 1주 후 | 적중률 분석 + 다음 회차 인사이트 |

> 예측은 학습 참고용이며 출제를 보장하지 않습니다. 출제진의 의도에 따라 신규 법령·표준이 즉시 출제될 수 있으므로 외부 트렌드 모니터링도 병행하시기 바랍니다.
{: .prompt-warning }
