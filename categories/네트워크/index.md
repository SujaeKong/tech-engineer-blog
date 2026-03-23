---
layout: default
title: "네트워크"
---

<h1>네트워크</h1>

<ul class="post-list">
{% for post in site.categories.네트워크 %}
<li>
  <span class="post-meta">{{ post.date | date: "%Y-%m-%d" }}</span>
  <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
  <p>{{ post.excerpt | strip_html | truncate: 150 }}</p>
</li>
{% endfor %}
</ul>
