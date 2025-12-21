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
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'J'accepte tout')]") )
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
                if line and re.search(r'\d|cup|tbsp|tsp|g|ml|gr|oz|pint|litre|l\b|kg', line, re.IGNORECASE):
                    if not any(word in line.lower() for word in ['ingrédients', 'ingredients', 'for the', 'instructions', 'préparation', 'étapes']):
                        ingredients.append(line)
        
        # Chercher la section "Préparation" ou "Instructions"
        # Chercher tout ce qui commence par "Instructions" ou "For the"
        instructions_pattern = r'(?:instructions?|préparation|étapes|directions)\s*[\:\n]*(.*?)(?=(?:notes?|ajouter un commentaire|publié|url|source|note|recette|comment))'
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
                    if not any(word in line.lower() for word in ['cup', 'tbsp', 'tsp', 'gramme', 'gram', 'ingrédients', 'ingredients', 'source', 'url', 'blogger', 'ajouter']):
                        # Vérifier qu'il y a des verbes ou des mots significatifs
                        if re.search(r'(stir|mix|add|pour|bake|grease|sprinkle|heat|boil|turn|wait|let|mélanger|versér|ajouter|mélanger|cuire|graisser)', line, re.IGNORECASE):
                            steps.append(line)

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
    md_content += f"\n_Merci à Boris pour le partage_\n\n"
    md_content += f"[Source Recettes B]({url})\n"
    
    return title, md_content

def slugify(text):
    """
    Convertit un titre en slug valide pour un nom de fichier
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')

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
                    # Remplacer l'URL par le chemin local dans le markdown
                    md_content = md_content.replace(image_url, image_filename)
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
