# Boris.py - Extracteur de Recettes Blogger

Script Python pour extraire automatiquement les recettes du blog Blogger **recettesb.blogspot.com** et générer des fichiers Markdown formatés.

## Vue d'ensemble

`boris.py` fonctionne de la même manière que `marmiton.py` mais est optimisé pour les pages du blog `recettesb.blogspot.com`. Il récupère :

- **Titre** de la recette
- **Ingrédients** avec quantités
- **Instructions de préparation**
- **Photo/Image** associée (téléchargement automatique)
- **Métadonnées** (source, date)

## Installation des dépendances

```bash
pip3 install selenium beautifulsoup4 webdriver-manager requests
```

Ou :

```bash
/opt/homebrew/bin/python3 -m pip install selenium beautifulsoup4 webdriver-manager requests
```

## Utilisation

### Syntaxe de base

```bash
python3 boris.py "<URL>"
```

### Exemple

```bash
python3 boris.py "https://recettesb.blogspot.com/2023/08/fluffy-turkish-cake-revani-with-syrup.html"
```

### Résultat

Le script génère automatiquement :

1. **Fichier Markdown** : `_recettes/fluffy_turkish_cake_revani_with_syrup.md`
2. **Image téléchargée** : `images/fluffy_turkish_cake_revani_with_syrup.jpg`
3. **Commit Git** : Enregistrement automatique dans le dépôt
4. **Push Git** : Envoi vers le dépôt distant

## Structure du fichier généré

```markdown
---
layout: default
title: "Titre de la recette"
source: "https://..."
date: "2025-12-21"
image: "images/..."
ingredients:
  - "1 tasse de sucre"
  - "2 œufs"
---

![illustration de la recette](images/...)

# Titre de la recette

## Ingrédients

- 1 tasse de sucre
- 2 œufs

## Préparation

1. Première étape
2. Deuxième étape

[Source Recettes B](https://...)
```

## Fonctionnement interne

### 1. Récupération du contenu

- Utilise Selenium pour charger la page avec JavaScript
- Accepte les popups de consentement automatiquement
- Attendqu le contenu soit chargé

### 2. Extraction des données

- **Titre** : Cherche le `<h1>` principal
- **Ingrédients** : Cherche les lignes contenant des quantités (nombres, unités : cup, tbsp, g, ml, etc.)
- **Instructions** : Cherche les sections après les mentions d'ingrédients
- **Image** : Récupère la première image trouvée dans le contenu du post

### 3. Nettoyage des données

- Supprime les doublons
- Filtre les lignes trop courtes ou non pertinentes
- Limite à 30 ingrédients et 20 étapes maximum

### 4. Téléchargement de l'image

- Récupère l'image principale de Blogger
- Sauvegarde localement dans le dossier `images/`
- Remplace l'URL par le chemin local dans le Markdown

### 5. Gestion Git

- Ajoute le fichier au staging (`git add`)
- Crée un commit avec le titre de la recette
- Pousse vers le dépôt distant (`git push`)

## Limitations et notes

- L'extraction dépend de la structure HTML du blog, qui peut varier
- Les instructions peuvent être partielles si le HTML n'est pas bien structuré
- Assurez-vous d'avoir accès à Internet pour :
  - Télécharger les pilotes Selenium
  - Accéder au blog
  - Télécharger les images
  - Pousser vers le dépôt Git

## Comparaison avec Marmiton.py

| Aspect | Marmiton.py | Boris.py |
|--------|-----------|----------|
| **Source** | Marmiton (JSON-LD) | Recettes B (HTML) |
| **Extraction** | Données structurées | Parsing HTML/texte |
| **Ingrédients** | Très précis | Basés sur les quantités |
| **Instructions** | Structurées | Texte brut |
| **Fiabilité** | Très élevée | Bonne (dépend du HTML) |

## Dépannage

### Erreur : `ModuleNotFoundError: No module named 'selenium'`

Installer les dépendances :
```bash
pip3 install selenium beautifulsoup4 webdriver-manager requests
```

### Erreur : `No module named 'chromedriver'`

Les drivers sont téléchargés automatiquement par `webdriver-manager`. Vérifiez votre connexion Internet.

### Image non téléchargée

Vérifiez que le dossier `images/` existe et que vous avez les droits d'écriture.

### Recette vide ou mal extraite

Certaines pages Blogger ont une structure HTML différente. Vous pouvez modifier le script pour ajouter des sélecteurs supplémentaires.

## Améliorations futures possibles

- [ ] Support de plus d'URL patterns Blogger
- [ ] Détection automatique de la langue (français/anglais)
- [ ] Meilleure séparation ingrédients/instructions
- [ ] Extraction des temps de cuisson/préparation
- [ ] Support de Blogger mobile (m.blogger.com)
- [ ] Gestion des ingrédients avec tirets/points
- [ ] Export en JSON ou CSV

## Auteur

Créé pour gérer les recettes du blog **Recettes B** (recettesb.blogspot.com)

## Licence

Même que le projet parent
