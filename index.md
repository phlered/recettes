---
layout: default
title: Mes recettes
---

<h1>🍽️ Mes recettes</h1>

<div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
  <h2>🔍 Recherche rapide</h2>
  <input type="text" id="searchInput"
         placeholder="Tapez un ingrédient, un tag, un mot-clé…"
         style="width:100%; padding:10px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 4px;">
  <ul id="searchResults" style="list-style: none; padding: 0;"></ul>
</div>

<h2>Toutes les recettes</h2>

<ul id="allRecettes">
{% for recette in site.recettes %}
  <li>
    <a href="{{ recette.url | relative_url }}">{{ recette.title }}</a>
  </li>
{% endfor %}
</ul>

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

