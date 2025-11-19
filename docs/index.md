---
layout: default
title: Accueil
---

# 🍴 Mes recettes

Bienvenue ! Voici toutes mes recettes :

{% for page in site.pages %}
  {% if page.path contains 'docs/' and page.name != 'index.md' and page.name != 'search.html' and page.name contains '.md' %}
- [{{ page.title }}]({{ page.url | relative_url }})
  {% endif %}
{% endfor %}

---

[🔎 Rechercher une recette](search.html)
