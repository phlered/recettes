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

def extract_marmiton_recipe_selenium(url):
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

    # Attendre que les ingrédients soient chargés (optionnel, car on utilise le JSON-LD)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-ingredient]'))
        )
    except Exception:
        pass

    html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(html, 'html.parser')

    import re, json
    ingredients = []
    steps = []
    title = 'Recette sans titre'
    tags = []
    keywords = ''
    image_url = ''
    # Parcours de toutes les balises JSON-LD pour trouver la recette
    ld_json_tags = soup.find_all('script', type='application/ld+json')
    for tag in ld_json_tags:
        try:
            # Sauvegarde brute pour debug (remplacé à chaque itération)
            with open('debug_jsonld.txt', 'w', encoding='utf-8') as f:
                f.write(tag.string or '')
            data = json.loads(tag.string)
            # Si data est une liste, prendre le premier Recipe
            if isinstance(data, list):
                for obj in data:
                    if isinstance(obj, dict) and obj.get('@type') == 'Recipe':
                        data = obj
                        break
            if isinstance(data, dict) and data.get('@type') == 'Recipe':
                title = data.get('name', title)
                # Ingrédients
                ingredients = data.get('recipeIngredient', [])
                # Étapes
                instructions = data.get('recipeInstructions', [])
                for step in instructions:
                    if isinstance(step, dict):
                        txt = step.get('text', '').strip()
                        if txt:
                            steps.append(txt)
                    elif isinstance(step, str):
                        steps.append(step.strip())
                # Tags/keywords
                keywords = data.get('keywords', '')
                if keywords:
                    tags = [t.strip() for t in keywords.split(',') if t.strip()]
                # Image principale
                img = data.get('image', '')
                if isinstance(img, list) and img:
                    image_url = img[0]
                elif isinstance(img, str):
                    image_url = img
                break  # On arrête dès qu'on a trouvé la recette
        except Exception:
            pass

    # 2. Fallback sur Mrtn.recipesData si besoin
    if not ingredients or not steps:
        script_tag = soup.find('script', string=re.compile(r'Mrtn.recipesData'))
        if script_tag:
            match = re.search(r'Mrtn.recipesData\s*=\s*(\{.*?\});', script_tag.string, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                if data.get('recipes') and len(data['recipes']) > 0:
                    recette = data['recipes'][0]
                    if not ingredients:
                        for ing in recette.get('ingredients', []):
                            qty = str(ing.get('qty', '')).strip()
                            unit = ing.get('unit', '').strip()
                            name = ing.get('name', '').strip()
                            line = f"{qty + ' ' if qty else ''}{unit + ' ' if unit else ''}{name}".strip()
                            ingredients.append(line)
                    if not steps:
                        # Pas d'étapes dans ce JSON, fallback BeautifulSoup
                        for step in soup.select('[data-test="instruction-step"]'):
                            txt = step.get_text(strip=True)
                            if txt:
                                steps.append(txt)
                        if not steps:
                            for li in soup.select('li.preparation-step'):
                                txt = li.get_text(strip=True)
                                if txt:
                                    steps.append(txt)
    # 3. Fallback BeautifulSoup si rien trouvé
    if not ingredients:
        for ing in soup.select('[data-ingredient]'):
            txt = ing.get_text(strip=True)
            if txt:
                ingredients.append(txt)
        if not ingredients:
            for li in soup.select('li.ingredient'):
                txt = li.get_text(strip=True)
                if txt:
                    ingredients.append(txt)
    if not steps:
        for step in soup.select('[data-test="instruction-step"]'):
            txt = step.get_text(strip=True)
            if txt:
                steps.append(txt)
        if not steps:
            for li in soup.select('li.preparation-step'):
                txt = li.get_text(strip=True)
                if txt:
                    steps.append(txt)


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
    if tags:
        yaml.append('tags: [' + ', '.join(tags) + ']')
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
    md_content += f"\n[Source Marmiton]({url})\n"
    return title, md_content

def slugify(text):
    import re
    import unicodedata
    # Supprimer les accents: NFKD -> ASCII sans diacritiques
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')

def main():
    if len(sys.argv) != 2:
        print("Usage: python marmiton.py <url>")
        sys.exit(1)
    url = sys.argv[1]

    title, md_content = extract_marmiton_recipe_selenium(url)
    filename = slugify(title) + '.md'
    outdir = os.path.join(os.path.dirname(__file__), '_recettes')
    os.makedirs(outdir, exist_ok=True)
    # Télécharger l'image si présente
    import re
    image_url_match = re.search(r'image: "([^"]+)"', md_content)
    if image_url_match:
        image_url = image_url_match.group(1)
        if image_url.startswith('http'):
            import requests
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
                    md_content = md_content.replace(image_url, f"{{{{ site.baseurl }}}}/{image_filename}")
            except Exception as e:
                print(f"Erreur lors du téléchargement de l'image : {e}")
    outfile = os.path.join(outdir, filename)
    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Recette enregistrée dans {outfile}")

    # Push automatique sur le dépôt git
    import subprocess
    try:
        # Ajouter la recette
        subprocess.run(["git", "add", outfile], check=True)
        # Ajouter l'image si elle a été téléchargée
        image_path_to_add = None
        image_url_match = re.search(r'image: "([^"]+)"', md_content)
        if image_url_match:
            image_url = image_url_match.group(1)
            if not image_url.startswith('http'):  # C'est un chemin local
                # Récupérer le chemin absolu de l'image
                image_path_to_add = os.path.join(os.path.dirname(__file__), image_url.replace('{{ site.baseurl }}/', ''))
                if os.path.exists(image_path_to_add):
                    subprocess.run(["git", "add", image_path_to_add], check=True)
        
        subprocess.run(["git", "commit", "-m", f"Ajout recette {title}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Recette poussée sur le dépôt distant.")
    except Exception as e:
        print(f"Erreur lors du push git : {e}")

if __name__ == "__main__":
    main()
