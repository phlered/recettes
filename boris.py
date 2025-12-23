import sys
import os
from datetime import date
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
import re
import json
import requests
from deep_translator import GoogleTranslator
from slugify import slugify

def extract_blogger_recipe(url):
    """
    Extrait une recette d'un blog Blogger (recettesb.blogspot.com)
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1200,800')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)

    # Accepter le consentement si présent
    try:
        consent_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., \"J'accepte tout\")]"))
        )
        consent_btn.click()
    except Exception:
        pass

    # Attendre le chargement du contenu
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
    except Exception:
        pass

    html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(html, 'html.parser')

    ingredients = []
    steps = []
    notes = ''
    title = 'Recette sans titre'
    tags = []
    image_url = ''
    
    # 1. Essayer d'extraire le titre depuis la structure HTML
    # Chercher le h1 ou h2 principal
    title_elem = soup.find(['h1', 'h2'], class_=re.compile(r'post-title|title|entry-title', re.I))
    if title_elem:
        title = title_elem.get_text(strip=True)
    else:
        # Fallback : prendre le premier h1
        for tag in soup.find_all('h1'):
            text = tag.get_text(strip=True)
            if text and len(text) > 3:
                title = text
                break

    # 2. Chercher la section des ingrédients et préparation
    # Sur Blogger, chercher tout le contenu du post
    content_elem = soup.find(['div', 'article'], class_=re.compile(r'post-body|entry-content|post-content', re.I))
    if not content_elem:
        content_elem = soup.find(['div'], class_='post')
    if not content_elem:
        # Dernier recours
        content_elem = soup.body

    if content_elem:
        # Récupérer tout le texte brut et chercher les sections
        full_text = content_elem.get_text(separator='\n', strip=True)
        
        # Chercher "Ingrédients" ou "ingredients" comme titre
        # Chercher après "For the syrup:" ou "For the semolina cake:" ou simples "Ingredients"
        ingredients_pattern = r'(?:for the .*?:|ingrédients?|ingredients?|composants?)'
        ingredients_matches = list(re.finditer(ingredients_pattern, full_text, re.IGNORECASE))
        
        if ingredients_matches:
            # Récupérer tout ce qui suit les mentions d'ingrédients jusqu'aux instructions
            start_idx = ingredients_matches[0].start()
            
            # Chercher où commencent les instructions
            instructions_pattern = r'(?:instructions?|préparation|étapes|directions|for the .*?:|add |stir |pour |grease|bake|press)'
            instructions_match = re.search(instructions_pattern, full_text[start_idx+50:], re.IGNORECASE)
            
            if instructions_match:
                ingredients_text = full_text[start_idx:start_idx+50+instructions_match.start()]
            else:
                ingredients_text = full_text[start_idx:]
            
            # Extraire les ingrédients (lignes contenant des quantités, mesures, ou noms d'ingrédients)
            for line in ingredients_text.split('\n'):
                line = line.strip()
                # Chercher les lignes avec quantités (nombres, fractions, ou mesures)
                # Écarter les lignes cassées se terminant par "("
                if line.endswith('('):
                    continue
                if line and re.search(r'\d|cup|tbsp|tsp|g|ml|gr|oz|pint|litre|l\b|kg', line, re.IGNORECASE):
                    if not any(word in line.lower() for word in ['ingrédients', 'ingredients', 'for the', 'instructions', 'préparation', 'étapes']):
                        ingredients.append(line)
        
        # Chercher la section "Préparation" ou "Instructions"
        # Chercher tout ce qui commence par "Instructions" ou "For the"
        instructions_pattern = r'(?:instructions?|préparation|étapes|directions)\s*[\:\n]*(.*?)(?=(?:notes?|ajouter un commentaire|publié|url|source|note|recette|comment)|$)'
        instructions_match = re.search(instructions_pattern, full_text, re.IGNORECASE | re.DOTALL)
        
        if instructions_match:
            instructions_text = instructions_match.group(1)
        else:
            # Fallback : chercher "For the" ou tout ce qui suit les derniers ingrédients
            last_ingredient_match = re.search(r'(about.*?cup unsweetened.*?)($|\n\n|\n(?=[A-Z]))', full_text, re.IGNORECASE | re.DOTALL)
            if last_ingredient_match:
                start_idx = last_ingredient_match.end()
                instructions_text = full_text[start_idx:]
            else:
                instructions_text = ""
        
        if instructions_text:
            # Chercher les lignes d'instructions
            for line in instructions_text.split('\n'):
                line = line.strip()
                # Les instructions (plus longues que les ingrédients, avec des verbes d'action)
                if line and len(line) > 15:
                    # Filtrer les trucs non pertinents
                    if not any(word in line.lower() for word in ['cup', 'tbsp', 'tsp', 'gramme', 'gram', 'ingrédients', 'ingredients', 'source', 'url', 'blogger']):
                        # Vérifier qu'il y a des verbes ou des mots significatifs
                        if re.search(r'(stir|mix|add|pour|bake|grease|sprinkle|heat|boil|turn|wait|let|mélanger|versér|ajouter|cuire|graisser)', line, re.IGNORECASE):
                            steps.append(line)

        # Fallback: si peu d'étapes détectées, découper le bloc en phrases
        if instructions_text and len(steps) < 3:
            alt_steps = []
            for sentence in re.split(r'(?<=[.!?])\s+', instructions_text):
                s = sentence.strip()
                if len(s) > 25:
                    alt_steps.append(s)
            if len(alt_steps) > len(steps):
                steps = alt_steps

        # Si le bloc est long mais que peu d'étapes sont détectées, reprendre toutes les phrases longues dans l'ordre
        if instructions_text and len(steps) < 8:
            alt_steps = []
            for sentence in re.split(r'(?<=[.!?])\s+', instructions_text):
                s = sentence.strip()
                if len(s) > 25:
                    alt_steps.append(s)
            if alt_steps:
                steps = alt_steps

        # Fallback supplémentaire: lister les éléments <li> si présents
        if content_elem and not steps:
            for li in content_elem.find_all('li'):
                txt = li.get_text(" ", strip=True)
                if txt and len(txt) > 15:
                    steps.append(txt)

        # Dernière chance: découper tous les paragraphes longs en phrases
        if not steps and content_elem:
            candidate_sentences = []
            for block in content_elem.find_all(['p', 'div']):
                txt = block.get_text(" ", strip=True)
                if not txt or len(txt) < 25:
                    continue
                if re.search(r'ingr[ée]dients?', txt, re.IGNORECASE):
                    continue
                for s in re.split(r'(?<=[.!?])\s+', txt):
                    s = s.strip()
                    if len(s) > 25:
                        candidate_sentences.append(s)
            if candidate_sentences:
                steps = candidate_sentences[:20]

        # Chercher une section Notes/Remarques
        notes_match = re.search(r'(?:notes?|remarques?)\s*[\:\-\n]*(.*?)(?=\n\s*(?:ajouter un commentaire|publié|url|source|note|recette|comment)|$)', full_text, re.IGNORECASE | re.DOTALL)
        if notes_match:
            raw_notes = notes_match.group(1).strip()
            # Nettoyer: réduire multiples sauts de ligne, garder un paragraphe
            lines = [l.strip() for l in raw_notes.split('\n') if l.strip()]
            notes = ' '.join(lines)

    # 3. Chercher l'image principale
    # Chercher l'image dans la structure du post
    if content_elem:
        img = content_elem.find('img')
        if img and img.get('src'):
            image_url = img.get('src')
    
    if not image_url:
        # Chercher une image en dehors du content
        img = soup.find('img', src=re.compile(r'blogger|googleusercontent|blogger.com'))
        if img and img.get('src'):
            image_url = img.get('src')

    # 4. Nettoyage des ingrédients et étapes
    # Supprimer les doublons et espaces inutiles
    ingredients = [ing.strip() for ing in ingredients if ing.strip() and len(ing.strip()) > 3]
    ingredients = list(dict.fromkeys(ingredients))  # Supprimer doublons
    
    # Limiter à 30 lignes max pour les ingrédients (éviter le bruit)
    if len(ingredients) > 30:
        ingredients = ingredients[:30]
    
    steps = [step.strip() for step in steps if step.strip() and len(step.strip()) > 10]
    steps = list(dict.fromkeys(steps))  # Supprimer doublons
    
    # Limiter à 20 étapes max
    if len(steps) > 20:
        steps = steps[:20]

    if not steps:
        print(f"Aucune instruction détectée pour {url}. Aucun fichier généré, aucun commit.")
        sys.exit(1)
    
    # 5. Traduction en français pour chaque champ
    title = translate_to_french(title)
    ingredients = [translate_to_french(ing) for ing in ingredients]
    steps = [translate_to_french(step) for step in steps]
    if notes:
        notes = translate_to_french(notes)

    # Bloc YAML
    yaml = [
        '---',
        'layout: default',
        f'title: "{title}"',
        f'source: "{url}"',
        f'date: "{date.today()}"',
    ]
    if image_url:
        yaml.append(f'image: "{image_url}"')
    yaml.append('ingredients:')
    for ing in ingredients:
        yaml.append(f'  - "{ing}"')
    yaml.append('---\n')

    # Construction du markdown
    md_content = '\n'.join(yaml)
    if image_url:
        md_content += f'![illustration de la recette]({image_url})\n\n'
    md_content += f"# {title}\n\n"
    md_content += "## Ingrédients\n\n"
    for ing in ingredients:
        md_content += f"- {ing}\n"
    md_content += "\n## Préparation\n\n"
    for i, step in enumerate(steps, 1):
        md_content += f"{i}. {step}\n"
    if notes:
        md_content += "\n## Notes\n\n"
        md_content += f"{notes}\n"
    md_content += f"\n_Merci à Boris pour le partage_\n\n"
    md_content += f"[Source Recettes B]({url})\n"
    
    return title, md_content

def replace_units(text):
    """
    Remplace les abréviations anglaises par leurs équivalents français.
    S'applique quel que soit la langue pour assurer la cohérence.
    """
    if not text:
        return text
    patterns = {
        r"\bts\b": "cuillère à café",
        r"\btsp\b": "cuillère à café",
        r"\bTbsp\b": "cuillère à soupe",
        r"\btbsp\b": "cuillère à soupe",
        r"\bcup\b": "tasse",
        r"\bcups\b": "tasses",
    }
    result = text
    for pat, repl in patterns.items():
        result = re.sub(pat, repl, result, flags=re.IGNORECASE)
    return result

def normalize_units_spacing(text):
    """
    Normalise les espaces autour des unités (ml, g, kg, l, °C) et formats fréquents.
    """
    if not text:
        return text
    s = text
    # Ajouter espace avant unités si nécessaire
    s = re.sub(r"(\d)(ml|mL|ML)", r"\1 ml", s)
    s = re.sub(r"(\d)(g|gr\.?|G)", r"\1 g", s)
    s = re.sub(r"(\d)(kg|KG)", r"\1 kg", s)
    s = re.sub(r"(\d)(l|L)\b", r"\1 l", s)
    # Unifier °C
    s = re.sub(r"\s*°\s*C", " °C", s)
    # Supprimer doublons d'espaces
    s = re.sub(r"\s+", " ", s).strip()
    return s

def postprocess_french(text):
    """
    Post-traitement pour éliminer les résidus anglais et améliorer le rendu français.
    - Normalise espaces d’unités
    - Remplace mots culinaires anglais courants
    - Corrige quelques formats (gr. → g)
    """
    if not text:
        return text
    s = text
    # Remplacements ciblés anglais → français (avec limites de mots)
    replacements = {
        r"\bbutter\b": "beurre",
        r"\begg\b": "œuf",
        r"\beggs\b": "œufs",
        r"\bmilk\b": "lait",
        r"\bsugar\b": "sucre",
        r"\bsemolina\b": "semoule",
        r"\bvanilla\b": "vanille",
        r"\borange rind\b": "zeste d'orange",
        r"\blemon rind\b": "zeste de citron",
        r"\bvegetable oil\b": "huile végétale",
        r"\bunsweetened grated coconut\b": "noix de coco râpée non sucrée",
        r"\bbaking powder\b": "levure chimique",
        r"\bbaking soda\b": "bicarbonate de soude",
    }
    for pat, repl in replacements.items():
        s = re.sub(pat, repl, s, flags=re.IGNORECASE)
    # Corriger gr. → g
    s = re.sub(r"\bgr\.?\b", "g", s, flags=re.IGNORECASE)
    # Ajouter "de" après "cuillère à (soupe|café) bombée" si suivi d’un nom
    s = re.sub(r"(cuillère à (?:soupe|café) bombée)\s+(\w+)", r"\1 de \2", s, flags=re.IGNORECASE)
    # Normaliser espaces d’unités
    s = normalize_units_spacing(s)
    return s

def detect_language(text):
    """
    Détecte si le texte est en anglais ou français
    """
    # Utiliser des mots clés simples pour détecter la langue
    english_words = {
        'the','for','and','or','in','of','to','with','without','a','is','are',
        'mix','add','bake','heat','cook','sprinkle','stir','pour','press',
        'lemon','orange','vanilla','juice','rind','oil','vegetable','unsweetened','grated','coconut',
        'cup','cups','tsp','tbsp'
    }
    french_words = {'le', 'la', 'et', 'de', 'à', 'un', 'une', 'mélanger', 'ajouter', 'cuire', 'chauffer', 'cuisiner', 'pour', 'avec'}
    
    text_lower = text.lower()
    english_count = sum(1 for word in english_words if word in text_lower)
    french_count = sum(1 for word in french_words if word in text_lower)
    
    # Si présence de marqueurs d'unités anglaises, considérer anglais
    if re.search(r"\b(cup|cups|tsp|tbsp)\b", text_lower):
        return 'en'
    # Par défaut, supposer anglais si on a plus de mots anglais
    if english_count > french_count:
        return 'en'
    return 'fr'

def translate_to_french(text):
    """
    Traduit un texte en français s'il n'est pas déjà en français,
    puis applique la conversion d'unités.
    """
    if not text or len(text) < 2:
        return text
    
    try:
        lang = detect_language(text)
        if lang != 'fr':
            translator = GoogleTranslator(source='en', target='fr', timeout=10)
            translated = translator.translate(text)
            return postprocess_french(replace_units(translated))
        return postprocess_french(replace_units(text))
    except Exception:
        # Fallback silencieux - retourner le texte avec unités converties
        return postprocess_french(replace_units(text))

def main():
    if len(sys.argv) != 2:
        print("Usage: python boris.py <url>")
        sys.exit(1)
    url = sys.argv[1]

    title, md_content = extract_blogger_recipe(url)
    filename = slugify(title) + '.md'
    outdir = os.path.join(os.path.dirname(__file__), '_recettes')
    os.makedirs(outdir, exist_ok=True)
    
    # Télécharger l'image si présente
    image_url_match = re.search(r'image: "([^"]+)"', md_content)
    if image_url_match:
        image_url = image_url_match.group(1)
        if image_url.startswith('http'):
            img_ext = os.path.splitext(image_url)[1].split('?')[0]
            if not img_ext or len(img_ext) > 5:
                img_ext = '.jpg'
            image_filename = f"images/{slugify(title)}{img_ext}"
            image_path = os.path.join(os.path.dirname(__file__), image_filename)
            try:
                r = requests.get(image_url, timeout=10)
                if r.status_code == 200:
                    with open(image_path, 'wb') as imgf:
                        imgf.write(r.content)
                    # Remplacer l'URL par le chemin local avec baseurl dans le markdown et le YAML
                    baseurl_path = f"{{{{ site.baseurl }}}}/{image_filename}"
                    md_content = md_content.replace(image_url, baseurl_path)
            except Exception as e:
                print(f"Erreur lors du téléchargement de l'image : {e}")
    
    outfile = os.path.join(outdir, filename)
    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Recette enregistrée dans {outfile}")

    # Push automatique sur le dépôt git
    import subprocess
    try:
        subprocess.run(["git", "add", outfile], check=True)
        subprocess.run(["git", "commit", "-m", f"Ajout recette {title}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Recette poussée sur le dépôt distant.")
    except Exception as e:
        print(f"Erreur lors du push git : {e}")

if __name__ == "__main__":
    main()
