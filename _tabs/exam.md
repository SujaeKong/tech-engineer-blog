---
layout: page
icon: fas fa-graduation-cap
order: 2
title: 출제예상
---

> 정보관리기술사 회차별 출제 예상 토픽 시리즈. KPC 기출·합숙·모의 + 최근 뉴스 트렌드를 분석해 회차별 핵심 토픽을 선정합니다.
{: .prompt-info }

{% assign exam_posts = site.posts | where_exp: "post", "post.tags contains 'exam-prediction'" | sort: 'date' | reverse %}

{% if exam_posts.size == 0 %}
포스트 준비 중입니다.
{% else %}

## 140회 대비 (2026-08-22 시행)

{% for post in exam_posts %}
  {% if post.tags contains '140회대비' %}
- [{{ post.title }}]({{ post.url | relative_url }}) — `{{ post.categories | first }}`
  {% endif %}
{% endfor %}

## 139회 대비 (2026-05-16 시행)

{% for post in exam_posts %}
  {% if post.tags contains '139회대비' %}
- [{{ post.title }}]({{ post.url | relative_url }}) — `{{ post.categories | first }}`
  {% endif %}
{% endfor %}

{% endif %}

---

- 기출 데이터: [KPC 정보관리기술사 기출·합숙·모의 통합 검색](https://kpcitpe-search.pages.dev/){:target="_blank"}

> 예측은 학습 참고용이며 출제를 보장하지 않습니다.
{: .prompt-warning }
