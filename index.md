# Accueil

Bienvenue sur le site de recettes !
<div class="recettes-scroll">
  <ul>
    {% for recette in site.recettes %}
      <li><a href="{{ recette.url }}">{{ recette.title }}</a></li>
    {% endfor %}
  </ul>
</div>
---
layout: default
title: Accueil
---

<h1>🍽️ Mes recettes maison</h1>

<div class="search-box">
  <h2>🔍 Recherche rapide</h2>
  <input type="text" id="searchInput"
         class="search-input"
         placeholder="Tapez un ingrédient, un tag, un mot-clé…">
  <ul id="searchResults" class="search-results"></ul>
</div>


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

<script>
const searchInput = document.getElementById("searchInput");
const searchResults = document.getElementById("searchResults");
const allRecettes = document.getElementById("allRecettes");

let recettes = [
{% for recette in site.recettes %}
  {
    "title": "{{ recette.title | escape }}",
    "url": "{{ recette.url | relative_url }}",
    "content": {{ recette.content | strip_html | jsonify }},
    "tags": {{ recette.tags | jsonify }}
  }{% unless forloop.last %},{% endunless %}
{% endfor %}
];

// Debounce function
function debounce(fn, delay) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

// Highlight helper
function highlight(text, query) {
  if (!query) return text;
  const regex = new RegExp(`(${query})`, "gi");
  return text.replace(regex, "<mark>$1</mark>");
}

// Update search results
function updateSearch() {
  const q = searchInput.value.toLowerCase();
  searchResults.innerHTML = "";
  allRecettes.style.display = q.trim() === "" ? "block" : "none";

  if (q.trim() === "") return;

  const filtered = recettes.filter(r =>
    r.title.toLowerCase().includes(q) ||
    r.content.toLowerCase().includes(q) ||
    (r.tags && r.tags.some(t => t.toLowerCase().includes(q)))
  );

  if (filtered.length === 0) {
    searchResults.innerHTML = "<li>Aucune recette trouvée</li>";
    return;
  }

  filtered.forEach(r => {
    const li = document.createElement("li");
    li.innerHTML = `
      <a href="${r.url}">
        <strong>${highlight(r.title, q)}</strong>
      </a><br>
      <small>${r.tags ? highlight(r.tags.join(", "), q) : ""}</small>
    `;
    searchResults.appendChild(li);
  });
}

searchInput.addEventListener("input", debounce(updateSearch, 150));
</script>

