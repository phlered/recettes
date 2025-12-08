---
layout: default
---

# 🍰 Mes recettes maison

Bienvenue ! Découvrez toutes mes recettes testées et approuvées :

{% assign sorted_posts = site.pages | where_exp: "post", "post.path contains 'docs'" | sort: 'title' %}
{% for post in sorted_posts %}
  {% if post.name != 'index.md' %}
- [{{ post.title }}]({{ post.url | relative_url }})
  {% endif %}
{% endfor %}
