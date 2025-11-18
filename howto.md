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

## ⚙️ 2. Créer le dossier local

Crée d'abord ton dossier de projet sur ton ordinateur :

``` bash
# Aller dans ton dossier de travail
cd ~/Documents

# Créer le dossier du projet
mkdir recettes
cd recettes

# Créer le sous-dossier docs
mkdir docs
```

------------------------------------------------------------------------

## 💻 3. Publier sur GitHub depuis VS Code

Ouvre ton dossier `recettes` dans VS Code, puis :

1.  Ouvrir la **palette de commandes** : `Cmd+Shift+P` (macOS) ou `Ctrl+Shift+P` (Windows)

2.  Taper : **Publish to GitHub**

3.  Choisir le nom du dépôt : `recettes`

4.  Sélectionner **Public** ou **Private** selon ta préférence

5.  VS Code va automatiquement :
    -   Créer le dépôt sur GitHub
    -   Initialiser Git localement
    -   Faire le premier commit
    -   Pousser tes fichiers sur GitHub

> ✅ Ton dépôt est maintenant en ligne et synchronisé !

### Vérifier que ça a marché

Ouvre ton navigateur et va sur : `https://github.com/tonpseudo/recettes`  
(remplace `tonpseudo` par ton nom d'utilisateur GitHub)

Tu devrais voir tous tes fichiers en ligne !

------------------------------------------------------------------------

## 🗂️ 4. Configurer les fichiers de base

### `_config.yml`

``` yaml
theme: minima
title: Mes recettes maison
description: Recettes testées et approuvées
```

### `docs/index.md`

Ce fichier va **automatiquement lister toutes tes recettes** sans que tu aies à les ajouter une par une :

``` markdown
---
layout: default
title: Accueil
---

# 🍴 Mes recettes

Bienvenue ! Voici toutes mes recettes :

{% for page in site.pages %}
  {% if page.dir == '/docs/' and page.name != 'index.md' and page.name != 'search.html' %}
- [{{ page.title }}]({{ page.url | relative_url }})
  {% endif %}
{% endfor %}

---

[🔎 Rechercher une recette](search.html)
```

> 💡 **Comment ça marche ?** Jekyll parcourt automatiquement tous les fichiers dans `docs/` et les affiche. Tu n'as qu'à ajouter de nouvelles recettes dans le dossier, elles apparaîtront automatiquement sur la page d'accueil !

------------------------------------------------------------------------

## 📤 5. Envoyer les modifications sur GitHub

Après avoir créé ou modifié des fichiers, il faut les "pousser" sur GitHub :

### Avec VS Code (recommandé)

1. **Ouvrir le panneau Source Control** : `Cmd+Shift+G` (ou clic sur l'icône de branche à gauche)

2. **Voir les changements** : Tous tes fichiers modifiés sont listés

3. **Stage les fichiers** : Clique sur le `+` en haut pour tout ajouter

4. **Écrire le message de commit** : Dans la zone de texte, tape par exemple :
   ```
   Ajout fichiers de configuration et recettes
   ```

5. **Commit** : Clique sur le bouton `✓ Commit` (ou `Cmd+Enter`)

6. **Push** : Clique sur `Sync Changes` ou `Push`

> ✅ Tes modifications sont maintenant en ligne sur GitHub !

### Avec le terminal (alternative)

``` bash
cd ~/Documents/recettes
git add .
git commit -m "Ajout fichiers de configuration et recettes"
git push
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
