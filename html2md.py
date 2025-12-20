import sys
import os
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md


def extract_marmiton_recipe(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Titre
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else 'Recette sans titre'

    # Ingrédients
    ingredients = []
    for ing in soup.select('[data-ingredient]'):
        txt = ing.get_text(strip=True)
        if txt:
            ingredients.append(txt)
    if not ingredients:
        # fallback
        for li in soup.select('li.ingredient'):
            txt = li.get_text(strip=True)
            if txt:
                ingredients.append(txt)

    # Étapes
    steps = []
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
    from datetime import date
    yaml = [
        '---',
        f'title: "{title}"',
        f'source: "{url}"',
        f'date: "{date.today()}"',
        'ingredients:',
    ]
    for ing in ingredients:
        yaml.append(f'  - "{ing}"')
    yaml.append('---\n')

    # Construction du markdown
    md_content = '\n'.join(yaml)
    md_content += f"# {title}\n\n"
    md_content += "## Ingrédients\n\n"
    for ing in ingredients:
        md_content += f"- {ing}\n"
    md_content += "\n## Préparation\n\n"
    for i, step in enumerate(steps, 1):
        md_content += f"{i}. {step}\n"
    md_content += f"\n[Source]({url})\n"
    return title, md_content

def slugify(text):
    import re
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')


def main():
    if len(sys.argv) != 2:
        print("Usage: python html2md.py <url>")
        sys.exit(1)
    url = sys.argv[1]
    title, md_content = extract_marmiton_recipe(url)
    filename = slugify(title) + '.md'
    outdir = os.path.join(os.path.dirname(__file__), '_recettes')
    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, filename)
    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Recette enregistrée dans {outfile}")

if __name__ == "__main__":
    main()
