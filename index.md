---
layout: default
title: Accueil
---

<h1>🍽️ Mes recettes maison</h1>

<h2>Toutes mes recettes</h2>
<div class="recette-cards">
{% for recette in site.recettes %}
  <a class="recette-card" href="{{ recette.url | relative_url }}">
    {% if recette.image %}
      <img src="{{ recette.image | relative_url }}" alt="{{ recette.title }}" class="recette-card-img">
    {% endif %}
    <div class="recette-card-content">
      <h3>{{ recette.title }}</h3>
      {% if recette.tags %}
        <div class="recette-tags">
        {% for tag in recette.tags %}
          <span class="recette-tag">{{ tag }}</span>
        {% endfor %}
        </div>
      {% endif %}
    </div>
  </a>
{% endfor %}
</div>

