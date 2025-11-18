---
layout: default
title: Accueil
---

# 🍴 Mes recettes

Bienvenue ! Voici toutes mes recettes :

{% for page in site.pages %}
  {% if page.dir == '/docs/' and page.name != 'index.md' and page.name != 'search.html' %}
- [{{ page.title }}]({{ page.url | relative_url }})
  {% endif %}
{% endfor %}

---

[🔎 Rechercher une recette](search.html)
