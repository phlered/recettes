---
layout: default
title: Recherche
permalink: /search/
---

<h1>🔍 Recherche</h1>

<input type="text" id="searchInput"
       placeholder="Tapez un ingrédient, un tag, un mot-clé…"
       style="width:100%; padding:10px; margin-bottom: 20px;">

<ul id="results"></ul>

<script>
const searchInput = document.getElementById("searchInput");
const results = document.getElementById("results");

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
  results.innerHTML = "";

  if (q.trim() === "") return;

  recettes
    .filter(r =>
      r.title.toLowerCase().includes(q) ||
      r.content.toLowerCase().includes(q) ||
      (r.tags && r.tags.some(t => t.toLowerCase().includes(q)))
    )
    .forEach(r => {
      const li = document.createElement("li");
      li.innerHTML = `
        <a href="${r.url}">
          <strong>${highlight(r.title, q)}</strong>
        </a><br>
        <small>${r.tags ? highlight(r.tags.join(", "), q) : ""}</small>
      `;
      results.appendChild(li);
    });
}

searchInput.addEventListener("input", debounce(updateSearch, 150));
</script>