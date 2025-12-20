---
layout: default
title: Accueil
---

<h1>🍽️ Mes recettes maison</h1>

<h2 id="recettes-title">Toutes mes recettes</h2>
<div class="recette-cards" id="recetteCards">
{% for recette in site.recettes %}
  <a class="recette-card" href="{{ recette.url | relative_url }}" 
     data-title="{{ recette.title | downcase }}" 
     data-tags="{% if recette.tags %}{{ recette.tags | join: ',' | downcase }}{% endif %}" 
     data-content="{{ recette.content | strip_html | downcase }}">
    <div class="recette-card-content">
      <h3>{{ recette.title }}</h3>
    </div>
  </a>
{% endfor %}
</div>

