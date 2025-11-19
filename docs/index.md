---
layout: default
title: Accueil
---

# 🍴 Mes recettes

Bienvenue ! Voici toutes mes recettes :

{% assign recettes = site.pages | where_exp: 'p', 'p.name != "index.md" and p.name != "search.html"' | sort: 'title' %}
{% for p in recettes %}
- [{{ p.title | default: p.name | split: '.' | first | replace: '_', ' ' }}]({{ p.url | relative_url }})
{% endfor %}

---

[🔎 Rechercher une recette]({{ '/search.html' | relative_url }})
