---
layout: default
title: Mes recettes
---

# 🍽️ Toutes les recettes

<ul>
{% for recette in site.recettes %}
  <li>
    <a href="{{ recette.url | relative_url }}">{{ recette.title }}</a>
    {% if recette.tags %}<em>({{ recette.tags | join: ", " }})</em>{% endif %}
  </li>
{% endfor %}
</ul>

[🔍 Recherche]({{ "/search" | relative_url }})