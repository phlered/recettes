<script>
const searchInput = document.getElementById("searchInput");
const results = document.getElementById("results");

let posts = [
{% for post in site.recettes %}
  {
    "title": "{{ post.title | escape }}",
    "url": "{{ post.url | relative_url }}",
    "content": {{ post.content | strip_html | jsonify }},
    "tags": {{ post.tags | jsonify }}
  },
{% endfor %}
];

// --- Debounce function ---
function debounce(fn, delay) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

// --- Highlight helper ---
function highlight(text, query) {
  if (!query) return text;
  const regex = new RegExp(`(${query})`, "gi");
  return text.replace(regex, "<mark>$1</mark>");
}

// --- Update search ---
function updateSearch() {
  const q = searchInput.value.toLowerCase();
  results.innerHTML = "";

  if (q.trim() === "") return;

  posts
    .filter(p =>
      p.title.toLowerCase().includes(q) ||
      p.content.toLowerCase().includes(q) ||
      (p.tags && p.tags.join(" ").toLowerCase().includes(q))
    )
    .forEach(p => {
      const li = document.createElement("li");
      li.innerHTML = `
        <a href="${p.url}">
          <strong>${highlight(p.title, q)}</strong>
        </a><br>
        <small>${highlight(p.tags ? p.tags.join(", ") : "", q)}</small>
      `;
      results.appendChild(li);
    });
}

searchInput.addEventListener("input", debounce(updateSearch, 150));
</script>


---
layout: default
title: Recherche
---

<h1>🔍 Recherche</h1>

<input type="text" id="searchInput"
       placeholder="Tapez un ingrédient, un tag, un mot-clé…"
       style="width:100%; padding:10px; margin-bottom: 20px;">

<ul id="results"></ul>

<script>
… (tout ton script actuel) …
</script>