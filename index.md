---
layout: default
title: Mes recettes
---

# 🍽️ Toutes les recettes

<ul>
{% for post in site.posts %}
  <li>
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    {% if post.categories %}<em>({{ post.categories | join: ", " }})</em>{% endif %}
  </li>
{% endfor %}
</ul>

[🔍 Recherche]({{ "/search" | relative_url }})