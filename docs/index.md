---
layout: default
title: Accueil
---

<style>
.recipe-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin: 30px 0;
}

.recipe-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  padding: 20px;
  color: white;
  text-decoration: none;
  transition: transform 0.3s, box-shadow 0.3s;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.recipe-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
}

.recipe-card h3 {
  margin: 0 0 10px 0;
  font-size: 1.2em;
}

.search-section {
  text-align: center;
  margin: 40px 0;
}

#search-input {
  width: 100%;
  max-width: 500px;
  padding: 12px 20px;
  font-size: 16px;
  border: 2px solid #667eea;
  border-radius: 8px;
  outline: none;
}

#search-input:focus {
  border-color: #764ba2;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}
</style>

<div class="search-section">
  <input type="text" id="search-input" placeholder="Cherchez une recette (chocolat, tarte, pain...)" />
</div>

<h2>Toutes les recettes</h2>
<div class="recipe-container" id="recipes-grid">
{% assign recettes = site.pages | where_exp: 'p', 'p.name != "index.md" and p.name != "search.html"' | sort: 'title' %}
{% for p in recettes %}
<a href="{{ p.url | relative_url }}" class="recipe-card">
  <h3>{{ p.title }}</h3>
  {% if p.tags %}<small>{{ p.tags | join: ', ' }}</small>{% endif %}
</a>
{% endfor %}
</div>

<script src="https://unpkg.com/simple-jekyll-search/dest/simple-jekyll-search.min.js"></script>
<script>
window.addEventListener('load', function() {
  SimpleJekyllSearch({
    searchInput: document.getElementById('search-input'),
    resultsContainer: document.getElementById('recipes-grid'),
    json: '{{ "/search.json" | relative_url }}',
    searchResultTemplate: '<a href="{url}" class="recipe-card"><h3>{title}</h3><small>{tags}</small></a>',
    noResultsText: 'Aucune recette trouvée',
    fuzzySearch: true
  });
});
</script>
