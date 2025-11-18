# 🧑‍🍳 HowTo -- Créer un site de recettes avec GitHub Pages et Markdown

Ce guide explique pas à pas comment construire un petit site web
statique pour y publier des recettes, **sans base de données, sans
cookies, et gratuitement**, grâce à **GitHub Pages** et **Jekyll**.

------------------------------------------------------------------------

## 🧱 1. Structure du projet

Ton dépôt GitHub contiendra à peu près ceci :

    recettes/
    │
    ├── docs/
    │   ├── index.md              → page d’accueil
    │   ├── tarte_aux_pommes.md   → une recette
    │   ├── veloute_celeri.md     → une autre recette
    │   ├── search.html           → page de recherche
    │   ├── search.json           → index de recherche généré par Jekyll
    │   └── assets/ (images, css…)
    │
    └── _config.yml               → configuration du site (titre, thème…)

> Le dossier `docs/` sera la racine du site publiée par GitHub Pages.

------------------------------------------------------------------------

## ⚙️ 2. Créer le dépôt sur GitHub

1.  Se connecter à ton compte GitHub.\

2.  Cliquer sur **New repository**.\

3.  Nommer ton dépôt :

        recettes

4.  Cocher : ✅ *Add a README file*\

5.  Créer le dépôt.

------------------------------------------------------------------------

## 💻 3. Cloner le dépôt sur ton ordinateur

Tu vas "lier" ton ordinateur à ce dépôt en ligne pour pouvoir envoyer et
récupérer les fichiers.

### Installer Git (si ce n'est pas déjà fait)

-   macOS : Git est souvent déjà installé.
-   Windows : https://git-scm.com/download/win

### Puis dans le terminal :

``` bash
# Aller dans ton dossier de travail
cd ~/Documents

# Cloner ton dépôt
git clone https://github.com/tonpseudo/recettes.git

# Entrer dans le dossier
cd recettes
```

Tu as maintenant une **copie locale** de ton dépôt GitHub.

------------------------------------------------------------------------

## 🗂️ 4. Créer la structure de base

``` bash
mkdir docs
touch docs/index.md
touch _config.yml
```

### `_config.yml`

``` yaml
theme: minima
title: Mes recettes maison
description: Recettes testées et approuvées
```

### `docs/index.md`

``` markdown
---
layout: default
title: Accueil
---

# 🍴 Mes recettes

Bienvenue !  
- [Tarte aux pommes](tarte_aux_pommes.md)
- [Velouté céleri-poireau](veloute_celeri.md)
- [Recherche de recette](search.html)
```

------------------------------------------------------------------------

## 🍏 5. Ajouter une recette en Markdown

Créer `docs/tarte_aux_pommes.md` :

``` markdown
---
layout: default
title: Tarte aux pommes
tags: [dessert, rapide, familial]
---

# 🥧 Tarte aux pommes

- 4 pommes  
- 1 pâte brisée  
- 50 g de sucre  
- 20 g de beurre

**Cuisson :** 35 min à 180°C.
```

------------------------------------------------------------------------

## 🕵️ 6. Ajouter la recherche locale

### `docs/search.json`

``` liquid
---
layout: null
---
[
{% for page in site.pages %}
  {
    "title": "{{ page.title | escape }}",
    "url": "{{ page.url | relative_url }}",
    "content": "{{ page.content | strip_html | escape }}",
    "tags": "{{ page.tags | join: ', ' }}"
  }{% unless forloop.last %},{% endunless %}
{% endfor %}
]
```

### `docs/search.html`

``` html
<h1>🔎 Recherche de recette</h1>
<input type="text" id="search-input" placeholder="Ex : carotte, dessert...">
<ul id="results-container"></ul>

<script src="https://unpkg.com/simple-jekyll-search/dest/simple-jekyll-search.min.js"></script>
<script>
var sjs = SimpleJekyllSearch({
  searchInput: document.getElementById('search-input'),
  resultsContainer: document.getElementById('results-container'),
  json: '/recettes/search.json'
})
</script>
```

------------------------------------------------------------------------

## 🚀 7. Publier le site sur GitHub Pages

1.  GitHub → *Settings → Pages*
2.  **Build and deployment** :
    -   *Source* : `Deploy from branch`
    -   *Branch* : `main`
    -   *Folder* : `/docs`
3.  Attendre 30--60 s.
4.  Le site apparaît sur :\
    `https://tonpseudo.github.io/recettes/`

------------------------------------------------------------------------

## 🔄 8. Mettre à jour le site (Git pas à pas)

``` bash
cd ~/Documents/recettes
git status
git add docs/tarte_carotte.md
git commit -m "Ajout recette tarte carotte"
git push
```

Une minute après le `git push`, le site se met à jour automatiquement.

------------------------------------------------------------------------

## 🧹 9. Commandes Git utiles

  Action                    Commande
  ------------------------- ---------------------------
  Voir les modifications    `git status`
  Ajouter tout              `git add .`
  Commit                    `git commit -m "message"`
  Envoyer                   `git push`
  Récupérer depuis GitHub   `git pull`
  Annuler avant commit      `git restore fichier.md`

------------------------------------------------------------------------

## 🧠 10. Cycle complet Git → GitHub Pages

  Étape   Action                     Effet
  ------- -------------------------- -------------------------
  1       Modifier un fichier        Changement local
  2       `git add` + `git commit`   Nouvelle version locale
  3       `git push`                 Envoi sur GitHub
  4       Reconstruction Jekyll      Site mis à jour

------------------------------------------------------------------------

## 🧩 11. Schéma visuel

            ┌───────────────────────────────┐
            │   Ordinateur (local)          │
            │───────────────────────────────│
            │ 1. Modifier                    │
            │ 2. git add                     │
            │ 3. git commit                  │
            │ 4. git push                    │
            └──────────────┬────────────────┘
                           │
                           ▼
            ┌───────────────────────────────┐
            │        GitHub                 │
            │ Reçoit les fichiers           │
            │ Lance GitHub Pages            │
            └──────────────┬────────────────┘
                           │
                           ▼
            ┌───────────────────────────────┐
            │   Site en ligne (Pages)       │
            │ https://tonpseudo.github.io/recettes/ │
            └───────────────────────────────┘

------------------------------------------------------------------------

🧑‍🍳 *Fait maison avec Jekyll, Markdown et un peu de Git.*
