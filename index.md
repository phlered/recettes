---
layout: default
title: Mes recettes
---

# 🍰 Bienvenue sur mon site de recettes !

Découvrez toutes mes recettes maison testées et approuvées.

## Toutes les recettes

{% for post in site.posts %}
- [{{ post.title }}]({{ post.url | relative_url }})
{% endfor %}
